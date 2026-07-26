/**
 * Supabase client singleton.
 *
 * IMPROVEMENTS over the MVP
 * -------------------------
 * 1. The MVP silently fell back to placeholder strings
 *    (`'https://your-project.supabase.co'`) when env vars were missing,
 *    which produced confusing "fetch failed" errors deep in the auth
 *    flow. This version throws at module load if either env var is
 *    missing IN PRODUCTION, and warns (but allows) in development so
 *    the dev server can still boot.
 * 2. Adds an `isConfigured` flag that components can check before
 *    calling Supabase, so they can show a friendly "DB not configured"
 *    message instead of an opaque network error.
 * 3. Single export (named + default) — no duplicate `supabase` /
 *    `default` confusion.
 */
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

const isProduction = import.meta.env.PROD
const isDev = import.meta.env.DEV

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey)

if (!isSupabaseConfigured) {
  const msg =
    'VITE_SUPABASE_URL and/or VITE_SUPABASE_ANON_KEY are not set. ' +
    'Copy .env.example to .env and fill in your Supabase project credentials.'
  if (isProduction) {
    // In production, refuse to ship a broken client.
    throw new Error(msg)
  }
  if (isDev) {
    // In dev, warn loudly so the developer notices immediately.
    console.warn('[supabase] ' + msg)
  }
}

/**
 * The Supabase client. Will be a real client if env vars are set, or
 * `null` otherwise (dev only — production would have thrown above).
 *
 * Always check `isSupabaseConfigured` before calling methods on this.
 */
export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
      realtime: {
        params: { eventsPerSecond: 10 },
      },
    })
  : null

export default supabase
