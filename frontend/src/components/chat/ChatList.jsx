import React, { useContext } from 'react';
import { AppContext } from '../../context/AppContext';
import classes from './ChatList.module.css';

const ChatList = () => {
  const { promptsChatResArr, openChat } = useContext(AppContext);

  if (promptsChatResArr.length === 0) {
    return (
      <div className={classes.emptyState}>
        <p>No chats yet. Start a new trip plan below!</p>
      </div>
    );
  }

  return (
    <div className={classes.listContainer}>
      {promptsChatResArr.map((chat, index) => (
        <div 
          key={index} 
          className={classes.chatItem}
          onClick={() => openChat(index)}
        >
          <div className={classes.promptPreview}>
            <strong>You:</strong> {chat.prompt.slice(0, 50)}{chat.prompt.length > 50 ? '...' : ''}
          </div>
          <div className={classes.responsePreview}>
            <strong>Agent:</strong> {chat.response ? chat.response.slice(0, 50) + (chat.response.length > 50 ? '...' : '') : '...'}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChatList;
