import { useEffect, useMemo, useState, useCallback } from "react";
import { MyTable } from "@/components/MyTable";
import type { MyTableConfig } from "@/components/MyTable";
import { PageHeader } from "@/components/PageHeader";
import { PageFooter } from "@/components/PageFooter";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { getMutatingHeaders } from "@/security/csrf";
import { Button } from "@/components/ui_custom/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { MultiSelect } from "@/components/ui_custom/multi-select";
import { ProgressModal } from "@/components/modals/ProgressModal";
import { BaseModal } from "@/components/modals/BaseModal";
import { apiGenerate, apiClearAllState, apiCancelJob } from "./hooks/useGeneratorApi";
import { useRef } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL as string | undefined;

type GenerateInputProps = {
  value: number;
  disabled: boolean;
  onDebouncedChange: (val: number) => void;
};

function GenerateInput({ value, disabled, onDebouncedChange }: GenerateInputProps) {
  const [localVal, setLocalVal] = useState<number>(value);

  useEffect(() => {
    setLocalVal(value);
  }, [value]);

  useEffect(() => {
    const timer = setTimeout(() => {
      onDebouncedChange(Math.max(0, localVal || 0));
    }, 500);
    return () => clearTimeout(timer);
  }, [localVal]); // DON'T add onDebouncedChange - causes infinite loop

  return (
    <input
      className="h-8 w-full rounded-md border border-input bg-background px-2 text-sm"
      type="number"
      min={0}
      value={localVal}
      disabled={disabled}
      onChange={(e) => setLocalVal(Number(e.target.value))}
    />
  );
}

type GeneratorRow = {
  id: string;
  key: string;
  label: string;
  model: string;
  count: number;
  parents: string[];
  children: string[];
  can_generate: boolean;
  default_count?: number;
};

const apiUrl = (path: string) => (API_BASE ? `${API_BASE}${path}` : path);
const INGEST_ENDPOINT = "http://127.0.0.1:7242/ingest/d3c6e42e-1222-49d9-b844-4ce8f03a2cc8";
let ingestDisabled = false;
const safeLog = (payload: Record<string, any>) => {
  if (ingestDisabled) return;
  fetch(INGEST_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).catch(() => {
    ingestDisabled = true;
  });
};

