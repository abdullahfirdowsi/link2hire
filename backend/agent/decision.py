"""
Decision agent for determining clarification requirements.
Analyzes extracted job data and decides whether user input is needed.
"""

import logging
from typing import List

from backend.models.job_model import ExtractedJobData, DecisionOutput


logger = logging.getLogger(__name__)


class DecisionAgent:
    """
    Agent responsible for analyzing extracted data and determining
    if clarification is needed from the user.
    """
    
    # Fields that are required and must not be empty
    REQUIRED_FIELDS = [
        "company",
        "location",
        "experience",
        "eligibility",
        "apply_link"
    ]
    
    # Threshold for multiple roles requiring clarification
    MULTIPLE_ROLES_THRESHOLD = 2
    
    def __init__(self):
        """Initialize decision agent."""
        pass
    
    def _check_missing_fields(self, extracted_data: ExtractedJobData) -> List[str]:
        """
        Check for missing or empty required fields.
        
        Args:
            extracted_data: Extracted job data
            
        Returns:
            List of missing field names
        """
        missing = []
        
        for field in self.REQUIRED_FIELDS:
            value = getattr(extracted_data, field, None)
            if not value or (isinstance(value, str) and value.strip() == ""):
                missing.append(field)
        
        # Check if roles array is empty
        if not extracted_data.roles or len(extracted_data.roles) == 0:
            missing.append("roles")
        
        return missing
    
    def _build_clarification_message(
        self,
        roles_count: int,
        missing_fields: List[str]
    ) -> str:
        """
        Build a human-friendly clarification message.
        
        Args:
            roles_count: Number of detected roles
            missing_fields: List of missing required fields
            
        Returns:
            Clarification message string
        """
        messages = []
        
        # Multiple roles clarification
        if roles_count >= self.MULTIPLE_ROLES_THRESHOLD:
            messages.append(
                f"🎯 Detected {roles_count} roles in this job posting.\n"
                f"Would you like to create:\n"
                f"  • **Combined entry**: Single job posting with all {roles_count} roles\n"
                f"  • **Separate entries**: {roles_count} individual job postings\n\n"
                f"Please respond with 'combined' or 'separate'."
            )
        
        # Missing fields clarification
        if missing_fields:
            field_list = ", ".join(missing_fields)
            messages.append(
                f"⚠️ Missing required information: {field_list}\n"
                f"Please provide the missing details to proceed."
            )
        
        return "\n\n".join(messages)
    
    async def decide(self, extracted_data: ExtractedJobData) -> DecisionOutput:
        """
        Analyze extracted data and determine if clarification is needed.
        
        Args:
            extracted_data: Extracted job data to analyze
            
        Returns:
            DecisionOutput: Decision result with clarification details
        """
        try:
            logger.info("Starting decision analysis")
            
            roles_count = len(extracted_data.roles)
            missing_fields = self._check_missing_fields(extracted_data)
            
            logger.debug(f"Detected {roles_count} role(s)")
            logger.debug(f"Missing fields: {missing_fields}")
            
            # Determine if clarification is needed
            requires_clarification = (
                roles_count >= self.MULTIPLE_ROLES_THRESHOLD or
                len(missing_fields) > 0
            )
            
            # Build clarification message
            clarification_message = None
            if requires_clarification:
                clarification_message = self._build_clarification_message(
                    roles_count,
                    missing_fields
                )
            
            # Create decision output
            decision = DecisionOutput(
                requires_clarification=requires_clarification,
                clarification_message=clarification_message,
                can_proceed=not requires_clarification,
                detected_roles_count=roles_count,
                missing_fields=missing_fields
            )
            
            logger.info(
                f"Decision complete: requires_clarification={requires_clarification}, "
                f"can_proceed={decision.can_proceed}"
            )
            
            return decision
        
        except Exception as e:
            logger.error(f"Decision analysis failed: {str(e)}")
            raise
    
    def decide_sync(self, extracted_data: ExtractedJobData) -> DecisionOutput:
        """
        Synchronous version of decide method.
        """
        import asyncio
        return asyncio.run(self.decide(extracted_data))
    
    def process_clarification_response(
        self,
        decision_output: DecisionOutput,
        user_response: str
    ) -> bool:
        """
        Process user's clarification response and validate it.
        
        Args:
            decision_output: Original decision output
            user_response: User's response text
            
        Returns:
            True if response is valid and processing can continue
        """
        user_response = user_response.strip().lower()
        
        # If clarification was about multiple roles
        if decision_output.detected_roles_count >= self.MULTIPLE_ROLES_THRESHOLD:
            if user_response in ["combined", "separate"]:
                logger.info(f"Valid clarification response: {user_response}")
                return True
            else:
                logger.warning(f"Invalid clarification response: {user_response}")
                return False
        
        # If clarification was about missing fields
        if decision_output.missing_fields:
            # In this case, we'd need additional logic to validate
            # the provided information. For now, assume valid.
            return True
        
        return True


# Singleton instance
_decision_agent_instance = None


def get_decision_agent() -> DecisionAgent:
    """Get or create singleton decision agent instance."""
    global _decision_agent_instance
    if _decision_agent_instance is None:
        _decision_agent_instance = DecisionAgent()
    return _decision_agent_instance
