// src/utils/date.ts
// Canonical date helpers (local, no TZ shifts)
export const toIsoLocal = (d?: Date): string => {
  if (!d) return '';
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};

export const parseIsoLocal = (s?: string): Date | undefined => {
  if (!s) return undefined;
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return undefined;
  const y = parseInt(m[1], 10);
  const mo = parseInt(m[2], 10);
  const d = parseInt(m[3], 10);
  const dt = new Date(y, (mo || 1) - 1, d || 1);
  if (dt.getFullYear() !== y || dt.getMonth() !== mo - 1 || dt.getDate() !== d) return undefined;
  return dt;
};

export const toDisplayDate = (iso?: string): string => {
  if (!iso) return '';
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return '';
  return `${m[3]}.${m[2]}.${m[1]}`;
};

export const fromDisplayDate = (s?: string): string | null => {
  const t = (s || '').trim();
  if (!t) return '';
  // accept DD.MM.YYYY or DD.MM.YY
  const m = t.match(/^(\d{1,2})[.](\d{1,2})[.](\d{2}|\d{4})$/);
  if (!m) return null;
  let d = parseInt(m[1], 10);
  let mo = parseInt(m[2], 10);
  let y = parseInt(m[3], 10);
  if (y < 100) y = 2000 + y; // map 2-digit to 20YY
  const dt = new Date(y, (mo || 1) - 1, d || 1);
  if (dt.getFullYear() !== y || dt.getMonth() !== mo - 1 || dt.getDate() !== d) return null;
  const mm = String(mo).padStart(2, '0');
  const dd = String(d).padStart(2, '0');
  return `${y}-${mm}-${dd}`;
};