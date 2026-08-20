import { Globe } from 'lucide-react';
import { useI18n } from '@/i18n/I18nContext';
import { SUPPORTED_LANGUAGES } from '@/i18n/translations';

export default function LanguageSelector() {
  const { locale, changeLanguage } = useI18n();

  return (
    <div className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 p-1 ring-1 ring-slate-200/80">
      <Globe className="ml-1.5 shrink-0 text-slate-400" size={16} />
      {SUPPORTED_LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          className={`rounded-full px-3 py-1.5 text-sm font-semibold transition-all duration-200 ${
            locale === lang.code
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          {lang.label}
        </button>
      ))}
    </div>
  );
}
