import { useEffect, useMemo, useState } from 'react';

import { fetchOperators, fetchSystemHealth } from '../lib/api';
import { useToastStore } from '../store/toast';

export function AdminPage() {
  const [health, setHealth] = useState<Record<string, string>>({});
  const [operatorCount, setOperatorCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const pushToast = useToastStore((s) => s.pushToast);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      try {
        const [h, o] = await Promise.all([fetchSystemHealth(), fetchOperators()]);
        setHealth(h.services ?? {});
        setOperatorCount((o ?? []).length);
      } catch {
        pushToast('Failed to load admin overview data.', 'error');
      } finally {
        setLoading(false);
      }
    })();
  }, [pushToast]);

  const healthyCount = useMemo(
    () => Object.values(health).filter((status) => String(status).toLowerCase() === 'healthy').length,
    [health],
  );

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
          <p>Operators</p>
          <h3>{operatorCount}</h3>
        </article>
      </div>

      <article className='card'>
        <h2>System Health</h2>
        {loading ? <p className='muted'>Loading health...</p> : null}
        <div className='badge-row tight-badge-row'>
          {Object.entries(health).map(([service, status]) => (
            <span className={`status-badge ${String(status).toLowerCase()}`} key={service}>
              {service}: {status}
            </span>
          ))}
        </div>
      </article>

    </section>
  );
}
