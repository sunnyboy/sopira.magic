//*........................................................
//*       ~/sopira.magic/version_01/frontend/src/components/NavBar.tsx
//*       Navigation bar component with auth menu
//*       Config-driven authentication using AuthContext
//*........................................................

import React, { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useAccessRights } from "@/hooks/useAccessRights";
import { Button } from "@/components/ui_custom/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui_custom/select";
import { cn } from "@/lib/utils";

type ItemProps = {
  to: string;
  children: React.ReactNode;
  className?: string;
};

const Item = ({ to, children, className }: ItemProps) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      cn(
        "px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
        isActive
          ? "bg-primary text-primary-foreground"
          : "bg-secondary text-secondary-foreground hover:bg-secondary/80 hover:-translate-y-px hover:shadow-sm",
        className,
      )
    }
  >
    {children}
  </NavLink>
);

export default function NavBar() {
  const { isAuthenticated, user, logout } = useAuth();
  const { getMenu } = useAccessRights();
  const navigate = useNavigate();
  const [selectedLanguage, setSelectedLanguage] = useState('EN');

  const isSuperUser = Boolean(
    user?.is_superuser ||
    user?.is_superuser_role ||
    user?.is_admin
  );

  const canSeeMenu = (key: string, fallback: boolean = true) => {
    const allowed = getMenu(key);
    return typeof allowed === 'boolean' ? allowed : fallback;
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/', { replace: true });
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <header className="border-b border-border shadow-sm py-4 bg-background">
      <div className="max-w-[1400px] mx-auto px-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <nav className="flex items-center justify-between w-full gap-4">
          {!isAuthenticated ? (
            // Public pages for non-authenticated users
            <>
              <div className="flex items-center gap-1">
                <Item to="/">Home</Item>
                <Item to="/contact">Contact</Item>
              </div>
              <div className="flex items-center gap-2">
                <Link to="/login">
                  <Button variant="solid">Login</Button>
                </Link>
              </div>
            </>
          ) : (
            // Authenticated menu
            <>
              <div className="flex items-center gap-1 flex-wrap">
                <Item to="/dashboard">Dashboard</Item>
                {canSeeMenu("dashboard") && <Item to="/dashboard">Dashboard</Item>}
                {canSeeMenu("measurements") && <Item to="/measurements">Measurements</Item>}
                {canSeeMenu("companies", isSuperUser) && <Item to="/companies">Company</Item>}
                {canSeeMenu("factories") && <Item to="/factories">Factories</Item>}
                {canSeeMenu("locations") && <Item to="/locations">Locations</Item>}
                {canSeeMenu("carriers") && <Item to="/carriers">Carriers</Item>}
                {canSeeMenu("drivers") && <Item to="/drivers">Drivers</Item>}
                {canSeeMenu("pots") && <Item to="/pots">Pots</Item>}
                {canSeeMenu("pits") && <Item to="/pits">Pits</Item>}
                {canSeeMenu("machines") && <Item to="/machines">Machines</Item>}
                {canSeeMenu("cameras") && <Item to="/cameras">Cameras</Item>}
                {canSeeMenu("users") && <Item to="/users">Users</Item>}
              </div>
              <div className="flex items-center gap-2">
                {/* Logout button */}
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-full bg-secondary text-secondary-foreground text-sm font-medium transition-all duration-200 hover:bg-secondary/80 hover:-translate-y-px hover:shadow-sm"
                >
                  Logout
                </button>

                {/* Language selector */}
                <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                  <SelectTrigger className="w-[70px] h-auto px-4 py-2 rounded-full bg-secondary text-secondary-foreground text-sm font-medium border-0 transition-all duration-200 hover:bg-secondary/80 hover:-translate-y-px hover:shadow-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EN">EN</SelectItem>
                    <SelectItem value="DE">DE</SelectItem>
                    <SelectItem value="ES">ES</SelectItem>
                    <SelectItem value="SK">SK</SelectItem>
                  </SelectContent>
                </Select>

                {/* Username - clickable link to preferences */}
                <Link
                  to="/user-preferences"
                  className="px-4 py-2 rounded-full bg-secondary text-secondary-foreground text-sm font-medium transition-all duration-200 hover:bg-secondary/80 hover:-translate-y-px hover:shadow-sm inline-block"
                >
                  {user?.username || 'User'}
                </Link>
              </div>
            </>
          )}
          </nav>
        </div>
      </div>
    </header>
  );
}
