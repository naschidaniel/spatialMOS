export default function formatNumber(value, digits) {
  if (value === undefined) return "–";
  return value.toLocaleString('de-AT', { style: 'decimal', minimumFractionDigits: digits, maximumFractionDigits: digits })
}