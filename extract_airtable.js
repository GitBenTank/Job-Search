// Airtable Mentor Data Extractor
// Run this in the browser console on the Airtable Mentor Lookbook page

(function() {
  console.log('🔍 Starting Airtable mentor extraction...');
  
  // Method 1: Try to find Airtable's internal data
  let airtableData = null;
  
  // Check for common Airtable data structures
  const dataSources = [
    window.__AIRTABLE_BASE__,
    window.__INITIAL_STATE__,
    window.__AIRTABLE_EMBED__,
    window.airtable,
    window.Airtable
  ];
  
  for (const source of dataSources) {
    if (source) {
      console.log('✅ Found Airtable data source:', source);
      airtableData = source;
      break;
    }
  }
  
  // Method 2: Extract from DOM
  const mentors = [];
  const pageText = document.body.innerText;
  
  // Count "Full Name" occurrences
  const fullNameMatches = pageText.match(/Full Name\s*\n\s*([^\n]+(?:\s*\|\s*[^\n]+)?)/g);
  console.log(`📊 Found ${fullNameMatches ? fullNameMatches.length : 0} "Full Name" entries`);
  
  // Method 3: Try to find record elements
  const recordSelectors = [
    '[data-testid*="record"]',
    '[class*="record"]',
    '[class*="Record"]',
    '.record',
    '[data-record-id]',
    '[class*="row"]',
    '[class*="Row"]'
  ];
  
  let records = [];
  for (const selector of recordSelectors) {
    const found = document.querySelectorAll(selector);
    if (found.length > 10) { // Only use if we find a reasonable number
      records = Array.from(found);
      console.log(`✅ Found ${records.length} records using selector: ${selector}`);
      break;
    }
  }
  
  // Method 4: Extract structured data from text
  function parseMentorText(text) {
    const mentors = [];
    const sections = text.split(/(?=Full Name\s*\n)/);
    
    for (const section of sections) {
      if (!section.includes('Full Name')) continue;
      
      const mentor = {};
      const lines = section.split('\n').map(l => l.trim()).filter(l => l);
      
      let currentField = null;
      let currentValue = [];
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        if (line === 'Full Name' || line === 'Title' || line === 'Company' || 
            line === 'City' || line === 'State' || line === 'Country' ||
            line === 'Areas of Expertise' || line === 'Biography' || 
            line === 'LinkedIn' || line === 'Website') {
          if (currentField && currentValue.length > 0) {
            mentor[currentField.toLowerCase().replace(/\s+/g, '_')] = currentValue.join(' ').trim();
          }
          currentField = line;
          currentValue = [];
        } else if (currentField && line) {
          currentValue.push(line);
        }
      }
      
      if (currentField && currentValue.length > 0) {
        mentor[currentField.toLowerCase().replace(/\s+/g, '_')] = currentValue.join(' ').trim();
      }
      
      if (Object.keys(mentor).length > 0) {
        mentors.push(mentor);
      }
    }
    
    return mentors;
  }
  
  const parsedMentors = parseMentorText(pageText);
  console.log(`📋 Parsed ${parsedMentors.length} mentors from page text`);
  
  // Output results
  const result = {
    timestamp: new Date().toISOString(),
    methods: {
      airtableData: airtableData ? 'Found' : 'Not found',
      domRecords: records.length,
      textMatches: fullNameMatches ? fullNameMatches.length : 0,
      parsedMentors: parsedMentors.length
    },
    mentors: parsedMentors,
    pageTextLength: pageText.length,
    recommendation: parsedMentors.length > 0 
      ? 'Use parsed mentors data below'
      : 'Try Method 4: Select All (Cmd+A) and Copy (Cmd+C) the entire page'
  };
  
  console.log('\n📊 EXTRACTION SUMMARY:');
  console.log('====================');
  console.log(`Airtable Data: ${result.methods.airtableData}`);
  console.log(`DOM Records: ${result.methods.domRecords}`);
  console.log(`Text Matches: ${result.methods.textMatches}`);
  console.log(`Parsed Mentors: ${result.methods.parsedMentors}`);
  console.log(`\n💡 Recommendation: ${result.recommendation}`);
  
  if (parsedMentors.length > 0) {
    console.log('\n✅ Copy this JSON to a file:');
    console.log(JSON.stringify(result.mentors, null, 2));
    
    // Try to copy to clipboard
    if (navigator.clipboard) {
      navigator.clipboard.writeText(JSON.stringify(result.mentors, null, 2))
        .then(() => console.log('✅ Copied to clipboard!'))
        .catch(() => console.log('⚠️ Could not copy to clipboard'));
    }
  } else {
    console.log('\n📝 Full page text (first 1000 chars):');
    console.log(pageText.substring(0, 1000));
    console.log('\n...');
    console.log('\n💡 Suggestion: Copy entire page text (Cmd+A, Cmd+C) and paste into a .txt file');
  }
  
  return result;
})();


