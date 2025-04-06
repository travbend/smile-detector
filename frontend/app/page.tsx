"use client";

import { useRef, useState, useEffect } from "react";

export default function Home() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean>(false);
  const [videoStarted, setVideoStarted] = useState<boolean>(false);
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
        setVideoStarted(true);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to access camera: ${errorMessage}`);
      setHasPermission(false);
      setVideoStarted(false);
    }
  };

  const stopVideo = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setHasPermission(false);
      setVideoStarted(false);
    }
  };

  const captureFrame = async () => {
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
        
        const imageUrl = canvas.toDataURL('image/png');
        const response = await fetch(imageUrl);
        if (!response.ok) 
          throw new Error(`Failed to fetch file: ${response.statusText}`);
  
        const fileBlob = await response.blob();
        const file = new File([fileBlob], "image.png", { type: fileBlob.type });
  
        const formData = new FormData();
        formData.append("file", file);
  
        const detectResponse = await fetch("http://localhost:8000/detect-smile", {
          method: "POST",
          body: formData,
        });

        const imageBlob = await detectResponse.blob();
        const resultImageUrl = URL.createObjectURL(imageBlob);
        setSnapshot(resultImageUrl);
      }
    }
  };

  useEffect(() => {
    if (!videoStarted) 
      return;

    const interval = setInterval(async () => {
      await captureFrame();
    }, 1000);

    return () => clearInterval(interval);
  }, [videoStarted]);

  return (
    <div className="m-3">
      <div>
        <div className="p-5 rounded-xl shadow-lg">
          <h1 className="font-bold text-xl font-sans">Smile Detector 😀</h1>
        </div>
      </div>
      <div className="flex justify-center mt-4">
        {!videoStarted ? (
          <button onClick={startVideo} className="w-80 p-4 rounded-xl bg-yellow-300 font-bold">Start Video</button>
        ) : (
          <button onClick={stopVideo} className="w-80 p-4 rounded-xl bg-yellow-300 font-bold">Stop Video</button>
        )}
      </div>
      {videoStarted && (
      <div className="flex mt-3 p-5">
        <div className="w-1/2">
        {snapshot ? (
          <img src={snapshot} alt="Captured frame" className="rounded-xl"/>
        ) : (
          <p>Testing</p>
        )}
        </div>
        <div className="w-1/2 bg-amber-50 rounded-xl p-5 ml-2">
          <h1>Coordinates</h1>
        </div>
      </div>
      )}
      <video
        className="hidden"
        ref={videoRef}
        autoPlay
        playsInline
      />
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}
