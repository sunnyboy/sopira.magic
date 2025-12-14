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
  id: string  // UUID
  username: string
  email: string
  last_login?: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  is_staff: boolean
  date_joined: string
  tags?: string
  companies?: string[]
}

/**
 * Base configuration for Users table (without data).
 *
 * Data will be injected at runtime by the UsersPage component, keeping
 * this module purely config-driven.
 */
export const userTableConfigBase: Omit<MyTableConfig<UserRow>, 'data'> = {
  tableName: 'Users',
  apiEndpoint: '/api/users/',
  storageKey: 'users',
  fields: [
    {
      key: 'username',
      header: 'Username',
      type: 'text',
      size: 180,
      sortable: true,
      filterable: true,
      order: 10,
    },
    {
      key: 'email',
      header: 'Email',
      type: 'text',
      size: 220,
      sortable: true,
      filterable: true,
      order: 20,
    },
    {
      key: 'full_name',
      header: 'Name',
      type: 'text',
      size: 220,
      sortable: true,
      filterable: true,
      accessor: (row: UserRow) => `${row.first_name} ${row.last_name}`.trim(),
      sortAccessor: (row: UserRow) => `${row.first_name} ${row.last_name}`.trim(),
      order: 30,
    },
    {
      key: 'role',
      header: 'Role',
      type: 'text',
      size: 140,
      sortable: true,
      filterable: true,
      order: 40,
    },
    {
      key: 'tags',
      header: 'Tags',
      type: 'text',
      size: 180,
      order: 240,
      sortable: false,
      filterable: false,
      isInColumnPanel: true,
      defaultVisible: false,
    },
    {
      key: 'last_login',
      header: 'Last Login',
      type: 'date',
      size: 180,
      order: 250,
      sortable: true,
      filterable: false,
      format: 'DD.MM.YYYY HH:mm:ss',
      isInColumnPanel: true,
      defaultVisible: false,
    },
    {
      key: 'first_name',
      header: 'First Name',
      type: 'text',
      size: 180,
      order: 260,
      sortable: true,
      filterable: true,
      isInColumnPanel: true,
      defaultVisible: false,
    },
    {
      key: 'last_name',
      header: 'Last Name',
      type: 'text',
      size: 180,
      order: 270,
      sortable: true,
      filterable: true,
      isInColumnPanel: true,
      defaultVisible: false,
    },
    {
      key: 'is_active',
      header: 'Active',
      type: 'boolean',
      size: 80,
      sortable: true,
      filterable: true,
      order: 50,
      // SA user (sopira) cannot be deactivated - protection against accidental logout
      editable: (row: UserRow) => row.username !== 'sopira',
    },
    {
      key: 'is_staff',
      header: 'Staff',
      type: 'boolean',
      size: 80,
      sortable: true,
      filterable: true,
      order: 60,
    },
    {
      key: 'date_joined',
      header: 'Joined',
      type: 'date',
      size: 180,
      sortable: true,
      filterable: true,
      order: 70,
    },
    {
      key: 'companies',
      header: 'Companies',
      type: 'text',
      size: 260,
      order: 80,
      sortable: false,
      filterable: false,
      isInColumnPanel: true,
      defaultVisible: true,
      editableInline: true,
      editableInEditModal: false,
    },
  ],
  pagination: {
    //defaultPageSize: 5,
    //pageSizeOptions: [5, 10, 25, 50, 100],
    custom: true,
  },
  filters: {
    fields: ['username', 'email', 'role', 'is_active', 'is_staff'],
  },
  globalSearch: {
    enabled: true,
    placeholder: 'Search users...',
  },
  rowSelection: {
    enabled: true,
  },
  toolbarVisibility: {
    filters: true,
    columns: true,
    add: false,
    csv: true,
    xlsx: true,
    reset: true,
  },
  emptyState: {
    text: 'No users found',
  },
}
