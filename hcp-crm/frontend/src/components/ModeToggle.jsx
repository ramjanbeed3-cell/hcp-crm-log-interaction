import React from 'react';

export default function ModeToggle({ mode, setMode }) {
  return (
    <div className="mode-toggle">
      <button
        className={mode === 'form' ? 'active' : ''}
        onClick={() => setMode('form')}
      >
        Structured Form
      </button>
      <button
        className={mode === 'chat' ? 'active' : ''}
        onClick={() => setMode('chat')}
      >
        Chat
      </button>
    </div>
  );
}
