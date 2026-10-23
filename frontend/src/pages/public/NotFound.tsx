import { Link } from 'react-router-dom';
import { SearchX } from 'lucide-react';
import { EmptyState } from '../../components/ui';
import { usePageMeta } from '../../lib/meta';

export default function NotFound() {
  usePageMeta('Page not found | PolyVote', 'That page does not exist.');
  return (
    <div className="narrow card">
      <EmptyState icon={<SearchX />} title="Page not found">
        There is nothing at this address. <Link to="/">Go to the home page</Link>, open the <Link to="/demo">demo guide</Link>, or <Link to="/contact">contact us</Link>.
      </EmptyState>
    </div>
  );
}
