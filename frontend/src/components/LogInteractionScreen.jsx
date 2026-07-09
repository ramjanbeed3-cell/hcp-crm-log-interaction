import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import StructuredForm from './StructuredForm';
import ChatInterface from './ChatInterface';
import { loadHCPs, loadInteractions, setSelectedHcp } from '../store/interactionsSlice';

export default function LogInteractionScreen() {
  const dispatch = useDispatch();
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

      {/* Side-by-side: structured form on the left, AI chat assistant on the right -
          the rep can use either, or both, for the same interaction. */}
      <div className="log-interaction-layout">
        <StructuredForm />
        <div>
          <h4 style={{ margin: '0 0 8px' }}>AI Assistant — Log Interaction via Chat</h4>
          <ChatInterface />
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Recent Interactions</h3>
        {interactions.length === 0 && <p style={{ color: '#6b7280' }}>No interactions logged yet.</p>}
        {interactions.map((i) => (
          <div key={i.id} className="result-summary" style={{ marginBottom: 10 }}>
            <strong>#{i.id}</strong> · {i.interaction_type} · sentiment: {i.sentiment} <br />
            {i.ai_summary}
            {i.follow_up_actions && (
              <>
                <br />
                <em>Follow-up: {i.follow_up_actions}</em>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
