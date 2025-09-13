import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const API_BASE = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:8000';

function App() {
  const [stage, setStage] = useState('intro');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState('');
  const [summary, setSummary] = useState('');
  const [completed, setCompleted] = useState(false);
  const [history, setHistory] = useState([]);
  const [timer, setTimer] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  
  // Audio states
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [autoListen, setAutoListen] = useState(true);
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const restartTimeoutRef = useRef(null);

  // Initialize speech recognition and synthesis
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setSpeechSupported(true);
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      // Simpler, more reliable settings
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.maxAlternatives = 1;
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Speech detected:', transcript);
        
        // Stop any ongoing speech when user starts talking
        if (synthRef.current && synthRef.current.speaking) {
          console.log('Stopping TTS because user is speaking');
          synthRef.current.cancel();
        }
        
        setAnswer(prev => {
          const newText = prev ? prev + ' ' + transcript : transcript;
          return newText.trim();
        });
      };
      
      recognitionRef.current.onerror = (event) => {
        console.log('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => {
        console.log('Speech recognition ended');
        setIsListening(false);
        
        // Auto-restart if still in auto-listen mode
        if (autoListen && stage === 'interview' && !completed) {
          setTimeout(() => {
            if (recognitionRef.current && autoListen) {
              try {
                console.log('Restarting speech recognition...');
                recognitionRef.current.start();
              } catch (e) {
                console.log('Failed to restart recognition:', e);
              }
            }
          }, 1000);
        }
      };
      
      recognitionRef.current.onstart = () => {
        console.log('Speech recognition started');
        setIsListening(true);
        
        // Also stop TTS when recognition starts (user might be about to speak)
        if (synthRef.current && synthRef.current.speaking) {
          console.log('Stopping TTS because recognition started');
          synthRef.current.cancel();
        }
      };
    }
    
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }
  }, []);

  // Auto-start listening when interview begins or auto-listen is toggled
  useEffect(() => {
    if (stage === 'interview' && autoListen && speechSupported && recognitionRef.current && !isListening) {
      setTimeout(() => {
        try {
          console.log('Starting auto-listen...');
          recognitionRef.current.start();
        } catch (e) {
          console.log('Error starting recognition:', e);
        }
      }, 1000);
    }
    
    return () => {
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
    };
  }, [stage, autoListen, speechSupported, isListening]);

  // Timer effect
  React.useEffect(() => {
    if (timeLeft > 0 && stage === 'interview' && !completed) {
      const timerId = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timerId);
    } else if (timeLeft === 0 && stage === 'interview' && !completed) {
      handleTimeout();
    }
  }, [timeLeft, stage, completed]);

  const handleTimeout = async () => {
    try {
      // Stop voice recognition
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setAutoListen(false);
      
      const res = await fetch(`${API_BASE}/timeout`, { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      
      if (data.completed) {
        // Interview is complete
        setSummary(data.summary);
        setCompleted(true);
        setStage('summary');
        setTimeLeft(0);
        setHistory(h => [...h, { role: 'system', content: 'Time expired - Interview ended' }]);
      } else {
        // Move to next question
        setFeedback(data.feedback);
        setQuestion(data.question);
        startTimer(data.timer);
        setHistory(h => [...h, 
          { role: 'system', content: 'Time expired - Moving to next question' },
          { role: 'interviewer', content: data.feedback },
          { role: 'interviewer', content: data.question }
        ]);
        
        // Speak the feedback and next question
        setTimeout(() => speakText(data.feedback), 800);
        setTimeout(() => speakText(data.question), 3000);
        
        // Restart voice recognition if auto-listen is on
        if (autoListen && recognitionRef.current) {
          setTimeout(() => {
            try {
              recognitionRef.current.start();
            } catch (e) {}
          }, 4000);
        }
      }
    } catch (error) {
      console.error('Timeout error:', error);
      // Fallback - show summary stage anyway
      setSummary('Interview ended due to timeout. Summary generation failed.');
      setCompleted(true);
      setStage('summary');
      setTimeLeft(0);
    }
  };

  const startTimer = (seconds) => {
    setTimer(seconds);
    setTimeLeft(seconds);
  };

  const speakText = (text) => {
    if (synthRef.current) {
      synthRef.current.cancel(); // Stop any ongoing speech
      
      // Temporarily stop voice recognition while speaking
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop();
      }
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      // More human-like voice settings
      utterance.rate = 0.8;   // Slower for clarity
      utterance.pitch = 0.9;  // Lower pitch
      utterance.volume = 0.85;
      
      // Load voices and select best one
      let voices = synthRef.current.getVoices();
      if (voices.length === 0) {
        // Wait for voices to load
        synthRef.current.onvoiceschanged = () => {
          voices = synthRef.current.getVoices();
          selectVoice();
        };
      } else {
        selectVoice();
      }
      
      function selectVoice() {
        // Prefer female voices as they often sound more natural
        const preferredVoices = voices.filter(voice => 
          voice.lang.startsWith('en') && 
          (voice.name.includes('Female') || voice.name.includes('Samantha') || 
           voice.name.includes('Karen') || voice.name.includes('Susan') ||
           voice.name.includes('Natural') || voice.name.includes('Neural'))
        );
        
        if (preferredVoices.length > 0) {
          utterance.voice = preferredVoices[0];
        } else {
          // Fallback to any English voice
          const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
          if (englishVoices.length > 0) {
            utterance.voice = englishVoices[1] || englishVoices[0]; // Skip default if possible
          }
        }
        
        utterance.onend = () => {
          // Restart voice recognition after speaking
          if (autoListen && stage === 'interview' && !completed) {
            setTimeout(() => {
              if (recognitionRef.current && autoListen) {
                try {
                  recognitionRef.current.start();
                } catch (e) {}
              }
            }, 1000);
          }
        };
        
        synthRef.current.speak(utterance);
      }
    }
  };

  const toggleAutoListen = () => {
    const newAutoListen = !autoListen;
    setAutoListen(newAutoListen);
    
    if (newAutoListen && recognitionRef.current && stage === 'interview' && !completed) {
      // Start listening
      setTimeout(() => {
        try {
          console.log('Toggling auto-listen ON');
          recognitionRef.current.start();
        } catch (e) {
          console.log('Error starting recognition:', e);
        }
      }, 500);
    } else if (!newAutoListen && recognitionRef.current) {
      // Stop listening
      console.log('Toggling auto-listen OFF');
      recognitionRef.current.stop();
      setIsListening(false);
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
    }
  };

  const startInterview = async () => {
    try {
      const res = await fetch(`${API_BASE}/start`, { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setStage('interview');
      setQuestion(data.question);
      startTimer(data.timer);
      setHistory([{ role: 'interviewer', content: data.intro }, { role: 'interviewer', content: data.question }]);
      
      // Speak the intro and first question with natural timing
      setTimeout(() => speakText(data.intro), 800);
      setTimeout(() => speakText(data.question), 4000);
    } catch (error) {
      alert(`Error starting interview: ${error.message}`);
    }
  };

  const submitAnswer = async () => {
    try {
      // Stop voice recognition during submission
      if (recognitionRef.current && autoListen) {
        recognitionRef.current.stop();
      }
      
      const res = await fetch(`${API_BASE}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setFeedback(data.feedback);
      setHistory([...history, { role: 'candidate', content: answer }, { role: 'interviewer', content: data.feedback }]);
      setAnswer('');
      
      // Speak feedback with more natural timing
      setTimeout(() => speakText(data.feedback), 800);
      
      if (data.completed) {
        setSummary(data.summary);
        setCompleted(true);
        setStage('summary');
        setTimeLeft(0);
        setAutoListen(false);
      } else {
        setQuestion(data.question);
        startTimer(data.timer);
        setHistory(h => [...h, { role: 'interviewer', content: data.question }]);
        
        // Speak next question and restart voice recognition with better timing
        setTimeout(() => {
          speakText(data.question);
          if (autoListen && recognitionRef.current) {
            // Wait for speech to finish before restarting recognition
            setTimeout(() => {
              try {
                recognitionRef.current.start();
              } catch (e) {}
            }, 3000);
          }
        }, 2500);
      }
    } catch (error) {
      alert(`Error submitting answer: ${error.message}`);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>📊 Excel Mock Interviewer</h1>
        <p>AI-powered Excel skills assessment with voice interaction</p>
      </header>
      {stage === 'intro' && (
        <div className="intro-container">
          <div className="intro-content">
            <h2>🎯 Excel Skills Assessment</h2>
            <p>Ready for an interactive Excel interview? I'll ask you questions about Excel functions, formulas, and best practices.</p>
            
            <div className="intro-features">
              <div className="feature">
                <span className="feature-icon">🎤</span>
                <div>
                  <strong>Voice Enabled</strong>
                  <p>Speak your answers naturally or type them</p>
                </div>
              </div>
              <div className="feature">
                <span className="feature-icon">⏱️</span>
                <div>
                  <strong>Timed Questions</strong>
                  <p>60-120 seconds per question</p>
                </div>
              </div>
              <div className="feature">
                <span className="feature-icon">📊</span>
                <div>
                  <strong>Detailed Feedback</strong>
                  <p>Get personalized assessment report</p>
                </div>
              </div>
            </div>
            
            <button onClick={startInterview} className="start-btn">🚀 Start Interview</button>
          </div>
        </div>
      )}
      {stage === 'interview' && (
        <div className="interview-container">
          <div className="main-interview">
            <div className="progress-bar">
              <div className="progress-text">Question {history.filter(m => m.role === 'candidate').length + 1} of 6 • Time: {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}</div>
              <div className="timer-progress">
                <div 
                  className="timer-fill" 
                  style={{ width: `${(timeLeft / timer) * 100}%`, backgroundColor: timeLeft < 30 ? '#ff4444' : timeLeft < 60 ? '#ffaa00' : '#44aa44' }}
                ></div>
              </div>
            </div>
            
            <div className="chat-history">
              {history.map((msg, i) => (
                <div key={i} className={`message ${msg.role}`}>
                  <div className="avatar">{msg.role === 'interviewer' ? '🧑‍💼' : '👤'}</div>
                  <div className="content">
                  {msg.content}
                  {msg.role === 'interviewer' && (
                    <button 
                      onClick={() => speakText(msg.content)} 
                      className="inline-speak-btn"
                      title="Read aloud"
                    >
                      🔊
                    </button>
                  )}
                </div>
                </div>
              ))}
            </div>
            
            <div className="question-panel">
              <div className="current-question">
                <div className="question-text">{question}</div>
                <button 
                  onClick={() => speakText(question)} 
                  className="speak-btn"
                  title="Repeat question"
                >
                  🔊
                </button>
              </div>
              
              <div className="input-section">
                <textarea
                  value={answer}
                  onChange={e => setAnswer(e.target.value)}
                  placeholder={autoListen ? "💬 Just start speaking or type your answer..." : "Type your answer here..."}
                  disabled={completed || timeLeft === 0}
                  rows={4}
                />
                
                <div className="input-controls">
                  {speechSupported && (
                    <>
                      <button 
                        onClick={toggleAutoListen}
                        disabled={completed || timeLeft === 0}
                        className={`voice-btn ${isListening ? 'listening' : ''} ${autoListen ? 'auto-on' : 'auto-off'}`}
                        title={autoListen ? 'Auto voice detection ON' : 'Auto voice detection OFF'}
                      >
                        {autoListen ? (isListening ? '🎤🔴' : '🎤✅') : '🎤❌'}
                      </button>
                      
                      {!autoListen && (
                        <button 
                          onClick={() => {
                            if (recognitionRef.current) {
                              try {
                                recognitionRef.current.start();
                              } catch (e) {}
                            }
                          }}
                          disabled={completed || timeLeft === 0 || isListening}
                          className="manual-voice-btn"
                          title="Click to speak once"
                        >
                          🎤 Speak
                        </button>
                      )}
                    </>
                  )}
                  
                  <button 
                    onClick={submitAnswer} 
                    disabled={!answer.trim() || completed || timeLeft === 0}
                    className="submit-btn"
                  >
                    Submit Answer
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div className="sidebar">
            <h3>💡 How to Use</h3>
            
            <div className="instruction-section">
              <h4>🎤 Voice Input</h4>
              <ul>
                <li><strong>🎤✅ Auto ON:</strong> Just speak naturally</li>
                <li><strong>🎤❌ Manual:</strong> Click "🎤 Speak" button</li>
                <li><strong>🎤🔴 Listening:</strong> Currently recording</li>
              </ul>
            </div>
            
            <div className="instruction-section">
              <h4>🗣️ Speech Tips</h4>
              <ul>
                <li>Speak clearly and at normal pace</li>
                <li>Pause briefly between sentences</li>
                <li>Use Chrome or Edge for best results</li>
                <li>Ensure microphone permission is granted</li>
              </ul>
            </div>
            
            <div className="instruction-section">
              <h4>📝 Interview Tips</h4>
              <ul>
                <li>Answer as if explaining to a colleague</li>
                <li>Be specific about Excel functions</li>
                <li>Mention keyboard shortcuts if you know them</li>
                <li>Explain your thought process</li>
              </ul>
            </div>
            
            <div className="status-indicator">
              <div className="status-item">
                <span className="status-label">Voice Status:</span>
                <span className={`status-value ${autoListen ? 'active' : 'inactive'}`}>
                  {autoListen ? (isListening ? 'Listening 🔴' : 'Ready 🟢') : 'Manual 🟡'}
                </span>
              </div>
              
              <div className="debug-info">
                <small>Debug: Auto={autoListen ? 'ON' : 'OFF'} | Listen={isListening ? 'YES' : 'NO'} | Stage={stage}</small>
              </div>
              
              {speechSupported ? (
                <div className="status-item">
                  <span className="status-label">Browser:</span>
                  <span className="status-value active">Compatible ✅</span>
                </div>
              ) : (
                <div className="status-item">
                  <span className="status-label">Browser:</span>
                  <span className="status-value inactive">Limited Support ⚠️</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      {stage === 'summary' && (
        <div className="summary-container">
          <h2>Interview Summary</h2>
          <button 
            onClick={() => speakText(summary)} 
            className="speak-btn summary-speak"
            title="Read summary aloud"
          >
            🔊 Read Summary
          </button>
          <div className="summary-content">{summary}</div>
        </div>
      )}
    </div>
  );
}

export default App;