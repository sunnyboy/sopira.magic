/*............................................................
    CameraPage.tsx
    
    Camera Management Table using MyTable unified component.
    ConfigDriven&SSOT - všetka konfigurácia je deklaratívna.
............................................................*/

import { MyTable } from '@/components/MyTable/MyTable';
import type { MyTableConfig } from '@/components/MyTable/MyTableTypes';

// Camera interface matching backend
interface Camera {
  id: string;
  uuid?: string;
  code: string;
  name: string;
  human_id?: string;
  comment?: string;
  note?: string;
  tags?: string;
  active: boolean;
  visible?: boolean;
  created: string;
  updated: string;
  factory?: string;
  factory_display_label?: string;
  location?: string;
  location_display_label?: string;
  [key: string]: unknown;
}

export function CameraPage() {
  const config: MyTableConfig<Camera> = {
    tableName: 'Cameras',
    apiEndpoint: '/api/cameras/',
    storageKey: 'camerasTable',

    fieldsMatrix: {
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
        editableInAddModal: false,
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
        editableInAddModal: false,
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
      factory_display_label: {
        type: 'text',
        header: 'Factory',
        size: 200,
        order: 75,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: false,
        resizable: true,
      },
      location_display_label: {
        type: 'text',
        header: 'Location',
        size: 180,
        order: 76,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: false,
        resizable: true,
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
      created: {
        type: 'date',
        header: 'Created',
        size: 180,
        order: 200,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: true,
        filterType: 'daterange',
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: true,
        resizable: true,
        format: 'DD.MM.YYYY HH:mm:ss',
      },
      updated: {
        type: 'date',
        header: 'Updated',
        size: 180,
        order: 210,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: true,
        filterType: 'daterange',
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: true,
        resizable: true,
        format: 'DD.MM.YYYY HH:mm:ss',
      },
      comment: {
        type: 'text',
        header: 'Comment',
        size: 200,
        order: 220,
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
        order: 230,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: false,
        editableInEditModal: true,
        editableInline: true,
        sortable: false,
        resizable: true,
        multiline: true,
      },
    },

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
      share: false,
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
      expand: false,
      inlineShare: false,
    },

    rowSelection: {
      enabled: true,
      persistence: false,
    },

    globalSearch: {
      enabled: true,
      placeholder: 'Search cameras by code, name...',
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
      text: 'No cameras found.',
    },

    callbacks: {},
  };

  return <MyTable<Camera> config={config} />;
}

export default CameraPage;
