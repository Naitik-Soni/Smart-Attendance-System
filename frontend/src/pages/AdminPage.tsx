import { useEffect, useMemo, useState } from 'react';

import { fetchOperators, fetchPolicies, fetchSystemHealth } from '../lib/api';
import { useToastStore } from '../store/toast';

export function AdminPage() {
  const [health, setHealth] = useState<Record<string, string>>({});
  const [policies, setPolicies] = useState<Record<string, unknown>>({});
  const [operators, setOperators] = useState<Array<Record<string, string>>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pushToast = useToastStore((s) => s.pushToast);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const [h, p, o] = await Promise.all([fetchSystemHealth(), fetchPolicies(), fetchOperators()]);
        setHealth(h.services ?? {});
        setPolicies(p ?? {});
        setOperators(o ?? []);
      } catch {
        setError('Failed to load admin dashboard data.');
        pushToast('Admin dashboard fetch failed.', 'error');
      } finally {
        setLoading(false);
      }
    })();
  }, [pushToast]);

  const healthyCount = useMemo(
    () => Object.values(health).filter((status) => String(status).toLowerCase() === 'healthy').length,
    [health],
  );

  const policyCount = Object.keys(policies).length;

  return (
    <section className='stack-lg'>
      <div className='metrics-grid'>
        <article className='metric-card'>
          <p>Services Healthy</p>
          <h3>{healthyCount}</h3>
        </article>
        <article className='metric-card'>
          <p>Total Services</p>
          <h3>{Object.keys(health).length}</h3>
        </article>
        <article className='metric-card'>
          <p>Policy Keys</p>
          <h3>{policyCount}</h3>
        </article>
        <article className='metric-card'>
          <p>Operators</p>
          <h3>{operators.length}</h3>
        </article>
      </div>

      <section className='grid'>
        <article className='card'>
          <h2>System Health</h2>
          {loading ? <p className='muted'>Loading health...</p> : null}
          {error ? <p className='error'>{error}</p> : null}
          <div className='badge-row'>
            {Object.entries(health).map(([service, status]) => (
              <span className={`status-badge ${String(status).toLowerCase()}`} key={service}>
                {service}: {status}
              </span>
            ))}
          </div>
        </article>

        <article className='card'>
          <h2>Operators</h2>
          <div className='table-wrap'>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {operators.map((op) => (
                  <tr key={op.operator_id}>
                    <td>{op.operator_id}</td>
                    <td>{op.name}</td>
                    <td>{op.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <article className='card'>
        <h2>Policy Snapshot</h2>
        <pre className='pre'>{JSON.stringify(policies, null, 2)}</pre>
      </article>
    </section>
  );
}
