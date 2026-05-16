/** Build CSP directives; includes API + WebSocket origins for local dev. */

function collectApiOrigins(): string[] {
  const origins = new Set<string>([
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "ws://localhost:8000",
    "ws://127.0.0.1:8000",
  ]);

  const api = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (api) {
    try {
      const parsed = new URL(api);
      origins.add(parsed.origin);
      if (parsed.protocol === "http:") {
        origins.add(parsed.origin.replace(/^http/, "ws"));
      } else if (parsed.protocol === "https:") {
        origins.add(parsed.origin.replace(/^https/, "wss"));
      }
    } catch {
      // ignore invalid URL
    }
  }

  const supabase = process.env.NEXT_PUBLIC_SUPABASE_URL?.trim();
  if (supabase) {
    try {
      origins.add(new URL(supabase).origin);
    } catch {
      // ignore
    }
  }

  return [...origins];
}

export function buildContentSecurityPolicy(): string {
  const isDev = process.env.NODE_ENV !== "production";
  const connectSrc = ["'self'", "https:", "wss:", ...collectApiOrigins()];
  if (isDev) {
    connectSrc.push("ws:");
  }

  return [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' https: data: blob:",
    `connect-src ${connectSrc.join(" ")}`,
    "font-src 'self' data:",
    "frame-ancestors 'none'",
  ].join("; ");
}
