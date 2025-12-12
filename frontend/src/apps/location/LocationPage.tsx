/*............................................................
    LocationPage.tsx
    
    Location Management Table using MyTable unified component.
    ConfigDriven&SSOT - všetka konfigurácia je deklaratívna.
............................................................*/

import { MyTable } from '@/components/MyTable/MyTable';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { locationTableConfig, type Location } from './locationTableConfig';

export function LocationPage() {
  const config = locationTableConfig;
  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />
      <MyTable<Location> config={config} />
      <PageFooter />
    </div>
  );
}

export default LocationPage;
