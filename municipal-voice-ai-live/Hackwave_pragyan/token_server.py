from flask import Flask, jsonify
from flask_cors import CORS
from livekit import AccessToken
from livekit.models import VideoGrant
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def generate_token(identity: str, room: str):
    """Generate a LiveKit access token"""
    token = access_token.AccessToken(
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET"),
        identity=identity,
        ttl=3600  # 1 hour expiration
    )
    
    grant = VideoGrant(room_join=True, room=room, room_create=True)
    token.add_grant(grant)
    
    return token.to_jwt()

@app.route('/token/<identity>/<room>')
def get_token(identity, room):
    try:
        token = generate_token(identity, room)
        return jsonify({'token': token})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)