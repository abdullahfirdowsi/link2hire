"""
Validation agent for job data quality checks.
Ensures data integrity before storage and posting.
"""

import logging
import re
from typing import List, Tuple, Dict, Any
from urllib.parse import urlparse

from backend.models.job_model import ExtractedJobData, JobRole


logger = logging.getLogger(__name__)


class ValidationAgent:
    """
    Agent responsible for validating extracted job data quality.
    Performs business logic validation beyond Pydantic schema validation.
    """
    
    # Common invalid/placeholder values
    INVALID_PLACEHOLDERS = [
        "not specified",
        "n/a",
        "na",
        "none",
        "null",
        "unknown",
        "tbd",
        "to be determined",
        ""
    ]
    
    def __init__(self):
        """Initialize validation agent."""
        pass
    
    def _validate_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate URL format and structure.
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                if result.scheme in ['http', 'https']:
                    return True, ""
                else:
                    return False, f"Invalid URL scheme: {result.scheme}"
            else:
                return False, "URL missing scheme or domain"
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"
    
    def _validate_company_name(self, company: str) -> Tuple[bool, str]:
        """
        Validate company name.
        
        Args:
            company: Company name string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not company or company.strip() == "":
            return False, "Company name is empty"
        
        if company.lower().strip() in self.INVALID_PLACEHOLDERS:
            return False, f"Company name is invalid: {company}"
        
        if len(company) < 2:
            return False, "Company name too short"
        
        return True, ""
    
    def _validate_roles(self, roles: List[JobRole]) -> Tuple[bool, str]:
        """
        Validate job roles.
        
        Args:
            roles: List of job roles
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not roles or len(roles) == 0:
            return False, "No roles specified"
        
        for idx, role in enumerate(roles):
            if not role.title or role.title.strip() == "":
                return False, f"Role {idx + 1} has empty title"
            
            if role.title.lower().strip() in self.INVALID_PLACEHOLDERS:
                return False, f"Role {idx + 1} has invalid title: {role.title}"
        
        return True, ""
    
    def _validate_location(self, location: str) -> Tuple[bool, str]:
        """
        Validate location string.
        
        Args:
            location: Location string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not location or location.strip() == "":
            return False, "Location is empty"
        
        if location.lower().strip() in self.INVALID_PLACEHOLDERS:
            return False, f"Location is invalid: {location}"
        
        return True, ""
    
    def _validate_experience(self, experience: str) -> Tuple[bool, str]:
        """
        Validate experience requirement.
        
        Args:
            experience: Experience requirement string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not experience or experience.strip() == "":
            return False, "Experience is empty"
        
        if experience.lower().strip() in self.INVALID_PLACEHOLDERS:
            return False, f"Experience is invalid: {experience}"
        
        return True, ""
    
    def _validate_deadline(self, deadline: str) -> Tuple[bool, str]:
        """
        Validate deadline format (optional field).
        
        Args:
            deadline: Deadline string (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not deadline:
            return True, ""  # Deadline is optional
        
        # Check for common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY or MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, deadline):
                return True, ""
        
        # If no pattern matches, it might still be a valid description
        # like "End of month" or "Rolling basis"
        return True, ""
    
    async def validate(self, job_data: ExtractedJobData) -> Tuple[bool, List[str]]:
        """
        Perform comprehensive validation on extracted job data.
        
        Args:
            job_data: Extracted job data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        logger.info("Starting job data validation")
        
        # Validate company
        valid, error = self._validate_company_name(job_data.company)
        if not valid:
            errors.append(f"Company: {error}")
        
        # Validate roles
        valid, error = self._validate_roles(job_data.roles)
        if not valid:
            errors.append(f"Roles: {error}")
        
        # Validate location
        valid, error = self._validate_location(job_data.location)
        if not valid:
            errors.append(f"Location: {error}")
        
        # Validate experience
        valid, error = self._validate_experience(job_data.experience)
        if not valid:
            errors.append(f"Experience: {error}")
        
        # Validate apply link
        valid, error = self._validate_url(job_data.apply_link)
        if not valid:
            errors.append(f"Apply Link: {error}")
        
        # Validate deadline (optional)
        if job_data.deadline:
            valid, error = self._validate_deadline(job_data.deadline)
            if not valid:
                errors.append(f"Deadline: {error}")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("Validation passed")
        else:
            logger.warning(f"Validation failed with {len(errors)} error(s)")
            for error in errors:
                logger.warning(f"  - {error}")
        
        return is_valid, errors
    
    def validate_sync(self, job_data: ExtractedJobData) -> Tuple[bool, List[str]]:
        """
        Synchronous version of validate method.
        """
        import asyncio
        return asyncio.run(self.validate(job_data))
    
    def get_validation_summary(self, job_data: ExtractedJobData) -> Dict[str, Any]:
        """
        Get a validation summary with quality metrics.
        
        Args:
            job_data: Extracted job data
            
        Returns:
            Dictionary with validation metrics
        """
        is_valid, errors = self.validate_sync(job_data)
        
        return {
            "is_valid": is_valid,
            "error_count": len(errors),
            "errors": errors,
            "quality_score": 100 - (len(errors) * 10),  # Simple quality score
            "has_optional_fields": {
                "salary": bool(job_data.salary),
                "deadline": bool(job_data.deadline)
            },
            "roles_count": len(job_data.roles)
        }


# Singleton instance
_validator_instance = None


def get_validation_agent() -> ValidationAgent:
    """Get or create singleton validation agent instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ValidationAgent()
    return _validator_instance
