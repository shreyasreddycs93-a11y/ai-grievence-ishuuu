import { FormEvent, useState } from 'react';
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  ChevronDown,
  Clock3,
  Copy,
  MapPin,
  RefreshCw,
  RotateCcw,
  Search,
  ShieldCheck,
  Star,
  ThumbsUp,
  XCircle,
} from 'lucide-react';
import ErrorBanner from '@/components/ErrorBanner';
import Spinner from '@/components/Spinner';
import { getGrievanceStatus, verifyGrievance } from '@/lib/api';
import { useI18n } from '@/i18n/I18nContext';
import type { GrievanceStatus, GrievanceStatusResponse, Subtask, TimelineEntry } from '@/types';

interface TrackProps {
  initialTrackingId?: string;
  onBack: () => void;
}

const STATUS_STYLES: Record<GrievanceStatus, string> = {
  new: 'bg-accent-50 text-accent-700 ring-accent-200',
  assigned: 'bg-primary-50 text-primary-700 ring-primary-200',
  in_progress: 'bg-warning-50 text-warning-800 ring-warning-200',
  escalated: 'bg-error-50 text-error-700 ring-error-200',
  resolved: 'bg-success-50 text-success-700 ring-success-200',
  closed: 'bg-slate-100 text-slate-600 ring-slate-200',
  reopened: 'bg-warning-50 text-warning-800 ring-warning-200',
};

const STATUS_DOT_STYLES: Record<GrievanceStatus, string> = {
  new: 'bg-accent-500',
  assigned: 'bg-primary-600',
  in_progress: 'bg-warning-500',
  escalated: 'bg-error-500',
  resolved: 'bg-success-600',
  closed: 'bg-slate-500',
  reopened: 'bg-warning-500',
};

function safeStatus(value: unknown): GrievanceStatus {
  const statuses: GrievanceStatus[] = [
    'new',
    'assigned',
    'in_progress',
    'escalated',
    'resolved',
    'closed',
    'reopened',
  ];
  return typeof value === 'string' && statuses.includes(value as GrievanceStatus)
    ? (value as GrievanceStatus)
    : 'new';
}

function formatDate(value: unknown, fallback = 'Update received'): string {
  if (typeof value !== 'string') return fallback;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return fallback;
  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date);
}

function normalizeResponse(data: GrievanceStatusResponse | null): GrievanceStatusResponse {
  const raw = (data || {}) as Partial<GrievanceStatusResponse>;
  const rawTimeline = Array.isArray(raw.timeline) ? raw.timeline : [];
  const rawSubtasks = Array.isArray(raw.subtasks) ? raw.subtasks : [];

  return {
    tracking_id: typeof raw.tracking_id === 'string' && raw.tracking_id ? raw.tracking_id : 'Unknown ID',
    status: safeStatus(raw.status),
    category: typeof raw.category === 'string' ? raw.category : 'Not specified',
    priority: typeof raw.priority === 'string' ? raw.priority : 'Not specified',
    department: typeof raw.department === 'string' ? raw.department : 'Civic department',
    summary: typeof raw.summary === 'string' && raw.summary ? raw.summary : 'No summary is available yet.',
    created_at: typeof raw.created_at === 'string' ? raw.created_at : '',
    sla_due_at: typeof raw.sla_due_at === 'string' ? raw.sla_due_at : '',
    timeline: rawTimeline.map((entry) => {
      const item = (entry || {}) as Partial<TimelineEntry>;
      return {
        status: typeof item.status === 'string' ? item.status : 'update',
        note: typeof item.note === 'string' && item.note ? item.note : 'Complaint updated',
        at: typeof item.at === 'string' ? item.at : '',
      };
    }),
    subtasks: rawSubtasks.map((subtask) => {
      const item = (subtask || {}) as Partial<Subtask>;
      return {
        id: typeof item.id === 'string' ? item.id : undefined,
        department: typeof item.department === 'string' ? item.department : 'Civic department',
        status: typeof item.status === 'string' ? item.status : 'new',
        category: typeof item.category === 'string' ? item.category : undefined,
        priority: typeof item.priority === 'string' ? item.priority : undefined,
        summary: typeof item.summary === 'string' ? item.summary : undefined,
        timeline: Array.isArray(item.timeline) ? item.timeline : [],
      };
    }),
  };
}

