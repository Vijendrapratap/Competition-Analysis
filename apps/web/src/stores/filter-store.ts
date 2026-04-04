import { create } from "zustand";

type FilterMode = "daily" | "weekly" | "monthly";

interface FilterStore {
  filterMode: FilterMode;
  setFilterMode: (mode: FilterMode) => void;
}

export const useFilterStore = create<FilterStore>((set) => ({
  filterMode: "weekly",
  setFilterMode: (mode) => set({ filterMode: mode }),
}));

export const useFilterMode = () => useFilterStore((s) => s.filterMode);
