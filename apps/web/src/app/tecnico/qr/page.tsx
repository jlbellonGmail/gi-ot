"use client";

import { theme } from "@/lib/theme";
import { ErrorBanner } from "@/components/ErrorBanner";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import jsQR from "jsqr";
import { api } from "@/lib/api";
import { Asset } from "@/lib/types";

export default function EscanearQRPage() {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState(true);

  async function handleDetected(qrCode: string) {
    setScanning(false);
    try {
      const asset = await api.get<Asset>(`/assets/qr/${encodeURIComponent(qrCode)}`);
      router.push(`/tecnico/nueva?asset_id=${asset.id}`);
    } catch {
      setError(`Código "${qrCode}" no corresponde a ningún activo registrado.`);
    }
  }

  useEffect(() => {
    if (!scanning) return;
    let stream: MediaStream | null = null;
    let frameId: number;
    let stopped = false;

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        tick();
      } catch {
        setError("No se pudo acceder a la cámara. Verificá los permisos del navegador.");
      }
    }

    function tick() {
      if (stopped) return;
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (video && canvas && video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const code = jsQR(imageData.data, imageData.width, imageData.height);
          if (code && code.data) {
            handleDetected(code.data);
            return;
          }
        }
      }
      frameId = requestAnimationFrame(tick);
    }

    start();
    return () => {
      stopped = true;
      if (frameId) cancelAnimationFrame(frameId);
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, [scanning]);

  return (
    <div>
      <h1 style={{ fontSize: "1.25rem", marginBottom: "0.25rem" }}>Escanear QR</h1>
      <p style={{ fontSize: "0.875rem", color: theme.textSecondary, marginBottom: "1rem" }}>
        Apuntá la cámara al código QR del activo.
      </p>

      {error && <ErrorBanner message={error} onRetry={() => { setError(null); setScanning(true); }} />}

      <div style={{ position: "relative", borderRadius: "0.75rem", overflow: "hidden", background: "#000" }}>
        <video ref={videoRef} playsInline muted style={{ width: "100%", display: scanning ? "block" : "none" }} />
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      <div style={{ marginTop: "1rem" }}>
        <a href="/tecnico" style={{ display: "block", textAlign: "center", padding: "0.875rem", background: theme.bg, color: theme.text, borderRadius: "0.5rem", textDecoration: "none" }}>
          Cancelar
        </a>
      </div>
    </div>
  );
}
