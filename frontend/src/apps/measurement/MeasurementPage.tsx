/*............................................................
    MeasurementPage.tsx
    
    Measurement Management Table using MyTable unified component.
    ConfigDriven&SSOT - všetka konfigurácia je deklaratívna.
............................................................*/

import { MyTable } from '@/components/MyTable/MyTable';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { measurementTableConfig, type Measurement } from './measurementTableConfig';

export function MeasurementPage() {
  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />
      <MyTable<Measurement> config={measurementTableConfig} />
      <PageFooter />
    </div>
  );
}

export default MeasurementPage;
