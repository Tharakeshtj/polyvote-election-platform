---
name: PolyVote
description: Ranked-choice elections with a tamper-evident ballot ledger, built to the Vercel and GitHub standard of product UI.
colors:
  bg: "#ffffff"
  bg-subtle: "#fafafa"
  bg-muted: "#f2f2f2"
  border: "#ebebeb"
  border-strong: "#d4d4d4"
  text: "#171717"
  text-2: "#5c5c5c"
  text-3: "#737373"
  ink: "#171717"
  ink-hover: "#383838"
  on-ink: "#ffffff"
  accent: "#0969da"
  accent-soft: "#ddf4ff"
  accent-border: "#54aeff66"
  success: "#1a7f37"
  success-soft: "#dafbe1"
  success-border: "#4ac26b66"
  attention: "#9a6700"
  attention-soft: "#fff8c5"
  attention-border: "#d4a72c66"
  danger: "#cf222e"
  danger-hover: "#a40e26"
  danger-soft: "#ffebe9"
  danger-border: "#ff818266"
  on-danger: "#ffffff"
  danger-emphasis: "#cf222e"
  danger-emphasis-hover: "#a40e26"
  scrim: "rgba(0, 0, 0, 0.32)"
  bg-dark: "#0a0a0a"
  bg-subtle-dark: "#111111"
  bg-muted-dark: "#1c1c1c"
  border-dark: "#262626"
  border-strong-dark: "#3a3a3a"
  text-dark: "#ededed"
  text-2-dark: "#a1a1a1"
  text-3-dark: "#8f8f8f"
  ink-dark: "#ededed"
  ink-hover-dark: "#cfcfcf"
  on-ink-dark: "#0a0a0a"
  accent-dark: "#4493f8"
  accent-soft-dark: "#121d2f"
  accent-border-dark: "#388bfd66"
  success-dark: "#3fb950"
  success-soft-dark: "#12261e"
  success-border-dark: "#2ea04366"
  attention-dark: "#d29922"
  attention-soft-dark: "#272115"
  attention-border-dark: "#bb800966"
  danger-dark: "#f85149"
  danger-hover-dark: "#ff7b72"
  danger-soft-dark: "#25171c"
  danger-border-dark: "#f8514966"
  danger-emphasis-dark: "#da3633"
  danger-emphasis-hover-dark: "#b62324"
typography:
  display:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "2rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  title:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-0.01em"
  title-sm:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.4
  body-lg:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1rem"
    fontWeight: 500
    lineHeight: 1.5
  body:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 500
    lineHeight: 1.5
  caption:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1
  figure:
    fontFamily: "'Geist Variable', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.5
    fontFeature: "tnum"
  mono:
    fontFamily: "'Geist Mono Variable', ui-monospace, 'Cascadia Code', Consolas, monospace"
    fontSize: "0.92em"
    fontWeight: 400
    fontFeature: "tnum"
