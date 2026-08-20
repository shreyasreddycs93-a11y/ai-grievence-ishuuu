import { useEffect, useState } from 'react';
import { ArrowLeft, ChevronRight, FileText } from 'lucide-react';
import Spinner from '@/components/Spinner';
import ErrorBanner from '@/components/ErrorBanner';
import { getMyGrievances } from '@/lib/api';
import { useI18n } from '@/i18n/I18nContext';
import type { GrievanceStatus, MyGrievanceItem } from '@/types';

interface MyComplaintsProps {
  onBack: () => void;
  onTrack: (trackingId: string) => void;
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

function formatDate(value: string): string {
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' });
}

export default function MyComplaints({ onBack, onTrack }: MyComplaintsProps) {
  const { t } = useI18n();
  const [items, setItems] = useState<MyGrievanceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getMyGrievances()
      .then(setItems)
      .catch(() => setError(t('myComplaints.error')))
      .finally(() => setLoading(false));
  }, [t]);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <button
        onClick={onBack}
        className="mb-6 flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-primary-600"
      >
        <ArrowLeft size={16} />
        {t('myComplaints.back')}
      </button>

      <h1 className="text-2xl font-bold text-slate-900">{t('myComplaints.title')}</h1>
      <p className="mt-1 text-sm text-slate-500">{t('myComplaints.subtitle')}</p>

      <div className="mt-6">
        {loading && (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        )}

        {!loading && error && <ErrorBanner message={error} />}

        {!loading && !error && items.length === 0 && (
          <div className="card flex flex-col items-center gap-2 py-12 text-center">
            <FileText className="text-slate-300" size={32} />
            <p className="text-sm font-medium text-slate-600">{t('myComplaints.empty')}</p>
            <p className="max-w-xs text-xs text-slate-400">{t('myComplaints.emptyHint')}</p>
          </div>
        )}

        {!loading && !error && items.length > 0 && (
          <ul className="space-y-3">
            {items.map((item) => (
              <li key={item.tracking_id}>
                <button
                  onClick={() => onTrack(item.tracking_id)}
                  className="card flex w-full items-center justify-between gap-3 p-4 text-left transition-all hover:shadow-card-hover"
                >
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-primary-600">
                        {item.tracking_id}
                      </span>
                      <span
                        className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ring-1 ring-inset ${STATUS_STYLES[item.status]}`}
                      >
                        {t(`status.${item.status}`)}
                      </span>
                    </div>
                    <p className="mt-1.5 truncate text-sm text-slate-700">
                      {item.summary || t('myComplaints.noSummary')}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      {item.department || t('track.notSpecified')} &middot; {formatDate(item.created_at)}
                    </p>
                  </div>
                  <ChevronRight className="shrink-0 text-slate-300" size={18} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
