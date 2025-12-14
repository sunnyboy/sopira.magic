//*........................................................
//*       ~/sopira.magic/version_01/frontend/src/apps/dashboard/DashboardPage.tsx
//*       Dashboard - Main dashboard for authenticated users (placeholder)
//*........................................................

// Dashboard Page
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { Button } from '@/components/ui_custom/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui_custom/card';
import { Factory, BarChart3, Users, Settings } from 'lucide-react';
import { DBWatchdog } from '@/components/DBWatchdog';

/**
 * Dashboard Page - Placeholder
 * 
 * This is a simplified placeholder dashboard.
 * Full functionality will be added incrementally.
 */
export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />

      <div className="bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between gap-4 p-6 border-b border-border bg-gradient-to-r from-primary/10 to-primary/5">
          <h1 className="text-2xl font-extrabold tracking-wide opacity-90">
            Dashboard
          </h1>
          <span className="text-sm text-muted-foreground">
            Welcome, {user?.first_name || user?.username || 'User'}
          </span>
        </div>

        <div className="p-6">
          {/* DB Watchdog Widget (DEV only) */}
          <div className="mb-6">
            <DBWatchdog />
          </div>

          {/* Quick Access Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Factories Card */}
            <Card className="flex flex-col hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <Factory className="w-6 h-6 text-primary" />
                  <CardTitle className="text-lg">Factories</CardTitle>
                </div>
                <CardDescription>
                  Manage your factories and production facilities
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col justify-end">
                <Link to="/factories">
                  <Button variant="solid" size="sm" className="w-full">
                    Open Factories →
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Measurements Card */}
            <Card className="flex flex-col hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <BarChart3 className="w-6 h-6 text-primary" />
                  <CardTitle className="text-lg">Measurements</CardTitle>
                </div>
                <CardDescription>
                  View and analyze measurement data
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col justify-end">
                <Link to="/measurements">
                  <Button variant="solid" size="sm" className="w-full">
                    Open Measurements →
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Users Card */}
            <Card className="flex flex-col hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <Users className="w-6 h-6 text-primary" />
                  <CardTitle className="text-lg">Users</CardTitle>
                </div>
                <CardDescription>
                  Manage users and permissions
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col justify-end">
                <Link to="/users">
                  <Button variant="solid" size="sm" className="w-full">
                    Open Users →
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Settings Card */}
            <Card className="flex flex-col hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <Settings className="w-6 h-6 text-primary" />
                  <CardTitle className="text-lg">Settings</CardTitle>
                </div>
                <CardDescription>
                  Configure system preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col justify-end">
                <Link to="/user-preferences">
                  <Button variant="solid" size="sm" className="w-full">
                    Open Settings →
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>

          {/* User Info Section */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                👤 Account Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="text-xs font-semibold text-muted-foreground uppercase">Username</div>
                  <div className="text-sm mt-1">{user?.username || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-xs font-semibold text-muted-foreground uppercase">Email</div>
                  <div className="text-sm mt-1">{user?.email || 'Not set'}</div>
                </div>
                <div>
                  <div className="text-xs font-semibold text-muted-foreground uppercase">Role</div>
                  <div className="text-sm mt-1">
                    {user?.is_superuser ? 'Superuser' : user?.is_staff ? 'Staff' : 'User'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <PageFooter />
    </div>
  );
}

export default DashboardPage;

