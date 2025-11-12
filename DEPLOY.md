# 🚀 How to Deploy & Share Your Job Search App

## Quick Options to Share with Friends

### Option 1: Local Network (Same WiFi) - Easiest!

**Steps:**
1. Make sure you and your friend are on the same WiFi network
2. Start the app:
   ```bash
   python3 app.py
   ```
3. Find your local IP address:
   - Mac: System Preferences → Network (or run `ifconfig | grep "inet "`)
   - Look for something like `192.168.1.xxx`
4. Share this URL with your friend:
   ```
   http://YOUR_IP_ADDRESS:5001
   ```
   Example: `http://192.168.1.100:5001`

**Pros:** Free, instant, no setup  
**Cons:** Only works on same network

---

### Option 2: Railway.app (Recommended - Free & Easy)

Railway is perfect for quick deployments:

1. **Sign up:** Go to [railway.app](https://railway.app) and sign up with GitHub
2. **Create project:** Click "New Project" → "Deploy from GitHub repo"
3. **Select repo:** Choose `GitBenTank/Job-Search`
4. **Add environment variables:**
   - Go to Variables tab
   - Add your Adzuna API keys (if you have them):
     ```
     ADZUNA_APP_ID=your_app_id
     ADZUNA_APP_KEY=your_app_key
     ```
5. **Deploy:** Railway auto-detects Flask and deploys
6. **Get URL:** You'll get a public URL like `https://your-app.railway.app`

**Pros:** Free tier, permanent URL, easy setup  
**Cons:** Requires API keys for full functionality

---

### Option 3: Render.com (Free)

Similar to Railway:

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. New → Web Service
4. Connect your `Job-Search` repo
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 app.py`
   - Environment: Python 3
6. Add environment variables for API keys
7. Deploy and get public URL

**Pros:** Free tier, reliable  
**Cons:** Slightly more setup

---

### Option 4: ngrok (Temporary Public URL)

Creates a temporary tunnel to your local server:

1. **Install ngrok:**
   ```bash
   brew install ngrok
   # OR download from ngrok.com
   ```

2. **Start your app** (in one terminal):
   ```bash
   python3 app.py
   ```

3. **Start ngrok** (in another terminal):
   ```bash
   ngrok http 5001
   ```

4. **Share the ngrok URL:**
   - You'll see something like: `https://abc123.ngrok.io`
   - This URL works from anywhere (not just same WiFi)
   - **Note:** URL expires when you close ngrok

**Pros:** Works from anywhere, instant  
**Cons:** Temporary URL, requires keeping your computer on

---

## What Your Friend Needs

**Nothing!** They just need:
- A web browser (Chrome, Safari, Firefox, etc.)
- The URL you share with them
- That's it! No code editor, no installation, nothing.

---

## Recommended Setup for Sharing

For the easiest experience, I recommend **Railway.app**:
- ✅ Free forever
- ✅ Permanent URL
- ✅ Easy to set up (5 minutes)
- ✅ Auto-deploys when you push to GitHub
- ✅ Professional looking URL

---

## Quick Start with Railway

```bash
# 1. Make sure your code is pushed to GitHub
git push origin master

# 2. Go to railway.app and sign up
# 3. Click "New Project" → "Deploy from GitHub repo"
# 4. Select Job-Search
# 5. Add environment variables (optional - for API keys)
# 6. Wait 2 minutes for deployment
# 7. Share the URL!
```

That's it! Your friend can now use your app from anywhere. 🎉

