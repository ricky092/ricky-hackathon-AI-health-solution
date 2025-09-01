# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
from database import create_connection, init_db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for all routes

# Hugging Face API configuration
API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
HEADERS = {"Authorization": f"Bearer {app.config['HUGGING_FACE_API_KEY']}"}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_sentiment():
    """Analyze the sentiment of a journal entry"""
    try:
        data = request.get_json()
        entry_text = data.get('journal_entry')
        
        if not entry_text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Call Hugging Face API
        payload = {"inputs": entry_text}
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        
        if response.status_code != 200:
            return jsonify({'error': 'API request failed'}), 500
            
        result = response.json()
        
        # Process the result
        if isinstance(result, list) and len(result) > 0:
            emotions = result[0]
            # Get the emotion with the highest score
            primary_emotion = max(emotions, key=lambda x: x['score'])
            
            # Save to database
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO journal_entries (entry_text, sentiment_label, sentiment_score)
                    VALUES (%s, %s, %s)
                """, (entry_text, primary_emotion['label'], primary_emotion['score']))
                connection.commit()
                cursor.close()
                connection.close()
            
            return jsonify({
                'success': True,
                'emotion': primary_emotion['label'],
                'score': primary_emotion['score'],
                'entry_text': entry_text
            })
        else:
            return jsonify({'error': 'Unexpected API response format'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/entries', methods=['GET'])
def get_entries():
    """Get all journal entries"""
    try:
        connection = create_connection()
        entries = []
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM journal_entries ORDER BY created_at DESC")
            entries = cursor.fetchall()
            cursor.close()
            connection.close()
        
        return jsonify(entries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/entries/chart', methods=['GET'])
def get_chart_data():
    """Get data for the chart (last 7 days)"""
    try:
        connection = create_connection()
        entries = []
        if connection:
            cursor = connection.cursor(dictionary=True)
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                SELECT DATE(created_at) as date, sentiment_label, AVG(sentiment_score) as avg_score
                FROM journal_entries 
                WHERE created_at >= %s
                GROUP BY DATE(created_at), sentiment_label
                ORDER BY date
            """, (seven_days_ago,))
            entries = cursor.fetchall()
            cursor.close()
            connection.close()
        
        return jsonify(entries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)