import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowDown, ArrowLeft, ArrowUp, Check, KeyRound, Lock, LogOut, ReceiptText, ShieldCheck, Vote, X } from 'lucide-react';
import { errorMessage, publicApi, voterApi, type CastResult, type PublicElection, type VoterBallot } from '../../api';
import { Avatar, ConfirmDialog, CopyButton, EmptyState, FormError, PageLoading, Spinner, useToast } from '../../components/ui';

type Step = 'signin' | 'ballot' | 'done';
const STEPS: { key: Step; label: string }[] = [
  { key: 'signin', label: 'Sign in' },
  { key: 'ballot', label: 'Rank' },
  { key: 'done', label: 'Receipt' },
];
const ORDINAL = ['1st', '2nd', '3rd', '4th', '5th'];

export default function VoteFlow() {
  const electionId = Number(useParams().electionId);
  const [election, setElection] = useState<PublicElection | null | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<Step>('signin');
  const [session, setSession] = useState<{ token: string; ballot: VoterBallot } | null>(null);
  const [receipt, setReceipt] = useState<CastResult | null>(null);

  useEffect(() => {
    publicApi.elections()
      .then((list) => setElection(list.find((e) => e.election_id === electionId) ?? null))
      .catch((e) => setError(errorMessage(e)));
  }, [electionId]);

  // Release the server-side voter session if the voter walks away mid-ballot.
  const tokenRef = useRef<string | null>(null);
  tokenRef.current = step === 'ballot' ? session?.token ?? null : null;
  useEffect(() => () => { if (tokenRef.current) voterApi.logout(tokenRef.current); }, []);

  if (error) return <div className="narrow"><FormError message={error} /></div>;
  if (election === undefined) return <div className="narrow card"><PageLoading rows={2} /></div>;
  if (election === null || (election.status !== 'VOTING' && step === 'signin')) {
    return (
      <div className="narrow card">
        <EmptyState icon={<Vote />} title={election ? 'This election isn’t open for voting' : 'Election not found'}>
          {election?.status === 'NOMINATION' ? 'Voting hasn’t opened yet. ' : election?.status === 'CLOSED' ? 'Voting has ended. ' : ''}
          <Link to="/">See all elections</Link>
        </EmptyState>
      </div>
    );
  }

  const signOut = () => {
    if (session) voterApi.logout(session.token);
    setSession(null);
    setStep('signin');
  };

  // The stepper shares the column of the step it describes, so it lines up with the card below it.
  const column = step === 'ballot' ? undefined : { maxWidth: step === 'done' ? 520 : 420, margin: '0 auto' };

  return (
    <div style={column}>
      <Stepper current={step} />
      {step === 'signin' && (
        <SignIn election={election} onSignedIn={(token, ballot) => { setSession({ token, ballot }); setStep('ballot'); }} />
      )}
      {step === 'ballot' && session && (
        <Ballot
          token={session.token}
          ballot={session.ballot}
          onSignOut={signOut}
          onCast={(r) => { setReceipt(r); setSession(null); setStep('done'); }}
        />
      )}
      {step === 'done' && receipt && <Done receipt={receipt} election={election} />}
    </div>
  );
}

function Stepper({ current }: { current: Step }) {
  const idx = STEPS.findIndex((s) => s.key === current);
  return (
    <ol className="steps" aria-label="Voting progress">
      {STEPS.map((s, i) => (
        <li key={s.key} className={i === idx ? 'active' : i < idx ? 'done' : ''} aria-current={i === idx ? 'step' : undefined}>
          <span className="n">{i < idx ? <Check /> : i + 1}</span>
          {s.label}
        </li>
      ))}
    </ol>
  );
}

// ----------------------------------------------------------------- sign in

