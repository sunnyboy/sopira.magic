// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// frontend/src/components/DBWatchdog.tsx
// DB Watchdog Widget - displays high DB usage warnings
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, Database } from 'lucide-react';

interface DBWarning {
  timestamp: string;
  method: string;
  path: string;
  query_count: number;
  top_queries: Array<{
    time: string;
    sql: string;
  }>;
}

interface DBWatchdogResponse {
  warnings: DBWarning[];
  total: number;
}

export function DBWatchdog() {
  const [warnings, setWarnings] = useState<DBWarning[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWarnings = async () => {
      try {
        const response = await fetch('/api/db-watchdog/', {
          credentials: 'include',
        });
        if (response.ok) {
          const data: DBWatchdogResponse = await response.json();
          setWarnings(data.warnings.slice(0, 5)); // Show only top 5
        }
      } catch (error) {
        console.error('[DBWatchdog] Failed to fetch warnings:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchWarnings();
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchWarnings, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5" />
            DB Watchdog
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Loading...</p>
        </CardContent>
      </Card>
    );
  }

  if (warnings.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="w-5 h-5 text-green-600" />
            DB Watchdog
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-green-600">✅ All queries optimized (&lt;10 queries per request)</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-orange-600" />
          DB Watchdog - High Query Usage
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {warnings.map((warning, index) => (
          <div
            key={`${warning.timestamp}-${index}`}
            className="border-l-4 border-orange-500 bg-orange-50 dark:bg-orange-950 p-3 rounded"
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs bg-orange-200 dark:bg-orange-900 px-2 py-1 rounded">
                  {warning.method}
                </span>
                <span className="font-mono text-sm">{warning.path}</span>
              </div>
              <span className="text-xs text-muted-foreground">
                {new Date(warning.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <div className="text-sm font-semibold text-orange-700 dark:text-orange-400">
              🔥 {warning.query_count} queries
            </div>
            {warning.top_queries.length > 0 && (
              <div className="mt-2 text-xs text-muted-foreground">
                Slowest: {warning.top_queries[0].time} - {warning.top_queries[0].sql.substring(0, 80)}...
              </div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

