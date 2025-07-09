# URL Scanner - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Start the Backend Server
```bash
cd url-scanner-backend
source venv/bin/activate
python src/main.py
```
✅ Backend will run on `http://localhost:5001`

### Step 2: Start the Frontend
```bash
cd url-scanner-frontend
pnpm run dev --host
```
✅ Frontend will run on `http://localhost:5173`

### Step 3: Get Your API Key

**Option A: Use the Test API Key**
```
API Key: fDJPu9jIRWTfaOZc072QCsfHuRzYrURR
```

**Option B: Create Your Own Client**
```bash
cd url-scanner-backend
source venv/bin/activate
python /home/ubuntu/create_test_client.py
```

### Step 4: Analyze a Website

1. Open `http://localhost:5173` in your browser
2. Enter your API key and click "Continue"
3. Enter a URL (e.g., `https://www.google.com`)
4. Click "Analyze" and watch the magic happen! ✨

## 🎯 What You'll Get

- **Technical Score**: HTTP status, SSL, robots.txt
- **Performance Score**: Core Web Vitals (LCP, FID, CLS)
- **SEO Score**: Meta tags, headings, content structure
- **Mobile Score**: Responsive design, touch targets

## 🔧 API Testing

Test the API directly:
```bash
# Check system health
curl http://localhost:5001/health

# Check analysis engines
curl http://localhost:5001/api/engines/status

# Analyze a URL
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer fDJPu9jIRWTfaOZc072QCsfHuRzYrURR" \
  -d '{"url": "https://example.com"}' \
  http://localhost:5001/api/analyze/url
```

## 🎨 Features to Explore

- **Engine Selection**: Toggle different analysis engines
- **Real-time Progress**: Watch analysis progress in real-time
- **Detailed Results**: Explore tabbed results for each engine
- **Priority Recommendations**: Get actionable insights
- **Responsive Design**: Works perfectly on mobile and desktop

## 🚨 Troubleshooting

**Port Already in Use?**
- Backend: Change port in `src/main.py` (line 56)
- Frontend: Change port with `pnpm run dev --port 3000`

**API Connection Issues?**
- Ensure backend is running on port 5001
- Check `src/App.jsx` line 24 for correct API URL

**Database Issues?**
- Delete `src/database/app.db` to reset database
- Restart backend to recreate tables

## 📁 Project Structure

```
url-scanner-backend/          # Flask API server
├── src/
│   ├── engines/             # Analysis engines
│   ├── models/              # Database models
│   ├── routes/              # API endpoints
│   └── main.py              # Application entry point
└── venv/                    # Python virtual environment

url-scanner-frontend/         # React web interface
├── src/
│   ├── components/ui/       # UI components
│   └── App.jsx              # Main application
└── package.json             # Dependencies
```

## 🎉 You're Ready!

The URL Scanner is now running and ready to analyze websites for Google Search Console best practices. Enjoy exploring the comprehensive analysis capabilities!

For detailed documentation, see `URL_Scanner_Documentation.md`.

