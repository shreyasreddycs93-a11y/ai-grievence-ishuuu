import type {
  GrievanceStatusResponse,
  IntakeResponse,
  MediaUploadResponse,
  MyGrievanceItem,
  VerifyResponse,
} from '@/types';
import { mockIntake, mockGetStatus, mockVerify, mockGetMyGrievances } from './mockApi';

// Empty default = same origin, which is how we deploy: one FastAPI process
// serves this app at /citizen/ and the API at unprefixed paths. Set it only
// when the backend is on a different origin (e.g. `npm run dev` against a
// separately-run backend).
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

// Mock mode must be opt-in. Inferring it from a missing base URL silently
// turned the whole deployed app into a demo — every citizen saw the same
// two fake tickets in My Complaints.
export const isMockMode = import.meta.env.VITE_USE_MOCK === 'true';

// Written by the Landing app on login/signup — shared via localStorage since
// all three apps run on the same origin. Optional here: the citizen app
// works anonymously too, this just links new submissions to the account
// when present.
export function getAuthToken(): string | null {
  return localStorage.getItem('grievance_token');
}

export function isLoggedIn(): boolean {
  return getAuthToken() !== null;
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
  });
  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function submitIntake(data: unknown): Promise<IntakeResponse> {
  if (isMockMode) {
    return mockIntake(data);
  }
  const token = getAuthToken();
  return request<IntakeResponse>(`${API_BASE_URL}/intake/web`, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
}

export async function getMyGrievances(): Promise<MyGrievanceItem[]> {
  if (isMockMode) {
    return mockGetMyGrievances();
  }
  const token = getAuthToken();
  if (!token) return [];
  return request<MyGrievanceItem[]>(`${API_BASE_URL}/citizen/my-grievances`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function uploadMedia(file: Blob, filename: string): Promise<MediaUploadResponse> {
  if (isMockMode) {
    return {
      media_url: URL.createObjectURL(file),
      kind: file.type.startsWith('audio/') ? 'audio' : 'image',
      transcript: file.type.startsWith('audio/') ? '[mock transcript unavailable offline]' : null,
    };
  }
  const form = new FormData();
  form.append('file', file, filename);
  const res = await fetch(`${API_BASE_URL}/intake/media`, { method: 'POST', body: form });
  if (!res.ok) {
    throw new Error(`Upload failed (${res.status})`);
  }
  return res.json() as Promise<MediaUploadResponse>;
}

export async function getGrievanceStatus(trackingId: string): Promise<GrievanceStatusResponse> {
  if (isMockMode) {
    return mockGetStatus(trackingId);
  }
  return request<GrievanceStatusResponse>(
    `${API_BASE_URL}/grievance/${encodeURIComponent(trackingId)}/status`,
  );
}

export async function verifyGrievance(
  trackingId: string,
  confirmed: boolean,
): Promise<VerifyResponse> {
  if (isMockMode) {
    return mockVerify(trackingId, confirmed);
  }
  return request<VerifyResponse>(
    `${API_BASE_URL}/grievance/${encodeURIComponent(trackingId)}/verify`,
    {
      method: 'POST',
      body: JSON.stringify({ confirmed }),
    },
  );
}
