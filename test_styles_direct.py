"""Test post styles generation"""
from backend.agent.post_styles import LinkedInPostStyles
from backend.models.job_model import ExtractedJobData, JobRole, WorkMode

# Create test job data
job_data = ExtractedJobData(
    company="TechFlow AI",
    roles=[JobRole(title="Software Engineer Intern")],
    location="Remote",
    work_mode=WorkMode.REMOTE,
    experience="Fresher",
    eligibility="2025-2027 graduates",
    salary="INR 30,000/month",
    apply_link="https://example.com"
)

# Test all 10 styles
for i in range(1, 11):
    template = LinkedInPostStyles.get_style_by_number(i)
    post = template(job_data)
    print(f"\n{'='*60}")
    print(f"STYLE #{i}")
    print(f"{'='*60}")
    print(post[:200] + "..." if len(post) > 200 else post)
    print(f"\nLength: {len(post)} characters")

print("\n\nAll styles generated successfully!")
