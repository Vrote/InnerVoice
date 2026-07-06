// frontend/stores/authStore.ts
import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  username: string;
  streak_count: number;
  longest_streak: number;
  total_messages: number;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isLoading: boolean;
  setAuth: (token: string, user: User) => void;
  logout: () => void;
  loadFromStorage: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isLoading: true,

  setAuth: (token, user) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('iv_token', token);
      localStorage.setItem('iv_user', JSON.stringify(user));
    }
    set({ token, user, isLoading: false });
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('iv_token');
      localStorage.removeItem('iv_user');
    }
    set({ token: null, user: null, isLoading: false });
  },

  loadFromStorage: () => {
    if (typeof window !== 'undefined') {
      const token   = localStorage.getItem('iv_token');
      const userStr = localStorage.getItem('iv_user');
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          set({ token, user, isLoading: false });
          return;
        } catch {
          // ignore parse error
        }
      }
    }
    set({ isLoading: false });
  },
}));