rounded:
  inline: "4px"
  r-sm: "6px"
  r: "6px"
  r-lg: "12px"
  pill: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  2xl: "32px"
  3xl: "40px"
  4xl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.r-sm}"
    padding: "0 12px"
    height: "32px"
  button-primary-hover:
    backgroundColor: "{colors.ink-hover}"
    textColor: "{colors.on-ink}"
  button-default:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
    rounded: "{rounded.r-sm}"
    padding: "0 12px"
    height: "32px"
  button-default-hover:
    backgroundColor: "{colors.bg-muted}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.text-2}"
    rounded: "{rounded.r-sm}"
    padding: "0 12px"
    height: "32px"
  button-ghost-hover:
    backgroundColor: "{colors.bg-muted}"
    textColor: "{colors.text}"
  button-danger:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.danger}"
    rounded: "{rounded.r-sm}"
    height: "32px"
  button-danger-hover:
    backgroundColor: "{colors.danger-emphasis}"
    textColor: "{colors.on-danger}"
  button-danger-solid:
    backgroundColor: "{colors.danger-emphasis}"
    textColor: "{colors.on-danger}"
    rounded: "{rounded.r-sm}"
    height: "32px"
  button-danger-solid-hover:
    backgroundColor: "{colors.danger-emphasis-hover}"
  button-sm:
    typography: "{typography.body-sm}"
    padding: "0 10px"
    height: "28px"
  button-lg:
    padding: "0 16px"
    height: "40px"
  input:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.r-sm}"
    padding: "0 12px"
    height: "36px"
  input-lg:
    typography: "{typography.body-lg}"
    height: "40px"
  input-sm:
    typography: "{typography.body-sm}"
    padding: "0 8px"
    height: "28px"
  box:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
    rounded: "{rounded.r}"
  box-header:
    backgroundColor: "{colors.bg-subtle}"
    typography: "{typography.title-sm}"
    padding: "12px 16px"
  box-body:
    padding: "16px"
  list-row:
    backgroundColor: "{colors.bg}"
    padding: "12px 16px"
  list-row-hover:
    backgroundColor: "{colors.bg-subtle}"
  tab:
    textColor: "{colors.text-2}"
    typography: "{typography.label}"
    padding: "8px 4px 10px"
  tab-active:
    textColor: "{colors.text}"
  counter:
    backgroundColor: "{colors.bg-muted}"
    textColor: "{colors.text-2}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: "0 6px"
    height: "18px"
  label:
    backgroundColor: "transparent"
    textColor: "{colors.text-2}"
    typography: "{typography.caption}"
    rounded: "{rounded.pill}"
    padding: "0 7px"
    height: "20px"
  label-success:
    backgroundColor: "{colors.success-soft}"
    textColor: "{colors.success}"
  label-attention:
    backgroundColor: "{colors.attention-soft}"
    textColor: "{colors.attention}"
  label-danger:
    backgroundColor: "{colors.danger-soft}"
    textColor: "{colors.danger}"
  label-accent:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent}"
  status:
    textColor: "{colors.text}"
    typography: "{typography.label}"
  flash-success:
    backgroundColor: "{colors.success-soft}"
    textColor: "{colors.text}"
    rounded: "{rounded.r-sm}"
    padding: "12px 16px"
  flash-attention:
    backgroundColor: "{colors.attention-soft}"
    textColor: "{colors.text}"
    rounded: "{rounded.r-sm}"
    padding: "12px 16px"
  flash-danger:
    backgroundColor: "{colors.danger-soft}"
    textColor: "{colors.text}"
    rounded: "{rounded.r-sm}"
    padding: "12px 16px"
  flash-info:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.text}"
    rounded: "{rounded.r-sm}"
    padding: "12px 16px"
  dialog:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
    rounded: "{rounded.r-lg}"
    width: "min(460px, calc(100vw - 32px))"
  dialog-footer:
    backgroundColor: "{colors.bg-subtle}"
    padding: "12px 20px"
  toast:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.text}"
    typography: "{typography.body}"
    rounded: "{rounded.r}"
    padding: "12px 14px"
    width: "360px"
  skeleton:
    backgroundColor: "{colors.bg-muted}"
    rounded: "{rounded.inline}"
    height: "12px"
  summary-row:
    textColor: "{colors.text-2}"
    typography: "{typography.body}"
    padding: "10px 16px"
  reconcile-cell:
    textColor: "{colors.text}"
    typography: "{typography.figure}"
    padding: "12px 16px"
  round-bar-track:
    backgroundColor: "{colors.bg-muted}"
    height: "20px"
  round-bar-fill:
    backgroundColor: "{colors.text-3}"
  round-bar-lead:
    backgroundColor: "{colors.success}"
  round-bar-out:
    backgroundColor: "{colors.border-strong}"
    textColor: "{colors.text-3}"
  meter:
    backgroundColor: "{colors.bg-muted}"
    rounded: "{rounded.pill}"
    height: "8px"
  token-chip:
    backgroundColor: "{colors.bg-muted}"
    typography: "{typography.mono}"
    rounded: "{rounded.inline}"
    padding: "1px 6px"
---

# Design System: PolyVote

