//..............................................................
//   ~/sopira.magic/version_01/frontend/src/apps/user/userTableConfig.ts
//   User table config - SSOT for Users MyTable configuration
//   Declarative column and table settings for the Users list
//..............................................................

/**
 * User table configuration for MyTable.
 *
 * This file is the Single Source of Truth (SSOT) for how the Users table
 * is rendered in the frontend. It is intentionally declarative and
 * domain-specific, but it does not contain any React rendering logic.
 *
 * The shape of the rows is aligned with the backend UserListSerializer.
 */

import type { MyTableConfig } from '@/components/MyTable/MyTableTypes'

export type UserRow = {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  is_staff: boolean
  date_joined: string
}

/**
 * Base configuration for Users table (without data).
 *
 * Data will be injected at runtime by the UsersPage component, keeping
 * this module purely config-driven.
 */
export const userTableConfigBase: Omit<MyTableConfig<UserRow>, 'data'> = {
  id: 'users',
  title: 'Users',
  description: 'User accounts and roles',
  columns: [
    {
      id: 'username',
      label: 'Username',
      field: 'username',
      sortable: true,
      filterable: true,
      width: 180,
    },
    {
      id: 'email',
      label: 'Email',
      field: 'email',
      sortable: true,
      filterable: true,
      width: 220,
    },
    {
      id: 'full_name',
      label: 'Name',
      accessor: (row) => `${row.first_name} ${row.last_name}`.trim(),
      sortable: true,
      filterable: true,
      sortAccessor: (row) => `${row.first_name} ${row.last_name}`.trim(),
      width: 220,
    },
    {
      id: 'role',
      label: 'Role',
      field: 'role',
      sortable: true,
      filterable: true,
      width: 140,
    },
    {
      id: 'is_active',
      label: 'Active',
      field: 'is_active',
      sortable: true,
      filterable: true,
      width: 80,
    },
    {
      id: 'is_staff',
      label: 'Staff',
      field: 'is_staff',
      sortable: true,
      filterable: true,
      width: 80,
    },
    {
      id: 'date_joined',
      label: 'Joined',
      field: 'date_joined',
      sortable: true,
      filterable: true,
      width: 180,
    },
  ],
  pageSize: 25,
  pageSizeOptions: [10, 25, 50, 100],
  initialSort: {
    columnId: 'username',
    direction: 'asc',
  },
  globalFilter: {
    enabled: true,
    placeholder: 'Search users...',
  },
  selectableRows: true,
  toolbar: {
    showGlobalFilter: true,
    showPageSize: true,
    showCount: true,
  },
  emptyState: {
    title: 'No users found',
    description: 'Try adjusting your filters or search term.',
  },
  dense: false,
}
