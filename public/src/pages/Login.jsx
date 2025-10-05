import React, { useState, useEffect } from "react";
import axios from "axios";
import styled from "styled-components";
import { useNavigate, Link } from "react-router-dom";
import Logo from "../assets/logo.svg";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { loginRoute } from "../utils/APIRoutes";

export default function Login() {
  const navigate = useNavigate();
  const [values, setValues] = useState({ username: "", password: "" });
  const toastOptions = {
    position: "bottom-right",
    autoClose: 8000,
    pauseOnHover: true,
    draggable: true,
    theme: "dark",
  };
  useEffect(() => {
    if (localStorage.getItem(process.env.REACT_APP_LOCALHOST_KEY)) {
      navigate("/");
    }
  }, [navigate]);

  const handleChange = (event) => {
    setValues({ ...values, [event.target.name]: event.target.value });
  };

  const validateForm = () => {
    const { username, password } = values;
    if (username === "") {
      toast.error("Email and Password is required.", toastOptions);
      return false;
    } else if (password === "") {
      toast.error("Email and Password is required.", toastOptions);
      return false;
    }
    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (validateForm()) {
      const { username, password } = values;
      const { data } = await axios.post(loginRoute, {
        username,
        password,
      });
      if (data.status === false) {
        toast.error(data.msg, toastOptions);
      }
      if (data.status === true) {
        localStorage.setItem(
          process.env.REACT_APP_LOCALHOST_KEY,
          JSON.stringify(data.user)
        );

        navigate("/");
      }
    }
  };

  return (
    <>
      <FormContainer>
        <form action="" onSubmit={(event) => handleSubmit(event)}>
          <div className="brand">
            <img src={Logo} alt="logo" />
            <h1>crypt talk</h1>
          </div>
          <input
            type="text"
            placeholder="Username"
            name="username"
            onChange={(e) => handleChange(e)}
            min="3"
          />
          <input
            type="password"
            placeholder="Password"
            name="password"
            onChange={(e) => handleChange(e)}
          />
          <button type="submit">Log In</button>
          <span>
            Don't have an account ? <Link to="/register">Create One.</Link>
          </span>
        </form>
      </FormContainer>
      <ToastContainer />
    </>
  );
}

const FormContainer = styled.div`
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
  align-items: center;
  background-color: #131324;
  padding: 1rem;
  
  .brand {
    display: flex;
    align-items: center;
    gap: 1rem;
    justify-content: center;
    
    img {
      height: 5rem;
    }
    
    h1 {
      color: white;
      text-transform: uppercase;
    }
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    background-color: #00000076;
    border-radius: 2rem;
    padding: 5rem;
    width: 100%;
    max-width: 500px;
  }
  
  input {
    background-color: transparent;
    padding: 1rem;
    border: 0.1rem solid #4e0eff;
    border-radius: 0.4rem;
    color: white;
    width: 100%;
    font-size: 1rem;
    
    &:focus {
      border: 0.1rem solid #997af0;
      outline: none;
    }
    
    &::placeholder {
      color: #ffffff80;
    }
  }
  
  button {
    background-color: #4e0eff;
    color: white;
    padding: 1rem 2rem;
    border: none;
    font-weight: bold;
    cursor: pointer;
    border-radius: 0.4rem;
    font-size: 1rem;
    text-transform: uppercase;
    transition: background-color 0.3s ease;
    
    &:hover {
      background-color: #3d0bcc;
    }
  }
  
  span {
    color: white;
    text-transform: uppercase;
    text-align: center;
    
    a {
      color: #4e0eff;
      text-decoration: none;
      font-weight: bold;
    }
  }

  /* Mobile styles */
  @media screen and (max-width: 768px) {
    padding: 2rem 1rem;
    gap: 2rem;
    
    .brand {
      img {
        height: 4rem;
      }
      
      h1 {
        font-size: 1.8rem;
      }
    }
    
    form {
      padding: 3rem 2rem;
      gap: 1.5rem;
      border-radius: 1.5rem;
    }
    
    input {
      padding: 0.8rem;
      font-size: 0.9rem;
    }
    
    button {
      padding: 0.8rem 1.5rem;
      font-size: 0.9rem;
    }
    
    span {
      font-size: 0.8rem;
    }
  }

  /* Very small mobile screens */
  @media screen and (max-width: 480px) {
    padding: 1rem 0.5rem;
    
    .brand {
      img {
        height: 3rem;
      }
      
      h1 {
        font-size: 1.5rem;
      }
    }
    
    form {
      padding: 2rem 1.5rem;
      gap: 1.2rem;
      margin: 0 0.5rem;
    }
    
    input {
      padding: 0.7rem;
      font-size: 0.85rem;
    }
    
    button {
      padding: 0.7rem 1.2rem;
      font-size: 0.85rem;
    }
    
    span {
      font-size: 0.75rem;
    }
  }
`;