## Overview

**Creative North Star: "The Open Ledger"**

PolyVote is a working product of the Vercel and GitHub class, played straight. Every screen leads with its task, every piece of state carries a word, and nothing on the page is there to decorate. The ledger in the name is literal: the product exists to prove that stored votes match what voters cast, so the visual system behaves like a ledger too. Hairline rules, labelled rows, numbers that line up, and proof shown in place rather than asserted.

The world is built from two well-known materials. Vercel supplies the ground: a white canvas, a #fafafa second layer, hairline borders, near-black ink, black primary buttons, Geist and Geist Mono. GitHub Primer supplies the state vocabulary: success green, attention amber, danger red, and an accent blue kept for links, focus, selection and information. The two meet in Primer's own structures (Boxes of rows, underline tabs with counters, Labels, flashes) set in Vercel's neutrals. Light is the default scene because results are projected and ballots are cast on phones in daylight; dark follows the operating system.

Density is that of an operator console: 14px body, 32px controls, 12 to 16px row insets. The system refuses the generic AI-dashboard default outright. It has no stat tiles, no tinted cards, no gradients, no eyebrow labels, no nested boxes and no decorative halos.

**Key Characteristics:**
- White ground, #fafafa headers and hover rows, hairline #ebebeb borders; depth comes from tone and rules, not shadow.
- Ink-black primary action; blue is never a button fill.
- State colours only report state, and always next to a word.
- Box-and-row lists, underline tabs with counters, dot-plus-word status.
- Geist Sans for everything; Geist Mono only for identifiers.
- 6px corners everywhere except dialogs (12px), pills for Labels and counters, and 4px for inline tokens.

## Colors

A neutral Vercel ground with four Primer state hues. Each hue has a strong, a soft and a translucent-border step, redefined as a set for dark mode.

