"""
FastAPI main application.
Defines API routes, middleware, and application lifecycle.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.config import settings
from backend.models.job_model import (
    JobProcessingRequest,
    ClarificationRequest,
    ProcessingResponse,
    ErrorResponse
)
from backend.agent.orchestrator import get_orchestrator
from backend.services.mongodb_service import get_mongodb_service
from backend.services.linkedin_service import get_linkedin_service
from backend.utils.helpers import (
    setup_logging,
    format_error_response,
    sanitize_input,
    get_health_status,
    TimingContext
)


# Setup logging
setup_logging("INFO" if not settings.debug else "DEBUG")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)
    
    try:
        # Initialize MongoDB connection
        mongodb_service = get_mongodb_service()
        await mongodb_service.connect()
        logger.info("MongoDB connection established")
        
        # Validate environment
        from backend.utils.helpers import validate_environment
        env_status = validate_environment()
        logger.info(f"Environment validation: {env_status}")
        
        if not all(env_status.values()):
            logger.warning("Some services are not properly configured!")
        
        logger.info("Application startup complete")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}", exc_info=True)
        raise
    
    # Shutdown
    logger.info("Shutting down application...")
    
    try:
        mongodb_service = get_mongodb_service()
        await mongodb_service.disconnect()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")
    
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered LinkedIn job processing tool",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Exception Handlers ====================

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation failed",
            error_code="VALIDATION_ERROR",
            details=exc.errors()
        ).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code="HTTP_ERROR"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            details=format_error_response(exc) if settings.debug else None
        ).dict()
    )


# ==================== API Routes ====================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health", response_model=dict)
async def health_check():
    """
    Health check endpoint.
    Returns application health status and service availability.
    """
    health_status = get_health_status()
    
    status_code = (
        status.HTTP_200_OK
        if health_status["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


@app.post("/process-job", response_model=ProcessingResponse)
async def process_job(request: JobProcessingRequest):
    """
    Process a job posting.
    
    This endpoint:
    1. Accepts raw unstructured job text
    2. Extracts structured data using AI
    3. Validates the extracted data
    4. Determines if clarification is needed
    5. If no clarification needed, processes and saves the job
    6. Returns response with next steps
    
    Args:
        request: JobProcessingRequest with raw job text
        
    Returns:
        ProcessingResponse with status and next steps
    """
    with TimingContext("process_job"):
        try:
            logger.info("Processing job request")
            
            # Sanitize input
            raw_job_text = sanitize_input(request.raw_job_text, max_length=20000)
            
            if len(raw_job_text) < 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Job text too short. Please provide more details."
                )
            
            # Get orchestrator and process
            orchestrator = get_orchestrator()
            response = await orchestrator.process_initial_request(
                raw_job_text=raw_job_text,
                user_context=request.user_context
            )
            
            logger.info(
                f"Job processing completed: conversation_id={response.conversation_id}, "
                f"state={response.state}"
            )
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Job processing failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: {str(e)}"
            )


@app.post("/clarification-response", response_model=ProcessingResponse)
async def clarification_response(request: ClarificationRequest):
    """
    Handle user's clarification response.
    
    This endpoint:
    1. Receives user's choice (combined/separate)
    2. Retrieves conversation state
    3. Continues processing based on user's decision
    4. Saves job entries to database and Google Sheets
    5. Returns final results
    
    Args:
        request: ClarificationRequest with conversation_id and choice
        
    Returns:
        ProcessingResponse with final results
    """
    with TimingContext("clarification_response"):
        try:
            logger.info(
                f"Processing clarification response: {request.conversation_id}, "
                f"choice={request.choice}"
            )
            
            # Get orchestrator and process
            orchestrator = get_orchestrator()
            response = await orchestrator.process_clarification_response(
                conversation_id=request.conversation_id,
                choice=request.choice
            )
            
            logger.info(
                f"Clarification processing completed: state={response.state}"
            )
            
            return response
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Clarification processing failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: {str(e)}"
            )


@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Retrieve conversation details.
    
    Args:
        conversation_id: Conversation identifier
        
    Returns:
        Conversation details
    """
    try:
        mongodb_service = get_mongodb_service()
        conversation = await mongodb_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found: {conversation_id}"
            )
        
        return conversation.dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation: {str(e)}"
        )


@app.get("/auth/linkedin/url")
async def linkedin_auth_url():
    """Return LinkedIn OAuth authorization URL for frontend redirect."""
    service = get_linkedin_service()
    if not service.is_configured():
        raise HTTPException(status_code=400, detail="LinkedIn service not configured")
    return {"auth_url": service.get_authorization_url()}


