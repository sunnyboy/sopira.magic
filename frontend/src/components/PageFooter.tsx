//*........................................................
//*       ~/sopira.magic/version_01/frontend/src/components/PageFooter.tsx
//*       Reusable page footer component
//*........................................................

import React from 'react';

export const PageFooter: React.FC = () => {
  return (
    <footer className="border-t border-border bg-background py-6 mt-auto">
      <div className="max-w-[1400px] mx-auto px-4">
        <div className="text-center text-sm text-muted-foreground">
          {/* Placeholder footer content */}
          <p>Sopira Magic © {new Date().getFullYear()}</p>
        </div>
      </div>
    </footer>
  );
};
