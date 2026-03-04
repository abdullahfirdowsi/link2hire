"""
Test: Professional Post Styles by Category
Shows how different job categories generate professional, appropriate tones
"""

from backend.agent.professional_styles import ProfessionalPostStyles
from backend.agent.classifier import JobCategory
from backend.models.job_model import ExtractedJobData, JobRole, WorkMode

# Create test job data
job_data = ExtractedJobData(
    company="TechFlow AI",
    roles=[JobRole(title="Software Engineer Intern"), JobRole(title="AI Developer Intern")],
    location="Remote",
    work_mode=WorkMode.REMOTE,
    experience="Fresher/0-1 years",
    eligibility="2025-2027 graduates",
    salary="INR 30,000/month",
    apply_link="https://techflow.careers/apply"
)

def test_professional_styles():
    """Test all professional post styles."""
    
    print("\n" + "="*100)
    print("PROFESSIONAL LINKEDIN POST STYLES - JOB CATEGORY MAPPING")
    print("="*100 + "\n")
    
    categories = [
        (JobCategory.INTERNSHIP, "Informational - For college student internships"),
        (JobCategory.FRESHER_HIRING, "Alert - For entry-level fresher roles"),
        (JobCategory.REMOTE_JOB, "Benefits - Highlights remote work flexibility"),
        (JobCategory.MASS_HIRING, "Urgent - For mass hiring drives (professional)"),
        (JobCategory.STARTUP_JOB, "Innovation - Focuses on growth potential"),
        (JobCategory.PAID_INTERNSHIP, "Compensation - Emphasizes monetary benefits"),
    ]
    
    for category, description in categories:
        print(f"\n{'─'*100}")
        print(f"CATEGORY: {category.value.upper()}")
        print(f"Description: {description}")
        print(f"{'─'*100}\n")
        
        # Get style for this category
        style_template = ProfessionalPostStyles.get_style_for_category(category)
        post_text = style_template(job_data)
        
        # Display post
        print(post_text)
        
        # Stats
        char_count = len(post_text)
        line_count = post_text.count('\n') + 1
        hashtags = [tag for tag in post_text.split() if tag.startswith('#')]
        
        print(f"\n📊 Stats:")
        print(f"   • Length: {char_count} characters")
        print(f"   • Lines: {line_count}")
        print(f"   • Hashtags: {len(hashtags)} ({', '.join(hashtags)})")

if __name__ == "__main__":
    test_professional_styles()
    
    print("\n" + "="*100)
    print("✅ PROFESSIONAL POSTS - Clean, informational, trust-building format")
    print("="*100)
    print("\n💡 Key improvements over previous viral-style posts:")
    print("   1. Consistent professional tone")
    print("   2. No marketing hype ('GOLDEN opportunity', 'MASSIVE', etc.)")
    print("   3. Clear, factual information")
    print("   4. Appropriate for LinkedIn algorithm")
    print("   5. Builds credibility and trust")
    print("\n" + "="*100 + "\n")
