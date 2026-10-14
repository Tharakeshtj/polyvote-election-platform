# Surface brief: PolyVote web app (voter booth + admin console)

Scope: every route in `frontend/src` (voter home, vote flow, receipt check, admin console). Mode: **Operate**. Build path: code-led (Operate surface; engine unavailable, no comps).

Audience and job: students cast one top-3 ranked ballot on phones or laptops; officers run the lifecycle and audit at laptops; results and sweeps are projected for a room. Every existing feature stays; no new claims.

## Direction contract

THESIS: PolyVote is a working product of the Vercel/GitHub class: the task is visible first, state is always legible, nothing decorates. It refuses the generic AI-dashboard default of tinted cards, stat tiles, eyebrow pills, gradients and modals-for-everything.

OWN-WORLD: Vercel neutrals (white ground, #fafafa second layer, hairline #ebebeb borders, #171717 ink, black primary buttons), Geist Sans + Geist Mono (mono only for tokens, hashes, registration numbers, counts in tables), GitHub Primer state colours (success green, attention amber, danger red, accent blue for links, focus and selection), 6px radii, Box-and-row lists, underline tabs with counters, dot-plus-word status.

STORY: a voter sees open elections and a receipt check on the first screen, signs in, ranks three candidates in a single list, confirms, keeps a token. An officer sees every election's state in one table, moves it through its lifecycle with guarded buttons, and proves integrity with a sweep that shows exactly what it found.

FIRST VIEWPORT: voter home: top bar (PolyVote wordmark left, "Verify receipt" and "Admin" right); 32px title "Vote in an election" with one line of context; a bordered list of elections, open ones first, each row with status dot, organisation, candidate count and a black "Vote" button on the right; directly below, an inline receipt-check field. Admin: left sidebar, page title plus primary action top right, then the content table.

ADAPTATIONS (recorded after the finish review, 2026-10-15): dialogs keep a 12px radius, as Primer overlays do; everything else is 6px. The top-bar link reads "Check receipt" because "check" is the product's verb on the home form, the receipt screen and the verify page.

FORM: category standard (standing exit), benchmarked against Vercel and GitHub. seed: none (unavailable)

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
