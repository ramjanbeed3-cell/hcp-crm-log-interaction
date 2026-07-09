import React from 'react';
import LogInteractionScreen from './components/LogInteractionScreen';

export default function App() {
  return (
    <div className="app-shell">
      <div className="app-header">
        <h1>AI-First CRM · HCP Module</h1>
        <p>Log Interaction — structured form or conversational chat, powered by a LangGraph agent.</p>
      </div>
      <LogInteractionScreen />
    </div>
  );
}
