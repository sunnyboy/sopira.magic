//..............................................................
//   ~/sopira.magic/version_01/frontend/src/apps/user/UsersPage.tsx
//   UsersPage - Users table rendered via generic MyTable
//   Fetches data from /api/users/ and applies config-driven table config
//..............................................................

/**
 * UsersPage - config-driven Users table using MyTable.
 *
 * This page loads user rows from the backend `/api/users/` endpoint and
 * combines them with the declarative `userTableConfigBase` to render a
 * fully generic MyTable instance. No column definitions are hardcoded in
 * this component.
 */

import React, { useEffect, useMemo, useState } from 'react'

import { PageHeader } from '@/components/PageHeader'
import { PageFooter } from '@/components/PageFooter'
import { MyTable } from '@/components/MyTable'
import type { MyTableConfig } from '@/components/MyTable/MyTableTypes'
import { userTableConfigBase, type UserRow } from './userTableConfig'
import { MultiSelect } from '@/components/ui_custom/multi-select'
import { loadFKOptionsFromCache } from '@/services/fkCacheService'
import { getMutatingHeaders } from '@/security/csrf'

interface UsersApiResponse {
  count?: number
  results?: UserRow[]
  // Fallback support for non-paginated responses
  [key: string]: unknown
}

export function UsersPage() {
  const [rows, setRows] = useState<UserRow[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [companyOptions, setCompanyOptions] = useState<{ value: string; label: string }[]>([])
  const [companiesByUser, setCompaniesByUser] = useState<Record<string, string[]>>({})

  useEffect(() => {
    let isMounted = true

    async function loadUsers() {
      try {
        setIsLoading(true)
        setError(null)
        const response = await fetch('/api/users/', {
          credentials: 'include',
        })
        if (!response.ok) {
          throw new Error(`Failed to load users (HTTP ${response.status})`)
        }
        const json = (await response.json()) as UsersApiResponse | UserRow[]
        const data: UserRow[] = Array.isArray(json)
          ? json
          : Array.isArray(json.results)
            ? json.results
            : []
        if (isMounted) {
          setRows(data)
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Unknown error while loading users')
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    loadUsers()

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    const loadCompanies = async () => {
      try {
        const opts = await loadFKOptionsFromCache('companies')
        setCompanyOptions(opts.map(o => ({ value: String(o.id), label: o.label ?? String(o.id) })))
      } catch (err) {
        console.error('Failed to load companies FK options', err)
      }
    }
    void loadCompanies()
  }, [])

  const config: MyTableConfig<UserRow> = useMemo(() => ({
    ...userTableConfigBase,
    data: rows,
    pageHeader: {
      visible: false, // PageHeader je na stránke, aby sme nemali duplicitný navbar
    },
    pageFooter: {
      visible: false,
    },
    customCellRenderers: {
      companies: (row: UserRow) => {
        const userId = row?.id ? String(row.id) : null
        if (!userId) return <span className="text-sm text-muted-foreground">N/A</span>
        const currentRaw = companiesByUser[userId] ?? row.companies ?? []
        const current = Array.isArray(currentRaw) ? currentRaw : []

        const handleChange = async (selected: string[]) => {
          setCompaniesByUser((prev) => ({ ...prev, [userId]: selected }))
          try {
            await fetch(`/api/users/${userId}/`, {
              method: 'PATCH',
              credentials: 'include',
              headers: getMutatingHeaders(),
              body: JSON.stringify({ companies: selected }),
            })
          } catch (err) {
            console.error('Failed to update user companies', err)
          }
        }

        return (
          <div className="min-w-[220px]">
            <MultiSelect
              options={companyOptions}
              defaultValue={current.map(String)}
              onValueChange={handleChange}
              placeholder="Select companies"
              maxCount={4}
              searchable
            />
          </div>
        )
      },
    },
  }), [rows, companiesByUser, companyOptions])

  if (error) {
    return (
      <div className="p-6">
        <h2 className="mb-2 text-lg font-semibold">Users</h2>
        <p className="text-sm text-destructive">{error}</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="p-6 text-sm text-muted-foreground">
        Loading users...
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />
      <MyTable config={config} />
      <PageFooter />
    </div>
  )
}
