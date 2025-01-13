import historyIcon from '../asset/history_icon.png';
import csvIcon from '../asset/csv_icon.png';
import PropTypes from 'prop-types';
import createIcon from '../asset/create_icon.png';

function ChatHeader({ onToggleCsv, onToggleHistory, onCreateChat }) {
  return (
    <div className="chatbot-header-bar">
      <div class="left-buttons">
      <button className="toggle-history-button" onClick={onToggleHistory}>
        <img src={historyIcon} alt="Toggle History" />
      </button>

      <button className="create-chat-button" onClick={onCreateChat}>
        <img src={createIcon} alt="Create New Chat Icon" />
    </button>
    </div>
      <div className="chatbot-header">Chatbot Tư Vấn Luật Hôn Nhân Và Gia Đình</div>
      
      <button className="toggle-csv-button" onClick={onToggleCsv}>
        <img src={csvIcon} alt="Toggle CSV" />
      </button>
    </div>
  );
}

ChatHeader.propTypes = {
    onToggleCsv: PropTypes.func.isRequired, // Đảm bảo rằng onToggleCsv là một hàm và là prop bắt buộc
    onToggleHistory: PropTypes.func.isRequired,
    onCreateChat: PropTypes.func.isRequired,
  };

export default ChatHeader;