import { create } from "zustand";

export type ThemeMode = "light" | "dark" | "system";

interface UIState {
  themeMode: ThemeMode;
  sidebarCollapsed: boolean;
  selectedDashboardTab: string;
  setThemeMode: (mode: ThemeMode) => void;
  toggleSidebar: () => void;
  setSelectedDashboardTab: (tab: string) => void;
}

// Helper to load theme from Local Storage or default to system
const getSavedThemeMode = (): ThemeMode => {
  const saved = localStorage.getItem("csap-theme-mode");
  if (saved === "light" || saved === "dark" || saved === "system") {
    return saved;
  }
  return "system";
};

export const useUIStore = create<UIState>((set) => ({
  themeMode: getSavedThemeMode(),
  sidebarCollapsed: false,
  selectedDashboardTab: "summary",

  setThemeMode: (mode) => {
    localStorage.setItem("csap-theme-mode", mode);
    set({ themeMode: mode });
  },

  toggleSidebar: () => {
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  },

  setSelectedDashboardTab: (tab) => {
    set({ selectedDashboardTab: tab });
  },
}));
