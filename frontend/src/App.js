import React, { useState } from 'react';
import axios from 'axios';
import { ReactMediaRecorder } from 'react-media-recorder';
import './App.css';

function App() {
  const [transcript, setTranscript] = useState('');
  const [responseAudio, setResponseAudio] = useState(null);

  const handleStop = async (blobUrl, blob) => {
    const audioBlob = await fetch(blobUrl).then(res => res.blob());
    const formData = new FormData();
    formData.append('audio_data', audioBlob, 'audio.wav');

    try {
      const res = await axios.post('http://localhost:5000/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log(res);
      setTranscript(res.data.transcript);
    } catch (error) {
      console.error('Error transcribing audio:', error);
    }
  };

  const handleGenerate = async () => {
    if (!transcript) {
      alert('Please transcribe the audio first');
      return;
    }

    try {
      const res = await axios.post('http://localhost:5000/generate', { text: transcript }, {
        responseType: 'arraybuffer'
      });
      console.log(res);
      const audioBlob = new Blob([res.data], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      setResponseAudio(audioUrl);
    } catch (error) {
      console.error('Error generating speech:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Speech-to-Text and Text-to-Speech App</h1>
        <ReactMediaRecorder
          audio
          onStop={handleStop}
          render={({ startRecording, stopRecording, mediaBlobUrl }) => (
            <div className="controls">
              <button onClick={startRecording}>Start Recording</button>
              <button onClick={stopRecording}>Stop Recording</button>
            </div>
          )}
        />
        {transcript && (
          <>
            <h2>Transcription</h2>
            <p>{transcript}</p>
            <button onClick={handleGenerate}>Generate Speech</button>
          </>
        )}
        {responseAudio && (
          <>
            <h2>Generated Speech</h2>
            <audio controls src={responseAudio}></audio>
          </>
        )}
      </header>
    </div>
  );
}

export default App;
