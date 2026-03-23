import { useEffect, useRef, useState } from 'react';

import { recognizeUpload } from '../lib/api';
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

export function OperatorScanPage() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [result, setResult] = useState<string>('');
  const [sourceId, setSourceId] = useState('BROWSER_CAM_1');
  const [busy, setBusy] = useState(false);
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
      pushToast('Webcam started for scan.', 'success');
    } catch {
      pushToast('Camera access failed.', 'error');
    }
  };

  const scanFrame = async () => {
    if (!videoRef.current || !canvasRef.current) {
      pushToast('Start camera before scanning.', 'error');
      return;
    }
    setBusy(true);
    try {
      const dataUrl = captureSquareFrame(videoRef.current, canvasRef.current);
      if (!dataUrl) {
        pushToast('Camera frame not ready yet.', 'error');
        return;
      }
      const file = dataUrlToFile(dataUrl, `${sourceId || 'browser_cam'}_scan.jpg`);
      const response = await recognizeUpload(file, 'upload_image', sourceId || 'BROWSER_CAM_1');
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
        <h2>Live Scan (Webcam)</h2>
        <p className='muted'>Capture a frame from browser webcam and send to recognition.</p>
        <div className='camera-actions'>
          <input value={sourceId} onChange={(e) => setSourceId(e.target.value)} placeholder='Source ID (example: BROWSER_CAM_1)' />
          <button className='ghost-btn' onClick={startCamera} type='button'>Start Webcam</button>
          <button className='primary-btn' disabled={busy} onClick={scanFrame} type='button'>{busy ? 'Scanning...' : 'Scan Now'}</button>
        </div>
        <video className='camera-video' ref={videoRef} muted playsInline />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </article>

      <article className='card'>
        <h2>Scan Response</h2>
        <pre className='pre'>{result || 'No scan response yet.'}</pre>
      </article>
    </section>
  );
}
