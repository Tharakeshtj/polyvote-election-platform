import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react';
import { AlertTriangle, Check, CheckCircle2, Copy, Info, Vote, XCircle } from 'lucide-react';
import type { ElectionStatus } from '../api';

// ------------------------------------------------------------- brand + small bits

export function BrandMark() {
  return (
    <span className="brand-mark" aria-hidden>
      <Vote />
    </span>
  );
}

const STATUS_LABEL: Record<ElectionStatus, string> = { NOMINATION: 'Nominations', VOTING: 'Voting open', CLOSED: 'Closed' };

export function StatusBadge({ status }: { status: ElectionStatus }) {
  return <span className={`status status-${status.toLowerCase()}`}>{STATUS_LABEL[status] ?? status}</span>;
}

export function Spinner() {
  return <span className="spinner" role="status" aria-label="Loading" />;
}

/** Placeholder rows shaped like the list that is loading. */
export function PageLoading({ rows = 4 }: { rows?: number }) {
  return (
    <div className="skeleton-rows list" role="status" aria-label="Loading">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="list-row">
          <span className="skeleton" style={{ width: 32, height: 32, borderRadius: '50%' }} />
          <div className="stack-sm" style={{ flex: 1 }}>
            <span className="skeleton" style={{ width: `${40 + ((i * 17) % 30)}%` }} />
            <span className="skeleton" style={{ width: `${20 + ((i * 11) % 20)}%`, height: 10 }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function EmptyState({ icon, title, children }: { icon: ReactNode; title: string; children?: ReactNode }) {
  return (
    <div className="empty">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      {children && <div className="muted" style={{ maxWidth: 420, margin: '0 auto' }}>{children}</div>}
    </div>
  );
}

export function FormError({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div className="form-error" role="alert">
      <AlertTriangle />
      <span>{message}</span>
    </div>
  );
}

export function Avatar({ name }: { name: string }) {
  const initials = name.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]?.toUpperCase()).join('');
  return <span className="avatar" aria-hidden>{initials || '?'}</span>;
}

export function CopyButton({ text, label = 'Copy' }: { text: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      className="btn btn-sm"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
          setCopied(true);
          setTimeout(() => setCopied(false), 1600);
        } catch { /* clipboard blocked: the text is still selectable */ }
      }}
    >
      {copied ? <Check /> : <Copy />}
      {copied ? 'Copied' : label}
    </button>
  );
}

/** Indices of values that differ from the most common value (empty when all agree). */
export function outliers(values: number[]): Set<number> {
  const freq = new Map<number, number>();
  values.forEach((v) => freq.set(v, (freq.get(v) ?? 0) + 1));
  const majority = [...freq.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];
  return new Set(values.flatMap((v, i) => (v === majority ? [] : [i])));
}

export function shortHash(value: string, n = 10) {
  return value.length > n * 2 ? `${value.slice(0, n)}…${value.slice(-4)}` : value;
}

export function formatDate(value: string | null) {
  if (!value) return '—';
  const d = new Date(value.includes('T') ? value : value.replace(' ', 'T') + 'Z');
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

// ------------------------------------------------------------- lifecycle

const PHASES: { key: ElectionStatus; label: string }[] = [
  { key: 'NOMINATION', label: 'Nominations' },
  { key: 'VOTING', label: 'Voting' },
  { key: 'CLOSED', label: 'Closed' },
];

export function Lifecycle({ status }: { status: ElectionStatus }) {
  const current = PHASES.findIndex((p) => p.key === status);
  return (
    <div className="lifecycle" aria-label={`Election phase: ${status}`}>
      {PHASES.map((p, i) => {
        const done = i < current || status === 'CLOSED';
        return (
          <div key={p.key} style={{ display: 'contents' }}>
            {i > 0 && <span className={`lc-line ${i <= current ? 'done' : ''}`} />}
            <span className={`lc-step ${done ? 'done' : ''} ${i === current && !done ? 'current' : ''}`}>
              <span className="lc-dot">{done ? <Check /> : i + 1}</span>
              <span className="lc-label">{p.label}</span>
            </span>
          </div>
        );
      })}
    </div>
  );
}

// ------------------------------------------------------------- dialog

export function Modal({
  open, onClose, title, icon, tone = 'brand', children, footer,
}: {
  open: boolean; onClose: () => void; title: string; icon?: ReactNode; tone?: 'brand' | 'danger';
  children?: ReactNode; footer: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) {
      d.showModal();
      // showModal() focuses the first button; honour an explicit choice instead.
      d.querySelector<HTMLElement>('[data-autofocus]')?.focus();
    }
    if (!open && d.open) d.close();
  }, [open]);
  return (
    <dialog
      ref={ref}
      className="modal"
      onCancel={(ev) => { ev.preventDefault(); onClose(); }}
      onClick={(ev) => { if (ev.target === ref.current) onClose(); }}
    >
      {open && (
        <>
          <div className="modal-head">
            {icon && <div className={`modal-icon ${tone === 'danger' ? 'danger' : ''}`}>{icon}</div>}
            <h2>{title}</h2>
          </div>
          <div className="modal-body">{children}</div>
          <div className="modal-foot">{footer}</div>
        </>
      )}
    </dialog>
  );
}

export function ConfirmDialog({
  open, title, body, confirmLabel, tone = 'brand', icon, busy, onConfirm, onCancel,
}: {
  open: boolean; title: string; body: ReactNode; confirmLabel: string; tone?: 'brand' | 'danger';
  icon?: ReactNode; busy?: boolean; onConfirm: () => void; onCancel: () => void;
}) {
  return (
    <Modal
      open={open}
      onClose={busy ? () => {} : onCancel}
      title={title}
      tone={tone}
      icon={icon ?? (tone === 'danger' ? <AlertTriangle /> : <Info />)}
      footer={
        <>
          {/* Destructive dialogs default to Cancel so Enter can't trigger them by accident. */}
          <button className="btn" onClick={onCancel} disabled={busy} data-autofocus={tone === 'danger' ? '' : undefined}>Cancel</button>
          <button className={`btn ${tone === 'danger' ? 'btn-danger-solid' : 'btn-primary'}`} onClick={onConfirm} disabled={busy} data-autofocus={tone === 'danger' ? undefined : ''}>
            {busy && <Spinner />}
            {confirmLabel}
          </button>
        </>
      }
    >
      {body}
    </Modal>
  );
}

// ------------------------------------------------------------- toasts

type ToastKind = 'success' | 'error' | 'info';
interface ToastItem { id: number; kind: ToastKind; message: string }

const ToastContext = createContext<(kind: ToastKind, message: string) => void>(() => {});

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const push = useCallback((kind: ToastKind, message: string) => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, kind, message }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), kind === 'error' ? 6000 : 3500);
  }, []);
  return (
    <ToastContext.Provider value={push}>
      {children}
      <div className="toasts" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.kind}`}>
            {t.kind === 'success' ? <CheckCircle2 /> : t.kind === 'error' ? <XCircle /> : <Info />}
            <span>{t.message}</span>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);
