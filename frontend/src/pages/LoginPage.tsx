import { useState } from 'react';
import type { FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { loginRequest } from '../lib/api';
import { useAuthStore } from '../store/auth';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const setSession = useAuthStore((state) => state.setSession);

  const [userId, setUserId] = useState('admin1');
  const [password, setPassword] = useState('StrongPass123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await loginRequest(userId, password);
      setSession({
        accessToken: data.tokens.access_token,
        refreshToken: data.tokens.refresh_token,
        user: data.user,
      });
      const target = (location.state as { from?: { pathname?: string } })?.from?.pathname ?? '/';
      navigate(target, { replace: true });
    } catch {
      setError('Login failed. Check user id and password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='auth-wrap'>
      <form className='auth-card' onSubmit={onSubmit}>
        <p className='eyebrow'>Smart Attendance</p>
        <h1>Welcome back</h1>
        <p className='muted'>Minimal demo frontend connected to your backend APIs.</p>

        <label>User ID</label>
        <input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder='admin1' required />

        <label>Password</label>
        <input type='password' value={password} onChange={(e) => setPassword(e.target.value)} required />

        {error ? <p className='error'>{error}</p> : null}

        <button className='primary-btn' disabled={loading} type='submit'>
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </div>
  );
}


