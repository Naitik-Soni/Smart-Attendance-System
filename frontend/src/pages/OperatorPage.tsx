import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

import { createUser, enrollUpload, fetchLogs, fetchUsers, recognizeUpload } from '../lib/api';
import { useToastStore } from '../store/toast';

export function OperatorPage() {
  const [users, setUsers] = useState<Array<Record<string, string>>>([]);
  const [logs, setLogs] = useState<Array<Record<string, string>>>([]);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState<string | null>(null);
  const pushToast = useToastStore((s) => s.pushToast);

  useEffect(() => {
    void refresh();
  }, []);

  const refresh = async () => {
    setLoading(true);
    try {
      const [u, l] = await Promise.all([fetchUsers(), fetchLogs()]);
      setUsers(u ?? []);
      setLogs(l ?? []);
    } catch {
      pushToast('Failed to refresh users/logs.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const onCreateUser = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const userId = String(fd.get('user_id') ?? '').trim();
    const name = String(fd.get('name') ?? '').trim();
    const password = String(fd.get('password') ?? '');

    if (!userId || !name || password.length < 8) {
      setStatus('User ID, name, and password(>=8) are required.');
      pushToast('Validation failed for user creation.', 'error');
      return;
    }

    setSubmitting('create');
    try {
      await createUser({ user_id: userId, name, email: String(fd.get('email') ?? ''), password, role: 'user', status: 'active' });
      setStatus('User created successfully.');
      pushToast(`User ${userId} created.`, 'success');
      e.currentTarget.reset();
      await refresh();
    } catch {
      setStatus('Create user failed.');
      pushToast('Create user failed.', 'error');
    } finally {
      setSubmitting(null);
    }
  };

  const onEnroll = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const userId = String(fd.get('enroll_user_id') ?? '').trim();
    const files = (fd.getAll('images') as File[]).filter((f) => f.size > 0);
    if (!userId || files.length < 3 || files.length > 5) {
      setStatus('Enrollment needs user id and 3-5 images.');
      pushToast('Enrollment validation failed (3-5 images).', 'error');
      return;
    }

    setSubmitting('enroll');
    try {
      await enrollUpload(userId, files);
      setStatus('Enrollment uploaded successfully.');
      pushToast(`Enrollment completed for ${userId}.`, 'success');
    } catch {
      setStatus('Enrollment failed.');
      pushToast('Enrollment request failed.', 'error');
    } finally {
      setSubmitting(null);
    }
  };

  const onRecognize = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const file = fd.get('recognize_image') as File;
    if (!file || file.size === 0) {
      setStatus('Please select a recognition image.');
      pushToast('Recognition image missing.', 'error');
      return;
    }

    setSubmitting('recognize');
    try {
      await recognizeUpload(file);
      setStatus('Recognition request completed.');
      pushToast('Recognition completed.', 'success');
      await refresh();
    } catch {
      setStatus('Recognition failed.');
      pushToast('Recognition request failed.', 'error');
    } finally {
      setSubmitting(null);
    }
  };

  return (
    <section className='stack-lg'>
      <section className='grid'>
        <article className='card'>
          <h2>Create User</h2>
          <form className='stack' onSubmit={onCreateUser}>
            <input name='user_id' placeholder='emp_101' required />
            <input name='name' placeholder='Employee Name' required />
            <input name='email' placeholder='employee@org.com' />
            <input name='password' type='password' placeholder='StrongPass123' required />
            <button className='primary-btn' disabled={submitting === 'create'} type='submit'>{submitting === 'create' ? 'Creating...' : 'Create'}</button>
          </form>
        </article>

        <article className='card'>
          <h2>Enroll Face</h2>
          <p className='muted'>Upload 3 to 5 images for each employee.</p>
          <form className='stack' onSubmit={onEnroll}>
            <input name='enroll_user_id' placeholder='emp_101' required />
            <input name='images' type='file' accept='image/*' multiple required />
            <button className='primary-btn' disabled={submitting === 'enroll'} type='submit'>{submitting === 'enroll' ? 'Uploading...' : 'Enroll'}</button>
          </form>
        </article>

        <article className='card'>
          <h2>Recognize Face</h2>
          <form className='stack' onSubmit={onRecognize}>
            <input name='recognize_image' type='file' accept='image/*' required />
            <button className='primary-btn' disabled={submitting === 'recognize'} type='submit'>{submitting === 'recognize' ? 'Processing...' : 'Recognize'}</button>
          </form>
        </article>
      </section>

      {status ? <p className='status'>{status}</p> : null}

      <section className='grid'>
        <article className='card'>
          <h2>Users ({users.length})</h2>
          {loading ? <p className='muted'>Loading users...</p> : null}
          <div className='table-wrap'>
            <table>
              <thead>
                <tr><th>User ID</th><th>Role</th><th>Status</th></tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.user_id}><td>{u.user_id}</td><td>{u.role}</td><td>{u.status}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className='card'>
          <h2>Recent Logs ({logs.length})</h2>
          {loading ? <p className='muted'>Loading logs...</p> : null}
          <div className='table-wrap'>
            <table>
              <thead>
                <tr><th>Action</th><th>Time</th></tr>
              </thead>
              <tbody>
                {logs.slice(0, 12).map((l) => (
                  <tr key={`${l.id}-${l.action}`}><td>{l.action}</td><td>{l.created_at}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </section>
  );
}
