import React, { useState, useEffect, useRef } from 'react';
import { useMutation } from 'react-query';
import { 
  FiMic, 
  FiMicOff, 
  FiVolume2, 
  FiVolumeX,
  FiPlay,
  FiPause,
  FiDownload,
  FiSettings,
  FiRefreshCw,
  FiCheckCircle,
  FiAlertCircle
} from 'react-icons/fi';
import { useAppStore } from '../store/appStore';
import { voiceAPI } from '../services/api';
import toast from 'react-hot-toast';

const VoiceAssistant = () => {
  const { 
    voiceEnabled, 
    setVoiceEnabled, 
    isRecording, 
    setIsRecording, 
    isProcessing, 
    setIsProcessing,
    voiceSettings,
    setVoiceSettings
  } = useAppStore();
  
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [responseAudio, setResponseAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [sentiment, setSentiment] = useState(null);
  const [emotions, setEmotions] = useState([]);
  
  const mediaRecorderRef = useRef(null);
  const audioRef = useRef(null);
  const streamRef = useRef(null);

  // Voice query mutation
  const voiceQueryMutation = useMutation(
    async (formData) => {
      return voiceAPI.processVoiceQuery(formData);
    },
    {
      onSuccess: (data) => {
        setTranscript(data.query_text);
        setResponse(data.response_text);
        setResponseAudio(data.response_audio);
        setSentiment(data.sentiment);
        setEmotions(data.emotions || []);
        setIsProcessing(false);
        toast.success('Voice query processed successfully');
      },
      onError: (error) => {
        setIsProcessing(false);
        toast.error('Failed to process voice query');
        console.error('Voice query error:', error);
      }
    }
  );

  // Text-to-speech mutation
  const ttsMutation = useMutation(
    async (data) => {
      return voiceAPI.textToSpeech(data.text, data.voice_id, data.speed, data.volume);
    },
    {
      onSuccess: (data) => {
        if (data.audio_data) {
          const audioBlob = new Blob([Uint8Array.from(atob(data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' });
          setResponseAudio(URL.createObjectURL(audioBlob));
        }
        toast.success('Speech generated successfully');
      },
      onError: (error) => {
        toast.error('Failed to generate speech');
        console.error('TTS error:', error);
      }
    }
  );

  // Sentiment analysis mutation
  const sentimentMutation = useMutation(
    async (formData) => {
      return voiceAPI.analyzeSentiment(formData);
    },
    {
      onSuccess: (data) => {
        setSentiment(data.sentiment);
        setEmotions(data.emotions || []);
        toast.success('Sentiment analyzed');
      },
      onError: (error) => {
        toast.error('Failed to analyze sentiment');
        console.error('Sentiment analysis error:', error);
      }
    }
  );

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const audioChunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        
        // Process voice query
        const formData = new FormData();
        formData.append('audio_file', audioBlob);
        formData.append('context', '');
        formData.append('session_id', null);
        
        setIsProcessing(true);
        await voiceQueryMutation.mutateAsync(formData);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      toast.success('Recording started');
      
    } catch (error) {
      toast.error('Failed to access microphone');
      console.error('Microphone access error:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      toast.success('Recording stopped');
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  const playResponse = () => {
    if (responseAudio && audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const pauseResponse = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const generateSpeech = () => {
    if (response.trim()) {
      ttsMutation.mutate({
        text: response,
        voice_id: voiceSettings.voice,
        speed: voiceSettings.speed,
        volume: voiceSettings.volume
      });
    }
  };

  const analyzeSentiment = () => {
    if (audioBlob) {
      const formData = new FormData();
      formData.append('audio_file', audioBlob);
      sentimentMutation.mutate(formData);
    }
  };

  const downloadAudio = () => {
    if (audioBlob) {
      const url = URL.createObjectURL(audioBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `voice-query-${Date.now()}.wav`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const downloadResponse = () => {
    if (responseAudio) {
      const a = document.createElement('a');
      a.href = responseAudio;
      a.download = `voice-response-${Date.now()}.wav`;
      a.click();
    }
  };

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'text-success-600 bg-success-100';
      case 'negative':
        return 'text-error-600 bg-error-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getEmotionColor = (emotion) => {
    const colors = {
      excitement: 'bg-yellow-100 text-yellow-800',
      worry: 'bg-red-100 text-red-800',
      confidence: 'bg-green-100 text-green-800',
      frustration: 'bg-orange-100 text-orange-800',
      curiosity: 'bg-blue-100 text-blue-800'
    };
    return colors[emotion] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Voice Assistant</h1>
          <p className="text-gray-600">Speak your questions and get AI-powered responses</p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors duration-200 ${
              voiceEnabled
                ? 'bg-primary-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {voiceEnabled ? <FiMic size={16} /> : <FiMicOff size={16} />}
            <span>{voiceEnabled ? 'Enabled' : 'Disabled'}</span>
          </button>
        </div>
      </div>

      {/* Voice Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center">
          <div className={`w-32 h-32 mx-auto mb-6 rounded-full flex items-center justify-center transition-all duration-300 ${
            isRecording 
              ? 'bg-error-500 animate-pulse' 
              : isProcessing 
              ? 'bg-warning-500 animate-spin' 
              : 'bg-primary-500'
          }`}>
            {isRecording ? (
              <FiMicOff size={48} className="text-white" />
            ) : isProcessing ? (
              <FiRefreshCw size={48} className="text-white" />
            ) : (
              <FiMic size={48} className="text-white" />
            )}
          </div>
          
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {isRecording ? 'Recording...' : isProcessing ? 'Processing...' : 'Voice Assistant'}
          </h2>
          
          <p className="text-gray-600 mb-6">
            {isRecording 
              ? 'Speak your question clearly' 
              : isProcessing 
              ? 'Analyzing your voice input...' 
              : 'Click the microphone to start recording'
            }
          </p>
          
          <div className="flex justify-center space-x-4">
            {!isRecording && !isProcessing && (
              <button
                onClick={startRecording}
                disabled={!voiceEnabled}
                className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
              >
                Start Recording
              </button>
            )}
            
            {isRecording && (
              <button
                onClick={stopRecording}
                className="px-6 py-3 bg-error-500 text-white rounded-lg hover:bg-error-600 transition-colors duration-200"
              >
                Stop Recording
              </button>
            )}
            
            {isProcessing && (
              <button
                disabled
                className="px-6 py-3 bg-gray-400 text-white rounded-lg cursor-not-allowed"
              >
                Processing...
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Transcript and Response */}
      {(transcript || response) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Transcript */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Your Question</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={downloadAudio}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Download Audio"
                >
                  <FiDownload size={16} />
                </button>
                <button
                  onClick={analyzeSentiment}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Analyze Sentiment"
                >
                  <FiSettings size={16} />
                </button>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-700">{transcript || 'No transcript available'}</p>
            </div>
            
            {/* Sentiment Analysis */}
            {sentiment && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Sentiment Analysis</h4>
                <div className="flex items-center space-x-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(sentiment)}`}>
                    {sentiment}
                  </span>
                  {emotions.length > 0 && (
                    <div className="flex space-x-2">
                      {emotions.map((emotion, index) => (
                        <span key={index} className={`px-2 py-1 rounded-full text-xs font-medium ${getEmotionColor(emotion)}`}>
                          {emotion}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Response */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">AI Response</h3>
              <div className="flex items-center space-x-2">
                {responseAudio && (
                  <button
                    onClick={isPlaying ? pauseResponse : playResponse}
                    className="p-2 text-gray-400 hover:text-gray-600"
                    title={isPlaying ? 'Pause' : 'Play'}
                  >
                    {isPlaying ? <FiPause size={16} /> : <FiPlay size={16} />}
                  </button>
                )}
                <button
                  onClick={generateSpeech}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Generate Speech"
                >
                  <FiVolume2 size={16} />
                </button>
                <button
                  onClick={downloadResponse}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Download Response"
                >
                  <FiDownload size={16} />
                </button>
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-700">{response || 'No response available'}</p>
            </div>
            
            {/* Audio Player */}
            {responseAudio && (
              <div className="mt-4">
                <audio
                  ref={audioRef}
                  src={responseAudio}
                  onEnded={() => setIsPlaying(false)}
                  onPause={() => setIsPlaying(false)}
                  onPlay={() => setIsPlaying(true)}
                />
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <FiVolume2 size={16} />
                  <span>Audio response available</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Voice Settings */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Voice Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <select
              value={voiceSettings.language}
              onChange={(e) => setVoiceSettings({ ...voiceSettings, language: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Speed: {voiceSettings.speed}x
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={voiceSettings.speed}
              onChange={(e) => setVoiceSettings({ ...voiceSettings, speed: parseFloat(e.target.value) })}
              className="w-full"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Volume: {Math.round(voiceSettings.volume * 100)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={voiceSettings.volume}
              onChange={(e) => setVoiceSettings({ ...voiceSettings, volume: parseFloat(e.target.value) })}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">💡 Voice Assistant Tips</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Speak clearly and at a moderate pace for better recognition</li>
          <li>• Use financial terms and specific questions for better results</li>
          <li>• Try asking: "What is the revenue trend?" or "Calculate the profit margin"</li>
          <li>• The system can detect your emotional state and adjust responses accordingly</li>
        </ul>
      </div>
    </div>
  );
};

export default VoiceAssistant;
