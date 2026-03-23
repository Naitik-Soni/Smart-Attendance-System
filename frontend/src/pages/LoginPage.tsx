import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { fetchBootstrapStatus, loginRequest } from '../lib/api';
import { useAuthStore } from '../store/auth';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const setSession = useAuthStore((state) => state.setSession);

  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkingSetup, setCheckingSetup] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const requiresBootstrap = await fetchBootstrapStatus();
        if (requiresBootstrap) {
          navigate('/setup-admin', { replace: true });
          return;
        }
      } catch {
        setError('Could not verify system setup status.');
      } finally {
        setCheckingSetup(false);
      }
    })();
  }, [navigate]);

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
      <form className='auth-card auth-card-plain' onSubmit={onSubmit}>
        <p className='eyebrow'>Secure Login</p>
        <h2>Attendance Management System</h2>
        <p className='muted'>Enter your credentials to continue.</p>

        <label>User ID</label>
        <input
          autoComplete='username'
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder='User ID'
          required
        />

        <label>Password</label>
        <input
          autoComplete='current-password'
          type='password'
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder='Password'
          required
        />

        {error ? <p className='error'>{error}</p> : null}

        <button className='primary-btn' disabled={loading || checkingSetup} type='submit'>
          {loading || checkingSetup ? 'Please wait...' : 'Sign in'}
        </button>
      </form>
    </div>
  );
}
