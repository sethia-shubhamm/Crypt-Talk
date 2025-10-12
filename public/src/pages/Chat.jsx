import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { io } from "socket.io-client";
import styled from "styled-components";
import { allUsersRoute, host } from "../utils/APIRoutes";
import ChatContainer from "../components/ChatContainer";
import Contacts from "../components/Contacts";
import Welcome from "../components/Welcome";

export default function Chat() {
  const navigate = useNavigate();
  const socket = useRef();
  const [contacts, setContacts] = useState([]);
  const [currentChat, setCurrentChat] = useState(undefined);
  const [currentUser, setCurrentUser] = useState(undefined);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [showContacts, setShowContacts] = useState(true);
  useEffect(() => {
    const checkUser = async () => {
      const userData = localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY);
      if (!userData) {
        navigate("/login");
      } else {
        try {
          setCurrentUser(JSON.parse(userData));
        } catch (error) {
          console.error("Error parsing user data:", error);
          navigate("/login");
        }
      }
    };
    checkUser();
  }, [navigate]);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  useEffect(() => {
    if (currentUser) {
      socket.current = io(host);
      socket.current.emit("add-user", currentUser._id);
    }
  }, [currentUser]);

  useEffect(() => {
    const fetchContacts = async () => {
      if (currentUser) {
        if (currentUser.isAvatarImageSet) {
          try {
            const data = await axios.get(`${allUsersRoute}/${currentUser._id}`);
            setContacts(data.data);
          } catch (error) {
            console.error("Error fetching contacts:", error);
            setContacts([]);
          }
        } else {
          navigate("/setAvatar");
        }
      }
    };
    fetchContacts();
  }, [currentUser, navigate]);
  const handleChatChange = (chat) => {
    setCurrentChat(chat);
    if (isMobile) {
      setShowContacts(false);
    }
  };

  const handleBackToContacts = () => {
    if (isMobile) {
      setShowContacts(true);
      setCurrentChat(undefined);
    }
  };
  return (
    <>
      <Container>
        <div className="container">
          {/* Desktop view - always show both */}
          {!isMobile && (
            <>
              <Contacts contacts={contacts} changeChat={handleChatChange} />
              {currentChat === undefined ? (
                <Welcome />
              ) : (
                <ChatContainer 
                  currentChat={currentChat} 
                  socket={socket} 
                  onBackToContacts={handleBackToContacts}
                />
              )}
            </>
          )}
          
          {/* Mobile view - show contacts or chat */}
          {isMobile && showContacts && (
            <Contacts contacts={contacts} changeChat={handleChatChange} />
          )}
          
          {isMobile && !showContacts && currentChat && (
            <ChatContainer 
              currentChat={currentChat} 
              socket={socket} 
              onBackToContacts={handleBackToContacts}
              isMobile={true}
            />
          )}
          
          {isMobile && !showContacts && !currentChat && (
            <Welcome />
          )}
        </div>
      </Container>
    </>
  );
}

const Container = styled.div`
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
  align-items: center;
  background-color: #131324;
  .container {
    height: 85vh;
    width: 85vw;
    background-color: #00000076;
    display: grid;
    grid-template-columns: 25% 75%;
    
    @media screen and (min-width: 720px) and (max-width: 1080px) {
      grid-template-columns: 35% 65%;
    }
    
    /* Mobile styles */
    @media screen and (max-width: 768px) {
      height: 100vh;
      width: 100vw;
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
      gap: 0;
    }
    
    /* Very small mobile screens */
    @media screen and (max-width: 480px) {
      height: 100vh;
      width: 100vw;
    }
  }
`;
