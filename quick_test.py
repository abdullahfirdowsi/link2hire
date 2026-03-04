"""
Simple Test: Get one job response to check structure
"""

import httpx
import json

SAMPLE_JOB = """Company: TechFlow AI
Role: Software Engineer Intern
Salary: INR 30,000 per month
Location: Remote
Experience: Fresher
Apply: https://example.com"""

response = httpx.post(
    "http://localhost:8000/process-job",
    json={"raw_job_text": SAMPLE_JOB}
)

print("Status Code:", response.status_code)
print("\nFull Response:")
data = response.json()
print(json.dumps(data, indent=2))
