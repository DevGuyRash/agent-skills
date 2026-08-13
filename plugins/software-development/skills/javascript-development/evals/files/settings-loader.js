export function loadSettings(raw) {
  return {
    enabled: raw.enabled || true,
    retries: raw.retries || 3,
    label: raw.label || "default",
  };
}
