import { useCallback, useEffect, useState } from 'react';
import { Link, Navigate, NavLink, useParams } from 'react-router-dom';
import { BarChart3, ChevronRight, Database, LayoutDashboard, Lock, PlayCircle, UserSquare2, Users } from 'lucide-react';
import { adminApi, errorMessage, type ElectionDetail } from '../../../api';
import { ConfirmDialog, FormError, Lifecycle, PageLoading, StatusBadge, useToast } from '../../../components/ui';
import OverviewTab from './OverviewTab';
import CandidatesTab from './CandidatesTab';
import VotersTab from './VotersTab';
import ResultsTab from './ResultsTab';
import StudioTab from './StudioTab';

export interface TabProps {
  election: ElectionDetail;
  reload: () => Promise<void>;
}

const TABS = [
  { key: 'overview', label: 'Overview', icon: LayoutDashboard, Component: OverviewTab },
  { key: 'candidates', label: 'Candidates', icon: UserSquare2, Component: CandidatesTab },
  { key: 'voters', label: 'Voters', icon: Users, Component: VotersTab },
  { key: 'results', label: 'Results', icon: BarChart3, Component: ResultsTab },
  { key: 'studio', label: 'DB Studio', icon: Database, Component: StudioTab },
] as const;

export default function ElectionPage() {
  const { id, tab = 'overview' } = useParams();
  const electionId = Number(id);
  const toast = useToast();
  const [election, setElection] = useState<ElectionDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [transition, setTransition] = useState<'VOTING' | 'CLOSED' | null>(null);
  const [busy, setBusy] = useState(false);

  const reload = useCallback(async () => {
    try {
      setElection(await adminApi.election(electionId));
      setError(null);
    } catch (e) {
      setError(errorMessage(e));
    }
  }, [electionId]);
  useEffect(() => { setElection(null); reload(); }, [reload]);

  const active = TABS.find((t) => t.key === tab);
  if (!active) return <Navigate to={`/admin/elections/${electionId}`} replace />;
  if (error && !election) return <FormError message={error} />;
  if (!election) return <PageLoading />;

  const advance = async () => {
    if (!transition) return;
    setBusy(true);
    try {
      await adminApi.setStatus(electionId, transition);
      toast('success', transition === 'VOTING' ? 'Voting is now open.' : 'Voting closed. Results are ready to audit.');
      await reload();
    } catch (e) {
      toast('error', errorMessage(e));
    } finally {
      setBusy(false);
      setTransition(null);
    }
  };

  const Tab = active.Component;
  const tooFew = election.candidates.length < 3;

  return (
    <>
      <div className="crumbs"><Link to="/admin">Elections</Link><ChevronRight /> <span>#{election.election_id}</span></div>
      <div className="page-head">
        <div>
          <div className="row wrap" style={{ gap: 10 }}>
            <h1>{election.org_name}</h1>
            <StatusBadge status={election.status} />
          </div>
          <div style={{ marginTop: 14 }}><Lifecycle status={election.status} /></div>
        </div>
        {election.status === 'NOMINATION' && (
          <button className="btn btn-primary" onClick={() => setTransition('VOTING')} disabled={election.candidates.length === 0}
            title={election.candidates.length === 0 ? 'Add candidates first' : undefined}>
            <PlayCircle /> Open voting
          </button>
        )}
        {election.status === 'VOTING' && (
          <button className="btn btn-danger" onClick={() => setTransition('CLOSED')}><Lock /> Close voting</button>
        )}        {election.status === 'CLOSED' && (
          <Link to={`/admin/elections/${electionId}/results`} className="btn btn-primary"><BarChart3 /> View results</Link>
        )}
      </div>

      <nav className="tabs" style={{ marginBottom: 24 }} aria-label="Election sections">
        {TABS.map((t) => {
          const count = t.key === 'candidates' ? election.candidates.length : t.key === 'voters' ? election.voters : t.key === 'results' ? election.ballots : null;
          return (
            <NavLink key={t.key} to={`/admin/elections/${electionId}${t.key === 'overview' ? '' : `/${t.key}`}`} end
              className={() => `tab ${t.key === active.key ? 'active' : ''}`} aria-current={t.key === active.key ? 'page' : undefined}>
              <t.icon /> {t.label}
              {count !== null && <span className="counter">{count}</span>}
            </NavLink>
          );
        })}
      </nav>

      <Tab election={election} reload={reload} />

      <ConfirmDialog
        open={transition === 'VOTING'}
        busy={busy}
        title="Open voting?"
        confirmLabel="Open voting"
        icon={<PlayCircle />}
        onCancel={() => setTransition(null)}
        onConfirm={advance}
        body={
          <div className="stack-sm">
            <p>The candidate list will be locked and registered voters can start casting ballots.</p>
            {tooFew && (
              <p style={{ color: 'var(--attention)' }}>
                Only {election.candidates.length} candidate{election.candidates.length === 1 ? '' : 's'}: voters will rank fewer than 3 and ballot simulation won't be available.
              </p>
            )}
          </div>
        }
      />
      <ConfirmDialog
        open={transition === 'CLOSED'}
        busy={busy}
        tone="danger"
        title="Close voting permanently?"
        confirmLabel="Close voting"
        onCancel={() => setTransition(null)}
        onConfirm={advance}
        body={<p>{election.voters - election.voted} registered voter{election.voters - election.voted === 1 ? ' has' : 's have'} not voted yet. Closed elections can't be reopened.</p>}
      />
    </>
  );
}
