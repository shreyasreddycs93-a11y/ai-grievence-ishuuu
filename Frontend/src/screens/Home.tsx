import {
  ArrowRight,
  ClipboardList,
  Search,
  ShieldCheck,
  Clock,
  MapPin,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import type { Screen } from '@/types';
import { useI18n } from '@/i18n/I18nContext';

interface HomeProps {
  onNavigate: (screen: Screen) => void;
}

export default function Home({ onNavigate }: HomeProps) {
  const { t } = useI18n();

  const STATS = [
    { label: t('home.stats.resolved'), value: '12,847', icon: TrendingUp },
    { label: t('home.stats.responseTime'), value: '4.2 hrs', icon: Clock },
    { label: t('home.stats.departments'), value: '28', icon: MapPin },
  ];

  const FEATURES = [
    {
      icon: Sparkles,
      title: t('home.feature.routing.title'),
      description: t('home.feature.routing.desc'),
    },
    {
      icon: Clock,
      title: t('home.feature.tracking.title'),
      description: t('home.feature.tracking.desc'),
    },
    {
      icon: ShieldCheck,
      title: t('home.feature.secure.title'),
      description: t('home.feature.secure.desc'),
    },
  ];

  const CATEGORIES = [
    { label: t('home.category.water'), emoji: '💧' },
    { label: t('home.category.potholes'), emoji: '🛣️' },
    { label: t('home.category.garbage'), emoji: '🗑️' },
    { label: t('home.category.streetlights'), emoji: '💡' },
    { label: t('home.category.drainage'), emoji: '🚰' },
    { label: t('home.category.trees'), emoji: '🌳' },
  ];

  return (
    <div className="animate-fade-in">
      {/* Hero */}
      <section className="relative overflow-hidden">
        {/* Background decoration */}
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -top-32 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-primary-200/40 blur-3xl" />
          <div className="absolute right-0 top-20 h-48 w-48 rounded-full bg-accent-200/30 blur-3xl" />
        </div>

        <div className="mx-auto max-w-5xl px-4 pt-10 pb-6 sm:px-6 sm:pt-16">
          {/* Hero content */}
          <div className="mt-8 text-center sm:mt-12">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary-50 px-4 py-1.5 text-sm font-medium text-primary-700 ring-1 ring-inset ring-primary-200">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary-500 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary-600" />
              </span>
              {t('home.badge')}
            </div>

            <h1 className="mt-5 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
              {t('home.heroTitlePre')}{' '}
              <span className="bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                {t('home.heroTitleHighlight')}
              </span>
            </h1>

            <p className="mx-auto mt-4 max-w-xl text-lg leading-relaxed text-slate-600">
              {t('home.heroSubtitle')}
            </p>

            {/* CTA buttons */}
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <button
                onClick={() => onNavigate('report')}
                className="btn-primary group text-base sm:text-lg sm:px-8 sm:py-4"
              >
                <ClipboardList size={22} />
                {t('home.ctaReport')}
                <ArrowRight
                  size={20}
                  className="transition-transform duration-200 group-hover:translate-x-1"
                />
              </button>
              <button
                onClick={() => onNavigate('track')}
                className="btn-secondary text-base sm:text-lg sm:px-8 sm:py-4"
              >
                <Search size={22} />
                {t('home.ctaTrack')}
              </button>
            </div>

            <p className="mt-4 text-sm text-slate-400">{t('home.ctaNote')}</p>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="mx-auto max-w-5xl px-4 py-6 sm:px-6">
        <div className="grid grid-cols-3 gap-3 sm:gap-4">
          {STATS.map((stat) => (
            <div key={stat.label} className="card p-4 text-center sm:p-5">
              <stat.icon className="mx-auto mb-2 text-primary-500" size={22} />
              <p className="text-xl font-bold text-slate-900 sm:text-2xl">{stat.value}</p>
              <p className="mt-0.5 text-[11px] font-medium text-slate-500 sm:text-xs">
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Category chips */}
      <section className="mx-auto max-w-5xl px-4 py-6 sm:px-6">
        <h2 className="mb-4 text-center text-sm font-semibold uppercase tracking-wide text-slate-400">
          {t('home.categoriesTitle')}
        </h2>
        <div className="flex flex-wrap justify-center gap-2.5">
          {CATEGORIES.map((cat) => (
            <div
              key={cat.label}
              className="inline-flex items-center gap-2 rounded-full bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700 ring-1 ring-inset ring-slate-200 transition-colors hover:bg-primary-50 hover:text-primary-700 hover:ring-primary-200"
            >
              <span className="text-base">{cat.emoji}</span>
              {cat.label}
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-4 py-8 sm:px-6 sm:py-12">
        <div className="grid gap-4 sm:grid-cols-3 sm:gap-6">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="card p-6 transition-all duration-200 hover:shadow-card-hover hover:-translate-y-0.5"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50">
                <feature.icon className="text-primary-600" size={22} />
              </div>
              <h3 className="mt-4 text-base font-bold text-slate-900">{feature.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="mx-auto max-w-5xl px-4 pb-12 sm:px-6 sm:pb-16">
        <div className="overflow-hidden rounded-2xl bg-gradient-to-br from-primary-600 to-primary-800 px-6 py-8 text-center shadow-lg sm:px-12 sm:py-10">
          <h2 className="text-2xl font-bold text-white sm:text-3xl">{t('home.bottomCta.title')}</h2>
          <p className="mx-auto mt-2 max-w-md text-primary-100">{t('home.bottomCta.subtitle')}</p>
          <button
            onClick={() => onNavigate('report')}
            className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-7 py-3.5 text-base font-semibold text-primary-700 shadow-md transition-all duration-200 hover:bg-primary-50 hover:shadow-lg active:scale-[0.98]"
          >
            <ClipboardList size={20} />
            {t('home.bottomCta.button')}
            <ArrowRight size={18} />
          </button>
        </div>
      </section>
    </div>
  );
}
