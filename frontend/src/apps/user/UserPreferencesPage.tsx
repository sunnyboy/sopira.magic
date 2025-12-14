//..............................................................
//   ~/sopira.magic/version_01/frontend/src/apps/user/UserPreferencesPage.tsx
//   UserPreferencesPage - User preferences and settings page
//   Allows users to configure their preferences (selected factories, general settings, etc.)
//   Based on TE UserPreferences.tsx with adaptations for SM project
//..............................................................

import { useEffect, useState } from 'react'
import { PageHeader } from '@/components/PageHeader'
import { PageFooter } from '@/components/PageFooter'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/contexts/AuthContext'
import { useScope } from '@/contexts/ScopeContext'
import { useTheme } from '@/contexts/ThemeContext'
import { FactorySelectionModal } from '@/components/modals/FactorySelectionModal'
import { API_BASE } from '@/config/api'
import { getMutatingHeaders } from '@/security/csrf'
import { User, Settings, Globe, Save, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'

interface UserPreferencesData {
  selected_factories: string[]
  general_settings?: {
    default_factories?: string[]
    currency?: string
    temperature_unit?: 'celsius' | 'fahrenheit'
    date_format?: string
    theme?: string
    theme_color?: string
    language?: string
    timezone?: string
  }
}

export function UserPreferencesPage() {
  const { user } = useAuth()
  const { selectedFactories, setSelectedFactories } = useScope()
  const { theme, setTheme, themeColor, setThemeColor } = useTheme()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [preferences, setPreferences] = useState<UserPreferencesData | null>(null)
  const [showDefaultFactoryModal, setShowDefaultFactoryModal] = useState(false)
  
  // Local state for settings
  const [currency, setCurrency] = useState<string>('EUR')
  const [temperatureUnit, setTemperatureUnit] = useState<'celsius' | 'fahrenheit'>('celsius')
  const [dateFormat, setDateFormat] = useState<string>('YYYY-MM-DD')
  const [language, setLanguage] = useState<string>('en')
  const [timezone, setTimezone] = useState<string>('UTC')
  const [defaultFactories, setDefaultFactories] = useState<string[]>([])

  // Load user preferences
  useEffect(() => {
    const loadPreferences = async () => {
      if (!user) return
      
      try {
        setLoading(true)
        const prefsUrl = API_BASE 
          ? `${API_BASE}/api/user/preferences/`
          : '/api/user/preferences/'
        const res = await fetch(prefsUrl, {
          credentials: 'include',
        })
        
        if (res.ok) {
          const data = await res.json()
          setPreferences(data)
          
          // Load settings from general_settings
          const settings = data.general_settings || {}
          setCurrency(settings.currency || 'EUR')
          setTemperatureUnit(settings.temperature_unit || 'celsius')
          setDateFormat(settings.date_format || 'YYYY-MM-DD')
          // Don't call setTheme/setThemeColor here - ThemeContext loads from backend itself in its own useEffect
          // We just sync the local state for display in the form
          setLanguage(settings.language || 'en')
          setTimezone(settings.timezone || 'UTC')
          setDefaultFactories(settings.default_factories || [])
        }
      } catch (err) {
        console.error('Failed to load preferences:', err)
        toast.error('Failed to load preferences')
      } finally {
        setLoading(false)
      }
    }

    loadPreferences()
  }, [user, setTheme, setThemeColor])

  const handleSave = async () => {
    try {
      setSaving(true)
      
      // Build general_settings object - merge with existing to preserve other settings
      const existingSettings = preferences?.general_settings || {}
      const updatedSettings = {
        ...existingSettings,
        default_factories: defaultFactories,
        currency: currency,
        temperature_unit: temperatureUnit,
        date_format: dateFormat,
        theme: theme, // Use theme from ThemeContext
        theme_color: themeColor, // Use theme color from ThemeContext
        language: language,
        timezone: timezone,
      }

      const body = {
        selected_factories: selectedFactories,
        general_settings: updatedSettings,
      }
      
      const prefsUrl = API_BASE 
        ? `${API_BASE}/api/user/preferences/`
        : '/api/user/preferences/'
      const res = await fetch(prefsUrl, {
        method: 'PUT',
        credentials: 'include',
        headers: getMutatingHeaders(),
        body: JSON.stringify(body),
      })

      if (res.ok) {
        toast.success('Preferences saved successfully!')
        // Reload preferences to sync state
        const data = await res.json()
        setPreferences(data)
      } else {
        const error = await res.json().catch(() => ({ error: 'Unknown error' }))
        toast.error(`Failed to save preferences: ${error.error || 'Unknown error'}`)
      }
    } catch (err) {
      console.error('Failed to save preferences:', err)
      toast.error('Failed to save preferences')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setSelectedFactories([])
    setDefaultFactories([])
    setCurrency('EUR')
    setTemperatureUnit('celsius')
    setDateFormat('YYYY-MM-DD')
    setLanguage('en')
    setTimezone('UTC')
    setTheme('auto')
    setThemeColor('blue')
    toast.info('Preferences reset to defaults')
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 py-6 space-y-4">
      <PageHeader showLogo={true} showMenu={true} />

      <div className="bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
        <Card className="border-0 shadow-none rounded-none">
          <CardHeader>
            <CardTitle className="text-xl">User Preferences</CardTitle>
            <CardDescription>
              Manage your account settings and preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-12 text-muted-foreground">
                Loading preferences...
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {/* Account Information */}
                  <Card className="flex flex-col">
                    <CardHeader>
                      <div className="flex items-center gap-3 mb-2">
                        <User className="w-6 h-6 text-primary" />
                        <CardTitle className="text-lg">Account Information</CardTitle>
                      </div>
                      <CardDescription>
                        View and manage your account details
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col gap-4">
                      <div className="space-y-3 text-sm">
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground">Username</Label>
                          <div className="text-sm mt-1 font-medium">{user?.username || '—'}</div>
                        </div>
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground">Email</Label>
                          <div className="text-sm mt-1 font-medium">{user?.email || 'Not set'}</div>
                        </div>
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground">Role</Label>
                          <div className="text-sm mt-1 font-medium">
                            {user?.role_display ?? user?.role ?? "Unknown"}
                          </div>
                        </div>
                        {user?.first_name || user?.last_name ? (
                          <div>
                            <Label className="text-xs font-semibold text-muted-foreground">Full Name</Label>
                            <div className="text-sm mt-1 font-medium">
                              {[user?.first_name, user?.last_name].filter(Boolean).join(' ') || '—'}
                            </div>
                          </div>
                        ) : null}
                        {user?.date_joined ? (
                          <div>
                            <Label className="text-xs font-semibold text-muted-foreground">Created</Label>
                            <div className="text-sm mt-1 font-medium">
                              {new Date(user.date_joined).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                              })}
                            </div>
                          </div>
                        ) : null}
                        {user?.last_login ? (
                          <div>
                            <Label className="text-xs font-semibold text-muted-foreground">Last Login</Label>
                            <div className="text-sm mt-1 font-medium">
                              {new Date(user.last_login).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </div>
                          </div>
                        ) : null}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Default Factory Selection */}
                  <Card className="flex flex-col">
                    <CardHeader>
                      <div className="flex items-center gap-3 mb-2">
                        <Settings className="w-6 h-6 text-primary" />
                        <CardTitle className="text-lg">Default Factory Selection</CardTitle>
                      </div>
                      <CardDescription>
                        Set default factories that will be loaded on login
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col gap-4">
                      <div className="space-y-3 text-sm">
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground">Default Factories</Label>
                          <div className="text-sm mt-1 font-medium">
                            {defaultFactories.length > 0 
                              ? `${defaultFactories.length} factory${defaultFactories.length !== 1 ? 'ies' : ''} selected`
                              : 'No default factories (all will be shown)'}
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">
                            These factories will be automatically selected when you log in. 
                            Leave empty to show all factories by default.
                          </p>
                        </div>
                      </div>
                      <div className="pt-4 border-t border-border">
                        <Button 
                          variant="default" 
                          size="sm" 
                          className="w-full"
                          onClick={() => setShowDefaultFactoryModal(true)}
                        >
                          Select Default Factories →
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  {/* System Settings */}
                  <Card className="flex flex-col">
                    <CardHeader>
                      <div className="flex items-center gap-3 mb-2">
                        <Globe className="w-6 h-6 text-primary" />
                        <CardTitle className="text-lg">System Settings</CardTitle>
                      </div>
                      <CardDescription>
                        Configure system preferences
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col gap-4">
                      <div className="space-y-4 text-sm">
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground mb-2 block">Interface Language</Label>
                          <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                          >
                            <option value="en">English</option>
                            <option value="sk">Slovenčina</option>
                            <option value="de">Deutsch</option>
                            <option value="es">Español</option>
                          </select>
                        </div>
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground mb-2 block">Timezone</Label>
                          <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            value={timezone}
                            onChange={(e) => setTimezone(e.target.value)}
                          >
                            <option value="UTC">UTC</option>
                            <option value="Europe/Bratislava">Europe/Bratislava</option>
                            <option value="Europe/Berlin">Europe/Berlin</option>
                            <option value="Europe/Madrid">Europe/Madrid</option>
                          </select>
                        </div>
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground mb-2 block">Currency</Label>
                          <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            value={currency}
                            onChange={(e) => setCurrency(e.target.value)}
                          >
                            <option value="EUR">EUR (€)</option>
                            <option value="USD">USD ($)</option>
                            <option value="GBP">GBP (£)</option>
                            <option value="CZK">CZK (Kč)</option>
                            <option value="PLN">PLN (zł)</option>
                          </select>
                        </div>
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground mb-2 block">Temperature Unit</Label>
                          <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            value={temperatureUnit}
                            onChange={(e) => setTemperatureUnit(e.target.value as 'celsius' | 'fahrenheit')}
                          >
                            <option value="celsius">Celsius (°C)</option>
                            <option value="fahrenheit">Fahrenheit (°F)</option>
                          </select>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Display Settings */}
                  <Card className="flex flex-col">
                    <CardHeader>
                      <div className="flex items-center gap-3 mb-2">
                        <Settings className="w-6 h-6 text-primary" />
                        <CardTitle className="text-lg">Display Settings</CardTitle>
                      </div>
                      <CardDescription>
                        Customize the appearance of the interface
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col gap-4">
                      <div className="space-y-4 text-sm">
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground mb-2 block">Theme</Label>
                          <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            value={theme}
                            onChange={(e) => {
                              const newTheme = e.target.value as 'light' | 'dark' | 'auto'
                              setTheme(newTheme) // This will apply immediately and save to localStorage
                            }}
                          >
                            <option value="auto">Auto (System)</option>
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                          </select>
                          <p className="text-xs text-muted-foreground mt-1">
                            Theme changes are applied immediately
                          </p>
                        </div>
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground mb-2 block">Theme Color</Label>
                          <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            value={themeColor}
                            onChange={(e) => {
                              const newColor = e.target.value as 'blue' | 'green' | 'orange'
                              setThemeColor(newColor) // This will apply immediately and save to localStorage
                            }}
                          >
                            <option value="blue">Blue</option>
                            <option value="green">Green</option>
                            <option value="orange">Orange</option>
                          </select>
                          <p className="text-xs text-muted-foreground mt-1">
                            Color scheme changes are applied immediately
                          </p>
                        </div>
                        <div>
                          <Label className="text-xs font-semibold text-muted-foreground mb-2 block">Date Format</Label>
                          <select 
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                            value={dateFormat}
                            onChange={(e) => setDateFormat(e.target.value)}
                          >
                            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                          </select>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
              </div>
            )}

            {/* Save Actions */}
            <div className="mt-8 p-6 border border-border rounded-xl bg-gradient-to-r from-primary/10 to-primary/5">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-2">Save Changes</h3>
                  <p className="text-sm text-muted-foreground">
                    Click the button below to save your preferences. Changes will be applied immediately.
                  </p>
                </div>
                <div className="flex gap-3">
                  <Button
                    variant="default"
                    size="default"
                    onClick={handleReset}
                    disabled={saving}
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                  <Button
                    variant="solid"
                    size="default"
                    onClick={handleSave}
                    disabled={saving}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Saving...' : 'Save Preferences'}
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Default Factory Selection Modal */}
      <FactorySelectionModal
        open={showDefaultFactoryModal}
        onClose={() => setShowDefaultFactoryModal(false)}
        onSave={(selectedIds) => {
          setDefaultFactories(selectedIds)
        }}
        initialSelection={defaultFactories}
        title="Select Default Factories"
        description="Choose factories that will be automatically selected when you log in"
      />
      <PageFooter />
    </div>
  )
}
