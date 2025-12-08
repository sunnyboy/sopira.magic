//*........................................................
//*       www/thermal_eye_ui/src/components/modals/ShareFactoryModal.tsx
//*       Share factories with users (assigns accessible_factories)
//*       Uses FormModal + UserSelectionModal for DRY architecture
//*........................................................

import { useState, useEffect } from 'react';
import { FormModal } from '@/components/modals/FormModal';
import { useApi } from '@/hooks/useApi';
import { useNotificationHandler } from '@/components/ui_custom/table/useNotificationHandler';
import { ErrorModal } from '@/components/modals/ErrorModal';
import { Share2, Users } from 'lucide-react';
import { UserSelectionModal } from './UserSelectionModal';
import { Button } from '@/components/ui_custom/button';

interface ShareFactoryModalProps {
  open: boolean;
  onClose: () => void;
  factoryIds: string[];  // Selected factories to share
  factoryNames?: string[]; // For display (optional)
  onSuccess?: () => void;  // Callback after successful share
}

export function ShareFactoryModal({ 
  open, 
  onClose, 
  factoryIds,
  factoryNames,
  onSuccess
}: ShareFactoryModalProps) {
  const [selectedUsers, setSelectedUsers] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const api = useApi();
  const { showSuccess, showError, error, isErrorModalOpen, closeErrorModal } = useNotificationHandler();

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setSelectedUsers([]);
    }
  }, [open]);

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedUsers.length === 0) {
      showError({ 
        operation: 'create',
        message: 'Please select at least one user to share with'
      });
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/api/factories/share/', {
        factory_ids: factoryIds,
        user_ids: selectedUsers,
        action: 'add'
      });

      if (response.ok) {
        showSuccess(response.message || `Factory access granted to ${selectedUsers.length} user${selectedUsers.length > 1 ? 's' : ''}`);
        onSuccess?.();
        onClose();
      } else {
        throw new Error(response.error || 'Share failed');
      }
    } catch (error: any) {
      showError({ 
        operation: 'create',
        message: error.message || 'Error sharing factory'
      });
    } finally {
      setLoading(false);
    }
  };

  const factoryCount = factoryIds.length;
  const displayNames = factoryNames && factoryNames.length > 0 
    ? factoryNames.slice(0, 3).join(', ') + (factoryNames.length > 3 ? `, +${factoryNames.length - 3} more` : '')
    : `${factoryCount} ${factoryCount === 1 ? 'factory' : 'factories'}`;

  return (
    <>
      <FormModal
        open={open}
        title="Share Factory Access"
        onClose={onClose}
        onSubmit={handleShare}
        submitText={loading ? 'Sharing...' : `Share to ${selectedUsers.length} user${selectedUsers.length !== 1 ? 's' : ''}`}
        size="md"
      >
        <div className="space-y-4">
          {/* Factory info */}
          <div className="bg-muted/50 rounded-md p-3 text-sm">
            <div className="font-medium mb-1 flex items-center gap-2">
              <Share2 className="h-4 w-4" />
              <span>Sharing:</span>
            </div>
            <div className="text-muted-foreground">{displayNames}</div>
          </div>

          {/* User selection */}
          <div>
            <div className="text-sm font-medium mb-2 flex items-center gap-2">
              <Users className="h-4 w-4" />
              <span>Grant access to users:</span>
            </div>
            
            {selectedUsers.length === 0 ? (
              <div className="border border-border rounded-md p-4 text-center">
                <p className="text-sm text-muted-foreground mb-3">No users selected</p>
                <Button
                  type="button"
                  variant="default"
                  size="sm"
                  onClick={() => setShowUserModal(true)}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Select Users
                </Button>
              </div>
            ) : (
              <div className="border border-border rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">
                    {selectedUsers.length} user{selectedUsers.length !== 1 ? 's' : ''} selected
                  </span>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowUserModal(true)}
                  >
                    Change Selection
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </FormModal>

      {/* User Selection Modal */}
      <UserSelectionModal
        open={showUserModal}
        onClose={() => setShowUserModal(false)}
        onSave={(ids) => {
          setSelectedUsers(ids);
          setShowUserModal(false);
        }}
        initialSelection={selectedUsers}
        excludeSuperusers={true}
      />

      {/* Error Modal */}
      <ErrorModal
        open={isErrorModalOpen}
        onClose={closeErrorModal}
        error={error}
      />
    </>
  );
}
