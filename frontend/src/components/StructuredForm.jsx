import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { submitInteraction } from '../store/interactionsSlice';

const SUGGESTED_FOLLOWUPS = [
  'Schedule follow-up meeting in 2 weeks',
  'Send Phase III data package',
  'Add HCP to advisory board invite list',
];

export default function StructuredForm() {
  const dispatch = useDispatch();
  const { hcps, selectedHcpId, status, lastResult } = useSelector((s) => s.interactions);

  const [form, setForm] = useState({
    hcp_id: selectedHcpId || '',
    interaction_type: 'visit',
    date: new Date().toISOString().slice(0, 10),
    time: new Date().toTimeString().slice(0, 5),
    attendees: '',
    products_discussed: '',
    notes: '',
    materials_shared: '',
    samples_distributed: '',
    user_sentiment: 'neutral',
    outcomes: '',
    follow_up_actions: '',
  });

  const handleChange = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const addSuggestedFollowup = (text) => {
    setForm((prev) => ({
      ...prev,
      follow_up_actions: prev.follow_up_actions ? `${prev.follow_up_actions}\n${text}` : text,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.hcp_id) return;
    dispatch(
      submitInteraction({
        hcp_id: Number(form.hcp_id),
        rep_id: 'rep_demo',
        interaction_type: form.interaction_type,
        products_discussed: form.products_discussed,
        notes: form.notes,
        attendees: form.attendees,
        materials_shared: form.materials_shared,
        samples_distributed: form.samples_distributed,
        outcomes: form.outcomes,
        follow_up_actions: form.follow_up_actions,
        user_sentiment: form.user_sentiment,
      })
    );
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3 style={{ marginTop: 0 }}>Interaction Details</h3>

      <label>Healthcare Professional</label>
      <select value={form.hcp_id} onChange={handleChange('hcp_id')} required>
        <option value="">Select an HCP...</option>
        {hcps.map((h) => (
          <option key={h.id} value={h.id}>
            {h.name} — {h.specialty}
          </option>
        ))}
      </select>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div>
          <label>Interaction Type</label>
          <select value={form.interaction_type} onChange={handleChange('interaction_type')}>
            <option value="visit">Meeting / Visit</option>
            <option value="call">Phone Call</option>
            <option value="email">Email</option>
          </select>
        </div>
        <div>
          <label>Date</label>
          <input type="date" value={form.date} onChange={handleChange('date')} />
        </div>
      </div>

      <label>Time</label>
      <input type="time" value={form.time} onChange={handleChange('time')} />

      <label>Attendees</label>
      <input
        type="text"
        placeholder="Enter names or search..."
        value={form.attendees}
        onChange={handleChange('attendees')}
      />

      <label>Topics Discussed / Products</label>
      <input
        type="text"
        placeholder="e.g. CardioMax, NeuroPlus"
        value={form.products_discussed}
        onChange={handleChange('products_discussed')}
      />

      <label>Notes / Key Discussion Points</label>
      <textarea
        placeholder="What happened during the interaction?"
        value={form.notes}
        onChange={handleChange('notes')}
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div>
          <label>Materials Shared</label>
          <input
            type="text"
            placeholder="e.g. Product brochure"
            value={form.materials_shared}
            onChange={handleChange('materials_shared')}
          />
        </div>
        <div>
          <label>Samples Distributed</label>
          <input
            type="text"
            placeholder="e.g. CardioMax 10mg x2"
            value={form.samples_distributed}
            onChange={handleChange('samples_distributed')}
          />
        </div>
      </div>

      <label>Observed / Inferred HCP Sentiment</label>
      <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
        {['positive', 'neutral', 'negative'].map((opt) => (
          <label
            key={opt}
            style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 0, fontWeight: 400 }}
          >
            <input
              type="radio"
              name="sentiment"
              value={opt}
              checked={form.user_sentiment === opt}
              onChange={handleChange('user_sentiment')}
              style={{ width: 'auto', marginBottom: 0 }}
            />
            {opt.charAt(0).toUpperCase() + opt.slice(1)}
          </label>
        ))}
      </div>

      <label>Outcomes</label>
      <textarea
        placeholder="Key outcomes or agreements..."
        value={form.outcomes}
        onChange={handleChange('outcomes')}
      />

      <label>Follow-up Actions</label>
      <textarea
        placeholder="Enter next steps or tasks..."
        value={form.follow_up_actions}
        onChange={handleChange('follow_up_actions')}
      />

      <div style={{ marginBottom: 16 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#6b7280' }}>AI Suggested Follow-ups:</span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 4 }}>
          {SUGGESTED_FOLLOWUPS.map((s) => (
            <button
              type="button"
              key={s}
              onClick={() => addSuggestedFollowup(s)}
              style={{
                background: 'none',
                border: 'none',
                color: '#4338ca',
                textAlign: 'left',
                cursor: 'pointer',
                fontSize: 13,
                padding: '2px 0',
              }}
            >
              + {s}
            </button>
          ))}
        </div>
      </div>

      <button type="submit" className="primary" disabled={status === 'loading'}>
        {status === 'loading' ? 'Logging...' : 'Log Interaction'}
      </button>

      {lastResult && (
        <div className="result-summary">
          <strong>AI Summary:</strong> {lastResult.ai_summary} <br />
          <strong>Sentiment:</strong> {lastResult.sentiment}
        </div>
      )}
    </form>
  );
}
