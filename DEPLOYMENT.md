# Deployment Guide

## Quick Start for GitHub + Render Deployment

### 1. Create GitHub Repository

**Option A: Using GitHub Web Interface**
1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Name: `shopping-assistant-api`
4. Make it public or private (your choice)
5. Don't initialize with README (we already have one)
6. Click "Create repository"

**Option B: Using GitHub CLI (if installed)**
```bash
gh repo create shopping-assistant-api --public
```

### 2. Push Code to GitHub

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Shopping Assistant API ready for deployment"

# Add your GitHub repository as origin
git remote add origin https://github.com/YOUR_USERNAME/shopping-assistant-api.git

# Push to GitHub
git push -u origin main
```

### 3. Deploy on Render

1. **Sign up/Login to Render**
   - Go to [render.com](https://render.com)
   - Sign up or login (can use GitHub account)

2. **Create Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub account
   - Select the `shopping-assistant-api` repository

3. **Configure Service**
   - **Name**: `shopping-assistant-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT shopping_api:app`

4. **Environment Variables**
   - Click "Advanced" 
   - Add environment variable:
     - **Key**: `GEMINI_API_KEY`
     - **Value**: Your Google Gemini API key (get from Google AI Studio)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (usually 2-5 minutes)

### 4. Test Your Deployment

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-app-name.onrender.com/api/health

# Create session (should return session_id)
curl -X POST https://your-app-name.onrender.com/api/session \
  -H "Content-Type: application/json" \
  -d '{"user_query": "I want shoes"}'
```

### 5. Get Your Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to Render environment variables

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check if all requirements are in `requirements.txt`
   - Ensure Python version compatibility

2. **App Crashes on Start**
   - Check if `GEMINI_API_KEY` environment variable is set
   - Verify the start command: `gunicorn --bind 0.0.0.0:$PORT shopping_api:app`

3. **API Key Issues**
   - Ensure your Gemini API key is valid
   - Check if there are any usage limits on your API key

### Logs

- View logs in Render dashboard under "Logs" tab
- Look for startup errors or API connection issues

## Alternative Deployment Options

If you prefer other platforms:

- **Heroku**: Use the included `Procfile`
- **Railway**: Connect GitHub repo directly
- **Vercel**: For serverless deployment (may need modifications)
- **DigitalOcean App Platform**: Similar to Render setup

## Production Considerations

1. **API Key Security**: Never commit API keys to code
2. **Rate Limiting**: Consider implementing API rate limiting
3. **Monitoring**: Set up health checks and monitoring
4. **Scaling**: Configure auto-scaling based on traffic
5. **Domain**: Consider adding a custom domain
6. **HTTPS**: Render provides SSL certificates automatically

## Cost Estimation

- **Render Free Tier**: Good for testing and low traffic
- **Render Starter**: $7/month for production apps
- **Google Gemini API**: Pay-per-use (check current pricing) 