function SignIn({ election, onSignedIn }: { election: PublicElection; onSignedIn: (token: string, ballot: VoterBallot) => void }) {
  const [regNo, setRegNo] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const { token } = await voterApi.login(election.election_id, regNo, password);
      onSignedIn(token, await voterApi.ballot(token));
    } catch (e) {
      setError(errorMessage(e));
      setBusy(false);
    }
  };

  return (
    <div className="narrow">
      <Link to="/" className="btn btn-ghost btn-sm" style={{ marginLeft: -10, marginBottom: 12 }}><ArrowLeft /> All elections</Link>
      <form className="card" onSubmit={submit}>
        <div className="card-body stack">
          <div>
            <h1>Sign in to vote</h1>
            <p className="muted" style={{ marginTop: 4 }}>{election.org_name} · Election #{election.election_id}</p>
          </div>
          <div className="field">
            <label htmlFor="reg">Registration number</label>
            <input
              id="reg" className="input input-lg input-mono" autoFocus autoComplete="username" placeholder="25BCE0001" required
              value={regNo} onChange={(e) => setRegNo(e.target.value.toUpperCase())}
            />
          </div>
          <div className="field">
            <label htmlFor="pw">Password</label>
            <input id="pw" type="password" className="input input-lg" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} />
            <span className="hint">Demo voters from bulk registration use <code>vote123</code>.</span>
          </div>
          <FormError message={error} />
          <button className="btn btn-primary btn-lg btn-block" disabled={busy || !regNo || !password}>
            {busy ? <Spinner /> : <KeyRound />}
            Continue to ballot
          </button>
        </div>
        <div className="card-foot subtle row" style={{ gap: 8 }}>
          <Lock size={14} /> Your registration number is only used to check you haven’t voted yet.
        </div>
      </form>
    </div>
  );
}

// ----------------------------------------------------------------- ballot

function Ballot({ token, ballot, onSignOut, onCast }: {
  token: string; ballot: VoterBallot; onSignOut: () => void; onCast: (r: CastResult) => void;
}) {
  const toast = useToast();
  const need = ballot.ranks_required;
  const [ranking, setRanking] = useState<number[]>([]);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const byId = new Map(ballot.candidates.map((c) => [c.candidate_id, c]));
  const complete = ranking.length === need;

  const toggle = (cid: number) => {
    setRanking((r) => (r.includes(cid) ? r.filter((x) => x !== cid) : r.length < need ? [...r, cid] : r));
  };
  const move = (i: number, dir: -1 | 1) => {
    setRanking((r) => {
      const next = [...r];
      [next[i], next[i + dir]] = [next[i + dir], next[i]];
      return next;
    });
  };

  const submit = async () => {
    setBusy(true);
    try {
      onCast(await voterApi.cast(token, ranking));
    } catch (e) {
      toast('error', errorMessage(e));
      setBusy(false);
      setConfirming(false);
    }
  };

  if (need === 0) {
    return (
      <div className="card narrow">
        <EmptyState icon={<Vote />} title="No candidates on this ballot">Please contact the election officer.</EmptyState>
      </div>
    );
  }

  return (
    <>
      <div className="spread" style={{ marginBottom: 20, alignItems: 'flex-end' }}>
        <div>
          <h1>Rank your choices</h1>
          <p className="muted" style={{ marginTop: 4 }}>
            {ballot.election.org_name}. Select {need} candidate{need === 1 ? '' : 's'} in order of preference.
          </p>
        </div>
        <div className="row" style={{ gap: 8 }}>
          <span className="token-chip">{ballot.reg_no}</span>
          <button className="btn btn-ghost btn-sm" onClick={onSignOut}><LogOut /> Sign out</button>
        </div>
      </div>

      <div className="ballot-layout">
        <div className="card list" role="group" aria-label="Candidates">
          {ballot.candidates.map((c) => {
            const pos = ranking.indexOf(c.candidate_id);
            const ranked = pos >= 0;
            const full = !ranked && complete;
            return (
              <button
                key={c.candidate_id}
                className={`row-button cand-row ${ranked ? 'ranked' : ''}`}
                onClick={() => toggle(c.candidate_id)}
                disabled={full}
                aria-pressed={ranked}
                aria-label={`${c.name}${ranked ? `, ranked ${ORDINAL[pos]}. Select to remove.` : full ? '. Your ballot is full.' : `. Select to rank ${ORDINAL[ranking.length]}.`}`}
              >
                <Avatar name={c.name} />
                <div className="cand-info">
                  <h3>{c.name}</h3>
                  {c.platform_statement && <p>{c.platform_statement}</p>}
                </div>
                <span className="rank-chip">{ranked ? ORDINAL[pos] : full ? 'Full' : `Rank ${ORDINAL[ranking.length]}`}</span>
              </button>
            );
          })}
        </div>

        <aside className="card ranking-panel" aria-label="Your ballot">
          <div className="card-header">
            <h2>Your ballot</h2>
            <span className="subtle num">{ranking.length} of {need}</span>
          </div>
          <div className="card-body stack-sm">
            {Array.from({ length: need }, (_, i) => {
              const c = byId.get(ranking[i]);
              return (
                <div key={i} className={`slot ${c ? 'filled' : ''}`}>
                  <span className="slot-rank">{ORDINAL[i]}</span>
                  {c ? (
                    <>
                      <span className="slot-name">{c.name}</span>
                      <span className="slot-actions">
                        <button className="btn btn-ghost icon-btn btn-sm" aria-label={`Move ${c.name} up`} disabled={i === 0} onClick={() => move(i, -1)}><ArrowUp /></button>
                        <button className="btn btn-ghost icon-btn btn-sm" aria-label={`Move ${c.name} down`} disabled={i === ranking.length - 1} onClick={() => move(i, 1)}><ArrowDown /></button>
                        <button className="btn btn-ghost icon-btn btn-sm" aria-label={`Remove ${c.name}`} onClick={() => toggle(c.candidate_id)}><X /></button>
                      </span>
                    </>
                  ) : (
                    <span className="slot-name placeholder">{i === ranking.length ? 'Select a candidate' : 'Empty'}</span>
                  )}
                </div>
              );
            })}
            <button className="btn btn-primary btn-lg btn-block" style={{ marginTop: 8 }} disabled={!complete} onClick={() => setConfirming(true)}>
              Review ballot
            </button>
            {ranking.length > 0 && (
              <button className="btn btn-ghost btn-sm" onClick={() => setRanking([])}>Clear ballot</button>
            )}
          </div>
        </aside>
      </div>

      <div className="mobile-submit">
        <div>
          <strong className="num">{ranking.length} of {need} ranked</strong>
          <div className="subtle">{complete ? 'Ready to review' : `Select your ${ORDINAL[ranking.length]} choice`}</div>
        </div>
        <button className="btn btn-primary btn-lg" disabled={!complete} onClick={() => setConfirming(true)}>Review ballot</button>
      </div>

      <ConfirmDialog
        open={confirming}
        busy={busy}
        icon={<ShieldCheck />}
        title="Cast this ballot?"
        confirmLabel="Cast ballot"
        onCancel={() => setConfirming(false)}
        onConfirm={submit}
        body={
          <div className="stack-sm">
            <p>Your ranking for <strong style={{ color: 'var(--text)' }}>{ballot.election.org_name}</strong>:</p>
            <ol style={{ margin: '4px 0', paddingLeft: 20, color: 'var(--text)', fontWeight: 500 }}>
              {ranking.map((cid) => <li key={cid}>{byId.get(cid)?.name}</li>)}
            </ol>
            <p>Once cast, a ballot can’t be changed.</p>
          </div>
        }
      />
    </>
  );
}

