#!/usr/bin/env python3
"""
Job Cross-Reference Script
Cross-references mentors from Spark/Gener8tor network with available jobs
based on skills, location, and career alignment.
"""

import pandas as pd
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import requests
from pathlib import Path


class MentorProcessor:
    """Processes and stores mentor information"""
    
    def __init__(self):
        self.mentors = []
    
    def load_from_csv(self, file_path: str) -> None:
        """Load mentors from CSV file"""
        try:
            df = pd.read_csv(file_path)
            self.mentors = df.to_dict('records')
            print(f"✓ Loaded {len(self.mentors)} mentors from {file_path}")
        except Exception as e:
            print(f"Error loading mentors: {e}")
            raise
    
    def load_from_json(self, file_path: str) -> None:
        """Load mentors from JSON file"""
        try:
            with open(file_path, 'r') as f:
                self.mentors = json.load(f)
            print(f"✓ Loaded {len(self.mentors)} mentors from {file_path}")
        except Exception as e:
            print(f"Error loading mentors: {e}")
            raise
    
    def get_mentor_skills(self) -> List[str]:
        """Extract unique skills from all mentors"""
        skills = set()
        for mentor in self.mentors:
            # Try different possible column names for skills
            skill_fields = ['skills', 'expertise', 'specialties', 'areas', 'competencies', 
                          'areas_of_expertise']
            for field in skill_fields:
                if field in mentor and mentor[field]:
                    if isinstance(mentor[field], str):
                        # Handle comma-separated values
                        skills.update([s.strip() for s in mentor[field].split(',') if s.strip()])
                    elif isinstance(mentor[field], list):
                        skills.update([str(s).strip() for s in mentor[field] if s])
        return list(skills)
    
    def get_mentor_companies(self) -> List[str]:
        """Extract unique companies from mentors"""
        companies = set()
        for mentor in self.mentors:
            company_fields = ['company', 'organization', 'employer', 'current_company']
            for field in company_fields:
                if field in mentor and mentor[field]:
                    companies.add(str(mentor[field]).strip())
        return list(companies)


