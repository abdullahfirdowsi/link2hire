"""
LinkedIn Post Style Templates for Unique Content Generation.
Provides 10 different post templates to rotate through for variety.
"""

from enum import Enum
from typing import List, Protocol
from backend.models.job_model import ExtractedJobData


class PostStyle(Enum):
    """Available post style formats."""
    DAILY_INTERNSHIPS = 1
    FRESHER_ALERT = 2
    REMOTE_JOBS = 3
    TOP_COMPANIES = 4
    MEGA_LIST = 5
    STARTUP_HIRING = 6
    WEEKLY_ROUNDUP = 7
    MASS_HIRING = 8
    PAID_INTERNSHIP = 9
    DAILY_JOBS = 10


class PostTemplate(Protocol):
    """Protocol for post template functions."""
    def __call__(self, job_data: ExtractedJobData) -> str:
        """Generate post text from job data."""
        ...


class LinkedInPostStyles:
    """Collection of LinkedIn post style templates."""
    
    @staticmethod
    def style_daily_internships(job_data: ExtractedJobData) -> str:
        """
        Style 1: "X Internships Today" - Most Viral Format
        Best for multiple internship listings.
        """
        roles_text = ", ".join([role.title for role in job_data.roles])
        
        post = f"""🚀 {len(job_data.roles)} Internship Opportunities Today

1️⃣ {job_data.company} – {roles_text}
2️⃣ Similar Role – Your Dream Company
3️⃣ Growth Opportunity – Leading MNC
4️⃣ Remote Position – Tech Focus
5️⃣ Stipend Based – Great Learning

📍 Location: {job_data.location}
💼 Work Mode: {job_data.work_mode.value}
✅ Eligibility: {job_data.eligibility}

{"💰 Stipend: " + job_data.salary if job_data.salary else ""}

Apply Links in Comments 👇

Follow Cheran Kanth for daily job & internship updates.

#internships #fresherjobs #techJobs #hiring"""
        
        return post.strip()
    
    @staticmethod
    def style_fresher_alert(job_data: ExtractedJobData) -> str:
        """
        Style 2: "Fresher Hiring Alert" - Urgent Format
        Emphasizes fresher eligibility and company prestige.
        """
        roles_text = " / ".join([role.title for role in job_data.roles])
        
        post = f"""🚨 FRESHER HIRING ALERT

Company: {job_data.company}
Role: {roles_text}

📍 Location: {job_data.location}
🎯 Eligibility: {job_data.eligibility}
💼 Work Mode: {job_data.work_mode.value}
⏰ Experience: {job_data.experience}

{"💰 Salary: " + job_data.salary if job_data.salary else "✨ Great Career Growth"}

This is a GOLDEN opportunity for freshers! Don't miss out.

Apply here 👇
{job_data.apply_link}

Follow Cheran Kanth for daily hiring updates.

#fresherjobs #hiring #careergrowth #mncjobs"""
        
        return post.strip()
    
    @staticmethod
    def style_remote_jobs(job_data: ExtractedJobData) -> str:
        """
        Style 3: "Remote Jobs Thread" - Work From Home Focus
        Highlights remote work benefits.
        """
        post = f"""🌍 Remote Job Opportunity!

Work From Home Edition 🏠

Company: {job_data.company}
Role(s): {", ".join([role.title for role in job_data.roles])}

📍 Location: {job_data.location}
💻 Work Mode: {job_data.work_mode.value}
✅ Eligibility: {job_data.eligibility}
📊 Experience Needed: {job_data.experience}

{"💵 Salary/Stipend: " + job_data.salary if job_data.salary else ""}

✨ Benefits of this role:
• Flexible work hours
• Work from anywhere
• Growing tech company
• Amazing learning curve

Apply Links in Comments 👇
{job_data.apply_link}

#remotework #workfromhome #techtjobs #hiring"""
        
        return post.strip()
    
    @staticmethod
    def style_top_companies(job_data: ExtractedJobData) -> str:
        """
        Style 4: "Top Companies Hiring" - Prestige Focus
        Emphasizes company brand and team.
        """
        post = f"""🔥 Top Company Hiring Freshers Today!

Company: {job_data.company}
Roles: {", ".join([role.title for role in job_data.roles])}

Why Apply?
✅ Prestigious Company
✅ Strong Career Growth
✅ Industry Experience
✅ Great Team & Culture

📍 Location: {job_data.location}
💼 Work: {job_data.work_mode.value}
🎓 Eligibility: {job_data.eligibility}

{"💰 Compensation: " + job_data.salary if job_data.salary else ""}

Apply Now 👇
{job_data.apply_link}

Follow for daily job updates.

#hiring #jobopportunity #careerGrowth """
        
        return post.strip()
    
    @staticmethod
    def style_mega_list(job_data: ExtractedJobData) -> str:
        """
        Style 5: "Mega Internship List" - Quantity Focus
        Emphasizes multiple opportunities and high stipends.
        """
        post = f"""💼 15+ Internships for IT/CS Students

THIS WEEK'S HOT OPPORTUNITIES:

🏆 Top Internships:
• {job_data.company} – {job_data.roles[0].title if job_data.roles else "Tech Role"}
• Leading Tech Companies
• Startup Opportunities
• Fortune 500 Firms

{"💰 Stipend Range: " + job_data.salary + "/month" if job_data.salary else ""}
📍 Locations: {job_data.location}
🌐 Work Mode: {job_data.work_mode.value}

Eligibility: {job_data.eligibility}

Save this post! ⭐

Apply now 👇
{job_data.apply_link}

#internships #fresherjobs #techtjobs #studentopportunity"""
        
        return post.strip()
    
    @staticmethod
    def style_startup_hiring(job_data: ExtractedJobData) -> str:
        """
        Style 6: "Startup Hiring" - Growth & Innovation Focus
        Emphasizes innovation and fast growth.
        """
        post = f"""🚀 Startup is Hiring!

Exciting Role at {job_data.company}

Position(s): {", ".join([role.title for role in job_data.roles])}

🌟 What makes this special:
• Rapid Learning Curve
• Direct Impact on Product
• Growing Team
• Innovative Projects

📍 Location: {job_data.location}
💼 Work: {job_data.work_mode.value}
✅ Eligibility: {job_data.eligibility}

{"💰 Stipend: " + job_data.salary if job_data.salary else "💡 Exposure & Learning"}

Great opportunity for it students.

Apply Links in Comments 👇
{job_data.apply_link}

#startup #hiringnow #innovation #techtjobs"""
        
        return post.strip()
    
    @staticmethod
    def style_weekly_roundup(job_data: ExtractedJobData) -> str:
        """
        Style 7: "Weekly Job Roundup" - Summary Format
        Summarizes top hiring companies this week.
        """
        post = f"""📢 Weekly Job Roundup 🎯

Top Companies Hiring THIS WEEK:

📌 Featured:
• {job_data.company}
• Top Tech Companies
• MNC Giants
• Emerging Startups

Roles: {", ".join([role.title for role in job_data.roles])}

📍 Locations: {job_data.location}
🔄 Work Mode: {job_data.work_mode.value}
🎓 Eligibility: {job_data.eligibility}

⏰ LIMITED SLOTS AVAILABLE

Save this post for later. 📌

Apply now 👇
{job_data.apply_link}

Follow for weekly job roundups.

#jobsearch #hiringalert #careerUpdate #weeklyJobs"""
        
        return post.strip()
    
    @staticmethod
    def style_mass_hiring(job_data: ExtractedJobData) -> str:
        """
        Style 8: "Mass Hiring Alert" - Urgency & Volume Focus
        Emphasizes large-scale hiring drive.
        """
        post = f"""⚡ MASS HIRING ALERT ⚡

{job_data.company} is Hiring LARGE SCALE

Position(s): {", ".join([role.title for role in job_data.roles])}

Eligibility: {job_data.eligibility}
Experience: {job_data.experience}

📊 Numbers:
✅ 100+ Open Positions
✅ Multiple Locations
✅ Fast-Track Process

📍 Location: {job_data.location}
💼 Work: {job_data.work_mode.value}

{"💰 Salary: " + job_data.salary if job_data.salary else ""}

This is THE opportunity you've been waiting for!

Apply Now 👇
{job_data.apply_link}

#massHiring #jobAlert #careers #jobOpportunity"""
        
        return post.strip()
    
    @staticmethod
    def style_paid_internship(job_data: ExtractedJobData) -> str:
        """
        Style 9: "Internship With Stipend" - Money Focus
        Emphasizes monetary benefits.
        """
        post = f"""💰 PAID Internship Opportunity

Get Paid While You Learn!

Company: {job_data.company}
Role: {job_data.roles[0].title if job_data.roles else "Internship"}

💵 Stipend: {job_data.salary if job_data.salary else "Competitive"}
📍 Location: {job_data.location}
🌐 Work: {job_data.work_mode.value}
✅ Eligibility: {job_data.eligibility}

Why Take This?
✨ Earn While Learning
✨ Real-World Experience
✨ Resume Booster
✨ Networking Opportunity

This is NOT just another internship—it's an investment in your future.

Apply Link 👇
{job_data.apply_link}

Don't miss out!

#paidinternship #internship #moneyandexperience #careergrowth"""
        
        return post.strip()
    
    @staticmethod
    def style_daily_jobs(job_data: ExtractedJobData) -> str:
        """
        Style 10: "Daily Job Thread" - List Format
        Quick list of daily job opportunities.
        """
        roles_list = "\n".join([f"{i+1}️⃣ {role.title}" for i, role in enumerate(job_data.roles[:5])])
        
        post = f"""📌 {len(job_data.roles)} Jobs for IT Freshers Today

Quick Daily Update:

{roles_list}

Company: {job_data.company}
📍 Location: {job_data.location}
💼 Work Mode: {job_data.work_mode.value}
🎯 Eligibility: {job_data.eligibility}

{"💰 Salary/Stipend: " + job_data.salary if job_data.salary else ""}

Apply Links in Comments 👇
{job_data.apply_link}

Follow Cheran Kanth for daily job updates.

#dailyjobs #fresherjobs #hiringnow #jobsearch#techJobs#careers"""
        
        return post.strip()
    
    @staticmethod
    def get_style_by_number(style_num: int) -> PostTemplate:
        """
        Get post template function by style number (1-10).
        
        Args:
            style_num: Number from 1-10
            
        Returns:
            PostTemplate function
        """
        styles = {
            1: LinkedInPostStyles.style_daily_internships,
            2: LinkedInPostStyles.style_fresher_alert,
            3: LinkedInPostStyles.style_remote_jobs,
            4: LinkedInPostStyles.style_top_companies,
            5: LinkedInPostStyles.style_mega_list,
            6: LinkedInPostStyles.style_startup_hiring,
            7: LinkedInPostStyles.style_weekly_roundup,
            8: LinkedInPostStyles.style_mass_hiring,
            9: LinkedInPostStyles.style_paid_internship,
            10: LinkedInPostStyles.style_daily_jobs,
        }
        return styles.get(style_num, LinkedInPostStyles.style_daily_internships)
    
    @staticmethod
    def get_all_styles() -> List[PostTemplate]:
        """Get all 10 post style templates."""
        return [
            LinkedInPostStyles.style_daily_internships,
            LinkedInPostStyles.style_fresher_alert,
            LinkedInPostStyles.style_remote_jobs,
            LinkedInPostStyles.style_top_companies,
            LinkedInPostStyles.style_mega_list,
            LinkedInPostStyles.style_startup_hiring,
            LinkedInPostStyles.style_weekly_roundup,
            LinkedInPostStyles.style_mass_hiring,
            LinkedInPostStyles.style_paid_internship,
            LinkedInPostStyles.style_daily_jobs,
        ]
