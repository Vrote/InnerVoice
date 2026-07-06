// frontend/stores/journalStore.ts
import { create } from 'zustand';

type ProcessingStatus = 'idle' | 'thinking' | 'waiting_for_answer' | 'done' | 'error';

interface JournalState {
  status: ProcessingStatus;
  entryId: string | null;
  sessionId: string | null;
  aiResponse: string | null;
  followupQuestion: string | null;
  emotion: string | null;
  toolsUsed: string[];
  plan: string[];
  error: string | null;

  setThinking: () => void;
  setWaitingForAnswer: (entryId: string, sessionId: string, question: string) => void;
  setDone: (entryId: string, response: string, emotion: string, tools: string[], plan: string[]) => void;
  setError: (msg: string) => void;
  reset: () => void;
}

export const useJournalStore = create<JournalState>((set) => ({
  status: 'idle',
  entryId: null,
  sessionId: null,
  aiResponse: null,
  followupQuestion: null,
  emotion: null,
  toolsUsed: [],
  plan: [],
  error: null,

  setThinking: () => set({ status: 'thinking', error: null }),

  setWaitingForAnswer: (entryId, sessionId, question) =>
    set({ status: 'waiting_for_answer', entryId, sessionId, followupQuestion: question }),

  setDone: (entryId, response, emotion, tools, plan) =>
    set({ status: 'done', entryId, aiResponse: response, emotion, toolsUsed: tools, plan }),

  setError: (msg) => set({ status: 'error', error: msg }),

  reset: () =>
    set({
      status: 'idle',
      entryId: null,
      sessionId: null,
      aiResponse: null,
      followupQuestion: null,
      emotion: null,
      toolsUsed: [],
      plan: [],
      error: null,
    }),
}));
