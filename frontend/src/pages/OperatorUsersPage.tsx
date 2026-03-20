import { createUser, fetchLogs, fetchUsers } from '../lib/api';
import { useToastStore } from '../store/toast';
import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

export function OperatorUsersPage() {
  const [users, setUsers] = useState<Array<Record<string, string>>>([]);
  const [logs, setLogs] = useState<Array<Record<string, string>>>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const pushToast = useToastStore((s) => s.pushToast);

  const refresh = async () => {
    setLoading(true);
    try {
      const [u, l] = await Promise.all([fetchUsers(), fetchLogs()]);
      setUsers(u ?? []);
      setLogs(l ?? []);
    } catch {
      pushToast('Failed to load users module data.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const onCreateUser = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const userId = String(fd.get('user_id') ?? '').trim();
    const name = String(fd.get('name') ?? '').trim();
    const password = String(fd.get('password') ?? '');
    if (!userId || !name || password.length < 8) {
      pushToast('Enter user id, name, and password >= 8 chars.', 'error');
      return;
    }

    setSubmitting(true);
    try {
      await createUser({
        user_id: userId,
        name,
        email: String(fd.get('email') ?? ''),
        password,
        role: 'user',
        status: 'active',
      });
      pushToast(`User ${userId} created.`, 'success');
      e.currentTarget.reset();
      await refresh();
    } catch {
      pushToast('Create user failed.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className='stack-lg'>
      <article className='card'>
        <h2>User Management</h2>
        <p className='muted'>Create and manage employee accounts. Enrollment is handled in a separate module.</p>
        <form className='stack form-grid' onSubmit={onCreateUser}>
          <input name='user_id' placeholder='emp_101' required />
          <input name='name' placeholder='Employee Name' required />
          <input name='email' placeholder='employee@org.com' />
          <input name='password' type='password' placeholder='StrongPass123' required />
          <button className='primary-btn' disabled={submitting} type='submit'>{submitting ? 'Creating...' : 'Create User'}</button>
        </form>
      </article>

      <section className='grid'>
        <article className='card'>
          <h2>Users ({users.length})</h2>
          {loading ? <p className='muted'>Loading users...</p> : null}
          <div className='table-wrap'>
            <table>
              <thead><tr><th>User ID</th><th>Name</th><th>Role</th><th>Status</th></tr></thead>
              <tbody>
                {users.map((u) => <tr key={u.user_id}><td>{u.user_id}</td><td>{u.name}</td><td>{u.role}</td><td>{u.status}</td></tr>)}
              </tbody>
            </table>
          </div>
        </article>

        <article className='card'>
          <h2>Recent Audit Logs</h2>
          <div className='table-wrap'>
            <table>
              <thead><tr><th>Action</th><th>Entity</th><th>Time</th></tr></thead>
              <tbody>
                {logs.slice(0, 12).map((l) => <tr key={`${l.id}-${l.action}`}><td>{l.action}</td><td>{l.entity_type}</td><td>{l.created_at}</td></tr>)}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </section>
  );
}
