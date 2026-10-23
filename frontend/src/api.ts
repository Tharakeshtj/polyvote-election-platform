export type ElectionStatus = 'NOMINATION' | 'VOTING' | 'CLOSED';

export interface PublicElection {
  election_id: number;
  org_name: string;
  status: ElectionStatus;
  start_time: string | null;
  end_time: string | null;
  candidates: number;
}

export interface ElectionSummary extends PublicElection {
  admin_contact: string;
  voters: number;
  voted: number;
  ballots: number;
}

export interface Candidate {
  candidate_id: number;
  name: string;
  platform_statement: string | null;
}

export interface ElectionDetail {
  election_id: number;
  org_name: string;
  admin_contact: string;
  status: ElectionStatus;
  start_time: string | null;
  end_time: string | null;
  candidates: (Candidate & { first_preferences: number })[];
  voters: number;
  voted: number;
  ballots: number;
  ledger_receipts: number;
}

export interface Voter {
  participation_id: number;
  student_reg_no: string;
  has_voted: 0 | 1;
}

export interface BallotRow {
  ballot_token: string;
  candidate_id: number;
  preference_rank: number;
}

export interface VoterBallot {
  reg_no: string;
  election: { election_id: number; org_name: string; status: ElectionStatus };
  candidates: Candidate[];
  ranks_required: number;
}

export interface CastResult {
  ballot_token: string;
  block_index: number;
  block_hash: string;
  timestamp: string;
}

export type Receipt =
  | { found: false }
  | {
      found: true;
      block_index: number;
      timestamp: string;
      election_id: number;
      org_name: string | null;
      block_hash: string;
      in_tally: boolean;
    };

export interface IntegrityResult {
  valid: boolean;
  message: string;
  modified: string[];
  deleted: string[];
  injected: string[];
  roster_changed: boolean;
  count_mismatch: { voted_flags: number; ballots: number; receipts: number } | null;
}

export interface TallyRound {
  round: number;
  rows: { candidate: string; votes: number; percentage: string }[];
  eliminated: string | null;
  tie_break: boolean;
}

export interface TallyResult {
  outcome: 'winner' | 'no_votes' | 'exhausted';
  winner: string | null;
  message: string;
  rounds: TallyRound[];
}

export interface LedgerBlock {
  index: number;
  timestamp: string;
  election_id: number;
  ballot_token: string;
  vote_data_hash: string;
  prev_hash: string;
  curr_hash: string;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

const ADMIN_KEY = 'polyvote.adminToken';

export const adminToken = {
  get(): string | null {
    try { return sessionStorage.getItem(ADMIN_KEY); } catch { return null; }
  },
  set(token: string) {
    try { sessionStorage.setItem(ADMIN_KEY, token); } catch { /* storage unavailable: session lasts for this tab only */ }
  },
  clear() {
    try { sessionStorage.removeItem(ADMIN_KEY); } catch { /* ignore */ }
  },
};

export const UNAUTHORIZED_EVENT = 'polyvote:unauthorized';

async function request<T>(path: string, opts: { method?: string; body?: unknown; token?: string | null } = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (opts.body !== undefined) headers['Content-Type'] = 'application/json';
  if (opts.token) headers.Authorization = `Bearer ${opts.token}`;
  let res: Response;
  try {
    res = await fetch(`/api${path}`, {
      method: opts.method ?? 'GET',
      headers,
      body: opts.body === undefined ? undefined : JSON.stringify(opts.body),
    });
  } catch {
    throw new ApiError(0, "Can't reach the PolyVote server. Is it running?");
  }
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    const message = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail[0]?.msg : `Request failed (${res.status})`;
    throw new ApiError(res.status, message ?? `Request failed (${res.status})`);
  }
  return data as T;
}

function asAdmin<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  return request<T>(path, { method, body, token: adminToken.get() }).catch((err) => {
    if (err instanceof ApiError && err.status === 401) window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
    throw err;
  });
}

export interface ContactMessage {
  message_id: number;
  received_at: number;
  name: string;
  email: string;
  message: string;
}

export interface PublicConfig {
  public_url: string | null;
  hosted_demo: boolean;
  otp_demo_hint: boolean;
  admin_public: boolean;
}

export const publicApi = {
  elections: () => request<PublicElection[]>('/elections'),
  receipt: (token: string) => request<Receipt>(`/receipts/${encodeURIComponent(token.trim())}`),
  config: () => request<PublicConfig>('/config'),
  contact: (body: { name: string; email: string; message: string; website: string }) => request<{ ok: boolean }>('/contact', { method: 'POST', body }),
};

export interface OtpChallenge {
  otp_required: true;
  challenge: string;
  email_hint: string;
  expires_in: number;
  resend_after: number;
  demo_code?: string;
}

export interface OutboxEntry {
  sent_at: number;
  election_id: number;
  reg_no: string;
  email: string;
  status: string;
  code: string | null;
  expired: boolean;
}

