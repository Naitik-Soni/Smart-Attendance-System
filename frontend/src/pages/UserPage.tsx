import { useEffect, useState } from 'react';

import { fetchAttendance } from '../lib/api';
import { useToastStore } from '../store/toast';

export function UserPage() {
  const [items, setItems] = useState<Array<Record<string, string>>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pushToast = useToastStore((s) => s.pushToast);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchAttendance();
        setItems(data ?? []);
      } catch {
        setError('Failed to load attendance history.');
        pushToast('Attendance fetch failed.', 'error');
      } finally {
        setLoading(false);
      }
    })();
  }, [pushToast]);

  return (
    <section className='stack-lg'>
      <article className='card'>
        <h2>My Attendance</h2>
        <p className='muted'>This is the only module available for normal users.</p>
        {loading ? <p className='muted'>Loading attendance...</p> : null}
        {error ? <p className='error'>{error}</p> : null}
        <div className='table-wrap'>
          <table>
            <thead>
              <tr><th>Date</th><th>Status</th><th>Method</th></tr>
            </thead>
            <tbody>
              {items.map((item, idx) => (
                <tr key={`${item.date}-${idx}`}>
                  <td>{item.date}</td>
                  <td>{item.status}</td>
                  <td>{item.method}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
