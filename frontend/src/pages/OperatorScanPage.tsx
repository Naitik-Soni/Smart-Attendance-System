import { useEffect, useMemo, useRef, useState } from 'react';

import { type CameraConfig, type CameraWorker, fetchOperatorCameras, recognizeUpload } from '../lib/api';
import { useToastStore } from '../store/toast';

function dataUrlToFile(dataUrl: string, name: string): File {
  const [meta, content] = dataUrl.split(',');
  const mime = meta.match(/data:(.*);base64/)?.[1] ?? 'image/jpeg';
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
  return canvas.toDataURL('image/jpeg', 0.9);
}

function statusFor(cam: CameraConfig, workers: CameraWorker[]): 'running' | 'idle' | 'disabled' {
  if (cam.enabled === false) return 'disabled';
  const worker = workers.find((w) => w.camera_id === cam.camera_id);
  return worker?.running ? 'running' : 'idle';
}

export function OperatorScanPage() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [result, setResult] = useState<string>('');
  const [cameras, setCameras] = useState<CameraConfig[]>([]);
  const [workers, setWorkers] = useState<CameraWorker[]>([]);
  const [cameraId, setCameraId] = useState('ENTRY_GATE_1');
  const [busy, setBusy] = useState(false);
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
      pushToast('Camera started for scan.', 'success');
    } catch {
      pushToast('Camera access failed.', 'error');
    }
  };

  const selectedStatus = useMemo(() => {
    const selected = cameras.find((c) => c.camera_id === cameraId);
    return selected ? statusFor(selected, workers) : 'idle';
  }, [cameraId, cameras, workers]);

  const scanFrame = async () => {
    if (!videoRef.current || !canvasRef.current) {
      pushToast('Start camera before scanning.', 'error');
      return;
    }
    setBusy(true);
    try {
      const v = videoRef.current;
      const c = canvasRef.current;
      const dataUrl = captureSquareFrame(v, c);
      if (!dataUrl) {
        pushToast('Camera frame not ready yet.', 'error');
        return;
      }
      const file = dataUrlToFile(dataUrl, `${cameraId || 'cam'}_scan.jpg`);
      const response = await recognizeUpload(file, 'wall_camera', cameraId || 'ENTRY_GATE_1');
      setResult(JSON.stringify(response, null, 2));
      pushToast('Scan completed.', 'success');
    } catch {
      pushToast('Scan request failed.', 'error');
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className='stack-lg'>
      <article className='card'>
        <h2>Live Camera Scan</h2>
        <p className='muted'>Capture a frame from connected camera and send to recognition pipeline.</p>
        <div className='camera-actions'>
          {cameras.length > 0 ? (
            <select value={cameraId} onChange={(e) => setCameraId(e.target.value)}>
              {cameras.map((cam) => (
                <option key={cam.camera_id} value={cam.camera_id}>
                  {cam.camera_id} ({cam.camera_type ?? 'camera'}{cam.location ? ` - ${cam.location}` : ''})
                </option>
              ))}
            </select>
          ) : (
            <input value={cameraId} onChange={(e) => setCameraId(e.target.value)} placeholder='Camera ID' />
          )}
          <button className='ghost-btn' onClick={startCamera} type='button'>Start Camera</button>
          <button className='primary-btn' disabled={busy} onClick={scanFrame} type='button'>{busy ? 'Scanning...' : 'Scan Now'}</button>
        </div>
        <video className='camera-video' ref={videoRef} muted playsInline />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        <div className='camera-meta-row'>
          <p className='muted'>Selected camera: {cameraId || 'not selected'}</p>
          <span className={`status-badge ${selectedStatus}`}>status: {selectedStatus}</span>
        </div>
      </article>

      <article className='card'>
        <h2>Scan Response</h2>
        <pre className='pre'>{result || 'No scan response yet.'}</pre>
      </article>
    </section>
  );
}
