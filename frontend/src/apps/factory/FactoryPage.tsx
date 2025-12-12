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
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { factoryTableConfig, type Factory } from './factoryTableConfig';

export function FactoryPage() {
  const config = factoryTableConfig;
  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />
      <MyTable<Factory> config={config} />
      <PageFooter />
    </div>
  );
}

export default FactoryPage;

