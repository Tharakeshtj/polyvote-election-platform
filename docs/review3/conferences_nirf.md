# PolyVote: India-only venues hosted by NIRF top-100 institutions (checked 2026-10-23)

Paper: "PolyVote: Database-Enforced Integrity and a Keyed Audit Ledger for Small Ranked-Choice Elections". Machine-readable copy: `conferences_nirf.json`. Earlier broader list: `conferences_open.md`.

The two tests used: (a) the venue is in India (in-person or hybrid with an India venue); (b) the host or organiser is an institution with a row in the NIRF top 100 (Overall, Engineering or University list). "Open" means the official page I read shows a submission deadline on or after 23 Oct 2026. "Not verified" means exactly that. Anything labelled "claimed" is the organiser's own wording; I call indexing "confirmed" only where an IEEE conference record number is visible on the official page (and even then Xplore inclusion is conditional on IEEE's own checks).

## 1. Which NIRF edition

- **Edition used: NIRF India Rankings 2025** (the latest published). I fetched the three HTML tables from nirfindia.org on 2026-10-23: Overall, Engineering and University (100 rows each; the University list has 100 ranks).
- **A 2026 edition does not exist yet.** `https://www.nirfindia.org/Rankings/2026/OverallRanking.html` (and the Engineering and University equivalents) returned HTTP 404 while the 2025 URLs returned 200. A Careers360 article dated 6 Sep 2026 says data submission is finished and "the official release date is yet to be announced"; a later search (to 12 Sep) still showed it forthcoming. One aggregator page claims a "2026" list but its figures do not match NIRF's, so I ignored it. Re-check nirfindia.org before you commit; if 2026 is published the ranks below can change.
- An institution counts if it appears in Overall OR Engineering OR University. Ranks quoted below are 2025 ranks; "O" = Overall, "E" = Engineering, "U" = University.

Ranks of every host that came up:

| Host | O | E | U | Note |
|---|---|---|---|---|
| IISc Bengaluru | 2 | - | 1 | |
| BITS Pilani (incl. Goa campus) | 16 | 11 | 7 | one NIRF entry for the university |
| Amrita Vishwa Vidyapeetham | 17 | 23 | 8 | |
| VIT Vellore | 21 | 16 | 14 | |
| SRM IST | 22 | 14 | 11 | |
| KIIT Bhubaneswar | 27 | 36 | 17 | |
| Amity University (Gautam Budh Nagar) | 37 | 37 | 22 | NIRF row is "Amity University", city Gautam Budh Nagar; I matched it to Amity University Uttar Pradesh, Noida by city, not by a NIRF PDF |
| University of Delhi | 15 | - | 5 | parent of ICICC host college |
| Bharati Vidyapeeth (Pune) | - | - | 59 | parent of BVICAM, New Delhi |
| IIT (ISM) Dhanbad | 35 | 15 | - | |
| SSN College of Engineering | 82 | 47 | - | |
| MNNIT Allahabad (Motilal Nehru NIT) | - | 62 | - | |
| COEP Tech University, Pune | - | 90 | - | |
| ABV-IIITM Gwalior | - | 96 | - | |
| IIT Palakkad / IIIT Bangalore | - | 64 / 69 | - | NCC 2027 co-hosts |
| IIT Jammu | - | 56 | - | |

Not in any of the three top-100 lists: Kalyani Govt Engineering College, IEM Kolkata, Asansol Engineering College, R P Sarathy Institute of Technology, Sardar Patel Institute of Technology (Mumbai), JIIT Noida, KIET Ghaziabad, Techno India University, Vishwakarma University, IIT Goa, COMSNETS Association (a society, not an institution).

## 2. The twelve venues you named

