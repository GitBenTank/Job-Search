// Job Cross-Reference Web App - Frontend JavaScript

let currentJobs = [];
let currentReports = {};
let bookmarkedJobs = new Set();
let mentorConnections = {}; // Cache for mentor connections by company

// Load mentor stats on page load
document.addEventListener('DOMContentLoaded', () => {
    loadMentorStats();
    loadRecentSearches();
    loadBookmarks();
    
    // Resume upload handler
    const resumeUpload = document.getElementById('resumeUpload');
    const clearResume = document.getElementById('clearResume');
    
    if (resumeUpload) {
        resumeUpload.addEventListener('change', handleResumeUpload);
    }
    
    if (clearResume) {
        clearResume.addEventListener('click', clearResumeData);
    }
    
    // Form submission
    document.getElementById('searchForm').addEventListener('submit', handleSearch);
    
    // Filter handlers
    document.getElementById('searchFilter').addEventListener('input', filterJobs);
    document.getElementById('locationFilter').addEventListener('change', filterJobs);
    document.getElementById('sortFilter').addEventListener('change', filterJobs);
    document.getElementById('scoreFilter').addEventListener('change', filterJobs);
    document.getElementById('mentorFilter').addEventListener('change', filterJobs);
    
    // Download buttons
    document.getElementById('downloadCsv').addEventListener('click', () => {
        if (currentReports.csv_report) {
            window.open(`/api/reports/${currentReports.csv_report.split('/').pop()}`, '_blank');
        }
    });
    
    document.getElementById('viewHtml').addEventListener('click', () => {
        if (currentReports.html_report) {
            window.open(`/api/reports/${currentReports.html_report.split('/').pop()}`, '_blank');
        }
    });
    
    // Bookmarks toggle
    const toggleBtn = document.getElementById('toggleBookmarks');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const bookmarksList = document.getElementById('bookmarksList');
            const isVisible = bookmarksList.style.display !== 'none';
            bookmarksList.style.display = isVisible ? 'none' : 'block';
            toggleBtn.textContent = isVisible ? 'Show' : 'Hide';
        });
    }
});

async function loadMentorStats() {
    try {
        const response = await fetch('/api/mentors');
        const data = await response.json();
        
        document.getElementById('totalMentors').textContent = data.total_mentors;
        document.getElementById('totalCompanies').textContent = data.unique_companies;
        document.getElementById('totalSkills').textContent = data.unique_skills;
    } catch (error) {
        console.error('Error loading mentor stats:', error);
    }
}

