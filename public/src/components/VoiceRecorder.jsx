import React, { useState, useRef, useEffect } from "react";
import { BsMicFill, BsStopFill } from "react-icons/bs";
import { IoMdSend, IoMdClose } from "react-icons/io";
import { MdDelete } from "react-icons/md";
import styled from "styled-components";
import axios from "axios";
import { uploadVoiceRoute } from "../utils/APIRoutes";

export default function VoiceRecorder({ handleSendVoice, currentChat, onClose }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [expiryMinutes, setExpiryMinutes] = useState(60);
  const [isUploading, setIsUploading] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioRef = useRef(null);
  const timerRef = useRef(null);
  const chunksRef = useRef([]);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setRecordedBlob(blob);
        
        // Stop all tracks to release the microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    setIsRecording(false);
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  };

  const playRecording = () => {
    if (recordedBlob && audioRef.current) {
      const url = URL.createObjectURL(recordedBlob);
      audioRef.current.src = url;
      audioRef.current.play();
      setIsPlaying(true);
      
      audioRef.current.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(url);
      };
    }
  };

  const deleteRecording = () => {
    setRecordedBlob(null);
    setRecordingTime(0);
    
    if (audioRef.current) {
      audioRef.current.src = '';
    }
  };

  const sendVoiceMessage = async () => {
    if (!recordedBlob) return;

    setIsUploading(true);
    
    try {
      const data = JSON.parse(
        localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY)
      );

      const formData = new FormData();
      
      // Create a file from the blob
      const file = new File([recordedBlob], `voice_${Date.now()}.webm`, {
        type: 'audio/webm'
      });
      
      formData.append('voice', file);
      formData.append('from', data._id);
      formData.append('to', currentChat._id);
      formData.append('expiry_minutes', expiryMinutes);

      const response = await axios.post(uploadVoiceRoute, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.status) {
        // Notify parent component about voice message
        if (handleSendVoice) {
          handleSendVoice({
            type: 'voice',
            voice_id: response.data.voice_id,
            filename: response.data.filename,
            file_size: response.data.file_size,
            duration_minutes: response.data.duration_minutes,
            expiry_time: response.data.expiry_time
          });
        }
        
        // Close the recorder
        onClose();
      } else {
        alert(response.data.msg || 'Failed to send voice message');
      }
    } catch (error) {
      console.error("Voice upload error:", error);
      alert("Failed to send voice message");
    } finally {
      setIsUploading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Container>
      <div className="header">
        <h3>Voice Message</h3>
        <button className="close-btn" onClick={onClose}>
          <IoMdClose />
        </button>
      </div>
      
      <div className="recorder-section">
        <div className="recording-controls">
          <div className="button-row">
            {!isRecording && !recordedBlob && (
              <button className="record-btn" onClick={startRecording}>
                <BsMicFill />
                <span>Start Recording</span>
              </button>
            )}
            
            {isRecording && (
              <button className="stop-btn" onClick={stopRecording}>
                <BsStopFill />
                <span>Stop Recording</span>
              </button>
            )}
          </div>
          
          <div className="timer">
            {formatTime(recordingTime)}
          </div>
        </div>
        
        {isRecording && (
          <div className="recording-indicator">
            <div className="pulse"></div>
            <span>Recording...</span>
          </div>
        )}
        
        {recordedBlob && (
          <div className="playback-section">
            <audio ref={audioRef} />
            <div className="playback-controls">
              <button className="play-btn" onClick={playRecording} disabled={isPlaying}>
                {isPlaying ? 'Playing...' : 'Play Recording'}
              </button>
              <button className="delete-btn" onClick={deleteRecording}>
                <MdDelete />
              </button>
            </div>
            
            <div className="expiry-settings">
              <label>Auto-delete after:</label>
              <select 
                value={expiryMinutes} 
                onChange={(e) => setExpiryMinutes(parseInt(e.target.value))}
              >
                <option value={5}>5 minutes</option>
                <option value={15}>15 minutes</option>
                <option value={30}>30 minutes</option>
                <option value={60}>1 hour</option>
                <option value={180}>3 hours</option>
                <option value={720}>12 hours</option>
                <option value={1440}>24 hours</option>
              </select>
            </div>
            
            <button 
              className="send-btn" 
              onClick={sendVoiceMessage}
              disabled={isUploading}
            >
              <IoMdSend />
              <span>{isUploading ? 'Sending...' : 'Send Voice Message'}</span>
            </button>
          </div>
        )}
      </div>
    </Container>
  );
}

