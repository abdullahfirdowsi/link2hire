"""
Test: Intelligent Job Classification + Professional Post Generation
Tests that different job types get appropriate professional tones
"""

from backend.agent.classifier import JobClassifier, JobCategory
from backend.agent.professional_styles import ProfessionalPostStyles
from backend.models.job_model import ExtractedJobData, JobRole, WorkMode

# Test job classifications
TEST_JOBS = {
    "internship": """Company: PGAGI
Role: AI/ML Intern
Batch Eligible: All college students
Expected Stipend: INR 20K per month
Location: Remote
Experience: Fresher/0-1 years
Apply Link: https://bit.ly/4aAehNf""",
    
    "fresher": """Company: Siemens
Role: Software Engineering Intern
Batch Eligible: 2026 & 2027 graduates
Experience: Fresher
Location: Noida
Apply Link: https://bit.ly/4c8tvvr""",
    
    "remote": """Company: Zenix Automotive
Role: App Developer Intern
Location: Remote (Work From Home)
Experience: Fresher
Apply Link: https://bit.ly/4rpR5Z5""",
    
    "paid_internship": """Company: Deconstruct Skincare
Role: Internship
Location: India
Salary: INR 1,00,000 stipend per month
Experience: Fresher
Apply Link: https://bit.ly/DeconstructIntern""",
    
    "mass_hiring": """Company: TCS (Tata Consultancy Services)
Role: Systems Engineer Intern
Location: Pan India (Multiple Locations)
Experience: Fresher
Salary: Competitive
Apply Link: https://www.tcs.com/careers
Note: Mass hiring drive with 100+ positions"""
}

async def test_classification_and_posts():
    """Test job classification and post generation."""
    
    print("\n" + "="*100)
    print("INTELLIGENT JOB CLASSIFICATION + PROFESSIONAL POST GENERATION TEST")
    print("="*100 + "\n")
    
    classifier = JobClassifier()
    
    for job_type, raw_text in TEST_JOBS.items():
        print(f"\n{'─'*100}")
        print(f"TEST: {job_type.upper()}")
        print(f"{'─'*100}\n")
        
        # Classify job
        category = await classifier.classify_job(raw_text)
        print(f"✅ Classified as: {category.value.upper()}")
        
        # Create sample job data
        job_data = ExtractedJobData(
            company="Test Company",
            roles=[JobRole(title="Test Role")],
            location="Remote",
            work_mode=WorkMode.REMOTE,
            experience="Fresher",
            eligibility="All students",
            salary="Competitive",
            apply_link="https://example.com"
        )
        
        # Generate post using the classified category
        style_template = ProfessionalPostStyles.get_style_for_category(category)
        post_text = style_template(job_data)
        
        print(f"\n📱 Professional Post:\n")
        print(post_text)
        print(f"\n📊 Post stats: {len(post_text)} characters, {post_text.count(chr(10)) + 1} lines")

if __name__ == "__main__":
    import asyncio
    
    try:
        asyncio.run(test_classification_and_posts())
        print("\n\n" + "="*100)
        print("✅ TEST COMPLETE - Classification and professional post generation working!")
        print("="*100 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
