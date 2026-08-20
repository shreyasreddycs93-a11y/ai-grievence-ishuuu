import type { GrievanceStatusResponse, IntakeResponse, VerifyResponse } from '@/types';

const MOCK_GRIEVANCE: GrievanceStatusResponse = {
  tracking_id: 'GRV-10023',
  status: 'in_progress',
  category: 'water_supply',
  priority: 'high',
  department: 'Water Board',
  summary: 'Burst water pipe flooding the street near MG Road market.',
  created_at: '2026-08-13T09:30:00Z',
  sla_due_at: '2026-08-14T09:30:00Z',
  timeline: [
    { status: 'new', note: 'Complaint received', at: '2026-08-13T09:30:00Z' },
    { status: 'assigned', note: 'Assigned to Water Board', at: '2026-08-13T09:31:00Z' },
    { status: 'in_progress', note: 'Field team dispatched', at: '2026-08-13T11:00:00Z' },
  ],
  subtasks: [],
};

const MOCK_GRIEVANCE_RESOLVED: GrievanceStatusResponse = {
  ...MOCK_GRIEVANCE,
  tracking_id: 'GRV-10024',
  status: 'resolved',
  summary: 'Burst water pipe repaired near MG Road market.',
  timeline: [
    { status: 'new', note: 'Complaint received', at: '2026-08-13T09:30:00Z' },
    { status: 'assigned', note: 'Assigned to Water Board', at: '2026-08-13T09:31:00Z' },
    { status: 'in_progress', note: 'Field team dispatched', at: '2026-08-13T11:00:00Z' },
    { status: 'resolved', note: 'Pipe repaired and water supply restored', at: '2026-08-13T15:00:00Z' },
  ],
};

const MOCK_GRIEVANCE_SUBTASKS: GrievanceStatusResponse = {
  tracking_id: 'GRV-10025',
  status: 'in_progress',
  category: 'road_safety',
  priority: 'medium',
  department: 'Municipal Corporation',
  summary: 'Fallen tree blocking road with damaged streetlight and water logging.',
  created_at: '2026-08-13T08:00:00Z',
  sla_due_at: '2026-08-15T08:00:00Z',
  timeline: [
    { status: 'new', note: 'Complaint received', at: '2026-08-13T08:00:00Z' },
    { status: 'assigned', note: 'Split across 3 departments', at: '2026-08-13T08:05:00Z' },
    { status: 'in_progress', note: 'Teams dispatched', at: '2026-08-13T09:30:00Z' },
  ],
  subtasks: [
    {
      id: 'SUB-1',
      department: 'Forest Department',
      status: 'resolved',
      category: 'tree_removal',
      summary: 'Fallen tree removed from roadway.',
      timeline: [
        { status: 'assigned', note: 'Assigned to Forest Department', at: '2026-08-13T08:05:00Z' },
        { status: 'resolved', note: 'Tree cleared', at: '2026-08-13T10:00:00Z' },
      ],
    },
    {
      id: 'SUB-2',
      department: 'Electricity Board',
      status: 'in_progress',
      category: 'streetlight',
      summary: 'Damaged streetlight pole needs replacement.',
      timeline: [
        { status: 'assigned', note: 'Assigned to Electricity Board', at: '2026-08-13T08:05:00Z' },
        { status: 'in_progress', note: 'Pole replacement in progress', at: '2026-08-13T11:00:00Z' },
      ],
    },
    {
      id: 'SUB-3',
      department: 'Water Board',
      status: 'new',
      category: 'water_supply',
      summary: 'Water logging near the fallen tree area.',
      timeline: [
        { status: 'assigned', note: 'Assigned to Water Board', at: '2026-08-13T08:05:00Z' },
      ],
    },
  ],
};

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function mockIntake(_data: unknown): Promise<IntakeResponse> {
  await delay(800);
  return {
    tracking_id: 'GRV-' + Math.floor(10000 + Math.random() * 90000),
    status: 'new',
    message: 'Complaint registered successfully',
  };
}

export async function mockGetStatus(trackingId: string): Promise<GrievanceStatusResponse> {
  await delay(700);
  const id = trackingId.trim().toUpperCase();
  if (id === 'GRV-10024') return { ...MOCK_GRIEVANCE_RESOLVED };
  if (id === 'GRV-10025') return { ...MOCK_GRIEVANCE_SUBTASKS };
  return { ...MOCK_GRIEVANCE };
}

export async function mockVerify(_trackingId: string, confirmed: boolean): Promise<VerifyResponse> {
  await delay(500);
  return {
    confirmed,
    message: confirmed ? 'Complaint confirmed as resolved' : 'Complaint reopened',
  };
}
