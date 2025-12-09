//*........................................................
//*       www/thermal_eye_ui/src/components/modals/UserSelectionModal.tsx
//*       Reusable modal for user selection (DRY)
//*       Analogous to FactorySelectionModal
//*........................................................

import React, { useState, useMemo, useEffect } from 'react';
import { BaseModal } from '@/components/modals/BaseModal';
import { Button } from '@/components/ui_custom/button';
import { Checkbox } from '@/components/ui_custom/checkbox';
import { TableSearch } from '@/components/ui_custom/table/TableSearch';
import { CheckSquare, Square, Users } from 'lucide-react';
import { API_BASE } from '@/config/api';

interface UserOption {
  id: string;  // UUID
  label: string;
  email?: string;
  is_staff: boolean;
  is_superuser: boolean;
}

interface UserSelectionModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (selectedIds: string[]) => void;  // UUID array
  initialSelection?: string[];  // UUID array
  title?: string;
  description?: string;
  excludeSuperusers?: boolean;
}

export function UserSelectionModal({
  open,
  onClose,
  onSave,
  initialSelection = [],
  title = 'Select Users',
  description = 'Choose users to share with',
  excludeSuperusers = true,
}: UserSelectionModalProps) {
  const [users, setUsers] = useState<UserOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>(initialSelection || []);  // UUID array

  // Load users
  useEffect(() => {
    if (open) {
      setLoading(true);
      fetch(`${API_BASE}/api/users/`, { credentials: 'include' })
        .then(res => res.json())
        .then(json => {
          if (json.ok) {
            let userList = json.users || [];
            
            // Filter out superusers if requested
            if (excludeSuperusers) {
              userList = userList.filter((u: any) => !u.is_superuser_role);
            }
            
            setUsers(userList.map((u: any) => ({
              id: u.id,
              label: u.username,
              email: u.email,
              is_staff: u.is_staff || false,
              is_superuser: u.is_superuser || false,
            })));
          }
        })
        .catch(err => {
          console.error('Failed to load users:', err);
        })
        .finally(() => setLoading(false));
    }
  }, [open, excludeSuperusers]);

  // Reset selection when modal opens
  useEffect(() => {
    if (open) {
      setSelectedIds(initialSelection);
      setSearch('');
    }
  }, [open, initialSelection]);

  // Filter users by search
  const filteredUsers = useMemo(() => {
    if (!search.trim()) return users;
    const searchLower = search.toLowerCase();
    return users.filter(u =>
      u.label.toLowerCase().includes(searchLower) ||
      (u.email && u.email.toLowerCase().includes(searchLower)) ||
      String(u.id).includes(searchLower)
    );
  }, [users, search]);

  const toggleUser = (id: string, checked: boolean) => {
    setSelectedIds(prev =>
      checked
        ? Array.from(new Set([...prev, id]))
        : prev.filter(x => x !== id)
    );
  };

  const selectAll = () => {
    setSelectedIds(filteredUsers.map(u => u.id));
  };

  const selectNone = () => {
    setSelectedIds([]);
  };

  const handleSave = () => {
    onSave(selectedIds);
    onClose();
  };

  return (
    <BaseModal
      open={open}
      onClose={onClose}
      size="md"
    >
      <div className="flex flex-col gap-4 p-4">
        {/* Title */}
        <div className="flex items-center gap-2 text-lg font-semibold border-b pb-3">
          <Users className="h-5 w-5" />
          <span>{title}</span>
        </div>

        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}

        {/* Search Field */}
        <div>
          <TableSearch
            value={search}
            onChange={setSearch}
            placeholder="Search users..."
          />
        </div>

        {/* Select All/None Buttons */}
        <div className="flex gap-2">
          <Button
            variant="default"
            size="sm"
            onClick={selectAll}
            className="flex-1"
          >
            <CheckSquare className="w-4 h-4 mr-1" />
            Select All
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={selectNone}
            className="flex-1"
          >
            <Square className="w-4 h-4 mr-1" />
            Select None
          </Button>
        </div>

        {/* Users List */}
        <div className="flex-1 overflow-auto max-h-96 border border-border rounded-md p-2 space-y-1">
          {loading ? (
            <div className="text-sm text-muted-foreground text-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
              Loading users...
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="text-sm text-muted-foreground text-center py-8">
              {users.length === 0 ? 'No users available' : 'No users found'}
            </div>
          ) : (
            filteredUsers.map(u => (
              <label
                key={u.id}
                className="flex items-center gap-2 text-sm cursor-pointer hover:bg-muted/50 px-2 py-2 rounded transition-colors"
              >
                <Checkbox
                  checked={selectedIds.includes(u.id)}
                  onCheckedChange={(checked) => toggleUser(u.id, checked === true)}
                  className="shrink-0"
                />
                <div className="flex-1 flex items-center justify-between min-w-0">
                  <div className="min-w-0 flex-1">
                    <div className="font-medium truncate" title={u.label}>{u.label}</div>
                    {u.email && (
                      <div className="text-xs text-muted-foreground truncate" title={u.email}>
                        {u.email}
                      </div>
                    )}
                  </div>
                  {(u.is_staff || u.is_admin || u.is_superuser_role) && (
                    <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded shrink-0 ml-2">
                      {u.is_superuser_role ? 'Superuser' : u.is_admin ? 'Admin' : 'Staff'}
                    </span>
                  )}
                </div>
              </label>
            ))
          )}
        </div>

        {/* Selected Count */}
        <div className="text-xs text-muted-foreground border-t border-border pt-2">
          {selectedIds.length > 0
            ? `${selectedIds.length} user${selectedIds.length !== 1 ? 's' : ''} selected`
            : 'No users selected'}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2 border-t border-border">
          <Button
            variant="default"
            size="sm"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            variant="solid"
            size="sm"
            onClick={handleSave}
            className="flex-1"
            disabled={selectedIds.length === 0}
          >
            Save
          </Button>
        </div>
      </div>
    </BaseModal>
  );
}


