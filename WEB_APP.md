# Job Cross-Reference Web App

A beautiful web interface for searching and viewing job matches based on your mentor network.

## Features

- 🎨 Modern, responsive UI
- 🔍 Real-time job search
- 📊 Interactive results with filtering and sorting
- 🎯 Match score visualization
- 📥 Download CSV and HTML reports
- 📱 Mobile-friendly design

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the web server:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   Navigate to: http://localhost:5001
   
   (Note: Using port 5001 to avoid conflict with macOS AirPlay Receiver on port 5000)

## Usage

1. **Enter your skills** (comma-separated):
   - Example: `Python, JavaScript, React, Full-Stack Development`

2. **Enter your interests** (optional):
   - Example: `AI, Machine Learning, Product Management`

3. **Enter your location** (optional):
   - Example: `Huntsville, AL`
   - Leave empty for US-wide only

4. **Click "Search Jobs"** and wait for results!

5. **Filter and sort** results:
   - Search by title/company
   - Sort by match score, title, company, or location
   - Filter by minimum match score

6. **Download reports**:
   - CSV for spreadsheet analysis
   - HTML for visual review

## API Endpoints

- `GET /` - Main web interface
- `POST /api/search` - Search for jobs
- `GET /api/mentors` - Get mentor statistics
- `GET /api/reports/<filename>` - Download report files

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Styling:** Modern CSS with gradients and animations
- **Job API:** Adzuna

Enjoy your new job search app! 🚀

