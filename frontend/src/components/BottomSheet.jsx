import React, { useState, useContext } from 'react';
import { AppContext } from '../context/AppContext';
import ResultsSidebar from './ResultsSidebar';
import ChatList from './chat/ChatList';
import ChatDetail from './chat/ChatDetail';
import ChatInput from './chat/ChatInput';
import classes from './BottomSheet.module.css';

const BottomSheet = () => {
  const { activeMobileTab, setActiveMobileTab, curSelectedPromptInd } = useContext(AppContext);
  const [isExpanded, setIsExpanded] = useState(false);

  // Content renderer based on tab
  const renderContent = () => {
    switch (activeMobileTab) {
      case 'results':
        // Reuse ResultsSidebar but ensure it fits mobile styling if needed
        return <ResultsSidebar onClose={() => setIsExpanded(false)} />;
      case 'chat':
        return curSelectedPromptInd !== null ? <ChatDetail /> : <ChatList />;
      case 'plan':
        return (
          <div style={{ padding: '10px' }}>
            <h3>Plan a New Trip</h3>
            <ChatInput />
          </div>
        );
      default:
        return null;
    }
  };

  const handleTabCLick = (e, tab) => {
      e.stopPropagation(); 
      if(activeMobileTab === tab){
        setIsExpanded(false)
        setActiveMobileTab(null); 
      }
      else{
        setActiveMobileTab(tab); 
        setIsExpanded(true); 
      }

  }

  return (
    <div className={`${classes.bottomSheet} ${isExpanded ? classes.expanded : ''}`}>
      {/* Drag Handle / Header */}
      <div
        className={classes.header}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className={classes.dragHandle} />
      </div>

      {/* Content Area */}
      <div className={classes.content}>
        {renderContent()}
      </div>

      {/* Tabs Bar */}
      <div className={classes.tabsBar}>
        <button
          className={activeMobileTab === 'results' ? classes.activeTab : ''}
          onClick={(e) => { handleTabCLick(e, 'results') }}
        >
          Results
        </button>
        <button
          className={activeMobileTab === 'chat' ? classes.activeTab : ''}
          onClick={(e) => { handleTabCLick(e, 'chat'); }}
        >
          Chat
        </button>
        <button
          className={activeMobileTab === 'plan' ? classes.activeTab : ''}
          onClick={(e) => { handleTabCLick(e, 'plan'); }}
        >
          Plan
        </button>
      </div>
    </div>
  );
};

export default BottomSheet;
