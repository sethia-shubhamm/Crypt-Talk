import React, { useState, useRef, useEffect } from "react";
import { BsPlayFill, BsPauseFill } from "react-icons/bs";
import { MdDownload, MdDelete } from "react-icons/md";
import { IoTimeOutline } from "react-icons/io5";
import styled from "styled-components";
import axios from "axios";
import { downloadVoiceRoute, voiceInfoRoute, deleteVoiceRoute } from "../utils/APIRoutes";

export default function VoiceMessage({ message, isOwn }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [voiceInfo, setVoiceInfo] = useState(null);
  const [isExpired, setIsExpired] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(null);
  
  const audioRef = useRef(null);
  const progressRef = useRef(null);

  useEffect(() => {
    // Load voice message info
    loadVoiceInfo();
    
    // Set up timer to check expiry
    const timer = setInterval(() => {
      if (voiceInfo && !isExpired) {
        updateTimeRemaining();
      }
    }, 60000); // Check every minute

    return () => clearInterval(timer);
  }, [message.voice_id]);

  const loadVoiceInfo = async () => {
    try {
      const response = await axios.get(`${voiceInfoRoute}/${message.voice_id}`);
      if (response.data.status) {
        setVoiceInfo(response.data.voice_message);
        setIsExpired(response.data.voice_message.is_expired);
        setTimeRemaining(response.data.voice_message.time_remaining_minutes);
      }
    } catch (error) {
      console.error("Error loading voice info:", error);
      if (error.response?.status === 404 || error.response?.status === 410) {
        setIsExpired(true);
      }
    }
  };

  const updateTimeRemaining = () => {
    if (voiceInfo && voiceInfo.expiry_time) {
      const expiryTime = new Date(voiceInfo.expiry_time);
      const now = new Date();
      const remaining = Math.max(0, Math.floor((expiryTime - now) / (1000 * 60)));
      
      setTimeRemaining(remaining);
      
      if (remaining <= 0) {
        setIsExpired(true);
      }
    }
  };

  const playVoice = async () => {
    if (isExpired) {
      alert("This voice message has expired");
      return;
    }

    setIsLoading(true);
    
    try {
      const response = await axios.get(`${downloadVoiceRoute}/${message.voice_id}`, {
        responseType: 'blob'
      });
      
      const audioUrl = URL.createObjectURL(response.data);
      audioRef.current.src = audioUrl;
      
      audioRef.current.onloadedmetadata = () => {
        setDuration(audioRef.current.duration);
        setIsLoading(false);
      };
      
      audioRef.current.onplay = () => setIsPlaying(true);
      audioRef.current.onpause = () => setIsPlaying(false);
      audioRef.current.onended = () => {
        setIsPlaying(false);
        setCurrentTime(0);
        URL.revokeObjectURL(audioUrl);
      };
      
      audioRef.current.ontimeupdate = () => {
        setCurrentTime(audioRef.current.currentTime);
        updateProgress();
      };
      
      await audioRef.current.play();
      
    } catch (error) {
      console.error("Error playing voice:", error);
      setIsLoading(false);
      
      if (error.response?.status === 410) {
        setIsExpired(true);
        alert("This voice message has expired or reached its play limit");
      } else if (error.response?.status === 404) {
        setIsExpired(true);
        alert("Voice message not found");
      } else {
        alert("Failed to play voice message");
      }
    }
  };

  const pauseVoice = () => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
  };

  const updateProgress = () => {
    if (audioRef.current && progressRef.current && duration > 0) {
      const progress = (currentTime / duration) * 100;
      progressRef.current.style.width = `${progress}%`;
    }
  };

  const formatTime = (timeInSeconds) => {
    if (!timeInSeconds || isNaN(timeInSeconds)) return "0:00";
    
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const formatTimeRemaining = (minutes) => {
    if (minutes < 60) {
      return `${minutes}m`;
    } else if (minutes < 1440) {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    } else {
      const days = Math.floor(minutes / 1440);
      const hours = Math.floor((minutes % 1440) / 60);
      return hours > 0 ? `${days}d ${hours}h` : `${days}d`;
    }
  };

  const downloadVoice = async () => {
    if (isExpired) {
      alert("This voice message has expired");
      return;
    }

    try {
      const response = await axios.get(`${downloadVoiceRoute}/${message.voice_id}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', voiceInfo?.original_filename || 'voice_message.webm');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error("Error downloading voice:", error);
      alert("Failed to download voice message");
    }
  };

  if (isExpired) {
    return (
      <ExpiredContainer className={isOwn ? "own" : ""}>
        <div className="expired-content">
          <IoTimeOutline />
          <span>Voice message expired</span>
        </div>
      </ExpiredContainer>
    );
  }

  return (
    <Container className={isOwn ? "own" : ""}>
      <audio ref={audioRef} />
      
      <div className="voice-content">
        <div className="play-controls">
          <button 
            className="play-btn" 
            onClick={isPlaying ? pauseVoice : playVoice}
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="loading-spinner" />
            ) : isPlaying ? (
              <BsPauseFill />
            ) : (
              <BsPlayFill />
            )}
          </button>
          
          <div className="waveform">
            <div className="progress-bar">
              <div className="progress" ref={progressRef}></div>
            </div>
            <div className="time-info">
              <span>{formatTime(currentTime)}</span>
              {duration > 0 && <span> / {formatTime(duration)}</span>}
            </div>
          </div>
        </div>
        
        <div className="voice-info">
          {voiceInfo && (
            <>
              <div className="file-size">
                {Math.round(voiceInfo.file_size / 1024)} KB
              </div>
              {timeRemaining !== null && timeRemaining > 0 && (
                <div className="expiry-info">
                  <IoTimeOutline />
                  <span>{formatTimeRemaining(timeRemaining)}</span>
                </div>
              )}
              {voiceInfo.play_count > 0 && (
                <div className="play-count">
                  Played {voiceInfo.play_count} time{voiceInfo.play_count !== 1 ? 's' : ''}
                </div>
              )}
            </>
          )}
        </div>
        
        <div className="action-buttons">
          <button className="download-btn" onClick={downloadVoice} title="Download">
            <MdDownload />
          </button>
        </div>
      </div>
    </Container>
  );
}

const ExpiredContainer = styled.div`
  background-color: #2a2a2a;
  border: 1px solid #555;
  border-radius: 1rem;
  padding: 1rem;
  margin: 0.5rem 0;
  max-width: 300px;
  opacity: 0.6;
  
  &.own {
    align-self: flex-end;
    background-color: #3a3a3a;
  }
  
  .expired-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #999;
    font-style: italic;
    
    svg {
      font-size: 1.2rem;
    }
  }
`;

const Container = styled.div`
  background-color: #080420;
  border: 1px solid #9a86f3;
  border-radius: 1rem;
  padding: 1rem;
  margin: 0.5rem 0;
  max-width: 350px;
  min-width: 250px;
  
  &.own {
    align-self: flex-end;
    background-color: #160d3dff;
    border-color: #8a76e3;
    
    .play-btn {
      background-color: #ffffff;
      color: #9a86f3;
      
      &:hover {
        background-color: #f0f0f0;
      }
    }
    
    .progress-bar {
      background-color: rgba(255, 255, 255, 0.3);
      
      .progress {
        background-color: #ffffff;
      }
    }
    
    .time-info, .file-size, .play-count {
      color: #ffffff;
    }
    
    .expiry-info {
      color: rgba(255, 255, 255, 0.8);
    }
    
    .action-buttons button {
      color: #ffffff;
      border-color: rgba(255, 255, 255, 0.3);
      
      &:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: #ffffff;
      }
    }
  }
  
  .voice-content {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }
  
  .play-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    
    .play-btn {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      border: none;
      background-color: #9a86f3;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover:not(:disabled) {
        background-color: #8a76e3;
        transform: scale(1.05);
      }
      
      &:disabled {
        background-color: #666;
        cursor: not-allowed;
      }
      
      svg {
        font-size: 1.2rem;
      }
      
      .loading-spinner {
        width: 16px;
        height: 16px;
        border: 2px solid #ffffff;
        border-top: 2px solid transparent;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    }
    
    .waveform {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
      
      .progress-bar {
        height: 4px;
        background-color: rgba(154, 134, 243, 0.3);
        border-radius: 2px;
        overflow: hidden;
        
        .progress {
          height: 100%;
          background-color: #9a86f3;
          border-radius: 2px;
          transition: width 0.1s ease;
          width: 0%;
        }
      }
      
      .time-info {
        font-size: 0.8rem;
        color: #999;
        font-family: 'Courier New', monospace;
      }
    }
  }
  
  .voice-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 0.75rem;
    
    .file-size {
      color: #999;
    }
    
    .expiry-info {
      display: flex;
      align-items: center;
      gap: 0.3rem;
      color: #ffa502;
      
      svg {
        font-size: 0.9rem;
      }
    }
    
    .play-count {
      color: #999;
      font-style: italic;
    }
  }
  
  .action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    
    button {
      background: none;
      border: 1px solid rgba(154, 134, 243, 0.3);
      border-radius: 0.3rem;
      color: #9a86f3;
      padding: 0.3rem;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background-color: rgba(154, 134, 243, 0.1);
        border-color: #9a86f3;
      }
      
      svg {
        font-size: 1rem;
      }
    }
  }

  /* Mobile styles */
  @media screen and (max-width: 768px) {
    max-width: 280px;
    min-width: 200px;
    padding: 0.8rem;
    
    .play-controls {
      gap: 0.8rem;
      
      .play-btn {
        width: 35px;
        height: 35px;
        
        svg {
          font-size: 1rem;
        }
      }
    }
    
    .voice-info {
      font-size: 0.7rem;
      gap: 0.3rem;
    }
  }
`;