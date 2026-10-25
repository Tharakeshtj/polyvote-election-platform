# PolyVote: more NIRF-hosted India venues, batch B (NITs, state/central universities, others) - checked 2026-10-25

Paper: "PolyVote: Database-Enforced Integrity and a Keyed Audit Ledger for Small Ranked-Choice Elections". Machine-readable copy: `conferences_nirf_more_B.json`. Earlier file (do not repeat): `conferences_nirf.md`.

## 0. Honest limits

- The search tool is US-only and snippet-based, and its budget ran out partway (the shared 200-search limit), so about 60 searches plus about 90 page fetches were done. Many institute sites are JavaScript apps or return 403/404/certificate errors; for those I read the JS bundle with curl or fell back to snippets, and I say so per venue.
- "Not found" means "not found by these tools", not "does not exist". The IEEE vTools event search and the IEEE conference calendar are JavaScript or ignore queries, so I could not sweep them. Aggregators used: EasyChair "CFPs in India" (80 rows), conferencealerts.com India listing (100 rows, first page read), myhuiban.
- Fees are quoted exactly as the official page states; GST status is noted where the page says it.

## 1. NIRF edition and ranks used

NIRF India Rankings 2025, fetched from nirfindia.org on 2026-10-25 (Overall, Engineering, University tables, 100 rows each; same edition as the earlier file). A 2026 list was still unpublished in the earlier note; I did not re-check. "O/E/U" = Overall / Engineering / University rank.

