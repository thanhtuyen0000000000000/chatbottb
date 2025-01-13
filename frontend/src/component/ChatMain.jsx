import  { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import robotIcon from '../asset/robot_icon.png';
import userIcon from '../asset/user.png';

function ChatMain({ messages = [], isTyping, onSendMessage }) {
  const [userInput, setUserInput] = useState('');
  const messagesEndRef = useRef(null);

  const handleSendMessage = () => {
    if (userInput.trim()) {
      onSendMessage(userInput);
      setUserInput('');
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chatbot-main">
      <div className="chatbot-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message-container ${message.sender}`}>
            <img
              src={message.sender === 'bot' ? robotIcon : userIcon}
              alt="Icon"
              className="message-icon"
            />
            <div
              className={`message ${message.sender}`}
              dangerouslySetInnerHTML={{
                __html: message.text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br />'),
              }}
            />
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {isTyping && (
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      )}

      <div className="chatbot-input">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Nhập câu hỏi của bạn..."
        />
        <button onClick={handleSendMessage}>Gửi</button>
      </div>
    </div>
  );
}

ChatMain.propTypes = {
    messages: PropTypes.arrayOf(
      PropTypes.shape({
        sender: PropTypes.string.isRequired,
        text: PropTypes.string.isRequired,
      })
    ).isRequired,
    isTyping: PropTypes.bool.isRequired,
    onSendMessage: PropTypes.func.isRequired,
  };

export default ChatMain;
