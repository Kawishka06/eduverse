/**
 * API base URL for local dev, Netlify (frontend), and Vercel (optional Next proxy).
 *
 * Netlify: set NEXT_PUBLIC_API_URL to your Vercel API URL (e.g. https://eduverse-api.vercel.app).
 * Vercel frontend (if used): set API_URL + auto proxy via /api/backend.
 */

const LOCAL_API = "";

function siteOrigin(): string {
  const explicit = process.env.NEXT_PUBLIC_SITE_URL?.trim().replace(/\/$/, "");
  if (explicit) return explicit;
  const netlify =
    process.env.URL?.trim() || process.env.DEPLOY_PRIME_URL?.trim();
  if (netlify) return netlify.startsWith("http") ? netlify : `https://${netlify}`;
  const vercel = process.env.VERCEL_URL?.trim();
  if (vercel) return `https://${vercel}`;
  return "http://localhost:3000";
}

/** Use Next.js /api/backend proxy (Vercel-hosted frontend only). */
export function useApiProxy(): boolean {
  if (process.env.NEXT_PUBLIC_USE_API_PROXY === "1") return true;
  if (process.env.NEXT_PUBLIC_USE_API_PROXY === "0") return false;
  return Boolean(process.env.VERCEL) && Boolean(process.env.API_URL?.trim());
}

/** Direct FastAPI origin (required for Netlify; also WebSockets). */
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
