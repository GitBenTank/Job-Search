# How to Extract Complete Mentor Data from Airtable

Here are several methods to get all the mentor data so we can ensure we have everyone:

## Method 1: Copy All Text (Easiest)

1. **Scroll through the entire Mentor Lookbook page** to load all mentors (Airtable may lazy-load)
2. **Select All**: Press `Cmd+A` (Mac) or `Ctrl+A` (Windows/Linux)
3. **Copy**: Press `Cmd+C` (Mac) or `Ctrl+C` (Windows/Linux)
4. **Paste into a text file**: Create a new file and paste everything
5. Save it as `mentor_lookbook_complete.txt` in the JobSearch folder

## Method 2: Browser Developer Tools (Most Reliable)

1. **Open Developer Tools**:
   - Chrome/Edge: Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - Firefox: Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - Safari: Enable Developer menu first (Preferences > Advanced > Show Develop menu), then `Cmd+Option+I`

2. **Go to Network Tab** in Developer Tools

3. **Filter by "Fetch/XHR"** to see API calls

4. **Refresh the page** or scroll to load all mentors

5. **Look for API requests** to Airtable (usually contain "airtable.com" in the URL)

6. **Right-click on the request** → "Copy" → "Copy as cURL" or "Copy response"

7. **Save the response** as JSON or text file

## Method 3: View Page Source

1. **Right-click on the page** → "View Page Source" (or `Cmd+Option+U` / `Ctrl+U`)

2. **Search for mentor data** using `Cmd+F` / `Ctrl+F`:
   - Search for "Full Name"
   - Search for mentor names you know exist

3. **Copy relevant sections** or save the entire source as HTML

## Method 4: Airtable Export (If Available)

1. **Look for an "Export" or "Download" button** in the Airtable interface
2. **Export as CSV or JSON** if the option is available
3. **Save the exported file** in the JobSearch folder

## Method 5: Browser Extension (Advanced)

Install a browser extension like:
- **Airtable Exporter** (if available)
- **Table Capture** (Chrome extension)
- **Copy All URLs** or similar data extraction tools

## Method 6: Manual Scroll & Copy (For Large Lists)

If the list is very long:

1. **Scroll to the top** of the Mentor Lookbook
2. **Click in the first mentor entry**
3. **Hold Shift** and scroll to the bottom
4. **Click on the last mentor entry** (this selects everything in between)
5. **Copy** (`Cmd+C` / `Ctrl+C`)
6. **Paste into a text file**

## What to Look For

When extracting, make sure you capture:
- ✅ All mentor names
- ✅ Company names
- ✅ Titles
- ✅ Areas of Expertise
- ✅ Biographies
- ✅ LinkedIn URLs
- ✅ Website URLs
- ✅ Location information (City, State, Country)

## After Extraction

Once you have the data:

1. **Save it** as `mentor_lookbook_complete.txt` in the `/Users/bentankersley/JobSearch/` folder
2. **Run the parser**:
   ```bash
   cd /Users/bentankersley/JobSearch
   python3 parse_mentor_lookbook.py mentor_lookbook_complete.txt --format csv -o mentors_complete.csv
   ```
3. **Check the count** - it should tell you how many mentors were found

## Quick Check: Count Current Mentors

To see how many we currently have:
```bash
cd /Users/bentankersley/JobSearch
python3 -c "import pandas as pd; df = pd.read_csv('mentors.csv'); print(f'Current mentors: {len(df)}')"
```

## Recommended Approach

**I recommend Method 1 (Copy All Text)** as it's the simplest:
1. Scroll through the entire page to ensure all mentors are loaded
2. Select All (`Cmd+A`)
3. Copy (`Cmd+C`)
4. Paste into a new text file
5. Save as `mentor_lookbook_complete.txt`

Then I can parse it and combine it with what we already have!


