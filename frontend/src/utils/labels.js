export const CATEGORY_LABELS = {
  organizational: 'Organizacional',
  people: 'Pessoas',
  physical: 'Fisico',
  technological: 'Tecnologico',
  annex_a1: 'Anexo A1 — Controlador',
  annex_a2: 'Anexo A2 — Operador',
  privacy: 'Privacidade',
}

export function categoryLabel(category) {
  return CATEGORY_LABELS[category] || category
}
