"""
Orchestrator for coordinating the entire job processing workflow.
Manages conversation state, agent coordination, and service integration.
"""

import logging
import uuid
from typing import Optional, Tuple
from datetime import datetime

from backend.models.job_model import (
    ExtractedJobData,
    DecisionOutput,
    ClarificationChoice,
    ConversationState,
    Conversation,
    JobEntry,
    LinkedInPost,
    ProcessingResponse,
    JobRole
)
from backend.agent.extractor import get_extraction_agent
from backend.agent.decision import get_decision_agent
from backend.agent.formatter import get_formatter_agent
from backend.agent.validator import get_validation_agent
from backend.services.mongodb_service import get_mongodb_service
from backend.services.sheets_service import get_sheets_service
from backend.services.linkedin_service import get_linkedin_service


logger = logging.getLogger(__name__)


class JobProcessingOrchestrator:
    """
    Central orchestrator that coordinates the entire job processing workflow.
    
    Responsibilities:
    1. Manage conversation state
    2. Coordinate agent execution (extraction, decision, validation, formatting)
    3. Coordinate service execution (MongoDB, Google Sheets, LinkedIn)
    4. Handle error recovery and retries
    5. Maintain clean separation between agents and services
    """
    
    def __init__(self):
        """Initialize orchestrator with all agents and services."""
        # Initialize agents
        self.extractor = get_extraction_agent()
        self.decision_agent = get_decision_agent()
        self.formatter = get_formatter_agent()
        self.validator = get_validation_agent()
        
        # Initialize services
        self.mongodb_service = get_mongodb_service()
        self.sheets_service = get_sheets_service()
        self.linkedin_service = get_linkedin_service()
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID."""
        return f"conv_{uuid.uuid4().hex[:12]}"
    
    def _generate_job_id(self) -> str:
        """Generate unique job entry ID."""
        return f"job_{uuid.uuid4().hex[:12]}"
    
    async def process_initial_request(
        self,
        raw_job_text: str,
        user_context: Optional[dict] = None
    ) -> ProcessingResponse:
        """
        Process initial job posting request.
        
        Workflow:
        1. Create conversation state
        2. Extract structured data
        3. Validate extracted data
        4. Make decision (clarification needed?)
        5. If no clarification needed, proceed to execution
        6. If clarification needed, return to user
        
        Args:
            raw_job_text: Raw job posting text
            user_context: Optional user context
            
        Returns:
            ProcessingResponse with next steps
        """
        conversation_id = self._generate_conversation_id()
        
        try:
            logger.info(f"Starting initial request processing: {conversation_id}")
            
            # Step 1: Extract structured data
            logger.info("Step 1: Extracting structured data")
            extracted_data = await self.extractor.extract(raw_job_text)
            logger.info(f"Extracted data for {len(extracted_data.roles)} role(s)")
            
            # Step 2: Validate extracted data
            logger.info("Step 2: Validating extracted data")
            is_valid, validation_errors = await self.validator.validate(extracted_data)
            
            if not is_valid:
                logger.warning(f"Validation failed: {validation_errors}")
                # Store failed state
                conversation = Conversation(
                    conversation_id=conversation_id,
                    state=ConversationState.ERROR,
                    raw_input=raw_job_text,
                    extracted_data=extracted_data
                )
                await self.mongodb_service.save_conversation(conversation)
                
                return ProcessingResponse(
                    success=False,
                    message=f"Data validation failed: {'; '.join(validation_errors)}",
                    conversation_id=conversation_id,
                    state=ConversationState.ERROR
                )
            
            # Step 3: Make decision
            logger.info("Step 3: Making decision")
            decision_output = await self.decision_agent.decide(extracted_data)
            
            # Step 4: Save conversation state
            conversation = Conversation(
                conversation_id=conversation_id,
                state=ConversationState.AWAITING_CLARIFICATION if decision_output.requires_clarification else ConversationState.PROCESSING,
                raw_input=raw_job_text,
                extracted_data=extracted_data,
                decision_output=decision_output
            )
            await self.mongodb_service.save_conversation(conversation)
            logger.info(f"Conversation state saved: {conversation.state}")
            
            # Step 5: Check if clarification is needed
            if decision_output.requires_clarification:
                logger.info("Clarification required, returning to user")
                return ProcessingResponse(
                    success=True,
                    message="Clarification needed before proceeding.",
                    conversation_id=conversation_id,
                    state=ConversationState.AWAITING_CLARIFICATION,
                    requires_clarification=True,
                    clarification_message=decision_output.clarification_message
                )
            
            # Step 6: No clarification needed, proceed with execution
            logger.info("No clarification needed, proceeding with execution")
            return await self._execute_job_processing(
                conversation_id,
                extracted_data,
                ClarificationChoice.COMBINED  # Default to combined if only one role
            )
        
        except Exception as e:
            logger.error(f"Initial request processing failed: {str(e)}", exc_info=True)
            
            # Try to save error state
            try:
                conversation = Conversation(
                    conversation_id=conversation_id,
                    state=ConversationState.ERROR,
                    raw_input=raw_job_text
                )
                await self.mongodb_service.save_conversation(conversation)
            except:
                pass
            
            return ProcessingResponse(
                success=False,
                message=f"Processing failed: {str(e)}",
                conversation_id=conversation_id,
                state=ConversationState.ERROR
            )
    
    async def process_clarification_response(
        self,
        conversation_id: str,
        choice: ClarificationChoice
    ) -> ProcessingResponse:
        """
        Process user's clarification response and continue workflow.
        
        Args:
            conversation_id: Conversation identifier
            choice: User's clarification choice
            
        Returns:
            ProcessingResponse with execution results
        """
        try:
            logger.info(f"Processing clarification response for {conversation_id}: {choice}")
            
            # Step 1: Retrieve conversation state
            conversation = await self.mongodb_service.get_conversation(conversation_id)
            
            if not conversation:
                return ProcessingResponse(
                    success=False,
                    message="Conversation not found",
                    conversation_id=conversation_id,
                    state=ConversationState.ERROR
                )
            
            if conversation.state != ConversationState.AWAITING_CLARIFICATION:
                return ProcessingResponse(
                    success=False,
                    message=f"Invalid conversation state: {conversation.state}",
                    conversation_id=conversation_id,
                    state=conversation.state
                )
            
            # Step 2: Update conversation with user choice
            conversation.user_choice = choice
            conversation.state = ConversationState.PROCESSING
            conversation.updated_at = datetime.utcnow()
            await self.mongodb_service.update_conversation(conversation)
            
            # Step 3: Execute job processing
            return await self._execute_job_processing(
                conversation_id,
                conversation.extracted_data,
                choice
            )
        
        except Exception as e:
            logger.error(f"Clarification response processing failed: {str(e)}", exc_info=True)
            
            return ProcessingResponse(
                success=False,
                message=f"Processing failed: {str(e)}",
                conversation_id=conversation_id,
                state=ConversationState.ERROR
            )
    
    async def _execute_job_processing(
        self,
        conversation_id: str,
        extracted_data: ExtractedJobData,
        user_choice: ClarificationChoice
    ) -> ProcessingResponse:
        """
        Execute the complete job processing workflow.
        
        Steps:
        1. Create job entries (combined or separate based on choice)
        2. Generate LinkedIn posts
        3. Save to MongoDB
        4. Append to Google Sheets
        5. Update conversation state to completed
        
        Args:
            conversation_id: Conversation identifier
            extracted_data: Validated extracted data
            user_choice: User's clarification choice
            
        Returns:
            ProcessingResponse with execution results
        """
        job_entry_ids = []
        
        try:
            logger.info(f"Executing job processing: {conversation_id}, choice: {user_choice}")
            
            # Step 1: Determine job entries to create
            if user_choice == ClarificationChoice.COMBINED or len(extracted_data.roles) == 1:
                # Create single combined entry
                logger.info("Creating combined job entry")
                job_entries = [await self._create_job_entry(conversation_id, extracted_data)]
            else:
                # Create separate entries for each role
                logger.info(f"Creating {len(extracted_data.roles)} separate job entries")
                job_entries = []
                for role in extracted_data.roles:
                    # Create a copy of extracted data with single role
                    single_role_data = ExtractedJobData(
                        company=extracted_data.company,
                        roles=[role],
                        location=extracted_data.location,
                        work_mode=extracted_data.work_mode,
                        experience=extracted_data.experience,
                        eligibility=extracted_data.eligibility,
                        salary=extracted_data.salary,
                        apply_link=extracted_data.apply_link,
                        deadline=extracted_data.deadline
                    )
                    job_entry = await self._create_job_entry(conversation_id, single_role_data)
                    job_entries.append(job_entry)
            
            # Step 2: Process each job entry
            for job_entry in job_entries:
                # Generate LinkedIn post
                logger.info(f"Generating LinkedIn post for {job_entry.id}")
                linkedin_post = await self.formatter.format_linkedin_post(job_entry.extracted_data)
                job_entry.linkedin_post = linkedin_post
                
                # Save to MongoDB
                logger.info(f"Saving job entry to MongoDB: {job_entry.id}")
                saved_entry = await self.mongodb_service.save_job_entry(job_entry)
                job_entry_ids.append(saved_entry["_id"])
                
                # Append to Google Sheets
                logger.info(f"Appending to Google Sheets: {job_entry.id}")
                try:
                    sheet_result = await self.sheets_service.append_job_entry(job_entry.extracted_data)
                    if sheet_result:
                        job_entry.posted_to_sheets = True
                        await self.mongodb_service.update_job_entry(job_entry)
                except Exception as sheet_error:
                    logger.error(f"Google Sheets append failed: {sheet_error}")
                    # Continue even if sheets fails - don't block the workflow
            
            # Step 3: Update conversation state to completed
            conversation = await self.mongodb_service.get_conversation(conversation_id)
            conversation.state = ConversationState.COMPLETED
            conversation.job_entry_ids = job_entry_ids
            conversation.updated_at = datetime.utcnow()
            await self.mongodb_service.update_conversation(conversation)
            
            # Step 4: Return success response
            logger.info(f"Job processing completed successfully: {len(job_entries)} entries created")
            
            return ProcessingResponse(
                success=True,
                message=f"✅ Successfully processed {len(job_entries)} job {'entry' if len(job_entries) == 1 else 'entries'}! Data saved to database and Google Sheets.",
                conversation_id=conversation_id,
                state=ConversationState.COMPLETED,
                requires_clarification=False,
                job_entries_created=job_entry_ids,
                linkedin_post=job_entries[0].linkedin_post if job_entries else None
            )
        
        except Exception as e:
            logger.error(f"Job processing execution failed: {str(e)}", exc_info=True)
            
            # Update conversation state to error
            try:
                conversation = await self.mongodb_service.get_conversation(conversation_id)
                conversation.state = ConversationState.ERROR
                conversation.updated_at = datetime.utcnow()
                await self.mongodb_service.update_conversation(conversation)
            except:
                pass
            
            return ProcessingResponse(
                success=False,
                message=f"Execution failed: {str(e)}",
                conversation_id=conversation_id,
                state=ConversationState.ERROR
            )
    
    async def _create_job_entry(
        self,
        conversation_id: str,
        extracted_data: ExtractedJobData
    ) -> JobEntry:
        """
        Create a JobEntry object from extracted data.
        
        Args:
            conversation_id: Related conversation ID
            extracted_data: Structured job data
            
        Returns:
            JobEntry object
        """
        job_id = self._generate_job_id()
        
        return JobEntry(
            id=job_id,
            conversation_id=conversation_id,
            raw_input="",  # Will be set from conversation if needed
            extracted_data=extracted_data,
            posted_to_sheets=False,
            posted_to_linkedin=False
        )


# Singleton instance
_orchestrator_instance = None


def get_orchestrator() -> JobProcessingOrchestrator:
    """Get or create singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = JobProcessingOrchestrator()
    return _orchestrator_instance