@app.get("/auth/linkedin/callback")
async def linkedin_callback(code: str | None = None):
    """Callback endpoint that LinkedIn redirects to with `code`.

    Exchanges `code` for an access token and validates the token.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    service = get_linkedin_service()
    token = await service.handle_oauth_callback(code)
    if not token:
        raise HTTPException(status_code=500, detail="Failed to exchange code for token")

    return {"success": True, "message": "LinkedIn authorized", "access_token": token}


@app.get("/jobs/{conversation_id}")
async def get_jobs_by_conversation(conversation_id: str):
    """
    Retrieve all job entries for a conversation.
    
    Args:
        conversation_id: Conversation identifier
        
    Returns:
        List of job entries
    """
    try:
        mongodb_service = get_mongodb_service()
        job_entries = await mongodb_service.get_job_entries_by_conversation(
            conversation_id
        )
        
        return {
            "conversation_id": conversation_id,
            "count": len(job_entries),
            "jobs": [entry.dict() for entry in job_entries]
        }
    
    except Exception as e:
        logger.error(f"Failed to retrieve jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve jobs: {str(e)}"
        )


# ==================== Development/Debug Routes ====================

if settings.debug:
    @app.get("/debug/validate-env")
    async def debug_validate_environment():
        """Debug endpoint to validate environment configuration."""
        from backend.utils.helpers import validate_environment
        return validate_environment()
    
    @app.get("/debug/test-extraction")
    async def debug_test_extraction(text: str = "Test job posting"):
        """Debug endpoint to test extraction agent."""
        from backend.agent.extractor import get_extraction_agent
        
        agent = get_extraction_agent()
        result = await agent.extract(text)
        return result.dict()


@app.post("/debug/sheets-test")
async def debug_sheets_test():
    """Attempt to append a test row to Google Sheets and return detailed result or traceback."""
    import traceback
    from backend.services.sheets_service import get_sheets_service
    from backend.models.job_model import ExtractedJobData, JobRole, WorkMode

    sheets = get_sheets_service()

    # Build minimal test job data
    test_data = ExtractedJobData(
        company="DEBUG_Corp",
        roles=[JobRole(title="Debug Role", description="Automated test")],
        location="Remote",
        work_mode=WorkMode.REMOTE,
        experience="0-1 years",
        eligibility="Open",
        salary="Not specified",
        apply_link="https://example.com/apply",
        deadline=None
    )

    try:
        result = await sheets.append_job_entry(test_data)
        return {"ok": result}
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Sheets test failed: {str(e)}\n{tb}")
        raise HTTPException(status_code=500, detail={"error": str(e), "trace": tb})


@app.post("/debug/linkedin/set-token")
async def debug_set_linkedin_token(body: dict):
    """Set a LinkedIn access token for the running process (debug only).
    
    Body: { "access_token": "..." }
    """
    access_token = body.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="access_token required")
    
    service = get_linkedin_service()
    ok = await service.authenticate(access_token)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to validate access token")
    
    return {"ok": True, "message": "LinkedIn token set and validated"}


@app.post("/debug/linkedin/force-token")
async def debug_force_linkedin_token(body: dict):
    """Force set a LinkedIn token WITHOUT validation (debug only).
    
    Body: { "access_token": "...", "author_urn": "urn:li:person:..." }
    """
    access_token = body.get("access_token")
    author_urn = body.get("author_urn")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="access_token required")
    
    service = get_linkedin_service()
    service.access_token = access_token
    service.author_urn = author_urn
    service.access_token_expires_at = datetime.utcnow() + timedelta(days=60)
    
    return {
        "success": True, 
        "message": "Token set (unvalidated)", 
        "has_author_urn": bool(author_urn)
    }


@app.get("/debug/linkedin/status")
async def debug_linkedin_status():
    """Check LinkedIn service configuration and token status."""
    service = get_linkedin_service()
    return {
        "is_configured": service.is_configured(),
        "has_access_token": bool(service.access_token),
        "has_author_urn": bool(service.author_urn),
        "author_urn": service.author_urn,
        "token_expires_at": service.access_token_expires_at.isoformat() if service.access_token_expires_at else None,
        "token_expired": (service.access_token_expires_at and datetime.utcnow() >= service.access_token_expires_at) if service.access_token_expires_at else None
    }


@app.post("/debug/linkedin/fetch-profile")
async def debug_fetch_linkedin_profile():
    """Fetch LinkedIn profile to populate author URN."""
    import httpx
    service = get_linkedin_service()
    
    if not service.access_token:
        raise HTTPException(status_code=400, detail="No access token configured")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {"Authorization": f"Bearer {service.access_token}"}
            r = await client.get("https://api.linkedin.com/v2/me", headers=headers)
            r.raise_for_status()
            profile = r.json()
            
            if "id" in profile:
                service.author_urn = f"urn:li:person:{profile['id']}"
                return {
                    "success": True,
                    "profile_id": profile.get("id"),
                    "author_urn": service.author_urn,
                    "first_name": profile.get("localizedFirstName"),
                    "last_name": profile.get("localizedLastName")
                }
            else:
                return {"success": False, "error": "No id in profile", "profile": profile}
    except httpx.HTTPStatusError as exc:
        return {
            "success": False,
            "error": "HTTP error",
            "status_code": exc.response.status_code,
            "response": exc.response.text
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/debug/linkedin/exchange-verbose")
async def debug_linkedin_exchange(code: str):
    """Debug endpoint that shows detailed LinkedIn API errors."""
    import httpx
    from backend.config import settings
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.linkedin_redirect_uri,
        "client_id": settings.linkedin_client_id,
        "client_secret": settings.linkedin_client_secret,
    }
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            return {
                "status_code": r.status_code,
                "response_text": r.text,
                "response_json": r.json() if r.status_code == 200 else None,
                "sent_data": {k: v if k != "client_secret" else "***" for k, v in data.items()}
            }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@app.post("/debug/linkedin/test-post")
async def debug_test_linkedin_post(body: dict):
    """Test LinkedIn posting with current token. Returns detailed error info.
    
    Body: {
        "post_text": "Your test post content",
        "author_urn": "urn:li:person:<sub>|urn:li:member:<id>"  # Optional, uses configured/token-bound fallback
    }
    """
    import httpx
    
    service = get_linkedin_service()
    
    if not service.access_token:
        raise HTTPException(status_code=400, detail="No LinkedIn token configured")
    
    post_text = body.get("post_text", "🚀 Test post from Link2Hire - automation system.")
    author_urn = body.get("author_urn", service.author_urn)
    
    candidate_authors = []
    if author_urn:
        candidate_authors.append(author_urn)

    token_sub = await service._get_userinfo_sub()
    if token_sub:
        token_person_urn = f"urn:li:person:{token_sub}"
        if token_person_urn not in candidate_authors:
            candidate_authors.append(token_person_urn)

    if not candidate_authors:
        raise HTTPException(status_code=400, detail="author_urn required and token userinfo sub unavailable")

    headers = {
        "Authorization": f"Bearer {service.access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202501",
        "Content-Type": "application/json"
    }
    
    try:
        last_result = None
        async with httpx.AsyncClient(timeout=30) as client:
            for candidate_author in candidate_authors:
                payload = {
                    "author": candidate_author,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": post_text},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }

                r = await client.post(service.UGC_POST_URL, headers=headers, json=payload)
                if r.status_code in [200, 201, 202]:
                    return {
                        "success": True,
                        "author_used": candidate_author,
                        "status_code": r.status_code,
                        "post_id": r.headers.get('x-linkedin-id'),
                        "message": "Post published successfully!"
                    }

                last_result = {
                    "success": False,
                    "author_used": candidate_author,
                    "status_code": r.status_code,
                    "response": r.json() if r.headers.get('content-type', '').startswith('application/json') else r.text,
                    "guidance": _get_linkedin_error_guidance(r.status_code, r.text)
                }

        return last_result
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "guidance": "Check token validity and network connectivity"
        }


def _get_linkedin_error_guidance(status_code: int, error_body: str) -> str:
    """Provide helpful guidance based on LinkedIn API error."""
    guidance = {
        403: "❌ ACCESS DENIED - Token lacks 'w_member_social' scope or author_urn mismatch. Re-authorize with proper scopes.",
        422: "❌ VALIDATION ERROR - Invalid author_urn format (must be urn:li:person:<sub>, urn:li:member:<id>, or urn:li:company:<id>) or empty post text.",
        401: "❌ UNAUTHORIZED - Token expired or invalid. Re-authorize.",
        429: "❌ RATE LIMITED - Too many requests. Wait before retrying.",
    }
    return guidance.get(status_code, f"Error {status_code} - Check LinkedIn API docs for details.")


# Run with: uvicorn backend.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
