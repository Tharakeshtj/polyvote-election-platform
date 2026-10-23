import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Info } from 'lucide-react';
import { publicApi, type PublicConfig } from '../../api';
import { Breadcrumbs } from '../../components/Breadcrumbs';
import { usePageMeta } from '../../lib/meta';

type PageRow = { path: string; name: string; what: string; admin?: boolean };

const PAGES: PageRow[] = [
  { path: '/', name: 'Home', what: 'Open elections with their status; start voting or check a receipt.' },
  { path: '/vote/1', name: 'Vote', what: 'Sign in with registration number and password, enter the emailed code, rank three candidates, review, cast, keep the receipt.' },
  { path: '/verify', name: 'Check receipt', what: 'Paste a receipt token to see whether the ballot is sealed in the ledger and still in the count.' },
  { path: '/demo', name: 'Demo guide', what: 'This page: a tour of every page and the demo logins.' },
  { path: '/privacy', name: 'Privacy policy', what: 'What is stored about voters, where, who can see it and for how long.' },
  { path: '/contact', name: 'Contact', what: 'Working contact form; messages appear in Admin, Contact messages.' },
  { path: '/admin/login', name: 'Admin sign-in', what: 'Officer login.', admin: true },
  { path: '/admin', name: 'Elections', what: 'All elections with status and turnout.', admin: true },
  { path: '/admin/elections/new', name: 'New election', what: 'Create an organisation and election.', admin: true },
  { path: '/admin/elections/1/overview', name: 'Election: Overview', what: 'Phase control (nomination, voting, closed), counts, and ballot simulation.', admin: true },
  { path: '/admin/elections/1/candidates', name: 'Election: Candidates', what: 'Add or remove candidates while in nomination.', admin: true },
  { path: '/admin/elections/1/voters', name: 'Election: Voters', what: 'Roster, emails for the one-time code, add voter, bulk register.', admin: true },
  { path: '/admin/elections/1/results', name: 'Election: Results', what: 'Integrity sweep (five rules) and the instant-runoff count with rounds.', admin: true },
  { path: '/admin/elections/1/studio', name: 'Election: DB Studio', what: 'A simulated rogue database administrator: edit or delete ballots, then run the sweep to see it caught.', admin: true },
  { path: '/admin/ledger', name: 'Audit ledger', what: 'Every sealed receipt; the chain check shows "intact" or the first tampered block.', admin: true },
  { path: '/admin/outbox', name: 'Mail outbox', what: 'Every one-time code issued, its recipient and delivery status.', admin: true },
  { path: '/admin/messages', name: 'Contact messages', what: 'Messages sent through the public contact form.', admin: true },
  { path: '/admin/admins', name: 'Administrators', what: 'Add officer accounts.', admin: true },
  { path: '/admin/settings', name: 'Settings', what: 'Reset (disabled on the public demo).', admin: true },
];

export default function DemoGuide() {
  usePageMeta('Demo guide: every page of PolyVote', 'A tour of every page of the PolyVote demo with links, demo logins and a three-minute walkthrough.');
  const [cfg, setCfg] = useState<PublicConfig | null>(null);
  useEffect(() => { publicApi.config().then(setCfg).catch(() => {}); }, []);
  const demo = cfg?.hosted_demo;

  return (
    <div className="stack" style={{ maxWidth: 860, margin: '0 auto' }}>
      <Breadcrumbs items={[{ label: 'Home', to: '/' }, { label: 'Demo guide' }]} />
      <div>
        <h1>{demo ? 'Demo guide' : 'Guide to every page'}</h1>
        <p className="muted" style={{ marginTop: 4 }}>
          PolyVote is a ranked-choice election platform with a tamper-evident audit ledger and an emailed one-time code at sign-in.
        </p>
      </div>

      {demo && (
        <div className="callout callout-info" role="note">
          <Info />
          <div>
            <strong>This is the public demo.</strong> Data is created fresh when the server starts and resets when it restarts. The server may take about a minute to wake after being idle.
            {cfg?.otp_demo_hint && ' It cannot send email from here, so the one-time code is shown on the screen ("Demo mode").'}
          </div>
        </div>
      )}

      <section className="card">
        <div className="card-header"><h2>Try it in three minutes</h2></div>
        <div className="card-body stack-sm">
          <ol style={{ margin: 0, paddingLeft: 20, display: 'grid', gap: 8 }}>
            <li>Open <Link to="/vote/1">Vote</Link> and sign in as <code>25BCE0025</code> with password <code>vote123</code>. Voters <code>25BCE0019</code> to <code>25BCE0030</code> have not voted.</li>
            <li>Enter the 6-digit code {cfg?.otp_demo_hint ? 'shown in the blue box' : 'sent to the voter’s email'}, rank three candidates, and cast. Copy your receipt token.</li>
            <li>Open <Link to="/verify">Check receipt</Link>, paste the token, and see that the ballot is sealed and counted.</li>
            {demo && cfg?.admin_public && (
              <li>Open <Link to="/admin/login">Admin</Link> (user <code>admin</code>, password <code>admin123</code> on this demo only), go to Election 1, then <strong>Results</strong> and run the sweep. In <strong>DB Studio</strong> delete a ballot and run it again to watch it get caught.</li>
            )}
          </ol>
        </div>
      </section>

      <section className="card">
        <div className="card-header"><h2>Every page</h2><span className="subtle">Admin pages need a login</span></div>
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>Page</th><th>Address</th><th>What it shows</th></tr></thead>
            <tbody>
              {PAGES.map((p) => (
                <tr key={p.path}>
                  <td><Link to={p.path}>{p.name}</Link>{p.admin && <span className="label" style={{ marginLeft: 8 }}>admin</span>}</td>
                  <td className="mono">{p.path}</td>
                  <td className="muted">{p.what}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <div className="card-body stack-sm">
          <h2>What this demonstrates</h2>
          <ul style={{ margin: 0, paddingLeft: 20, display: 'grid', gap: 6 }}>
            <li>Rules enforced inside the database: one vote per voter, valid ranks, real candidates.</li>
            <li>Voters and ballots stored with no linking column; voter emails kept in a separate database.</li>
            <li>A keyed, hash-chained audit ledger and an integrity sweep that names edited, deleted or injected ballots.</li>
            <li>An emailed one-time code as a second factor, and QR-code voting from a phone.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
