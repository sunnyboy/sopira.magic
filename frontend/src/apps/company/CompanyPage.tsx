/*............................................................
    CompanyPage.tsx

    Company Management Table using MyTable unified component.
    ConfigDriven&SSOT - všetka konfigurácia je deklaratívna.
    SA-only: stránka aj menu sú určené pre superuserov.
............................................................*/

import { MyTable } from '@/components/MyTable/MyTable';
import type { MyTableConfig } from '@/components/MyTable/MyTableTypes';
import { useAuth } from '@/contexts/AuthContext';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { MultiSelect } from '@/components/ui_custom/multi-select';
import { loadFKOptionsFromCache } from '@/services/fkCacheService';
import { getMutatingHeaders } from '@/security/csrf';
import { companyTableConfigBase, type Company } from './companyTableConfig';
import { Building2 } from 'lucide-react';

export function CompanyPage() {
  const { user, isAuthenticated } = useAuth();
  const location = useLocation();
  const isNewUser = location.state?.isNewUser;
  
  const isSuperUser = Boolean(
    user?.is_superuser ||
    user?.is_superuser_role ||
    user?.role?.toLowerCase() === 'superadmin'
  );

  const [userOptions, setUserOptions] = useState<{ value: string; label: string }[]>([]);
  const [usersByCompany, setUsersByCompany] = useState<Record<string, string[]>>({});
  const [factoryOptions, setFactoryOptions] = useState<{ value: string; label: string }[]>([]);
  const [factoriesByCompany, setFactoriesByCompany] = useState<Record<string, string[]>>({});

  useEffect(() => {
    const loadUsers = async () => {
      try {
        // Použi FK cache pre jednotné labely podľa fk_display_template (users)
        const results = await loadFKOptionsFromCache('users');
        setUserOptions(
          results.map((opt: any) => ({
            value: String(opt.id),
            label: opt.label ?? String(opt.id),
          }))
        );
      } catch (error) {
        console.error('Failed to load users for CompanyPage:', error);
      }
    };

    void loadUsers();
  }, []);

  useEffect(() => {
    const loadFactories = async () => {
      try {
        const results = await loadFKOptionsFromCache('factories');
        setFactoryOptions(
          results.map((opt: any) => ({
            value: String(opt.id),
            label: opt.label ?? String(opt.id),
          }))
        );
      } catch (error) {
        console.error('Failed to load factories for CompanyPage:', error);
      }
    };

    void loadFactories();
  }, []);

  const config: MyTableConfig<Company> = useMemo(() => ({
    ...companyTableConfigBase,
    emptyState: {
      icon: <Building2 size={64} className="text-muted-foreground/50" />,
      title: isNewUser 
        ? "Welcome! Create your first company" 
        : "No companies yet",
      text: isNewUser
        ? "Create your first company to start using the platform. A company is the top-level organizational unit that contains factories, machines, and other resources."
        : "You don't have any companies yet. Click +Add above to create your first company.",
    },
    customCellRenderers: {
      users: (row: Company) => {
        const companyId = row?.id ? String(row.id) : null;
        if (!companyId) {
          return (
            <div className="text-sm text-muted-foreground">
              Loading…
            </div>
          );
        }

        const currentRaw = usersByCompany[companyId] ?? (row.users ?? []);
        const current = Array.isArray(currentRaw) ? currentRaw : [];

        const handleChange = async (selected: string[]) => {
          setUsersByCompany((prev) => ({ ...prev, [companyId]: selected }));
          try {
            await fetch(`/api/companies/${companyId}/`, {
              method: 'PATCH',
              headers: getMutatingHeaders(),
              credentials: 'include',
              body: JSON.stringify({ users: selected }),
            });
          } catch (error) {
            console.error('Failed to update company users:', error);
          }
        };

        return (
          <div className="min-w-[220px]">
            <MultiSelect
              options={userOptions}
              defaultValue={current.map(String)}
              onValueChange={handleChange}
              placeholder="Select users"
              maxCount={4}
              searchable
            />
          </div>
        );
      },
      factories: (row: Company) => {
        const companyId = row?.id ? String(row.id) : null;
        if (!companyId) {
          return (
            <div className="text-sm text-muted-foreground">
              Loading…
            </div>
          );
        }

        const currentRaw = factoriesByCompany[companyId] ?? (row.factories ?? []);
        const current = Array.isArray(currentRaw) ? currentRaw : [];

        const handleChange = async (selected: string[]) => {
          setFactoriesByCompany((prev) => ({ ...prev, [companyId]: selected }));
          try {
            await fetch(`/api/companies/${companyId}/`, {
              method: 'PATCH',
              headers: getMutatingHeaders(),
              credentials: 'include',
              body: JSON.stringify({ factories: selected }),
            });
          } catch (error) {
            console.error('Failed to update company factories:', error);
          }
        };

        return (
          <div className="min-w-[220px]">
            <MultiSelect
              options={factoryOptions}
              defaultValue={current.map(String)}
              onValueChange={handleChange}
              placeholder="Select factories"
              maxCount={4}
              searchable
            />
          </div>
        );
      },
    },
  }), [usersByCompany, userOptions, factoriesByCompany, factoryOptions, isNewUser]);

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />
      <MyTable<Company> config={config} />
      <PageFooter />
    </div>
  );
}

export default CompanyPage;

