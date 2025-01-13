import PropTypes from 'prop-types';

function ChatHistory({ sessions, onSessionClick }) {
  
  return (
    <ul className="chat-history-list">
      {sessions.map((session) => (
        <li
          key={session.session_id}
          className="chat-history-item"
          onClick={() => {
            console.log("click");  // Moved inside onClick handler
            onSessionClick(session.session_id);
          }}
        >
          {`${session.session_id.substring(0, 16)}`}
        </li>
      ))}
    </ul>
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
