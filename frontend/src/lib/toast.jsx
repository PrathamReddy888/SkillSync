/**
 * Minimal toast notification system (no external dependency).
 *
 * USAGE
 * -----
 *   // In your app root:
 *   import { ToastProvider } from '../lib/toast'
 *   <ToastProvider>{children}</ToastProvider>
 *
 *   // Anywhere else (no hook required):
 *   import toast from '../lib/toast'
 *   toast.success('Saved!')
 *   toast.error('Something broke.')
 *
 * IMPLEMENTATION NOTES
 * --------------------
 * The MVP had two issues:
 *   1. `toast.js` and `toast.jsx` were identical duplicates.
 *   2. The singleton `_addToast` was never wired up — `ToastProvider`
 *      registered the function on its own local state but never
 *      assigned it to the module-level `_addToast`, so every call to
 *      `toast.success(...)` etc. silently fell through to `console.log`
 *      and the user never saw a toast.
 *
 * This version fixes (2): the provider registers itself into the
 * singleton on mount and unregisters on unmount, so the bare-import
 * `toast` object works from anywhere in the tree.
 */
import React, { useState, useEffect, createContext, useContext, useCallback } from 'react'
import { CheckCircle, XCircle, AlertCircle, X, Info } from 'lucide-react'

const ToastContext = createContext(null)

let toastCounter = 0

// Module-level singleton — set by <ToastProvider> on mount.
let _addToast = null

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info', duration = 3500) => {
    const id = ++toastCounter
    setToasts(ts => [...ts, { id, message, type }])
    // Auto-dismiss after `duration` ms.
    setTimeout(() => setToasts(ts => ts.filter(t => t.id !== id)), duration)
    return id
  }, [])

  const remove = useCallback((id) => setToasts(ts => ts.filter(t => t.id !== id)), [])

  // Wire the singleton on mount, unwire on unmount. This is the fix —
  // the MVP never assigned `_addToast`, so toasts were silently dropped.
  useEffect(() => {
    _addToast = addToast
    return () => { _addToast = null }
  }, [addToast])

  return (
    <ToastContext.Provider value={{ addToast, remove }}>
      {children}
      {/* Toast container */}
      <div style={{
        position: 'fixed', bottom: '20px', right: '20px', zIndex: 9999,
        display: 'flex', flexDirection: 'column', gap: '10px',
        maxWidth: '360px', pointerEvents: 'none',
      }}>
        {toasts.map(t => <Toast key={t.id} toast={t} onRemove={remove} />)}
      </div>
    </ToastContext.Provider>
  )
}

const ICONS = { success: CheckCircle, error: XCircle, warning: AlertCircle, info: Info }
const COLORS = { success: '#10B981', error: '#EF4444', warning: '#F59E0B', info: '#6366F1' }

function Toast({ toast, onRemove }) {
  const Icon = ICONS[toast.type] || Info
  const color = COLORS[toast.type] || '#6366F1'
  return (
    <div style={{
      background: '#111827', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px',
      padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '10px',
      fontFamily: 'Inter, sans-serif', fontSize: '14px', color: '#F1F5F9',
      boxShadow: '0 8px 30px rgba(0,0,0,0.4)', animation: 'slide-up 0.3s ease',
      borderLeft: `3px solid ${color}`, pointerEvents: 'auto',
    }}>
      <Icon size={16} style={{ color, flexShrink: 0 }} />
      <span style={{ flex: 1 }}>{toast.message}</span>
      <button
        onClick={() => onRemove(toast.id)}
        aria-label="Dismiss notification"
        style={{
          background: 'none', border: 'none', color: '#6B7280',
          cursor: 'pointer', padding: 0, display: 'flex',
        }}
      >
        <X size={14} />
      </button>
    </div>
  )
}

// Hook (for components that prefer context lookup over the singleton)
export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast requires ToastProvider')
  const { addToast } = ctx
  return {
    success: (msg) => addToast(msg, 'success'),
    error: (msg) => addToast(msg, 'error'),
    warning: (msg) => addToast(msg, 'warning'),
    info: (msg) => addToast(msg, 'info'),
    toast: (msg) => addToast(msg, 'info'),
  }
}

// Singleton-style global toast — usable from anywhere AFTER <ToastProvider>
// has mounted. Before mount (or in tests without a provider), it falls
// back to console methods so calls never throw.
const toast = {
  success: (m) => _addToast ? _addToast(m, 'success') : console.log('[toast:success]', m),
  error:   (m) => _addToast ? _addToast(m, 'error')   : console.error('[toast:error]', m),
  warning: (m) => _addToast ? _addToast(m, 'warning') : console.warn('[toast:warning]', m),
  info:    (m) => _addToast ? _addToast(m, 'info')    : console.log('[toast:info]', m),
}

// Allow `toast('msg')` as well as `toast.info('msg')`.
const toastProxy = (m, opts) => toast.info(m)
Object.assign(toastProxy, toast)
toastProxy.default = toastProxy

export default toastProxy
