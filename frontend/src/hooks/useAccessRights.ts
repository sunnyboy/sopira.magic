import { useEffect, useMemo, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'

export type AccessActions = {
  view?: boolean
  add?: boolean
  edit?: boolean
  delete?: boolean
  export?: boolean
  menu?: boolean
}

export type AccessRightsMatrix = {
  menu: Record<string, boolean>
  actions: Record<string, AccessActions>
}

type AccessState = {
  data: AccessRightsMatrix | null
  loading: boolean
}

// Jednoduchý cache layer (memory) aby sme nevolali endpoint opakovane
const cache: { data: AccessRightsMatrix | null; promise: Promise<AccessRightsMatrix | null> | null } = {
  data: null,
  promise: null,
}

async function fetchAccessRights(): Promise<AccessRightsMatrix | null> {
  const res = await fetch('/api/accessrights/matrix/', { credentials: 'include' })
  if (!res.ok) return null
  return (await res.json()) as AccessRightsMatrix
}

export function useAccessRights() {
  const { isAuthenticated } = useAuth()
  const [state, setState] = useState<AccessState>({ data: cache.data, loading: false })

  useEffect(() => {
    if (!isAuthenticated) {
      setState({ data: null, loading: false })
      return
    }
    if (cache.data) {
      setState({ data: cache.data, loading: false })
      return
    }
    if (!cache.promise) {
      cache.promise = fetchAccessRights()
    }
    setState((prev) => ({ ...prev, loading: true }))
    cache.promise
      ?.then((data) => {
        cache.data = data
        setState({ data, loading: false })
      })
      .catch(() => setState({ data: null, loading: false }))
  }, [isAuthenticated])

  const getMenu = useMemo(
    () => (key: string) => {
      return state.data?.menu?.[key]
    },
    [state.data],
  )

  const getActions = useMemo(
    () => (viewName: string): AccessActions | undefined => {
      return state.data?.actions?.[viewName]
    },
    [state.data],
  )

  return {
    matrix: state.data,
    loading: state.loading,
    getMenu,
    getActions,
  }
}

