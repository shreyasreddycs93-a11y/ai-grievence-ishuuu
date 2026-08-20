import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import type { Language } from '@/types';
import { FALLBACK_LANGUAGE, translations } from './translations';

interface I18nContextValue {
  locale: Language;
  t: (key: string, vars?: Record<string, string | number>) => string;
  changeLanguage: (lang: Language) => void;
}

const STORAGE_KEY = 'grievanceai-language';

const I18nContext = createContext<I18nContextValue | null>(null);

function getInitialLanguage(): Language {
  if (typeof window === 'undefined') return FALLBACK_LANGUAGE;
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === 'en' || stored === 'hi' || stored === 'kn') return stored;
  } catch {
    // localStorage unavailable; fall through to default
  }
  return FALLBACK_LANGUAGE;
}

function interpolate(template: string, vars?: Record<string, string | number>): string {
  if (!vars) return template;
  return template.replace(/\{\{(\w+)\}\}/g, (_, name: string) =>
    name in vars ? String(vars[name]) : `{{${name}}}`,
  );
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Language>(getInitialLanguage);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      const dict = translations[locale];
      const fallback = translations[FALLBACK_LANGUAGE];
      const raw = dict[key] ?? fallback[key] ?? key;
      return interpolate(raw, vars);
    },
    [locale],
  );

  const changeLanguage = useCallback((lang: Language) => {
    setLocale(lang);
    try {
      window.localStorage.setItem(STORAGE_KEY, lang);
    } catch {
      // localStorage unavailable; state still updates in-memory
    }
  }, []);

  const value = useMemo(() => ({ locale, t, changeLanguage }), [locale, t, changeLanguage]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return ctx;
}
