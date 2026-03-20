import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className='auth-wrap'>
      <div className='auth-card'>
        <h1>Page not found</h1>
        <p className='muted'>The page does not exist.</p>
        <Link className='primary-btn inline-btn' to='/'>Go to dashboard</Link>
      </div>
    </div>
  );
}

