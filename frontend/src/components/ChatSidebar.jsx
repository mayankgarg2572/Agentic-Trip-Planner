
import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext';
import ChatList from './chat/ChatList';
import ChatDetail from './chat/ChatDetail';
import ChatInput from './chat/ChatInput';
import classes from './ChatSideBar.module.css';

const ChatSidebar = ({ width, onResizeStart }) => {
  const { curSelectedPromptInd } = useContext(AppContext);

  return (
    <div style={{ width: width}} className={classes.chatSidebar}>
      <div
        onMouseDown={onResizeStart}
        className={classes.resizer}
      />
      
      {curSelectedPromptInd !== null ? (
        <ChatDetail />
      ) : (
        <>
          <ChatList />
          <ChatInput />
        </>
      )}
    </div>
  );
};

export default ChatSidebar;