/*............................................................
    FactoryPage.tsx
    
    Factory Management Table using MyTable unified component.
    Features:
    - Full CRUD operations
    - Share factory access to users (Admin/SA only)
    - Server-side pagination, sorting, filtering
    - State persistence (columns, filters, sorting, pagination)
    
............................................................*/

import { MyTable } from '@/components/MyTable/MyTable';
import type { MyTableConfig } from '@/components/MyTable/MyTableTypes';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';

// Factory interface matching backend
interface Factory {
  id: string;
  uuid?: string;
  code: string;
  name: string;
  address?: string;
  comment?: string;
  note?: string;
  tags?: string;
  human_id?: string;
  active: boolean;
  visible?: boolean;
  created: string;
  updated: string;
  created_by?: number;
  created_by_username?: string;
  [key: string]: unknown; // Allow additional properties
}

export function FactoryPage() {
  const config: MyTableConfig<Factory> = {
    // ============================================
    // IDENTIFIKÁCIA
    // ============================================
    tableName: 'Factories',
    apiEndpoint: '/api/factories/',
    storageKey: 'factoriesTable',
    pageHeader: {
      visible: false, // header rieši wrapper
    },
    pageFooter: {
      visible: false, // footer rieši wrapper
    },

    // ============================================
    // FIELDS MATRIX - Deklaratívna konfigurácia polí
    // ============================================
    fieldsMatrix: {
      // Base fields (v správnom poradí podľa konvencie)
      uuid: {
        type: 'text',
        header: 'UUID',
        size: 120,
        order: 30,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false, // System field
        sortable: false,
        resizable: true,
      },
      id: {
        type: 'text',
        header: 'ID',
        size: 80,
        order: 40,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false, // System field
        sortable: true,
        resizable: true,
      },
      human_id: {
        type: 'text',
        header: 'Human ID',
        size: 150,
        order: 50,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: true,
        filterType: 'text',
        editableInEditModal: true,
        editableInline: true,
        sortable: true,
        resizable: true,
      },
      code: {
        type: 'text',
        header: 'Code',
        size: 150,
        order: 60,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: true,
        filterType: 'text',
        editableInEditModal: true,
        editableInline: true,
        sortable: true,
        resizable: true,
        required: true,
      },
      name: {
        type: 'text',
        header: 'Name',
        size: 250,
        order: 70,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: true,
        filterType: 'text',
        editableInEditModal: true,
        editableInline: true,
        sortable: true,
        resizable: true,
        required: true,
      },
      created: {
        type: 'date',
        header: 'Created',
        size: 180,
        order: 80,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: true,
        filterType: 'daterange',
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false, // System field
        sortable: true,
        resizable: true,
        format: 'DD.MM.YYYY HH:mm:ss',
      },
      updated: {
        type: 'date',
        header: 'Updated',
        size: 180,
        order: 90,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: true,
        filterType: 'daterange',
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false, // System field
        sortable: true,
        resizable: true,
        format: 'DD.MM.YYYY HH:mm:ss',
      },
      active: {
        type: 'boolean',
        header: 'Active',
        size: 100,
        minSize: 80,
        maxSize: 120,
        order: 100,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: true,
        filterType: 'boolean',
        editableInEditModal: true,
        editableInline: true,
        sortable: true,
        resizable: true,
        trueLabel: 'Active',
        falseLabel: 'Inactive',
        style: 'badge',
        quickToggle: false,
      },
      visible: {
        type: 'boolean',
        header: 'Visible',
        size: 100,
        minSize: 80,
        maxSize: 120,
        order: 110,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: true,
        filterType: 'boolean',
        editableInEditModal: true,
        editableInline: true,
        sortable: true,
        resizable: true,
        trueLabel: 'Visible',
        falseLabel: 'Hidden',
        style: 'badge',
        quickToggle: false,
      },
      tags: {
        type: 'text',
        header: 'Tags',
        size: 180,
        order: 120,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: true,
        filterType: 'text',
        editableInEditModal: true,
        editableInline: true,
        sortable: false,
        resizable: true,
      },
      comment: {
        type: 'text',
        header: 'Comment',
        size: 200,
        order: 130,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: false,
        editableInEditModal: true,
        editableInline: true,
        sortable: false,
        resizable: true,
        multiline: true,
      },
      note: {
        type: 'text',
        header: 'Note',
        size: 200,
        order: 140,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: false,
        editableInEditModal: true,
        editableInline: true,
        sortable: false,
        resizable: true,
        multiline: true,
      },
      
      // Other fields (table-specific, abecedne)
      address: {
        type: 'text',
        header: 'Address',
        size: 300,
        order: 200,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: true,
        filterType: 'text',
        editableInEditModal: true,
        editableInline: true,
        sortable: true,
        resizable: true,
      },
      created_by_username: {
        type: 'text',
        header: 'Owner',
        size: 150,
        order: 210,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false, // System field
        sortable: false,
        resizable: true,
      },
    },

    // ============================================
    // FEATURES
    // ============================================
    headerVisibility: {
      title: true,
      toolbar: true,
      stats: true,
      pagination: true,
    },

    toolbarVisibility: {
      filters: true,
      columns: true,
      compact: false,
      add: true,
      share: true,  // ✅ Enable share button (Admin/SA only)
      csv: true,
      xlsx: true,
      pdf: false,
      reset: true,
      save: false,
      editAll: false,
      delete: true,
    },

    actions: {
      edit: true,
      delete: true,
      expand: false,  // ✅ Skryté
      inlineShare: true,  // ✅ Share button in row actions (Admin/SA only)
    },

    rowSelection: {
      enabled: true,
      persistence: false,
    },

    globalSearch: {
      enabled: true,
      placeholder: 'Search factories by code, name, address...',
    },

    filters: {
      persistence: true,
    },

    columns: {
      enabled: true,
      persistence: true,
      fields: {},
    },

    pagination: {
      defaultPageSize: 10,
      pageSizeOptions: [5, 10, 20, 50, 100],
      persistence: true,
    },

    multiLine: {
      enabled: false,
      allowToggle: true,
      persistence: true,
    },

    sorting: {
      initialSort: [{ id: 'name', desc: false }],
      persistence: true,
    },

    emptyState: {
      text: 'No factories found. Please select some Factory in Dashboard or create one.',
    },

    // ============================================
    // CALLBACKS
    // ============================================
    callbacks: {
      // onAdd, onEdit, onDelete will be handled by MyTable automatically
      // Share is handled by MyTable with ShareFactoryModal
    },
    
    // Disable factory scope for Factories table (it's the scope master)
    disableFactoryScope: true,
  };

  return (
    <>
      <PageHeader showLogo={true} showMenu={true} />
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-[1400px] mx-auto">
          <MyTable<Factory> config={config} />
        </div>
      </div>
      <PageFooter />
    </>
  );
}

export default FactoryPage;

