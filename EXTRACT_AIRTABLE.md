# Extracting Mentor Data from Airtable

Since you have Developer Tools open, here are the best methods:

## Method 1: Network Tab (Get Raw Data) ⭐ RECOMMENDED

1. **Switch to the "Network" tab** in Developer Tools (instead of Sources)
2. **Filter by "Fetch/XHR"** or "WS" (WebSocket) - Airtable often uses these
3. **Clear the network log** (trash icon)
4. **Scroll through the entire Mentor Lookbook page** to load all records
5. **Look for requests** that contain:
   - `airtable.com/api`
   - `records` or `data` in the URL
   - JSON responses
6. **Click on a promising request** → Go to "Response" or "Preview" tab
7. **Right-click** → "Copy response" or "Save as..."
8. **Save as JSON file** (e.g., `airtable_mentors.json`)

## Method 2: Console Tab (Extract from DOM)

1. **Switch to the "Console" tab** in Developer Tools
2. **Scroll to load all mentors** on the page first
3. **Paste and run this script**:

```javascript
// Extract all mentor data from Airtable page
function extractMentors() {
  const mentors = [];
  
  // Try to find Airtable record elements
  // Airtable uses various class names, try different selectors
  const selectors = [
    '[data-testid*="record"]',
    '[class*="record"]',
    '[class*="Record"]',
    '.record',
    '[data-record-id]'
  ];
  
  let records = [];
  for (const selector of selectors) {
    records = document.querySelectorAll(selector);
    if (records.length > 0) break;
  }
  
  console.log(`Found ${records.length} record elements`);
  
  // Alternative: Look for text patterns
  const pageText = document.body.innerText;
  const mentorMatches = pageText.match(/Full Name\s*\n\s*([^\n]+)/g);
  
  if (mentorMatches) {
    console.log(`Found ${mentorMatches.length} "Full Name" entries in text`);
  }
  
  // Try to access Airtable's internal data structure
  if (window.__AIRTABLE_BASE__ || window.__INITIAL_STATE__) {
    console.log('Found Airtable data structure!');
    console.log(window.__AIRTABLE_BASE__ || window.__INITIAL_STATE__);
  }
  
  // Return all text content as fallback
  return {
    recordCount: records.length,
    pageText: pageText,
    suggestion: 'Copy the entire page text (Cmd+A, Cmd+C) and paste into a file'
  };
}

const result = extractMentors();
console.log(result);
```

## Method 3: Application/Storage Tab

1. **Go to "Application" tab** (Chrome) or "Storage" tab (Firefox)
2. **Look under "Local Storage"** or "Session Storage"
3. **Find entries** related to Airtable
4. **Copy the values** - they might contain JSON data

## Method 4: Simple Copy-Paste (Easiest)

Since Airtable can be tricky with developer tools:

1. **Scroll to the very top** of the Mentor Lookbook
2. **Click once** in the content area
3. **Press Cmd+A** (Mac) or Ctrl+A (Windows) to select all
4. **Press Cmd+C** (Mac) or Ctrl+C (Windows) to copy
5. **Paste into a text file** and save as `mentor_lookbook_complete.txt`

This method captures everything visible on the page.

## Method 5: Check Airtable API (If You Have Access)

If you have API access or can view the page source:

1. **View Page Source** (Right-click → View Page Source)
2. **Search for** `"records"` or `"data"` 
3. **Look for JSON data** embedded in the page
4. **Copy the JSON** and save it

## Quick Test Script

Run this in the Console to see what's available:

```javascript
// Quick diagnostic
console.log('=== Airtable Data Extraction Diagnostic ===');
console.log('Window objects:', Object.keys(window).filter(k => k.includes('AIR') || k.includes('TABLE')));
console.log('Document records:', document.querySelectorAll('[class*="record"], [data-record-id]').length);
console.log('Full Name occurrences:', (document.body.innerText.match(/Full Name/g) || []).length);
console.log('Page text length:', document.body.innerText.length);
```

## After Extraction

Once you have the data:

1. **Save it** in `/Users/bentankersley/JobSearch/`
2. **Run the parser**:
   ```bash
   python3 parse_mentor_lookbook.py <your_file> --format csv -o mentors_new.csv
   ```
3. **Compare with existing**:
   ```bash
   python3 -c "
   import pandas as pd
   old = pd.read_csv('mentors.csv')
   new = pd.read_csv('mentors_new.csv')
   print(f'Old: {len(old)}, New: {len(new)}, Difference: {len(new) - len(old)}')
   "
   ```

## Recommended Approach

**For Airtable specifically, I recommend Method 4 (Copy-Paste)** because:
- Airtable's DOM structure can be complex
- The copy-paste method captures all visible text
- It's the most reliable for getting complete data
- We can parse the text format we've already handled

Just make sure to:
1. Scroll through the ENTIRE page first (to load all lazy-loaded content)
2. Select All (Cmd+A)
3. Copy (Cmd+C)  
4. Paste into a text file

Then I can parse it and we'll have everyone!


