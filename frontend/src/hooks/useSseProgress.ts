import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

type ProgressSnapshot = {
  job_id?: string;
  name?: string;
  completed?: number;
  total?: number;
  pct?: number;
  eta_seconds?: number | null;
  elapsed_seconds?: number | null;
  note?: string | null;
  done?: boolean;
  cancel_requested?: boolean;
  error?: string;
};

const TOAST_INTERVAL_MS = 15000;

type StoredJob = { jobId: string; title?: string; startedAt: number };
const LS_KEY = "generator_jobs";

function loadStoredJobs(): StoredJob[] {
  try {
    const raw = localStorage.getItem(LS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed;
  } catch {}
  return [];
}

function saveStoredJobs(jobs: StoredJob[]) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(jobs));
  } catch {}
}

export function useSseProgress(jobId: string | null, baseUrl = "", title?: string) {
  const [snapshot, setSnapshot] = useState<ProgressSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const sourceRef = useRef<EventSource | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(jobId);
  const lastSnapshotRef = useRef<ProgressSnapshot | null>(null);

  useEffect(() => {
    // pick jobId from arg or stored
    if (!jobId) {
      const stored = loadStoredJobs();
      if (stored.length > 0) {
        setActiveJobId(stored[stored.length - 1].jobId);
      }
    } else {
      setActiveJobId(jobId);
    }
  }, [jobId]);

  useEffect(() => {
    if (!activeJobId) return;
    const jobs = loadStoredJobs();
    if (!jobs.find((j) => j.jobId === activeJobId)) {
      jobs.push({ jobId: activeJobId, title, startedAt: Date.now() });
      saveStoredJobs(jobs);
    }

    const url = `${baseUrl}/api/generator/progress/${activeJobId}/stream/`;
    const es = new EventSource(url, { withCredentials: true });
    sourceRef.current = es;
    setConnected(true);

    es.onmessage = (ev) => {
      try {
        const data: ProgressSnapshot = JSON.parse(ev.data);
        setSnapshot(data);
        lastSnapshotRef.current = data;
        const finished = data.done || data.cancel_requested || data.error;
        if (finished) {
          // Close stream immediately to prevent duplicate events / loops
          es.close();
          setConnected(false);
          const jobs = loadStoredJobs().filter((j) => j.jobId !== activeJobId);
          saveStoredJobs(jobs);
        }
      } catch (err) {
        setError("Invalid progress payload");
      }
    };
    es.onerror = (err) => {
      const last = lastSnapshotRef.current;
      const finished = last && (last.done || last.cancel_requested || last.error);
      if (!finished) {
        console.error("EventSource failed:", err);
        setError("SSE connection error");
      }
      es.close();
      setConnected(false);
    };

    return () => {
      es.close();
      setConnected(false);
    };
  }, [activeJobId, baseUrl, title]);

  useEffect(() => {
    if (!snapshot) return;
    
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    // Don't start heartbeat if job is finished
    const finished = snapshot.done || snapshot.cancel_requested || snapshot.error;
    if (finished) {
      return;
    }
    
    // periodic toast heartbeat (only for running jobs)
    intervalRef.current = setInterval(() => {
      const current = lastSnapshotRef.current;
      if (!current) return;
      
      // Stop heartbeat if job finished
      const isFinished = current.done || current.cancel_requested || current.error;
      if (isFinished) {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        return;
      }
      
      const pct = current.pct != null ? `${current.pct.toFixed(1)}%` : "…";
      const note = current.note ? ` • ${current.note}` : "";
      toast.info(`Job ${current.name || current.job_id}: ${pct}${note}`);
    }, TOAST_INTERVAL_MS);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [snapshot]);

  return { snapshot, error, connected };
}

