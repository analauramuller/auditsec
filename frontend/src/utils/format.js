export function formatAuditDate(value) {
  if (!value) return '—'
  const text = String(value)
  const [year, month, day] = text.split('T')[0].split('-')
  if (!year || !month || !day) return text
  return `${day}/${month}/${year}`
}
