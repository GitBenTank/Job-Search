#!/usr/bin/env python3
"""
Quick script to merge new mentor batches with existing database
Usage: python merge_new_mentors.py <new_mentor_file.txt>
"""

import sys
import pandas as pd
from parse_mentor_lookbook import parse_mentor_lookbook, save_to_csv
from pathlib import Path

def merge_mentors(new_file_path: str):
    """Parse new mentors and merge with existing, showing what's new"""
    
    # Load existing mentors
    existing_file = 'mentors.csv'
    if Path(existing_file).exists():
        df_existing = pd.read_csv(existing_file)
        print(f"📊 Current mentors in database: {len(df_existing)}")
    else:
        df_existing = pd.DataFrame()
        print("📊 No existing mentors file found, starting fresh")
    
    # Parse new mentors
    print(f"\n🔍 Parsing new mentors from: {new_file_path}")
    with open(new_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_mentors = parse_mentor_lookbook(content)
    print(f"✓ Found {len(new_mentors)} mentors in new file")
    
    # Convert to DataFrame
    df_new = pd.DataFrame(new_mentors)
    
    if len(df_existing) == 0:
        # No existing data, just save new
        save_to_csv(new_mentors, existing_file)
        print(f"\n✅ Saved {len(new_mentors)} mentors to {existing_file}")
        return
    
    # Create deduplication key
    df_existing['dedup_key'] = (
        df_existing['name'].str.lower().str.strip().fillna('') + '|' + 
        df_existing['company'].str.lower().str.strip().fillna('')
    )
    df_new['dedup_key'] = (
        df_new['name'].str.lower().str.strip().fillna('') + '|' + 
        df_new['company'].str.lower().str.strip().fillna('')
    )
    
    # Find new mentors (not in existing)
    existing_keys = set(df_existing['dedup_key'].values)
    new_keys = set(df_new['dedup_key'].values)
    truly_new_keys = new_keys - existing_keys
    
    print(f"\n📈 Analysis:")
    print(f"  - Existing mentors: {len(df_existing)}")
    print(f"  - New mentors found: {len(df_new)}")
    print(f"  - Already in database: {len(new_keys) - len(truly_new_keys)}")
    print(f"  - NEW mentors to add: {len(truly_new_keys)}")
    
    if len(truly_new_keys) == 0:
        print("\n✅ No new mentors found - all are already in the database!")
        return
    
    # Get the new mentor records
    df_truly_new = df_new[df_new['dedup_key'].isin(truly_new_keys)].copy()
    df_truly_new = df_truly_new.drop('dedup_key', axis=1)
    
    # Show new mentor names
    print(f"\n🆕 New mentors being added:")
    for idx, row in df_truly_new.iterrows():
        name = row.get('name', 'N/A')
        company = row.get('company', 'N/A')
        print(f"  - {name} | {company}")
    
    # Merge
    df_existing_clean = df_existing.drop('dedup_key', axis=1)
    df_combined = pd.concat([df_existing_clean, df_truly_new], ignore_index=True)
    
    # Save
    df_combined.to_csv(existing_file, index=False)
    
    print(f"\n✅ Updated {existing_file}")
    print(f"   Total mentors now: {len(df_combined)}")
    
    # Summary stats
    companies = df_combined['company'].dropna().unique()
    print(f"   Unique companies: {len(companies)}")
    
    if 'areas_of_expertise' in df_combined.columns:
        all_expertise = set()
        for expertise in df_combined['areas_of_expertise'].dropna():
            if isinstance(expertise, str):
                all_expertise.update([e.strip() for e in expertise.split(',') if e.strip()])
        print(f"   Unique expertise areas: {len(all_expertise)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python merge_new_mentors.py <new_mentor_file.txt>")
        sys.exit(1)
    
    merge_mentors(sys.argv[1])


