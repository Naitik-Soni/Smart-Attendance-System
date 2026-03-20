import { NavLink, Outlet, useNavigate } from 'react-router-dom';

import { useAuthStore } from '../store/auth';
import { DemoGuide } from './DemoGuide';
import { Toasts } from './Toasts';

export function AppShell() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const onLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className='console-layout'>
      <aside className='sidebar'>
        <div className='brand'>
          <p>Smart Attendance</p>
          <h2>Enterprise Console</h2>
        </div>

        <nav className='nav'>
          {user?.role === 'admin' ? <NavLink to='/admin'>Admin Overview</NavLink> : null}

          {user?.role === 'operator' || user?.role === 'admin' ? <NavLink to='/operations/users'>User Management</NavLink> : null}
          {user?.role === 'operator' || user?.role === 'admin' ? <NavLink to='/operations/enrollment'>Face Enrollment</NavLink> : null}
          {user?.role === 'operator' || user?.role === 'admin' ? <NavLink to='/operations/scan'>Camera Scan</NavLink> : null}

          {user?.role === 'user' ? <NavLink to='/me'>My Attendance</NavLink> : null}
        </nav>

        <div className='sidebar-user'>
          <strong>{user?.name ?? 'User'}</strong>
          <span>{user?.role ?? 'user'}</span>
        </div>
      </aside>

      <div className='workspace'>
        <header className='workspace-head'>
          <div>
            <p className='eyebrow'>Secure Operations</p>
            <h1>Control Center</h1>
          </div>
          <button className='ghost-btn' onClick={onLogout}>Logout</button>
        </header>

        <main className='workspace-main'>
          <DemoGuide role={user?.role ?? 'user'} />
          <Outlet />
        </main>
      </div>
      <Toasts />
    </div>
  );
}
