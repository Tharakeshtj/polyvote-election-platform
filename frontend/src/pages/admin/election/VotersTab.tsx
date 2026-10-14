import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react';
import { Search, UserPlus, Users, UsersRound } from 'lucide-react';
import { adminApi, errorMessage, type Voter } from '../../../api';
import { EmptyState, PageLoading, Spinner, useToast } from '../../../components/ui';
import type { TabProps } from './ElectionPage';

const PAGE = 25;
type Filter = 'all' | 'voted' | 'pending';

export default function VotersTab({ election, reload }: TabProps) {
  const toast = useToast();
  const editable = election.status !== 'CLOSED';
  const [voters, setVoters] = useState<Voter[] | null>(null);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<Filter>('all');
  const [page, setPage] = useState(0);

  const load = useCallback(() => {
    adminApi.voters(election.election_id).then(setVoters).catch((e) => toast('error', errorMessage(e)));
  }, [election.election_id, toast]);
  useEffect(load, [load]);

  const refresh = async () => { load(); await reload(); };

  const filtered = useMemo(() => {
    const q = query.trim().toUpperCase();
    return (voters ?? []).filter((v) =>
      (!q || v.student_reg_no.includes(q)) && (filter === 'all' || (filter === 'voted') === Boolean(v.has_voted)));
  }, [voters, query, filter]);
  useEffect(() => setPage(0), [query, filter]);
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE));
  const rows = filtered.slice(page * PAGE, page * PAGE + PAGE);

  return (
    <div className="grid-2" style={{ gridTemplateColumns: editable ? 'minmax(0, 1.5fr) minmax(0, 1fr)' : '1fr' }}>
      <div className="card">
        <div className="card-header">
          <div className="row" style={{ flex: 1, minWidth: 220 }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={16} style={{ position: 'absolute', left: 10, top: 10, color: 'var(--text-3)' }} />
              <input className="input" style={{ paddingLeft: 34 }} placeholder="Search registration no." value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search voters" />
            </div>
          </div>
          <select className="select" style={{ width: 'auto' }} value={filter} onChange={(e) => setFilter(e.target.value as Filter)} aria-label="Filter voters">
            <option value="all">All voters</option>
            <option value="voted">Voted</option>
            <option value="pending">Not voted</option>
          </select>
        </div>
        {!voters ? <PageLoading /> : voters.length === 0 ? (
          <EmptyState icon={<Users />} title="No voters registered">Add voters individually or bulk-register a demo roster.</EmptyState>
        ) : filtered.length === 0 ? (
          <EmptyState icon={<Search />} title="No matches">Try a different search or filter.</EmptyState>
        ) : (
          <>
            <div className="table-wrap">
              <table className="table">
                <thead><tr><th>Registration no.</th><th>Status</th></tr></thead>
                <tbody>
                  {rows.map((v) => (
                    <tr key={v.participation_id}>
                      <td className="mono">{v.student_reg_no}</td>
                      <td>{v.has_voted ? <span className="label label-success">Voted</span> : <span className="label">Not voted</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pager">
              <span>{filtered.length} voter{filtered.length === 1 ? '' : 's'}</span>
              <div className="row" style={{ gap: 6 }}>
                <button className="btn btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
                <span>Page {page + 1} of {pages}</span>
                <button className="btn btn-sm" disabled={page >= pages - 1} onClick={() => setPage(page + 1)}>Next</button>
              </div>
            </div>
          </>
        )}
      </div>

      {editable ? (
        <div className="stack">
          <AddVoter electionId={election.election_id} onDone={refresh} />
          <BulkRegister electionId={election.election_id} onDone={refresh} />
        </div>
      ) : null}
    </div>
  );
}

function AddVoter({ electionId, onDone }: { electionId: number; onDone: () => Promise<void> }) {
  const toast = useToast();
  const [reg, setReg] = useState('');
  const [pw, setPw] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    setBusy(true);
    try {
      const { reg_no } = await adminApi.addVoter(electionId, reg, pw);
      toast('success', `${reg_no} added to the roster.`);
      setReg('');
      setPw('');
      await onDone();
    } catch (e) {
      toast('error', errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card" onSubmit={submit}>
      <div className="card-header"><h2 className="section-title"><UserPlus /> Add a voter</h2></div>
      <div className="card-body stack">
        <div className="field">
          <label htmlFor="vr">Registration no.</label>
          <input id="vr" className="input input-mono" placeholder="25BCE9999" value={reg} onChange={(e) => setReg(e.target.value.toUpperCase())} />
        </div>
        <div className="field">
          <label htmlFor="vp">Access password</label>
          <input id="vp" type="password" className="input" autoComplete="new-password" value={pw} onChange={(e) => setPw(e.target.value)} />
          <span className="hint">Share this with the voter privately.</span>
        </div>
        <button className="btn btn-primary" disabled={busy || !reg.trim() || !pw}>{busy && <Spinner />} Add voter</button>
      </div>
    </form>
  );
}

function BulkRegister({ electionId, onDone }: { electionId: number; onDone: () => Promise<void> }) {
  const toast = useToast();
  const [count, setCount] = useState(25);
  const [busy, setBusy] = useState(false);

  const submit = async (ev: FormEvent) => {
    ev.preventDefault();
    setBusy(true);
    try {
      const r = await adminApi.bulkVoters(electionId, count);
      toast('success', `Registered ${r.added} voters starting at ${r.first} (password ${r.password}).`);
      await onDone();
    } catch (e) {
      toast('error', errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card" onSubmit={submit}>
      <div className="card-header"><h2 className="section-title"><UsersRound /> Bulk register demo voters</h2></div>
      <div className="card-body stack-sm">
        <p className="muted">Creates sequential <code>25BCE####</code> voters, all with the password <code>vote123</code>.</p>
        <div className="row">
          <input type="number" className="input" min={1} max={1000} value={count} onChange={(e) => setCount(Number(e.target.value))} style={{ width: 110 }} aria-label="Number of voters" />
          <button className="btn" disabled={busy || count < 1}>{busy && <Spinner />} Register</button>
        </div>
      </div>
    </form>
  );
}
