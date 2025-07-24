from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import requests
import os
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

# Configure Gemini API and YouTube Data API
API_KEY = os.getenv('GEMINI_API_KEY', "AIzaSyAQ-V9IvNDDegtQ2yhGUDQy7uF0zq1ajsM")
genai.configure(api_key=API_KEY)

class ShoppingAssistantAPI:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.youtube_api_key = API_KEY
        self.youtube_base_url = "https://www.googleapis.com/youtube/v3"
        self.sessions = {}  # Store session data
    
    def create_session(self, session_id: str):
        """Create a new session"""
        self.sessions[session_id] = {
            'user_query': '',
            'follow_up_questions': [],
            'answers': {},
            'summary': '',
            'step': 'initial'
        }
    
    def get_follow_up_questions(self, user_query: str) -> List[str]:
        """Generate follow-up questions based on the user's initial query"""
        
        prompt = f"""
        You are an intelligent shopping assistant. The user has searched for: "{user_query}"
        
        Analyze the product type and generate EXACTLY 5 highly relevant, specific follow-up questions that would help narrow down their search.
        
        IMPORTANT: Make questions specific to the product type mentioned. For example:
        - For clothing: fabric type, occasion, season, fit preference, etc.
        - For electronics: specifications, brand preference, usage purpose, etc.
        - For shoes: type, size system, comfort level, activity, etc.
        - For jewelry: metal type, stone preference, occasion, etc.
        
        Focus on the 5 most important aspects:
        - Budget range, always remember the price i will give is in indian rupees.
        - Specific preferences (color, style, material, etc.)
        - Size/dimensions
        - Brand preferences
        - Usage/occasion
        
        CRITICAL: You must respond with ONLY a valid JSON array of EXACTLY 5 question strings.
        Do not include any other text, explanations, or formatting.
        
        Example response:
        ["What's your budget range?", "What specific style are you looking for?", "Do you have any brand preferences?", "What size do you need?", "What's the primary use/occasion?"]
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from the response
            if response_text.startswith('[') and response_text.endswith(']'):
                questions = json.loads(response_text)
            else:
                # If the response isn't pure JSON, try to extract it
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    questions = json.loads(json_match.group())
                else:
                    # If no JSON found, split by lines and clean up
                    lines = response_text.split('\n')
                    questions = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('-'):
                            # Remove numbering if present
                            line = re.sub(r'^\d+\.\s*', '', line)
                            if line:
                                questions.append(line)
                    
                    if not questions:
                        raise Exception("Could not parse questions from response")
            
            return questions
        except Exception as e:
            print(f"Error generating questions: {e}")
            print("Using fallback questions...")
            # Fallback questions (exactly 5)
            return [
                "What's your budget range?",
                "What color do you prefer?",
                "Are you looking for male, female, or unisex items?",
                "What size do you need?",
                "Do you have any brand preferences?"
            ]
    
    def search_youtube_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search YouTube videos using the YouTube Data API v3"""
        
        url = f"{self.youtube_base_url}/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': max_results,
            'key': self.youtube_api_key,
            'order': 'relevance'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            if 'items' in data:
                for item in data['items']:
                    video_info = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel_title': item['snippet']['channelTitle'],
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    }
                    videos.append(video_info)
            
            return videos
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching YouTube: {e}")
            return []
    
    def generate_summary(self, user_query: str, answers: Dict[str, str]) -> str:
        """Generate a summary of the user's requirements"""
        
        answers_text = "\n".join([f"- {question}: {answer}" for question, answer in answers.items()])
        
        prompt = f"""
        Based on the following information, create a concise shopping summary:
        
        Original Query: {user_query}
        
        User's Answers:
        {answers_text}
        
        Create a well-formatted summary that includes:
        1. Product category/type
        2. Key specifications
        3. Preferences
        4. Budget considerations
        
        Format it nicely for console output with clear sections.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"""
Shopping Summary:
===============
Original Query: {user_query}

Requirements:
{answers_text}

