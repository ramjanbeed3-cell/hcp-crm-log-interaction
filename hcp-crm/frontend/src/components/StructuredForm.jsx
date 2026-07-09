import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { submitInteraction } from '../store/interactionsSlice';

export default function StructuredForm() {
  const dispatch = useDispatch();
  const { hcps, selectedHcpId, status, lastResult } = useSelector((s) => s.interactions);

  const [form, setForm] = useState({
    hcp_id: selectedHcpId || '',
    interaction_type: 'visit',
    products_discussed: '',
    notes: '',
  });

  const handleChange = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.hcp_id) return;
    dispatch(submitInteraction({ ...form, hcp_id: Number(form.hcp_id), rep_id: 'rep_demo' }));
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <label>Healthcare Professional</label>
      <select value={form.hcp_id} onChange={handleChange('hcp_id')} required>
        <option value="">Select an HCP...</option>
        {hcps.map((h) => (
          <option key={h.id} value={h.id}>
            {h.name} — {h.specialty}
          </option>
        ))}
      </select>

      <label>Interaction Type</label>
      <select value={form.interaction_type} onChange={handleChange('interaction_type')}>
        <option value="visit">In-person Visit</option>
        <option value="call">Phone Call</option>
        <option value="email">Email</option>
      </select>

      <label>Products Discussed</label>
      <input
        type="text"
        placeholder="e.g. CardioMax, NeuroPlus"
        value={form.products_discussed}
        onChange={handleChange('products_discussed')}
      />

      <label>Notes</label>
      <textarea
        placeholder="What happened during the interaction?"
        value={form.notes}
        onChange={handleChange('notes')}
      />

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
