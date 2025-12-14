//*.........................................................
//*       ~/sopira.magic/version_01/frontend/src/pages/Home.tsx
//*       Home page with feature cards and image collage
//*.........................................................

import React, { useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { Flame, BarChart3, Factory, X, Bug } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Link, useNavigate } from 'react-router-dom';
import { BaseModal } from '@/components/modals/BaseModal';
import { useAuth } from '@/contexts/AuthContext';

// DEV: Test users for quick login
const TEST_USERS = [
  { username: 'sopira', password: 'sopirapass', label: 'Sopira (SA)' },
  { username: 'fero', password: 'feropass', label: 'Fero (Admin)' },
  { username: 'test_empty', password: 'testpass', label: 'Empty Admin' },
];

const Home: React.FC = () => {
  const [openModal, setOpenModal] = useState<string | null>(null);
  const [devLoginLoading, setDevLoginLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleCardClick = (modalId: string) => {
    setOpenModal(modalId);
  };

  const handleCloseModal = () => {
    setOpenModal(null);
  };

  // DEV: Direct login with username and password
  const handleDevLoginDirect = async (username: string, password: string) => {
    setDevLoginLoading(true);
    try {
      const success = await login(username, password);
      if (success) {
        navigate('/dashboard');
      } else {
        console.error('Dev login failed for', username);
        alert(`Dev login failed for ${username}`);
      }
    } catch (error) {
      console.error('Dev login error:', error);
      alert('Dev login error');
    } finally {
      setDevLoginLoading(false);
    }
  };

  return (
    <>
      <PageHeader showLogo={true} showMenu={true} />
      
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-[1400px] mx-auto bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between gap-4 p-6 border-b border-border bg-gradient-theme">
            <h1 className="text-2xl font-extrabold tracking-wide opacity-90">
              Sopira Magic System
            </h1>
            <span className="text-sm text-muted-foreground">
              Welcome to the professional config-driven management system
            </span>
          </div>

          <div className="p-6">
            {/* Top Collage - 3 images */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <img 
                src="/collage/collage-1.jpg" 
                alt="System feature 1" 
                className="w-full h-48 object-cover rounded-lg shadow-md"
                loading="lazy"
              />
              <img 
                src="/collage/collage-2.jpg" 
                alt="System feature 2" 
                className="w-full h-48 object-cover rounded-lg shadow-md"
                loading="lazy"
              />
              <img 
                src="/collage/collage-3.jpg" 
                alt="System feature 3" 
                className="w-full h-48 object-cover rounded-lg shadow-md"
                loading="lazy"
              />
            </div>

            {/* Feature Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Real-time Monitoring */}
              <div 
                onClick={() => handleCardClick('monitoring')}
                className="bg-gradient-theme-card rounded-xl p-6 border border-border shadow-sm flex flex-col cursor-pointer hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3 mb-3">
                  <Flame className="w-6 h-6 text-primary" />
                  <h3 className="text-lg font-bold text-primary">
                    Real-time Monitoring
                  </h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                  Monitor measurements in real-time with advanced analytical tools.
                </p>
              </div>

              {/* Historical Analysis */}
              <div 
                onClick={() => handleCardClick('analysis')}
                className="bg-gradient-theme-card rounded-xl p-6 border border-border shadow-sm flex flex-col cursor-pointer hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3 mb-3">
                  <BarChart3 className="w-6 h-6 text-primary" />
                  <h3 className="text-lg font-bold text-primary">
                    Historical Analysis
                  </h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                  Analyze trends and patterns in your data using advanced tools.
                </p>
              </div>

              {/* Factory Management */}
              <div 
                onClick={() => handleCardClick('management')}
                className="bg-gradient-theme-card rounded-xl p-6 border border-border shadow-sm flex flex-col cursor-pointer hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3 mb-3">
                  <Factory className="w-6 h-6 text-primary" />
                  <h3 className="text-lg font-bold text-primary">
                    Factory Management
                  </h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                  Centralized management of all production facilities and their configurations.
                </p>
              </div>
            </div>

            {/* Bottom Collage - 3 images */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <img 
                src="/collage/collage-4.jpg" 
                alt="System feature 4" 
                className="w-full h-48 object-cover rounded-lg shadow-md"
                loading="lazy"
              />
              <img 
                src="/collage/collage-5.jpg" 
                alt="System feature 5" 
                className="w-full h-48 object-cover rounded-lg shadow-md"
                loading="lazy"
              />
              <img 
                src="/collage/collage-6.jpg" 
                alt="System feature 6" 
                className="w-full h-48 object-cover rounded-lg shadow-md"
                loading="lazy"
              />
            </div>

            {/* Call-to-Action Section */}
            <div className="bg-gradient-theme-card rounded-xl p-6 border border-border shadow-sm text-center">
              <h2 className="text-xl font-bold text-foreground mb-4">
                Get Started with Sopira Magic
              </h2>
              <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                Sign in to your account to access advanced features and data management.
              </p>
              <div className="flex justify-center items-center gap-4">
                <Link to="/login">
                  <Button variant="solid">
                    Sign In
                  </Button>
                </Link>
                
                {/* DEV: Quick login buttons */}
                <div className="grid grid-cols-3 gap-2">
                  {TEST_USERS.map(user => (
                    <Button 
                      key={user.username}
                      variant="outline" 
                      onClick={() => handleDevLoginDirect(user.username, user.password)}
                      disabled={devLoginLoading}
                      className="border-orange-500 text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-950"
                    >
                      <Bug className="w-4 h-4 mr-2" />
                      {user.label}
                    </Button>
                  ))}
                </div>
                
                <Link to="/contact">
                  <Button variant="default">
                    Contact
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <BaseModal open={openModal === 'monitoring'} onClose={handleCloseModal} size="lg">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Flame className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-primary">Real-time Monitoring</h2>
            </div>
            <Button variant="ghost" size="sm" onClick={handleCloseModal} className="h-8 w-8 p-0">
              <X size={18} />
            </Button>
          </div>
          <div className="space-y-4">
            <img 
              src="/collage/collage-1.jpg" 
              alt="Real-time Monitoring" 
              className="w-full h-48 object-cover rounded-lg"
            />
            <div className="space-y-3 text-sm text-foreground leading-relaxed">
              <p>
                Our real-time monitoring system provides instant access to measurements as they occur, enabling immediate detection of anomalies and critical variations. The advanced analytical tools process data streams continuously, offering live insights into industrial processes without delay.
              </p>
              <p>
                The system supports multiple sensor types and can handle thousands of simultaneous measurements across different factory locations. Each measurement is validated in real-time, ensuring data integrity and reliability for critical decision-making processes.
              </p>
              <p>
                Interactive dashboards allow operators to customize their view, filtering by location, machine type, or specific measurement ranges. Alert systems can be configured to notify personnel immediately when thresholds are exceeded, preventing potential equipment damage or production issues.
              </p>
              <p>
                Historical context is integrated seamlessly with real-time data, allowing operators to compare current readings with past performance. This dual perspective enables predictive maintenance and trend analysis, helping optimize production efficiency and reduce downtime.
              </p>
            </div>
            <div className="flex justify-end pt-4 border-t border-border">
              <Button variant="solid" onClick={handleCloseModal}>Close</Button>
            </div>
          </div>
        </div>
      </BaseModal>

      <BaseModal open={openModal === 'analysis'} onClose={handleCloseModal} size="lg">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-primary">Historical Analysis</h2>
            </div>
            <Button variant="ghost" size="sm" onClick={handleCloseModal} className="h-8 w-8 p-0">
              <X size={18} />
            </Button>
          </div>
          <div className="space-y-4">
            <img 
              src="/collage/collage-2.jpg" 
              alt="Historical Analysis" 
              className="w-full h-48 object-cover rounded-lg"
            />
            <div className="space-y-3 text-sm text-foreground leading-relaxed">
              <p>
                Historical analysis capabilities enable deep insights into long-term measurement trends, identifying patterns that may not be apparent in real-time monitoring. The system stores years of measurement data with high precision, allowing for comprehensive retrospective studies.
              </p>
              <p>
                Advanced statistical tools help identify correlations between different measurement parameters, factory locations, and time periods. Machine learning algorithms can detect subtle patterns that human operators might miss, improving overall system intelligence and predictive accuracy.
              </p>
              <p>
                Customizable reporting features allow users to generate detailed analysis reports for specific time ranges, comparing performance across different production cycles or equipment configurations. Export capabilities support various formats, making it easy to share findings with stakeholders.
              </p>
              <p>
                Trend visualization tools provide intuitive graphical representations of historical data, making complex patterns easy to understand. Interactive charts allow drilling down into specific time periods or measurement categories, enabling detailed investigation of anomalies or performance improvements.
              </p>
            </div>
            <div className="flex justify-end pt-4 border-t border-border">
              <Button variant="solid" onClick={handleCloseModal}>Close</Button>
            </div>
          </div>
        </div>
      </BaseModal>

      <BaseModal open={openModal === 'management'} onClose={handleCloseModal} size="lg">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Factory className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold text-primary">Factory Management</h2>
            </div>
            <Button variant="ghost" size="sm" onClick={handleCloseModal} className="h-8 w-8 p-0">
              <X size={18} />
            </Button>
          </div>
          <div className="space-y-4">
            <img 
              src="/collage/collage-3.jpg" 
              alt="Factory Management" 
              className="w-full h-48 object-cover rounded-lg"
            />
            <div className="space-y-3 text-sm text-foreground leading-relaxed">
              <p>
                Centralized factory management provides comprehensive control over all production facilities, their configurations, and associated measurement equipment. The system supports multi-factory operations, allowing organizations to manage multiple locations from a single unified interface.
              </p>
              <p>
                Factory configuration management includes detailed settings for locations, carriers, drivers, pots, pits, and machines. Each component can be individually configured with specific parameters, tags, and operational settings that influence how measurements are collected and processed.
              </p>
              <p>
                User access control and scope management ensure that operators only see data relevant to their assigned factories or responsibilities. This feature is crucial for organizations with multiple production sites, maintaining data security while enabling efficient collaboration.
              </p>
              <p>
                Maintenance scheduling and equipment tracking capabilities help optimize factory operations by ensuring all measurement equipment is properly calibrated and maintained. Automated alerts notify managers when equipment requires attention, reducing downtime and maintaining measurement accuracy throughout the production network.
              </p>
            </div>
            <div className="flex justify-end pt-4 border-t border-border">
              <Button variant="solid" onClick={handleCloseModal}>Close</Button>
            </div>
          </div>
        </div>
      </BaseModal>
      <PageFooter />
    </>
  );
};

export default Home;
