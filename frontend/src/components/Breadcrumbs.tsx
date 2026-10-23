import { Link } from 'react-router-dom';

export function Breadcrumbs({ items }: { items: { label: string; to?: string }[] }) {
  return (
    <nav aria-label="Breadcrumb" className="subtle" style={{ fontSize: 13, marginBottom: 12 }}>
      <ol style={{ listStyle: 'none', display: 'flex', flexWrap: 'wrap', gap: 6, margin: 0, padding: 0 }}>
        {items.map((it, i) => (
          <li key={it.label}>
            {it.to ? <Link to={it.to}>{it.label}</Link> : <span aria-current="page">{it.label}</span>}
            {i < items.length - 1 && <span aria-hidden="true"> /</span>}
          </li>
        ))}
      </ol>
    </nav>
  );
}
