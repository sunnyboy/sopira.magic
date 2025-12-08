//*........................................................
//*       www/thermal_eye_ui/src/components/ui_custom/table/TableWrapper.tsx
//*       Wrapper component for table content
//*........................................................

import { CardContent } from "@/components/ui_custom/card";
import { ReactNode } from "react";

interface TableWrapperProps {
  children: ReactNode;
}

export function TableWrapper({ children }: TableWrapperProps) {
  return (
    <CardContent className="p-0" data-component="TableWrapper">
      <div className="overflow-auto max-w-full max-h-[calc(100vh-280px)] border border-border">
        <div className="p-2">
          {children}
        </div>
      </div>
    </CardContent>
  );
}