| Venue | Official host | NIRF rank (2025) | Passes (b)? | Status |
|---|---|---|---|---|
| Confluence 2027 | Amity School of Engineering and Technology, Amity Univ. Uttar Pradesh, Noida | O 37 / E 37 / U 22 | Yes | Open, 4 Dec 2026 |
| INDIACom-2027 | BVICAM, a constituent of Bharati Vidyapeeth (Deemed to be University) | U 59 (parent only) | Borderline | Open, 7 Dec 2026 |
| IEM-ICDC 2027 | Institute of Engineering and Management, Kolkata | not ranked | No | Rejected |
| ICRCICN 2027 | **Kalyani Government Engineering College** (the official page does not say RCC Institute) | not ranked | No | Rejected |
| ICESICSC-2027 | KIIT Deemed to be University, School of Computer Engineering | O 27 / E 36 / U 17 | Yes | Open, 30 Oct 2026 (7 days) |
| i-PACT 2027 | VIT Vellore with Universiti Malaya | O 21 / E 16 / U 14 | Yes | Open, 31 May 2027 |
| ICICC-2027 | Shaheed Sukhdev College of Business Studies, University of Delhi (with Universal Innovators) | parent DU: O 15 / U 5 | Borderline | Open, 30 Oct 2026 (7 days) |
| iConCISE 2027 | Asansol Engineering College | not ranked | No | Rejected |
| ICCIDS 2027 | SSN College of Engineering, Kalavakkam, Chennai | O 82 / E 47 | Yes | Open, 18 Nov 2026 |
| IEEE PerCom 2027 | IEEE Computer Society event; local chairs at BITS Pilani K K Birla Goa Campus; general co-chair IIT Kharagpur | BITS O 16 / E 11 / U 7; IIT Kharagpur O 6 / E 5 | Yes, as local host | WiP track open, 17 Nov 2026 |
| ICPCSN 2027 | R P Sarathy Institute of Technology, Salem | not ranked | No | Rejected |
| IEEE CONECCT 2027 | IEEE Bangalore Section | n/a (not an institution) | No | Rejected; call not open until December (not re-verified) |

## 3. Qualifying open venues, cheapest first

Fee is the student-author fee in INR at the realistic registration date (after acceptance), non-member rate first, IEEE-member rate in brackets. "Tier B" = only the parent university is ranked. Venues with no published fee are listed last.

