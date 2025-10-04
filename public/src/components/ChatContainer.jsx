import React, { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import ChatInput from "./ChatInput";
import Logout from "./Logout";
import SelfDestructTimer from "./SelfDestructTimer";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";
import { IoArrowBack } from "react-icons/io5";
import { sendMessageRoute, recieveMessageRoute, downloadFileRoute } from "../utils/APIRoutes";
import ImagePreview from "./ImagePreview";
import { toast } from "react-toastify";

export default function ChatContainer({ currentChat, socket, onBackToContacts, isMobile }) {
  const [messages, setMessages] = useState([]);
  const scrollRef = useRef();
  const [arrivalMessage, setArrivalMessage] = useState(null);

  useEffect(async () => {
    const data = await JSON.parse(
      localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY)
    );
    const response = await axios.post(recieveMessageRoute, {
      from: data._id,
      to: currentChat._id,
    });
    setMessages(response.data);
  }, [currentChat]);

  useEffect(() => {
    const getCurrentChat = async () => {
      if (currentChat) {
        await JSON.parse(
          localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY)
        )._id;
      }
    };
    getCurrentChat();
  }, [currentChat]);

  const handleSendMsg = async (msg) => {
    const data = await JSON.parse(
      localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY)
    );
    socket.current.emit("send-msg", {
      to: currentChat._id,
      from: data._id,
      msg,
    });
    await axios.post(sendMessageRoute, {
      from: data._id,
      to: currentChat._id,
      message: msg,
    });

    const msgs = [...messages];
    msgs.push({ fromSelf: true, type: "text", message: msg });
    setMessages(msgs);
  };

  const handleSendFile = async (fileData) => {
    const data = await JSON.parse(
      localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY)
    );
    
    // Emit file to socket for real-time notification
    socket.current.emit("send-file", {
      to: currentChat._id,
      from: data._id,
      file: fileData,
    });

    const msgs = [...messages];
    msgs.push({ 
      fromSelf: true, 
      type: "file", 
      ...fileData 
    });
    setMessages(msgs);
  };

  useEffect(() => {
    if (socket.current) {
      socket.current.on("msg-recieve", (msg) => {
        setArrivalMessage({ fromSelf: false, type: "text", message: msg });
      });
      
      socket.current.on("file-recieve", (fileData) => {
        setArrivalMessage({ fromSelf: false, type: "file", ...fileData });
      });
      
      // Handle conversation self-destruct notification
      socket.current.on("conversation-destroyed", (data) => {
        const currentUserId = JSON.parse(localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY))?._id;
        
        // Check if this conversation involves the current user
        if (data.user1_id === currentUserId || data.user2_id === currentUserId) {
          // Clear messages for this conversation
          setMessages([]);
          
          // Clear any cached conversation data
          const conversationKey = `conversation_${currentChat._id}`;
          localStorage.removeItem(conversationKey);
          
          // Show toast notification
          toast.success("🔥 Conversation self-destructed! All messages have been permanently deleted.", {
            position: "top-center",
            autoClose: 5000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
          });
        }
      });
    }
  }, [currentChat]);

  useEffect(() => {
    arrivalMessage && setMessages((prev) => [...prev, arrivalMessage]);
  }, [arrivalMessage]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Container isMobile={isMobile}>
      <div className="chat-header">
        {isMobile && (
          <div className="back-button" onClick={onBackToContacts}>
            <IoArrowBack />
          </div>
        )}
        <div className="user-details">
          <div className="avatar">
            <img
              src={`data:image/svg+xml;base64,${currentChat.avatarImage}`}
              alt=""
            />
          </div>
          <div className="username">
            <h3>{currentChat.username}</h3>
          </div>
        </div>
        <div className="header-controls">
          <SelfDestructTimer currentChat={currentChat} />
          <Logout />
        </div>
      </div>
      <div className="chat-messages">
        {messages.map((message) => {
          return (
            <div ref={scrollRef} key={uuidv4()}>
              <div
                className={`message ${
                  message.fromSelf ? "sended" : "recieved"
                }`}
              >
                <div className="content">
                  {message.type === "file" ? (
                    <div className="file-message">
                      {message.file_type === "image" ? (
                        <div className="image-preview">
                          <ImagePreview 
                            fileId={message.file_id}
                            filename={message.filename}
                            onImageClick={() => window.open(`${downloadFileRoute}/${message.file_id}`, '_blank')}
                          />
                          <p>{message.original_filename || message.filename}</p>
                        </div>
                      ) : (
                        <div className="file-download">
                          <div className="file-icon">📄</div>
                          <div className="file-info">
                            <p className="filename">{message.original_filename || message.filename}</p>
                            <p className="filesize">{Math.round(message.file_size / 1024)} KB</p>
                          </div>
                          <button 
                            onClick={() => window.open(`${downloadFileRoute}/${message.file_id}`, '_blank')}
                            className="download-btn"
                          >
                            Download
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p>{message.message}</p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <ChatInput 
        handleSendMsg={handleSendMsg} 
        handleSendFile={handleSendFile}
        currentChat={currentChat}
      />
    </Container>
  );
}

const Container = styled.div`
  display: grid;
  grid-template-rows: 10% 80% 10%;
  gap: 0.1rem;
  overflow: hidden;
  height: ${props => props.isMobile ? '100vh' : 'auto'};
  
  @media screen and (min-width: 720px) and (max-width: 1080px) {
    grid-template-rows: 15% 70% 15%;
  }
  
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    background-color: #080420;
    
    .back-button {
      color: white;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color 0.3s ease;
      
      &:hover {
        background-color: #ffffff20;
      }
      
      svg {
        font-size: 1.5rem;
      }
    }
    
    .user-details {
      display: flex;
      align-items: center;
      gap: 1rem;
      
      .avatar {
        img {
          height: 3rem;
        }
      }
      
      .username {
        h3 {
          color: white;
        }
      }
    }
    
    .header-controls {
      display: flex;
      align-items: center;
      gap: 1rem;
      position: relative;
    }
  }
  
  .chat-messages {
    padding: 1rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    overflow: auto;
    
    &::-webkit-scrollbar {
      width: 0.2rem;
      &-thumb {
        background-color: #ffffff39;
        width: 0.1rem;
        border-radius: 1rem;
      }
    }
    
    .message {
      display: flex;
      align-items: center;
      
      .content {
        max-width: 40%;
        overflow-wrap: break-word;
        padding: 1rem;
        font-size: 1.1rem;
        border-radius: 1rem;
        color: #d1d1d1;
        
        @media screen and (min-width: 720px) and (max-width: 1080px) {
          max-width: 70%;
        }
        
        .file-message {
          .image-preview {
            img {
              max-width: 200px;
              max-height: 150px;
              border-radius: 8px;
              cursor: pointer;
              transition: transform 0.2s ease;
              
              &:hover {
                transform: scale(1.05);
              }
            }
            
            p {
              margin-top: 0.5rem;
              font-size: 0.9rem;
              color: #b1b1b1;
            }
          }
          
          .file-download {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.5rem;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            
            .file-icon {
              font-size: 2rem;
            }
            
            .file-info {
              flex: 1;
              
              .filename {
                margin: 0;
                font-weight: bold;
                font-size: 0.9rem;
              }
              
              .filesize {
                margin: 0;
                font-size: 0.8rem;
                color: #b1b1b1;
              }
            }
            
            .download-btn {
              background-color: #9a86f3;
              color: white;
              border: none;
              padding: 0.5rem 1rem;
              border-radius: 6px;
              cursor: pointer;
              font-size: 0.8rem;
              transition: background-color 0.3s ease;
              
              &:hover {
                background-color: #8a76e3;
              }
            }
          }
        }
      }
    }
    
    .sended {
      justify-content: flex-end;
      .content {
        background-color: #4f04ff21;
      }
    }
    
    .recieved {
      justify-content: flex-start;
      .content {
        background-color: #9900ff20;
      }
    }
  }

    /* Mobile styles */
    @media screen and (max-width: 768px) {
      padding: 0 1rem;
      gap: 0.5rem;
      
      .user-details {
        gap: 0.8rem;
        
        .avatar {
          img {
            height: 2.5rem;
          }
        }
        
        .username {
          h3 {
            font-size: 1.1rem;
          }
        }
      }
      
      .header-controls {
        gap: 0.5rem;
        flex-direction: row;
        align-items: center;
        justify-content: flex-end;
        flex-wrap: wrap;
      }
    }  /* Very small mobile screens */
  @media screen and (max-width: 480px) {
    .chat-header {
      padding: 0 0.5rem;
      
      .back-button {
        svg {
          font-size: 1.3rem;
        }
      }
      
      .user-details {
        gap: 0.5rem;
        
        .avatar {
          img {
            height: 2rem;
          }
        }
        
        .username {
          h3 {
            font-size: 1rem;
          }
        }
      }
    }
    
    .chat-messages {
      padding: 0.5rem;
      
      .message {
        .content {
          max-width: 85%;
          padding: 0.6rem;
          font-size: 0.9rem;
        }
      }
    }
  }
`;
