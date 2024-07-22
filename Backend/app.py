from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import openai
from deepgram import Deepgram
import requests
import asyncio
import nest_asyncio
from io import BytesIO
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv()

nest_asyncio.apply()

openai.api_key = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
deepgram = Deepgram(DEEPGRAM_API_KEY)

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No audio data provided'}), 400

    audio_data = request.files['audio_data']
    source = {'buffer': audio_data.read(), 'mimetype': 'audio/wav'}
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(deepgram.transcription.prerecorded(source, {'punctuate': True}))

    transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
    return jsonify({'transcript': transcript})

@app.route('/generate', methods=['POST'])
def generate_speech():
    data = request.json
    text = data['text']
    
    # Generate response from OpenAI
    openai_response = openai.Completion.create(
        engine="gpt-3.5-turbo-16k",  # You can use other engines like 'gpt-3.5-turbo'
        prompt=text,
        max_tokens=100  # Adjust as needed
    )
    response_text = openai_response['choices'][0]['text'].strip()

    
    response_text = "Hello This is a test can you generate speech out of this?"
    
    
    # Generate speech from response text
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "text": response_text
    }
    response = requests.post(url, headers=headers, json=data)
    
    audio = BytesIO(response.content)
    audio.seek(0)
    return Response(audio, mimetype='audio/mpeg', headers={'Content-Length': len(response.content)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)