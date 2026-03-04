"""
LinkedIn post formatter agent.
Generates professional LinkedIn post text from structured job data.
Uses intelligent job classification to select appropriate tone.
"""

import logging
from typing import List
from openai import AzureOpenAI

from backend.config import settings
from backend.models.job_model import ExtractedJobData, LinkedInPost, JobRole
from backend.agent.classifier import get_job_classifier, JobCategory
from backend.agent.professional_styles import ProfessionalPostStyles


logger = logging.getLogger(__name__)


class FormatterAgent:
    """
    Agent responsible for generating LinkedIn post content
    from structured job data.
    """
    
    def __init__(self):
        """Initialize formatter with classifier for intelligent tone selection."""
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_name = settings.azure_openai_deployment_name
        self.classifier = get_job_classifier()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for LinkedIn post generation."""
        return """You are an expert LinkedIn content creator specializing in job postings.

TASK: Generate an engaging, professional LinkedIn post for a job opportunity.

GUIDELINES:
1. Start with an attention-grabbing emoji and opening line
2. Highlight the company and opportunity
3. Include key details: roles, location, experience, work mode
4. Make it conversational and exciting
5. Include a clear call-to-action
6. Keep it under 3000 characters
7. Use emojis strategically (2-4 total)
8. Create urgency if deadline is mentioned
9. End with relevant hashtags

TONE: Professional yet enthusiastic, inclusive, action-oriented

FORMAT:
- Opening hook with emoji
- 2-3 short paragraphs
- Bullet points for key details
- Call to action
- Hashtags at the end (3-5 relevant tags)

Do NOT use excessive emojis or overly casual language."""

    def _build_user_prompt(self, job_data: ExtractedJobData) -> str:
        """Build user prompt with job data."""
        roles_text = ", ".join([role.title for role in job_data.roles])
        
        deadline_text = f"Application deadline: {job_data.deadline}" if job_data.deadline else ""
        salary_text = f"Salary: {job_data.salary}" if job_data.salary else ""
        
        return f"""Generate a LinkedIn post for this job opportunity:

Company: {job_data.company}
Roles: {roles_text}
Location: {job_data.location}
Work Mode: {job_data.work_mode.value}
Experience Required: {job_data.experience}
Eligibility: {job_data.eligibility}
{salary_text}
{deadline_text}
Application Link: {job_data.apply_link}

Generate an engaging LinkedIn post that will attract qualified candidates."""

    async def format_linkedin_post(self, job_data: ExtractedJobData, raw_job_text: str = "") -> LinkedInPost:
        """
        Generate professional LinkedIn post from job data.
        Intelligently classifies job type and selects appropriate tone.
        
        Args:
            job_data: Structured job data
            raw_job_text: Original job posting text for classification
            
        Returns:
            LinkedInPost: Generated post content with hashtags
            
        Raises:
            Exception: For classification or generation errors
        """
        try:
            logger.info(f"Generating LinkedIn post for {job_data.company}")
            
            # Classify job to determine tone
            if raw_job_text:
                category = await self.classifier.classify_job(raw_job_text)
            else:
                # Fallback heuristic classification
                category = self.classifier.heuristic_classify(job_data.company)
            
            logger.info(f"Job classified as: {category.value}")
            
            # Select appropriate style based on category
            style_template = ProfessionalPostStyles.get_style_for_category(category)
            post_text = style_template(job_data)
            
            logger.info(f"LinkedIn post generated using {category.value} tone")
            
            # Extract hashtags from the generated post
            hashtags = self._extract_hashtags(post_text)
            
            return LinkedInPost(
                post_text=post_text,
                hashtags=hashtags
            )
        
        except Exception as e:
            logger.error(f"LinkedIn post generation failed: {str(e)}")
            # Fallback to professional informational style
            return self.generate_fallback_post(job_data)
    
    def _extract_hashtags(self, post_text: str) -> List[str]:
        """
        Extract hashtags from generated post text.
        
        Args:
            post_text: Generated post content
            
        Returns:
            List of hashtags without the # symbol
        """
        import re
        hashtags = re.findall(r'#(\w+)', post_text)
        return hashtags
    
    def format_linkedin_post_sync(self, job_data: ExtractedJobData) -> LinkedInPost:
        """
        Synchronous version of format_linkedin_post.
        """
        import asyncio
        return asyncio.run(self.format_linkedin_post(job_data))
    
    def format_with_category(self, job_data: ExtractedJobData, category: JobCategory) -> LinkedInPost:
        """
        Generate LinkedIn post using a specific job category tone.
        Useful for manual tone selection/overrides.
        
        Args:
            job_data: Structured job data
            category: JobCategory for tone selection
            
        Returns:
            LinkedInPost: Formatted post using specified category tone
        """
        try:
            # Get the specific category template
            style_template = ProfessionalPostStyles.get_style_for_category(category)
            post_text = style_template(job_data)
            hashtags = self._extract_hashtags(post_text)
            
            logger.info(f"LinkedIn post generated using {category.value} tone")
            
            return LinkedInPost(
                post_text=post_text,
                hashtags=hashtags
            )
        except Exception as e:
            logger.error(f"Failed to generate post with category {category.value}: {str(e)}")
            raise
    
    def generate_fallback_post(self, job_data: ExtractedJobData) -> LinkedInPost:
        """
        Generate a fallback post using professional informational style.
        Used when classification or generation fails.
        
        Args:
            job_data: Structured job data
            
        Returns:
            LinkedInPost: Professional fallback post
        """
        # Use informational style as safe default
        post_text = ProfessionalPostStyles.style_informational(job_data)
        hashtags = self._extract_hashtags(post_text)
        
        logger.info("Fallback LinkedIn post generated using informational style")
        
        return LinkedInPost(
            post_text=post_text,
            hashtags=hashtags
        )


# Singleton instance
_formatter_instance = None


def get_formatter_agent() -> FormatterAgent:
    """Get or create singleton formatter agent instance."""
    global _formatter_instance
    if _formatter_instance is None:
        _formatter_instance = FormatterAgent()
    return _formatter_instance
