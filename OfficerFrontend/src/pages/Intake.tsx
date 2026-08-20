import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ClipboardList,
  MapPin,
  Image as ImageIcon,
  Mic,
  CheckCircle2,
  AlertTriangle,
  LocateFixed,
  X,
  Upload,
} from 'lucide-react'
import { submitIntake } from '../api/client'
import type { IntakeResponse } from '../api/types'
import clsx from 'clsx'

export default function Intake() {
  const navigate = useNavigate()

  // Form fields
  const [description, setDescription] = useState('')
  const [address, setAddress] = useState('')
  const [lat, setLat] = useState<number | undefined>()
  const [lng, setLng] = useState<number | undefined>()
  const [language, setLanguage] = useState('')

  // Photo
  const [photoFile, setPhotoFile] = useState<File | null>(null)
  const [photoPreview, setPhotoPreview] = useState<string | null>(null)
  const photoInputRef = useRef<HTMLInputElement>(null)

  // Audio
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const audioChunks = useRef<BlobPart[]>([])
  const audioInputRef = useRef<HTMLInputElement>(null)

  // Submission
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<IntakeResponse | null>(null)

  // GPS
  const [gpsLoading, setGpsLoading] = useState(false)
  const [gpsError, setGpsError] = useState<string | null>(null)

  function handlePhotoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setPhotoFile(file)
    setPhotoPreview(URL.createObjectURL(file))
  }

  function removePhoto() {
    setPhotoFile(null)
    setPhotoPreview(null)
    if (photoInputRef.current) photoInputRef.current.value = ''
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      audioChunks.current = []
      recorder.ondataavailable = e => audioChunks.current.push(e.data)
      recorder.onstop = () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/webm' })
        setAudioFile(new File([blob], 'voice-note.webm', { type: 'audio/webm' }))
        stream.getTracks().forEach(t => t.stop())
      }
      recorder.start()
      setMediaRecorder(recorder)
      setIsRecording(true)
    } catch {
      setError('Microphone access denied. Please allow microphone permissions.')
    }
  }

  function stopRecording() {
    mediaRecorder?.stop()
    setIsRecording(false)
    setMediaRecorder(null)
  }

  function removeAudio() {
    setAudioFile(null)
    if (audioInputRef.current) audioInputRef.current.value = ''
  }

  function getLocation() {
    if (!navigator.geolocation) {
      setGpsError('Geolocation not supported by this browser')
      return
    }
    setGpsLoading(true)
    setGpsError(null)
    navigator.geolocation.getCurrentPosition(
      pos => {
        setLat(pos.coords.latitude)
        setLng(pos.coords.longitude)
        setAddress(`${pos.coords.latitude.toFixed(5)}, ${pos.coords.longitude.toFixed(5)}`)
        setGpsLoading(false)
      },
      () => {
        setGpsError('Could not get location. Try entering manually.')
        setGpsLoading(false)
      },
    )
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!description.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Photo/audio upload is a backend stub — we note the file names in the
      // description as a fallback until POST /intake/upload is live.
      let mediaNote = ''
      if (photoFile) mediaNote += ` [Photo attached: ${photoFile.name}]`
      if (audioFile) mediaNote += ` [Voice note attached: ${audioFile.name}]`

      const response = await submitIntake({
        description: description.trim() + mediaNote,
        address: address || undefined,
        lat,
        lng,
        language: language || undefined,
      })
      setResult(response)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Submission failed')
    } finally {
      setLoading(false)
    }
  }

  // ── Success screen ──────────────────────────────────────────────────────────
  if (result) {
    return (
      <div className="max-w-lg mx-auto mt-10">
        <div className="bg-white rounded-2xl border border-gray-100 p-8 text-center">
          <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 size={28} className="text-emerald-600" />
          </div>
          <h2 className="text-lg font-bold text-gray-900 mb-1">Grievance submitted</h2>
          <p className="text-sm text-gray-500 mb-5">
            The AI has classified and routed this complaint automatically.
          </p>

          <div className="bg-gray-50 rounded-xl p-4 text-left space-y-2 mb-6">
            <Row label="Tracking ID">
              <span className="font-mono font-semibold text-indigo-600">{result.tracking_id}</span>
            </Row>
            <Row label="Status">{result.status.replace('_', ' ')}</Row>
            <Row label="Category">{result.category.replace('_', ' ')}</Row>
            <Row label="Priority">
              <span className={clsx(
                'font-semibold',
                result.priority === 'critical' ? 'text-red-600' :
                result.priority === 'high' ? 'text-orange-600' :
                result.priority === 'medium' ? 'text-yellow-600' : 'text-emerald-600',
              )}>
                {result.priority}
              </span>
            </Row>
            <Row label="Routed to">{result.department ?? '—'}</Row>
            {result.merged && (
              <Row label="Note">
                <span className="text-yellow-700 text-xs">Merged with an existing open complaint</span>
              </Row>
            )}
            {result.split && result.subtask_tracking_ids.length > 0 && (
              <Row label="Sub-tickets">
                <span className="text-xs text-indigo-600">{result.subtask_tracking_ids.join(', ')}</span>
              </Row>
            )}
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => navigate(`/queue/${result.tracking_id}`)}
              className="flex-1 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition"
            >
              View in queue
            </button>
            <button
              onClick={() => {
                setResult(null)
                setDescription('')
                setAddress('')
                setLat(undefined)
                setLng(undefined)
                setLanguage('')
                setPhotoFile(null)
                setPhotoPreview(null)
                setAudioFile(null)
              }}
              className="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition"
            >
              New intake
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── Form ────────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto">
      {/* Page header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center">
          <ClipboardList size={20} className="text-indigo-600" />
        </div>
        <div>
          <p className="text-xs font-semibold text-indigo-600 uppercase tracking-wide">Officer intake</p>
          <h1 className="text-xl font-bold text-gray-900 leading-tight">Report a Problem</h1>
        </div>
      </div>
      <p className="text-sm text-gray-500 mb-6">
        Submit a grievance on behalf of a citizen. The AI will classify and route it automatically.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">

        {/* Description */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-start justify-between mb-1">
            <label className="text-sm font-semibold text-gray-800">
              What is the problem? <span className="text-red-500">*</span>
            </label>
          </div>
          <p className="text-xs text-gray-400 mb-3">
            Include useful details like landmarks, timings, or frequency.
          </p>
          <textarea
            value={description}
            onChange={e => setDescription(e.target.value)}
            required
            rows={5}
            maxLength={2000}
            placeholder="e.g. There is a large pothole near the entrance of MG Road causing accidents…"
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400 transition bg-gray-50"
          />
          <div className="text-right text-xs text-gray-400 mt-1">{description.length}/2000</div>
        </div>

        {/* Photo upload */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-1">
            <label className="text-sm font-semibold text-gray-800">Add a photo</label>
            <ImageIcon size={16} className="text-gray-300" />
          </div>
          <p className="text-xs text-gray-400 mb-3">
            A photo helps the team understand the issue faster.{' '}
            <span className="text-orange-500 font-medium">Upload will be enabled once backend is ready.</span>
          </p>

          {photoPreview ? (
            <div className="relative inline-block">
              <img
                src={photoPreview}
                alt="Preview"
                className="w-32 h-32 object-cover rounded-xl border border-gray-200"
              />
              <button
                type="button"
                onClick={removePhoto}
                className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition"
              >
                <X size={12} />
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => photoInputRef.current?.click()}
              className="w-full flex flex-col items-center gap-2 border-2 border-dashed border-gray-200 rounded-xl py-6 text-gray-400 hover:border-indigo-300 hover:text-indigo-500 transition"
            >
              <Upload size={22} />
              <span className="text-xs font-medium">Choose a photo</span>
              <span className="text-[11px] text-gray-400">JPG, PNG or HEIC · Optional</span>
            </button>
          )}
          <input
            ref={photoInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handlePhotoChange}
          />
        </div>

        {/* Audio / voice note */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-1">
            <label className="text-sm font-semibold text-gray-800">Add a voice note</label>
            <Mic size={16} className="text-gray-300" />
          </div>
          <p className="text-xs text-gray-400 mb-3">
            Prefer speaking? Record a quick explanation.{' '}
            <span className="text-orange-500 font-medium">Transcription will be enabled once backend is ready.</span>
          </p>

          {audioFile ? (
            <div className="flex items-center gap-3 bg-indigo-50 rounded-xl px-4 py-3">
              <Mic size={16} className="text-indigo-600 shrink-0" />
              <span className="text-xs text-indigo-700 font-medium flex-1 truncate">{audioFile.name}</span>
              <button type="button" onClick={removeAudio} className="text-gray-400 hover:text-red-500 transition">
                <X size={14} />
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <button
                type="button"
                onClick={isRecording ? stopRecording : startRecording}
                className={clsx(
                  'flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium border transition',
                  isRecording
                    ? 'bg-red-50 border-red-200 text-red-600 hover:bg-red-100'
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-600',
                )}
              >
                <Mic size={15} className={isRecording ? 'animate-pulse' : ''} />
                {isRecording ? 'Stop recording' : 'Record voice note'}
              </button>
              <button
                type="button"
                onClick={() => audioInputRef.current?.click()}
                className="px-4 py-3 rounded-xl text-sm font-medium bg-gray-50 border border-gray-200 text-gray-600 hover:bg-gray-100 transition"
                title="Upload audio file"
              >
                <Upload size={15} />
              </button>
            </div>
          )}
          <input
            ref={audioInputRef}
            type="file"
            accept="audio/*"
            className="hidden"
            onChange={e => {
              const file = e.target.files?.[0]
              if (file) setAudioFile(file)
            }}
          />
        </div>

        {/* Location */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-1">
            <label className="text-sm font-semibold text-gray-800">Where is it?</label>
            <MapPin size={16} className="text-gray-300" />
          </div>
          <p className="text-xs text-gray-400 mb-3">
            Location helps route this to the correct local team.
          </p>

          <button
            type="button"
            onClick={getLocation}
            disabled={gpsLoading}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-50 text-indigo-700 text-sm font-medium hover:bg-indigo-100 transition disabled:opacity-60 mb-3"
          >
            <LocateFixed size={15} className={gpsLoading ? 'animate-spin' : ''} />
            {gpsLoading ? 'Getting location…' : 'Use my location'}
          </button>

          {gpsError && (
            <p className="text-xs text-red-600 mb-3">{gpsError}</p>
          )}

          <div className="relative">
            <MapPin size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={address}
              onChange={e => setAddress(e.target.value)}
              placeholder="Or enter an address, landmark or area"
              className="w-full pl-8 pr-4 py-2.5 border border-gray-200 rounded-xl text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-400 transition"
            />
          </div>
          {lat && lng && (
            <p className="text-[11px] text-gray-400 mt-2">
              GPS: {lat.toFixed(5)}, {lng.toFixed(5)}
            </p>
          )}
          <p className="text-[11px] text-gray-400 mt-1">Both location options are optional.</p>
        </div>

        {/* Language (optional) */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <label className="text-sm font-semibold text-gray-800 block mb-1">
            Language <span className="text-xs font-normal text-gray-400">(optional)</span>
          </label>
          <p className="text-xs text-gray-400 mb-3">
            If the description is in a regional language, specify it here.
          </p>
          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
            className="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
          >
            <option value="">Auto-detect</option>
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="kn">Kannada</option>
            <option value="te">Telugu</option>
            <option value="ta">Tamil</option>
            <option value="mr">Marathi</option>
          </select>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 rounded-2xl px-5 py-4 text-sm">
            <AlertTriangle size={16} className="shrink-0" />
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !description.trim()}
          className="w-full py-4 rounded-2xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 active:bg-indigo-800 transition disabled:opacity-60 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Submitting…
            </>
          ) : (
            <>Submit complaint →</>
          )}
        </button>

        <p className="text-center text-[11px] text-gray-400 flex items-center justify-center gap-1">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          Details are securely shared only with the relevant civic department.
        </p>
      </form>
    </div>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-800">{children}</span>
    </div>
  )
}
