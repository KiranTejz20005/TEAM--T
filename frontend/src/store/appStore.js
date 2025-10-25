import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAppStore = create(
  persist(
    (set, get) => ({
      // UI State
      sidebarOpen: true,
      theme: 'light',
      loading: false,
      
      // User State
      user: null,
      isAuthenticated: false,
      
      // Chat State
      chatSessions: [],
      currentSession: null,
      messages: [],
      
      // Document State
      documents: [],
      selectedDocument: null,
      uploadProgress: 0,
      
      // Analytics State
      analyticsData: null,
      selectedMetrics: [],
      
      // Voice Assistant State
      voiceEnabled: false,
      isRecording: false,
      isProcessing: false,
      voiceSettings: {
        language: 'en',
        voice: 'default',
        speed: 1.0,
        volume: 0.9
      },
      
      // FAQ State
      faqCategories: [],
      searchResults: [],
      
      // Settings
      settings: {
        autoSave: true,
        notifications: true,
        darkMode: false,
        language: 'en',
        timezone: 'UTC'
      },
      
      // Actions
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      setTheme: (theme) => set({ theme }),
      
      setLoading: (loading) => set({ loading }),
      
      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user 
      }),
      
      addChatSession: (session) => set((state) => ({
        chatSessions: [...state.chatSessions, session]
      })),
      
      setCurrentSession: (session) => set({ currentSession: session }),
      
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, message]
      })),
      
      clearMessages: () => set({ messages: [] }),
      
      addDocument: (document) => set((state) => ({
        documents: [...state.documents, document]
      })),
      
      setSelectedDocument: (document) => set({ selectedDocument: document }),
      
      setUploadProgress: (progress) => set({ uploadProgress: progress }),
      
      setAnalyticsData: (data) => set({ analyticsData: data }),
      
      setSelectedMetrics: (metrics) => set({ selectedMetrics: metrics }),
      
      setVoiceEnabled: (enabled) => set({ voiceEnabled: enabled }),
      
      setIsRecording: (recording) => set({ isRecording: recording }),
      
      setIsProcessing: (processing) => set({ isProcessing: processing }),
      
      setVoiceSettings: (settings) => set((state) => ({
        voiceSettings: { ...state.voiceSettings, ...settings }
      })),
      
      setFaqCategories: (categories) => set({ faqCategories: categories }),
      
      setSearchResults: (results) => set({ searchResults: results }),
      
      updateSettings: (newSettings) => set((state) => ({
        settings: { ...state.settings, ...newSettings }
      })),
      
      // Computed getters
      getUnreadMessages: () => {
        const { messages } = get();
        return messages.filter(msg => !msg.read);
      },
      
      getRecentDocuments: () => {
        const { documents } = get();
        return documents
          .sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt))
          .slice(0, 5);
      },
      
      getActiveSessions: () => {
        const { chatSessions } = get();
        return chatSessions.filter(session => session.active);
      },
      
      // Reset functions
      resetChat: () => set({
        chatSessions: [],
        currentSession: null,
        messages: []
      }),
      
      resetDocuments: () => set({
        documents: [],
        selectedDocument: null,
        uploadProgress: 0
      }),
      
      resetAnalytics: () => set({
        analyticsData: null,
        selectedMetrics: []
      }),
      
      resetAll: () => set({
        sidebarOpen: true,
        theme: 'light',
        loading: false,
        user: null,
        isAuthenticated: false,
        chatSessions: [],
        currentSession: null,
        messages: [],
        documents: [],
        selectedDocument: null,
        uploadProgress: 0,
        analyticsData: null,
        selectedMetrics: [],
        voiceEnabled: false,
        isRecording: false,
        isProcessing: false,
        voiceSettings: {
          language: 'en',
          voice: 'default',
          speed: 1.0,
          volume: 0.9
        },
        faqCategories: [],
        searchResults: [],
        settings: {
          autoSave: true,
          notifications: true,
          darkMode: false,
          language: 'en',
          timezone: 'UTC'
        }
      })
    }),
    {
      name: 'finmda-bot-store',
      partialize: (state) => ({
        theme: state.theme,
        settings: state.settings,
        voiceSettings: state.voiceSettings,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);

export { useAppStore };
