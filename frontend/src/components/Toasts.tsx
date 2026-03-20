import { useToastStore } from '../store/toast';

export function Toasts() {
  const toasts = useToastStore((s) => s.toasts);
  const dismiss = useToastStore((s) => s.dismissToast);

  return (
    <div className='toasts'>
      {toasts.map((toast) => (
        <button
          key={toast.id}
          className={`toast toast-${toast.tone}`}
          onClick={() => dismiss(toast.id)}
          type='button'
        >
          {toast.message}
        </button>
      ))}
    </div>
  );
}
