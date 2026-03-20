import { create } from 'zustand';

type Role = 'admin' | 'operator' | 'user';

type User = {
  user_id: string;
  role: Role;
  name: string;
};

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  setSession: (payload: { accessToken: string; refreshToken: string; user: User }) => void;
  logout: () => void;
};

const initialAccess = localStorage.getItem('sas_access_token');
const initialRefresh = localStorage.getItem('sas_refresh_token');
const initialUser = localStorage.getItem('sas_user');

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: initialAccess,
  refreshToken: initialRefresh,
  user: initialUser ? (JSON.parse(initialUser) as User) : null,
  setSession: ({ accessToken, refreshToken, user }) => {
    localStorage.setItem('sas_access_token', accessToken);
    localStorage.setItem('sas_refresh_token', refreshToken);
    localStorage.setItem('sas_user', JSON.stringify(user));
    localStorage.setItem('sas_role', user.role);
    set({ accessToken, refreshToken, user });
  },
  logout: () => {
    localStorage.removeItem('sas_access_token');
    localStorage.removeItem('sas_refresh_token');
    localStorage.removeItem('sas_user');
    localStorage.removeItem('sas_role');
    set({ accessToken: null, refreshToken: null, user: null });
  },
}));