NITs in the lists (all Engineering unless stated): Tiruchirappalli E9 (O30); Rourkela E13 (O34); Karnataka Surathkal E17 (O54); Calicut E21 (O45); Warangal E28 (O63); Durgapur E49; Silchar E50 (O97); Patna E53; Jalandhar E55; Delhi E65; Srinagar E73; Jamshedpur E82; Meghalaya E83; Kurukshetra E85; Raipur E86; Hamirpur E97; Puducherry E99; MNIT Jaipur E42 (O77); VNIT Nagpur E44 (O86); SVNIT Surat E66; MANIT Bhopal E81; MNNIT Allahabad E62 (already found).
NOT in any top-100 list: NIT Goa, Agartala, Arunachal, Manipur, Mizoram, Nagaland, Sikkim, Andhra Pradesh, Uttarakhand (so NIT Uttarakhand's IICPE-2026, i-TRANS 2027, ICoIED-2027 do not count), Coimbatore Institute of Technology, Thiagarajan College of Engineering, Punjab Engineering College, VJTI Mumbai, UIET (Panjab University itself is E93 / U35), Kalyani GEC, JNTU Anantapur (the NIRF "JNTU" row E94 is Hyderabad; so ICCETT-2027 at JNTUA does not count), DES Pune University (PuneCon 2026 host).
Universities and others in the lists: Anna University E20/O29/U20; Jadavpur E18/O18/U9; University of Delhi O15/U5; JNU O9/U2; Jamia Millia Islamia E24/O13/U4; AMU E34/O19/U10; BHU O10/U6; SPPU O91/U56; University of Hyderabad E74/O26/U18; Osmania O53/U30; DTU E30/O62/U42; NSUT E70; PSG Tech E68; M S Ramaiah Institute of Technology E75; AU College of Engineering E88; COEP E90 (found); BIT Mesra E51; IIEST Shibpur E54; ICT Mumbai E41/O65/U40; Thapar E29/O44/U27; Panjab University E93/O57/U35; JNTU Hyderabad E94.

## 2. NEW venues with an open call (deadline on or after 25 Oct 2026), India, host passes the NIRF test

Sorted by deadline. "Fit" is for PolyVote (databases, security, privacy, e-voting, software systems).

| # | Venue | Host and NIRF | City, dates | Deadline / decision | Length | Student fee (INR) | IEEE or Springer claim, exactly as stated | Record no.? | Fit |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [E2A'27](https://e2a.nits.ac.in/) Int'l Conf. on Emerging Electronics and Automation (6th) | NIT Silchar, E50 / O97 | Silchar, 20-22 Jan 2027, in person | **26 Oct 2026, 11:59 PM IST** (extended; page also shows 5 Oct) / notification 25 Nov 2026; camera-ready 31 Dec 2026 | not stated | not stated (early bird to 15 Nov 2026) | Springer "Publication Partner", Lecture Notes in Electrical Engineering, "(Approval pending )". No IEEE claim | n/a | unlikely (electronics; has an "AI and Soft Computing" track) |
| 2 | [ICPC2T 2027](https://icpc2t.nitrr.ac.in/) Int'l Conf. on Power, Control and Computing Technologies | NIT Raipur (Dept. of EE), E86 | Raipur, 3-5 Mar 2027, hybrid | **31 Oct 2026** / notification 15 Nov 2026; camera-ready 15 Dec 2026 (submission page also says 15 Jan 2027); registration 15 Jan 2027 | max 6 pages IEEE double column; 2 extra pages at extra charge, absolute max 8 | Student/research scholar 8,000 (IEEE member) / **9,000 (non-member)**, "All fees include 18% GST" (page also says "Registration details will be updated soon") | "IEEE Sponsored - proceedings in IEEE Xplore (Scopus indexed)"; "Proceedings submitted for indexing in IEEE Xplore"; at least one author must register and present for Xplore | not visible | unlikely (15 power-system tracks; only T6 "Smart Grids, Data Analytics and Cyber Security" and T13 "AI, ML and Digital Twins" touch computing) |
| 3 | [ICBEST 2027](https://icbest2027.nitrr.ac.in/) Biomedical Eng. Science and Technology (4th) | NIT Raipur (Biomedical Eng.), E86 | Raipur, 15-16 Apr 2027 ("likely to be extended") | **30 Oct 2026** / notification 15 Dec 2026; camera-ready 30 Dec 2026 | not stated | not stated | No IEEE claim; Springer paper template, no explicit indexing claim | none | unlikely (biomedical computing) |
| 4 | [ICSSD 2027 / ICS2Dev2027](https://icssd.nitt.edu) SPARC-sponsored Int'l Conf. on Secure Software Development | NIT Tiruchirappalli (Dept. of Computer Applications), E9 / O30 | Tiruchirappalli, 4-6 Feb 2027 | **10 Nov 2026** (home page and brochure) / acceptance 15 Dec 2026 (brochure also lists 20-30 Dec); camera-ready and registration 1 Jan 2027; slides/posters 1 Feb 2027 | 10-12 pages, Springer single-column (camera-ready: full 12-15+, max 18; short 8-11); double-blind; <10% similarity | Indian **student presenter 7,500 early bird (23 Jul-31 Dec 2026) / 10,000 regular (1 Jan-2 Feb 2027)**; student participant 5,000 / 6,000; foreign student presenter USD 175 / 222; GST not mentioned | No IEEE. "Springer is the named proceedings publisher"; page says papers "will be sent to IET Digital Library, EI Compendex, and Scopus", series "currently indexed in Scopus, DBLP, INSPEC, SCImago", indexing "outside the organizers' and publisher's control" | n/a | **good on topic** (tracks: Secure Engineering - privacy, cybersecurity, application security; Information Architecture - data science, "next-generation databases"; also AI/LLM). Format mismatch: Springer 10-12 pages, not IEEE 5-8 |
| 5 | [ICSETIC-2027](https://icsetic.nitrr.ac.in/) IEEE Int'l Conf. on Intelligent Computing for Sustainable Energy Technologies and Industrial Control | NIT Raipur, E86 (IEEE MP Section people on committee) | Raipur, 23-25 Jun 2027, hybrid | **30 Jan 2027** (CMT opens 28 Sep 2026) / notification 28 Feb 2027; camera-ready 15 Apr 2027; registration 30 Apr 2027 (a second banner says 5 Jan 2027) | "IEEE format only - maximum 6 pages" | Student/research scholar 8,000 (IEEE member) / 9,000 (non-member); "GST applicable as per Govt. directives" | "Accepted and presented papers will be submitted for inclusion in the IEEE Xplore Digital Library, subject to meeting IEEE Xplore" scope and quality requirements | not visible | unlikely (power systems, drives, control; "Computational Technologies" is a generic mention) |

Sources behind row 2 and 5 fee/date text: the sites are React apps that return an empty shell; I read the text from the sites' compiled JS bundles (https://icpc2t.nitrr.ac.in/assets/ and https://icsetic.nitrr.ac.in/assets/ files). This is the page's own content but could differ from what a browser renders if a later build changes it. Search snippets (not my own reading) agree with the dates.

Open but off-topic (listed so you do not rediscover them): ICRAMIE 2027, NIT Warangal, manufacturing, full paper 30 Oct 2026 (https://nitw.ac.in/api/static/files/ICRAMIE_2027_2026-7-29-10-39-45.pdf, snippet only); MatTECH 2027, NIT Raipur, materials, dates unclear; ICSEMT 2027, NIT Jalandhar, 28-30 May 2027, abstract 5 Mar and full paper 10 Apr 2027, IOP J. Phys. Conf. Series (https://v1.nitj.ac.in/icsemt_2027/, snippet); ISCESTI-2027, NIT Patna, civil, 27-29 May 2027 (https://iscesti.nitp.ac.in/, snippet); ICES 2027, NIT Calicut, civil/environment, Feb 2027, no deadline shown.

Fee waivers or reimbursement: none published at any of the venues above (ICSSD page: waivers "not mentioned"; ICPC2T and ICSETIC: none). ICSSD runs a PhD Symposium and poster presentations, but those pages are placeholders with no deadlines.

Best of this batch for PolyVote: **ICSSD 2027 (NIT Trichy)**, because the topic match is direct (secure software, privacy, databases) and the deadline is 10 Nov 2026, but it is a Springer 10-12 page venue, not IEEE, and its indexing wording is "will be sent". Nothing in this batch is both IEEE-backed and on-topic.

## 3. Checked and closed, or conditional (do not use)

| Venue | Host / NIRF | Why not |
|---|---|---|
| ICDCN 2027, 4-7 Jan 2027 (https://cs3-lab.github.io/icdcn/) | NITK Surathkal, E17 / O54 | main paper 13 Aug 2026 (firm), PhD forum, posters, tutorials 15 Oct, demos extended to 21 Oct 2026; all passed. ACM in-cooperation, not IEEE |
| CVIP 2026, 9-12 Dec 2026 (https://cvip2026.nitc.ac.in) | NIT Calicut, E21 / O45 | round 2 deadline 16 Aug 2026, notification 5 Oct; Springer LNCS/CCIS, IAPR; no IEEE |
| OCIT 2026, 17-19 Dec 2026 (https://oits-ocit.github.io/) | NIT Kurukshetra, E85 | hard deadline 31 Aug 2026 passed; IEEE record #73091 appears in a CFP post; IEEE Delhi Section technical co-sponsor |
| IEEE GSCon 2027, 9-11 Jan 2027 (https://ieeegscon.org/) | SVNIT Surat, E66 | review papers 15 Aug 2026; notification to 22 Oct; early bird 15 Nov; IEEE Conference Record #71435 shown; registration only |
| ICoAC 2026, 17-19 Dec 2026 (https://icoac.mitindia.edu/) | Anna University MIT Campus, E20 / O29 | submission 16 Oct 2026 passed (no extension shown); IEEE technical co-sponsorship "Pending Approval" per brochure snippet |
| SoCTA 2026, 4-5 Dec 2026 (https://socta.in/) | SVNIT Surat (CSE), E66 | extended deadline 15 Oct 2026 "firm"; Springer LNNS "To be Approved" |
| ICDEC-2026, 26-28 Nov 2026 | SVNIT Surat with a trust | round 2 deadline 30 Sep 2026 |
| ICEFEET-2026, 21-22 Nov 2026 | NIT Patna (EE), E53 | submission closed 15 Feb 2026; electrical |
| EPREC 2027, 19 Feb 2027 | NIT Jamshedpur, E82 | 15 Jul 2026 deadline passed (aggregator snippet only); power |
| MNDCS 2027 | NIT Silchar | extended to 15 Oct 2026 (snippet); micro/nano-electronics |
| ICISNC-2026 | NIT Meghalaya (CSE), E83 | held Jul 2026; no 2027 edition found |
| IC2SDT 2024, 2025 | NIT Delhi (CSE), E65 | editions in Aug 2024 and 4-6 Dec 2025 (IEEE-published); no 2026/27 call found, site returned 502 |
| ICSPCRE-2026, 4-6 Dec 2026 (IEEE) | NIT Rourkela (EE), E13 | power/renewables; deadline not read |
| ICPCES-2026, AIMLAC-2027 (11-13 Feb 2027, AI/ML methods in advanced computing, Mathematics dept.) | MNNIT Allahabad, E62 | listed on MNNIT's events page; no deadline listed, official URL not found (404 on guesses); not verified |
| CALDAM 2027, 11-13 Feb 2027 | LNMIIT Jaipur | not in NIRF top 100; deadline 21 Sep 2026 in any case |
| AIM-CON 2026, 31 Oct-1 Nov 2026 | Jamia Millia Islamia (CSE), E24 | event is before the window; publisher not read |
| BIT Mesra ICCoSD 2026, 17-18 Dec 2026 (BIT Mesra, E51) | BIT Mesra | listed on the events page with no deadline, fee or IEEE detail; ICCoSD-25 used 4-6 page IEEE format via CMT; 2026 call not found: not verified |
| ICAIRSC-2026 "Tiruchirappalli" | none | EasyChair listing by ScienceTechXplore (Netherlands address), virtual; not NIT Trichy |
| 2026 Indian Conf. on Adv. in Electrical, Computers and Communications, Trichy, 18-20 Dec 2026 | MAM College of Engineering | not NIRF top 100; abstract deadline 30 Oct 2026 |
| ICACECT-27 (Lucknow), IEEE-IC4 (Indore), ICCECE 2027, ACET-2027 and similar | Integral Univ., Medicaps, Techno India, AKGEC | hosts not in NIRF top 100 |
| IEEE INDICON 2026, 18-20 Dec 2026 | Sri Sai Ram Engg College, Chennai | host not ranked; deadline 31 Aug 2026 passed |
| IEEE PuneCon 2026, 17-19 Dec 2026 | DES Pune University | host not in lists; deadline 15 Aug 2026 passed (invitation email only) |
| ICCETT-2027, 27-28 Feb 2027, deadline 16 Nov 2026 (https://iccett.jntua.ac.in/) | JNTU Anantapur | NIRF "JNTU" row is Hyderabad, so not counted |
| IEEE CALCON 2026, SPICES 2026, ICMACC 2026, DELCON 2026 | IEEE Sections or ranked/unranked colleges | sections are not institutions, or events are in 2026 with passed deadlines |
| ICCCNT 2027 | unknown | 2027 host not announced in anything I read (2025 IIT Indore, 2026 listed at IIT Delhi) |

## 4. Institutions where nothing open and relevant was found (one line each)

- NIT Rourkela: only power/materials/bio conferences (ICSPCRE, IBEC, FMFP, ICPCM); no CS call. 
- NIT Karnataka Surathkal: ICDCN 2027 only, all tracks closed.
- NIT Warangal: ICRAMIE 2027 (manufacturing), SWAT (hydrology); no CS/IEEE call found; site had a certificate error.
- NIT Calicut: CVIP 2026 closed; ICES 2027 is civil/environment.
- NIT Durgapur: no 2027 call found; site not reachable (DNS/connection errors).
- NIT Kurukshetra: OCIT 2026 closed; ICGEST-2026 and SPACE 2027 (civil) have no deadline text.
- MNIT Jaipur: events page lists materials/chemistry conferences only; IEEE iSES 2025 was earlier, no 2026/27 iSES call found.
- VNIT Nagpur: PCEMS 2026 (30-31 Oct 2026, ECE) already running; nothing for 2027; IEEE SeFET 2026 past.
- NIT Jalandhar: ICSEMT 2027 is IOP-published energy; home page lists no CS call.
- NIT Hamirpur: ChEmference-2026 only; ICGESI 2026 past.
- NIT Patna: ICEFEET closed; ISCESTI-2027 civil.
- NIT Delhi: no 2026/27 IC2SDT call found.
- NIT Srinagar: STEPS-2026 (23 Oct 2026, energy) and ICCBT 2026 only.
- NIT Jamshedpur: EPREC 2027 closed; home page returned only a title.
- NIT Meghalaya, NIT Puducherry (IConSCEPT series: 2023 and 2024 editions found, no 2026/27 call; site returned only a title): nothing open.
- MANIT Bhopal: site certificate error; searches found only ICAMT-2025.
- NIT Raipur: three IEEE/other calls found (rows 2, 3, 5 above); all off-topic. Also a one-week online STTP on cryptography and cloud security, 4-9 Jan 2027, deadline 20 Dec 2026 (not a paper conference).
- NIT Silchar: E2A'27 (row 1); AICTA 2026 was 2-3 Oct 2026.
- Anna University: ICoAC 2026 closed; nothing for 2027.
- Jadavpur University: no Jadavpur-hosted call found; site unreachable.
- University of Delhi: only the already-found ICICC; commerce and law conferences otherwise.
- Jawaharlal Nehru University: NetCrypt 2026 (8-10 Oct 2026) past; nothing for 2027.
- Jamia Millia Islamia: AIM-CON 2026 (before the window), plus mechanical and education conferences.
- Aligarh Muslim University, BHU, Savitribai Phule Pune University, Osmania University, University of Hyderabad, Panjab University, JNTU Hyderabad, AU College of Engineering: no 2027 call found; University of Hyderabad events list was empty.
- DTU, NSUT, PSG Tech, Thapar, M S Ramaiah (I4C-2026 was Sep 2026, closed), BIT Mesra (ICCoSD 2026 not verified), IIEST Shibpur (ICEPE-2026 energy, 21-23 Dec 2026; AIIoT 2025 past), ICT Mumbai, VJTI, Thapar: nothing open and relevant.

## 5. Sources actually read

NIRF 2025 tables: https://www.nirfindia.org/Rankings/2025/EngineeringRanking.html (and OverallRanking, UniversityRanking). Venue pages: https://icssd.nitt.edu (home, paper submission, registration, contact, brochure PDF read with pdftotext); https://icpc2t.nitrr.ac.in/ and https://icsetic.nitrr.ac.in/ (JS bundles); https://icaihc.nitrr.ac.in/; https://icbest2027.nitrr.ac.in/; https://nitrr.ac.in/conference.php; https://e2a.nits.ac.in/; https://oits-ocit.github.io/; https://cs3-lab.github.io/icdcn/; https://cvip2026.nitc.ac.in; https://icoac.mitindia.edu/; https://ieeegscon.org/; https://vtsociety.org/event/conference/ieee-gujarat-section-conference-2027; https://socta.in/; https://sites.nitm.ac.in/icisnc/; https://events.vtools.ieee.org/event/538815/ical; https://sciencetechxplore.org/conference/ICAIRSC-2026.php. Institute event pages: nitt.edu, nitrkl.ac.in, nitkkr.ac.in, nitc.ac.in, nits.ac.in, svnit.ac.in (+ /web/Events.php), vnit.ac.in (+ /category/events/), mnit.ac.in, mnnit.ac.in (events page), nith.ac.in, nitsri.ac.in, nitdelhi.ac.in, nitj.ac.in, nitp.ac.in, nitk.ac.in, dtu.ac.in, annauniv.edu, psgtech.edu, thapar.edu, jmi.ac.in, uohyd.ac.in. Aggregators: https://easychair.org/cfp/country?cc=in, https://conferencealerts.com/country-listing?country=India, https://www.myhuiban.com/.

Snippet-only (official page not opened by me): ICRAMIE 2027, ICSEMT 2027, ISCESTI-2027, EPREC 2027, MNDCS 2027, ICCETT-2027, PuneCon 2026, INDICON 2026, CALDAM 2027.
