"""
Google Sheets service for job data synchronization.
Appends structured job entries to Google Sheets for tracking.
"""

import logging
from typing import Optional, List, Dict, Any
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

from backend.config import settings
from backend.models.job_model import ExtractedJobData, JobRole


logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """
    Service for Google Sheets integration.
    Handles appending job entries to a tracking spreadsheet.
    """
    
    # Google Sheets API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Sheet header columns
    HEADER_COLUMNS = [
        "Date Added",
        "Company",
        "Role(s)",
        "Location",
        "Work Mode",
        "Experience",
        "Eligibility",
        "Salary",
        "Apply Link",
        "Deadline",
        "Posted to LinkedIn"
    ]
    
    def __init__(self):
        """Initialize Google Sheets service."""
        self.client: Optional[gspread.Client] = None
        self.spreadsheet = None
        self.worksheet = None
        self._initialized = False
    
    def _initialize_client(self):
        """Initialize Google Sheets client with service account."""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing Google Sheets client...")
            
            # Load service account credentials
            credentials = Credentials.from_service_account_file(
                settings.google_sheets_credentials_path,
                scopes=self.SCOPES
            )
            
            # Create gspread client
            self.client = gspread.authorize(credentials)
            
            # Open spreadsheet
            self.spreadsheet = self.client.open_by_key(
                settings.google_sheets_spreadsheet_id
            )
            
            # Get or create worksheet
            try:
                self.worksheet = self.spreadsheet.worksheet(
                    settings.google_sheets_worksheet_name
                )
            except WorksheetNotFound:
                logger.info(f"Worksheet '{settings.google_sheets_worksheet_name}' not found, creating...")
                self.worksheet = self.spreadsheet.add_worksheet(
                    title=settings.google_sheets_worksheet_name,
                    rows=1000,
                    cols=len(self.HEADER_COLUMNS)
                )
                # Add header row
                self.worksheet.append_row(self.HEADER_COLUMNS)
            
            self._initialized = True
            logger.info("Google Sheets client initialized successfully")
        
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {settings.google_sheets_credentials_path}")
            raise
        except SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found: {settings.google_sheets_spreadsheet_id}")
            raise
        except Exception as e:
            logger.error(f"Google Sheets initialization failed: {str(e)}")
            raise
    
    def _format_roles_text(self, roles: List[JobRole]) -> str:
        """
        Format roles list into readable text.
        
        Args:
            roles: List of job roles
            
        Returns:
            Formatted roles string
        """
        if len(roles) == 1:
            return roles[0].title
        
        return ", ".join([role.title for role in roles])
    
    async def append_job_entry(self, job_data: ExtractedJobData) -> bool:
        """
        Append job entry to Google Sheets.
        
        Args:
            job_data: Structured job data to append
            
        Returns:
            True if successful
            
        Raises:
            Exception: For Google Sheets API errors
        """
        try:
            # Initialize client if not already done
            self._initialize_client()
            
            logger.info(f"Appending job entry to Google Sheets: {job_data.company}")
            
            # Prepare row data
            from datetime import datetime
            row_data = [
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),  # Date Added
                job_data.company,
                self._format_roles_text(job_data.roles),
                job_data.location,
                job_data.work_mode.value,
                job_data.experience,
                job_data.eligibility,
                job_data.salary or "Not specified",
                job_data.apply_link,
                job_data.deadline or "Not specified",
                "No"  # Posted to LinkedIn (default)
            ]
            
            # Append row
            self.worksheet.append_row(row_data)
            
            logger.info("Job entry appended to Google Sheets successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to append to Google Sheets: {str(e)}")
            raise
    
    def append_job_entry_sync(self, job_data: ExtractedJobData) -> bool:
        """
        Synchronous version of append_job_entry.
        """
        import asyncio
        return asyncio.run(self.append_job_entry(job_data))
    
    async def update_linkedin_status(
        self,
        company: str,
        role: str,
        posted: bool = True
    ) -> bool:
        """
        Update LinkedIn posting status for a job entry.
        
        Args:
            company: Company name to search for
            role: Role title to search for
            posted: New posting status
            
        Returns:
            True if successful
        """
        try:
            self._initialize_client()
            
            logger.info(f"Updating LinkedIn status for {company} - {role}")
            
            # Find the row
            cell = self.worksheet.find(company)
            if cell:
                row_number = cell.row
                # Update Posted to LinkedIn column (last column)
                self.worksheet.update_cell(
                    row_number,
                    len(self.HEADER_COLUMNS),
                    "Yes" if posted else "No"
                )
                logger.info(f"LinkedIn status updated for row {row_number}")
                return True
            
            logger.warning(f"Job entry not found in sheets: {company} - {role}")
            return False
        
        except Exception as e:
            logger.error(f"Failed to update LinkedIn status: {str(e)}")
            return False
    
    async def get_all_entries(self) -> List[Dict[str, Any]]:
        """
        Retrieve all entries from the sheet.
        
        Returns:
            List of job entry dictionaries
        """
        try:
            self._initialize_client()
            
            # Get all records as dictionaries
            records = self.worksheet.get_all_records()
            
            logger.info(f"Retrieved {len(records)} entries from Google Sheets")
            return records
        
        except Exception as e:
            logger.error(f"Failed to retrieve entries: {str(e)}")
            raise
    
    def clear_worksheet(self) -> bool:
        """
        Clear all data except header row.
        Use with caution!
        
        Returns:
            True if successful
        """
        try:
            self._initialize_client()
            
            logger.warning("Clearing worksheet data (keeping header)")
            self.worksheet.delete_rows(2, self.worksheet.row_count)
            
            logger.info("Worksheet cleared successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear worksheet: {str(e)}")
            return False


# Singleton instance
_sheets_service_instance = None


def get_sheets_service() -> GoogleSheetsService:
    """Get or create singleton Google Sheets service instance."""
    global _sheets_service_instance
    if _sheets_service_instance is None:
        _sheets_service_instance = GoogleSheetsService()
    return _sheets_service_instance
