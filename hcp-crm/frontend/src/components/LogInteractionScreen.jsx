import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ModeToggle from './ModeToggle';
import StructuredForm from './StructuredForm';
import ChatInterface from './ChatInterface';
import { loadHCPs, loadInteractions, setSelectedHcp } from '../store/interactionsSlice';

export default function LogInteractionScreen() {
  const dispatch = useDispatch();
  const [mode, setMode] = useState('form');
  const { hcps, selectedHcpId, interactions } = useSelector((s) => s.interactions);

  useEffect(() => {
    dispatch(loadHCPs());
  }, [dispatch]);

  useEffect(() => {
    dispatch(loadInteractions(selectedHcpId));
  }, [dispatch, selectedHcpId]);

  return (
    <div>
      <div className="card" style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
        <label style={{ marginBottom: 0, minWidth: 160 }}>Active HCP context</label>
        <select
          value={selectedHcpId || ''}
          onChange={(e) => dispatch(setSelectedHcp(e.target.value ? Number(e.target.value) : null))}
        >
          <option value="">None selected</option>
          {hcps.map((h) => (
            <option key={h.id} value={h.id}>
              {h.name} — {h.specialty}
            </option>
          ))}
        </select>
      </div>

      <ModeToggle mode={mode} setMode={setMode} />

      {mode === 'form' ? <StructuredForm /> : <ChatInterface />}

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Recent Interactions</h3>
        {interactions.length === 0 && <p style={{ color: '#6b7280' }}>No interactions logged yet.</p>}
        {interactions.map((i) => (
          <div key={i.id} className="result-summary" style={{ marginBottom: 10 }}>
            <strong>#{i.id}</strong> · {i.interaction_type} · sentiment: {i.sentiment} <br />
            {i.ai_summary}
          </div>
        ))}
      </div>
    </div>
  );
}
