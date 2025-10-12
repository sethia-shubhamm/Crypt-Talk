import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { setSelfDestructRoute, getSelfDestructRoute, getConversationTimerRoute, cancelConversationTimerRoute, activateTimerRoute } from "../utils/APIRoutes";
import styled from "styled-components";
import { MdTimer, MdTimerOff, MdCancel } from "react-icons/md";

export default function SelfDestructTimer({ currentChat }) {
  const [currentTimer, setCurrentTimer] = useState("never");
  const [customMinutes, setCustomMinutes] = useState("");
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [conversationTimer, setConversationTimer] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const containerRef = useRef(null);

  useEffect(() => {
    loadCurrentTimer();
    if (currentChat) {
      loadConversationTimer();
    }
  }, [currentChat]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setShowDropdown(false);
        setShowCustomInput(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    // Update countdown timer every second
    let interval;
    if (conversationTimer && conversationTimer.has_timer) {
      interval = setInterval(() => {
        const now = new Date();
        const expiry = new Date(conversationTimer.expires_at);
        const remaining = Math.max(0, expiry - now);
        setTimeRemaining(remaining);
        
        if (remaining <= 0) {
          // Timer expired, refresh conversation info
          loadConversationTimer();
        }
      }, 1000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [conversationTimer]);

  const loadCurrentTimer = async () => {
    try {
      const user = JSON.parse(localStorage.getItem("chat-app-current-user"));
      const response = await axios.get(`${getSelfDestructRoute}/${user._id}`);
      
      if (response.data.status) {
        const timerMinutes = response.data.timer;
        if (!timerMinutes || timerMinutes === 0) {
          setCurrentTimer("never");
        } else if ([10, 20, 30].includes(timerMinutes)) {
          setCurrentTimer(timerMinutes.toString());
        } else {
          setCurrentTimer("custom");
          setCustomMinutes(timerMinutes.toString());
        }
      }
    } catch (error) {
      console.error("Error loading timer settings:", error);
    }
  };

  const loadConversationTimer = async () => {
    if (!currentChat) return;
    
    try {
      const user = JSON.parse(localStorage.getItem("chat-app-current-user"));
      const response = await axios.get(`${getConversationTimerRoute}/${user._id}/${currentChat._id}`);
      
      if (response.data.status) {
        setConversationTimer(response.data);
        if (response.data.has_timer) {
          const now = new Date();
          const expiry = new Date(response.data.expires_at);
          const remaining = Math.max(0, expiry - now);
          setTimeRemaining(remaining);
        }
      }
    } catch (error) {
      console.error("Error loading conversation timer:", error);
    }
  };

  const handleTimerChange = async (value) => {
    setCurrentTimer(value);
    setShowDropdown(false);
    
    if (value === "custom") {
      setShowCustomInput(true);
      return;
    } else {
      setShowCustomInput(false);
      setCustomMinutes("");
    }

    let timerMinutes = null;
    if (value !== "never") {
      timerMinutes = parseInt(value);
    }

    await saveTimer(timerMinutes);
  };

  const handleCustomSubmit = async () => {
    const minutes = parseInt(customMinutes);
    if (isNaN(minutes) || minutes <= 0) {
      alert("Please enter a valid number of minutes");
      return;
    }
    
    setShowCustomInput(false);
    await saveTimer(minutes);
  };

  const saveTimer = async (minutes) => {
    setIsLoading(true);
    try {
      const user = JSON.parse(localStorage.getItem("chat-app-current-user"));
      const response = await axios.post(setSelfDestructRoute, {
        userId: user._id,
        timerMinutes: minutes
      });

      if (response.data.status) {
        console.log("Timer updated successfully");
        
        // If we have an active chat and timer is set, activate it immediately
        if (currentChat && minutes && minutes > 0) {
          console.log("Activating timer for current conversation...");
          try {
            const activateResponse = await axios.post(activateTimerRoute, {
              fromUser: user._id,
              toUser: currentChat._id
            });
            
            if (activateResponse.data.status) {
              console.log("Conversation timer activated!");
            } else {
              console.log("Failed to activate conversation timer");
            }
          } catch (activateError) {
            console.error("Error activating timer:", activateError);
          }
        }
        
        // Reload conversation timer info after setting new timer
        setTimeout(() => {
          loadConversationTimer();
        }, 1000);
      } else {
        alert("Failed to update timer settings");
      }
    } catch (error) {
      console.error("Error saving timer:", error);
      alert("Error saving timer settings");
    } finally {
      setIsLoading(false);
    }
  };

  const cancelConversationTimer = async () => {
    if (!currentChat || !conversationTimer?.has_timer) return;
    
    setIsLoading(true);
    try {
      const user = JSON.parse(localStorage.getItem("chat-app-current-user"));
      const response = await axios.delete(`${cancelConversationTimerRoute}/${user._id}/${currentChat._id}`);
      
      if (response.data.status) {
        setConversationTimer({ has_timer: false });
        setTimeRemaining(null);
        console.log("Conversation timer cancelled");
      } else {
        alert("Failed to cancel timer");
      }
    } catch (error) {
      console.error("Error cancelling timer:", error);
      alert("Error cancelling timer");
    } finally {
      setIsLoading(false);
      setShowDropdown(false);
    }
  };

  const formatTimeRemaining = (ms) => {
    if (!ms) return "";
    const minutes = Math.floor(ms / (1000 * 60));
    const seconds = Math.floor((ms % (1000 * 60)) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getDisplayText = () => {
    if (conversationTimer?.has_timer && timeRemaining > 0) {
      return `🔥 ${formatTimeRemaining(timeRemaining)}`;
    }
    if (currentTimer === "never") return "No Timer";
    if (currentTimer === "custom" && customMinutes) return `${customMinutes}m`;
    if (currentTimer !== "never") return `${currentTimer}m`;
    return "No Timer";
  };

  const getIcon = () => {
    if (conversationTimer?.has_timer) return <MdTimer />;
    return currentTimer === "never" ? <MdTimerOff /> : <MdTimer />;
  };

  const isActive = () => {
    return conversationTimer?.has_timer || currentTimer !== "never";
  };

  return (
    <Container ref={containerRef}>
      <TimerButton 
        onClick={() => setShowDropdown(!showDropdown)}
        disabled={isLoading}
        active={isActive()}
        hasActiveTimer={conversationTimer?.has_timer}
      >
        {getIcon()}
        <span>{getDisplayText()}</span>
        {isLoading && <LoadingDot />}
      </TimerButton>
      
      {showDropdown && (
        <DropdownMenu>
          {conversationTimer?.has_timer && (
            <>
              <DropdownHeader>
                🔥 Chat will be deleted in {formatTimeRemaining(timeRemaining)}
              </DropdownHeader>
              <DropdownItem onClick={cancelConversationTimer}>
                <MdCancel /> Cancel Timer
              </DropdownItem>
              <DropdownDivider />
            </>
          )}
          <DropdownHeader>Set New Timer:</DropdownHeader>
          <DropdownItem 
            onClick={() => handleTimerChange("never")}
            active={currentTimer === "never"}
          >
            <MdTimerOff /> Never
          </DropdownItem>
          <DropdownItem 
            onClick={() => handleTimerChange("10")}
            active={currentTimer === "10"}
          >
            <MdTimer /> 10 minutes
          </DropdownItem>
          <DropdownItem 
            onClick={() => handleTimerChange("20")}
            active={currentTimer === "20"}
          >
            <MdTimer /> 20 minutes
          </DropdownItem>
          <DropdownItem 
            onClick={() => handleTimerChange("30")}
            active={currentTimer === "30"}
          >
            <MdTimer /> 30 minutes
          </DropdownItem>
          <DropdownItem 
            onClick={() => handleTimerChange("custom")}
            active={currentTimer === "custom"}
          >
            <MdTimer /> Custom
          </DropdownItem>
        </DropdownMenu>
      )}
      
      {showCustomInput && (
        <CustomInputContainer>
          <CustomInput
            type="number"
            placeholder="Minutes"
            value={customMinutes}
            onChange={(e) => setCustomMinutes(e.target.value)}
            min="1"
            disabled={isLoading}
            autoFocus
          />
          <CustomButton 
            onClick={handleCustomSubmit}
            disabled={isLoading || !customMinutes}
          >
            Set
          </CustomButton>
          <CustomButton 
            onClick={() => {
              setShowCustomInput(false);
              setCurrentTimer("never");
            }}
            secondary
          >
            Cancel
          </CustomButton>
        </CustomInputContainer>
      )}
    </Container>
  );
}

const Container = styled.div`
  position: relative;
  display: flex;
  flex-direction: column;
  
  /* Ensure dropdown and custom input don't go beyond viewport */
  @media screen and (max-width: 768px) {
    /* On mobile, ensure we have enough space for dropdowns */
    margin-right: 10px;
  }
`;

const TimerButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.8rem;
  background: ${props => 
    props.hasActiveTimer 
      ? 'linear-gradient(135deg, #ff4757, #ff3742)' 
      : props.active 
        ? 'linear-gradient(135deg, #ff6b6b, #ee5a24)' 
        : 'linear-gradient(135deg, #4e0eff, #997af0)'};
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(78, 14, 255, 0.3);
  position: relative;
  animation: ${props => props.hasActiveTimer ? 'pulse 2s infinite' : 'none'};

  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(78, 14, 255, 0.4);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  svg {
    font-size: 1rem;
  }

  span {
    white-space: nowrap;
  }

  @media screen and (max-width: 768px) {
    padding: 0.4rem 0.6rem;
    font-size: 0.8rem;
    
    svg {
      font-size: 0.9rem;
    }
  }
`;

const LoadingDot = styled.div`
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  margin-left: 0.3rem;
  animation: pulse 1.5s infinite;
  
  @keyframes pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
  }
`;

const DropdownMenu = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(78, 14, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  z-index: 1000;
  min-width: 160px;
  max-width: 200px;
  animation: slideDown 0.2s ease-out;

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @media screen and (max-width: 768px) {
    right: auto;
    left: 0;
    min-width: 140px;
    max-width: 180px;
  }

  @media screen and (max-width: 480px) {
    min-width: 120px;
    max-width: 160px;
  }
`;

const DropdownItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 1rem;
  color: white;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  background: ${props => props.active ? 'rgba(78, 14, 255, 0.3)' : 'transparent'};
  
  &:hover {
    background: rgba(78, 14, 255, 0.2);
    color: #997af0;
  }
  
  &:not(:last-child) {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  svg {
    font-size: 0.9rem;
    color: ${props => props.active ? '#ff6b6b' : '#997af0'};
  }

  @media screen and (max-width: 768px) {
    padding: 0.6rem 0.8rem;
    font-size: 0.8rem;
  }
`;

const CustomInputContainer = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
  padding: 0.8rem;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(78, 14, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  min-width: 200px;
  max-width: 280px;
  animation: slideDown 0.2s ease-out;

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @media screen and (max-width: 768px) {
    right: auto;
    left: 0;
    min-width: 180px;
    max-width: 250px;
    padding: 0.6rem;
    gap: 0.4rem;
  }

  @media screen and (max-width: 480px) {
    min-width: 160px;
    max-width: 200px;
    padding: 0.5rem;
    gap: 0.3rem;
  }
`;

const CustomInput = styled.input`
  flex: 1;
  padding: 0.4rem 0.6rem;
  border: 1px solid rgba(78, 14, 255, 0.5);
  border-radius: 6px;
  background: rgba(22, 33, 62, 0.8);
  color: white;
  font-size: 0.8rem;
  min-width: 60px;
  max-width: 80px;
  
  &:focus {
    outline: none;
    border-color: #997af0;
    box-shadow: 0 0 0 2px rgba(153, 122, 240, 0.2);
  }
  
  &:disabled {
    opacity: 0.6;
  }

  &::placeholder {
    color: #888;
    font-size: 0.75rem;
  }

  @media screen and (max-width: 768px) {
    padding: 0.3rem 0.5rem;
    font-size: 0.75rem;
    min-width: 50px;
    max-width: 70px;
  }
`;

const CustomButton = styled.button`
  padding: 0.4rem 0.6rem;
  background: ${props => props.secondary 
    ? 'rgba(255, 255, 255, 0.1)' 
    : 'linear-gradient(135deg, #4e0eff, #997af0)'};
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: 45px;
  
  &:hover:not(:disabled) {
    background: ${props => props.secondary 
      ? 'rgba(255, 255, 255, 0.2)' 
      : 'linear-gradient(135deg, #5a1aff, #a186f0)'};
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @media screen and (max-width: 768px) {
    padding: 0.3rem 0.5rem;
    font-size: 0.7rem;
    min-width: 40px;
  }

  @media screen and (max-width: 480px) {
    padding: 0.25rem 0.4rem;
    font-size: 0.65rem;
    min-width: 35px;
  }
`;

const DropdownHeader = styled.div`
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #997af0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(78, 14, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const DropdownDivider = styled.div`
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0.3rem 0;
`;