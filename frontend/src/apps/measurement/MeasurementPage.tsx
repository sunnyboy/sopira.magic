/*............................................................
    MeasurementPage.tsx
    
    Measurement Management Table using MyTable unified component.
    ConfigDriven&SSOT - všetka konfigurácia je deklaratívna.
............................................................*/

import { MyTable } from '@/components/MyTable/MyTable';
import type { MyTableConfig } from '@/components/MyTable/MyTableTypes';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';

// Measurement interface matching backend
interface Measurement {
  id: string;
  uuid?: string;
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
  carrier?: string;
  carrier_display_label?: string;
  driver?: string;
  driver_display_label?: string;
  pot?: string;
  pot_display_label?: string;
  pit?: string;
  pit_display_label?: string;
  machine?: string;
  machine_display_label?: string;
  [key: string]: unknown;
}

export function MeasurementPage() {
  const config: MyTableConfig<Measurement> = {
    tableName: 'Measurements',
    apiEndpoint: '/api/measurements/',
    storageKey: 'measurementsTable',
    pageHeader: {
      visible: false, // header rendruje wrapper
    },
    pageFooter: {
      visible: false, // footer rendruje wrapper
    },

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
        size: 100,
        order: 40,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: true,
        resizable: true,
      },
      factory_display_label: {
        type: 'text',
        header: 'Factory',
        size: 180,
        order: 50,
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
        size: 150,
        order: 60,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: false,
        resizable: true,
      },
      carrier_display_label: {
        type: 'text',
        header: 'Carrier',
        size: 150,
        order: 70,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: false,
        resizable: true,
      },
      driver_display_label: {
        type: 'text',
        header: 'Driver',
        size: 150,
        order: 80,
        isInColumnPanel: true,
        defaultVisible: true,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: false,
        resizable: true,
      },
      pot_display_label: {
        type: 'text',
        header: 'Pot',
        size: 120,
        order: 90,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: false,
        resizable: true,
      },
      pit_display_label: {
        type: 'text',
        header: 'Pit',
        size: 120,
        order: 100,
        isInColumnPanel: true,
        defaultVisible: false,
        isInFilterPanel: false,
        editableInEditModal: false,
        editableInline: false,
        editableInAddModal: false,
        sortable: false,
        resizable: true,
      },
      machine_display_label: {
        type: 'text',
        header: 'Machine',
        size: 150,
        order: 110,
        isInColumnPanel: true,
        defaultVisible: false,
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
        order: 150,
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
        order: 160,
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
        defaultVisible: true,
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
      placeholder: 'Search measurements...',
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
      initialSort: [{ id: 'created', desc: true }],
      persistence: true,
    },

    emptyState: {
      text: 'No measurements found.',
    },

    callbacks: {},
  };

  return (
    <>
      <PageHeader showLogo={true} showMenu={true} />
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-[1400px] mx-auto">
          <MyTable<Measurement> config={config} />
        </div>
      </div>
      <PageFooter />
    </>
  );
}

export default MeasurementPage;
