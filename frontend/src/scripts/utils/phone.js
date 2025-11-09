// Utilidades para números de teléfono en Chile
// UI: se ingresa solo el cuerpo (8 dígitos), mostrando prefijo "+569" fijo
// Backend: se envía normalizado como "+569" + 8 dígitos

export function digitsOnly(value) {
  return String(value ?? '').replace(/\D/g, '');
}

export function clampEightDigits(value) {
  return digitsOnly(value).slice(0, 8);
}

// Quita prefijo chileno de un número almacenado, para mostrar solo los 8 dígitos
export function stripCLPrefix(value) {
  return String(value ?? '').replace(/^\+?56\s?9\s?/, '').replace(/\s+/g, '');
}

// Normaliza para backend: asegura el formato "+569########"
export function normalizePhoneCL(value) {
  const body = clampEightDigits(value);
  return body ? `+569${body}` : '';
}

// Formateo visual simple: retorna solo los 8 dígitos (sin espacios)
export function formatPhoneUI(value) {
  return clampEightDigits(value);
}