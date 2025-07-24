# Smart Shopping Assistant

A Python-based shopping assistant that uses Google's Gemini AI to ask intelligent follow-up questions and generate shopping summaries.

## Features

- 🤖 AI-powered follow-up questions using Gemini API
- 🛍️ Product-specific question generation (especially for shoes)
- 📋 Comprehensive shopping summaries
- 💬 Interactive terminal interface
- 🔄 Multiple search sessions

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the shopping assistant:**
   ```bash
   python shopping_assistant.py
   ```

## How to Use

1. **Start the assistant** - Run the Python script
2. **Enter your search query** - e.g., "I want shoes", "I need a laptop"
3. **Answer follow-up questions** - The AI will ask relevant questions like:
   - Price range
   - Color preferences
   - Gender (male/female/unisex)
   - Size requirements
   - Brand preferences
   - And more...
4. **Get your summary** - Receive a comprehensive shopping summary
5. **Search again** - Option to start a new search

## Example Usage

```
🛍️  Welcome to the Smart Shopping Assistant!
==================================================
What are you looking for today? (e.g., 'I want shoes', 'I need a laptop'): I want shoes

🔍 Analyzing your search for: I want shoes
Generating personalized follow-up questions...

📝 Please answer the following questions (press Enter to skip any question):

1. What's your budget range?
   Your answer: $50-100

2. What type of shoes are you looking for?
   Your answer: Sneakers

3. What color do you prefer?
   Your answer: Black

4. Are you looking for male, female, or unisex items?
   Your answer: Male

5. What size do you need?
   Your answer: 10

📋 Generating your shopping summary...

==================================================
SHOPPING SUMMARY
==================================================
[AI-generated summary will appear here]
==================================================
```

## Supported Product Types

The assistant is optimized for various product categories, with special focus on:
- 👟 Shoes (sneakers, formal, casual, sports)
- 👕 Clothing
- 💻 Electronics
- 🏠 Home & Garden
- 🎮 Gaming
- And more!

## Requirements

- Python 3.7+
- Internet connection (for Gemini API)
- Google Generative AI package

## API Key

The script includes a pre-configured Gemini API key for development. For production use, set the `GEMINI_API_KEY` environment variable for security.

## Deployment on Render

This application is ready for deployment on Render. Follow these steps:

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository
2. Clone this code to your local machine
3. Initialize git and push to your new repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/shopping-assistant-api.git
   git push -u origin main
   ```

### 2. Deploy to Render

1. Go to [Render](https://render.com) and sign up/login
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT shopping_api:app`
5. Add environment variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: Your Google Gemini API key
6. Click "Create Web Service"

### 3. API Endpoints

Once deployed, your API will be available at `https://your-app-name.onrender.com` with the following endpoints:

- `GET /api/health` - Health check
- `POST /api/session` - Create a new session
- `POST /api/questions` - Get follow-up questions
- `POST /api/answer` - Submit an answer
- `POST /api/summary` - Get shopping summary
- `GET /api/session/<session_id>` - Get session data

### 4. Environment Variables

Required environment variables for production:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: Automatically set by Render

## Local Development vs Production

### Local Development
```bash
python shopping_assistant.py  # Terminal interface
python shopping_api.py        # API server
```

### Production
The application runs as a Flask API server using Gunicorn for better performance and reliability.

## Error Handling

The assistant includes robust error handling for:
- Network connectivity issues
- API rate limits
- Invalid user inputs
- Graceful exit with Ctrl+C
- Production-level error logging 