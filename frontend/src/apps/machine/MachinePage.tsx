/*............................................................
    MachinePage.tsx
    
    Machine Management Table using MyTable unified component.
    ConfigDriven&SSOT - všetka konfigurácia je deklaratívna.
............................................................*/

import { MyTable } from '@/components/MyTable/MyTable';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { machineTableConfig, type Machine } from './machineTableConfig';

export function MachinePage() {
  const config = machineTableConfig;

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />
      <MyTable<Machine> config={config} />
      <PageFooter />
    </div>
  );
}

export default MachinePage;
