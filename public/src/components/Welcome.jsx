import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { useNavigate } from "react-router-dom";
import Robot from "../assets/robot.gif";
import Logout from "./Logout";
export default function Welcome() {
  const navigate = useNavigate();
  const [userName, setUserName] = useState("");
  useEffect(async () => {
    setUserName(
      await JSON.parse(
        localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY)
      ).username
    );
  }, []);
  return (
    <Container>
      <img src={Robot} alt="" />
      <h1>
        Welcome, <span>{userName}!</span>
      </h1>
      <h3>Please select a chat to Start messaging.</h3>
      <div className="actions">
        <button 
          className="chat-rooms-button"
          onClick={() => navigate('/rooms')}
        >
          🛡️ Join Encrypted Chat Rooms
        </button>
      </div>
      <Logout/>
    </Container>
  );
}

const Container = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  flex-direction: column;
  padding: 2rem;
  text-align: center;
  gap: 1rem;
  
  img {
    height: 20rem;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  h3 {
    font-size: 1.2rem;
  }
  
  span {
    color: #4e0eff;
  }

  .actions {
    margin: 1rem 0;
    
    .chat-rooms-button {
      background: linear-gradient(45deg, #4e0eff, #997af0);
      border: none;
      padding: 1rem 2rem;
      border-radius: 0.5rem;
      color: white;
      font-weight: bold;
      font-size: 1rem;
      cursor: pointer;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      
      &:hover {
        background: linear-gradient(45deg, #997af0, #4e0eff);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(78, 14, 255, 0.4);
      }
      
      &:active {
        transform: translateY(0);
      }
    }
  }

  /* Mobile styles */
  @media screen and (max-width: 768px) {
    padding: 1rem;
    gap: 1rem;
    
    img {
      height: 15rem;
    }
    
    h1 {
      font-size: 1.5rem;
    }
    
    h3 {
      font-size: 1rem;
    }

    .actions {
      .chat-rooms-button {
        padding: 0.8rem 1.5rem;
        font-size: 0.9rem;
      }
    }
  }

  /* Very small mobile screens */
  @media screen and (max-width: 480px) {
    padding: 0.5rem;
    
    img {
      height: 12rem;
    }
    
    h1 {
      font-size: 1.3rem;
    }
    
    h3 {
      font-size: 0.9rem;
    }

    .actions {
      .chat-rooms-button {
        padding: 0.7rem 1.2rem;
        font-size: 0.8rem;
      }
    }
  }
`;
