import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Chatbot.css';
import robotIcon from '../asset/robot_icon.png';
import userIcon from '../asset/user.png';
import historyIcon from '../asset/history_icon.png'; // Icon cho ẩn/hiện lịch sử
import csvIcon from '../asset/csv_icon.png'; // Icon cho ẩn/hiện CSV

function getPaginationButtons(currentPage, totalPages) {
  const maxVisibleButtons = 5; // Số nút trang hiển thị trước khi thêm "..."

  const buttons = [];
  const half = Math.floor(maxVisibleButtons / 2);

  if (totalPages <= maxVisibleButtons + 5) {
    // Hiển thị tất cả các nút nếu số trang ít hơn hoặc bằng 7 (5 nút + 2 đầu/cuối)
    for (let i = 1; i <= totalPages; i++) {
      buttons.push(i);
    }
  } else {
    if (currentPage <= half + 1) {
      // Hiển thị các nút đầu tiên và "..."
      for (let i = 1; i <= maxVisibleButtons; i++) {
        buttons.push(i);
      }
      buttons.push('...');
      buttons.push(totalPages);
    } else if (currentPage > totalPages - half) {
      // Hiển thị "..." và các nút cuối cùng
      buttons.push(1);
      buttons.push('...');
      for (let i = totalPages - maxVisibleButtons + 1; i <= totalPages; i++) {
        buttons.push(i);
      }
    } else {
      // Hiển thị "..." hai bên và các nút ở giữa
      buttons.push(1);
      buttons.push('...');
      for (let i = currentPage - half; i <= currentPage + half; i++) {
        buttons.push(i);
      }
      buttons.push('...');
      buttons.push(totalPages);
    }
  }

  return buttons;
}



function Chatbot() {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [csvData, setCsvData] = useState([]);
  const [isCsvVisible, setIsCsvVisible] = useState(true);
  const [isHistoryVisible, setIsHistoryVisible] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage] = useState(10); // Number of rows to display per page
  const messagesEndRef = useRef(null);

  const toggleCsvVisibility = () => {
    setIsCsvVisible(!isCsvVisible);
  };

  const toggleHistoryVisibility = () => {
    setIsHistoryVisible(!isHistoryVisible);
  };

  const handleSendMessage = async () => {
    if (!userInput.trim()) return;

    const currentInput = userInput;
    setUserInput('');

    const newMessages = [...messages, { sender: 'user', text: currentInput }];
    setMessages(newMessages);

    setIsTyping(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/get_answer/', { query: currentInput });
      let botReply = response.data.results;

      botReply = botReply.replace(/(\d+\.\s)/g, '\n$1');
      botReply = botReply.replace(/([a-zA-Z]\)\s)/g, '\n$1');
      botReply = botReply.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
      botReply = botReply.replace(/-\s/g, '\n- ');

      setMessages([...newMessages, { sender: 'bot', text: botReply }]);
    } catch (error) {
      console.error('Error getting response from server:', error);
      setMessages([...newMessages, { sender: 'bot', text: 'Xin lỗi, tôi không thể trả lời câu hỏi của bạn lúc này.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
  
      try {
        const response = await axios.post('http://127.0.0.1:8000/upload_csv/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        const { headers, data } = response.data;
        setCsvData([headers, ...data]);
      } catch (error) {
        console.error('Error uploading file:', error);
        alert('Có lỗi xảy ra khi tải lên file CSV');
      }
    }
  };

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  const currentTableData = () => {
    const startIndex = (currentPage - 1) * rowsPerPage;
    return csvData.slice(startIndex + 1, startIndex + rowsPerPage + 1); // Skip the header row
  };
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  const totalPages = Math.ceil((csvData.length - 1) / rowsPerPage);

  return (
    <div className="chatbot-wrapper">
      <div className="chatbot-header-bar">
        <button className="toggle-history-button" onClick={toggleHistoryVisibility}>
          <img src={historyIcon} alt="Toggle History" />
        </button>
        <div className="chatbot-header">CHATBOT HỎI ĐÁP TRÊN DỮ LIỆU DẠNG BẢNG</div>
        <button className="toggle-csv-button" onClick={toggleCsvVisibility}>
          <img src={csvIcon} alt="Toggle CSV" />
        </button>
      </div>

      <div className="chatbot-content">
        {isHistoryVisible && (
          <div className="chat-history">
            <div className="chat-history-header">Lịch sử chat</div>
            <ul className="chat-history-list">
              <li className="chat-history-item">Lịch sử 1</li>
              <li className="chat-history-item">Lịch sử 2</li>
            </ul>
          </div>
        )}

        <div className={`chatbot-container ${!isCsvVisible ? 'expanded' : ''}`}>
          <div className="chatbot-main">
            <div className="chatbot-messages">
              {messages.map((message, index) => (
                <div key={index} className={`message-container ${message.sender}`}>
                  {message.sender === 'bot' ? (
                    <img src={robotIcon} alt="Bot Icon" className="message-icon" />
                  ) : (
                    <img src={userIcon} alt="User Icon" className="message-icon" />
                  )}
                  <div className={`message ${message.sender}`}>
                    {message.sender === 'bot' ? (
                      <div
                        dangerouslySetInnerHTML={{
                          __html: message.text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br />'),
                        }}
                      />
                    ) : (
                      <pre>{message.text}</pre>
                    )}
                  </div>
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
                onKeyDown={handleKeyDown}
                placeholder="Nhập câu hỏi của bạn..."
              />
              <button onClick={handleSendMessage}>Gửi</button>
            </div>
          </div>
        </div>

        {isCsvVisible && (
          <div className="csv-container">
            <h3>Upload File CSV</h3>
            <input type="file" accept=".csv" onChange={handleFileUpload} />
            {csvData.length > 0 && (
              <div className="csv-table-wrapper">
                <table className="csv-table">
                  <thead>
                    <tr>
                      {csvData[0].map((header, index) => (
                        <th key={index}>{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {currentTableData().map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {row.map((cell, cellIndex) => (
                          <td key={cellIndex}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="pagination">
                  {getPaginationButtons(currentPage, totalPages).map((page, index) => (
                    <button
                      key={index}
                      className={currentPage === page ? 'active' : ''}
                      onClick={() => {
                        if (page !== '...') paginate(page);
                      }}
                      disabled={page === '...'}
                    >
                      {page}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Chatbot;