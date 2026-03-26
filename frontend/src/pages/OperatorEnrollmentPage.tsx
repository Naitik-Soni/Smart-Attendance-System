import { useEffect, useMemo, useRef, useState } from 'react';

import { enrollUpload } from '../lib/api';
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

  canvas.width = target;
  canvas.height = target;
  const ctx = canvas.getContext('2d');
  if (!ctx) return null;
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, target, target);
  const scale = Math.min(target / srcW, target / srcH);
  const drawW = Math.round(srcW * scale);
  const drawH = Math.round(srcH * scale);
  const dx = Math.floor((target - drawW) / 2);
  const dy = Math.floor((target - drawH) / 2);
  ctx.drawImage(video, 0, 0, srcW, srcH, dx, dy, drawW, drawH);
  return canvas.toDataURL('image/jpeg', 0.92);
}

function parseShotIndexFromMessage(message: string): number | null {
  const m = message.match(/webcam_shot_(\d+)\.jpg/i);
  if (!m) return null;
  const n = Number(m[1]);
  if (!Number.isFinite(n) || n < 1) return null;
  return n - 1;
}

export function OperatorEnrollmentPage() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [userId, setUserId] = useState('');
  const [shots, setShots] = useState<string[]>([]);
  const [cameraReady, setCameraReady] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const pushToast = useToastStore((s) => s.pushToast);

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const startCamera = async () => {
    try {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraReady(true);
      pushToast('Webcam started.', 'success');
    } catch {
      pushToast('Unable to access webcam.', 'error');
    }
  };

  const captureShot = () => {
    if (!videoRef.current || !canvasRef.current) return;
    if (shots.length >= 5) {
      pushToast('Maximum 5 shots reached.', 'info');
      return;
    }

    const shot = captureSquareFrame(videoRef.current, canvasRef.current);
    if (!shot) {
      pushToast('Camera frame not ready yet.', 'error');
      return;
    }
    setShots((prev) => [...prev, shot]);
    pushToast(`Shot ${shots.length + 1} captured.`, 'success');
  };

  const removeShot = (idx: number) => setShots((prev) => prev.filter((_, i) => i !== idx));

  const canFinalize = useMemo(() => userId.trim().length > 0 && shots.length >= 3 && shots.length <= 5, [shots.length, userId]);

  const finalizeEnrollment = async () => {
    if (!canFinalize) {
      pushToast('Need user id and 3-5 captured shots.', 'error');
      return;
    }

    setSubmitting(true);
    try {
      const files = shots.map((s, idx) => dataUrlToFile(s, `webcam_shot_${idx + 1}.jpg`));
      await enrollUpload(userId.trim(), files);
      pushToast(`Enrollment finalized for ${userId}.`, 'success');
      setShots([]);
    } catch (err: any) {
      const message = String(err?.response?.data?.message || 'Enrollment finalize failed.');
      const shotIdx = parseShotIndexFromMessage(message);
      if (shotIdx !== null && shotIdx >= 0 && shotIdx < shots.length) {
        setShots((prev) => prev.filter((_, i) => i !== shotIdx));
        pushToast(`Shot ${shotIdx + 1} removed automatically. Retake and finalize again.`, 'info');
      }
      pushToast(message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className='stack-lg'>
      <article className='card'>
        <h2>Face Enrollment</h2>
        <p className='muted'>Use browser webcam to capture 3 to 5 images and finalize enrollment.</p>
        <div className='camera-actions'>
          <input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder='User ID (example: emp_101)' />
          <button className='ghost-btn' onClick={startCamera} type='button'>Start Webcam</button>
          <button className='primary-btn' disabled={!cameraReady} onClick={captureShot} type='button'>Capture Shot</button>
          <button className='primary-btn' disabled={submitting} onClick={finalizeEnrollment} type='button'>
            {submitting ? 'Finalizing...' : 'Finalize Enrollment'}
          </button>
        </div>
        <video className='camera-video' ref={videoRef} muted playsInline />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        <p className='muted'>Captured shots: {shots.length} (required: 3 to 5)</p>
        {!canFinalize ? <p className='muted'>Finalize requires User ID and 3 to 5 valid face shots.</p> : null}
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
