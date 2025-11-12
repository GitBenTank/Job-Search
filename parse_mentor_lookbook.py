#!/usr/bin/env python3
"""
Parser for Spark/Gener8tor Mentor Lookbook
Converts the formatted text lookbook into structured CSV/JSON format
"""

import re
import csv
import json
from typing import List, Dict


def parse_mentor_lookbook(text_content: str) -> List[Dict]:
    """Parse the mentor lookbook text into structured data"""
    mentors = []
    
    # Handle two formats:
    # Format 1: Name | Company followed by Full Name (new format)
    # Format 2: Full Name at the start (old format)
    
    # First, try to split by name pattern (Format 1)
    # Pattern: Name | Company on its own line, followed by Full Name
    name_pattern = r'\n([A-Z][^\n|]+(?:\s*\|\s*[^\n|]+)?)\s*\nFull Name\n'
    entries_by_name = re.split(name_pattern, text_content)
    
    # If that doesn't work well, try Format 2: split by "Full Name\n"
    if len(entries_by_name) < 2:
        entries = re.split(r'\n(?=Full Name\n)', text_content)
    else:
        # Reconstruct entries - every other element is a name, then the entry
        entries = []
        for i in range(1, len(entries_by_name), 2):
            if i + 1 < len(entries_by_name):
                # Combine name with entry content
                entries.append(entries_by_name[i] + '\nFull Name\n' + entries_by_name[i+1])
    
    # Fallback to original method if needed
    if not entries or len(entries) < 2:
        entries = re.split(r'\n(?=Full Name\n)', text_content)
    
    for entry in entries:
        if not entry.strip() or 'Full Name' not in entry:
            continue
        
        mentor = {}
        lines = entry.strip().split('\n')
        
        current_field = None
        current_value = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if this is a field label
            if line in ['Full Name', 'Title', 'Company', 'City', 'State', 'Country', 
                       'Areas of Expertise', 'Biography', 'LinkedIn', 'Website']:
                # Save previous field
                if current_field and current_value:
                    mentor[current_field.lower().replace(' ', '_')] = '\n'.join(current_value).strip()
                
                # Start new field
                current_field = line
                current_value = []
            elif current_field:
                # This is a continuation of the current field
                current_value.append(line)
            else:
                # Might be a continuation from previous entry or header
                continue
        
        # Save last field
        if current_field and current_value:
            mentor[current_field.lower().replace(' ', '_')] = '\n'.join(current_value).strip()
        
        # Process areas of expertise - split by newlines or commas
        if 'areas_of_expertise' in mentor:
            expertise = mentor['areas_of_expertise']
            # Split by newlines first, then by commas
            expertise_list = []
            for item in expertise.split('\n'):
                expertise_list.extend([e.strip() for e in item.split(',') if e.strip()])
            mentor['areas_of_expertise'] = ', '.join(expertise_list)
            mentor['areas_of_expertise_list'] = expertise_list
        
        # Clean up name - remove company if present
        if 'full_name' in mentor:
            name = mentor['full_name']
            # Remove "| Company" pattern if present
            if '|' in name:
                name = name.split('|')[0].strip()
            mentor['full_name'] = name
            mentor['name'] = name
        
        if mentor:  # Only add if we extracted data
            mentors.append(mentor)
    
    return mentors


def save_to_csv(mentors: List[Dict], filename: str = 'mentors.csv'):
    """Save mentors to CSV file"""
    if not mentors:
        print("No mentors to save")
        return
    
    # Get all unique keys
    all_keys = set()
    for mentor in mentors:
        all_keys.update(mentor.keys())
    
    # Define column order (exclude areas_of_expertise_list from CSV)
    column_order = [
        'name', 'full_name', 'title', 'company', 'city', 'state', 'country',
        'areas_of_expertise', 'biography', 'linkedin', 'website'
    ]
    
    # Add any other keys not in the standard order (but exclude areas_of_expertise_list)
    other_keys = sorted([k for k in all_keys if k not in column_order and k != 'areas_of_expertise_list'])
    fieldnames = [k for k in column_order if k in all_keys] + other_keys
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for mentor in mentors:
            writer.writerow(mentor)
    
    print(f"✓ Saved {len(mentors)} mentors to {filename}")


def save_to_json(mentors: List[Dict], filename: str = 'mentors.json'):
    """Save mentors to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(mentors, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(mentors)} mentors to {filename}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse mentor lookbook into CSV/JSON')
    parser.add_argument('input_file', help='Path to mentor lookbook text file')
    parser.add_argument('--output', '-o', default='mentors.csv', 
                       help='Output filename (default: mentors.csv)')
    parser.add_argument('--format', choices=['csv', 'json', 'both'], default='csv',
                       help='Output format (default: csv)')
    
    args = parser.parse_args()
    
    # Read input file
    print(f"Reading mentor lookbook from: {args.input_file}")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse mentors
    print("Parsing mentor data...")
    mentors = parse_mentor_lookbook(content)
    
    print(f"✓ Parsed {len(mentors)} mentors")
    
    # Save in requested format
    if args.format in ['csv', 'both']:
        csv_file = args.output if args.output.endswith('.csv') else args.output.replace('.json', '.csv')
        save_to_csv(mentors, csv_file)
    
    if args.format in ['json', 'both']:
        json_file = args.output if args.output.endswith('.json') else args.output.replace('.csv', '.json')
        save_to_json(mentors, json_file)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Mentors: {len(mentors)}")
    
    # Count unique companies
    companies = set()
    for mentor in mentors:
        if mentor.get('company'):
            companies.add(mentor['company'])
    print(f"Unique Companies: {len(companies)}")
    
    # Count unique expertise areas
    all_expertise = set()
    for mentor in mentors:
        if mentor.get('areas_of_expertise_list'):
            all_expertise.update(mentor['areas_of_expertise_list'])
    print(f"Unique Expertise Areas: {len(all_expertise)}")
    print(f"\nTop Expertise Areas:")
    from collections import Counter
    expertise_counts = Counter()
    for mentor in mentors:
        if mentor.get('areas_of_expertise_list'):
            expertise_counts.update(mentor['areas_of_expertise_list'])
    for area, count in expertise_counts.most_common(10):
        print(f"  - {area}: {count} mentors")


if __name__ == "__main__":
    main()

