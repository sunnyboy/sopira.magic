//*........................................................
//*       ~/sopira.magic/version_01/frontend/src/components/PageHeader.tsx
//*       Reusable page header with logo and build number
//*........................................................

import React from 'react';
import NavBar from './NavBar';

interface PageHeaderProps {
  showLogo?: boolean;
  showMenu?: boolean;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ 
  showLogo = true,
  showMenu = true 
}) => {
  return (
    <div>
      {/* Logo and Build Number Row - aligned with content card (max-w-[1400px]) */}
      {showLogo && (
        <div className="flex justify-between items-center p-6 border-b border-border bg-background">
          <div className="max-w-[1400px] w-full mx-auto flex justify-between items-center">
            {/* Logo - left aligned with content card */}
            <div>
              <img 
                src="/assets/logo.png" 
                alt="Sopira Magic Logo" 
                style={{ height: '120px', objectFit: 'contain' }} 
              />
            </div>
            
            {/* Build Number - right aligned with content card */}
            <div className="text-xs text-muted-foreground font-mono opacity-60">
              Build: {typeof __GIT_HASH__ !== 'undefined' ? __GIT_HASH__ : 'dev'}
            </div>
          </div>
        </div>
      )}
      
      {/* Navigation Menu - shown by default, aligned with content card */}
      {showMenu && <NavBar />}
    </div>
  );
};
