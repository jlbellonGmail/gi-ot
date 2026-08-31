"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import styles from "./offline-status-banner.module.css";

export default function OfflineStatusBanner() {
  const [isOnline, setIsOnline] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const pathname = usePathname();

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    setIsOnline(navigator.onLine);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  useEffect(() => {
    const checkSyncStatus = async () => {
      try {
        const response = await fetch("/api/sync/status", { cache: "no-store" });
        if (response.ok) {
          const data = await response.json();
          setIsSyncing(data.syncing ?? false);
          setPendingCount(data.pendingCount ?? 0);
        }
      } catch {
        // Silencioso: si no hay endpoint de sync, no mostrar estado
      }
    };

    checkSyncStatus();
    const interval = setInterval(checkSyncStatus, 10000);
    return () => clearInterval(interval);
  }, [pathname]);

  if (isOnline && !isSyncing && pendingCount === 0) {
    return null;
  }

  return (
    <div className={styles.banner} role="status" aria-live="polite">
      {!isOnline && (
        <span className={styles.offline}>
          <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <path d="M1 1l22 22" />
            <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55" />
            <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39" />
            <path d="M10.71 5.05A16 16 0 0 1 22.58 9" />
            <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88" />
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
            <path d="M12 20h.01" />
          </svg>
          <span>Sin conexión</span>
        </span>
      )}

      {isSyncing && (
        <span className={styles.syncing}>
          <svg className={styles.iconSpinner} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="12" cy="12" r="10" strokeOpacity="0.25" />
            <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round" />
          </svg>
          <span>Sincronizando...</span>
        </span>
      )}

      {isOnline && pendingCount > 0 && !isSyncing && (
        <span className={styles.pending}>
          <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <path d="M12 8v4l3 3" />
            <circle cx="12" cy="12" r="10" />
          </svg>
          <span>{pendingCount} pendiente{pendingCount > 1 ? "s" : ""} de sincronización</span>
        </span>
      )}
    </div>
  );
}