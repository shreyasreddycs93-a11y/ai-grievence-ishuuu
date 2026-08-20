import { ChangeEvent, FormEvent, useRef, useState } from 'react';
import {
  ArrowLeft,
  Camera,
  Check,
  ChevronRight,
  CircleStop,
  ClipboardList,
  Copy,
  FileAudio,
  ImagePlus,
  LocateFixed,
  MapPin,
  Mic,
  RefreshCw,
  ShieldCheck,
  X,
} from 'lucide-react';
import ErrorBanner from '@/components/ErrorBanner';
import Spinner from '@/components/Spinner';
import { submitIntake, uploadMedia } from '@/lib/api';
import { useI18n } from '@/i18n/I18nContext';
import type { IntakeResponse } from '@/types';

interface ReportProps {
  onBack: () => void;
  onTrack: (trackingId: string) => void;
}

type Coordinates = { latitude: number; longitude: number };

function formatCoordinates(coordinates: Coordinates): string {
  return `${coordinates.latitude.toFixed(5)}, ${coordinates.longitude.toFixed(5)}`;
}

export default function Report({ onBack, onTrack }: ReportProps) {
  const { t } = useI18n();
  const [description, setDescription] = useState('');
  const [address, setAddress] = useState('');
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [photoName, setPhotoName] = useState<string | null>(null);
  const [photoMediaUrl, setPhotoMediaUrl] = useState<string | null>(null);
  const [photoDescription, setPhotoDescription] = useState<string | null>(null);
  const [photoUploading, setPhotoUploading] = useState(false);
  const [voiceNote, setVoiceNote] = useState<string | null>(null);
  const [voiceMediaUrl, setVoiceMediaUrl] = useState<string | null>(null);
  const [voiceUploading, setVoiceUploading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isLocating, setIsLocating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<IntakeResponse | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioStreamRef = useRef<MediaStream | null>(null);

  const handlePhotoChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError(t('report.photoErrorType'));
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setPhotoPreview(typeof reader.result === 'string' ? reader.result : null);
      setPhotoName(file.name);
      setError(null);
    };
    reader.onerror = () => setError(t('report.photoErrorRead'));
    reader.readAsDataURL(file);

    setPhotoMediaUrl(null);
    setPhotoDescription(null);
    setPhotoUploading(true);
    uploadMedia(file, file.name)
      .then((result) => {
        setPhotoMediaUrl(result.media_url);
        setPhotoDescription(result.description || null);
      })
      .catch(() => setError(t('report.photoErrorRead')))
      .finally(() => setPhotoUploading(false));
  };

  const removePhoto = () => {
    setPhotoPreview(null);
    setPhotoName(null);
    setPhotoMediaUrl(null);
    setPhotoDescription(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleLocation = () => {
    if (!navigator.geolocation) {
      setError(t('report.locationUnavailable'));
      return;
    }

    setIsLocating(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      (position: GeolocationPosition) => {
        setCoordinates({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
        setIsLocating(false);
      },
      () => {
        setIsLocating(false);
        setError(t('report.locationError'));
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  const stopAudioStream = () => {
    audioStreamRef.current?.getTracks().forEach((track) => track.stop());
    audioStreamRef.current = null;
  };

  const toggleRecording = async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      setError(t('report.voiceUnavailable'));
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;
      audioChunksRef.current = [];
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      recorder.onstop = () => {
        stopAudioStream();
        const blob = new Blob(audioChunksRef.current, { type: recorder.mimeType || 'audio/webm' });
        setVoiceNote(t('report.voiceRecorded'));
        setVoiceUploading(true);
        uploadMedia(blob, 'voice-note.webm')
          .then((result) => {
            setVoiceMediaUrl(result.media_url);
            if (result.transcript) {
              setDescription((current) => (current.trim() ? current : result.transcript || ''));
            }
          })
          .catch(() => setError(t('report.voiceErrorUpload')))
          .finally(() => setVoiceUploading(false));
      };

      setVoiceNote(null);
      setVoiceMediaUrl(null);
      recorder.start();
      setIsRecording(true);
    } catch {
      setError(t('report.voicePermissionDenied'));
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!description.trim()) {
      setError(t('report.errorEmptyDescription'));
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      const media_urls = [photoMediaUrl, voiceMediaUrl].filter((url): url is string => Boolean(url));
      const response = await submitIntake({
        description: description.trim(),
        address: address.trim() || null,
        lat: coordinates?.latitude ?? null,
        lng: coordinates?.longitude ?? null,
        media_urls,
        image_description: photoDescription,
      });
      setSubmitted({
        tracking_id: response?.tracking_id || 'GRV-PENDING',
        status: response?.status,
        message: response?.message,
      });
    } catch {
      setError(t('report.errorSubmit'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const copyTrackingId = async () => {
    if (!submitted?.tracking_id) return;
    try {
      await navigator.clipboard.writeText(submitted.tracking_id);
      setIsCopied(true);
      window.setTimeout(() => setIsCopied(false), 1800);
    } catch {
      setError(t('report.errorCopy'));
    }
  };

  if (submitted) {
    return (
      <section className="mx-auto max-w-2xl px-4 py-8 sm:px-6 sm:py-12">
        <div className="animate-scale-in text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-success-100 ring-8 ring-success-50">
            <Check className="text-success-700" size={32} strokeWidth={2.5} />
          </div>
          <p className="mt-7 text-sm font-semibold uppercase tracking-[0.18em] text-success-700">
            {t('report.success.badge')}
          </p>
          <h1 className="mt-3 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
            {t('report.success.title')}
          </h1>
          <p className="mx-auto mt-3 max-w-lg text-base leading-relaxed text-slate-600">
            {t('report.success.body')}
          </p>

          <div className="card mt-8 p-5 sm:p-7">
            <p className="text-sm font-medium text-slate-500">{t('report.success.yourId')}</p>
            <div className="mt-3 flex items-center justify-center gap-2">
              <p className="select-all text-3xl font-extrabold tracking-wider text-primary-700 sm:text-4xl">
                {submitted.tracking_id}
              </p>
              <button
                type="button"
                onClick={copyTrackingId}
                aria-label={t('track.copyLabel')}
                className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-primary-50 hover:text-primary-600"
              >
                {isCopied ? <Check size={20} /> : <Copy size={20} />}
              </button>
            </div>
            <p className="mt-2 text-xs text-slate-400">
              {isCopied ? t('report.success.copied') : t('report.success.copyHint')}
            </p>
          </div>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <button type="button" onClick={() => onTrack(submitted.tracking_id)} className="btn-primary">
              {t('report.success.track')}
              <ChevronRight size={18} />
            </button>
            <button type="button" onClick={onBack} className="btn-secondary">
              {t('report.success.home')}
            </button>
          </div>

          <div className="mt-8 flex items-center justify-center gap-2 text-sm text-slate-400">
            <ShieldCheck size={17} className="text-success-600" />
            {t('report.success.security')}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-2xl px-4 py-8 sm:px-6 sm:py-10">
      <button
        type="button"
        onClick={onBack}
        className="group inline-flex items-center gap-2 text-sm font-semibold text-slate-500 transition-colors hover:text-primary-600"
      >
        <ArrowLeft size={17} className="transition-transform group-hover:-translate-x-1" />
        {t('report.back')}
      </button>

      <div className="mt-8">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50">
            <ClipboardList className="text-primary-600" size={23} />
          </div>
          <div>
            <p className="text-sm font-semibold text-primary-600">{t('report.step')}</p>
            <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
              {t('report.title')}
            </h1>
          </div>
        </div>
        <p className="mt-4 leading-relaxed text-slate-600">{t('report.subtitle')}</p>
      </div>

      <form onSubmit={handleSubmit} className="mt-8 space-y-5">
        {error && <ErrorBanner message={error} />}

        <div className="card p-5 sm:p-6">
          <label htmlFor="description" className="block text-sm font-bold text-slate-900">
            {t('report.descriptionLabel')} <span className="text-error-600">*</span>
          </label>
          <p className="mt-1 text-sm text-slate-500">{t('report.descriptionHint')}</p>
          <textarea
            id="description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder={t('report.descriptionPlaceholder')}
            rows={5}
            maxLength={2000}
            className="mt-4 w-full resize-y rounded-xl border-0 bg-slate-50 px-4 py-3.5 text-base text-slate-800 outline-none ring-1 ring-inset ring-slate-200 transition focus:bg-white focus:ring-2 focus:ring-primary-500"
          />
          <p className="mt-2 text-right text-xs text-slate-400">{description.length}/2000</p>
        </div>

        <div className="card p-5 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-900">{t('report.photoLabel')}</label>
              <p className="mt-1 text-sm text-slate-500">{t('report.photoHint')}</p>
            </div>
            <Camera className="shrink-0 text-slate-300" size={22} />
          </div>

          {photoPreview ? (
            <div className="relative mt-4 overflow-hidden rounded-xl bg-slate-100 ring-1 ring-slate-200">
              <img src={photoPreview} alt={t('report.photoAlt')} className="max-h-64 w-full object-cover" />
              <button
                type="button"
                onClick={removePhoto}
                aria-label={t('report.photoRemove')}
                className="absolute right-3 top-3 rounded-full bg-slate-900/75 p-2 text-white transition-colors hover:bg-error-600"
              >
                <X size={17} />
              </button>
              <div className="flex items-center gap-2 px-3 py-2 text-xs font-medium text-slate-600">
                <ImagePlus size={15} />
                <span className="truncate">{photoName}</span>
              </div>
              {photoUploading && (
                <p className="border-t border-slate-200 px-3 py-2 text-xs italic text-slate-400">
                  {t('report.photoAnalyzing')}
                </p>
              )}
              {!photoUploading && photoDescription && (
                <p className="border-t border-slate-200 bg-primary-50/60 px-3 py-2 text-xs text-primary-800">
                  <span className="font-bold">{t('report.photoAiSees')}</span> {photoDescription}
                </p>
              )}
            </div>
          ) : (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handlePhotoChange}
                className="hidden"
                id="photo"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="mt-4 flex w-full flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 px-4 py-7 text-center transition-colors hover:border-primary-300 hover:bg-primary-50"
              >
                <ImagePlus className="text-primary-500" size={27} />
                <span className="mt-2 text-sm font-semibold text-slate-700">{t('report.photoChoose')}</span>
                <span className="mt-1 text-xs text-slate-400">{t('report.photoFormats')}</span>
              </button>
            </>
          )}
        </div>

        <div className="card p-5 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-900">{t('report.voiceLabel')}</label>
              <p className="mt-1 text-sm text-slate-500">{t('report.voiceHint')}</p>
            </div>
            <FileAudio className="shrink-0 text-slate-300" size={22} />
          </div>
          <button
            type="button"
            onClick={toggleRecording}
            className={`mt-4 flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3.5 text-sm font-semibold transition-all ${
              isRecording
                ? 'bg-error-50 text-error-700 ring-1 ring-inset ring-error-200'
                : 'bg-slate-50 text-slate-700 ring-1 ring-inset ring-slate-200 hover:bg-primary-50 hover:text-primary-700 hover:ring-primary-200'
            }`}
          >
            {isRecording ? (
              <>
                <span className="relative flex h-2.5 w-2.5">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-error-500 opacity-75" />
                  <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-error-600" />
                </span>
                {t('report.voiceRecording')}
                <CircleStop size={18} />
              </>
            ) : voiceNote ? (
              <>
                <Check size={18} className="text-success-600" />
                {t('report.voiceSaved')}
                <RefreshCw size={16} />
              </>
            ) : (
              <>
                <Mic size={18} />
                {t('report.voiceRecord')}
              </>
            )}
          </button>
        </div>

        <div className="card p-5 sm:p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <label className="block text-sm font-bold text-slate-900">{t('report.locationLabel')}</label>
              <p className="mt-1 text-sm text-slate-500">{t('report.locationHint')}</p>
            </div>
            <MapPin className="shrink-0 text-slate-300" size={22} />
          </div>
          <button
            type="button"
            onClick={handleLocation}
            disabled={isLocating}
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary-50 px-4 py-3.5 text-sm font-semibold text-primary-700 ring-1 ring-inset ring-primary-200 transition-colors hover:bg-primary-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLocating ? <Spinner className="text-primary-600" /> : <LocateFixed size={18} />}
            {isLocating
              ? t('report.locationFinding')
              : coordinates
                ? t('report.locationCaptured')
                : t('report.locationUse')}
          </button>
          {coordinates && (
            <div className="mt-3 flex items-center gap-2 rounded-lg bg-success-50 px-3 py-2.5 text-sm text-success-800 ring-1 ring-inset ring-success-200">
              <Check size={16} className="shrink-0 text-success-600" />
              <span>{t('report.locationCoords', { coords: formatCoordinates(coordinates) })}</span>
            </div>
          )}
          <div className="relative mt-4">
            <MapPin className="pointer-events-none absolute left-3.5 top-3.5 text-slate-400" size={18} />
            <input
              type="text"
              value={address}
              onChange={(event) => setAddress(event.target.value)}
              placeholder={t('report.locationPlaceholder')}
              className="w-full rounded-xl border-0 bg-slate-50 py-3.5 pl-10 pr-4 text-base text-slate-800 outline-none ring-1 ring-inset ring-slate-200 transition focus:bg-white focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <p className="mt-2 text-xs text-slate-400">{t('report.locationOptional')}</p>
        </div>

        <button type="submit" disabled={isSubmitting || photoUploading || voiceUploading} className="btn-primary w-full py-4 text-base sm:text-lg">
          {isSubmitting ? (
            <>
              <Spinner />
              {t('report.submitting')}
            </>
          ) : (
            <>
              {t('report.submit')}
              <ChevronRight size={20} />
            </>
          )}
        </button>
        <p className="flex items-center justify-center gap-1.5 px-4 text-center text-xs leading-relaxed text-slate-400">
          <ShieldCheck size={15} className="shrink-0 text-slate-400" />
          {t('report.securityNote')}
        </p>
      </form>
    </section>
  );
}
