"""
Test Script: Send 10 Real Jobs to Link2Hire API
Tests automatic post style rotation (1-10 unique styles)
Run this after starting both backend and frontend
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
API_ENDPOINT = f"{BACKEND_URL}/process-job"

# 10 Real Jobs from Krishan Kumar's LinkedIn Posts
JOBS = [
    {
        "raw_job_text": """Company: PGAGI
Role: AI/ML Intern
Salary: INR 20K per month
Batch Eligible: All college students
Location: Remote (Work From Home)
Experience: Fresher/0-1 years
Apply Link: https://bit.ly/4aAehNf"""
    },
    {
        "raw_job_text": """Company: MackyTech 
Role: Software Developer Intern
Batch Eligible: All college students
Location: Remote (Work From Home)
Experience: Fresher
Apply Link: https://bit.ly/4rSyvsH"""
    },
    {
        "raw_job_text": """Company: Zenix Automotive
Role: App Developer Intern
Batch Eligible: All college students
Location: Remote (Work From Home)
Experience: Fresher/0-1 years
Apply Link: https://bit.ly/4rpR5Z5"""
    },
    {
        "raw_job_text": """Company: Brick & Bolt
Role: Software Engineer Intern 
Batch Eligible: 2025 & 2026 graduates
Experience: Fresher
Location: India
Apply Link: https://www.linkedin.com/jobs/view/4374388719/"""
    },
    {
        "raw_job_text": """Company: Confluent Solutions (Unstop Trusted)
Role: Fullstack Developer Intern
Batch Eligible: All college students
Location: Remote (Work From Home)
Experience: Fresher
Apply Link: https://perfleap.com/woSBvU"""
    },
    {
        "raw_job_text": """Company: Siemens 
Role: Software Engineering Intern
Batch Eligible: 2026 & 2027 graduates
Location: Noida
Experience: Fresher
Apply Link: https://bit.ly/4c8tvvr"""
    },
    {
        "raw_job_text": """Company: Sense
Role: Software Engineering Intern - Backend
Batch Eligible: 2026 & 2027 graduates
Location: Bengaluru 
Experience: Fresher
Apply Link: https://sensehr.sensehq.com/careers/jobs/196"""
    },
    {
        "raw_job_text": """Company: Deconstruct Skincare
Role: Internship
Batch Eligible: All students
Location: India
Salary: INR 1,00,000 stipend
Experience: Fresher
Features: Opportunity to feature on brand billboards, Learning & mentorship from industry experts
Apply Link: https://bit.ly/DeconstructIntern"""
    },
    {
        "raw_job_text": """Company: IBM
Role: Software Engineer Intern 
Batch Eligible: 2026 & 2027 graduates
Location: Remote / Multiple Locations
Experience: Fresher
Apply Link: https://careers.ibm.com/en_US/careers/JobDetail?jobId=93073"""
    },
    {
        "raw_job_text": """Company: TCS (Tata Consultancy Services)
Role: Systems Engineer Intern
Batch Eligible: 2025-2027 graduates
Location: Pan India
Salary: Competitive internship stipend
Experience: Fresher/0-2 years
Apply Link: https://www.tcs.com/careers"""
    }
]

# Post style names for reference
STYLE_NAMES = {
    1: "🚀 X Internships Today",
    2: "🚨 Fresher Alert",
    3: "🌍 Remote Jobs",
    4: "🔥 Top Companies",
    5: "💼 Mega List",
    6: "🚀 Startup Hiring",
    7: "📢 Weekly Roundup",
    8: "⚡ Mass Hiring",
    9: "💰 Paid Internship",
    10: "📌 Daily Jobs"
}


async def test_job_processing():
    """Send 10 jobs and display results with different post styles."""
    
    print("\n" + "="*80)
    print("LINK2HIRE - POST STYLE ROTATION TEST")
    print("="*80)
    print(f"Testing: {len(JOBS)} unique jobs with automatic style rotation")
    print(f"Backend: {BACKEND_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for index, job in enumerate(JOBS, 1):
            expected_style = (index % 10) if (index % 10) != 0 else 10
            style_name = STYLE_NAMES[expected_style]
            
            print(f"\n{'─'*80}")
            print(f"JOB #{index} - Expected Style #{expected_style}: {style_name}")
            print(f"{'─'*80}")
            
            try:
                # Send request to backend
                response = await client.post(
                    API_ENDPOINT,
                    json={
                        "raw_job_text": job["raw_job_text"],
                        "user_context": {
                            "test_run": True,
                            "test_job_number": index,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display response details
                    print(f"✅ Status: SUCCESS (200)")
                    
                    if "data" in data:
                        job_data = data["data"].get("job_data", {})
                        print(f"\n📋 Job Extracted:")
                        print(f"   Company: {job_data.get('company', 'N/A')}")
                        print(f"   Role(s): {', '.join([r.get('title', 'N/A') for r in job_data.get('roles', [])])}")
                        print(f"   Location: {job_data.get('location', 'N/A')}")
                        print(f"   Work Mode: {job_data.get('work_mode', 'N/A')}")
                        
                        # Display LinkedIn Post
                        if "linkedin_post" in data["data"]:
                            post = data["data"]["linkedin_post"]
                            print(f"\n📱 LinkedIn Post (Style #{expected_style}):")
                            print(f"{'─'*80}")
                            print(post.get("post_text", "No post generated"))
                            print(f"{'─'*80}")
                            print(f"Hashtags: {', '.join(post.get('hashtags', []))}")
                        else:
                            print("\n⚠️ No LinkedIn post in response")
                    
                    # Display metadata
                    if "meta" in data:
                        meta = data["meta"]
                        print(f"\n⏱️ Processing Time: {meta.get('processing_time_ms', 'N/A')}ms")
                        print(f"📊 State: {meta.get('conversation_state', 'N/A')}")
                    
                else:
                    print(f"❌ Status: ERROR ({response.status_code})")
                    print(f"Response: {response.text}")
                    
            except httpx.ConnectError:
                print(f"❌ CONNECTION ERROR: Cannot reach {BACKEND_URL}")
                print("   Make sure backend is running: uvicorn backend.main:app --reload --port 8000")
                break
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
            
            # Small delay between requests
            await asyncio.sleep(1)
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE ✅")
    print(f"{'='*80}\n")


def print_style_summary():
    """Print summary of all 10 post styles."""
    print("\n" + "="*80)
    print("POST STYLE REFERENCE")
    print("="*80 + "\n")
    
    descriptions = {
        1: "Multiple internship listings - Highest viral potential",
        2: "Urgent fresher hiring alert - FOMO-driven",
        3: "Remote work opportunities - Flexible work focus",
        4: "Top companies hiring - Brand prestige focus",
        5: "Mega bulk opportunities - Comprehensive list",
        6: "Startup growth roles - Innovation focus",
        7: "Weekly job summary - Organized roundup",
        8: "Large-scale hiring drive - Urgency + volume",
        9: "Paid internships - Monetary benefits focus",
        10: "Daily quick list - Newsletter style"
    }
    
    for num, desc in descriptions.items():
        print(f"Style #{num}: {STYLE_NAMES[num]}")
        print(f"         {desc}\n")


if __name__ == "__main__":
    print_style_summary()
    print("\nStarting API tests...\n")
    asyncio.run(test_job_processing())
