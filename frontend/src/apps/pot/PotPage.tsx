/*............................................................
    PotPage.tsx
    
    Pot Management Table using MyTable unified component.
    ConfigDriven&SSOT - všetka konfigurácia je deklaratívna.
............................................................*/

import { MyTable } from '@/components/MyTable/MyTable';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { potTableConfig, type Pot } from './potTableConfig';

export function PotPage() {
  const config = potTableConfig;

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />
      <MyTable<Pot> config={config} />
      <PageFooter />
    </div>
  );
}

export default PotPage;
