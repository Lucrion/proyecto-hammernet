// Utilidades para trabajar con RUT (formato UI y envío)
export function cleanRutInput(value) {
  // Limpiar y limitar a 9 caracteres (cuerpo hasta 8 + DV), excluyendo guion
  return String(value ?? '')
    .replace(/[^0-9kK]/g, '')
    .toUpperCase()
    .slice(0, 9);
}

export function digitsOnly(value) {
  return String(value ?? '').replace(/\D/g, '');
}

// Cálculo del dígito verificador (DV) para un RUT
export function computeRutDV(digits) {
  const body = digitsOnly(digits);
  if (!body) return '';
  let sum = 0;
  let factor = 2;
  for (let i = body.length - 1; i >= 0; i--) {
    sum += Number(body[i]) * factor;
    factor = factor === 7 ? 2 : factor + 1;
  }
  const rest = 11 - (sum % 11);
  if (rest === 11) return '0';
  if (rest === 10) return 'K';
  return String(rest);
}

// Formatear valor ingresado (puede incluir DV al final) como UI: XX.XXX.XXX-DV
export function formatRutUI(value) {
  const cleaned = cleanRutInput(value);
  if (!cleaned) return '';
  if (cleaned.length === 1) return cleaned;
  const dv = cleaned.slice(-1);
  let body = cleaned.slice(0, -1);
  // Permitir cuerpo hasta 8 dígitos
  body = body.slice(0, 8);
  let formatted = '';
  while (body.length > 3) {
    formatted = '.' + body.slice(-3) + formatted;
    body = body.slice(0, -3);
  }
  formatted = body + formatted + '-' + dv;
  return formatted;
}

// Formatear desde solo dígitos (sin DV) calculando DV automáticamente
export function formatRutFromDigits(digits) {
  // El cuerpo del RUT (sin DV) se limita a 8 dígitos
  const body = digitsOnly(digits).slice(0, 8);
  if (!body) return '';
  const dv = computeRutDV(body);
  let formatted = '';
  let tmp = body;
  while (tmp.length > 3) {
    formatted = '.' + tmp.slice(-3) + formatted;
    tmp = tmp.slice(0, -3);
  }
  formatted = tmp + formatted + '-' + dv;
  return formatted;
}