| # | Venue | Host and rank | City, dates | Deadline / decision | Student fee (INR) | Indexing | Fit |
|---|---|---|---|---|---|---|---|
| 1 | [SCES-2027](https://mnnit.ac.in/sces2027/) (Students' Conf. on Engineering and Systems) | MNNIT Allahabad, E 62 | Prayagraj, 12-14 Mar 2027 | 15 Nov 2026 (tentative) / 10 Jan 2027 | **5,900 incl. GST** | claimed (oral papers "sent to IEEE" for Xplore; poster papers proceedings only) | stretch |
| 2 | [IEEE COEP CON 2027](https://ieeecoepcon.coeptech.ac.in/) | COEP Tech University, E 90 | Pune, 4-6 Jun 2027 | 31 Mar 2027 / 15 Apr 2027 | 6,000 early (3,500) | claimed | stretch |
| 3 | [IEEE SANKALP 2027](https://sankalp.iiitm.ac.in/) | ABV-IIITM Gwalior, E 96 | Gwalior, 9-11 Apr 2027 | 30 Nov 2026 / 11 Jan 2027 | 7,000 (6,000) | **record #73342 shown**; Xplore and "Scopus" claimed | **good** |
| 4 | [ICSEAMS 2027](https://www.amrita.edu/?p=670200) | Amrita Vishwa Vidyapeetham, O 17 | Bengaluru, 17-19 Jun 2027 | 31 Jan 2027 / 15 Apr 2027 | 8,000 (6,000) | claimed | unlikely (energy topic) |
| 5 | [Confluence 2027](https://amity.edu/aset/confluence2027/) | Amity Univ., O 37 / E 37 / U 22 | Noida, 21-22 Jan 2027 | 4 Dec 2026 / 25 Dec 2026 | 8,000 + 18% GST = 9,440 (7,000 + GST = 8,260) | **record #71526 shown**; Xplore conditional | **good** |
| 6 | [INDIACom-2027](https://indiacom.org/home/call_for_paper) (tier B) | BVICAM / Bharati Vidyapeeth, U 59 | New Delhi, 7-9 Apr 2027 | 7 Dec 2026 / 8 Feb 2027 | 8,000 + GST = 9,440 (6,400 + GST = 7,552), early bird to 22 Feb 2027 | claimed (applied to IEEE Delhi Section; record 74162 appears in a link) | good |
| 7 | [ICESICSC-2027](https://esicconference.com/) | KIIT, O 27 / E 36 / U 17 | Bhubaneswar, 20-21 Feb 2027 | **30 Oct 2026** (firm) / 20 Jan 2027 | 9,000 (8,500) | claimed ("published by IEEE", no record number) | **good** |
| 8 | [i-PACT 2027](https://vit.ac.in/ipact) | VIT Vellore, O 21 / E 16 / U 14 | Vellore, 2-3 Sep 2027 | 31 May 2027 / 30 Jun 2027 | 12,000 (10,000) | claimed ("recommended to IEEE"; "Conference ID 73849") | stretch |
| 9 | [ICICC-2027](https://www.icicc-conf.com/) (tier B) | SSCBS, University of Delhi (DU O 15 / U 5) | Delhi, 5-6 Feb 2027 | **30 Oct 2026** / revised ms 30 Nov 2026 | 13,000 (12,000 early) | claimed (Springer LNNS "Approved") | stretch |
| - | [ICCIDS 2027](https://iccids.in/) | SSN College of Engineering, O 82 / E 47 | Chennai, 6-8 Jan 2027 | 18 Nov 2026 (extended) / TBA | **not published** ("yet to be updated") | claimed (IEEE application under review) | unlikely |
| - | [PerCom 2027 WiP](https://percom.org/call-for-wip-papers/) | local hosts BITS Pilani Goa, O 16 / E 11 / U 7 | Goa, 8-12 Mar 2027 | 17 Nov 2026 / 8 Jan 2027 | **not published** | claimed (WiP papers go into IEEE-published PerCom Workshops proceedings, "added to IEEE Xplore") | unlikely |
| - | [NCC 2027](https://ece.iisc.ac.in/~ncc2027/index.html) | IISc, O 2 / U 1 (IIT Palakkad E 64, IIIT Bangalore E 69) | Bengaluru, 17-20 Feb 2027 | **31 Oct 2026** (firm) / 24 Dec 2026 | **not published** | claimed ("will be indexed on IEEEXplore") | unlikely |

Best three for this paper: SANKALP 2027 (explicit security and distributed-database tracks, IEEE record number shown, cheap, deadline 30 Nov), Confluence 2027 (IEEE record number shown, deadline 4 Dec, cloud/security/blockchain scope) and ICESICSC-2027 (security track, but only 7 days left). INDIACom is cheap and relevant but its IEEE status is still "applied for" and its host is borderline.

## 4. Details and fee-waiver / reimbursement information per venue

None of the organisers publishes a student fee waiver, scholarship or reimbursement for registration. Where something exists it is listed here; "none published" means I read the registration/author pages and found nothing.

- **SCES-2027** (MNNIT Allahabad). First author must be a student. 6 pages, IEEE format. Fee INR 5,900 incl. 18% GST, bank-transfer instructions use a "2026-27" payment note, so the page is current. Past editions' proceedings are linked on IEEE Xplore from the site. Waiver: none published. Dates are marked tentative.
- **IEEE COEP CON 2027** (COEP Tech). Fee PDF (`IEEE-Registration_Fees.pdf`) gives Indian student INR 3,500 / 6,000 early (20 Apr-14 May 2027) and 5,000 / 6,000 regular (IEEE member / non-member); the PDF text is a flattened table, so the row labels were inferred from layout. GST not stated. Deadline caveat: the page shows full-paper deadline 31 Mar 2027 but also contradictory "submission opens" banners; a search snippet quoted 15 Dec 2026, which the page itself does not show. Waiver: none; plagiarism rejections "even after registration, without refund".
- **IEEE SANKALP 2027** (ABV-IIITM Gwalior). IEEE Record #73342 on every page. 6 pages plus up to 2 paid pages. Tracks include "Security and IoT" (cybersecurity, privacy-preserving computing, blockchain security) and "Distributed Computing, Cloud Computing and Big Data" (distributed databases). The registration form offers an in-person, virtual or to-be-decided presentation format. Papers not presented ("no-show") are not sent to Xplore. Waiver: none published. Note: another page on the same domain (a placeholder) says 2-4 Apr 2027; the live pages say 9-11 Apr.
- **ICSEAMS 2027** (Amrita, Bengaluru). Energy and mechatronics scope, listed only because the host passes. Waiver: none; only accommodation help.
- **Confluence 2027** (Amity). IEEE Conference Record #71526. 5-6 pages, extra pages INR 1,000 each up to 8. Registration is non-refundable "under any circumstances". Dual submission not allowed; AI plagiarism barred. Waiver: none. Fees exclude 18% GST.
- **INDIACom-2027** (BVICAM). 6 pages (+2 at INR 2,000 each). No publication fee. Discounts: 20% for co-authors and BVICAM alumni, 10% for five or more registrations from one organisation (General category only); only one discount at a time. Non-refundable even if you fail to attend. Student rate needs a bonafide certificate dated 31 Jan 2027.
- **ICESICSC-2027** (KIIT). Student INR 9,000 (non-member) / 8,500 (IEEE member); USD 300 foreign. 6 pages; no-show policy removes papers. The site menu lists payment, refund and publication policy pages but all three return 404, so refund terms are not published. Deadline 30 Oct is stated as firm.
- **i-PACT 2027** (VIT). 12,000 / 10,000; co-author INR 5,000; 10% off a second and 20% off a third paper. VIT students get no separate rate on this page. Paper-length rule not stated.
- **ICICC-2027** (SSCBS, DU). 10-page Springer LNNS format. "Fees are non-refundable." Organised with a private firm (Universal Innovators), which also runs a paid awards programme; the earlier research file already flagged it as lower confidence.
- **ICCIDS 2027** (SSNCE). Fee page empty; IEEE under review; deadline already extended from 15 Oct to 18 Nov.
- **PerCom 2027 WiP**. The Student Travel Award page says "Will be announced soon!" and the Travel Grants page "Will be updated soon", so there is a possible route to support but nothing usable yet; the home page names TCPP/TCCC and ACM India Council/SIGMOBILE as sponsors of student participation and travel grants (amounts and eligibility not published). WiP deadline 17 Nov 2026 AoE, 4 pages, single-blind; at least one author needs a full registration and must present in Goa.
- **NCC 2027**. 6 pages, double-blind, firm 31 Oct deadline; one full registration covers up to two accepted papers; fees not on the pages read.

## 5. Rejected, closed or not countable

| Venue | Host | Why dropped |
|---|---|---|
| IEEE ICRCICN 2027 | Kalyani Govt Engineering College | host not in NIRF top 100 (IEEE record #73691 shown, deadline 30 Nov 2026, but irrelevant) |
| IEM-ICDC 2027 | IEM Kolkata | host not in NIRF top 100 |
| iConCISE 2027 | Asansol Engineering College | host not in NIRF top 100 (IEEE record #73082) |
| ICPCSN 2027 | R P Sarathy Institute of Technology | host not in NIRF top 100 |
| IEEE CONECCT 2027 | IEEE Bangalore Section | organiser is an IEEE section; call not open until December |
| ICSC 2027 | JIIT Noida | host not in NIRF top 100 (IEEE record 71980) |
| ISEC 2027 | Sardar Patel Institute of Technology, Mumbai | host not in NIRF top 100; round 2 closed 25 Sep 2026 |
| ICCISS-2027 | KIET Ghaziabad | host not in NIRF top 100 |
| ICMDRSE-2027 | Vishwakarma University, Pune | host not in NIRF top 100 |
| ICCECE 2027 | Techno India University, Kolkata | host not in NIRF top 100 |
| COMSNETS 2027 (5-9 Jan 2027, has Undergraduate Forum and Poster Session) | COMSNETS Association | organiser is a society; the forum, registration and travel-grant pages are JavaScript-rendered and could not be read, so deadlines and fees are not verified |
| IATMSI-2027 | ABV-IIITM Gwalior | venue reported as Kathmandu, Nepal (20-22 May 2027) per a search summary of the CFP PDF; the PDF could not be read; fails the India test |
| RAIT 2027 | IIT (ISM) Dhanbad (O 35 / E 15) | host passes but papers closed (extended to 19 Oct 2026, 550+ submissions); only a Doctoral Consortium call is open to 2 Nov |
| ICDCIT 2027 | KIIT | host passes but closed (full paper 28 Aug, camera-ready 23 Oct 2026); student-symposium deadlines not readable (site returned 403) |
| IEEE DELCON 2026 | BITS Pilani | host passes but closed (31 Jul 2026 deadline) |
| ISEA-ISAP 2026-27 | IIT Jammu (E 56) | host passes but closed (30 Jul 2026), conference 17-19 Dec 2026 |
| ICRTAC 2026 | VIT Chennai | host passes but closed 15 Aug 2026 (earlier file) |
| ACM COMPUTE 2026 | Amrita, Coimbatore | host passes but closed 26 Jul 2026; computing-education topic |
| IEEE ICIDeA 2026 | KIIT | conference is 29-31 Oct 2026, so the window is closed |

Searches for 2027 calls hosted by other top-100 institutions (IIT Bombay, Delhi, Kanpur, Kharagpur, Roorkee, Hyderabad, Guwahati, Indore; NIT Trichy, Rourkela, Calicut, Surathkal, Warangal; IIIT Hyderabad, Delhi, Allahabad; BITS; Thapar; DTU; NSUT; Jadavpur; Anna University; JMI; AMU; SASTRA; SRM; Manipal; Saveetha; Sathyabama; Vel Tech; Kalasalingam; KLU; UPES; Graphic Era; Chandigarh Univ.; LPU; PSG; Shiv Nadar; Symbiosis; VIT Chennai and Vellore other than i-PACT) returned no further open 2027 call with a readable official page. That is a limit of the search tool (US-only, snippet-style results), not proof none exists; the IEEE conference calendar and each institution's events page would find more.

## 6. Does VIT reimburse undergraduates' conference fees?

**Official, public (found):** VIT's *Research Promotion Policy* ("Approved in the 56th Meeting of the Board of Management held on 04.04.2019"), published by the Office of Academic Research.
- Section 3(g) "Financial support for research paper presentation in national/international conferences/seminars/workshops" is **for faculty members only**: up to INR 20,000 a year for conferences in India and INR 50,000 a year abroad, claimable once in two years, only if the faculty member is presenter/first author/invited speaker and no other agency paid.
- The only student-facing schemes are the **Raman Research Award** (incentive for *research scholars* publishing in reputed journals, first author with the supervisor as corresponding author) and enhanced TRA fellowships. Neither covers conference registration fees, and neither mentions undergraduates.
- Sources: https://vit.ac.in/files/ebooks/Research-Promotion-Policy/files/basic-html/page12.html (section g), https://vit.ac.in/files/ebooks/Research-Promotion-Policy/files/basic-html/page5.html (student schemes), and a PDF copy at https://chennai.vit.ac.in/files/VIT-Research%20Promotion%20Policy.pdf (scanned, no text layer).
- Caveat: it is a 2019 document; a newer version, or an unpublished student scheme, may exist.

**Official, public (not a reimbursement):** VIT-hosted conference pages (NEleX-2026 at https://vit.ac.in/NEleX-2026/registration.html and i-PACT 2027) list normal student fees with no concession, no waiver and no refund clause. A search summary of the ic-ETITE'24 registration page says it had a separate "VIT (internal)" rate of INR 5,000; I could not open that page (HTTP 502), so treat it as not verified.

**Hearsay / forum:** none found. I searched for student-forum or Quora/Reddit answers on VIT paying conference or publication fees and found none, so I cannot report any.

**Not found at all:** no public VIT circular, policy or office page that reimburses *undergraduate* students' conference registration or publication fees. I will not claim such a policy exists.

**Who would know (suggestion only):** your School's Dean or Programme Chair (SCORE for CS), the Office of Academic Research (which owns the policy above), and the Directorate of Student Welfare / Student Affairs; the head of your project guide's department can also say whether the school pays out of its own budget. A comparable external scheme to ask about is the AICTE-INAE Travel Grant (for presenting at international events; it appeared in search results but I did not check whether it covers domestic conferences or this year's call).

## 7. Caveats

- Ranks are NIRF 2025; a 2026 release would supersede them.
- Fees exclude GST except where marked; card or bank charges are not included. Check each page again before paying. Fees are non-refundable at most of these venues.
- Deadlines can be extended (ICCIDS, NCC and RAIT already were). ICESICSC says its 30 Oct deadline is firm.
- "Confirmed" here means only a visible IEEE record number (Confluence #71526, SANKALP #73342); I did not cross-check them on the IEEE site, and none of the venues guarantees Xplore inclusion. Everything else is a claim.
- For VIT credit, verify with your school which indexing they require before choosing among the "claimed" venues.

## 8. Sources read

NIRF 2025 tables: https://www.nirfindia.org/Rankings/2025/OverallRanking.html, https://www.nirfindia.org/Rankings/2025/EngineeringRanking.html, https://www.nirfindia.org/Rankings/2025/UniversityRanking.html. NIRF 2026 status: https://news.careers360.com/nirf-2026-ranking-date-top-colleges-india-iit-madras-hindu-college-2025-toppers-moe-nirfindia-org-iisc-aiims (6 Sep 2026).

Venue pages: https://amity.edu/aset/confluence2027/ (and /Registration.aspx, /call-for-paper.aspx, /Submission.aspx); https://indiacom.org/home/call_for_paper (/registration_fee_details, /important_dates, /IEEE_oversight_committee); https://www.iemicdc.org/; https://icrcicn.in/; https://esicconference.com/ (/important-dates, /registration, /call-for-papers); https://vit.ac.in/ipact (/registration.html); https://www.icicc-conf.com/ (site bundle read); https://www.iconcise.in/; https://iccids.in/; https://percom.org/ (/call-for-wip-papers/, /organizing-committee/, /student-travel-award/, /travel-grants/, /registration/); https://icpcsn.com/2027/; https://mnnit.ac.in/sces2027/ (registration, guidelines, brochure PDF); https://ieeecoepcon.coeptech.ac.in/ (author guideline, fee PDF); https://sankalp.iiitm.ac.in/ (/submission, /register); https://www.amrita.edu/?p=670200; https://ece.iisc.ac.in/~ncc2027/cfp.html and /submission.html; https://people.iitism.ac.in/~rait/; https://icdcit.kiit.ac.in/23rd-icdcit-2027/; https://conf.researchr.org/home/isec-2027; https://www.comsnets.org/ (home only).

Search summaries only (official page not opened): DELCON 2026 (https://www.bits-pilani.ac.in/delcon2026/important-dates/), ISEA-ISAP 2026-27 (https://iitjammu.ac.in/isea-isap2026/), IATMSI-2027 (https://iatmsi.iiitm.ac.in/), ACM COMPUTE 2026 (https://isigcse.acm.org/compute/2026/), ICIDeA 2026.

VIT: https://vit.ac.in/files/ebooks/Research-Promotion-Policy/files/basic-html/page4.html through page12.html; https://vit.ac.in/NEleX-2026/registration.html.
