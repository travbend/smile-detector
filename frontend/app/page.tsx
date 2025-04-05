"use client";

import { useRef, useState } from "react";

export default function Home() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean>(false);
  const [snapshot, setSnapshot] = useState<string | null>(null);

  const startVideo = async () => {
    // TODO: clean up the video stream when the component unmounts

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user'
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setHasPermission(true);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to access camera: ${errorMessage}`);
      setHasPermission(false);
    }
  };

  const stopVideo = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setHasPermission(false);
    }
  }

  const captureFrame = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw current video frame to canvas
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to data URL and store it
        const imageData = canvas.toDataURL('image/png');
        setSnapshot(imageData);
      }
    }
  };

  return (
    <div>
      <button onClick={startVideo}>Start Video</button>
      <button onClick={stopVideo}>Stop Video</button>
      <button onClick={captureFrame}>Capture Frame</button>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{ width: '100%', maxWidth: '640px' }}
      />
      <canvas ref={canvasRef} className="hidden" />
      {snapshot && (
        <div>
          <h3>Captured Frame:</h3>
          <img src={snapshot} alt="Captured frame" style={{ maxWidth: '100%' }} />
        </div>
      )}
    </div>
  );
}
