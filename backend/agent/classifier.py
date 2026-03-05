"""
Job Classification Agent
Classifies job postings to determine appropriate post tone and template
Uses LLM to intelligently categorize job types
"""

import logging
from enum import Enum
from typing import Optional
from openai import AzureOpenAI

from backend.config import settings

logger = logging.getLogger(__name__)


class JobCategory(str, Enum):
    """Job posting categories for tone selection."""
    INTERNSHIP = "internship"
    FRESHER_HIRING = "fresher_hiring"
    REMOTE_JOB = "remote_job"
    MASS_HIRING = "mass_hiring"
    STARTUP_JOB = "startup_job"
    PAID_INTERNSHIP = "paid_internship"
    UNKNOWN = "unknown"


class JobClassifier:
    """
    Classifies job postings to determine appropriate content tone.
    This ensures consistent, professional LinkedIn posts.
    """
    
    def __init__(self):
        """Initialize job classifier (lazy load Azure OpenAI client)."""
        self.client = None  # Lazy initialization
        self.deployment_name = settings.azure_openai_deployment_name
    
    def _ensure_client(self):
        """Lazily initialize Azure OpenAI client only when needed."""
        if self.client is None:
            try:
                self.client = AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version,
                    azure_endpoint=settings.azure_openai_endpoint
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Azure OpenAI client: {e}")
                self.client = None  # Keep as None so heuristic fallback will be used
    
    def _build_classification_prompt(self) -> str:
        """Build system prompt for job classification."""
        return """You are a job classification expert. Your task is to classify job postings into appropriate categories.

CATEGORIES:
1. internship - College students, unpaid/paid training roles, focused on learning
2. fresher_hiring - Entry-level roles for 0-2 years experience, often for 2024-2027 graduates
3. remote_job - Work-from-home roles across all experience levels
4. mass_hiring - Large-scale hiring (100+ positions), multiple locations
5. startup_job - Early-stage/growth company roles focused on innovation
6. paid_internship - Internships with significant compensation (>INR 20k/month or equivalent)
7. unknown - Cannot be classified

RULES (in priority order):
1. If stipend/salary > INR 20,000/month AND internship → paid_internship
2. If explicitly hiring 100+ positions → mass_hiring
3. If explicitly startup/early-stage company → startup_job
4. If fully remote/WFH → remote_job (unless paid_internship takes priority)
5. If targets "freshers" or "2024-2027 graduates" → fresher_hiring
6. If targets "college students" or "learning" focused → internship
7. If none match clearly → unknown

RESPONSE FORMAT:
Return ONLY the category name in lowercase (e.g., 'internship', 'fresher_hiring', 'remote_job')
Do not include explanation or additional text."""

    def _build_user_prompt(self, raw_job_text: str) -> str:
        """Build user prompt with job data for classification."""
        return f"""Classify this job posting:

{raw_job_text}

Return only the category name."""

    async def classify_job(self, raw_job_text: str) -> JobCategory:
        """
        Classify a job posting to determine appropriate tone/template.
        
        Args:
            raw_job_text: Raw job posting text
            
        Returns:
            JobCategory: Classified job category
        """
        try:
            self._ensure_client()
            
            # If client initialization failed, use heuristic fallback
            if self.client is None:
                logger.info("Using heuristic classification (Azure OpenAI unavailable)")
                return self.heuristic_classify(raw_job_text)
            
            logger.info("Classifying job posting...")
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self._build_classification_prompt()},
                    {"role": "user", "content": self._build_user_prompt(raw_job_text)}
                ],
                temperature=0.3,  # Low temp for consistent classification
                max_tokens=50
            )
            
            category_text = response.choices[0].message.content.strip().lower()
            
            # Parse category
            try:
                category = JobCategory(category_text)
                logger.info(f"Job classified as: {category.value}")
                return category
            except ValueError:
                logger.warning(f"Unknown category returned: {category_text}, defaulting to heuristic")
                return self.heuristic_classify(raw_job_text)
        
        except Exception as e:
            logger.error(f"Job classification failed: {str(e)}, using heuristic")
            return self.heuristic_classify(raw_job_text)
    
    def classify_job_sync(self, raw_job_text: str) -> JobCategory:
        """Synchronous version of classify_job."""
        import asyncio
        return asyncio.run(self.classify_job(raw_job_text))
    
    def heuristic_classify(self, raw_job_text: str) -> JobCategory:
        """
        Fallback heuristic classification when LLM fails.
        Uses keyword matching for reasonable category detection.
        
        Args:
            raw_job_text: Raw job posting text
            
        Returns:
            JobCategory: Heuristically classified category
        """
        text_lower = raw_job_text.lower()
        
        # Paid internship detection
        if "intern" in text_lower and ("20000" in text_lower or "25000" in text_lower or 
                                       "30000" in text_lower or "stipend" in text_lower):
            return JobCategory.PAID_INTERNSHIP
        
        # Mass hiring detection
        if "100+" in text_lower or "mass hiring" in text_lower or "bulk hiring" in text_lower:
            return JobCategory.MASS_HIRING
        
        # Startup detection
        if "startup" in text_lower or "early-stage" in text_lower or "growth stage" in text_lower:
            return JobCategory.STARTUP_JOB
        
        # Remote job detection
        if "remote" in text_lower and "work from home" in text_lower:
            return JobCategory.REMOTE_JOB
        
        # Fresher hiring detection
        if "fresher" in text_lower or "2024-" in text_lower or "2025-" in text_lower or \
           "2026-" in text_lower or "2027" in text_lower or "0-1 year" in text_lower or \
           "0-2 year" in text_lower:
            return JobCategory.FRESHER_HIRING
        
        # Internship detection
        if "intern" in text_lower or "college student" in text_lower:
            return JobCategory.INTERNSHIP
        
        return JobCategory.UNKNOWN


# Singleton instance
_classifier_instance = None


def get_job_classifier() -> JobClassifier:
    """Get or create singleton classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = JobClassifier()
    return _classifier_instance