const Container = styled.div`
  position: fixed;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #c98fffff 0%, #5c37e0af 100%);
  border: 3px solid #111111ff;
  border-radius: 1rem;
  padding: 1.2rem;
  width: 380px;
  max-width: 85vw;
  z-index: 1000;
  box-shadow: 0 15px 30px rgba(78, 14, 255, 0.4), 
              0 0 0 1px rgba(78, 14, 255, 0.2);
  backdrop-filter: blur(15px);

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(78, 14, 255, 0.2);
    
    h3 {
      color: #ffffff;
      margin: 0;
      font-size: 1.1rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      
      &:before {
        content: "🎤";
        font-size: 1rem;
      }
    }
    
    .close-btn {
      background: rgba(78, 14, 255, 0.1);
      border: 1px solid rgba(78, 14, 255, 0.3);
      color: #4e0eff;
      cursor: pointer;
      font-size: 1.2rem;
      padding: 0.5rem;
      border-radius: 0.5rem;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      
      &:hover {
        background: rgba(78, 14, 255, 0.2);
        color: #ffffff;
        transform: scale(1.05);
      }
    }
  }
  
  .recorder-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .recording-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.2rem;
    padding: 1rem 0;
    
    .button-row {
      display: flex;
      align-items: center;
      gap: 1rem;
      justify-content: center;
    }
    
    button {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.8rem 1.5rem;
      border: 1px solid transparent;
      border-radius: 0.8rem;
      cursor: pointer;
      font-size: 0.95rem;
      font-weight: 500;
      transition: all 0.2s ease;
      min-width: 120px;
      
      &:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
      }
    }
    
    .record-btn {
      background: linear-gradient(135deg, #4e0eff, #7928ca);
      color: white;
      border-color: #4e0eff;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #5a1aff, #8b35d1);
        box-shadow: 0 4px 15px rgba(78, 14, 255, 0.4);
      }
    }
    
    .stop-btn {
      background: rgba(255, 71, 87, 0.1);
      color: #ff4757;
      border-color: rgba(255, 71, 87, 0.3);
      
      &:hover:not(:disabled) {
        background: rgba(255, 71, 87, 0.2);
        border-color: #ff4757;
      }
    }
    
    .timer {
      background: rgba(78, 14, 255, 0.1);
      color: #4e0eff;
      font-size: 1.3rem;
      font-weight: 600;
      font-family: 'Courier New', monospace;
      padding: 0.8rem 1.5rem;
      border-radius: 0.8rem;
      border: 1px solid rgba(78, 14, 255, 0.2);
      min-width: 100px;
      text-align: center;
    }
  }
  
  .recording-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    color: #ff4757;
    font-weight: 500;
    font-size: 0.9rem;
    background: rgba(255, 71, 87, 0.1);
    padding: 0.6rem 1.2rem;
    border-radius: 2rem;
    border: 1px solid rgba(255, 71, 87, 0.2);
    
    .pulse {
      width: 8px;
      height: 8px;
      background-color: #ff4757;
      border-radius: 50%;
      animation: recordPulse 1.5s infinite;
    }
    
    @keyframes recordPulse {
      0% {
        transform: scale(1);
        opacity: 1;
      }
      50% {
        transform: scale(1.4);
        opacity: 0.6;
      }
      100% {
        transform: scale(1);
        opacity: 1;
      }
    }
  }
  
  .playback-section {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    padding: 1rem 0;
    border-top: 1px solid rgba(78, 14, 255, 0.1);
    margin-top: 1rem;
    
    .playback-controls {
      display: flex;
      gap: 1rem;
      justify-content: center;
      align-items: center;
      
      .play-btn {
        background: linear-gradient(135deg, #00d2ff, #3a7bd5);
        color: white;
        padding: 0.8rem 1.5rem;
        border: 1px solid rgba(0, 210, 255, 0.3);
        border-radius: 0.8rem;
        cursor: pointer;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        
        &:hover:not(:disabled) {
          background: linear-gradient(135deg, #00c4ff, #3570cd);
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0, 210, 255, 0.3);
        }
        
        &:disabled {
          background: rgba(116, 125, 140, 0.5);
          cursor: not-allowed;
          color: rgba(255, 255, 255, 0.6);
          border-color: transparent;
        }
      }
      
      .delete-btn {
        background: rgba(255, 71, 87, 0.1);
        color: #ff4757;
        padding: 0.8rem;
        border: 1px solid rgba(255, 71, 87, 0.3);
        border-radius: 0.8rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease;
        width: 40px;
        height: 40px;
        
        &:hover {
          background: rgba(255, 71, 87, 0.2);
          transform: translateY(-1px);
          border-color: #ff4757;
        }
        
        svg {
          font-size: 1.1rem;
        }
      }
    }
    
    .expiry-settings {
      display: flex;
      align-items: center;
      gap: 1rem;
      justify-content: center;
      padding: 0.8rem;
      background: rgba(78, 14, 255, 0.05);
      border-radius: 0.8rem;
      border: 1px solid rgba(78, 14, 255, 0.1);
      
      label {
        color: #ffffff;
        font-weight: 500;
        font-size: 0.9rem;
      }
      
      select {
        background: rgba(13, 13, 32, 0.8);
        color: #ffffff;
        border: 1px solid rgba(78, 14, 255, 0.3);
        border-radius: 0.5rem;
        padding: 0.5rem 0.8rem;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        
        &:focus {
          outline: none;
          border-color: #4e0eff;
          background: rgba(13, 13, 32, 1);
        }
        
        &:hover {
          border-color: rgba(78, 14, 255, 0.6);
        }
      }
    }
    
    .send-btn {
      background: linear-gradient(135deg, #4e0eff, #7928ca);
      color: white;
      padding: 1rem 2rem;
      border: 1px solid #4e0eff;
      border-radius: 0.8rem;
      cursor: pointer;
      font-size: 1rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.8rem;
      transition: all 0.2s ease;
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #5a1aff, #8b35d1);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(78, 14, 255, 0.4);
      }
      
      &:disabled {
        background: rgba(116, 125, 140, 0.5);
        cursor: not-allowed;
        transform: none;
        border-color: transparent;
        color: rgba(255, 255, 255, 0.6);
      }
      
      svg {
        font-size: 1.1rem;
      }
    }
  }

  /* Mobile styles */
  @media screen and (max-width: 768px) {
    width: 95vw;
    max-width: 95vw;
    padding: 1rem;
    bottom: 100px;
    
    .header h3 {
      font-size: 1rem;
    }
    
    .recording-controls {
      gap: 1rem;
      
      .button-row {
        flex-direction: column;
        gap: 0.8rem;
        width: 100%;
      }
      
      button {
        padding: 0.8rem 1.2rem;
        font-size: 0.9rem;
        width: 100%;
        max-width: 200px;
      }
      
      .timer {
        font-size: 1.2rem;
        padding: 0.6rem 1.2rem;
      }
    }
    
    .playback-controls {
      flex-direction: column;
      align-items: center;
      gap: 0.8rem;
      
      .play-btn {
        width: 100%;
        max-width: 200px;
        justify-content: center;
      }
    }
    
    .expiry-settings {
      flex-direction: column;
      gap: 0.8rem;
      text-align: center;
      
      select {
        width: 100%;
        max-width: 200px;
      }
    }
    
    .send-btn {
      width: 100%;
      padding: 1rem;
    }
  }
  
  @media screen and (max-width: 480px) {
    width: 90vw;
    padding: 0.8rem;
    bottom: 90px;
    
    .header {
      margin-bottom: 0.8rem;
      padding-bottom: 0.6rem;
      
      h3 {
        font-size: 0.9rem;
      }
      
      .close-btn {
        width: 26px;
        height: 26px;
        font-size: 0.9rem;
      }
    }
    
    .recording-controls .timer {
      font-size: 1rem;
    }
  }
`;