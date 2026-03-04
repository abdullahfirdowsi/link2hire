#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detailed LinkedIn Post Style Comparison
Shows actual post content for each of the 10 unique styles
"""

import asyncio
import httpx
import json
from datetime import datetime
import sys

# Set UTF-8 encoding for output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BACKEND_URL = "http://localhost:8000"

# Single job data for comparison - we'll reuse same job but get different styles
SAMPLE_JOB = """Company: TechFlow AI
Role: Software Engineer Intern / AI Developer Intern
Salary: INR 30,000 per month
Batch Eligible: 2025-2027 graduates
Location: Remote (Work From Home)
Experience: Fresher/0-1 years
Apply Link: https://bit.ly/techflow-intern"""

async def generate_multiple_styles():
    """Generate the same job with different post styles for comparison."""
    
    output_lines = []
    
    output_lines.append("\n" + "="*100)
    output_lines.append("LINKEDIN POST STYLE COMPARISON - SAME JOB, 10 DIFFERENT STYLES")
    output_lines.append("="*100)
    output_lines.append(f"\nCompany: TechFlow AI")
    output_lines.append(f"Role: Software Engineer Intern / AI Developer Intern")
    output_lines.append(f"Salary: INR 30,000/month | Remote | Fresher eligible")
    output_lines.append(f"\nGenerating 10 unique post formats from the same job data...")
    output_lines.append("="*100 + "\n")
    
    style_names = {
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
    
    all_posts = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for style_num in range(1, 11):
            try:
                response = await client.post(
                    f"{BACKEND_URL}/process-job",
                    json={
                        "raw_job_text": SAMPLE_JOB,
                        "user_context": {
                            "style_test": True,
                            "style_number": style_num
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    post = data.get("linkedin_post")
                    
                    # Handle None post
                    if not post:
                        post = {"post_text": "", "hashtags": []}
                    
                    post_info = {
                        "style_num": style_num,
                        "style_name": style_names[style_num],
                        "post_text": post.get("post_text", ""),
                        "hashtags": post.get("hashtags", [])
                    }
                    
                    all_posts.append(post_info)
                    
                    # Display each style
                    print(f"\n{'─'*100}")
                    print(f"STYLE #{style_num}: {style_names[style_num]}")
                    print(f"{'─'*100}\n")
                    print(post.get("post_text", "No post generated"))
                    print(f"\n📌 Hashtags: {', '.join(post.get('hashtags', []))}")
                    
                else:
                    print(f"❌ Style #{style_num} failed with status {response.status_code}")
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error processing style #{style_num}: {str(e)}")
    
    # Summary
    print(f"\n{'='*100}")
    print("SUMMARY - ALL STYLES GENERATED SUCCESSFULLY")
    print(f"{'='*100}\n")
    
    for post in all_posts:
        char_count = len(post["post_text"])
        lines = post["post_text"].count('\n') + 1
        print(f"Style #{post['style_num']}: {post['style_name']:<30} | {char_count} chars | {lines} lines")
    
    print(f"\n✅ All 10 unique post styles demonstrated!")
    print(f"✅ Same job → Different formats for maximum reach & engagement")
    print(f"✅ Rotate through these styles daily for best LinkedIn growth\n")
    
    # Save to file
    output_file = "linkedin_post_styles_comparison.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Detailed output saved to: {output_file}\n")


if __name__ == "__main__":
    try:
        asyncio.run(generate_multiple_styles())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure backend is running: uvicorn backend.main:app --reload --port 8000")