### Primary
- **Ink** (#171717 light / #ededed dark): primary buttons, the active tab underline, completed lifecycle and stepper dots, ranked-candidate chips, filled ballot-slot numbers, the brand mark. Hover lifts to **Ink Hover** (#383838 / #cfcfcf). Text on ink is **On Ink** (#ffffff / #0a0a0a).

### Secondary
- **Accent Blue** (#0969da / #4493f8): links, the focus outline, focused-input border, text caret, info flashes and accent Labels. **Accent Soft** (#ddf4ff / #121d2f) fills the selection highlight, the 3px input focus ring and info flashes. **Accent Border** (#54aeff66 / #388bfd66) outlines them.

### Tertiary (state)
- **Success Green** (#1a7f37 / #3fb950): the "Voting open" dot, the winning round bar, turnout meters, done checks, passed-sweep flashes. Soft #dafbe1 / #12261e; border #4ac26b66 / #2ea04366.
- **Attention Amber** (#9a6700 / #d29922): the "Nominations" dot, counts that disagree with the other two, warning flashes. Soft #fff8c5 / #272115; border #d4a72c66 / #bb800966.
- **Danger Red** (#cf222e / #f85149): destructive buttons, "Tampering detected" flashes, Modified and Deleted Labels, the Danger zone Box. Solid hover #a40e26 / #ff7b72. Soft #ffebe9 / #25171c; border #ff818266 / #f8514966. Text on a danger fill is white (#ffffff) in both schemes, so solid fills use **Danger Emphasis** (#cf222e / #da3633, hover #a40e26 / #b62324). The brighter dark-mode Danger Red fails AA under white text and is reserved for danger-coloured text, borders and icons.

### Neutral
- **Canvas** (#ffffff / #0a0a0a): page ground, Box bodies, controls.
- **Subtle** (#fafafa / #111111): Box headers and footers, table heads, hovered rows, ranked rows, the admin sidebar, the login backdrop.
- **Muted** (#f2f2f2 / #1c1c1c): button hover, counters, avatars, meter and bar tracks, skeletons, inline token chips.
- **Hairline** (#ebebeb / #262626): every Box border and row divider.
- **Strong Hairline** (#d4d4d4 / #3a3a3a): control borders, Label outlines, stepper connectors, eliminated round bars, scrollbar thumb.
- **Text** (#171717 / #ededed), **Secondary Text** (#5c5c5c / #a1a1a1) and **Tertiary Text** (#737373 / #8f8f8f): body, supporting copy, and hints, placeholders and closed-status dots.
- **Scrim** (rgba(0,0,0,0.32)): dialog backdrop and the mobile drawer overlay.

### Named Rules
**The Ink Primary Rule.** The primary action is an ink-black button. Blue never fills a button; it belongs to links, focus, selection and information.

**The State-Only Colour Rule.** Green, amber and red appear only to report state: status dots, Labels, flashes, the lead round bar, a disagreeing count. They are never decoration, section colour or brand colour.

**The Dot-Plus-Word Rule.** No meaning is carried by colour alone. Every status dot sits beside its word ("Voting open", "Nominations", "Closed"), and every amber count is also explained by a flash.

## Typography

**Display Font:** Geist Variable (with ui-sans-serif, system-ui, Segoe UI)
**Body Font:** Geist Variable
**Label/Mono Font:** Geist Mono Variable (with ui-monospace, Cascadia Code, Consolas)

**Character:** One grotesque does all the talking at three weights. Mono appears only where the content is machine-shaped. The pairing reads as Vercel's own product UI. Headings tighten slightly as they grow, and figures are always tabular.

### Hierarchy
- **Display** (600, 32px, 1.25, -0.03em): the voter home page title only. Drops to 24px under 640px.
- **Headline** (600, 24px, 1.25, -0.02em): every other page's h1 (admin page heads, sign-in, ballot, receipt).
- **Title** (600, 16px, 1.4, -0.01em): section and dialog titles.
- **Title Small** (600, 14px, 1.4): Box header titles, round headings, h3.
- **Body Large** (500, 16px, 1.5): candidate names, election names in the voter list, round-bar rows; 400 for the home intro paragraph (max 60ch).
- **Body** (400, 14px, 1.5): default text, table cells, buttons and tabs at 500.
- **Body Small / Label** (400 or 500, 13px): hints, subtle meta lines, table heads, field labels, status words, small buttons.
- **Caption** (500, 12px, line-height 1): Labels, counters, sidebar group names in sentence case.
- **Figure** (600, 20px, tabular): the three reconcile counts.
- **Mono** (400, 0.92em of context, tabular): receipt tokens, block hashes, registration numbers, election IDs, demo credentials.

### Named Rules
**The Mono-for-Identifiers Rule.** Geist Mono is reserved for strings a person copies or compares character by character: tokens, hashes, registration numbers, IDs. Counts and percentages stay in Geist with tabular figures.

**The Three Weights Rule.** Only 400, 500 and 600. Emphasis comes from weight 500 or ink colour, never from 700, uppercase or letter-spacing.

## Layout

The spatial model is an operator console. Public pages sit in a centred column (1040px shell, 680px "medium" reading column, 420px "narrow" form column) under a 56px sticky top bar. The admin console is a 240px sticky sidebar on #fafafa beside a content area capped at 1200px with 32px/40px padding. Each page starts with a title and one line of context, with the primary action at the top right, followed directly by the content Box.

Spacing runs on a 4px base. The working steps are 4, 8, 12, 16, 24, 32, 40 and 48px. Odd steps (6, 10, 14, 20, 28px) appear only as optical adjustments inside components. Rows inset 12px by 16px (16px for election rows), Box bodies pad 16px, and stacked Boxes and sections gap 16px (24px for page-level stacks). Two-column admin grids gap 16px; the ballot uses a list plus a 320px sticky ballot panel with a 24px gap.

Responsive rules, all observed in the build:
- **≤900px:** the admin sidebar becomes a 260px off-canvas drawer with a scrim and a 52px mobile bar. Admin padding drops to 20/16/56px. The ballot collapses to one column, and a fixed bottom submit bar appears with the count and "Review ballot".
- **≤860px:** two-column grids stack.
- **≤720px:** the home "how it works" trio stacks.
- **≤640px:** the top bar and page gutters drop to 16px, display type goes from 32 to 24px, and round bars reflow so name and count share a line with a full-width 12px bar beneath, keeping bars comparable.
- **≤560px:** Box headers, footers and summary lists share one 12px inset. The reconcile strip stacks into rows. Election rows wrap with the status on its own line.

Touch targets are 32px controls by default, 40px for primary voter actions and sign-in fields, and 68px for candidate rows.

### Named Rules
**The Box-and-Row Rule.** Collections are a bordered Box of hairline-divided rows with a #fafafa header, never a grid of cards.

**The Flush Strip Rule.** A sub-region inside a Box is separated by hairlines and stays flush to the Box edges. A Box never contains another Box.

## Elevation & Depth

The system is flat at rest. Depth is tonal: #fafafa headers, footers and hover rows sit one step above the white canvas, and hairlines do the rest. Shadows exist only for surfaces that actually float above the page.

### Shadow Vocabulary
- **Pop** (`box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 16px -4px rgba(0,0,0,0.08), 0 24px 32px -8px rgba(0,0,0,0.08)`; dark uses 0.4/0.5/0.5 alpha): dialogs, toasts, and the open mobile drawer.
- **Bar** (`box-shadow: 0 -1px 2px rgba(0,0,0,0.03), 0 -8px 16px -8px rgba(0,0,0,0.08)`; dark `0 -8px 16px -8px rgba(0,0,0,0.6)`): the fixed mobile ballot submit bar.

State rings are not shadows. Focused inputs get a 3px Accent Soft ring, and the current lifecycle dot gets a 3px Muted ring. Both report state and never decorate.

### Named Rules
**The Flat-at-Rest Rule.** Nothing on the page plane casts a shadow. Only dialogs, toasts, the drawer and the bottom bar float, and only they carry one.

## Shapes

The geometry is rectangular and quiet. One 6px radius covers every button, input, select, Box, flash, toast, nav link, rank chip, ballot slot and the brand mark. Dialogs take 12px, following Primer overlays, as recorded in the contract's ADAPTATIONS. Pills (999px) are kept for things that are inherently pill-shaped in Primer: Labels, counters and meters. Small inline wells (token chips, slot rank numbers, skeleton bars) use 4px, and round-bar ends use 3px. Status dots, stepper dots and avatars are circles. Borders are always 1px hairlines; the only 2px line is the active tab underline. Empty ballot slots use a dashed hairline, which turns solid when filled.

### Named Rules
**The Two Radii Rule.** Containers and controls are 6px and dialogs are 12px. Any other radius belongs to a pill, a dot or an inline token, never to a container.

## Components

### Buttons
Restrained and exact, in the Vercel mould.
- **Shape:** gently squared (6px), 1px border, label 14px/500 with an optional 16px leading icon at a 6px gap.
- **Default:** canvas fill, Strong Hairline border, text colour; 32px high, 12px side padding. Hover fills Muted.
- **Primary:** Ink fill and border, On Ink text; hover goes to Ink Hover.
- **Danger (outline):** danger-coloured text on canvas; hover fills solid Danger Red with white text. Used for "Close voting".
- **Danger solid:** Danger Red fill, white text, hover to the darker step. Used for confirming destructive dialogs.
- **Ghost:** transparent with Secondary Text; hover fills Muted. Used for the top-bar link, back links, sign out, and slot reorder icons.
- **Sizes:** small 28px (13px text, 10px padding), default 32px, large 40px (16px padding). Icon-only buttons are square.
- **States:** colours transition over 150ms on the house ease-out; pressing nudges down 0.5px; disabled is 45% opacity with a not-allowed cursor. A busy action swaps its icon for a 14px spinner and keeps its label.

### Inputs / Fields
- **Style:** 36px high (40px large, 28px small), 6px radius, Strong Hairline border, canvas fill, 14px text, Tertiary Text placeholder. Registration numbers and receipt tokens switch to Geist Mono.
- **Hover:** the border darkens to Tertiary Text.
- **Focus:** the border turns Accent Blue with a 3px Accent Soft ring; there is no outline glow beyond that.
- **Labels and help:** 13px/500 label above with a 6px gap; 13px Tertiary Text hint below.
- **Error:** an inline danger flash (Danger Soft fill, Danger Border, danger text, alert icon) placed above the submit button.

### Boxes and List Rows
The signature container, taken from GitHub's Box.
- **Box:** canvas fill, 1px Hairline border, 6px radius, no shadow.
- **Header:** #fafafa, a 49px minimum, 12px by 16px padding, 14px/600 title, optional 13px subtle description below it, and actions or a subtle count on the right. The footer mirrors the header with a top hairline.
- **Rows:** 12px by 16px (election rows 16px), top hairline between rows, none under the header. Clickable rows and table rows hover to #fafafa over 150ms.
- **Ranked candidate rows:** stay #fafafa while ranked; the trailing rank chip flips from an outline "Rank 2nd" to an ink "1st".
- **Danger zone:** the only tinted Box header, Danger Soft over a Danger Border (GitHub's pattern).

### Underline Tabs with Counters
- **Style:** a row of 14px/500 Secondary Text tabs on a 1px inset hairline baseline, each with a 16px Tertiary Text icon and an optional counter.
- **States:** hover darkens the text and shows a Strong Hairline underline. Active has text colour, an icon in text colour and a 2px Ink underline.
- **Counter:** a Muted pill, 18px line, 12px/500 tabular Secondary Text, minimum 20px wide.
- **Mobile:** scrolls horizontally with a hidden scrollbar.

### Status (Dot Plus Word)
An 8px circle followed by a 13px word in text colour at a 6px gap. Green means "Voting open", amber "Nominations", tertiary grey "Closed". It never appears as a filled pill.

### Labels
Primer Labels: a 20px pill, 7px side padding, 12px/500 type, 1px border. The neutral variant uses a Strong Hairline outline with Secondary Text. The success, attention, danger and accent variants use the hue's text, translucent border and soft fill. Labels mark facts about a row ("Modified", "Deleted", "Majority reached", "Admin"), not section headings.

### Flashes (Primer)
Full-width notices with a 6px radius, 12px by 16px padding, 14px text colour and a 16px leading icon in the hue. Four tones: ok (success), warn (attention), danger and info (accent), each a soft fill with a translucent border. A bold lead phrase states the verdict ("Sweep passed.", "Tampering detected."), followed by the evidence.

### Dialogs
Native `<dialog>`, 12px radius, Hairline border, Pop shadow, Scrim backdrop, width min(460px, viewport less 32px). The head has a 32px icon tile (Muted, or Danger Soft for danger) and a 16px title. The body is Secondary Text, and the footer is a #fafafa bar with right-aligned Cancel and confirm. Dialogs open with a 200ms rise-and-scale. They are reserved for commitments: casting a ballot, opening or closing voting, and destructive deletes. Destructive dialogs focus Cancel by default.

### Toasts
Vercel-style, stacked at the bottom right with an 8px gap. Each is 360px wide with a canvas fill, Hairline border, 6px radius and Pop shadow, 14px text, and a 16px icon tinted by outcome. They slide up 8px over 250ms and dismiss after 3.5s (6s for errors).

### Loading and Empty
- **Skeletons:** shaped like the list that is loading. Each row has a 32px circle and two 12px/10px Muted bars of varying width, at 4px radius, pulsing to 55% opacity over 1.4s.
- **Spinner:** 14px, a 1.5px currentColor ring, 0.7s linear.
- **Empty states:** centred, a 40px hairline-bordered icon tile, a 16px title and one muted sentence.

### Summary Lists
Label/value grids inside a Box: Secondary Text label on the left, 500-weight tabular value right-aligned, 10px by 16px cells divided by hairlines. A disagreeing value turns amber.

### Reconcile Strip
A flush, three-column strip directly under the Integrity sweep Box header. Each cell has a 13px subtle label over a 20px/600 tabular figure, with hairline dividers between cells and below the strip. A count that disagrees with the majority turns Attention Amber, and a warning flash explains it. It stacks into rows under 560px. This is the system's answer to stat tiles.

### Round Bars
Instant-runoff rounds as rows of three columns: name (180px), bar, and count with a subtle percentage (104px). The text is 16px. The track is 20px Muted with 3px ends, and the fill is Tertiary Text. The winner's bar in the final round is Success Green. An eliminated candidate is struck through in Tertiary Text with a Strong Hairline bar. Widths animate over 400ms. Under 640px the name and count share a line above a full-width 12px bar.

### Progress Steppers
The voter flow uses a 13px stepper with 20px numbered circles: Ink fill for the active step, success-soft with a check for done, and 24px hairline connectors. The admin lifecycle (Nominations, Voting, Closed) uses the same dots with ink-filled done steps and a 3px Muted ring on the current one.

### Navigation
- **Top bar (public):** 56px, sticky, canvas with a bottom hairline. The wordmark (24px ink brand mark plus 16px/600 "PolyVote") sits on the left; a ghost "Check receipt" and a default "Admin" small button sit on the right.
- **Sidebar (admin):** #fafafa with a right hairline. Nav links are 32px with a 16px icon in 14px/500 Secondary Text; hover and active fill Muted with text colour. Groups are introduced by a 12px sentence-case Tertiary Text name. The account sits in the footer.
- **Breadcrumbs:** 13px Tertiary Text with chevrons above admin page titles.

### Browser Surfaces
`color-scheme` follows the active scheme, so native controls and scrollbars match. The scrollbar thumb is Strong Hairline on a transparent track. Selection is Accent Soft with text colour, the caret is Accent Blue, and native checkboxes and ranges use Ink as their accent. The favicon is a 32px Ink tile (8px corners) with a white ballot-box glyph, matching the 24px brand mark. Fonts are self-hosted Geist and Geist Mono variable via Fontsource.

### Motion
One curve, `cubic-bezier(0.16, 1, 0.3, 1)`, for everything that eases. Hover and colour changes take 150ms, dialog pop-in and drawer slides 200ms, toast entry 250ms, and bar and meter widths 400ms. Loops are reserved for the spinner and skeleton pulse. `prefers-reduced-motion` collapses all animation and transition durations to near zero.

## Do's and Don'ts

### Do:
- **Do** make the primary action an Ink button (#171717 light, #ededed dark) and keep at most one per view region.
- **Do** put collections in a Box of hairline rows with a #fafafa header, and put counts in that header as subtle text or in tab counters.
- **Do** show state as an 8px dot plus its word, or as a Primer Label, and pair every colour signal with text.
- **Do** report proof as a reconcile strip, summary list or flash with a bold verdict followed by the evidence.
- **Do** use 6px corners for containers and controls and 12px for dialogs only.
- **Do** use Geist Mono only for tokens, hashes, registration numbers and IDs, and tabular Geist for every count.
- **Do** keep shadows to floating surfaces (dialogs, toasts, drawer, bottom bar).
- **Do** keep 150ms transitions on the house ease-out, and honour reduced motion.

### Don't:
- **Don't** build stat tiles or KPI cards. Counts go in a flush reconcile strip, a summary list or a table column.
- **Don't** tint cards. Box bodies stay canvas white; soft state fills belong only to flashes, Labels and the Danger zone header.
- **Don't** use gradients anywhere: not on surfaces, buttons, bars or text.
- **Don't** put eyebrow labels or kickers above headings, and don't use uppercase or letter-spaced micro-labels. Context goes in a subtle line under the title.
- **Don't** nest a Box inside a Box. Split regions with hairlines flush to the edges.
- **Don't** add decorative halos, glows or coloured shadows. The only rings are the input focus ring and the current-step ring, and both report state.
- **Don't** fill a button with Accent Blue, and don't use blue to mean anything but link, focus, selection or information.
- **Don't** reach for a dialog unless the action commits a ballot, changes the lifecycle, or destroys data.
