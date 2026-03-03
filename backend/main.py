"""
FastAPI main application.
Defines API routes, middleware, and application lifecycle.
"""

import logging
from contextlib import asynccontextmanager
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


# Run with: uvicorn backend.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
