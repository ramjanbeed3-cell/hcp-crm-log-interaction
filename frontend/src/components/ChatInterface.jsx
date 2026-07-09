import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addUserMessage, sendMessage } from '../store/chatSlice';
import { loadInteractions } from '../store/interactionsSlice';

export default function ChatInterface() {
  const dispatch = useDispatch();
  const { messages, status } = useSelector((s) => s.chat);
  const { selectedHcpId } = useSelector((s) => s.interactions);
  const [draft, setDraft] = useState('');
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Whenever the agent finishes replying, re-fetch interactions/HCPs so any
  // tool call it just made (log/edit/follow-up) shows up immediately.
  useEffect(() => {
    if (status === 'succeeded') {
      dispatch(loadInteractions(selectedHcpId));
    }
  }, [status, dispatch, selectedHcpId]);

  const handleSend = () => {
    if (!draft.trim()) return;
    dispatch(addUserMessage(draft));
    const updated = [...messages, { role: 'user', content: draft }];
    dispatch(sendMessage({ messages: updated, hcpId: selectedHcpId }));
    setDraft('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="card">
      <div className="chat-window">
        {messages.map((m, idx) => (
          <div key={idx} className={`chat-bubble ${m.role}`}>
            {m.content}
            {m.toolCalls && m.toolCalls.length > 0 && (
              <span className="tools-fired">
                Tools used: {m.toolCalls.join(', ')}
              </span>
            )}
          </div>
        ))}
        <div ref={scrollRef} />
      </div>
      <div className="chat-input-row">
        <textarea
          placeholder="Describe your interaction with the HCP..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="primary" onClick={handleSend} disabled={status === 'loading'}>
          {status === 'loading' ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}