async function handleSearch(e) {
    e.preventDefault();
    
    const form = e.target;
    const btn = document.getElementById('searchBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    // Get form data
    const skills = form.skills.value.split(',').map(s => s.trim()).filter(s => s);
    const interests = form.interests.value.split(',').map(s => s.trim()).filter(s => s);
    const location = form.location.value.trim();
    const us_wide = form.us_wide.checked;
    
    if (skills.length === 0) {
        alert('Please enter at least one skill');
        return;
    }
    
    // Show loading state
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    
    // Hide previous results
    document.getElementById('resultsCard').style.display = 'none';
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                skills,
                interests,
                location,
                us_wide
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Store results
        currentJobs = data.jobs || [];
        currentReports = {
            csv_report: data.csv_report,
            html_report: data.html_report
        };
        
        // Save to recent searches
        saveRecentSearch({ skills, interests, location, us_wide, timestamp: Date.now() });
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Search error:', error);
        alert('Error searching for jobs: ' + error.message);
    } finally {
        // Reset button
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

function displayResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const resultsStats = document.getElementById('resultsStats');
    const jobsList = document.getElementById('jobsList');
    
    // Show results card
    resultsCard.style.display = 'block';
    
    // Update stats
    const stats = data.stats;
    resultsStats.textContent = `${stats.total_jobs} jobs found | ${stats.high_matches} high matches (≥50%)`;
    
    // Display jobs
    currentJobs = data.jobs;
    filterJobs();
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Track which jobs have mentor connections
const jobsWithMentors = new Set();

function filterJobs() {
    const jobsList = document.getElementById('jobsList');
    const searchFilter = document.getElementById('searchFilter').value.toLowerCase();
    const locationFilter = document.getElementById('locationFilter').value;
    const sortFilter = document.getElementById('sortFilter').value;
    const scoreFilter = document.getElementById('scoreFilter').value;
    const mentorFilter = document.getElementById('mentorFilter').checked;
    const userLocation = document.getElementById('location').value.toLowerCase();
    
    // Filter jobs
    let filtered = currentJobs.filter(job => {
        // Text filter
        const matchesSearch = !searchFilter || 
            job.title.toLowerCase().includes(searchFilter) ||
            job.company.toLowerCase().includes(searchFilter) ||
            (job.location && job.location.toLowerCase().includes(searchFilter));
        
        // Score filter
        const score = job.match_score || 0;
        const matchesScore = scoreFilter === 'all' || score >= parseInt(scoreFilter);
        
        // Location filter - strict matching
        let matchesLocation = true;
        if (locationFilter === 'local' && userLocation) {
            // Extract city and state from user location
            const locationParts = userLocation.split(',').map(s => s.trim().toLowerCase());
            const userCity = locationParts[0] || '';
            const userState = locationParts[1] || '';
            
            if (!userCity && !userState) {
                // No valid location provided, show all
                matchesLocation = true;
            } else {
                const jobLocation = (job.location || '').toLowerCase();
                const jobTitle = (job.title || '').toLowerCase();
                
                // State abbreviation mapping (all 50 states)
                const stateMap = {
                    'al': 'alabama', 'alabama': 'al',
                    'ak': 'alaska', 'alaska': 'ak',
                    'az': 'arizona', 'arizona': 'az',
                    'ar': 'arkansas', 'arkansas': 'ar',
                    'ca': 'california', 'california': 'ca',
                    'co': 'colorado', 'colorado': 'co',
                    'ct': 'connecticut', 'connecticut': 'ct',
                    'de': 'delaware', 'delaware': 'de',
                    'fl': 'florida', 'florida': 'fl',
                    'ga': 'georgia', 'georgia': 'ga',
                    'hi': 'hawaii', 'hawaii': 'hi',
                    'id': 'idaho', 'idaho': 'id',
                    'il': 'illinois', 'illinois': 'il',
                    'in': 'indiana', 'indiana': 'in',
                    'ia': 'iowa', 'iowa': 'ia',
                    'ks': 'kansas', 'kansas': 'ks',
                    'ky': 'kentucky', 'kentucky': 'ky',
                    'la': 'louisiana', 'louisiana': 'la',
                    'me': 'maine', 'maine': 'me',
                    'md': 'maryland', 'maryland': 'md',
                    'ma': 'massachusetts', 'massachusetts': 'ma',
                    'mi': 'michigan', 'michigan': 'mi',
                    'mn': 'minnesota', 'minnesota': 'mn',
                    'ms': 'mississippi', 'mississippi': 'ms',
                    'mo': 'missouri', 'missouri': 'mo',
                    'mt': 'montana', 'montana': 'mt',
                    'ne': 'nebraska', 'nebraska': 'ne',
                    'nv': 'nevada', 'nevada': 'nv',
                    'nh': 'new hampshire', 'new hampshire': 'nh',
                    'nj': 'new jersey', 'new jersey': 'nj',
                    'nm': 'new mexico', 'new mexico': 'nm',
                    'ny': 'new york', 'new york': 'ny',
                    'nc': 'north carolina', 'north carolina': 'nc',
                    'nd': 'north dakota', 'north dakota': 'nd',
                    'oh': 'ohio', 'ohio': 'oh',
                    'ok': 'oklahoma', 'oklahoma': 'ok',
                    'or': 'oregon', 'oregon': 'or',
                    'pa': 'pennsylvania', 'pennsylvania': 'pa',
                    'ri': 'rhode island', 'rhode island': 'ri',
                    'sc': 'south carolina', 'south carolina': 'sc',
                    'sd': 'south dakota', 'south dakota': 'sd',
                    'tn': 'tennessee', 'tennessee': 'tn',
                    'tx': 'texas', 'texas': 'tx',
                    'ut': 'utah', 'utah': 'ut',
                    'vt': 'vermont', 'vermont': 'vt',
                    'va': 'virginia', 'virginia': 'va',
                    'wa': 'washington', 'washington': 'wa',
                    'wv': 'west virginia', 'west virginia': 'wv',
                    'wi': 'wisconsin', 'wisconsin': 'wi',
                    'wy': 'wyoming', 'wyoming': 'wy',
                    'dc': 'district of columbia', 'district of columbia': 'dc'
                };
                
                // STRICT: Check if job is clearly remote (exclude these)
                const isRemote = jobLocation.includes('remote') || 
                               jobTitle.includes('remote') ||
                               jobLocation.includes('work from home') ||
                               jobTitle.includes('work from home') ||
                               jobLocation.includes('wfh') ||
                               jobLocation === 'us' ||
                               jobLocation.startsWith('us,') ||
                               jobLocation.includes('international') ||
                               jobLocation.includes('anywhere');
                
                if (isRemote) {
                    matchesLocation = false;
                } else {
                    // STRICT matching: Must match city OR state (not just any word)
                    let cityMatch = false;
                    let stateMatch = false;
                    
                    if (userCity) {
                        // City must be a complete word match (not just substring)
                        // Check if city appears as a standalone word or at start of location
                        const cityRegex = new RegExp(`\\b${userCity.replace(/\s+/g, '\\s+')}\\b`, 'i');
                        cityMatch = cityRegex.test(jobLocation) || 
                                   jobLocation.startsWith(userCity) ||
                                   jobLocation.includes(`, ${userCity}`) ||
                                   jobLocation.includes(`${userCity},`);
                        
                        // If city doesn't match directly, check if job location has a different state
                        // If job explicitly mentions a different state, don't match by city alone
                        if (!cityMatch && userState && userCity.length > 3) {
                            // Get all state abbreviations and names from stateMap (excluding user's state)
                            const allStates = [];
                            const userStateAbbr = stateMap[userState] || userState;
                            const userStateFull = Object.keys(stateMap).find(k => stateMap[k] === userState) || userState;
                            
                            for (const [abbr, full] of Object.entries(stateMap)) {
                                // Skip user's state
                                if (abbr !== userState && abbr !== userStateAbbr && 
                                    full !== userState && full !== userStateFull) {
                                    // Add both abbreviation and full name
                                    if (abbr.length === 2) allStates.push(abbr);
                                    if (full && full !== abbr) allStates.push(full);
                                }
                            }
                            
                            // Check if job location mentions a different state
                            let hasOtherState = false;
                            if (allStates.length > 0) {
                                // Escape states for regex
                                const escapedStates = allStates.map(s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
                                const otherStatePattern = new RegExp(`\\b(${escapedStates.join('|')})\\b`, 'i');
                                hasOtherState = otherStatePattern.test(jobLocation);
                            }
                            
                            // If no other state is mentioned and city name appears, match it
                            // This handles cases like "Birmingham, Jefferson County" when user is in AL
                            // But only if the city name appears at the start or after a comma (not in the middle of another word)
                            if (!hasOtherState) {
                                // Check if the city name appears at the start or after a comma
                                const cityInLocation = new RegExp(`(^|,\\s*)${userCity.replace(/\s+/g, '\\s*')}\\b`, 'i');
                                if (cityInLocation.test(jobLocation)) {
                                    cityMatch = true;
                                }
                            }
                        }
                    }
                    
                    if (userState) {
                        // State must match exactly (abbreviation or full name)
                        // Get both abbreviation and full name
                        let stateAbbr = userState;
                        let stateFull = userState;
                        
                        // If user entered abbreviation, get full name
                        if (stateMap[userState]) {
                            stateFull = stateMap[userState];
                        }
                        // If user entered full name, get abbreviation
                        else {
                            const foundKey = Object.keys(stateMap).find(k => stateMap[k] === userState);
                            if (foundKey) {
                                stateAbbr = foundKey;
                            }
                        }
                        
                        // Check for state abbreviation or full name
                        // Escape special regex characters
                        const escapeRegex = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                        const stateAbbrEscaped = escapeRegex(stateAbbr);
                        const stateFullEscaped = escapeRegex(stateFull);
                        
                        // Match state as word boundary or at end of location
                        const statePattern = `\\b(${stateAbbrEscaped}|${stateFullEscaped})\\b`;
                        const stateRegex = new RegExp(statePattern, 'i');
                        
                        // Use regex for strict word boundary matching to avoid false matches
                        // e.g., "al" should NOT match "alameda"
                        stateMatch = stateRegex.test(jobLocation);
                        
                        // Also check for explicit state patterns at end of location string
                        if (!stateMatch) {
                            // Check if state appears after a comma (most common format)
                            const stateAfterComma = new RegExp(`,\\s*(${stateAbbrEscaped}|${stateFullEscaped})(?:\\s|,|$)`, 'i');
                            stateMatch = stateAfterComma.test(jobLocation);
                        }
                        
                        // Final check: state at the very end
                        if (!stateMatch) {
                            const stateAtEnd = new RegExp(`(?:^|\\s)(${stateAbbrEscaped}|${stateFullEscaped})$`, 'i');
                            stateMatch = stateAtEnd.test(jobLocation);
                        }
                    }
                    
                    // Must match at least city OR state (strict)
                    matchesLocation = cityMatch || stateMatch;
                }
            }
        } else if (locationFilter === 'remote') {
            const jobLocation = (job.location || '').toLowerCase();
            const jobTitle = (job.title || '').toLowerCase();
            matchesLocation = jobLocation.includes('remote') ||
                             jobTitle.includes('remote') ||
                             jobLocation.includes('work from home') ||
                             jobTitle.includes('work from home') ||
                             jobLocation.includes('wfh');
        }
        
        // Mentor filter
        const hasMentor = jobsWithMentors.has(`${job.title}_${job.company}`.replace(/[^a-zA-Z0-9]/g, '_'));
        const matchesMentor = !mentorFilter || hasMentor;
        
        return matchesSearch && matchesScore && matchesLocation && matchesMentor;
    });
    
    // Sort jobs
    filtered.sort((a, b) => {
        switch(sortFilter) {
            case 'score-desc':
                return (b.match_score || 0) - (a.match_score || 0);
            case 'score-asc':
                return (a.match_score || 0) - (b.match_score || 0);
            case 'title-asc':
                return (a.title || '').localeCompare(b.title || '');
            case 'company-asc':
                return (a.company || '').localeCompare(b.company || '');
            case 'location-asc':
                return (a.location || '').localeCompare(b.location || '');
            default:
                return 0;
        }
    });
    
    // Display filtered jobs
    if (filtered.length === 0) {
        jobsList.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <h3>No jobs match your filters</h3>
                <p>Try adjusting your search criteria</p>
            </div>
        `;
        return;
    }
    
    // Update filter summary
    updateFilterSummary(filtered.length, currentJobs.length, jobsWithMentors.size);
    
    jobsList.innerHTML = filtered.map(job => createJobCard(job)).join('');
    
    // Load mentor connections for each job
    filtered.forEach(job => {
        const jobId = `${job.title}_${job.company}`.replace(/[^a-zA-Z0-9]/g, '_');
        if (job.company) {
            loadMentorConnections(jobId, job.company);
        }
    });
}

function updateFilterSummary(filteredCount, totalCount, mentorsCount) {
    const summary = document.getElementById('filterSummary');
    if (!summary) return;
    
    const mentorText = mentorsCount > 0 ? ` | ${mentorsCount} with mentor connections` : '';
    summary.textContent = `Showing ${filteredCount} of ${totalCount} jobs${mentorText}`;
    summary.style.display = filteredCount < totalCount ? 'block' : 'none';
}

function createJobCard(job) {
    const score = job.match_score || 0;
    const scoreClass = score >= 50 ? 'high' : score >= 30 ? 'medium' : '';
    const jobId = `${job.title}_${job.company}`.replace(/[^a-zA-Z0-9]/g, '_');
    const isBookmarked = bookmarkedJobs.has(jobId);
    
    const salary = job.salary_min && job.salary_max 
        ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`
        : job.salary_min 
        ? `$${job.salary_min.toLocaleString()}+`
        : '';
    
    return `
        <div class="job-card" data-job-id="${jobId}">
            <div class="job-header">
                <div class="job-title">${escapeHtml(job.title || 'N/A')}</div>
                <div class="match-score ${scoreClass}">${score.toFixed(1)}% Match</div>
            </div>
            <div class="job-details">
                <div class="job-detail-item">
                    <strong>🏢 Company:</strong> ${escapeHtml(job.company || 'N/A')}
                </div>
                <div class="job-detail-item">
                    <strong>📍 Location:</strong> ${escapeHtml(job.location || 'N/A')}
                </div>
                ${salary ? `<div class="job-detail-item"><strong>💰 Salary:</strong> ${salary}</div>` : ''}
                <div class="job-detail-item">
                    <strong>📅 Source:</strong> ${escapeHtml(job.source || 'N/A')}
                </div>
            </div>
            ${job.description ? `<div class="job-description">${escapeHtml(job.description.substring(0, 300))}${job.description.length > 300 ? '...' : ''}</div>` : ''}
            <div class="mentor-connections" id="mentors-${jobId}">
                <div class="mentor-loading">🔍 Checking mentor connections...</div>
            </div>
            <div class="job-footer">
                <button class="btn-bookmark ${isBookmarked ? 'bookmarked' : ''}" 
                        onclick="toggleBookmark('${jobId}')"
                        data-job='${JSON.stringify(job).replace(/'/g, "&#39;")}'
                        title="${isBookmarked ? 'Remove bookmark' : 'Save job'}">
                    ${isBookmarked ? '⭐ Saved' : '☆ Save'}
                </button>
                ${job.url ? `<a href="${job.url}" target="_blank" class="job-link">🔗 View Job →</a>` : ''}
            </div>
        </div>
    `;
}

// Load mentor connections for a job (with error handling and debouncing)
const mentorConnectionCache = {};
const mentorConnectionQueue = new Set();

async function loadMentorConnections(jobId, company) {
    if (!company || !company.trim()) {
        const container = document.getElementById(`mentors-${jobId}`);
        if (container) container.innerHTML = '';
        return;
    }
    
    const container = document.getElementById(`mentors-${jobId}`);
    if (!container) return;
    
    // Check cache first
    const cacheKey = company.toLowerCase().trim();
    if (mentorConnectionCache[cacheKey] !== undefined) {
        displayMentorConnections(container, company, mentorConnectionCache[cacheKey]);
        return;
    }
    
    // Debounce: don't make multiple requests for the same company
    if (mentorConnectionQueue.has(cacheKey)) {
        return;
    }
    
    mentorConnectionQueue.add(cacheKey);
    
    try {
        const encodedCompany = encodeURIComponent(company.trim());
        const response = await fetch(`/api/mentors/company/${encodedCompany}`);
        
        if (!response.ok) {
            // If error, just hide the section silently
            container.innerHTML = '';
            mentorConnectionCache[cacheKey] = { mentors: [], count: 0 };
            return;
        }
        
        const data = await response.json();
        
        // Cache the result
        mentorConnectionCache[cacheKey] = data;
        
        // Display results
        displayMentorConnections(container, company, data);
        
    } catch (error) {
        // Log error for debugging but don't show to user
        console.log(`Mentor lookup failed for ${company}:`, error);
        container.innerHTML = '';
        mentorConnectionCache[cacheKey] = { mentors: [], count: 0 };
    } finally {
        mentorConnectionQueue.delete(cacheKey);
    }
}

function displayMentorConnections(container, company, data) {
    if (!container) {
        console.log('displayMentorConnections: container is null');
        return;
    }
    
    if (data && data.mentors && data.mentors.length > 0) {
        // Mark this job as having mentors
        const jobCard = container.closest('.job-card');
        if (jobCard) {
            const jobId = jobCard.getAttribute('data-job-id');
            if (jobId) {
                jobsWithMentors.add(jobId);
                // Add visual indicator
                jobCard.classList.add('has-mentor-connection');
            }
        }
        
        container.innerHTML = `
            <div class="mentor-connections-header">
                <strong>🤝 ${data.count} Mentor${data.count > 1 ? 's' : ''} at ${escapeHtml(company)}:</strong>
            </div>
            <div class="mentor-list">
                ${data.mentors.map(mentor => `
                    <div class="mentor-item">
                        <strong>${escapeHtml(mentor.name || mentor.full_name || 'N/A')}</strong> - ${escapeHtml(mentor.title || 'N/A')}
                        ${mentor.linkedin ? `<a href="${mentor.linkedin}" target="_blank" class="mentor-link">LinkedIn →</a>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        // No mentors found - hide the section
        container.innerHTML = '';
    }
}

// Bookmark functions
async function toggleBookmark(jobId) {
    const isBookmarked = bookmarkedJobs.has(jobId);
    const button = document.querySelector(`[data-job-id="${jobId}"] .btn-bookmark`);
    const jobData = button ? JSON.parse(button.getAttribute('data-job').replace(/&#39;/g, "'")) : null;
    
    if (!jobData) {
        console.error('Could not find job data');
        return;
    }
    
    try {
        if (isBookmarked) {
            // Remove bookmark
            const response = await fetch('/api/bookmarks', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: jobId })
            });
            
            if (response.ok) {
                bookmarkedJobs.delete(jobId);
                updateBookmarkButton(jobId, false);
                loadBookmarks(); // Refresh bookmarks list
            }
        } else {
            // Add bookmark
            const response = await fetch('/api/bookmarks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: jobId, job_data: jobData })
            });
            
            if (response.ok) {
                bookmarkedJobs.add(jobId);
                updateBookmarkButton(jobId, true);
                loadBookmarks(); // Refresh bookmarks list
            }
        }
    } catch (error) {
        console.error('Error toggling bookmark:', error);
        alert('Error saving bookmark');
    }
}

function updateBookmarkButton(jobId, isBookmarked) {
    const button = document.querySelector(`[data-job-id="${jobId}"] .btn-bookmark`);
    if (button) {
        button.className = `btn-bookmark ${isBookmarked ? 'bookmarked' : ''}`;
        button.textContent = isBookmarked ? '⭐ Saved' : '☆ Save';
        button.title = isBookmarked ? 'Remove bookmark' : 'Save job';
    }
}

async function loadBookmarks() {
    try {
        const response = await fetch('/api/bookmarks');
        const data = await response.json();
        
        bookmarkedJobs = new Set(data.bookmarks.map(b => b.job_id));
        
        // Show bookmarks card if there are bookmarks
        const bookmarksCard = document.getElementById('bookmarksCard');
        const bookmarksList = document.getElementById('bookmarksList');
        
        if (data.bookmarks && data.bookmarks.length > 0) {
            bookmarksCard.style.display = 'block';
            bookmarksList.innerHTML = data.bookmarks.map(bookmark => {
                const job = bookmark.job_data;
                return createJobCard(job);
            }).join('');
        } else {
            bookmarksCard.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading bookmarks:', error);
    }
}

// Recent searches functions
function saveRecentSearch(searchData) {
    let recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    
    // Add new search
    recentSearches.unshift(searchData);
    
    // Keep only last 5
    recentSearches = recentSearches.slice(0, 5);
    
    localStorage.setItem('recentSearches', JSON.stringify(recentSearches));
    displayRecentSearches();
}

function loadRecentSearches() {
    displayRecentSearches();
}

function displayRecentSearches() {
    const recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    const card = document.getElementById('recentSearchesCard');
    const list = document.getElementById('recentSearchesList');
    
    if (recentSearches.length > 0) {
        card.style.display = 'block';
        list.innerHTML = recentSearches.map((search, idx) => {
            const skillsStr = search.skills.join(', ');
            const interestsStr = search.interests && search.interests.length > 0 ? search.interests.join(', ') : 'None';
            return `
                <div class="recent-search-item" onclick="loadRecentSearch(${idx})">
                    <div class="recent-search-skills"><strong>Skills:</strong> ${escapeHtml(skillsStr)}</div>
                    <div class="recent-search-meta">
                        <span>📍 ${escapeHtml(search.location || 'US-wide')}</span>
                        <span>${new Date(search.timestamp).toLocaleDateString()}</span>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        card.style.display = 'none';
    }
}

function loadRecentSearch(index) {
    const recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    if (recentSearches[index]) {
        const search = recentSearches[index];
        document.getElementById('skills').value = search.skills.join(', ');
        document.getElementById('interests').value = (search.interests || []).join(', ');
        document.getElementById('location').value = search.location || '';
        document.getElementById('us_wide').checked = search.us_wide !== false;
        
        // Trigger search
        document.getElementById('searchForm').dispatchEvent(new Event('submit', { cancelable: true }));
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Resume upload functions
async function handleResumeUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const fileName = document.getElementById('resumeFileName');
    const clearBtn = document.getElementById('clearResume');
    const skillsInput = document.getElementById('skills');
    const locationInput = document.getElementById('location');
    
    // Show file name
    fileName.textContent = file.name;
    clearBtn.style.display = 'inline-block';
    
    // Show loading
    fileName.textContent = `Uploading ${file.name}...`;
    
    try {
        const formData = new FormData();
        formData.append('resume', file);
        
        const response = await fetch('/api/upload-resume', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Auto-fill skills and location
        if (data.skills && data.skills.length > 0) {
            skillsInput.value = data.skills.join(', ');
        }
        
        if (data.location) {
            locationInput.value = data.location;
        }
        
        fileName.textContent = `✓ ${file.name} - Skills extracted!`;
        fileName.style.color = '#11998e';
        
    } catch (error) {
        console.error('Resume upload error:', error);
        fileName.textContent = `Error: ${error.message}`;
        fileName.style.color = '#f5576c';
    }
}

function clearResumeData() {
    const resumeUpload = document.getElementById('resumeUpload');
    const fileName = document.getElementById('resumeFileName');
    const clearBtn = document.getElementById('clearResume');
    
    resumeUpload.value = '';
    fileName.textContent = '';
    fileName.style.color = '';
    clearBtn.style.display = 'none';
}

