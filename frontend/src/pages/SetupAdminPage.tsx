import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';

import { bootstrapAdminRequest, fetchBootstrapStatus } from '../lib/api';
import { useAuthStore } from '../store/auth';

export function SetupAdminPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((state) => state.setSession);

  const [loadingStatus, setLoadingStatus] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const required = await fetchBootstrapStatus();
        if (!required) {
          navigate('/login', { replace: true });
          return;
        }
      } catch {
        setError('Could not verify bootstrap status.');
      } finally {
        setLoadingStatus(false);
      }
    })();
  }, [navigate]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const fd = new FormData(event.currentTarget);
    const payload = {
      org_name: String(fd.get('org_name') ?? '').trim(),
      org_legal_name: String(fd.get('org_legal_name') ?? '').trim(),
      org_code: String(fd.get('org_code') ?? '').trim(),
      user_id: String(fd.get('user_id') ?? '').trim(),
      password: String(fd.get('password') ?? ''),
      name: String(fd.get('name') ?? '').trim(),
      email: String(fd.get('email') ?? '').trim() || undefined,
    };

    if (!payload.org_name || !payload.org_legal_name || !payload.org_code || !payload.user_id || !payload.name || payload.password.length < 8) {
      setError('Fill all required fields. Password must be at least 8 characters.');
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const data = await bootstrapAdminRequest(payload);
      setSession({
        accessToken: data.tokens.access_token,
        refreshToken: data.tokens.refresh_token,
        user: data.user,
      });
      navigate('/admin/overview', { replace: true });
    } catch {
      setError('Admin setup failed. Check values and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loadingStatus) {
    return (
      <div className='auth-wrap'>
        <div className='auth-card auth-card-plain'>
          <h2>Preparing Admin Setup...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className='auth-wrap'>
      <form autoComplete='off' className='auth-card auth-card-plain' onSubmit={onSubmit}>
        <p className='eyebrow'>Initial Setup</p>
        <h2>Create First Admin</h2>
        <p className='muted'>No admin account exists yet. Configure organization and primary admin.</p>

        <input autoComplete='off' name='org_name' placeholder='Organization Name' required />
        <input autoComplete='off' name='org_legal_name' placeholder='Organization Legal Name' required />
        <input autoComplete='off' name='org_code' placeholder='Organization Code' required />
        <input autoComplete='off' name='name' placeholder='Admin Full Name' required />
        <input autoComplete='off' name='user_id' placeholder='Admin User ID' required />
        <input autoComplete='off' name='email' placeholder='Admin Email (optional)' />
        <input autoComplete='new-password' name='password' type='password' placeholder='Set Admin Password' required />

        {error ? <p className='error'>{error}</p> : null}

        <button className='primary-btn' disabled={submitting} type='submit'>
          {submitting ? 'Creating Admin...' : 'Create Admin & Continue'}
        </button>
      </form>
    </div>
  );
}
