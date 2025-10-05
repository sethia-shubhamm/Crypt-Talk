import React from 'react';

const ConnectionTest = () => {
  const apiUrl = process.env.REACT_APP_API_URL;
  const localStorageKey = process.env.REACT_APP_LOCALHOST_KEY;
  
  const testConnection = async () => {
    try {
      console.log('🔗 Testing connection to:', apiUrl);
      const response = await fetch(`${apiUrl}/health`);
      const data = await response.json();
      console.log('✅ Backend response:', data);
      alert(`Backend connected! Status: ${data.status}`);
    } catch (error) {
      console.error('❌ Connection failed:', error);
      alert(`Connection failed: ${error.message}`);
    }
  };

  return (
    <div style={{padding: '20px', background: '#f0f0f0', margin: '10px'}}>
      <h3>🔧 Connection Debug Panel</h3>
      <p><strong>API URL:</strong> {apiUrl || 'NOT SET'}</p>
      <p><strong>LocalStorage Key:</strong> {localStorageKey || 'NOT SET'}</p>
      <button onClick={testConnection} style={{padding: '10px', background: '#007bff', color: 'white', border: 'none', borderRadius: '5px'}}>
        Test Backend Connection
      </button>
    </div>
  );
};

export default ConnectionTest;