function StatusBadge({ status }: { status: string }) {
  const { t } = useI18n();
  const normalizedStatus = safeStatus(status);
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-bold ring-1 ring-inset ${STATUS_STYLES[normalizedStatus]}`}
    >
      <span className={`h-2 w-2 rounded-full ${STATUS_DOT_STYLES[normalizedStatus]}`} />
      {t(`status.${normalizedStatus}`)}
    </span>
  );
}

function Timeline({ entries }: { entries: TimelineEntry[] }) {
  const { t } = useI18n();

  if (!entries.length) {
    return (
      <div className="rounded-xl bg-slate-50 px-4 py-5 text-center text-sm text-slate-500 ring-1 ring-inset ring-slate-200">
        {t('track.timelineEmpty')}
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {entries.map((entry, index) => {
        const status = safeStatus(entry.status);
        const isLast = index === entries.length - 1;
        return (
          <div key={`${entry.at}-${index}`} className="relative flex gap-4 pb-6 last:pb-0">
            {!isLast && <div className="absolute left-[9px] top-5 h-full w-px bg-slate-200" />}
            <div className={`relative mt-1 h-5 w-5 shrink-0 rounded-full ring-4 ring-white ${STATUS_DOT_STYLES[status]}`} />
            <div className="min-w-0 flex-1">
              <div className="flex flex-col justify-between gap-1 sm:flex-row sm:gap-4">
                <p className="text-sm font-bold text-slate-800">{entry.note || t('track.timelineDefaultNote')}</p>
                <p className="shrink-0 text-xs font-medium text-slate-400">{formatDate(entry.at)}</p>
              </div>
              <p className="mt-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
                {t(`status.${status}`)}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function SubtaskCard({ subtask }: { subtask: Subtask }) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);
  const status = safeStatus(subtask.status);

  return (
    <div className="rounded-xl bg-white p-4 ring-1 ring-inset ring-slate-200">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary-50">
            <MapPin className="text-primary-600" size={18} />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-bold text-slate-900">{subtask.department || t('track.subtaskDefault')}</p>
            <p className="mt-0.5 text-xs text-slate-500">{subtask.category || t('track.subtaskDefault')}</p>
          </div>
        </div>
        <StatusBadge status={status} />
      </div>
      {subtask.summary && <p className="mt-3 text-sm leading-relaxed text-slate-600">{subtask.summary}</p>}
      {subtask.timeline?.length ? (
        <>
          <button
            type="button"
            onClick={() => setExpanded((current) => !current)}
            className="mt-3 inline-flex items-center gap-1 text-xs font-bold text-primary-600 hover:text-primary-700"
          >
            {expanded ? t('track.subtaskHide') : t('track.subtaskView', { count: subtask.timeline.length })}
            <ChevronDown className={`transition-transform ${expanded ? 'rotate-180' : ''}`} size={15} />
          </button>
          {expanded && <div className="mt-4 border-t border-slate-100 pt-4"><Timeline entries={subtask.timeline} /></div>}
        </>
      ) : null}
    </div>
  );
}

type VerifyState = 'idle' | 'loading' | 'confirmed' | 'reopened' | 'error';

function ResolutionPanel({ trackingId }: { trackingId: string }) {
  const { t } = useI18n();
  const [verifyState, setVerifyState] = useState<VerifyState>('idle');
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [ratingSubmitted, setRatingSubmitted] = useState(false);

  const handleVerify = async (confirmed: boolean) => {
    setVerifyError(null);
    setVerifyState('loading');
    try {
      await verifyGrievance(trackingId, confirmed);
      setVerifyState(confirmed ? 'confirmed' : 'reopened');
    } catch {
      setVerifyState('error');
      setVerifyError(t('resolution.error'));
    }
  };

  const handleStarClick = (value: number) => {
    setRating(value);
  };

  const submitRating = () => {
    if (rating > 0) setRatingSubmitted(true);
  };

  if (verifyState === 'loading') {
    return (
      <div className="card flex flex-col items-center justify-center px-6 py-10 text-center">
        <Spinner className="text-primary-600" />
        <p className="mt-4 text-sm font-semibold text-slate-700">{t('resolution.submitting')}</p>
      </div>
    );
  }

  if (verifyState === 'error') {
    return (
      <div className="card p-5 sm:p-6">
        {verifyError && <ErrorBanner message={verifyError} />}
        <button
          type="button"
          onClick={() => setVerifyState('idle')}
          className="btn-secondary mt-4 w-full"
        >
          {t('resolution.tryAgain')}
        </button>
      </div>
    );
  }

  if (verifyState === 'confirmed' || verifyState === 'reopened') {
    const isConfirmed = verifyState === 'confirmed';
    return (
      <div className="card overflow-hidden animate-scale-in">
        <div className={`px-5 py-5 text-center sm:px-6 ${isConfirmed ? 'bg-success-50' : 'bg-warning-50'}`}>
          <div className={`mx-auto flex h-14 w-14 items-center justify-center rounded-full ${isConfirmed ? 'bg-success-100' : 'bg-warning-100'}`}>
            {isConfirmed ? <CheckCircle2 className="text-success-700" size={28} /> : <RotateCcw className="text-warning-700" size={28} />}
          </div>
          <h3 className="mt-3 text-lg font-bold text-slate-900">
            {isConfirmed ? t('resolution.confirmedTitle') : t('resolution.reopenedTitle')}
          </h3>
          <p className="mt-1 text-sm text-slate-600">
            {isConfirmed ? t('resolution.confirmedBody') : t('resolution.reopenedBody')}
          </p>
        </div>

        {isConfirmed && (
          <div className="p-5 sm:p-6">
            {ratingSubmitted ? (
              <div className="flex flex-col items-center py-4 text-center animate-fade-in">
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      size={28}
                      className={star <= rating ? 'fill-warning-400 text-warning-400' : 'text-slate-200'}
                    />
                  ))}
                </div>
                <p className="mt-3 text-sm font-semibold text-slate-700">
                  {t('resolution.ratingThanks')}
                </p>
                <p className="mt-1 text-xs text-slate-500">{t('resolution.ratingBody')}</p>
              </div>
            ) : (
              <>
                <p className="text-center text-sm font-bold text-slate-900">
                  {t('resolution.ratingPrompt')}
                </p>
                <div className="mt-4 flex justify-center gap-1.5">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => handleStarClick(star)}
                      onMouseEnter={() => setHoverRating(star)}
                      onMouseLeave={() => setHoverRating(0)}
                      aria-label={t('resolution.star', { count: star })}
                      className="rounded-lg p-1 transition-transform hover:scale-110 active:scale-95"
                    >
                      <Star
                        size={32}
                        className={star <= (hoverRating || rating) ? 'fill-warning-400 text-warning-400' : 'fill-none text-slate-300'}
                      />
                    </button>
                  ))}
                </div>
                {rating > 0 && (
                  <button
                    type="button"
                    onClick={submitRating}
                    className="btn-primary mt-5 w-full animate-fade-in"
                  >
                    {t('resolution.ratingSubmit')}
                  </button>
                )}
              </>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="card p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-success-50">
          <CheckCircle2 className="text-success-600" size={22} />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900">{t('resolution.title')}</h3>
          <p className="mt-1 text-sm text-slate-500">{t('resolution.subtitle')}</p>
        </div>
      </div>
      <div className="mt-5 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={() => handleVerify(true)}
          className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-success-600 px-5 py-3.5 text-sm font-bold text-white shadow-sm transition-all hover:bg-success-700 hover:shadow-md active:scale-[0.98]"
        >
          <ThumbsUp size={18} />
          {t('resolution.confirm')}
        </button>
        <button
          type="button"
          onClick={() => handleVerify(false)}
          className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-white px-5 py-3.5 text-sm font-bold text-error-700 ring-1 ring-inset ring-error-200 transition-all hover:bg-error-50 hover:ring-error-300 active:scale-[0.98]"
        >
          <XCircle size={18} />
          {t('resolution.reopen')}
        </button>
      </div>
    </div>
  );
}

export default function Track({ initialTrackingId = '', onBack }: TrackProps) {
  const { t } = useI18n();
  const [trackingId, setTrackingId] = useState(initialTrackingId);
  const [result, setResult] = useState<GrievanceStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isCopied, setIsCopied] = useState(false);

  const checkStatus = async (event?: FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
    const value = trackingId.trim();
    if (!value) {
      setError(t('track.errorEmpty'));
      return;
    }

    setError(null);
    setResult(null);
    setIsLoading(true);
    try {
      const response = await getGrievanceStatus(value);
      setResult(normalizeResponse(response));
    } catch {
      setError(t('track.errorNotFound'));
    } finally {
      setIsLoading(false);
    }
  };

  const copyTrackingId = async () => {
    const value = result?.tracking_id;
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setIsCopied(true);
      window.setTimeout(() => setIsCopied(false), 1800);
    } catch {
      setError(t('track.errorCopy'));
    }
  };

  return (
    <section className="mx-auto max-w-2xl px-4 py-8 sm:px-6 sm:py-10">
      <button
        type="button"
        onClick={onBack}
        className="group inline-flex items-center gap-2 text-sm font-semibold text-slate-500 transition-colors hover:text-primary-600"
      >
        <ArrowLeft size={17} className="transition-transform group-hover:-translate-x-1" />
        {t('track.back')}
      </button>

      <div className="mt-8">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50">
            <Search className="text-primary-600" size={23} />
          </div>
          <div>
            <p className="text-sm font-semibold text-primary-600">{t('track.eyebrow')}</p>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">{t('track.title')}</h1>
          </div>
        </div>
        <p className="mt-4 leading-relaxed text-slate-600">{t('track.subtitle')}</p>
      </div>

      <form onSubmit={checkStatus} className="card mt-7 p-5 sm:p-6">
        <label htmlFor="tracking-id" className="block text-sm font-bold text-slate-900">{t('track.idLabel')}</label>
        <div className="mt-3 flex flex-col gap-3 sm:flex-row">
          <input
            id="tracking-id"
            value={trackingId}
            onChange={(event) => setTrackingId(event.target.value)}
            placeholder={t('track.idPlaceholder')}
            autoCapitalize="characters"
            className="min-w-0 flex-1 rounded-xl border-0 bg-slate-50 px-4 py-3.5 text-base font-semibold uppercase tracking-wide text-slate-800 outline-none ring-1 ring-inset ring-slate-200 transition focus:bg-white focus:ring-2 focus:ring-primary-500"
          />
          <button type="submit" disabled={isLoading} className="btn-primary shrink-0 sm:px-5">
            {isLoading ? <Spinner /> : <Search size={19} />}
            {isLoading ? t('track.checking') : t('track.check')}
          </button>
        </div>
        <p className="mt-3 text-xs text-slate-400">{t('track.demoHint')}</p>
      </form>

      {error && <div className="mt-5"><ErrorBanner message={error} /></div>}

      {isLoading && (
        <div className="card mt-5 flex flex-col items-center justify-center px-6 py-14 text-center">
          <Spinner className="text-primary-600" />
          <p className="mt-4 text-sm font-semibold text-slate-700">{t('track.loadingTitle')}</p>
          <p className="mt-1 text-sm text-slate-500">{t('track.loadingBody')}</p>
        </div>
      )}

      {result && !isLoading && (
        <div className="mt-6 space-y-5 animate-fade-in">
          <div className="card overflow-hidden">
            <div className="border-b border-slate-100 bg-slate-50/70 px-5 py-4 sm:px-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{t('track.trackingIdLabel')}</p>
                  <div className="mt-1 flex items-center gap-2">
                    <p className="text-lg font-extrabold tracking-wide text-slate-900">{result.tracking_id}</p>
                    <button
                      type="button"
                      onClick={copyTrackingId}
                      aria-label={t('track.copyLabel')}
                      className="rounded-md p-1.5 text-slate-400 transition-colors hover:bg-white hover:text-primary-600"
                    >
                      {isCopied ? <CheckCircle2 size={17} className="text-success-600" /> : <Copy size={17} />}
                    </button>
                  </div>
                </div>
                <StatusBadge status={result.status} />
              </div>
            </div>

            <div className="p-5 sm:p-6">
              <p className="text-xs font-bold uppercase tracking-wider text-primary-600">{t('track.aiSummary')}</p>
              <p className="mt-2 text-lg font-semibold leading-relaxed text-slate-900">{result.summary}</p>
              <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
                <div className="rounded-xl bg-slate-50 p-3.5 ring-1 ring-inset ring-slate-100">
                  <p className="text-xs font-medium text-slate-400">{t('track.metaCategory')}</p>
                  <p className="mt-1 text-sm font-bold text-slate-800">{result.category || t('track.notSpecified')}</p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3.5 ring-1 ring-inset ring-slate-100">
                  <p className="text-xs font-medium text-slate-400">{t('track.metaPriority')}</p>
                  <p className="mt-1 text-sm font-bold capitalize text-slate-800">{result.priority || t('track.notSpecified')}</p>
                </div>
                <div className="col-span-2 rounded-xl bg-slate-50 p-3.5 ring-1 ring-inset ring-slate-100 sm:col-span-1">
                  <p className="text-xs font-medium text-slate-400">{t('track.metaDepartment')}</p>
                  <p className="mt-1 text-sm font-bold text-slate-800">{result.department}</p>
                </div>
              </div>
              {result.sla_due_at && (
                <div className="mt-4 flex items-center gap-2 text-xs font-medium text-slate-500">
                  <Clock3 size={15} className="text-slate-400" />
                  {t('track.slaDue', { date: formatDate(result.sla_due_at, t('track.slaFallback')) })}
                </div>
              )}
            </div>
          </div>

          <div className="card p-5 sm:p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900">{t('track.timelineTitle')}</h2>
                <p className="mt-1 text-sm text-slate-500">{t('track.timelineSubtitle')}</p>
              </div>
              <RefreshCw className="text-slate-300" size={20} />
            </div>
            <div className="mt-6"><Timeline entries={result.timeline} /></div>
          </div>

          {result.subtasks.length > 0 && (
            <div className="card p-5 sm:p-6">
              <div>
                <h2 className="text-lg font-bold text-slate-900">{t('track.subtasksTitle')}</h2>
                <p className="mt-1 text-sm text-slate-500">{t('track.subtasksSubtitle')}</p>
              </div>
              <div className="mt-5 space-y-3">
                {result.subtasks.map((subtask, index) => <SubtaskCard key={subtask.id || `${subtask.department}-${index}`} subtask={subtask} />)}
              </div>
            </div>
          )}

          {result.status === 'resolved' && <ResolutionPanel trackingId={result.tracking_id} />}

          <div className="flex items-start gap-3 rounded-xl bg-primary-50 px-4 py-3.5 ring-1 ring-inset ring-primary-100">
            <ShieldCheck className="mt-0.5 shrink-0 text-primary-600" size={19} />
            <p className="text-sm leading-relaxed text-primary-800">{t('track.securityNote')}</p>
          </div>
        </div>
      )}

      {!result && !isLoading && !error && (
        <div className="mt-8 flex flex-col items-center px-6 py-10 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
            <AlertCircle className="text-slate-400" size={26} />
          </div>
          <h2 className="mt-4 text-lg font-bold text-slate-800">{t('track.emptyTitle')}</h2>
          <p className="mt-1 max-w-sm text-sm leading-relaxed text-slate-500">{t('track.emptyBody')}</p>
        </div>
      )}
    </section>
  );
}
