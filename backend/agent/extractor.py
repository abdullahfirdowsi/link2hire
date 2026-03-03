"""
Job data extraction agent using Azure OpenAI.
Responsible for extracting structured job information from raw text.
"""

import json
import logging
from typing import Dict, Any
from openai import AzureOpenAI
from pydantic import ValidationError

from backend.config import settings
from backend.models.job_model import ExtractedJobData, JobRole, WorkMode


logger = logging.getLogger(__name__)


class ExtractionAgent:
    """
    Agent responsible for extracting structured job data using Azure OpenAI.
    Uses strict JSON schema and temperature=0 for deterministic output.
    """
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_name = settings.azure_openai_deployment_name
        self.temperature = settings.azure_openai_temperature
        self.max_tokens = settings.azure_openai_max_tokens
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with JSON schema instructions."""
        schema_example = {
            "company": "string (required)",
            "roles": [
                {
                    "title": "string (required)",
                    "description": "string (optional)"
                }
            ],
            "location": "string (required)",
            "work_mode": "Remote | On-site | Hybrid | Unknown",
            "experience": "string (required)",
            "eligibility": "string (required)",
            "salary": "string (optional)",
            "apply_link": "string (required)",
            "deadline": "string (optional, format: YYYY-MM-DD)"
        }
        
        return f"""You are a job posting data extraction expert. Your task is to extract structured information from unstructured job postings.

INSTRUCTIONS:
1. Extract ALL relevant information from the job posting.
2. Return ONLY valid JSON matching the exact schema provided.
3. If multiple job roles are mentioned, include ALL of them in the roles array.
4. For work_mode, choose from: Remote, On-site, Hybrid, or Unknown.
5. If information is not explicitly stated, use your best judgment based on context.
6. For missing optional fields, use null or omit them entirely.
7. Ensure the apply_link is a valid URL (if not found, use the source URL or "Not specified").

REQUIRED JSON SCHEMA:
{json.dumps(schema_example, indent=2)}

CRITICAL RULES:
- Do NOT add any text before or after the JSON.
- Do NOT use markdown code blocks.
- Return raw JSON only.
- Ensure all required fields are present.
- If you detect multiple roles (e.g., "Senior Backend Engineer and Frontend Engineer"), create separate entries in the roles array.

Examples of multiple roles detection:
- "Hiring Backend Engineer and Frontend Engineer" → 2 roles
- "Looking for SDE-1/SDE-2/SDE-3" → 3 roles
- "Backend Engineer (Python/Java)" → 1 role with description"""

    def _build_user_prompt(self, raw_job_text: str) -> str:
        """Build user prompt with the raw job text."""
        return f"""Extract structured job information from the following job posting:

---
{raw_job_text}
---

Return the extracted data as JSON following the schema provided in the system prompt."""

    async def extract(self, raw_job_text: str) -> ExtractedJobData:
        """
        Extract structured job data from raw text.
        
        Args:
            raw_job_text: Unstructured job posting text
            
        Returns:
            ExtractedJobData: Validated structured job data
            
        Raises:
            ValueError: If extraction fails or data is invalid
            Exception: For API or network errors
        """
        try:
            logger.info("Starting job data extraction")
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": self._build_user_prompt(raw_job_text)}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Enforce JSON response
            )
            
            # Extract response content
            raw_response = response.choices[0].message.content
            logger.debug(f"Raw LLM response: {raw_response}")
            
            # Parse JSON
            try:
                extracted_json = json.loads(raw_response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON from extraction: {e}")
            
            # Validate and convert to Pydantic model
            try:
                extracted_data = ExtractedJobData(**extracted_json)
                logger.info(f"Successfully extracted job data with {len(extracted_data.roles)} role(s)")
                return extracted_data
            except ValidationError as e:
                logger.error(f"Validation failed: {e}")
                raise ValueError(f"Extracted data validation failed: {e}")
        
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise
    
    def extract_sync(self, raw_job_text: str) -> ExtractedJobData:
        """
        Synchronous version of extract method.
        Useful for non-async contexts.
        """
        import asyncio
        return asyncio.run(self.extract(raw_job_text))


# Singleton instance
_extractor_instance = None


def get_extraction_agent() -> ExtractionAgent:
    """Get or create singleton extraction agent instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = ExtractionAgent()
    return _extractor_instance
