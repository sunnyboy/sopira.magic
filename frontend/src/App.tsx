//..............................................................
//   ~/sopira.magic/version_01/frontend/src/App.tsx
//   App - Root application shell and router
//   Top-level React component wiring global providers and routes
//..............................................................

/**
 * Root application component.
 *
 * Responsible for mounting the router and wiring the top-level layout.
 * Feature modules should register their routes here (or via a route config)
 * instead of creating ad-hoc entrypoints.
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import { ThemeProvider } from '@/contexts/ThemeContext'
import { AuthProvider } from '@/contexts/AuthContext'
import { ScopeProvider } from '@/contexts/ScopeContext'
import { DashboardPage } from '@/apps/dashboard/DashboardPage'
import { FactoryPage } from '@/apps/factory/FactoryPage'
import { UsersPage } from '@/apps/user/UsersPage'
import { PdfViewerPage } from '@/apps/pdfviewer/PdfViewerPage'
import { LocationPage } from '@/apps/location/LocationPage'
import { CarrierPage } from '@/apps/carrier/CarrierPage'
import { DriverPage } from '@/apps/driver/DriverPage'
import { PotPage } from '@/apps/pot/PotPage'
import { PitPage } from '@/apps/pit/PitPage'
import { MachinePage } from '@/apps/machine/MachinePage'
import { CameraPage } from '@/apps/camera/CameraPage'
import { MeasurementPage } from '@/apps/measurement/MeasurementPage'
import { CompanyPage } from '@/apps/company/CompanyPage'
import Home from '@/pages/Home'
import Contact from '@/pages/Contact'
import Login from '@/pages/Login'

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ScopeProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-background text-foreground">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/login" element={<Login />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/companies" element={<CompanyPage />} />
                <Route path="/factories" element={<FactoryPage />} />
              <Route path="/users" element={<UsersPage />} />
                <Route path="/user-preferences" element={<UsersPage />} />
              <Route path="/pdfviewer" element={<PdfViewerPage />} />
              <Route path="/locations" element={<LocationPage />} />
              <Route path="/carriers" element={<CarrierPage />} />
              <Route path="/drivers" element={<DriverPage />} />
              <Route path="/pots" element={<PotPage />} />
              <Route path="/pits" element={<PitPage />} />
              <Route path="/machines" element={<MachinePage />} />
              <Route path="/cameras" element={<CameraPage />} />
              <Route path="/measurements" element={<MeasurementPage />} />
            </Routes>
          </div>
        </BrowserRouter>
        </ScopeProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App

