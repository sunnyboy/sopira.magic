//*........................................................
//*       ~/sopira.magic/version_01/frontend/src/pages/Contact.tsx
//*       Contact page with support information
//*........................................................

import React from 'react';
import { PageHeader } from '@/components/PageHeader';
import { PageFooter } from '@/components/PageFooter';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui_custom/card';
import { Mail, CheckCircle2 } from 'lucide-react';

const Contact: React.FC = () => {
  return (
    <>
      <PageHeader showLogo={true} showMenu={true} />
      
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-[1400px] mx-auto bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between gap-4 p-6 border-b border-border bg-gradient-theme">
            <h1 className="text-2xl font-extrabold tracking-wide opacity-90">
              Contact Us
            </h1>
            <span className="text-sm text-muted-foreground">
              Get in touch with our support team
            </span>
          </div>

          <div className="p-6">
            {/* Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* System Info Card */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-2xl">🔥</span>
                    </div>
                    <CardTitle className="text-lg">Sopira Magic System</CardTitle>
                  </div>
                  <CardDescription>
                    Advanced config-driven management and analysis platform
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Sopira Magic is an advanced system for managing and analyzing data in industrial environments. 
                    It provides real-time monitoring, historical analysis, and advanced tools for managing industrial processes.
                  </p>
                </CardContent>
              </Card>

              {/* Support Email Card */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <Mail className="w-6 h-6 text-primary" />
                    <CardTitle className="text-lg">Support Email</CardTitle>
                  </div>
                  <CardDescription>
                    Technical questions and support requests
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <a 
                      href="mailto:support@sopira-magic.com"
                      className="text-sm font-semibold text-primary hover:underline block"
                    >
                      support@sopira-magic.com
                    </a>
                    <p className="text-xs text-muted-foreground">
                      For technical questions and support, please contact us via email. 
                      We typically respond within 24 hours during business days.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Features Section */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-primary" />
                  System Features
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <CheckCircle2 className="w-5 h-5 text-primary shrink-0" />
                    <span className="text-sm text-foreground">Real-time monitoring</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <CheckCircle2 className="w-5 h-5 text-primary shrink-0" />
                    <span className="text-sm text-foreground">Historical analysis</span>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <CheckCircle2 className="w-5 h-5 text-primary shrink-0" />
                    <span className="text-sm text-foreground">Advanced tools</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      <PageFooter />
    </>
  );
};

export default Contact;

