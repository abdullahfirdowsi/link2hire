"""
LinkedIn post formatter agent.
Generates engaging LinkedIn post text from structured job data.
"""

import logging
from typing import List
from openai import AzureOpenAI

from backend.config import settings
from backend.models.job_model import ExtractedJobData, LinkedInPost, JobRole


logger = logging.getLogger(__name__)


class FormatterAgent:
    """
    Agent responsible for generating LinkedIn post content
    from structured job data.
    """
    
    def __init__(self):
        """Initialize Azure OpenAI client for post generation."""
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_name = settings.azure_openai_deployment_name
    
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

    async def format_linkedin_post(self, job_data: ExtractedJobData) -> LinkedInPost:
        """
        Generate LinkedIn post from job data.
        
        Args:
            job_data: Structured job data
            
        Returns:
            LinkedInPost: Generated post content with hashtags
            
        Raises:
            Exception: For API or generation errors
        """
        try:
            logger.info(f"Generating LinkedIn post for {job_data.company}")
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": self._build_user_prompt(job_data)}
                ],
                temperature=0.7,  # Slightly higher for creative content
                max_tokens=1000
            )
            
            post_text = response.choices[0].message.content.strip()
            
            # Extract hashtags from the generated post
            hashtags = self._extract_hashtags(post_text)
            
            logger.info("LinkedIn post generated successfully")
            
            return LinkedInPost(
                post_text=post_text,
                hashtags=hashtags
            )
        
        except Exception as e:
            logger.error(f"LinkedIn post generation failed: {str(e)}")
            raise
    
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
    
    def generate_fallback_post(self, job_data: ExtractedJobData) -> LinkedInPost:
        """
        Generate a simple fallback post without AI.
        Used when AI generation fails.
        
        Args:
            job_data: Structured job data
            
        Returns:
            LinkedInPost: Basic formatted post
        """
        roles_text = " and ".join([role.title for role in job_data.roles])
        
        post_text = f"""🚀 Exciting Opportunity at {job_data.company}!

We're looking for talented individuals to join as {roles_text}.

📍 Location: {job_data.location}
💼 Work Mode: {job_data.work_mode.value}
🎯 Experience: {job_data.experience}
✅ Eligibility: {job_data.eligibility}
"""
        
        if job_data.salary:
            post_text += f"💰 Compensation: {job_data.salary}\n"
        
        if job_data.deadline:
            post_text += f"⏰ Deadline: {job_data.deadline}\n"
        
        post_text += f"""
🔗 Apply now: {job_data.apply_link}

#hiring #jobopportunity #careers #techJobs"""
        
        return LinkedInPost(
            post_text=post_text,
            hashtags=["hiring", "jobopportunity", "careers", "techJobs"]
        )


# Singleton instance
_formatter_instance = None


def get_formatter_agent() -> FormatterAgent:
    """Get or create singleton formatter agent instance."""
    global _formatter_instance
    if _formatter_instance is None:
        _formatter_instance = FormatterAgent()
    return _formatter_instance
