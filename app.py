#!/usr/bin/env python3
"""
Job Cross-Reference Web Application
Flask backend for the job search tool
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
from pathlib import Path
from job_cross_reference import JobCrossReference
import os
import pdfplumber
import re

app = Flask(__name__)

# Load API keys from config
def load_api_keys():
    """Load API keys from config.json"""
    config_path = Path(__file__).parent / 'config.json'
    api_keys = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'adzuna' in config:
                    api_keys['adzuna_app_id'] = config['adzuna'].get('app_id', '')
                    api_keys['adzuna_app_key'] = config['adzuna'].get('app_key', '')
        except Exception as e:
            print(f"Error loading config: {e}")
    return api_keys if api_keys else None


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search_jobs():
    """API endpoint to search for jobs"""
    try:
        data = request.json
        skills = data.get('skills', [])
        interests = data.get('interests', [])
        location = data.get('location', '')
        us_wide = data.get('us_wide', True)
        
        if not skills:
            return jsonify({'error': 'Skills are required'}), 400
        
        # Load API keys
        api_keys = load_api_keys()
        
        # Create cross-reference instance
        cross_ref = JobCrossReference(
            user_skills=skills,
            user_interests=interests,
            location=location,
            api_keys=api_keys
        )
        
        # Process search
        result = cross_ref.process('mentors.csv', us_wide=us_wide)
        
        # Return results
        return jsonify({
            'success': True,
            'jobs': result['jobs'],
            'top_matches': result['top_matches'],
            'stats': {
                'total_jobs': len(result['jobs']),
                'high_matches': len(result['top_matches']),
                'mentor_stats': result['mentor_stats']
            },
            'csv_report': result['csv_report'],
            'html_report': result['html_report']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mentors')
def get_mentors():
    """Get mentor statistics"""
    try:
        from job_cross_reference import MentorProcessor
        
        processor = MentorProcessor()
        processor.load_from_csv('mentors.csv')
        
        mentor_skills = processor.get_mentor_skills()
        mentor_companies = processor.get_mentor_companies()
        
        return jsonify({
            'total_mentors': len(processor.mentors),
            'unique_companies': len(mentor_companies),
            'unique_skills': len(mentor_skills),
            'top_skills': list(mentor_skills)[:10]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mentors/company/<path:company_name>')
def get_mentors_by_company(company_name):
    """Get mentors who work at a specific company"""
    try:
        from job_cross_reference import MentorProcessor
        import urllib.parse
        
        # Decode URL-encoded company name
        company_name = urllib.parse.unquote(company_name)
        
        # Initialize processor (cache it to avoid reloading every time)
        if not hasattr(get_mentors_by_company, '_processor'):
            get_mentors_by_company._processor = MentorProcessor()
            get_mentors_by_company._processor.load_from_csv('mentors.csv')
        
        processor = get_mentors_by_company._processor
        
        # Find mentors at this company (improved fuzzy matching)
        matching_mentors = []
        company_lower = company_name.lower().strip()
        
        # Normalize company name (remove common suffixes, etc.)
        def normalize_company(name):
            name = name.lower().strip()
            # Remove common suffixes
            name = re.sub(r'\s+(inc|llc|ltd|corp|corporation|company|co)\.?$', '', name)
            # Remove special characters
            name = re.sub(r'[^\w\s]', '', name)
            return name
        
        normalized_search = normalize_company(company_name)
        
        for mentor in processor.mentors:
            mentor_company = str(mentor.get('company', '')).strip()
            if not mentor_company:
                continue
            
            mentor_company_lower = mentor_company.lower()
            normalized_mentor = normalize_company(mentor_company)
            
            # Multiple matching strategies
            matches = False
            
            # 1. Exact match (case insensitive)
            if company_lower == mentor_company_lower:
                matches = True
            # 2. Normalized match
            elif normalized_search == normalized_mentor:
                matches = True
            # 3. One contains the other (for partial matches)
            elif (normalized_search in normalized_mentor or normalized_mentor in normalized_search) and len(normalized_search) > 3:
                matches = True
            # 4. Word-by-word match (e.g., "JPMorgan Chase" matches "JPMorgan Chase & Co.")
            elif normalized_search and normalized_mentor:
                search_words = set(normalized_search.split())
                mentor_words = set(normalized_mentor.split())
                # If most words match, consider it a match
                if len(search_words) > 0 and len(mentor_words) > 0:
                    common_words = search_words.intersection(mentor_words)
                    if len(common_words) >= min(2, len(search_words)):
                        matches = True
            
            if matches:
                matching_mentors.append({
                    'name': str(mentor.get('name', 'N/A')),
                    'full_name': str(mentor.get('full_name', mentor.get('name', 'N/A'))),
                    'title': str(mentor.get('title', 'N/A')),
                    'company': str(mentor.get('company', 'N/A')),
                    'linkedin': str(mentor.get('linkedin', '')),
                    'areas_of_expertise': str(mentor.get('areas_of_expertise', ''))
                })
        
        return jsonify({
            'company': company_name,
            'mentors': matching_mentors,
            'count': len(matching_mentors)
        })
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(f"Mentor lookup error: {error_msg}")
        return jsonify({'error': str(e), 'company': company_name, 'mentors': [], 'count': 0}), 500


@app.route('/api/bookmarks', methods=['GET', 'POST', 'DELETE'])
def bookmarks():
    """Handle job bookmarks (stored in memory for now, could use database)"""
    # In a real app, use a database. For now, we'll use a simple file
    bookmarks_file = Path('bookmarks.json')
    
    if request.method == 'GET':
        if bookmarks_file.exists():
            with open(bookmarks_file, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'bookmarks': []})
    
    elif request.method == 'POST':
        data = request.json
        job_id = data.get('job_id')
        job_data = data.get('job_data')
        
        # Load existing bookmarks
        bookmarks = []
        if bookmarks_file.exists():
            with open(bookmarks_file, 'r') as f:
                bookmarks = json.load(f).get('bookmarks', [])
        
        # Add if not already bookmarked
        if not any(b.get('job_id') == job_id for b in bookmarks):
            bookmarks.append({
                'job_id': job_id,
                'job_data': job_data,
                'bookmarked_at': str(Path(__file__).stat().st_mtime)  # Simple timestamp
            })
            
            with open(bookmarks_file, 'w') as f:
                json.dump({'bookmarks': bookmarks}, f, indent=2)
            
            return jsonify({'success': True, 'bookmarked': True})
        return jsonify({'success': True, 'bookmarked': False, 'message': 'Already bookmarked'})
    
    elif request.method == 'DELETE':
        data = request.json
        job_id = data.get('job_id')
        
        if bookmarks_file.exists():
            with open(bookmarks_file, 'r') as f:
                bookmarks_data = json.load(f)
            
            bookmarks = [b for b in bookmarks_data.get('bookmarks', []) if b.get('job_id') != job_id]
            
            with open(bookmarks_file, 'w') as f:
                json.dump({'bookmarks': bookmarks}, f, indent=2)
            
            return jsonify({'success': True, 'removed': True})
        return jsonify({'success': False, 'error': 'No bookmarks file'})


@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """Extract skills and location from uploaded resume"""
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save temporarily
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / file.filename
        file.save(file_path)
        
        # Extract text from PDF
        text = ""
        if file.filename.lower().endswith('.pdf'):
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                return jsonify({'error': f'Error reading PDF: {str(e)}'}), 500
        
        # Extract skills and location
        skills = extract_skills_from_resume(text)
        location = extract_location_from_resume(text)
        
        # Clean up
        file_path.unlink()
        
        return jsonify({
            'success': True,
            'skills': skills,
            'location': location
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def extract_skills_from_resume(text):
    """Extract skills from resume text - improved parsing"""
    found_skills = set()
    text_lower = text.lower()
    
    # Look for "TECHNICAL SKILLS" or "SKILLS" section - capture full multi-line section
    # First try to find the section header
    skills_header_match = re.search(r'(?:technical\s+)?skills?[:\s]+', text, re.IGNORECASE)
    if skills_header_match:
        # Find where the skills section ends (next major section)
        start_pos = skills_header_match.end()
        # Look for next section (EXPERIENCE, EDUCATION, PROJECTS, or double newline + caps)
        end_match = re.search(r'\n(EXPERIENCE|EDUCATION|PROJECTS|HIGHLIGHTS)', text[start_pos:], re.IGNORECASE)
        if end_match:
            skills_text = text[start_pos:start_pos + end_match.start()]
        else:
            # Fallback: take next 500 characters or until double newline
            remaining = text[start_pos:start_pos + 500]
            double_newline = remaining.find('\n\n')
            if double_newline > 0:
                skills_text = remaining[:double_newline]
            else:
                skills_text = remaining
    else:
        # Fallback to original pattern
        skills_section_patterns = [
            r'(?:technical\s+)?skills?[:\s]+\n?(.*?)(?:\n\n|\nEXPERIENCE|\nEDUCATION|\nPROJECTS|$)',
            r'technologies?[:\s]+\n?(.*?)(?:\n\n|\nEXPERIENCE|$)',
        ]
        for pattern in skills_section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if match:
                skills_text = match.group(1)
                break
        else:
            skills_text = ""
    
    # If found skills section, parse it
    if skills_text:
        # First, replace newlines with spaces but preserve structure
        skills_text = skills_text.replace('\n', ' ')
        # Clean up extra whitespace but preserve single spaces
        skills_text = re.sub(r'\s+', ' ', skills_text)
        
        # Remove category labels and replace with commas to separate categories
        # This prevents "Tailwind CSS Tools: Git" from becoming "Tailwind CSS Git"
        skills_text = re.sub(r'\b(Languages|Frameworks|Tools|Other|Technologies):\s*', ', ', skills_text, flags=re.IGNORECASE)
        # Remove leading comma if present
        skills_text = skills_text.lstrip(', ').strip()
        
        all_skills_text = skills_text
        
        # Better parsing: first split by commas, then handle slashes
        # This preserves structure: "A, B/C, D" -> ["A", "B/C", "D"]
        comma_split = []
        current_item = ""
        paren_depth = 0
        
        for char in all_skills_text:
            if char == '(':
                paren_depth += 1
                current_item += char
            elif char == ')':
                paren_depth -= 1
                current_item += char
            elif char == ',' and paren_depth == 0:
                if current_item.strip():
                    comma_split.append(current_item.strip())
                current_item = ""
            else:
                current_item += char
        
        if current_item.strip():
            comma_split.append(current_item.strip())
        
        # Now process each comma-separated item, splitting by "/" if needed
        skills_list = []
        for item in comma_split:
            item = item.strip()
            if not item:
                continue
            
            # If item contains "/", split it
            if '/' in item and '(' not in item:  # Don't split if it's in parentheses
                parts = item.split('/')
                for part in parts:
                    part = part.strip()
                    if part:
                        skills_list.append(part)
            else:
                skills_list.append(item)
        
        # Process each skill
        for skill in skills_list:
            skill = skill.strip()
            if not skill or len(skill) < 2:
                continue
            
            # Remove category prefixes
            skill = re.sub(r'^(basic|advanced|proficient|experienced|other)\s+', '', skill, flags=re.IGNORECASE)
            skill = re.sub(r'^\d+\.\s*', '', skill)
            
            # Skip category labels
            if skill.lower() in ['languages', 'frameworks', 'tools', 'other', 'technologies']:
                continue
            
            # Handle skills with parentheses - extract main skill name
            if '(' in skill and ')' in skill:
                # Extract main part before parentheses
                main_skill = skill.split('(')[0].strip()
                # Also check if there's useful info in parentheses
                paren_content = re.search(r'\(([^)]+)\)', skill)
                if paren_content:
                    paren_text = paren_content.group(1)
                    # For "AWS (basic)", just use "AWS"
                    if 'basic' not in paren_text.lower() and 'liquid' not in paren_text.lower():
                        # For "Hardware Integration (Raspberry Pi / FM9)", add both
                        if '/' in paren_text:
                            for part in paren_text.split('/'):
                                part = part.strip()
                                if part and len(part) > 2:
                                    found_skills.add(part.title())
                        else:
                            # Single item in parentheses might be worth adding
                            if len(paren_text.strip()) > 2 and paren_text.strip() not in ['basic', 'liquid']:
                                found_skills.add(paren_text.strip().title())
                if main_skill:
                    skill = main_skill
                else:
                    continue
            
            if skill and len(skill) > 2:
                # Handle special abbreviations
                if skill.lower() in ['ai', 'ml', 'api', 'aws', 'css', 'html', 'iot', 'js']:
                    if skill.lower() == 'js':
                        found_skills.add('JavaScript')
                    else:
                        found_skills.add(skill.upper())
                elif '/' in skill:
                    # Handle "HTML/CSS" or "Git/GitHub"
                    parts = skill.split('/')
                    for part in parts:
                        part = part.strip()
                        if part:
                            if part.lower() in ['html', 'css']:
                                found_skills.add(part.upper())
                            elif part.lower() == 'git':
                                found_skills.add('Git')
                            elif part.lower() == 'github':
                                found_skills.add('GitHub')
                            else:
                                found_skills.add(part.title())
                elif '-' in skill and not skill.startswith('-'):
                    found_skills.add(skill.title())
                else:
                    found_skills.add(skill.title() if skill.islower() else skill)
    
    # Also search entire text for common skills if section parsing didn't work well
    if len(found_skills) < 5:
        skill_keywords = {
            'python', 'javascript', 'java', 'react', 'node.js', 'nodejs',
            'typescript', 'html', 'css', 'sql', 'mongodb', 'postgresql',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'github',
            'flask', 'django', 'express', 'vue', 'angular', 'next.js',
            'machine learning', 'ai', 'artificial intelligence', 'ml',
            'data science', 'data analysis', 'pandas', 'numpy',
            'full stack', 'fullstack', 'frontend', 'backend', 'full-stack',
            'rest api', 'graphql', 'microservices', 'agile', 'scrum',
            'creative coding', 'music technology', 'hardware integration',
            'raspberry pi', 'embedded systems', 'iot', 'streamlit', 'vite',
            'tailwind css', 'shopify', 'railway'
        }
        
        for keyword in skill_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                if keyword in ['ai', 'ml', 'api', 'aws', 'css', 'html', 'iot']:
                    found_skills.add(keyword.upper())
                else:
                    found_skills.add(keyword.title() if keyword.islower() else keyword)
    
    return list(found_skills)[:20]  # Return up to 20 skills


def extract_location_from_resume(text):
    """Extract location from resume text - improved"""
    # Look for location in header (most common place)
    # Pattern: "City, State |" or "City, State | phone"
    header_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z]{2})\s*\|'
    match = re.search(header_pattern, text, re.MULTILINE)
    if match:
        city = match.group(1).strip()
        state = match.group(2).strip()
        # Clean up city if it has newlines
        city = city.replace('\n', ' ').strip()
        return f"{city}, {state}"
    
    # Fallback: look for any City, State pattern
    location_patterns = [
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z]{2})\b',  # City, State
        r'location[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z]{2})',  # Location: City, State
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Take the first valid match (usually in header)
            for match in matches:
                if len(match) == 2:
                    city = match[0].replace('\n', ' ').strip()
                    state = match[1].strip()
                    # Skip if city looks wrong (e.g., contains "Tankersley")
                    if 'tankersley' not in city.lower() and len(city) > 2:
                        return f"{city}, {state}"
    
    return ""


@app.route('/api/reports/<filename>')
def download_report(filename):
    """Download report files"""
    report_path = Path('output') / filename
    if report_path.exists():
        return send_file(report_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    # Get port from environment variable (for Railway/Heroku) or default to 5001
    port = int(os.environ.get('PORT', 5001))
    # Use 0.0.0.0 for Railway (allows external connections), 127.0.0.1 for local
    host = '0.0.0.0' if os.environ.get('RAILWAY_ENVIRONMENT') else '127.0.0.1'
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"\n🚀 Starting Job Cross-Reference Web App...")
    print(f"🌐 Open your browser to: http://localhost:{port}")
    print(f"📊 Your mentor network: 91 mentors ready")
    print(f"\nPress Ctrl+C to stop the server\n")
    app.run(debug=debug, port=port, host=host)