This summary can be used to search for products that match your criteria.
"""
    
    def search_product_recommendations(self, user_query: str, summary: str) -> str:
        """Search for product recommendations using YouTube Data API"""
        
        # Let Gemini create the search query based on the summary
        search_prompt = f"""
        Based on this shopping summary, create a natural YouTube search query that a human would type.
        
        Original Query: {user_query}
        Shopping Summary: {summary}
        
        Create a simple, natural search query like how people actually search on YouTube.
        Include the product and budget if mentioned, but keep it conversational and natural.
        
        Examples of good queries:
        - "laptop under 1 lakh"
        - "best gaming laptop"
        - "iPhone 15 review"
        - "shoes for running"
        
        Return ONLY the search query in one line, nothing else.
        """
        
        try:
            response = self.model.generate_content(search_prompt)
            search_query = response.text.strip()
        except Exception as e:
            print(f"Error generating search query: {e}")
            search_query = f"{user_query} review unboxing"
        
        # Search for videos
        videos = self.search_youtube_videos(search_query, max_results=10)
        
        if not videos:
            return "No videos found for your search query."
        
        # Format the results
        result = "🎥 YouTube Video Recommendations:\n"
        result += "=" * 50 + "\n\n"
        
        for i, video in enumerate(videos, 1):
            result += f"{i}. 📺 {video['title']}\n"
            result += f"   👤 Channel: {video['channel_title']}\n"
            result += f"   📅 Published: {video['published_at'][:10]}\n"
            result += f"   🔗 URL: {video['url']}\n"
            result += f"   📝 Description: {video['description']}\n"
            result += "\n" + "-" * 40 + "\n\n"
        
        return result

# Initialize the assistant
assistant = ShoppingAssistantAPI()

@app.route('/api/start', methods=['POST'])
def start_session():
    """Start a new shopping session with initial query"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Create session
        assistant.create_session(session_id)
        assistant.sessions[session_id]['user_query'] = user_query
        
        # Generate follow-up questions
        questions = assistant.get_follow_up_questions(user_query)
        assistant.sessions[session_id]['follow_up_questions'] = questions
        assistant.sessions[session_id]['step'] = 'questions'
        
        return jsonify({
            'session_id': session_id,
            'user_query': user_query,
            'follow_up_questions': questions,
            'message': 'Session started successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/answer', methods=['POST'])
def submit_answer():
    """Submit answer to a follow-up question"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')
        question_index = data.get('question_index')  # 0-based index
        answer = data.get('answer', '').strip()
        
        if session_id not in assistant.sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        if question_index is None:
            return jsonify({'error': 'Question index is required'}), 400
        
        session = assistant.sessions[session_id]
        
        if question_index >= len(session['follow_up_questions']):
            return jsonify({'error': 'Invalid question index'}), 400
        
        # Store the answer
        question = session['follow_up_questions'][question_index]
        session['answers'][question] = answer
        
        # Check if all questions are answered
        if len(session['answers']) == len(session['follow_up_questions']):
            # Generate summary and recommendations
            summary = assistant.generate_summary(session['user_query'], session['answers'])
            recommendations = assistant.search_product_recommendations(session['user_query'], summary)
            
            session['summary'] = summary
            session['step'] = 'complete'
            
            return jsonify({
                'session_id': session_id,
                'step': 'complete',
                'summary': summary,
                'recommendations': recommendations,
                'message': 'All questions answered. Here are your results!'
            })
        else:
            # Return next question info
            next_question_index = len(session['answers'])
            next_question = session['follow_up_questions'][next_question_index]
            
            return jsonify({
                'session_id': session_id,
                'step': 'questions',
                'next_question_index': next_question_index,
                'next_question': next_question,
                'questions_answered': len(session['answers']),
                'total_questions': len(session['follow_up_questions']),
                'message': f'Question {next_question_index + 1} of {len(session["follow_up_questions"])}'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<session_id>', methods=['GET'])
def get_session_status(session_id):
    """Get current session status"""
    try:
        if session_id not in assistant.sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = assistant.sessions[session_id]
        
        return jsonify({
            'session_id': session_id,
            'step': session['step'],
            'user_query': session['user_query'],
            'questions_answered': len(session['answers']),
            'total_questions': len(session['follow_up_questions']),
            'summary': session.get('summary', ''),
            'follow_up_questions': session.get('follow_up_questions', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Shopping Assistant API is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port) 