import { Link } from 'react-router-dom';
import { Breadcrumbs } from '../../components/Breadcrumbs';
import { usePageMeta } from '../../lib/meta';

const ROWS: [string, string, string][] = [
  ['Registration number', 'Election database (voter roster)', 'Checks you are on the roster and whether you have already voted.'],
  ['Password', 'Election database, as a SHA-256 hash only', 'Signs you in. The plain password is never stored.'],
  ['Email address', 'Verification database (a separate file)', 'Sends your one-time code. It is never stored with ballots.'],
  ['One-time code', 'Verification database, as a keyed hash only', 'Checks the code you type. Valid 5 minutes, one use, 3 guesses.'],
  ['Your ballot (ranked choices)', 'Election database, under a random token', 'Counts the result. No column links it to you.'],
  ['Receipt block', 'Audit ledger', 'Holds the ballot token and a hash of the choices, so tampering can be detected.'],
  ['Contact message (name, email, text)', 'Verification database', 'Answers you. Only administrators can read it.'],
];

export default function Privacy() {
  usePageMeta('Privacy policy | PolyVote', 'What PolyVote stores about voters, where it is stored, who can see it and how long it is kept.');
  return (
    <div className="medium stack">
      <Breadcrumbs items={[{ label: 'Home', to: '/' }, { label: 'Privacy policy' }]} />
      <header className="page-intro">
        <h1>Privacy policy</h1>
        <p>PolyVote is a course project. This page says in plain words what the system stores and why. Last updated 23 October 2026.</p>
      </header>

      <section className="card">
        <div className="card-header"><h2>What is stored, and where</h2></div>
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>Data</th><th>Stored in</th><th>Why</th></tr></thead>
            <tbody>{ROWS.map(([a, b, c]) => <tr key={a}><td>{a}</td><td>{b}</td><td className="muted">{c}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <div className="card-body stack-sm">
          <h2>Your vote stays secret</h2>
          <p>The ballot table and the voter table share no column, so the database cannot tell who cast which ballot. Your email address lives in a different database file from the ballots. The receipt token you receive proves your ballot is recorded and counted; if you share the token, anyone who also has database access could see the choices stored under it.</p>
          <h2>Who can see what</h2>
          <p>Election officers can see the roster, voter email addresses and the Mail outbox (which lists codes for ten minutes). Nobody can look up a voter&apos;s choices through the application. A person with direct access to the database files could read ballots but not link them to people.</p>
          <h2>Cookies, tracking and analytics</h2>
          <p>PolyVote sets no tracking cookies. The administrator console keeps a session token in your browser until you sign out. Your connection address is held in memory only, to limit repeated requests, and is not saved. Google Analytics is off unless the site operator turns it on, and then it reports which pages are used.</p>
          <h2>How long data is kept</h2>
          <p>On the public demo, all data is replaced when the server restarts. In your own deployment, data stays until an administrator removes it.</p>
          <h2>Questions or removal requests</h2>
          <p>Use the <Link to="/contact">contact form</Link>.</p>
        </div>
      </section>
    </div>
  );
}
