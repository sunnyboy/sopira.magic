// Core helper functions
export function formatDate(date: Date): string {
  return date.toLocaleDateString()
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount)
}

