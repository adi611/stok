from flask import Flask, jsonify
from flask_cors import CORS
import redis
import os
import json

app = Flask(__name__)
CORS(app)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD', None),
    decode_responses=True
)

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        news_data = redis_client.lrange('news_stories', 0, -1)
        parsed_news = [json.loads(item) for item in news_data]
        return jsonify(parsed_news)
    except Exception as e:
        print(f"Error fetching news from Redis: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)