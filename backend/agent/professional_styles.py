"""
Professional LinkedIn Post Styles
Clean, informational tone that builds trust with LinkedIn audience
Tone-based templates instead of viral-optimized formats
"""

from typing import List
from backend.models.job_model import ExtractedJobData
from backend.agent.classifier import JobCategory


class ProfessionalPostStyles:
    """Professional LinkedIn post templates based on job category."""
    
    @staticmethod
    def style_informational(job_data: ExtractedJobData) -> str:
        """
        Informational Style - Used for internships
        Clean, fact-based format with minimal marketing language
        """
        roles_text = " / ".join([role.title for role in job_data.roles])
        
        post = f"""📌 {roles_text}

Company: {job_data.company}
Location: {job_data.location}
Work Mode: {job_data.work_mode.value}
Eligibility: {job_data.eligibility}
"""
        
        if job_data.salary:
            post += f"Compensation: {job_data.salary}\n"
        
        post += f"""
Apply: {job_data.apply_link}

Follow Cheran Kanth for daily job updates.

#internship #fresherjobs #hiring"""
        
        return post.strip()
    
    @staticmethod
    def style_alert(job_data: ExtractedJobData) -> str:
        """
        Alert Style - Used for fresher hiring
        Highlights urgency without sounding spammy
        """
        roles_text = " / ".join([role.title for role in job_data.roles])
        
        post = f"""Fresher Hiring: {job_data.company}

Role: {roles_text}
Location: {job_data.location}
Eligibility: {job_data.eligibility}
"""
        
        if job_data.salary:
            post += f"Salary: {job_data.salary}\n"
        
        post += f"""
Apply: {job_data.apply_link}

Follow for more opportunities.

#fresherjobs #hiring #careerstart"""
        
        return post.strip()
    
    @staticmethod
    def style_benefits(job_data: ExtractedJobData) -> str:
        """
        Benefits Style - Used for remote jobs
        Focuses on work flexibility benefits
        """
        roles_text = " / ".join([role.title for role in job_data.roles])
        
        post = f"""Remote Opportunity: {job_data.company}

Role: {roles_text}
Location: {job_data.location} (Remote)
Work Mode: {job_data.work_mode.value}
Eligibility: {job_data.eligibility}
"""
        
        if job_data.salary:
            post += f"Compensation: {job_data.salary}\n"
        
        post += f"""
Apply: {job_data.apply_link}

Work flexibly from anywhere.
Follow for daily updates.

#remotework #techJobs #fresherjobs"""
        
        return post.strip()
    
    @staticmethod
    def style_urgent(job_data: ExtractedJobData) -> str:
        """
        Urgent Style - Used for mass hiring
        Emphasizes scale and immediate opportunity (professionally)
        """
        roles_text = " / ".join([role.title for role in job_data.roles])
        
        post = f"""Mass Hiring: {job_data.company}

Multiple positions open

Roles: {roles_text}
Location: {job_data.location}
Eligibility: {job_data.eligibility}
"""
        
        if job_data.salary:
            post += f"Compensation: {job_data.salary}\n"
        
        post += f"""
Apply: {job_data.apply_link}

Follow Cheran Kanth for daily job updates.

#hiring #careergrowth #techJobs"""
        
        return post.strip()
    
    @staticmethod
    def style_innovation(job_data: ExtractedJobData) -> str:
        """
        Innovation Style - Used for startup jobs
        Highlights growth and learning potential
        """
        roles_text = " / ".join([role.title for role in job_data.roles])
        
        post = f"""Growth Opportunity: {job_data.company}

Role: {roles_text}
Location: {job_data.location}
Work Mode: {job_data.work_mode.value}
Eligibility: {job_data.eligibility}

Impact-driven role with strong learning potential.
"""
        
        if job_data.salary:
            post += f"Compensation: {job_data.salary}\n"
        
        post += f"""
Apply: {job_data.apply_link}

Follow for opportunities in growth-stage companies.

#startup #growth #careerdevelopment"""
        
        return post.strip()
    
    @staticmethod
    def style_compensation(job_data: ExtractedJobData) -> str:
        """
        Compensation Style - Used for paid internships
        Highlights monetary value professionally
        """
        roles_text = " / ".join([role.title for role in job_data.roles])
        
        post = f"""Paid Internship: {job_data.company}

Role: {roles_text}
Location: {job_data.location}
Work Mode: {job_data.work_mode.value}
Eligibility: {job_data.eligibility}
"""
        
        if job_data.salary:
            post += f"Stipend: {job_data.salary}\n"
        
        post += f"""
Earn while you learn.

Apply: {job_data.apply_link}

Follow for paid internship opportunities.

#paidinternship #internship #earn"""
        
        return post.strip()
    
    @staticmethod
    def get_style_for_category(category: JobCategory) -> callable:
        """
        Get appropriate post style based on job category.
        Maps job classifications to professional tone templates.
        
        Args:
            category: JobCategory from classifier
            
        Returns:
            Callable that generates post text
        """
        styles = {
            JobCategory.INTERNSHIP: ProfessionalPostStyles.style_informational,
            JobCategory.FRESHER_HIRING: ProfessionalPostStyles.style_alert,
            JobCategory.REMOTE_JOB: ProfessionalPostStyles.style_benefits,
            JobCategory.MASS_HIRING: ProfessionalPostStyles.style_urgent,
            JobCategory.STARTUP_JOB: ProfessionalPostStyles.style_innovation,
            JobCategory.PAID_INTERNSHIP: ProfessionalPostStyles.style_compensation,
            JobCategory.UNKNOWN: ProfessionalPostStyles.style_informational,  # Default
        }
        return styles.get(category, ProfessionalPostStyles.style_informational)
    
    @staticmethod
    def get_all_styles() -> List[callable]:
        """Get all professional post style templates."""
        return [
            ProfessionalPostStyles.style_informational,
            ProfessionalPostStyles.style_alert,
            ProfessionalPostStyles.style_benefits,
            ProfessionalPostStyles.style_urgent,
            ProfessionalPostStyles.style_innovation,
            ProfessionalPostStyles.style_compensation,
        ]
