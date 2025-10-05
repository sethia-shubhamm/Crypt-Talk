import React, { useState, useRef } from "react";
import { BsEmojiSmileFill, BsMicFill } from "react-icons/bs";
import { IoMdSend } from "react-icons/io";
import { IoAttach } from "react-icons/io5";
import styled from "styled-components";
import Picker from "emoji-picker-react";
import axios from "axios";
import { uploadFileRoute } from "../utils/APIRoutes";
import VoiceRecorder from "./VoiceRecorder";

export default function ChatInput({ handleSendMsg, handleSendFile, handleSendVoice, currentChat }) {
  const [msg, setMsg] = useState("");
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false);
  const fileInputRef = useRef();
  const handleEmojiPickerhideShow = () => {
    setShowEmojiPicker(!showEmojiPicker);
  };

  const handleEmojiClick = (event, emojiObject) => {
    let message = msg;
    message += emojiObject.emoji;
    setMsg(message);
  };

  const sendChat = (event) => {
    event.preventDefault();
    if (msg.length > 0) {
      handleSendMsg(msg);
      setMsg("");
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      alert("File size should be less than 10MB");
      return;
    }

    // Check file type (PDF and images only)
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      alert("Only PDF and image files are allowed");
      return;
    }

    try {
      const data = await JSON.parse(
        localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY)
      );

      const formData = new FormData();
      formData.append('file', file);
      formData.append('from', data._id);
      formData.append('to', currentChat._id);

      const response = await axios.post(uploadFileRoute, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.status) {
        // Notify parent component about file upload
        if (handleSendFile) {
          handleSendFile({
            type: 'file',
            file_id: response.data.file_id,
            filename: response.data.filename,
            file_type: response.data.file_type,
            file_size: response.data.file_size
          });
        }
      }
    } catch (error) {
      console.error("File upload error:", error);
      alert("Failed to upload file");
    }

    // Reset file input
    event.target.value = '';
  };

  const openFileDialog = () => {
    fileInputRef.current.click();
  };

  const openVoiceRecorder = () => {
    setShowVoiceRecorder(true);
  };

  const closeVoiceRecorder = () => {
    setShowVoiceRecorder(false);
  };

  return (
    <Container>
      <div className="button-container">
        <div className="emoji">
          <BsEmojiSmileFill onClick={handleEmojiPickerhideShow} />
          {showEmojiPicker && <Picker onEmojiClick={handleEmojiClick} />}
        </div>
        <div className="file-upload">
          <IoAttach onClick={openFileDialog} />
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.png,.jpg,.jpeg,.gif,.webp"
            style={{ display: 'none' }}
          />
        </div>
        <div className="voice-record">
          <BsMicFill onClick={openVoiceRecorder} />
        </div>
      </div>
      <form className="input-container" onSubmit={(event) => sendChat(event)}>
        <input
          type="text"
          placeholder="type your message here"
          onChange={(e) => setMsg(e.target.value)}
          value={msg}
        />
        <button type="submit">
          <IoMdSend />
        </button>
      </form>
      
      {showVoiceRecorder && (
        <VoiceRecorder
          handleSendVoice={handleSendVoice}
          currentChat={currentChat}
          onClose={closeVoiceRecorder}
        />
      )}
    </Container>
  );
}

const Container = styled.div`
  display: grid;
  align-items: center;
  grid-template-columns: 8% 92%;
  background-color: #080420;
  padding: 0 2rem;
  
  @media screen and (min-width: 720px) and (max-width: 1080px) {
    padding: 0 1rem;
    gap: 1rem;
  }
  
  .button-container {
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    gap: 0.8rem;
    padding: 0.2rem;
    
    .emoji {
      position: relative;
      
      svg {
        font-size: 1.5rem;
        color: #ffff00c8;
        cursor: pointer;
        transition: color 0.3s ease;
        
        &:hover {
          color: #ffff00ff;
        }
      }
      
      .emoji-picker-react {
        position: absolute;
        top: -350px;
        background-color: #080420;
        box-shadow: 0 5px 10px #9a86f3;
        border-color: #9a86f3;
        z-index: 1000;
        
        .emoji-scroll-wrapper::-webkit-scrollbar {
          background-color: #080420;
          width: 5px;
          &-thumb {
            background-color: #9a86f3;
          }
        }
        
        .emoji-categories {
          button {
            filter: contrast(0);
          }
        }
        
        .emoji-search {
          background-color: transparent;
          border-color: #9a86f3;
        }
        
        .emoji-group:before {
          background-color: #080420;
        }
      }
    }
    
    .file-upload {
      svg {
        font-size: 1.5rem;
        color: #9a86f3;
        cursor: pointer;
        transition: color 0.3s ease;
        
        &:hover {
          color: #8a76e3;
        }
      }
    }
    
    .voice-record {
      svg {
        font-size: 1.5rem;
        color: #8872ffff;
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          color: #ff3838;
          transform: scale(1.1);
        }
      }
    }
  }
  
  .input-container {
    width: 100%;
    border-radius: 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    background-color: #ffffff34;
    min-height: 3rem;
    
    input {
      width: 90%;
      background-color: transparent;
      color: white;
      border: none;
      padding: 1rem;
      font-size: 1.2rem;

      &::selection {
        background-color: #9a86f3;
      }
      
      &:focus {
        outline: none;
      }
    }
    
    button {
      padding: 0.3rem 2rem;
      border-radius: 2rem;
      display: flex;
      justify-content: center;
      align-items: center;
      background-color: #9a86f3;
      border: none;
      cursor: pointer;
      transition: background-color 0.3s ease;
      
      &:hover {
        background-color: #8a76e3;
      }
      
      @media screen and (min-width: 720px) and (max-width: 1080px) {
        padding: 0.3rem 1rem;
        svg {
          font-size: 1rem;
        }
      }
      
      svg {
        font-size: 2rem;
        color: white;
      }
    }
  }

  /* Mobile styles */
  @media screen and (max-width: 768px) {
    grid-template-columns: 15% 85%;
    padding: 0 1rem;
    gap: 0.5rem;
    
    .button-container {
      flex-direction: column;
      gap: 0.3rem;
      padding: 0.1rem;
      
      .emoji {
        svg {
          font-size: 1.3rem;
        }
        
        .emoji-picker-react {
          top: -320px;
          left: -50px;
          width: 280px;
        }
      }
      
      .file-upload {
        svg {
          font-size: 1.3rem;
        }
      }
      
      .voice-record {
        svg {
          font-size: 1.3rem;
        }
      }
    }
    
    .input-container {
      gap: 1rem;
      min-height: 2.5rem;
      
      input {
        padding: 0.8rem;
        font-size: 1rem;
      }
      
      button {
        padding: 0.4rem 1.2rem;
        
        svg {
          font-size: 1.3rem;
        }
      }
    }
  }

  /* Very small mobile screens */
  @media screen and (max-width: 480px) {
    grid-template-columns: 18% 82%;
    padding: 0 0.5rem;
    
    .button-container {
      .emoji {
        svg {
          font-size: 1.2rem;
        }
        
        .emoji-picker-react {
          width: 260px;
          left: -40px;
        }
      }
      
      .file-upload {
        svg {
          font-size: 1.2rem;
        }
      }
      
      .voice-record {
        svg {
          font-size: 1.2rem;
        }
      }
    }
    
    .input-container {
      gap: 0.8rem;
      min-height: 2.2rem;
      
      input {
        padding: 0.6rem;
        font-size: 0.9rem;
      }
      
      button {
        padding: 0.3rem 1rem;
        
        svg {
          font-size: 1.1rem;
        }
      }
    }
  }
`;
