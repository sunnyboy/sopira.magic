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
import { MultiSelect } from '@/components/ui_custom/multi-select';
import { loadFKOptionsFromCache } from '@/services/fkCacheService';
import { getMutatingHeaders } from '@/security/csrf';
import { companyTableConfigBase, type Company } from './companyTableConfig';

export function CompanyPage() {
  const { user, isAuthenticated } = useAuth();
  const isSuperUser = Boolean(
    user?.is_superuser ||
    user?.is_superuser_role ||
    user?.is_admin
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
  }), [usersByCompany, userOptions, factoriesByCompany, factoryOptions]);

  // Guard on FE: show message if not SA
  if (!isAuthenticated || !isSuperUser) {
    return (
      <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
        <PageHeader showLogo={true} showMenu={true} />
        <div className="max-w-[900px] mx-auto bg-card border border-border rounded-xl p-8 shadow-sm">
          <h2 className="text-xl font-semibold mb-2">Access restricted</h2>
          <p className="text-sm text-muted-foreground">
            Táto sekcia je dostupná iba pre superuserov (SA).
          </p>
        </div>
        <PageFooter />
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />
      <MyTable<Company> config={config} />
      <PageFooter />
    </div>
  );
}

export default CompanyPage;

