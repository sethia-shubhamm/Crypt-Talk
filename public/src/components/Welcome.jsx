import React, { useState, useEffect } from "react";
import styled from "styled-components";
import Robot from "../assets/robot.gif";
import Logout from "./Logout";
export default function Welcome() {
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
  }
`;
