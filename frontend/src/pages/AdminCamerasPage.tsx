import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

import { fetchAdminCameras, registerCamera, startCamera, stopCamera } from '../lib/api';
import { useToastStore } from '../store/toast';

function getErrorMessage(error: unknown, fallback: string) {
  const candidate = error as { response?: { data?: { message?: string; error?: { message?: string } } }; message?: string };
  return candidate?.response?.data?.message || candidate?.response?.data?.error?.message || candidate?.message || fallback;
}

export function AdminCamerasPage() {
  const [cameras, setCameras] = useState<Array<Record<string, unknown>>>([]);
  const [workers, setWorkers] = useState<Array<Record<string, unknown>>>([]);
  const [cameraBusyId, setCameraBusyId] = useState<string | null>(null);
  const pushToast = useToastStore((s) => s.pushToast);

  const refresh = async () => {
    try {
      const c = await fetchAdminCameras();
      setCameras((c.cameras ?? []) as Array<Record<string, unknown>>);
      setWorkers((c.workers ?? []) as Array<Record<string, unknown>>);
    } catch (error) {
      pushToast(getErrorMessage(error, 'Failed to load camera config.'), 'error');
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const onRegisterCamera = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const cameraId = String(fd.get('camera_id') ?? '').trim();
    const source = String(fd.get('source') ?? '').trim();
    if (!cameraId || !source) {
      pushToast('Camera ID and source (RTSP/IP URL) are required.', 'error');
      return;
    }

    try {
      await registerCamera({
        camera_id: cameraId,
        camera_type: String(fd.get('camera_type') ?? 'wall_camera') === 'ceiling_camera' ? 'ceiling_camera' : 'wall_camera',
        source,
        location: String(fd.get('location') ?? '').trim() || undefined,
        gate_id: String(fd.get('gate_id') ?? '').trim() || undefined,
        direction: (String(fd.get('direction') ?? 'both') as 'entry' | 'exit' | 'both'),
        enabled: String(fd.get('enabled') ?? 'true') === 'true',
      });
      pushToast(`Camera ${cameraId} saved.`, 'success');
      e.currentTarget.reset();
      await refresh();
    } catch (error) {
      pushToast(getErrorMessage(error, 'Camera register/update failed.'), 'error');
    }
  };

  const cameraRunning = (cameraId: string) => {
    const st = workers.find((w) => String(w.camera_id) === cameraId);
    return Boolean(st?.running);
  };

  const onStartCamera = async (cameraId: string) => {
    setCameraBusyId(cameraId);
    try {
      await startCamera(cameraId);
      pushToast(`Camera ${cameraId} start requested.`, 'success');
      await refresh();
    } catch (error) {
      pushToast(getErrorMessage(error, `Failed to start ${cameraId}.`), 'error');
    } finally {
      setCameraBusyId(null);
    }
  };

  const onStopCamera = async (cameraId: string) => {
    setCameraBusyId(cameraId);
    try {
      await stopCamera(cameraId);
      pushToast(`Camera ${cameraId} stop requested.`, 'success');
      await refresh();
    } catch (error) {
      pushToast(getErrorMessage(error, `Failed to stop ${cameraId}.`), 'error');
    } finally {
      setCameraBusyId(null);
    }
  };

  return (
    <section className='stack-lg'>
      <article className='card'>
        <h2>Add Camera (RTSP/IP)</h2>
        <form className='stack form-grid' onSubmit={onRegisterCamera}>
          <input name='camera_id' placeholder='Camera ID (example: CA_1)' required />
          <select name='camera_type' defaultValue='wall_camera'>
            <option value='wall_camera'>wall_camera</option>
            <option value='ceiling_camera'>ceiling_camera</option>
          </select>
          <input name='source' placeholder='rtsp://user:pass@ip:554/stream' required />
          <input name='location' placeholder='Location (example: Main Entrance)' />
          <input name='gate_id' placeholder='Gate ID (example: GATE_A)' />
          <select name='direction' defaultValue='both'>
            <option value='entry'>entry</option>
            <option value='exit'>exit</option>
            <option value='both'>both</option>
          </select>
          <select name='enabled' defaultValue='true'>
            <option value='true'>enabled</option>
            <option value='false'>disabled</option>
          </select>
          <button className='primary-btn' type='submit'>Save Camera</button>
        </form>
      </article>

      <article className='card'>
        <h2>Camera Runtime Control (24x7)</h2>
        <div className='table-wrap'>
          <table>
            <thead>
              <tr><th>Camera ID</th><th>Type</th><th>Source</th><th>Enabled</th><th>Worker</th><th>Actions</th></tr>
            </thead>
            <tbody>
              {cameras.map((cam) => {
                const cameraId = String(cam.camera_id ?? '');
                const running = cameraRunning(cameraId);
                return (
                  <tr key={cameraId}>
                    <td>{cameraId}</td>
                    <td>{String(cam.camera_type ?? '')}</td>
                    <td>{String(cam.source ?? '')}</td>
                    <td>{String(cam.enabled ?? '')}</td>
                    <td>{running ? 'running' : 'stopped'}</td>
                    <td>
                      <div className='inline-actions'>
                        <button className='ghost-btn' disabled={cameraBusyId === cameraId} onClick={() => void onStartCamera(cameraId)} type='button'>
                          Start
                        </button>
                        <button className='ghost-btn' disabled={cameraBusyId === cameraId} onClick={() => void onStopCamera(cameraId)} type='button'>
                          Stop
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}