class JobSearcher:
    """Searches for jobs using various APIs and methods"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}
        self.jobs = []
    
    def search_indeed(self, query: str, location: str = "", limit: int = 50) -> List[Dict]:
        """
        Search Indeed jobs (Note: Indeed API requires authentication)
        For now, returns structure for manual implementation
        """
        # TODO: Implement Indeed API integration
        # You'll need: https://ads.indeed.com/jobroll/xmlfeed
        print(f"Searching Indeed for: {query} in {location}")
        return []
    
    def search_linkedin(self, query: str, location: str = "", limit: int = 50) -> List[Dict]:
        """
        Search LinkedIn jobs (Note: LinkedIn API requires authentication)
        """
        # TODO: Implement LinkedIn API integration
        print(f"Searching LinkedIn for: {query} in {location}")
        return []
    
    def search_adzuna(self, query: str, location: str = "us", limit: int = 50) -> List[Dict]:
        """
        Search Adzuna jobs (Free API available)
        """
        if 'adzuna_app_id' not in self.api_keys or 'adzuna_app_key' not in self.api_keys:
            print("⚠ Adzuna API keys not configured. Skipping Adzuna search.")
            return []
        
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                'app_id': self.api_keys['adzuna_app_id'],
                'app_key': self.api_keys['adzuna_app_key'],
                'results_per_page': min(limit, 50),
                'what': query,
                'where': location,
                'content-type': 'application/json'
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for job in data.get('results', []):
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', {}).get('display_name', ''),
                        'location': job.get('location', {}).get('display_name', ''),
                        'description': job.get('description', ''),
                        'url': job.get('redirect_url', ''),
                        'created': job.get('created', ''),
                        'salary_min': job.get('salary_min'),
                        'salary_max': job.get('salary_max'),
                        'source': 'Adzuna'
                    })
                if len(jobs) > 0:
                    print(f"✓ Found {len(jobs)} jobs from Adzuna")
                return jobs
            else:
                print(f"⚠ Adzuna API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error searching Adzuna: {e}")
            return []
    
    def search_job_apis(self, skills: List[str], location: str = "", us_wide: bool = True) -> List[Dict]:
        """Search multiple job APIs with multiple query variations"""
        all_jobs = []
        
        # Create multiple search query variations for better coverage
        queries = []
        
        # 1. Individual skills (most specific)
        for skill in skills[:5]:  # Top 5 skills individually
            queries.append(skill)
        
        # 2. Skill combinations (2-3 skills together)
        if len(skills) >= 2:
            queries.append(f"{skills[0]} {skills[1]}")
        if len(skills) >= 3:
            queries.append(f"{skills[0]} {skills[2]}")
        if len(skills) >= 3:
            queries.append(f"{skills[1]} {skills[2]}")
        
        # 3. Generic variations for broader search
        if any('full' in s.lower() or 'stack' in s.lower() for s in skills):
            queries.append("full stack developer")
            queries.append("fullstack developer")
        if any('ai' in s.lower() or 'artificial' in s.lower() or 'machine learning' in s.lower() for s in skills):
            queries.append("AI developer")
            queries.append("machine learning engineer")
        if any('creative' in s.lower() or 'music' in s.lower() for s in skills):
            queries.append("software developer")
            queries.append("creative technologist")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            q_lower = q.lower()
            if q_lower not in seen:
                seen.add(q_lower)
                unique_queries.append(q)
        
        print(f"   Using {len(unique_queries)} search query variations")
        
        # Search local area with all query variations
        if location:
            print(f"\n🔍 Searching jobs in: {location}")
            for i, query in enumerate(unique_queries[:5], 1):  # Reduced to 5 for local to prioritize local results
                print(f"   Query {i}/{min(len(unique_queries), 5)}: '{query}'")
                jobs = self.search_adzuna(query, location, limit=30)
                all_jobs.extend(jobs)
        
        # Search US-wide with all query variations (only if us_wide is True)
        if us_wide:
            print(f"\n🔍 Searching jobs US-wide")
            for i, query in enumerate(unique_queries[:5], 1):  # Reduced to 5 queries
                print(f"   Query {i}/{min(len(unique_queries), 5)}: '{query}'")
                jobs = self.search_adzuna(query, "us", limit=40)  # Reduced limit
                all_jobs.extend(jobs)
        
        # Remove duplicates based on title + company + URL
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            # Create unique key from title, company, and URL
            title = job.get('title', '').lower().strip()
            company = job.get('company', '').lower().strip()
            url = job.get('url', '').strip()
            
            # Use URL as primary key if available, otherwise title+company
            if url:
                key = url
            else:
                key = f"{title}|{company}"
            
            if key not in seen and title:  # Only add if we have a title
                seen.add(key)
                unique_jobs.append(job)
        
        print(f"✓ Found {len(unique_jobs)} unique jobs (from {len(all_jobs)} total results)")
        self.jobs = unique_jobs
        return unique_jobs


class SkillMatcher:
    """Matches jobs with skills and career alignment"""
    
    def __init__(self, user_skills: List[str], user_interests: List[str] = None):
        self.user_skills = [s.lower() for s in user_skills]
        self.user_interests = [i.lower() for i in (user_interests or [])]
    
    def calculate_match_score(self, job: Dict, mentor_skills: List[str], mentor_companies: List[str] = None) -> float:
        """Calculate how well a job matches based on skills - improved algorithm"""
        score = 0.0
        max_score = 100.0
        
        # Extract job text for analysis
        job_title = job.get('title', '').lower()
        job_description = job.get('description', '').lower()
        job_company = job.get('company', '').lower()
        job_text = job_title + ' ' + job_description + ' ' + job_company
        
        # Normalize skills for better matching
        def normalize_skill(skill):
            return skill.lower().strip().replace('-', ' ').replace('_', ' ')
        
        user_skills_normalized = [normalize_skill(s) for s in self.user_skills]
        
        # 1. Title match (highest weight - 30%)
        title_matches = sum(1 for skill in user_skills_normalized if skill in job_title)
        if self.user_skills:
            score += (title_matches / len(self.user_skills)) * 30
        
        # 2. Description match (25% weight)
        desc_matches = sum(1 for skill in user_skills_normalized if skill in job_description)
        if self.user_skills:
            score += (desc_matches / len(self.user_skills)) * 25
        
        # 3. Mentor network skills match (20% weight)
        mentor_skill_matches = sum(1 for skill in mentor_skills if normalize_skill(skill) in job_text)
        if mentor_skills:
            score += min((mentor_skill_matches / len(mentor_skills)) * 20, 20)
        
        # 4. User interests match (15% weight)
        if self.user_interests:
            interests_normalized = [normalize_skill(i) for i in self.user_interests]
            interest_matches = sum(1 for interest in interests_normalized if interest in job_text)
            score += (interest_matches / len(self.user_interests)) * 15
        
        # 5. Mentor company match bonus (10% weight) - big boost if mentor works there
        if mentor_companies and job_company:
            for mentor_company in mentor_companies:
                if normalize_skill(mentor_company) in job_company or job_company in normalize_skill(mentor_company):
                    score += 10
                    break  # Only count once
        
        return min(score, max_score)
    
    def rank_jobs(self, jobs: List[Dict], mentor_skills: List[str], mentor_companies: List[str] = None) -> List[Dict]:
        """Rank jobs by match score"""
        for job in jobs:
            job['match_score'] = self.calculate_match_score(job, mentor_skills, mentor_companies)
        
        return sorted(jobs, key=lambda x: x.get('match_score', 0), reverse=True)


class ReportGenerator:
    """Generates reports of matched jobs"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_csv_report(self, jobs: List[Dict], filename: str = None) -> str:
        """Generate CSV report of matched jobs"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_matches_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        df = pd.DataFrame(jobs)
        # Select and order columns
        columns = ['title', 'company', 'location', 'match_score', 'url', 'source', 'salary_min', 'salary_max']
        available_columns = [c for c in columns if c in df.columns]
        df = df[available_columns]
        
        # Sort by match score
        if 'match_score' in df.columns:
            df = df.sort_values('match_score', ascending=False)
        
        df.to_csv(filepath, index=False)
        print(f"✓ Report saved to: {filepath}")
        return str(filepath)
    
    def generate_html_report(self, jobs: List[Dict], mentors: List[Dict], filename: str = None) -> str:
        """Generate HTML report of matched jobs"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_matches_{timestamp}.html"
        
        filepath = self.output_dir / filename
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Job Cross-Reference Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .job-card {{ background: white; margin: 15px 0; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .match-score {{ font-size: 24px; font-weight: bold; color: #27ae60; }}
        .job-title {{ font-size: 20px; font-weight: bold; color: #2c3e50; margin: 10px 0; }}
        .company {{ color: #7f8c8d; font-size: 16px; }}
        .location {{ color: #7f8c8d; }}
        .description {{ margin: 15px 0; color: #34495e; }}
        .link {{ color: #3498db; text-decoration: none; }}
        .stats {{ background: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Job Cross-Reference Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Total Jobs Found: {len(jobs)} | Mentors Analyzed: {len(mentors)}</p>
    </div>
    
    <div class="stats">
        <h2>Top Matches</h2>
        <p>Jobs sorted by alignment score (skills, interests, mentor network)</p>
    </div>
"""
        
        for job in jobs[:50]:  # Top 50 matches
            score = job.get('match_score', 0)
            html += f"""
    <div class="job-card">
        <div class="match-score">Match: {score:.1f}%</div>
        <div class="job-title">{job.get('title', 'N/A')}</div>
        <div class="company">{job.get('company', 'N/A')}</div>
        <div class="location">📍 {job.get('location', 'N/A')}</div>
        {f'<div>💰 ${job.get("salary_min", "")} - ${job.get("salary_max", "")}</div>' if job.get('salary_min') else ''}
        <div class="description">{job.get('description', '')[:300]}...</div>
        <a href="{job.get('url', '#')}" class="link" target="_blank">View Job →</a>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        print(f"✓ HTML report saved to: {filepath}")
        return str(filepath)


class JobCrossReference:
    """Main class for cross-referencing mentors with jobs"""
    
    def __init__(self, user_skills: List[str], user_interests: List[str] = None, 
                 location: str = "", api_keys: Dict[str, str] = None):
        self.mentor_processor = MentorProcessor()
        self.job_searcher = JobSearcher(api_keys)
        self.skill_matcher = SkillMatcher(user_skills, user_interests)
        self.report_generator = ReportGenerator()
        self.location = location
    
    def process(self, mentor_file: str, us_wide: bool = True) -> Dict:
        """Main processing function"""
        print("=" * 60)
        print("Job Cross-Reference Analysis")
        print("=" * 60)
        
        # Load mentors
        if mentor_file.endswith('.csv'):
            self.mentor_processor.load_from_csv(mentor_file)
        elif mentor_file.endswith('.json'):
            self.mentor_processor.load_from_json(mentor_file)
        else:
            raise ValueError("Mentor file must be CSV or JSON")
        
        # Extract mentor skills and companies
        mentor_skills = self.mentor_processor.get_mentor_skills()
        mentor_companies = self.mentor_processor.get_mentor_companies()
        print(f"✓ Extracted {len(mentor_skills)} unique skills from mentors")
        print(f"✓ Found {len(mentor_companies)} unique companies")
        
        # Search for jobs using USER skills (not mentor skills)
        user_skills_for_search = self.skill_matcher.user_skills
        print(f"✓ Searching jobs matching your skills: {', '.join(user_skills_for_search[:5])}...")
        jobs = self.job_searcher.search_job_apis(
            user_skills_for_search, 
            location=self.location, 
            us_wide=us_wide
        )
        print(f"✓ Found {len(jobs)} total jobs")
        
        # Match and rank jobs (pass mentor companies for better scoring)
        ranked_jobs = self.skill_matcher.rank_jobs(jobs, mentor_skills, list(mentor_companies))
        print(f"✓ Ranked {len(ranked_jobs)} jobs by match score")
        
        # Generate reports
        csv_path = self.report_generator.generate_csv_report(ranked_jobs)
        html_path = self.report_generator.generate_html_report(
            ranked_jobs, 
            self.mentor_processor.mentors
        )
        
        # Summary
        top_matches = [j for j in ranked_jobs if j.get('match_score', 0) >= 50]
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total Jobs Found: {len(ranked_jobs)}")
        print(f"High Matches (≥50%): {len(top_matches)}")
        print(f"Reports Generated:")
        print(f"  - CSV: {csv_path}")
        print(f"  - HTML: {html_path}")
        
        return {
            'jobs': ranked_jobs,
            'top_matches': top_matches,
            'csv_report': csv_path,
            'html_report': html_path,
            'mentor_stats': {
                'total_mentors': len(self.mentor_processor.mentors),
                'unique_skills': len(mentor_skills),
                'unique_companies': len(mentor_companies)
            }
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cross-reference mentors with job opportunities')
    parser.add_argument('mentor_file', help='Path to mentor CSV or JSON file')
    parser.add_argument('--skills', nargs='+', required=True, 
                       help='Your current skills (space-separated)')
    parser.add_argument('--interests', nargs='+', default=[], 
                       help='Your interests/future skills (space-separated)')
    parser.add_argument('--location', default='', 
                       help='Your location for local job search (e.g., "San Francisco, CA")')
    parser.add_argument('--us-wide', action='store_true', default=True,
                       help='Also search US-wide jobs')
    parser.add_argument('--adzuna-app-id', help='Adzuna API App ID')
    parser.add_argument('--adzuna-app-key', help='Adzuna API App Key')
    
    args = parser.parse_args()
    
    # Setup API keys - try config file first, then command line args
    api_keys = {}
    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'adzuna' in config:
                    api_keys['adzuna_app_id'] = config['adzuna'].get('app_id', '')
                    api_keys['adzuna_app_key'] = config['adzuna'].get('app_key', '')
                    print("✓ Loaded API keys from config.json")
        except Exception as e:
            print(f"⚠ Could not load config.json: {e}")
    
    # Command line args override config file
    if args.adzuna_app_id and args.adzuna_app_key:
        api_keys['adzuna_app_id'] = args.adzuna_app_id
        api_keys['adzuna_app_key'] = args.adzuna_app_key
        print("✓ Using API keys from command line arguments")
    
    # Create and run cross-reference
    cross_ref = JobCrossReference(
        user_skills=args.skills,
        user_interests=args.interests,
        location=args.location,
        api_keys=api_keys if api_keys else None
    )
    
    cross_ref.process(args.mentor_file, us_wide=args.us_wide)


if __name__ == "__main__":
    main()

