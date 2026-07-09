import React from 'react';

export default function Header() {
  return (
    <header className="app-header">
      <div className="app-header-mark" aria-hidden="true">
        <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="15" cy="15" r="15" fill="#4338CA" />
          <path
            d="M6 15H10.5L12.5 9L17 20L19 15H24"
            stroke="white"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      <div>
        <h1>AI-First CRM <span className="app-header-divider">·</span> HCP Module</h1>
        <p>Log Interaction — structured form or conversational chat, powered by a LangGraph agent.</p>
      </div>
    </header>
  );
}