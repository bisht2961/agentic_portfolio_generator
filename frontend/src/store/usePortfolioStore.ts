import { create } from 'zustand';
import { FinalPortfolioPayload, LogEntry, PipelineStage } from '../types/portfolio';
import sampleResponse from '../../sample_response.json';

export type UiTheme = 'dark' | 'light';

const applyThemeToDom = (theme: UiTheme) => {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  if (theme === 'light') {
    root.classList.add('light');
    root.classList.remove('dark');
    root.setAttribute('data-theme', 'light');
  } else {
    root.classList.add('dark');
    root.classList.remove('light');
    root.setAttribute('data-theme', 'dark');
  }
};

const getInitialTheme = (): UiTheme => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('portfolio-ui-theme');
    if (saved === 'light' || saved === 'dark') {
      applyThemeToDom(saved);
      return saved;
    }
  }
  applyThemeToDom('dark');
  return 'dark';
};

interface PortfolioState {
  portfolio: FinalPortfolioPayload | null;
  status: PipelineStage;
  activeAgent: string;
  logs: LogEntry[];
  error: string | null;
  targetRole: string;
  themePreference: string;
  selectedFile: File | null;
  viewMode: 'interactive' | 'sandbox' | 'code';
  uiTheme: UiTheme;
  
  // Actions
  setPortfolio: (portfolio: FinalPortfolioPayload | null) => void;
  setStatus: (status: PipelineStage) => void;
  setActiveAgent: (agent: string) => void;
  addLog: (agent: string, message: string, status?: LogEntry['status']) => void;
  updateLastLogStatus: (status: LogEntry['status']) => void;
  clearLogs: () => void;
  setError: (error: string | null) => void;
  setTargetRole: (role: string) => void;
  setThemePreference: (theme: string) => void;
  setSelectedFile: (file: File | null) => void;
  setViewMode: (mode: 'interactive' | 'sandbox' | 'code') => void;
  loadSampleData: () => void;
  resetPipeline: () => void;
  toggleUiTheme: () => void;
  setUiTheme: (theme: UiTheme) => void;
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
  portfolio: sampleResponse as FinalPortfolioPayload, // Pre-loaded with sample response
  status: 'completed',
  activeAgent: 'Ready',
  uiTheme: getInitialTheme(),
  logs: [
    {
      id: 'log-init-1',
      timestamp: '20:58:00',
      agent: 'System',
      message: 'Agentic Portfolio Engine v1.0.0 initialized.',
      status: 'completed',
    },
    {
      id: 'log-init-2',
      timestamp: '20:58:01',
      agent: 'Demo Loader',
      message: `Sample profile loaded: ${(sampleResponse as FinalPortfolioPayload).full_name} (${(sampleResponse as FinalPortfolioPayload).headline}).`,
      status: 'completed',
    },
  ],
  error: null,
  targetRole: (sampleResponse as FinalPortfolioPayload).headline || 'Senior AI Systems Engineer',
  themePreference: (sampleResponse as FinalPortfolioPayload).theme?.palette || 'cyber-dark',
  selectedFile: null,
  viewMode: 'interactive',

  setPortfolio: (portfolio) => set({ portfolio }),
  setStatus: (status) => set({ status }),
  setActiveAgent: (activeAgent) => set({ activeAgent }),
  addLog: (agent, message, status = 'running') =>
    set((state) => {
      const now = new Date();
      const timeStr = now.toTimeString().split(' ')[0];
      const newEntry: LogEntry = {
        id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`,
        timestamp: timeStr,
        agent,
        message,
        status,
      };
      return { logs: [...state.logs, newEntry] };
    }),
  updateLastLogStatus: (status) =>
    set((state) => {
      if (state.logs.length === 0) return state;
      const updated = [...state.logs];
      updated[updated.length - 1] = {
        ...updated[updated.length - 1],
        status,
      };
      return { logs: updated };
    }),
  clearLogs: () => set({ logs: [] }),
  setError: (error) => set({ error }),
  setTargetRole: (targetRole) => set({ targetRole }),
  setThemePreference: (themePreference) => set({ themePreference }),
  setSelectedFile: (selectedFile) => set({ selectedFile }),
  setViewMode: (viewMode) => set({ viewMode }),
  loadSampleData: () =>
    set({
      portfolio: sampleResponse as FinalPortfolioPayload,
      status: 'completed',
      activeAgent: 'Sample Ready',
      error: null,
      logs: [
        {
          id: `log-load-${Date.now()}`,
          timestamp: new Date().toTimeString().split(' ')[0],
          agent: 'Demo Loader',
          message: `Loaded sample profile for ${(sampleResponse as FinalPortfolioPayload).full_name}.`,
          status: 'completed',
        },
      ],
    }),
  resetPipeline: () =>
    set({
      portfolio: null,
      status: 'idle',
      activeAgent: 'Idle',
      logs: [],
      error: null,
      selectedFile: null,
    }),
  setUiTheme: (uiTheme) => {
    applyThemeToDom(uiTheme);
    if (typeof window !== 'undefined') {
      localStorage.setItem('portfolio-ui-theme', uiTheme);
    }
    set({ uiTheme });
  },
  toggleUiTheme: () => {
    const nextTheme = get().uiTheme === 'dark' ? 'light' : 'dark';
    get().setUiTheme(nextTheme);
  },
}));

