import React, { useState, useRef, useEffect } from 'react';
import { useQuery, useMutation } from 'react-query';
import { 
  FiSend, 
  FiMic, 
  FiMicOff, 
  FiPaperclip, 
  FiDownload,
  FiRefreshCw,
  FiUser,
  FiCpu
} from 'react-icons/fi';
import { useAppStore } from '../store/appStore';
import { chatAPI } from '../services/api';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

const FiBot = FiCpu;

const Chat = () => {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef(null);
  
  const { 
    messages, 
    addMessage, 
    voiceEnabled, 
    isRecording: globalRecording,
    setIsRecording: setGlobalRecording,
    isProcessing: globalProcessing,
    setIsProcessing: setGlobalProcessing
  } = useAppStore();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message mutation
  const sendMessageMutation = useMutation(
    async (messageData) => {
      const response = await chatAPI.sendMessage(messageData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        addMessage({
          id: data.message_id || Date.now(),
          type: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString(),
          metadata: {
            confidence_score: data.confidence_score,
            citations: data.citations,
            processing_time: data.processing_time,
            model_used: data.model_used
          }
        });
        setIsProcessing(false);
        setGlobalProcessing(false);
      },
      onError: (error) => {
        const errorMessage = error?.response?.data?.detail || 'Failed to send message';
        toast.error(errorMessage);
        addMessage({
          id: Date.now(),
          type: 'assistant',
          content: `Error: ${errorMessage}`,
          timestamp: new Date().toISOString()
        });
        setIsProcessing(false);
        setGlobalProcessing(false);
      }
    }
  );

  // Voice query mutation
  const voiceQueryMutation = useMutation(
    async (audioData) => {
      const response = await chatAPI.sendVoiceQuery(audioData);
      return response.data;
    },
    {
      onSuccess: (data) => {
        addMessage({
          id: Date.now(),
          type: 'assistant',
          content: data.response_text,
          timestamp: new Date().toISOString(),
          metadata: data.metadata || {}
        });
        setIsProcessing(false);
        setGlobalProcessing(false);
      },
      onError: (error) => {
        toast.error('Failed to process voice query');
        setIsProcessing(false);
        setGlobalProcessing(false);
      }
    }
  );

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || isProcessing) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    addMessage(userMessage);
    setMessage('');
    setIsProcessing(true);
    setGlobalProcessing(true);

    try {
      await sendMessageMutation.mutateAsync({
        query: message,
        session_id: null,
        document_id: null
      });
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleVoiceRecord = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      toast.error('Voice recording not supported');
      return;
    }

    if (isRecording) {
      // Stop recording
      setIsRecording(false);
      setGlobalRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio_file', audioBlob);
        formData.append('context', '');
        formData.append('session_id', null);

        setIsProcessing(true);
        setGlobalProcessing(true);

        try {
          await voiceQueryMutation.mutateAsync(formData);
        } catch (error) {
          console.error('Error processing voice query:', error);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setGlobalRecording(true);

      // Auto-stop after 10 seconds
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
          stream.getTracks().forEach(track => track.stop());
        }
      }, 10000);

    } catch (error) {
      toast.error('Failed to access microphone');
      console.error('Error accessing microphone:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Add file message
    addMessage({
      id: Date.now(),
      type: 'user',
      content: `Uploaded file: ${file.name}`,
      timestamp: new Date().toISOString(),
      file: file
    });

    // Process file upload
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await chatAPI.uploadDocument(formData);
      toast.success('Document uploaded successfully');
      
      addMessage({
        id: Date.now(),
        type: 'assistant',
        content: `Document "${file.name}" has been processed and is ready for analysis. You can now ask questions about it.`,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      toast.error('Failed to upload document');
      console.error('Error uploading document:', error);
    }
  };

  const clearChat = () => {
    // Implement clear chat logic
    toast.success('Chat cleared');
  };

  const exportChat = () => {
    const chatData = {
      messages: messages,
      exported_at: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chat with FinMDA-Bot</h1>
          <p className="text-gray-600">Ask questions about your financial data</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={clearChat}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            title="Clear Chat"
          >
            <FiRefreshCw size={20} />
          </button>
          <button
            onClick={exportChat}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            title="Export Chat"
          >
            <FiDownload size={20} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiBot size={32} className="text-primary-500" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to FinMDA-Bot!
            </h3>
            <p className="text-gray-600 mb-6">
              I'm your AI financial assistant. Upload documents and ask questions to get started.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              <button className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors duration-200">
                Upload Document
              </button>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200">
                Ask a Question
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-3 max-w-3xl ${
                msg.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  msg.type === 'user' 
                    ? 'bg-primary-500 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {msg.type === 'user' ? <FiUser size={16} /> : <FiBot size={16} />}
                </div>
                <div className={`flex-1 ${
                  msg.type === 'user' ? 'text-right' : 'text-left'
                }`}>
                  <div className={`inline-block p-4 rounded-lg ${
                    msg.type === 'user'
                      ? 'bg-primary-500 text-white'
                      : 'bg-white border border-gray-200 shadow-sm'
                  }`}>
                    {msg.type === 'assistant' ? (
                      <ReactMarkdown
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '');
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={tomorrow}
                                language={match[1]}
                                PreTag="div"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            );
                          }
                        }}
                      >
                        {typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}
                      </ReactMarkdown>
                    ) : (
                      <p className="whitespace-pre-wrap">{typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}</p>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
        {isProcessing && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center">
                <FiBot size={16} />
              </div>
              <div className="bg-white border border-gray-200 shadow-sm rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-primary-500"></div>
                  <span className="text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.xlsx,.xls,.csv"
            onChange={handleFileUpload}
          />
          <label
            htmlFor="file-upload"
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200 cursor-pointer"
            title="Upload Document"
          >
            <FiPaperclip size={20} />
          </label>
          
          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask a question about your financial data..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={isProcessing}
            />
          </div>
          
          <button
            type="button"
            onClick={handleVoiceRecord}
            disabled={!voiceEnabled || isProcessing}
            className={`p-2 rounded-lg transition-colors duration-200 ${
              isRecording
                ? 'bg-error-500 text-white animate-pulse'
                : voiceEnabled
                ? 'text-primary-500 hover:bg-primary-100'
                : 'text-gray-400 cursor-not-allowed'
            }`}
            title={isRecording ? 'Stop Recording' : 'Start Voice Recording'}
          >
            {isRecording ? <FiMicOff size={20} /> : <FiMic size={20} />}
          </button>
          
          <button
            type="submit"
            disabled={!message.trim() || isProcessing}
            className="p-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            <FiSend size={20} />
          </button>
        </form>
        
        {voiceEnabled && (
          <p className="text-xs text-gray-500 mt-2">
            💡 Voice assistant is enabled. Click the microphone to speak your question.
          </p>
        )}
      </div>
    </div>
  );
};

export default Chat;
