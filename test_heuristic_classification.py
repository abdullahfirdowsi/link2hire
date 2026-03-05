#!/usr/bin/env python3
"""
Test job classification using heuristic method (no LLM, no Azure OpenAI dependency)
This shows how professional posts are formatted for different job types
"""

import sys
sys.path.insert(0, 'backend')

from agent.classifier import JobClassifier
from agent.professional_styles import ProfessionalPostStyles
from models.job_model import ExtractedJobData, JobRole, WorkMode

# Real job examples from LinkedIn
test_jobs = [
    {
        "title": "Software Engineer Intern",
        "company": "TechFlow AI",
        "text": """
        We are hiring Software Engineers and AI Developer Interns for our Remote internship program.
        Location: Remote
        Batch: 2025-2027 graduates
        Stipend: 30,000/month
        Apply: https://apply.techflow.io
        """
    },
    {
        "title": "Fresher Hiring Drive",
        "company": "TechCorp",
        "text": """
        TechCorp is launching a massive hiring drive for freshers.
        Multiple openings across departments.
        Salary: 4.5 - 6 LPA
        Experience needed: 0 years
        Location: Multiple cities
        """
    },
    {
        "title": "Remote Work Opportunity",
        "company": "GlobalSoft",
        "text": """
        Work from anywhere in India
        No location restrictions
        Remote-first company culture
        Flexible hours
        Annual Salary: 8 - 12 LPA
        """
    },
    {
        "title": "Mass Hiring Event",
        "company": "BigTech Solutions",
        "text": """
        We are hiring 500+ candidates
        Multiple roles: Backend, Frontend, DevOps, etc.
        Batch 2024-2025 graduates preferred
        Salary: 3.5 - 5 LPA
        Quick selection process
        """
    },
    {
        "title": "Startup Opportunity",
        "company": "InnovateLabs",
        "text": """
        Join our fast-growing startup
        Ground floor opportunity to impact product roadmap
        Work on cutting-edge AI/ML technologies
        Competitive equity + salary
        Batch: 2025-2026
        Salary: 15000-25000/month
        """
    },
    {
        "title": "Paid Internship",
        "company": "ResearchHub",
        "text": """
        Summer paid internship program
        Monthly stipend: 40,000 INR
        3-month duration, 5 days/week
        Research-focused role
        Learning opportunity for final year students
        """
    }
]

def create_job_data(title: str, company: str, salary: str) -> ExtractedJobData:
    """Create ExtractedJobData from test job info."""
    return ExtractedJobData(
        company=company,
        roles=[JobRole(title=title, description=None)],
        location="Remote",
        work_mode=WorkMode.REMOTE,
        experience="0 years",
        eligibility="2025-2027 graduates",
        salary=salary,
        apply_link="https://apply.techflow.io",
        deadline=None
    )

def main():
    print("\n" + "="*80)
    print("HEURISTIC JOB CLASSIFICATION + PROFESSIONAL POST GENERATION")
    print("="*80)
    
    classifier = JobClassifier()
    styles = ProfessionalPostStyles()
    
    for i, job in enumerate(test_jobs, 1):
        print(f"\n{'─'*80}")
        print(f"JOB #{i}: {job['title']}")
        print(f"{'─'*80}\n")
        
        # Classify using heuristic method (no LLM)
        category = classifier.heuristic_classify(job['text'])
        
        print(f"Classification: {category.name}")
        print(f"Post Style: {category.value}\n")
        
        # Create ExtractedJobData
        job_data = create_job_data(
            job['title'],
            job['company'],
            "INR 30,000-40,000/month"
        )
        
        # Generate professional post using the style for this category
        style_func = styles.get_style_for_category(category)
        post = style_func(job_data)
        
        print("GENERATED POST:")
        print(post)
        print()

if __name__ == "__main__":
    main()
