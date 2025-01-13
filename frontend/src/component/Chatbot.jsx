// File: Chatbot.jsx
import  { useState, useEffect } from 'react'; 
import ChatHeader from './ChatHeader';
import ChatHistory from './ChatHistory';
 import ChatMain from './ChatMain';
import CsvContainer from './CsvContainer';
import './Chatbot.css';
import axios from 'axios';


function Chatbot() {

  const [messages, setMessages] = useState([]);  // Khởi tạo mảng rỗng cho messages
  const [csvData, setCsvData] = useState([]); // Khởi tạo csvData là mảng rỗng
  const [showCsv, setShowCsv] = useState(false); // Trạng thái để điều khiển việc ẩn/hiện CsvContainer
  const [showHistory, setShowHistory] = useState(true);  // Trạng thái để hiển thị/ẩn ChatHistory

  const [sessions, setSessions] = useState([]); // Mô phỏng data sessions
  const [selectedSession, setSelectedSession] = useState(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const response = await axios.get('http://localhost:8000/get_sessions/');
        const fetchedSessions = response.data.sessions; // Cập nhật danh sách session

        // Loại bỏ session trùng lặp
        setSessions((prevSessions) => {
          const sessionMap = new Map();
          [...prevSessions, ...fetchedSessions].forEach((session) => {
            sessionMap.set(session.session_id, session);
          });
          return Array.from(sessionMap.values()); // Loại bỏ session trùng
        });
      } catch (error) {
        console.error('Error fetching sessions:', error);
      }
    };

    fetchSessions();
  }, []);

  const onSessionClick = async (session_id) => {
    try {
      const response = await fetch(`http://localhost:8000/get_session_data/${session_id}/`);
      const data = await response.json();
      
      // Chuyển đổi dữ liệu thành định dạng phù hợp với ChatMain
      const formattedMessages = data.data.flatMap(item => [
        {
          sender: 'user', // Câu hỏi từ người dùng
          text: `${item.query}`,
          timestamp: item.timestamp,
        },
        {
          sender: 'bot', // Câu trả lời từ bot
          text: `${item.answer}`,
          timestamp: item.timestamp,
        },
      ]);
  
      setMessages(formattedMessages); // Cập nhật messages
      setSelectedSession(data.session_id); // Cập nhật session_id

      // Kiểm tra và cập nhật CSV data nếu có
    if (data.file_info && data.file_info.filename) {
      console.log("File info found:", data.file_info.filename);
      setCsvData([data.file_info.headers, ...data.file_info.data]); // Hiển thị file
      setShowCsv(true); // Hiển thị CsvContainer
    } else {
      setCsvData([]); // Xóa dữ liệu CSV nếu không có file
      setShowCsv(false);
    }
    } catch (error) {
      console.error('Error fetching session data:', error);
    }
  };

  const handleSendMessage = async (message) => {  // Thêm 'async' vào đây
    // Gửi tin nhắn và thêm vào `messages`
    setMessages([...messages, { sender: 'user', text: message }]);

    try {
      const response = await axios.post('http://127.0.0.1:8000/get_answer/', { query: message, session_id: selectedSession});
      const botReply = response.data.results;
      // Thêm câu trả lời của bot vào UI
      setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: botReply }]);
    } catch (error) {
      console.error("Error fetching answer:", error);
      setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: "Không thể trả lời, vui lòng thử lại sau." }]);
    }
};

  const handleFileUpload = async (event, session_id) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', session_id);

      console.log(selectedSession)
  
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

  const toggleCsv = () => {
    setShowCsv(!showCsv); // Đảo ngược trạng thái showCsv khi bấm vào biểu tượng CSV
  };

  // Toggle hiển thị/ẩn ChatHistory
  const toggleHistory = () => {
    setShowHistory((prevShowHistory) => !prevShowHistory);  // Đảo ngược trạng thái showHistory
  };

  const onCreateChat = () => {
    // Hành động khi tạo đoạn chat mới (ví dụ: xóa tin nhắn cũ hoặc thêm session mới)
    setMessages([]); // Reset tin nhắn
    const newSession = {
      session_id: `session${Math.random().toString(36).substr(2, 9)}`, // Tạo session_id ngẫu nhiên
    };
    setSessions(prevSessions => [newSession, ...prevSessions]);
    setSelectedSession(newSession.session_id);
    console.log('Tạo đoạn chat mới');
  };

  return (
    <div className="chatbot-wrapper">
      <ChatHeader onToggleCsv={toggleCsv} onToggleHistory={toggleHistory} onCreateChat={onCreateChat}/>
      <div className="chatbot-content">

        {showHistory && <ChatHistory sessions={sessions} onSessionClick={onSessionClick} />}
        {/* <ChatHistory /> */}
        <ChatMain messages={messages} isTyping={false} onSendMessage={handleSendMessage} />

        {showCsv && (<CsvContainer csvData={csvData} 
        onFileUpload={(event) => handleFileUpload(event, selectedSession)} 
        rowsPerPage={10} />)}

        
      </div>
    </div>
  );
}

export default Chatbot;
