import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const fetchHCPs = () => api.get('/api/hcps').then((r) => r.data);

export const fetchInteractions = (hcpId) =>
  api.get('/api/interactions', { params: hcpId ? { hcp_id: hcpId } : {} }).then((r) => r.data);

export const createInteraction = (payload) =>
  api.post('/api/interactions', payload).then((r) => r.data);

export const sendChatMessage = (messages, hcpId) =>
  api.post('/api/chat', { messages, hcp_id: hcpId }).then((r) => r.data);
