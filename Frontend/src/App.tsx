import { useState } from 'react';
import type { Screen } from '@/types';
import Header from '@/components/Header';
import Home from '@/screens/Home';
import Report from '@/screens/Report';
import Track from '@/screens/Track';
import { useI18n } from '@/i18n/I18nContext';

function App() {
  const { t } = useI18n();
  const [screen, setScreen] = useState<Screen>('home');
  const [trackingId, setTrackingId] = useState('');

  const navigate = (s: Screen) => {
    setScreen(s);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <main>
        {screen === 'home' && <Home onNavigate={navigate} />}
        {screen === 'report' && (
          <Report
            onBack={() => navigate('home')}
            onTrack={(id) => {
              setTrackingId(id);
              navigate('track');
            }}
          />
        )}
        {screen === 'track' && <Track initialTrackingId={trackingId} onBack={() => navigate('home')} />}
      </main>

      <footer className="border-t border-slate-200/70 bg-slate-50">
        <div className="mx-auto max-w-5xl px-4 py-6 text-center sm:px-6">
          <p className="text-sm text-slate-400">{t('footer.tagline')}</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