export default function GeneratorPage() {
  const { csrfToken } = useAuth();
  const [reloadKey, setReloadKey] = useState(0);
  const [assignTagsInputs, setAssignTagsInputs] = useState<Record<string, number>>({});
  const [removeTagsInputs] = useState<Record<string, number>>({});
  
  // Load from localStorage on mount
  const [generateCounts, setGenerateCounts] = useState<Record<string, number>>(() => {
    try {
      const stored = localStorage.getItem('sopira-generator-counts');
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  });
  const [selectedModelsForTags, setSelectedModelsForTags] = useState<string[]>([]);
  const [applyToAllObjects, setApplyToAllObjects] = useState<boolean>(true);
  const [selectedObjectIds, setSelectedObjectIds] = useState<string[]>([]);
  const [generatorModels, setGeneratorModels] = useState<GeneratorRow[]>([]);
  const [modelsLoading, setModelsLoading] = useState<boolean>(false);
  const [objectOptions, setObjectOptions] = useState<{ label: string; value: string }[]>([]);
  const [objectsLoading, setObjectsLoading] = useState<boolean>(false);
  const [progressJobId, setProgressJobId] = useState<string | null>(null);
  const [progressTitle, setProgressTitle] = useState<string>("Processing");
  const [progressVisible, setProgressVisible] = useState<boolean>(false);
  const [progressCompleted, setProgressCompleted] = useState(false);
  const hasRefreshedRef = useRef(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const generateCountsRef = useRef<Record<string, number>>(generateCounts);
  const setGenerateCountsRef = useRef(setGenerateCounts);

  // Keep refs in sync with state
  useEffect(() => {
    generateCountsRef.current = generateCounts;
    setGenerateCountsRef.current = setGenerateCounts;
  }, [generateCounts, setGenerateCounts]);

  // Stable callback that won't change between renders
  const updateGenerateCount = useCallback((id: string, value: number) => {
    setGenerateCountsRef.current((prev) => {
      const updated = { ...prev, [id]: Math.max(0, value || 0) };
      // Write directly to localStorage
      try {
        localStorage.setItem('sopira-generator-counts', JSON.stringify(updated));
      } catch (e) {
        console.warn('Failed to save to localStorage:', e);
      }
      return updated;
    });
  }, []); // Empty deps = stable reference

  const triggerRefreshOnce = () => {
    if (hasRefreshedRef.current) return;
    hasRefreshedRef.current = true;
    setReloadKey((k) => k + 1);
  };

  const startProgress = (jobId: string, title: string) => {
    hasRefreshedRef.current = false;
    setProgressJobId(jobId);
    setProgressTitle(title);
    setProgressVisible(true);
    setProgressCompleted(false);
  };

  const handleClearAll = () => {
    setShowClearConfirm(true);
    // #region agent log
    safeLog({sessionId:'debug-session',runId:'run1',hypothesisId:'H1',location:'GeneratorPage:handleClearAll',message:'clear-all dialog opened',data:{},timestamp:Date.now()});
    // #endregion
  };

  const confirmClearAll = async () => {
    // #region agent log
    safeLog({sessionId:'debug-session',runId:'run1',hypothesisId:'H1',location:'GeneratorPage:handleClearAll',message:'clear-all confirmed',data:{},timestamp:Date.now()});
    // #endregion
    setShowClearConfirm(false);
    try {
      const data = await apiClearAllState();
      // #region agent log
      safeLog({sessionId:'debug-session',runId:'run1',hypothesisId:'H1',location:'GeneratorPage:handleClearAll',message:'clear-all response',data:{job_id:data?.job_id ?? null,keys:Object.keys(data||{})},timestamp:Date.now()});
      // #endregion
      if (data.job_id) {
        startProgress(data.job_id, "Clear all");
      } else {
        // #region agent log
        safeLog({sessionId:'debug-session',runId:'run1',hypothesisId:'H1',location:'GeneratorPage:handleClearAll',message:'clear-all no job_id -> refresh immediately',data:{},timestamp:Date.now()});
        // #endregion
        triggerRefreshOnce();
      }
      toast.success("Mazanie spustené.");
    } catch (err: any) {
      // #region agent log
      safeLog({sessionId:'debug-session',runId:'run1',hypothesisId:'H1',location:'GeneratorPage:handleClearAll',message:'clear-all error',data:{error:err?.message||String(err)},timestamp:Date.now()});
      // #endregion
      toast.error(err.message || "Mazanie zlyhalo");
    }
  };

  const handleAssignTags = async () => {
    if (selectedModelsForTags.length === 0) {
      toast.error('Vyber aspoň jeden model pre tagy');
      return;
    }
    if (!applyToAllObjects && selectedModelsForTags.length !== 1) {
      toast.error('Pre konkrétne objekty vyber len jeden model');
      return;
    }

    try {
      for (const modelKey of selectedModelsForTags) {
        const tagsPerObject = assignTagsInputs[modelKey] || 1;
        const objectIdsPayload = applyToAllObjects ? null : selectedObjectIds;

        const res = await fetch(apiUrl('/api/generator/tags/assign/'), {
          method: 'POST',
          credentials: 'include',
          headers: getMutatingHeaders(),
          body: JSON.stringify({
            model_key: modelKey,
            count_per_object: tagsPerObject,
            object_ids: objectIdsPayload,
          }),
        });
        
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || 'Nepodarilo sa priradiť tagy');
        }
      }

      toast.success(`Pridanie tagov pre ${selectedModelsForTags.length} modelov dokončené`);
      setReloadKey(prev => prev + 1);
    } catch (err: any) {
      toast.error(err.message || 'Pridávanie tagov zlyhalo');
    }
  };

  const handleRemoveTags = async () => {
    if (selectedModelsForTags.length === 0) {
      toast.error('Vyber aspoň jeden model pre tagy');
      return;
    }
    if (!applyToAllObjects && selectedModelsForTags.length !== 1) {
      toast.error('Pre konkrétne objekty vyber len jeden model');
      return;
    }

    try {
      for (const modelKey of selectedModelsForTags) {
        const tagsPerObject = removeTagsInputs[modelKey];
        const objectIdsPayload = applyToAllObjects ? null : selectedObjectIds;

        const res = await fetch(apiUrl('/api/generator/tags/remove/'), {
          method: 'POST',
          credentials: 'include',
          headers: getMutatingHeaders(),
          body: JSON.stringify({
            model_key: modelKey,
            count_per_object: tagsPerObject,
            object_ids: objectIdsPayload,
          }),
        });
        
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || 'Nepodarilo sa odstrániť tagy');
        }
      }

      toast.success(`Odstránenie tagov pre ${selectedModelsForTags.length} modelov dokončené`);
      setReloadKey(prev => prev + 1);
    } catch (err: any) {
      toast.error(err.message || 'Odstraňovanie tagov zlyhalo');
    }
  };

  const handleGenerate = async (modelKey: string, count: number) => {
    const safeCount = count && count > 0 ? count : 1;
    hasRefreshedRef.current = false;
    try {
      const data = await apiGenerate(modelKey, safeCount);
      if (data.job_id) {
        startProgress(data.job_id, `Generate ${modelKey}`);
      } else {
        toast.success(`Vygenerovaných ${data.created} záznamov`);
        triggerRefreshOnce();
      }
    } catch (err: any) {
      toast.error(err.message || "Generovanie zlyhalo");
    }
  };

  const config = useMemo<MyTableConfig<GeneratorRow>>(() => {
    const baseEndpoint = apiUrl("/api/generator/models/");
    const endpointWithReload = `${baseEndpoint}?reload=${reloadKey}`;

    return {
      tableName: "Generator",
      apiEndpoint: endpointWithReload,
      storageKey: "generator-table",
      pageHeader: { visible: false },
      pageFooter: { visible: false },
      inlineEdit: { enabled: false },
      globalSearch: { enabled: true, placeholder: "Hľadať model" },
      toolbarVisibility: {
        filters: true,
        columns: true,
        compact: true,
        add: false,
        csv: true,
        xlsx: true,
        pdf: false,
        reset: true,
        save: false,
        editAll: false,
        delete: false,
        share: false,
        search: true,
      },
      headerVisibility: {
        title: true,
        stats: true,
        pagination: true,
        pageSize: true,
        search: true,
        toolbar: true,
      },
      pagination: {
        //defaultPageSize: 5,
        //pageSizeOptions: [5, 10, 25, 50, 100],
        custom: true,
      },
      filters: { persistence: true, fields: [] },
      columns: {
        enabled: true,
        persistence: true,
        fields: {
          actions: [true, true], // viditeľný a v columns paneli
          label: [true, true],
          count: [true, true],
          relations: [true, false],
          generate: [true, true],
        },
        defaultOrder: ["actions", "label", "count", "relations", "generate"],
      },
      actions: { 
        edit: false, 
        delete: false, 
        expand: false, 
        inlineShare: false, 
        customActions: [
          {
            label: "Generate",
            variant: "default",
            onClick: (_row: GeneratorRow) => {}, // rendering je nižšie v customCellRenderers.actions
          },
        ], 
      },
      rowSelection: { enabled: false },
      fields: [
        { key: "label", header: "Názov modelu", type: "text", size: 200, editableInline: false, sortable: true },
        { key: "count", header: "Aktuálny počet", type: "number", size: 120, editableInline: false, sortable: true, decimals: 0, alignRight: true },
        { key: "relations", header: "Relácie", type: "text", size: 260, editableInline: false, sortable: false, filterable: false },
        { key: "generate", header: "Generate N", type: "number", size: 140, editableInline: false, sortable: false, filterable: false, decimals: 0, min: 0 },
      ],
      customColumns: [],
      customCellRenderers: {
        actions: (row) => {
          const r = row as GeneratorRow;
          const count = generateCountsRef.current[r.id] ?? r.default_count ?? 1;
          const disabled = !r.can_generate;
          return (
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="default"
                disabled={disabled}
                className="h-8 px-3 text-sm"
                onClick={() => handleGenerate(r.key, count)}
              >
                Generate
              </Button>
            </div>
          );
        },
        count: (row) => Math.trunc((row as GeneratorRow).count),
        label: (row) => (row as GeneratorRow).label,
        generate: (row) => {
          const r = row as GeneratorRow;
          const val = generateCountsRef.current[r.id] ?? r.default_count ?? 1;
          return (
            <GenerateInput
              value={val}
              disabled={!r.can_generate}
              onDebouncedChange={(next) => updateGenerateCount(r.id, next)}
            />
          );
        },
      },
    };
  }, [reloadKey, csrfToken, updateGenerateCount]);

  useEffect(() => {
    const fetchModels = async () => {
      setModelsLoading(true);
      try {
        const res = await fetch(apiUrl("/api/generator/models/"), {
          credentials: "include",
        });
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || "Nepodarilo sa načítať modely");
        }
        const data = await res.json();
        setGeneratorModels(Array.isArray(data) ? data : []);
        setSelectedModelsForTags((prev) =>
          prev.filter((key) => data.find((row: any) => row.key === key))
        );
        
        // Merge defaults with existing localStorage values
        setGenerateCounts((prevCounts) => {
          let hasChanges = false;
          const newCounts = { ...prevCounts };
          data.forEach((row: any) => {
            // Only set default if it's not already in state/localStorage
            if (newCounts[row.id] === undefined) {
              newCounts[row.id] = row.default_count || 1;
              hasChanges = true;
            }
          });
          // Only return new object if something changed, otherwise return same reference
          return hasChanges ? newCounts : prevCounts;
        });
      } catch (err: any) {
        toast.error(err.message || "Chyba pri načítaní modelov");
      } finally {
        setModelsLoading(false);
      }
    };
    fetchModels();
  }, [reloadKey]);

  useEffect(() => {
    if (selectedModelsForTags.length !== 1 || applyToAllObjects) {
      setObjectOptions([]);
      setSelectedObjectIds([]);
      return;
    }

    const fetchObjects = async () => {
      setObjectsLoading(true);
      try {
        const url = apiUrl(
          `/api/generator/objects/?model_key=${encodeURIComponent(selectedModelsForTags[0])}`
        );
        const res = await fetch(url, {
          credentials: "include",
        });
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.error || data.detail || "Nepodarilo sa načítať objekty");
        }
        const data = await res.json();
        const options = (data.objects || []).map((obj: any) => ({
          label: obj.label || String(obj.id),
          value: String(obj.id),
        }));
        setObjectOptions(options);
      } catch (err: any) {
        toast.error(err.message || "Chyba pri načítaní objektov");
      } finally {
        setObjectsLoading(false);
      }
    };

    fetchObjects();
  }, [selectedModelsForTags, applyToAllObjects, reloadKey]);

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader
        showLogo
        showMenu
      />

      <div className="rounded-lg border border-border bg-card shadow-sm">
        <MyTable<GeneratorRow> config={config} />
      </div>

      {/* Tag Management Section */}
      <div className="rounded-lg border border-border bg-card shadow-sm p-6 space-y-4">
        <h3 className="text-lg font-semibold">Správa tagov</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Model Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Model</label>
            <MultiSelect
              value={selectedModelsForTags}
              onValueChange={(vals) => {
                setSelectedModelsForTags(vals);
                if (vals.length !== 1) {
                  setApplyToAllObjects(true);
                }
              }}
              options={generatorModels.map((row) => ({
                label: row.label,
                value: row.key,
              }))}
              placeholder={modelsLoading ? "Načítavam..." : "Vyber modely"}
              disabled={modelsLoading}
            />
          </div>

          {/* Tags per object */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Tagy na objekt</label>
            <Input
              type="number"
              min="1"
              value={
                selectedModelsForTags.length === 1
                  ? assignTagsInputs[selectedModelsForTags[0]] || 1
                  : 1
              }
              onChange={(e) => setAssignTagsInputs(prev => ({
                ...prev,
                [selectedModelsForTags[0] ?? '']: Math.max(1, Number(e.target.value) || 1)
              }))}
              placeholder="Počet tagov"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Apply to all checkbox */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="apply-to-all"
              checked={applyToAllObjects}
              onCheckedChange={(checked) =>
                setApplyToAllObjects(
                  checked === true || selectedModelsForTags.length !== 1
                )
              }
              disabled={selectedModelsForTags.length !== 1}
            />
            <label htmlFor="apply-to-all" className="text-sm font-medium">
              Aplikovať na všetky objekty
              {selectedModelsForTags.length !== 1 ? " (len pri jednom modeli)" : ""}
            </label>
          </div>

          {/* Object selection (when not applying to all) */}
          {!applyToAllObjects && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Špecifické objekty (ID)</label>
              <MultiSelect
                value={selectedObjectIds}
                onValueChange={setSelectedObjectIds}
                placeholder={objectsLoading ? "Načítavam objekty..." : "Vyber objekty"}
                options={objectOptions}
              />
            </div>
          )}
        </div>

        <div className="flex flex-wrap gap-4 justify-start items-center">
          <Button onClick={handleAssignTags}>
            Pridať tagy
          </Button>
          <Button variant="danger" onClick={handleRemoveTags}>
            Odstrániť tagy
          </Button>
          <div className="flex-1" />
          <Button variant="danger" onClick={handleClearAll}>
            Clear all (keep sopira)
          </Button>
        </div>
      </div>

      {showClearConfirm && (
        <BaseModal open={showClearConfirm} onClose={() => setShowClearConfirm(false)} size="sm">
          <div className="p-4 space-y-4">
            <div className="text-lg font-semibold">Vymazať všetky generované dáta?</div>
            <div className="text-sm text-muted-foreground">
              Odstráni všetky generované objekty, ale ponechá superusera sopira.
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setShowClearConfirm(false)}>Zrušiť</Button>
              <Button variant="danger" onClick={confirmClearAll}>Vymazať</Button>
            </div>
          </div>
        </BaseModal>
      )}

      <PageFooter />
      {progressJobId && (
        <ProgressModal
          jobId={progressJobId}
          title={progressTitle}
          apiBase={API_BASE || ""}
          open={progressVisible}
          onHide={() => {
            setProgressVisible(false);
            if (progressCompleted) {
              triggerRefreshOnce();
            }
          }}
          onCancel={async () => {
            if (progressJobId) {
              await apiCancelJob(progressJobId);
            }
          }}
          onComplete={() => {
            setProgressCompleted(true);
            triggerRefreshOnce();
          }}
        />
      )}
    </div>
  );
}

