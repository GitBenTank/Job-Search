# Loading All Mentors from Airtable

The script found 24 mentors, but we know there are more (we have 71 in the database). Airtable often lazy-loads records, so you need to scroll to load them all.

## Steps to Load All Mentors:

1. **Scroll to the very top** of the Mentor Lookbook page
2. **Slowly scroll all the way to the bottom** - this forces Airtable to load all records
3. **Wait for loading indicators** to finish (spinners, etc.)
4. **Scroll back up** to make sure everything is loaded
5. **Run the script again** in the console

## Alternative: Use Copy-Paste Method

Since Airtable lazy-loads, the most reliable method is:

1. **Scroll through the ENTIRE page** (top to bottom, slowly)
2. **Wait for all records to load** (no more spinners)
3. **Click anywhere in the content area**
4. **Press Cmd+A** (Select All)
5. **Press Cmd+C** (Copy)
6. **Paste into a text file** and save as `mentor_lookbook_complete.txt`

This captures everything that's visible, including all loaded mentors.

## Quick Check: How Many Should There Be?

To see how many we currently have:
```bash
cd /Users/bentankersley/JobSearch
python3 -c "import pandas as pd; df = pd.read_csv('mentors.csv'); print(f'Current mentors in database: {len(df)}')"
```

We should aim to get ALL mentors, not just the 24 that loaded initially.


