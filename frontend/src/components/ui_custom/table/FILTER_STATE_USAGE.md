# Filter State Management Usage

## Overview
Implementácia ukladania, vyvolávaniaa resetovania filtrov v tabuľkách.

## Required Imports

```typescript
import {
  FilterPanel,
  SaveFilterModal,
  RecallFilterModal,
  useFilterState,
  useEscapeKey,
  type SavedFilter,
} from '@/components/ui_custom/table';
```

## Implementation Steps

### 1. Add State Variables

```typescript
// Filter state management
const [showSaveFilterModal, setShowSaveFilterModal] = useState(false);
const [showRecallFilterModal, setShowRecallFilterModal] = useState(false);

// Initialize filter state hook
const {
  savedFilters,
  saveFilter,
  deleteFilter,
  getDefaultFilterName,
} = useFilterState('measurements-filters'); // unique key per table
```

### 2. Add Escape Key Handlers

```typescript
useEscapeKey(
  // ... existing handlers
  showSaveFilterModal ? () => setShowSaveFilterModal(false) : undefined,
  showRecallFilterModal ? () => setShowRecallFilterModal(false) : undefined
);
```

### 3. Implement Filter Callbacks

```typescript
// Get current filter state
const getCurrentFilterState = () => ({
  columnFilters,
  globalFilter,
  // Add any other filter-related state
});

// Set - Save current filter
const handleSetFilter = () => {
  setShowSaveFilterModal(true);
};

// Reset - Clear all filters
const handleResetFilters = () => {
  setColumnFilters([]);
  setGlobalFilter("");
  // Reset any other filter state
};

// Recall - Load saved filter
const handleRecallFilter = () => {
  setShowRecallFilterModal(true);
};

// Save filter with name
const handleSaveFilter = (name: string) => {
  saveFilter(name, getCurrentFilterState());
};

// Load saved filter
const handleLoadFilter = (filter: SavedFilter) => {
  setColumnFilters(filter.state.columnFilters || []);
  setGlobalFilter(filter.state.globalFilter || "");
  // Restore any other filter state
};
```

### 4. Update FilterPanel

```tsx
<FilterPanel
  title="Filters"
  icon={<SlidersHorizontal size={16}/>}
  onSet={handleSetFilter}
  onReset={handleResetFilters}
  onRecall={handleRecallFilter}
  onClose={() => setShowFilters(false)}
>
  {/* Filter components */}
</FilterPanel>
```

### 5. Add Modals

```tsx
{/* Save Filter Modal */}
<SaveFilterModal
  open={showSaveFilterModal}
  onClose={() => setShowSaveFilterModal(false)}
  onSave={handleSaveFilter}
  defaultName={getDefaultFilterName('Measurements')}
/>

{/* Recall Filter Modal */}
<RecallFilterModal
  open={showRecallFilterModal}
  onClose={() => setShowRecallFilterModal(false)}
  savedFilters={savedFilters}
  onRecall={handleLoadFilter}
  onDelete={deleteFilter}
/>
```

## Complete Example

See `MeasurementsTable.tsx` for a complete working implementation.
