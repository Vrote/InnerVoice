// frontend/lib/api.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000, // 2 min — agent reasoning can be slow
});

// ── Attach JWT token to every request ─────────────────────────────────────────
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('iv_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Auto-unwrap {success, data, error} envelope ────────────────────────────────
api.interceptors.response.use(
  (res) => {
    // If the response body has the {success, data} envelope, unwrap transparently
    if (res.data && typeof res.data === 'object' && 'success' in res.data && 'data' in res.data) {
      if (!res.data.success) {
        return Promise.reject(new Error(res.data.error || 'API error'));
      }
      // Mutate so callers do res.data.whatever normally
      res.data = res.data.data;
    }
    return res;
  },
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('iv_token');
      localStorage.removeItem('iv_user');
      window.location.href = '/auth/login';
    }
    return Promise.reject(err);
  }
);

export default api;
