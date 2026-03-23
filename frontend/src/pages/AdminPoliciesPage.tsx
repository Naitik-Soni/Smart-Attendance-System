import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

import { fetchPolicies, updatePolicies } from '../lib/api';
import { useToastStore } from '../store/toast';

type PolicyField = {
  key: string;
  label: string;
  help: string;
  min?: number;
  max?: number;
  step?: number;
  integer?: boolean;
};

const POLICY_FIELDS: PolicyField[] = [
  { key: 'recognition.threshold', label: 'Recognition Threshold', help: '0 to 1. Higher value means stricter matching.', min: 0, max: 1, step: 0.01 },
  { key: 'attendance.min_time_minutes', label: 'Minimum Work Minutes', help: 'Minutes needed to mark present.', min: 0, step: 1, integer: true },
  { key: 'retention.days', label: 'Retention Days', help: 'Days to keep attendance/face metadata.', min: 1, step: 1, integer: true },
  { key: 'camera.stream.sampling_fps', label: 'Camera Sampling FPS', help: 'Frames sampled per second from stream.', min: 1, step: 1, integer: true },
  { key: 'camera.wall.min_face_area_ratio', label: 'Min Face Area Ratio', help: '0 to 1. Minimum frame ratio for face area.', min: 0, max: 1, step: 0.01 },
  { key: 'enrollment.images.min_count', label: 'Enrollment Min Images', help: 'Minimum images required for enrollment.', min: 0, step: 1, integer: true },
  { key: 'enrollment.images.max_count', label: 'Enrollment Max Images', help: 'Maximum images accepted for enrollment.', min: 0, step: 1, integer: true },
  { key: 'quality.min_image_width', label: 'Min Image Width (px)', help: 'Minimum image width for quality checks.', min: 0, step: 1, integer: true },
  { key: 'quality.min_image_height', label: 'Min Image Height (px)', help: 'Minimum image height for quality checks.', min: 0, step: 1, integer: true },
  { key: 'quality.min_face_width_px', label: 'Min Face Width (px)', help: 'Minimum detected face width.', min: 0, step: 1, integer: true },
  { key: 'quality.min_face_height_px', label: 'Min Face Height (px)', help: 'Minimum detected face height.', min: 0, step: 1, integer: true },
  { key: 'quality.min_laplacian_variance', label: 'Min Laplacian Variance', help: 'Image sharpness threshold.', min: 0, step: 0.1 },
  { key: 'quality.max_yaw_degrees', label: 'Max Yaw Degrees', help: 'Maximum left/right face rotation.', min: 0, step: 1, integer: true },
  { key: 'quality.max_pitch_degrees', label: 'Max Pitch Degrees', help: 'Maximum up/down face rotation.', min: 0, step: 1, integer: true },
];

function getErrorMessage(error: unknown, fallback: string) {
  const candidate = error as { response?: { data?: { message?: string; error?: { message?: string } } }; message?: string };
  return candidate?.response?.data?.message || candidate?.response?.data?.error?.message || candidate?.message || fallback;
}

export function AdminPoliciesPage() {
  const [policyDraft, setPolicyDraft] = useState<Record<string, string>>({});
  const [savingPolicy, setSavingPolicy] = useState(false);
  const pushToast = useToastStore((s) => s.pushToast);

  useEffect(() => {
    void (async () => {
      try {
        const data = (await fetchPolicies()) ?? {};
        const nextDraft: Record<string, string> = {};
        POLICY_FIELDS.forEach((field) => {
          nextDraft[field.key] = String(data[field.key] ?? '');
        });
        setPolicyDraft(nextDraft);
      } catch (error) {
        pushToast(getErrorMessage(error, 'Failed to load policy config.'), 'error');
      }
    })();
  }, [pushToast]);

  const onSavePolicies = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const payload: Record<string, unknown> = {};

    for (const field of POLICY_FIELDS) {
      const raw = String(policyDraft[field.key] ?? '').trim();
      if (!raw) continue;
      const numeric = Number(raw);
      if (!Number.isFinite(numeric)) {
        pushToast(`${field.label}: enter a valid number.`, 'error');
        return;
      }
      if (typeof field.min === 'number' && numeric < field.min) {
        pushToast(`${field.label}: must be >= ${field.min}.`, 'error');
        return;
      }
      if (typeof field.max === 'number' && numeric > field.max) {
        pushToast(`${field.label}: must be <= ${field.max}.`, 'error');
        return;
      }
      if (field.integer && !Number.isInteger(numeric)) {
        pushToast(`${field.label}: must be a whole number.`, 'error');
        return;
      }
      payload[field.key] = numeric;
    }

    if (Object.keys(payload).length === 0) {
      pushToast('No policy values to save.', 'info');
      return;
    }

    setSavingPolicy(true);
    try {
      await updatePolicies(payload);
      pushToast('Policy values updated.', 'success');
    } catch (error) {
      pushToast(getErrorMessage(error, 'Policy update failed.'), 'error');
    } finally {
      setSavingPolicy(false);
    }
  };

  return (
    <section className='stack-lg'>
      <article className='card'>
        <h2>Policy Configuration</h2>
        <p className='muted'>Numeric policy settings only.</p>
        <form autoComplete='off' className='stack policy-grid' onSubmit={onSavePolicies}>
          {POLICY_FIELDS.map((field) => (
            <label className='policy-field' key={field.key}>
              <span className='policy-label'>{field.label}</span>
              <span className='policy-help'>{field.help}</span>
              <input
                autoComplete='off'
                type='number'
                min={field.min}
                max={field.max}
                step={field.step ?? 1}
                value={policyDraft[field.key] ?? ''}
                onChange={(e) => setPolicyDraft((prev) => ({ ...prev, [field.key]: e.target.value }))}
                required
              />
            </label>
          ))}
          <button className='primary-btn' disabled={savingPolicy} type='submit'>
            {savingPolicy ? 'Saving...' : 'Save Policies'}
          </button>
        </form>
      </article>
    </section>
  );
}
