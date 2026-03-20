import { useEffect, useMemo, useRef, useState } from 'react';

import { type CameraConfig, type CameraWorker, enrollUpload, fetchOperatorCameras } from '../lib/api';
import { useToastStore } from '../store/toast';

function dataUrlToFile(dataUrl: string, name: string): File {
  const [meta, content] = dataUrl.split(',');
  const mime = meta.match(/data:(.*);base64/)?.[1] ?? 'image/png';
  const binary = atob(content);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return new File([bytes], name, { type: mime });
}

function captureSquareFrame(video: HTMLVideoElement, canvas: HTMLCanvasElement): string | null {
  const target = 720;
  const srcW = video.videoWidth;
  const srcH = video.videoHeight;
  if (!srcW || !srcH) return null;

  const size = Math.min(srcW, srcH);
  const sx = Math.floor((srcW - size) / 2);
  const sy = Math.floor((srcH - size) / 2);

  canvas.width = target;
  canvas.height = target;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.drawImage(video, sx, sy, size, size, 0, 0, target, target);
  return canvas.toDataURL('image/jpeg', 0.92);
}

function statusFor(cam: CameraConfig, workers: CameraWorker[]): 'running' | 'idle' | 'disabled' {
  if (cam.enabled === false) return 'disabled';
  const worker = workers.find((w) => w.camera_id === cam.camera_id);
  return worker?.running ? 'running' : 'idle';
}

export function OperatorEnrollmentPage() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [userId, setUserId] = useState('');
  const [shots, setShots] = useState<string[]>([]);
  const [cameraReady, setCameraReady] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [cameras, setCameras] = useState<CameraConfig[]>([]);
  const [workers, setWorkers] = useState<CameraWorker[]>([]);
  const [cameraId, setCameraId] = useState('');
  const pushToast = useToastStore((s) => s.pushToast);

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    const loadCameras = async (silent = false) => {
      try {
        const payload = await fetchOperatorCameras();
        if (cancelled) return;
        setCameras(payload.cameras);
        setWorkers(payload.workers);
        if (!cameraId && payload.cameras.length > 0) {
          setCameraId(payload.cameras[0].camera_id);
        }
      } catch {
        if (!silent) pushToast('Could not load registered cameras. Manual ID available.', 'info');
      }
    };

    void loadCameras();
    const timer = setInterval(() => void loadCameras(true), 10000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [pushToast, cameraId]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraReady(true);
      pushToast('Camera started.', 'success');
    } catch {
      pushToast('Unable to access camera.', 'error');
    }
  };

  const captureShot = () => {
    if (!videoRef.current || !canvasRef.current) return;
    if (shots.length >= 5) {
      pushToast('Maximum 5 shots reached.', 'info');
      return;
    }

    const v = videoRef.current;
    const c = canvasRef.current;
    const shot = captureSquareFrame(v, c);
    if (!shot) {
      pushToast('Camera frame not ready yet.', 'error');
      return;
    }
    setShots((prev) => [...prev, shot]);
    pushToast(`Shot ${shots.length + 1} captured from ${cameraId || 'camera'}.`, 'success');
  };

  const removeShot = (idx: number) => setShots((prev) => prev.filter((_, i) => i !== idx));

  const canFinalize = useMemo(() => userId.trim().length > 0 && shots.length >= 3 && shots.length <= 5, [shots.length, userId]);

  const selectedStatus = useMemo(() => {
    const selected = cameras.find((c) => c.camera_id === cameraId);
    return selected ? statusFor(selected, workers) : 'idle';
  }, [cameraId, cameras, workers]);

  const finalizeEnrollment = async () => {
    if (!canFinalize) {
      pushToast('Need employee id and 3-5 captured shots.', 'error');
      return;
    }

    setSubmitting(true);
    try {
      const files = shots.map((s, idx) => dataUrlToFile(s, `${cameraId || 'cam'}_shot_${idx + 1}.jpg`));
      await enrollUpload(userId.trim(), files);
      pushToast(`Enrollment finalized for ${userId}.`, 'success');
      setShots([]);
    } catch {
      pushToast('Enrollment finalize failed.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className='stack-lg'>
      <article className='card'>
        <h2>Camera Enrollment</h2>
        <p className='muted'>Capture employee images one-by-one from camera, then finalize enrollment.</p>
        <div className='camera-actions'>
          <input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder='Employee ID (e.g., emp_101)' />

          {cameras.length > 0 ? (
            <select value={cameraId} onChange={(e) => setCameraId(e.target.value)}>
              {cameras.map((cam) => (
                <option key={cam.camera_id} value={cam.camera_id}>
                  {cam.camera_id} ({cam.camera_type ?? 'camera'}{cam.location ? ` - ${cam.location}` : ''})
                </option>
              ))}
            </select>
          ) : (
            <input value={cameraId} onChange={(e) => setCameraId(e.target.value)} placeholder='Camera ID (manual fallback)' />
          )}

          <button className='ghost-btn' onClick={startCamera} type='button'>Start Camera</button>
          <button className='primary-btn' disabled={!cameraReady} onClick={captureShot} type='button'>Capture Shot</button>
          <button className='primary-btn' disabled={!canFinalize || submitting} onClick={finalizeEnrollment} type='button'>
            {submitting ? 'Finalizing...' : 'Finalize Enrollment'}
          </button>
        </div>
        <video className='camera-video' ref={videoRef} muted playsInline />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        <div className='camera-meta-row'>
          <p className='muted'>Source camera: {cameraId || 'not selected'} | Captured shots: {shots.length} (required: 3 to 5)</p>
          <span className={`status-badge ${selectedStatus}`}>status: {selectedStatus}</span>
        </div>
      </article>

      <article className='card'>
        <h2>Camera Status</h2>
        <div className='camera-status-grid'>
          {cameras.map((cam) => {
            const st = statusFor(cam, workers);
            return (
              <div className='camera-status-item' key={cam.camera_id}>
                <strong>{cam.camera_id}</strong>
                <span className='muted'>{cam.location || cam.camera_type || 'camera'}</span>
                <span className={`status-badge ${st}`}>{st}</span>
              </div>
            );
          })}
        </div>
      </article>

      <article className='card'>
        <h2>Captured Shots</h2>
        <div className='shot-grid'>
          {shots.map((shot, idx) => (
            <div className='shot-card' key={`${idx}-${shot.slice(0, 20)}`}>
              <img alt={`shot ${idx + 1}`} src={shot} />
              <button className='ghost-btn' onClick={() => removeShot(idx)} type='button'>Remove</button>
            </div>
          ))}
        </div>
      </article>
    </section>
  );
}
