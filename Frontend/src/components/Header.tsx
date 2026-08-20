import { ShieldCheck } from 'lucide-react';
import { isMockMode } from '@/lib/api';
import { useI18n } from '@/i18n/I18nContext';
import LanguageSelector from '@/components/LanguageSelector';

export default function Header() {
  const { t } = useI18n();

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-600 shadow-sm">
            <ShieldCheck className="text-white" size={20} />
          </div>
          <div>
            <p className="text-base font-bold leading-tight text-slate-900">{t('header.brand')}</p>
            <p className="text-[11px] font-medium leading-tight text-slate-400">
              {t('header.tagline')}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {isMockMode && (
            <span className="hidden rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700 ring-1 ring-inset ring-amber-200 sm:inline">
              {t('header.demoMode')}
            </span>
          )}
          <LanguageSelector />
        </div>
      </div>
    </header>
  );
}