export const voterApi = {
  login: (election_id: number, reg_no: string, password: string) =>
    request<{ token: string; reg_no: string } | OtpChallenge>('/voter/login', { method: 'POST', body: { election_id, reg_no, password } }),
  otpVerify: (challenge: string, code: string) =>
    request<{ token: string; reg_no: string }>('/voter/otp/verify', { method: 'POST', body: { challenge, code } }),
  otpResend: (challenge: string) =>
    request<{ email_hint: string; expires_in: number; resend_after: number; demo_code?: string }>('/voter/otp/resend', { method: 'POST', body: { challenge } }),
  ballot: (token: string) => request<VoterBallot>('/voter/ballot', { token }),
  cast: (token: string, ranking: number[]) => request<CastResult>('/voter/ballot', { method: 'POST', body: { ranking }, token }),
  logout: (token: string) => request<null>('/logout', { method: 'POST', token }).catch(() => null),
};

const e = (id: number) => `/admin/elections/${id}`;

export const adminApi = {
  login: (username: string, password: string) =>
    request<{ token: string; username: string }>('/admin/login', { method: 'POST', body: { username, password } }),
  me: () => asAdmin<{ username: string }>('/admin/me'),
  logout: () => request<null>('/logout', { method: 'POST', token: adminToken.get() }).catch(() => null),

  elections: () => asAdmin<ElectionSummary[]>('/admin/elections'),
  createElection: (org_name: string, admin_contact: string) =>
    asAdmin<{ election_id: number }>('/admin/elections', 'POST', { org_name, admin_contact }),
  election: (id: number) => asAdmin<ElectionDetail>(e(id)),
  setStatus: (id: number, status: ElectionStatus) => asAdmin(`${e(id)}/status`, 'POST', { status }),

  addCandidate: (id: number, name: string, platform_statement: string) =>
    asAdmin(`${e(id)}/candidates`, 'POST', { name, platform_statement }),
  seedCandidates: (id: number, count: number) => asAdmin<{ added: number }>(`${e(id)}/candidates/seed`, 'POST', { count }),
  deleteCandidate: (id: number, cid: number) => asAdmin(`${e(id)}/candidates/${cid}`, 'DELETE'),

  voters: (id: number) => asAdmin<Voter[]>(`${e(id)}/voters`),
  addVoter: (id: number, reg_no: string, password: string) => asAdmin<{ reg_no: string }>(`${e(id)}/voters`, 'POST', { reg_no, password }),
  bulkVoters: (id: number, count: number) =>
    asAdmin<{ added: number; first: string; password: string }>(`${e(id)}/voters/bulk`, 'POST', { count }),
  simulate: (id: number, count: number) => asAdmin<{ cast: number }>(`${e(id)}/simulate`, 'POST', { count }),

  contacts: (id: number) => asAdmin<Record<string, string>>(`${e(id)}/contacts`),
  setContact: (id: number, reg_no: string, email: string) => asAdmin(`${e(id)}/contacts`, 'PUT', { reg_no, email }),
  fillContacts: (id: number, base_email: string) => asAdmin<{ filled: number }>(`${e(id)}/contacts/fill`, 'POST', { base_email }),
  messages: () => asAdmin<ContactMessage[]>('/admin/contact'),
  otpStatus: () => asAdmin<{ required: boolean; smtp_configured: boolean; smtp_host: string; sender: string | null; ttl_seconds: number; max_attempts: number }>('/admin/otp/status'),
  otpOutbox: () => asAdmin<OutboxEntry[]>('/admin/otp/outbox'),

  integrity: (id: number) => asAdmin<IntegrityResult>(`${e(id)}/integrity`),
  tally: (id: number) => asAdmin<TallyResult>(`${e(id)}/tally`),
  ledger: (electionId?: number) =>
    asAdmin<{ chain_valid: boolean; chain_message: string; blocks: LedgerBlock[] }>(
      `/admin/ledger${electionId ? `?election_id=${electionId}` : ''}`,
    ),

  studio: (id: number) => asAdmin<{ candidates: Candidate[]; voters: Voter[]; ballots: BallotRow[] }>(`${e(id)}/studio`),
  studioCandidate: (id: number, cid: number, name: string, platform_statement: string) =>
    asAdmin(`${e(id)}/studio/candidates/${cid}`, 'PUT', { name, platform_statement }),
  studioVoter: (id: number, pid: number, reg_no: string) => asAdmin(`${e(id)}/studio/voters/${pid}`, 'PUT', { reg_no }),
  studioDropVoter: (id: number, pid: number) => asAdmin(`${e(id)}/studio/voters/${pid}`, 'DELETE'),
  studioBallot: (id: number, ballot_token: string, preference_rank: number, candidate_id: number) =>
    asAdmin(`${e(id)}/studio/ballots`, 'PUT', { ballot_token, preference_rank, candidate_id }),
  studioDeleteRank: (id: number, ballot_token: string, preference_rank: number) =>
    asAdmin(`${e(id)}/studio/ballots/delete`, 'POST', { ballot_token, preference_rank }),
  studioDeleteBallot: (id: number, token: string) => asAdmin(`${e(id)}/studio/ballots/${encodeURIComponent(token)}`, 'DELETE'),

  admins: () => asAdmin<string[]>('/admin/admins'),
  addAdmin: (username: string, password: string) => asAdmin('/admin/admins', 'POST', { username, password }),
  reset: () => asAdmin('/admin/reset', 'POST', { confirm: 'RESET' }),
};

export function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : 'Something went wrong.';
}
