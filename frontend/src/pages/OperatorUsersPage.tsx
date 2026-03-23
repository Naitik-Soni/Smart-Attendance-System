import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';

import { createUser, deleteUser, fetchLogs, fetchUsers, markManualAttendance, updateUser } from '../lib/api';
import { useToastStore } from '../store/toast';

export function OperatorUsersPage() {
  const [users, setUsers] = useState<Array<Record<string, string>>>([]);
  const [logs, setLogs] = useState<Array<Record<string, string>>>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState<'create' | 'update' | 'delete' | 'manual' | null>(null);
  const [selectedUserId, setSelectedUserId] = useState('');
  const pushToast = useToastStore((s) => s.pushToast);

  const refresh = async () => {
    setLoading(true);
    try {
      const [u, l] = await Promise.all([fetchUsers(), fetchLogs()]);
      setUsers(u ?? []);
      setLogs(l ?? []);
      if (!selectedUserId && (u ?? []).length > 0) {
        setSelectedUserId(String((u ?? [])[0].user_id ?? ''));
      }
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

    setSubmitting('create');
    try {
      await createUser({
        user_id: userId,
        name,
        email: String(fd.get('email') ?? ''),
        password,
        role: 'user',
        status: String(fd.get('status') ?? 'active') === 'inactive' ? 'inactive' : 'active',
      });
      pushToast(`User ${userId} created.`, 'success');
      e.currentTarget.reset();
      await refresh();
      setSelectedUserId(userId);
    } catch {
      pushToast('Create user failed.', 'error');
    } finally {
      setSubmitting(null);
    }
  };

  const onUpdateUser = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const userId = String(fd.get('target_user_id') ?? '').trim();
    if (!userId) {
      pushToast('Select a user to update.', 'error');
      return;
    }

    const name = String(fd.get('name') ?? '').trim();
    const email = String(fd.get('email') ?? '').trim();
    const status = String(fd.get('status') ?? '').trim();
    const payload: { name?: string; email?: string; status?: 'active' | 'inactive' } = {};
    if (name) payload.name = name;
    if (email) payload.email = email;
    if (status === 'active' || status === 'inactive') payload.status = status;

    if (Object.keys(payload).length === 0) {
      pushToast('Provide at least one field to update.', 'info');
      return;
    }

    setSubmitting('update');
    try {
      await updateUser(userId, payload);
      pushToast(`User ${userId} updated.`, 'success');
      await refresh();
    } catch {
      pushToast('Update user failed.', 'error');
    } finally {
      setSubmitting(null);
    }
  };

  const onDeleteUser = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const userId = String(fd.get('delete_user_id') ?? '').trim();
    if (!userId) {
      pushToast('Select a user to delete.', 'error');
      return;
    }

    setSubmitting('delete');
    try {
      await deleteUser(userId);
      pushToast(`User ${userId} deleted.`, 'success');
      await refresh();
      if (selectedUserId === userId) {
        setSelectedUserId('');
      }
    } catch {
      pushToast('Delete user failed.', 'error');
    } finally {
      setSubmitting(null);
    }
  };

  const onManualAttendance = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const userId = String(fd.get('attendance_user_id') ?? '').trim();
    const timestamp = String(fd.get('timestamp') ?? '').trim();
    const status = String(fd.get('attendance_status') ?? 'present').trim();
    const reason = String(fd.get('reason') ?? '').trim();
    if (!userId || !timestamp) {
      pushToast('User and timestamp are required for manual attendance.', 'error');
      return;
    }

    setSubmitting('manual');
    try {
      await markManualAttendance([
        {
          user_id: userId,
          attendance_type: 'manual',
          status,
          timestamp: new Date(timestamp).toISOString(),
          reason: reason || undefined,
        },
      ]);
      pushToast(`Manual attendance marked for ${userId}.`, 'success');
      await refresh();
    } catch {
      pushToast('Manual attendance request failed.', 'error');
    } finally {
      setSubmitting(null);
    }
  };

  const filteredReport = useMemo(() => {
    if (!selectedUserId) return logs.slice(0, 20);
    return logs.filter((l) => String(l.entity_id ?? '').toLowerCase() === selectedUserId.toLowerCase()).slice(0, 20);
  }, [logs, selectedUserId]);

  const attendanceLogs = useMemo(
    () =>
      logs.filter((l) => {
        const action = String(l.action ?? '').toUpperCase();
        const entityType = String(l.entity_type ?? '').toLowerCase();
        return action.includes('ATTENDANCE') || entityType === 'attendance';
      }),
    [logs],
  );

  const filteredAttendanceLogs = useMemo(() => {
    if (!selectedUserId) return attendanceLogs;
    return attendanceLogs.filter((l) => String(l.entity_id ?? '').toLowerCase() === selectedUserId.toLowerCase());
  }, [attendanceLogs, selectedUserId]);

  const dailySummary = useMemo(() => {
    const map = new Map<string, { date: string; userId: string; manualMarked: number; autoMarked: number; totalEvents: number }>();
    filteredAttendanceLogs.forEach((row) => {
      const userId = String(row.entity_id ?? row.user_id ?? 'unknown');
      const createdAt = String(row.created_at ?? '');
      const action = String(row.action ?? '').toUpperCase();
      const date = createdAt ? createdAt.slice(0, 10) : 'unknown';
      const key = `${date}|${userId}`;
      const existing = map.get(key) ?? { date, userId, manualMarked: 0, autoMarked: 0, totalEvents: 0 };
      existing.totalEvents += 1;
      if (action === 'ATTENDANCE_MARKED') existing.manualMarked += 1;
      if (action === 'ATTENDANCE_AUTO_MARKED') existing.autoMarked += 1;
      map.set(key, existing);
    });
    return Array.from(map.values()).sort((a, b) => `${b.date}-${b.userId}`.localeCompare(`${a.date}-${a.userId}`)).slice(0, 40);
  }, [filteredAttendanceLogs]);

  const weeklySummary = useMemo(() => {
    const startOfWeek = (date: Date) => {
      const d = new Date(date);
      const day = d.getDay();
      const diff = day === 0 ? -6 : 1 - day;
      d.setDate(d.getDate() + diff);
      d.setHours(0, 0, 0, 0);
      return d;
    };

    const map = new Map<string, { weekStart: string; userId: string; manualMarked: number; autoMarked: number; totalEvents: number }>();
    filteredAttendanceLogs.forEach((row) => {
      const userId = String(row.entity_id ?? row.user_id ?? 'unknown');
      const createdAt = String(row.created_at ?? '');
      const action = String(row.action ?? '').toUpperCase();
      const parsed = createdAt ? new Date(createdAt) : null;
      const weekStart = parsed && !Number.isNaN(parsed.getTime()) ? startOfWeek(parsed).toISOString().slice(0, 10) : 'unknown';
      const key = `${weekStart}|${userId}`;
      const existing = map.get(key) ?? { weekStart, userId, manualMarked: 0, autoMarked: 0, totalEvents: 0 };
      existing.totalEvents += 1;
      if (action === 'ATTENDANCE_MARKED') existing.manualMarked += 1;
      if (action === 'ATTENDANCE_AUTO_MARKED') existing.autoMarked += 1;
      map.set(key, existing);
    });
    return Array.from(map.values()).sort((a, b) => `${b.weekStart}-${b.userId}`.localeCompare(`${a.weekStart}-${a.userId}`)).slice(0, 40);
  }, [filteredAttendanceLogs]);

  return (
    <section className='stack-lg ops-compact'>
      <section className='stack'>
        <article className='card'>
          <h2>Create User</h2>
          <form autoComplete='off' className='stack form-grid' onSubmit={onCreateUser}>
            <input aria-hidden='true' autoComplete='username' style={{ display: 'none' }} tabIndex={-1} />
            <input aria-hidden='true' autoComplete='new-password' style={{ display: 'none' }} tabIndex={-1} type='password' />
            <input autoComplete='off' name='user_id' placeholder='emp_101' required />
            <input autoComplete='off' name='name' placeholder='Employee/Student Name' required />
            <input autoComplete='off' name='email' placeholder='employee@org.com' />
            <input autoComplete='new-password' name='password' type='password' placeholder='Set Password' required />
            <select name='status' defaultValue='active'>
              <option value='active'>active</option>
              <option value='inactive'>inactive</option>
            </select>
            <button className='primary-btn' disabled={submitting === 'create'} type='submit'>
              {submitting === 'create' ? 'Creating...' : 'Create User'}
            </button>
          </form>
        </article>

        <article className='card'>
          <h2>Update User</h2>
          <form autoComplete='off' className='stack form-grid' onSubmit={onUpdateUser}>
            <select name='target_user_id' value={selectedUserId} onChange={(e) => setSelectedUserId(e.target.value)}>
              <option value=''>Select user</option>
              {users.map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  {u.user_id}
                </option>
              ))}
            </select>
            <input autoComplete='off' name='name' placeholder='New name (optional)' />
            <input autoComplete='off' name='email' placeholder='New email (optional)' />
            <select name='status' defaultValue=''>
              <option value=''>status unchanged</option>
              <option value='active'>active</option>
              <option value='inactive'>inactive</option>
            </select>
            <button className='ghost-btn' disabled={submitting === 'update'} type='submit'>
              {submitting === 'update' ? 'Updating...' : 'Update User'}
            </button>
          </form>
        </article>
      </section>

      <section className='stack'>
        <article className='card'>
          <h2>Manual Attendance</h2>
          <form autoComplete='off' className='stack form-grid' onSubmit={onManualAttendance}>
            <select name='attendance_user_id' defaultValue={selectedUserId}>
              <option value=''>Select user</option>
              {users.map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  {u.user_id}
                </option>
              ))}
            </select>
            <select name='attendance_status' defaultValue='present'>
              <option value='present'>present</option>
              <option value='late'>late</option>
              <option value='absent'>absent</option>
              <option value='half_day'>half_day</option>
            </select>
            <input name='timestamp' type='datetime-local' required />
            <input name='reason' placeholder='Reason (optional)' />
            <button className='primary-btn' disabled={submitting === 'manual'} type='submit'>
              {submitting === 'manual' ? 'Marking...' : 'Mark Manual Attendance'}
            </button>
          </form>
        </article>

        <article className='card'>
          <h2>Delete User</h2>
          <form autoComplete='off' className='stack form-grid' onSubmit={onDeleteUser}>
            <select name='delete_user_id' defaultValue=''>
              <option value=''>Select user</option>
              {users.map((u) => (
                <option key={u.user_id} value={u.user_id}>
                  {u.user_id}
                </option>
              ))}
            </select>
            <button className='ghost-btn' disabled={submitting === 'delete'} type='submit'>
              {submitting === 'delete' ? 'Deleting...' : 'Delete User'}
            </button>
          </form>
        </article>
      </section>

      <section className='stack'>
        <article className='card'>
          <h2>Users ({users.length})</h2>
          {loading ? <p className='muted'>Loading users...</p> : null}
          <div className='table-wrap'>
            <table>
              <thead>
                <tr><th>User ID</th><th>Name</th><th>Role</th><th>Status</th></tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.user_id}>
                    <td>{u.user_id}</td>
                    <td>{u.name}</td>
                    <td>{u.role}</td>
                    <td>{u.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className='card'>
          <h2>Daily Attendance Summary</h2>
          <p className='muted'>Grouped by date and user{selectedUserId ? ` for ${selectedUserId}` : ''}.</p>
          <div className='table-wrap'>
            <table>
              <thead>
                <tr><th>Date</th><th>User ID</th><th>Manual</th><th>Auto</th><th>Total Events</th></tr>
              </thead>
              <tbody>
                {dailySummary.map((row) => (
                  <tr key={`${row.date}-${row.userId}`}>
                    <td>{row.date}</td>
                    <td>{row.userId}</td>
                    <td>{row.manualMarked}</td>
                    <td>{row.autoMarked}</td>
                    <td>{row.totalEvents}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section className='stack'>
        <article className='card'>
          <h2>Weekly Attendance Summary</h2>
          <p className='muted'>Grouped by week start (Monday) and user{selectedUserId ? ` for ${selectedUserId}` : ''}.</p>
          <div className='table-wrap'>
            <table>
              <thead>
                <tr><th>Week Start</th><th>User ID</th><th>Manual</th><th>Auto</th><th>Total Events</th></tr>
              </thead>
              <tbody>
                {weeklySummary.map((row) => (
                  <tr key={`${row.weekStart}-${row.userId}`}>
                    <td>{row.weekStart}</td>
                    <td>{row.userId}</td>
                    <td>{row.manualMarked}</td>
                    <td>{row.autoMarked}</td>
                    <td>{row.totalEvents}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className='card'>
          <h2>Attendance/Audit Raw Logs</h2>
          <p className='muted'>Latest detailed logs{selectedUserId ? ` for ${selectedUserId}` : ''}.</p>
          <div className='table-wrap'>
            <table>
              <thead>
                <tr><th>Action</th><th>Entity</th><th>Entity ID</th><th>Time</th></tr>
              </thead>
              <tbody>
                {filteredReport.map((l) => (
                  <tr key={`${l.id}-${l.action}-${l.created_at}`}>
                    <td>{l.action}</td>
                    <td>{l.entity_type}</td>
                    <td>{l.entity_id}</td>
                    <td>{l.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>
    </section>
  );
}
