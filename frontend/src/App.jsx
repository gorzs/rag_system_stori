import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [userInput, setUserInput] = useState('');
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState('');
  const chatBoxRef = useRef(null);

  // Generate or retrieve session ID
  useEffect(() => {
    let existingId = localStorage.getItem('user_session_id');
    if (!existingId) {
      existingId = crypto.randomUUID(); // Generate UUID v4
      localStorage.setItem('user_session_id', existingId);
    }
    setUserId(existingId);
  }, []);

  const sendMessage = async () => {
    if (!userInput.trim()) return;

    const newMessage = { role: 'user', content: userInput };
    setChat(prev => [...prev, newMessage]);
    setUserInput('');
    setLoading(true);

    try {
      const res = await fetch(`${import.meta.env.VITE_BACK_API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userInput,
          user_id: userId
        })
      });
      const data = await res.json();
      setChat(prev => [...prev, { role: 'bot', content: data.answer }]);
    } catch (err) {
      console.error('Error:', err);
      setChat(prev => [...prev, { role: 'bot', content: 'Error: could not fetch response.' }]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    chatBoxRef.current?.scrollTo(0, chatBoxRef.current.scrollHeight);
  }, [chat, loading]);

  return (
    <div className="chat-container">
      <h1 className="title">Mexican revolution chat</h1>
      <div className="chat-box" ref={chatBoxRef}>
        {chat.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="bubble">{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="bubble">AV is typing...</div>
          </div>
        )}
      </div>
      <div className="input-section">
        <input
          type="text"
          value={userInput}
          onChange={e => setUserInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask something..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