// ----------------------------------------------------------------- receipt

function Done({ receipt, election }: { receipt: CastResult; election: PublicElection }) {
  const navigate = useNavigate();
  return (
    <div className="narrow" style={{ maxWidth: 520 }}>
      <div className="card">
        <div className="card-body stack">
          <div className="row">
            <span className="receipt-icon"><Check /></span>
            <div>
              <h1>Ballot cast</h1>
              <p className="muted">{election.org_name} · Election #{election.election_id}</p>
            </div>
          </div>
          <div className="stack-sm">
            <span className="label-text">Receipt token</span>
            <div className="token-box">
              <code>{receipt.ballot_token}</code>
              <CopyButton text={receipt.ballot_token} />
            </div>
            <p className="hint">Save this token. It doesn’t reveal how you voted, but it shows whether your ballot is recorded and still counted.</p>
          </div>
          <dl className="kv">
            <dt>Ledger block</dt><dd className="mono">#{receipt.block_index}</dd>
            <dt>Block hash</dt><dd className="mono">{receipt.block_hash.slice(0, 24)}…</dd>
          </dl>
        </div>
        <div className="card-foot row" style={{ justifyContent: 'flex-end', gap: 8 }}>
          <Link to={`/verify?token=${receipt.ballot_token}`} className="btn"><ReceiptText /> Check receipt</Link>
          <button className="btn btn-primary" onClick={() => navigate('/')}>Done</button>
        </div>
      </div>
    </div>
  );
}
