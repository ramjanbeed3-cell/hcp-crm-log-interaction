import React from 'react';

const CONFIG = {
  positive: { label: 'Positive', bg: '#ECFDF5', color: '#059669', dot: '#10B981' },
  neutral: { label: 'Neutral', bg: '#F3F4F6', color: '#4B5563', dot: '#9CA3AF' },
  negative: { label: 'Negative', bg: '#FEF2F2', color: '#DC2626', dot: '#EF4444' },
};

export default function SentimentBadge({ sentiment }) {
  const key = (sentiment || 'neutral').toLowerCase();
  const cfg = CONFIG[key] || CONFIG.neutral;

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        padding: '2px 10px',
        borderRadius: 999,
        background: cfg.bg,
        color: cfg.color,
        fontSize: 12,
        fontWeight: 600,
        letterSpacing: '0.01em',
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: cfg.dot, display: 'inline-block' }} />
      {cfg.label}
    </span>
  );
}