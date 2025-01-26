import { useState } from "react";
import PropTypes from "prop-types";

function ChatHistory({ sessions, onSessionClick }) {
  const [activeSession, setActiveSession] = useState(null); // Lưu trạng thái session được chọn

  const handleSessionClick = (session) => {
    setActiveSession(session.session_id); // Cập nhật session được chọn
    onSessionClick(session.session_id);  // Gọi hàm xử lý từ cha
  };

  return (
    <div className="chat-history">
      <div className="chat-history-list">
        {sessions.map((session) => (
          <div
            key={session.session_id}
            className={`chat-history-item ${
              activeSession === session.session_id ? "selected" : ""
            }`} // Kiểm tra nếu session đang được chọn thì thêm class "selected"
            onClick={() => handleSessionClick(session)}
          >
            {`${session.session_id.substring(0, 16)}`}
          </div>
        ))}
      </div>
    </div>
  );
}

ChatHistory.propTypes = {
  sessions: PropTypes.arrayOf(
    PropTypes.shape({
      session_id: PropTypes.string.isRequired,
    })
  ).isRequired,
  onSessionClick: PropTypes.func.isRequired,
};

export default ChatHistory;
