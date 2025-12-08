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

import React, { useEffect, useState } from 'react'

import { PageHeader } from '@/components/PageHeader'
import { PageFooter } from '@/components/PageFooter'
import { MyTable } from '@/components/MyTable'
import type { MyTableConfig } from '@/components/MyTable/MyTableTypes'
import { userTableConfigBase, type UserRow } from './userTableConfig'

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

  const config: MyTableConfig<UserRow> = {
    ...userTableConfigBase,
    data: rows,
    pageHeader: {
      visible: false, // PageHeader je na stránke, aby sme nemali duplicitný navbar
    },
    pageFooter: {
      visible: false,
    },
  }

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
    <>
      <PageHeader showLogo={true} showMenu={true} />
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-[1400px] mx-auto">
          <MyTable config={config} />
        </div>
      </div>
      <PageFooter />
    </>
  )
}
