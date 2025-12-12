import { useEffect, useRef } from "react";
import { Button } from "@/components/ui_custom/button";
import { useSseProgress } from "@/hooks/useSseProgress";
import { toast } from "sonner";
import { BaseModal } from "@/components/modals/BaseModal";

type Props = {
  jobId: string;
  title?: string;
  apiBase?: string;
  onHide: () => void;
  onCancel?: () => Promise<void>;
  onComplete?: () => void;
  open?: boolean;
};

export function ProgressModal({ jobId, title = "Processing", apiBase = "", onHide, onCancel, onComplete, open = true }: Props) {
  const { snapshot, error } = useSseProgress(jobId, apiBase, title);
  const handledRef = useRef<string | null>(null);

  const isDone = snapshot?.done || snapshot?.error || snapshot?.cancel_requested;
  const showCancel = onCancel && !isDone;
  const primaryLabel = isDone ? "OK" : "Hide";

  useEffect(() => {
    if (!snapshot) return;

    // Reset guard when job changes
    if (handledRef.current !== snapshot.job_id && handledRef.current !== jobId) {
      handledRef.current = null;
    }

    const finished = snapshot.done || snapshot.cancel_requested || snapshot.error;
    const alreadyHandled = handledRef.current === snapshot.job_id || handledRef.current === jobId;

    if (!snapshot) return;
    if (snapshot.error) {
      toast.error(snapshot.error);
    }
    if (finished && !alreadyHandled) {
      handledRef.current = snapshot.job_id || jobId || "handled";
    }
    if (snapshot.done && !alreadyHandled) {
      toast.success(`${title} dokončené`);
      onComplete?.();
    }
    if (snapshot.cancel_requested && !alreadyHandled) {
      toast.info(`${title} zrušené`);
      onComplete?.();
    }
  }, [snapshot, title, onComplete, jobId]);

  const pct = snapshot?.pct != null ? Math.min(Math.max(snapshot.pct, 0), 100) : null;
  const note = snapshot?.note;

  const handleCancel = async () => {
    try {
      if (onCancel) await onCancel();
      toast.info("Cancel requested");
    } catch (err: any) {
      toast.error(err?.message || "Cancel failed");
    }
  };

  return (
    <BaseModal open={open} onClose={onHide} size="md">
      <div className="p-4 space-y-4">
        <div className="text-lg font-semibold">{title}</div>
        <div className="text-sm text-muted-foreground break-words">
          Job: {jobId}
        </div>
        <div className="space-y-2">
          <div className="text-sm">
            {pct != null ? `${pct.toFixed(1)}%` : "Prebieha..."} {note ? `• ${note}` : ""}
          </div>
          <div className="h-3 w-full bg-muted rounded-full overflow-hidden">
            {pct != null ? (
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${pct}%` }}
              />
            ) : (
              <div className="h-full w-1/3 bg-primary animate-pulse" />
            )}
          </div>
        </div>

        {error && <div className="text-xs text-red-500">{error}</div>}

        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onHide}>{primaryLabel}</Button>
          {showCancel && (
            <Button variant="danger" onClick={handleCancel}>Cancel</Button>
          )}
        </div>
      </div>
    </BaseModal>
  );
}

