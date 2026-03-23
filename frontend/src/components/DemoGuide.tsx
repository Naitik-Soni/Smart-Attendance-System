type DemoGuideProps = {
  role: 'admin' | 'operator' | 'user';
};

export function DemoGuide({ role }: DemoGuideProps) {
  const stepsByRole: Record<DemoGuideProps['role'], string[]> = {
    admin: [
      'Review system health and policy baseline.',
      'Review operator and user activity from audit logs.',
    ],
    operator: [
      'Create or update employee/student accounts in User Management.',
      'Mark manual attendance when needed for approved exceptions.',
      'Review attendance/audit report for selected users.',
      'Open Face Enrollment and capture 3-5 camera shots.',
      'Finalize enrollment for the employee.',
      'Use Camera Scan module for live recognition.',
    ],
    user: [
      'Login using your assigned user ID and password.',
      'View attendance history only.',
    ],
  };

  const steps = stepsByRole[role];

  return (
    <article className='guide-card'>
      <div>
        <p className='eyebrow'>Role Workflow</p>
        <h2>Suggested Actions</h2>
      </div>
      <ol>
        {steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
    </article>
  );
}
