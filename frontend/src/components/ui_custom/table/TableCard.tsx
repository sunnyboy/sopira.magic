//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/TableCard.tsx
//*       Card wrapper for tables with page layout
//*........................................................

/*
 * Card wrapper for tables with page layout
 */

import { Card } from "@/components/ui_custom/card";
import { ReactNode } from "react";

interface TableCardProps {
  children: ReactNode;
}

export function TableCard({ children }: TableCardProps) {
  return (
    <div className="min-h-screen bg-background p-6">
      <Card className="max-w-[1400px] mx-auto">
        {children}
      </Card>
    </div>
  );
}
