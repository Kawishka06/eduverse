/**
 * API base URL resolution for local dev vs Vercel production.
 *
 * On Vercel, set API_URL (server) to your deployed FastAPI host and optionally
 * NEXT_PUBLIC_SITE_URL=https://eduverse-gold-mu.vercel.app
 * Browser traffic uses /api/backend proxy (same-origin, cookies work).
 */

const LOCAL_API = "http://localhost:8000";

function siteOrigin(): string {
  const explicit = process.env.NEXT_PUBLIC_SITE_URL?.trim().replace(/\/$/, "");
  if (explicit) return explicit;
  const vercel = process.env.VERCEL_URL?.trim();
  if (vercel) return `https://${vercel}`;
  return "http://localhost:3000";
}

/** True when requests should go through the Next.js BFF proxy. */
export function useApiProxy(): boolean {
  if (process.env.NEXT_PUBLIC_USE_API_PROXY === "1") return true;
  if (process.env.NEXT_PUBLIC_USE_API_PROXY === "0") return false;
  // Auto: proxy on Vercel when a server API_URL is configured
  return Boolean(process.env.VERCEL) && Boolean(process.env.API_URL?.trim());
}

/** Direct FastAPI origin (server-side proxy target, WebSockets). */
export function getBackendOrigin(): string {
  return (
    process.env.API_URL?.trim() ||
    process.env.NEXT_PUBLIC_API_URL?.trim() ||
    LOCAL_API
  ).replace(/\/$/, "");
}

/** Base URL for fetch() from browser or server components. */
export function getApiBase(options?: { server?: boolean }): string {
  if (useApiProxy()) {
    if (options?.server) {
      return `${siteOrigin()}/api/backend`;
    }
    return "/api/backend";
  }
  return getBackendOrigin();
}
