"use client";

import { useRef, useState, useEffect } from "react";

const baseUrl = "http://localhost:8000";
const emptyCoords = {
  x: null,
  y: null,
  w: null,
  h: null
};

export default function Home() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [videoStarted, setVideoStarted] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [snapshot, setSnapshot] = useState<string | null>(null);
  const [coords, setCoords] = useState(emptyCoords);

  const startVideo = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user'
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setVideoStarted(true);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`Failed to access camera: ${errorMessage}`);
      setVideoStarted(false);
    }
  };

  const stopVideo = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setVideoStarted(false);
    }

    if (snapshot != null) {
      URL.revokeObjectURL(snapshot);
      setSnapshot(null);
    }

    setCoords({
      x: null,
      y: null,
      w: null,
      h: null
    });
  };

  const captureFrame = async () => {
    if (!videoRef.current || !canvasRef.current)
      return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (!ctx)
      return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const baseImageUrl = canvas.toDataURL('image/png');
    const baseImageResponse = await fetch(baseImageUrl);
    if (!baseImageResponse.ok) 
      throw new Error(`Failed to fetch file: ${baseImageResponse.statusText}`);

    const baseImageBlob = await baseImageResponse.blob();
    const baseFile = new File([baseImageBlob], "image.png", { type: baseImageBlob.type });

    if (baseFile.size === 0)
      return;

    const formData = new FormData();
    formData.append("file", baseFile);

    const detectResponse = await fetch(baseUrl + "/detect-smile", {
      method: "POST",
      body: formData,
    });
    const detectJson = await detectResponse.json();
    setCoords(detectJson.coordinates);

    const params = new URLSearchParams({ id: detectJson.id });
    const imageResponse = await fetch(baseUrl + `/smile-image?${params}`);
    const imageBlob = await imageResponse.blob();

    let oldSnapshot = snapshot;
    const resultImageUrl = URL.createObjectURL(imageBlob);
    setSnapshot(resultImageUrl);
    if (oldSnapshot != null)
      URL.revokeObjectURL(oldSnapshot);
  };

  useEffect(() => {
    if (!videoStarted) 
      return;

    let doLoop = true;

    const runTaskWithDelay = async () => {
      while (doLoop) {
        await captureFrame();
        await sleep(250);
      }
    };

    runTaskWithDelay();

    return () => { doLoop = false; };
  }, [videoStarted]);

  useEffect(() => {
    stopVideo();
  }, []);

  const sleep = async (ms: number) => {
    return new Promise<void>(resolve => setTimeout(resolve, ms));
  }

  return (
    <div className="m-3">
      <div>
        <div className="p-5 rounded-xl shadow-lg">
          <h1 className="font-bold text-xl font-sans">😀  Smile Detector</h1>
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
          <p>Loading...</p>
        )}
        </div>
        <div className="w-1/2 bg-amber-50 rounded-xl p-5 ml-2">
          <h1>Coordinates</h1>
          <div className="ml-3">
            <p>x: {coords.x}</p>
            <p>y: {coords.y}</p>
            <p>w: {coords.w}</p>
            <p>h: {coords.h}</p>
          </div>
        </div>
      </div>
      )}
      {error && (
        <p>{error}</p>
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
