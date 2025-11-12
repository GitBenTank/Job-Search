# Job Cross-Reference Tool

Cross-reference your Spark/Gener8tor network mentors with available job opportunities based on skills, location, and career alignment.

## Features

- 📊 Process mentor data from CSV or JSON files
- 🔍 Search jobs from multiple sources (Adzuna API, extensible for others)
- 🎯 Intelligent skill matching algorithm
- 📍 Location-based filtering (local + US-wide)
- 📈 Match scoring based on:
  - Your current skills (40% weight)
  - Mentor network skills (30% weight)
  - Your interests/future skills (20% weight)
  - Mentor company connections (10% weight)
- 📄 Generate CSV and HTML reports

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Get API keys:
   - **Adzuna**: Free API available at https://developer.adzuna.com/
   - Sign up and get your App ID and App Key

## Usage

### Basic Usage

```bash
python job_cross_reference.py mentor_file.csv \
  --skills "Python" "Data Analysis" "Machine Learning" \
  --interests "AI" "Product Management" \
  --location "San Francisco, CA" \
  --us-wide
```

### With API Keys

```bash
python job_cross_reference.py mentor_file.csv \
  --skills "Python" "Data Analysis" \
  --location "San Francisco, CA" \
  --adzuna-app-id YOUR_APP_ID \
  --adzuna-app-key YOUR_APP_KEY
```

### Arguments

- `mentor_file`: Path to your mentor CSV or JSON file (required)
- `--skills`: Your current skills, space-separated (required)
- `--interests`: Your interests/future skills, space-separated (optional)
- `--location`: Your location for local job search (optional)
- `--us-wide`: Also search US-wide jobs (default: True)
- `--adzuna-app-id`: Adzuna API App ID (optional)
- `--adzuna-app-key`: Adzuna API App Key (optional)

## Mentor File Format

### CSV Format

Your mentor CSV should include columns like:
- `name` or `mentor_name`
- `company` or `organization`
- `skills`, `expertise`, `specialties`, or `areas`
- Any other relevant fields

Example:
```csv
name,company,skills,title
John Doe,Google,"Python, Machine Learning, AI",Senior Engineer
Jane Smith,Microsoft,"Product Management, Strategy",Product Manager
```

### JSON Format

```json
[
  {
    "name": "John Doe",
    "company": "Google",
    "skills": "Python, Machine Learning, AI",
    "title": "Senior Engineer"
  },
  {
    "name": "Jane Smith",
    "company": "Microsoft",
    "skills": "Product Management, Strategy",
    "title": "Product Manager"
  }
]
```

## Output

The script generates two reports in the `output/` directory:

1. **CSV Report** (`job_matches_YYYYMMDD_HHMMSS.csv`): 
   - Spreadsheet-friendly format
   - Includes job title, company, location, match score, URL, salary range

2. **HTML Report** (`job_matches_YYYYMMDD_HHMMSS.html`):
   - Visual report with top 50 matches
   - Color-coded match scores
   - Clickable job links

## Quick Start: Parsing Mentor Lookbook

If you have a mentor lookbook (formatted text from Spark/Gener8tor dashboard):

1. **Parse the lookbook into CSV:**
   ```bash
   python parse_mentor_lookbook.py mentor_lookbook.txt --format csv
   ```
   This creates `mentors.csv` with all mentor data structured.

2. **Run the cross-reference analysis:**
   ```bash
   python job_cross_reference.py mentors.csv \
     --skills "Software Engineering" "Python" "JavaScript" \
     --interests "AI" "Startups" \
     --location "Austin, TX"
   ```

3. **Check the `output/` folder for your reports!**

## Example Workflow

### Option 1: Using Mentor Lookbook (Recommended)

1. Copy your mentor lookbook text and save it as `mentor_lookbook.txt`
2. Parse it: `python parse_mentor_lookbook.py mentor_lookbook.txt`
3. Run cross-reference: `python job_cross_reference.py mentors.csv --skills "Your Skills" --location "Your City, State"`

### Option 2: Using Existing CSV/JSON

1. Export your mentor list from Spark/Gener8tor dashboard as CSV
2. Save it in this directory (e.g., `mentors.csv`)
3. Run the script with your skills:
   ```bash
   python job_cross_reference.py mentors.csv \
     --skills "Software Engineering" "Python" "JavaScript" \
     --interests "AI" "Startups" \
     --location "Austin, TX"
   ```
4. Check the `output/` folder for your reports!

## Extending the Tool

The script is designed to be extensible:

- **Add more job APIs**: Extend the `JobSearcher` class with new methods
- **Customize matching**: Modify the `SkillMatcher.calculate_match_score()` method
- **Additional data sources**: Add methods to `MentorProcessor` for different formats

## Notes

- Without API keys, the script will still run but won't fetch real job data
- You can manually add job data by modifying the `JobSearcher` class
- The matching algorithm can be customized based on your priorities

## Troubleshooting

**"No jobs found"**: 
- Check if API keys are configured correctly
- Verify your location format
- Try without location filter (US-wide only)

**"Error loading mentors"**:
- Ensure CSV/JSON format matches expected structure
- Check file encoding (should be UTF-8)

**Low match scores**:
- Add more skills to your profile
- Include more diverse interests
- Ensure mentor data includes skills/expertise fields

