# Quick Start Guide

## Step 1: Parse Your Mentor Lookbook

Your mentor lookbook has already been parsed! The file `mentors.csv` contains **71 mentors** with their expertise areas.

If you need to parse it again or parse a new lookbook:

```bash
python parse_mentor_lookbook.py mentor_lookbook.txt --format csv
```

## Step 2: Set Your Skills and Location

Before running the job search, you need to know:
- **Your current skills** (what you're good at now)
- **Your interests** (what you want to learn/grow into)
- **Your location** (for local job searches)

## Step 3: Run the Job Cross-Reference

### Example 1: Software Developer

```bash
python job_cross_reference.py mentors.csv \
  --skills "Software Development" "Python" "JavaScript" "Data Analytics" \
  --interests "AI" "Machine Learning" "Product Management" \
  --location "Huntsville, AL" \
  --us-wide
```

### Example 2: Business/Startup Focus

```bash
python job_cross_reference.py mentors.csv \
  --skills "Business Development" "Marketing" "Sales" "Fundraising" \
  --interests "Growth Strategy" "Startups" "Venture Capital" \
  --location "Birmingham, AL" \
  --us-wide
```

### Example 3: With Job API Keys (for real job data)

First, get free API keys from [Adzuna](https://developer.adzuna.com/):

```bash
python job_cross_reference.py mentors.csv \
  --skills "Your Skills Here" \
  --location "Your City, State" \
  --adzuna-app-id YOUR_APP_ID \
  --adzuna-app-key YOUR_APP_KEY
```

## Step 4: Review Your Results

Check the `output/` folder for:
- **CSV report**: Spreadsheet with all matched jobs
- **HTML report**: Visual report with top 50 matches

## What the Script Does

1. ✅ Loads your **71 mentors** from `mentors.csv`
2. ✅ Extracts expertise areas (**40 unique areas** found!)
3. ✅ Searches for jobs matching those skills
4. ✅ Scores each job based on:
   - Your skills (40%)
   - Mentor network skills (30%)
   - Your interests (20%)
   - Mentor company connections (10%)
5. ✅ Generates reports sorted by match score

## Top Mentor Expertise Areas

Based on your complete mentor network (71 mentors):
- **Business Development** (25 mentors)
- **Growth Strategy** (25 mentors)
- **Leadership and Management** (22 mentors)
- **Pitching** (21 mentors)
- **Fundraising** (20 mentors)
- **B2B Sales** (19 mentors)
- **KPIs and Business Metrics** (18 mentors)
- **Marketing** (15 mentors)
- **Product Research** (15 mentors)
- **Software Development** (14 mentors)
- **Revenue Models** (13 mentors)
- **Data and Analytics** (13 mentors)
- **Go-To Market Strategy** (12 mentors)
- **Sales** (12 mentors)

These areas will be used to find relevant job opportunities!

