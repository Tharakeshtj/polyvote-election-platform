import { useEffect } from 'react';

/** Keeps the tab title and meta description in step with the page (the server also writes them into the HTML for crawlers). */
export function usePageMeta(title: string, description?: string) {
  useEffect(() => {
    document.title = title;
    if (description) document.querySelector('meta[name="description"]')?.setAttribute('content', description);
  }, [title, description]);
}
