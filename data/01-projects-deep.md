# Defending the four projects on your SWE resume

Written for **eTech Global Services** (Gandhinagar) — but the depth trees are company-agnostic,
so reuse this file for every interview where this resume goes out.

## Why this file exists

Your ValorX post-mortem showed one clean pattern: **every miss was one level deeper than the
headline question.** You knew normalization, not BCNF. Knew 2nd-highest salary, not Nth. Knew
closures, not hoisting. Knew the four pillars, not compile-time vs runtime dispatch.

So this is not a summary of your projects. It is a **depth tree** — headline question, then the
follow-up, then the follow-up's follow-up. The L2 answers are the point.

**One habit fixes the whole pattern:** after every answer, add one sentence going a level deeper
*before* they ask. Not "exponential backoff doubles the delay" — "exponential backoff doubles the
delay, and the thing it's still missing is jitter." You get credit for the depth *and* you steer
the follow-up onto ground you've prepared.

---

## eTech-specific framing — read first

eTech is a ~4,000-person BPO/contact-centre company (HQ Nacogdoches TX; India sites Gandhinagar
and Vadodara) with an in-house software arm, **ETS Labs** (~250 engineers) building QEval,
Speech AI, Real-Time Agent Assist and RPA/Document AI.

Their full-stack roles come in two shapes:

| Variant | Your fit |
|---|---|
| .NET / C# / ASP.NET + React or Angular | ✗ no C# anywhere on your resume |
| **Node.js + Angular + MySQL / MongoDB / MSSQL + AWS/Azure/GCP** | ✓ this is your lane |

**So reorder how you lead:**

1. **Angular Admin** — normally your weakest project, but Angular is the one skill named in
   *both* their variants. Lead with it more than you would elsewhere, while staying precise
   about the size of your contribution.
2. **QuickCourt** — closest to their actual work: full-stack web, relational DB, auth, roles.
3. **Mocha Leads** — your depth showcase. React, but the auth/multi-tenant story travels.
4. **SFSync** — Python isn't in their JD, *but* ETS Labs does RPA and document automation, and
   SFSync is literally a bulk data pipeline with retry semantics. Frame it as **automation**,
   not as "a Python project."

Expect **SQL to be weighted heavily** — MySQL and MSSQL are both named. That's also where you
lost points last time (Nth-highest salary). Drill it.

---

# 1. SFSync — the one you fumbled

`g:\Internship\sfsync` · Python, FastAPI, Pydantic, pandas, httpx, SQLite · 489 lines

Your Python centrepiece and the project most aligned with where you want your career to go.
Know it cold.

## The 60-second pitch

> "SFSync models the bulk-import problem. You upload a CSV or Excel file; every row is validated
> against a Pydantic schema; valid rows get chunked into batches and pushed to a downstream API;
> and the rows that fail come back as a per-row error report keyed to the spreadsheet line number.
>
> The design goal was that **one bad row must never sink the job** — a 5,000-row upload with three
> bad emails should import 4,997 and tell you about the three. So validation collects errors and
> carries on instead of raising on the first one.
>
> On top of that, the two things bulk imports always hit: per-record API calls don't scale, so
> rows are batched; and bulk writes get rate-limited, so a 429 is retried with exponential backoff
> instead of being hammered or dropped."

## Data flow — draw this on paper

```
POST /jobs (file, target_url, batch_size)
   |
   +- parse_upload()    pandas -> DataFrame   (.csv/.xlsx/.xls, else 400)
   +- column check      missing required cols -> 400
   +- validate_rows()   per row -> ContactRow  -+- ok   -> valid[]  (dicts)
   |                                            +- fail -> errors[] (row_number, field, msg)
   +- push_all()        chunk(valid, 200) -> each batch, sequentially:
   |                      post_batch_with_retry()
   |                        |- 2xx                     -> ok, return attempts
   |                        |- 429/5xx or RequestError -> sleep(backoff) -> retry (max 4)
   |                        +- other 4xx               -> fail immediately
   +- store.save_job()  SQLite: jobs + row_errors
   +- return JobSummary
```

## Depth tree

### "Why batch at all?"

**L0** — 5,000 rows posted one at a time is 5,000 round trips, and most bulk APIs meter you per
request against a rate limit. Chunking at 200 turns that into 25 requests.

**L1 · "Why 200?"** — It's a default parameter, overridable per job via a form field. Trade-off:
a bigger batch means fewer requests but a single failure loses more work and the payload grows.
200 is a common bulk-API page size — a sensible default rather than a measured one.

**L1 · "What if the batch is too large for the server?"** — You'd get a 413. In my code that's a
non-retryable 4xx, so it fails fast instead of looping. Better behaviour would be to split the
batch in half and retry — I don't do that.

### "Explain your backoff." ⭐ most likely drill

**L0** — `backoff_delay(attempt) = min(0.5 * 2**(attempt-1), 8.0)` → 0.5s, 1s, 2s, 4s, capped at
8. Maximum 4 attempts.

**L1 · "Why exponential rather than a fixed delay?"** — Retrying immediately adds load to a server
already refusing load. Doubling gives the rate window time to reset.

**L1 · "Why cap it?"** — Without a cap the delay doubles forever and a long retry chain stalls the
request indefinitely. There's a test asserting `backoff_delay(10) == 8.0`.

**L2 · "What's the problem if every client uses the same backoff schedule?"** ← *this is the level
that broke you last time* — **Thundering herd.** If many clients fail at the same moment and all
back off on the identical schedule, they retry in sync and re-spike the server. The fix is
**jitter** — randomise the delay within a window. **My code has no jitter. That's a real gap and
it's the first thing I'd add.**

**L2 · "What about the `Retry-After` header?"** — When a server returns 429 it often tells you
exactly how long to wait, which beats guessing. There's a comment in my code saying to honour it,
**but the code doesn't actually read it yet.** Be the one who points that out.

### "Which failures do you retry, and which do you not?"

**L0** — `RETRYABLE_STATUS = {429, 500, 502, 503, 504}`, plus any `httpx.RequestError` (connection
reset, DNS failure, timeout). Everything else fails immediately.

**L1 · "Why not retry a 400 or 422?"** — Those mean the payload itself is wrong. Sending identical
bytes again fails identically — pure wasted load.

**L2 · "Is retrying a POST actually safe?"** ⭐ — **No. POST isn't idempotent.** If the server
accepted the batch but the response was lost on the way back, my retry writes those rows twice.
That is exactly why **idempotency keys** are the first item on my "what I'd add next" list — a
stable key per batch so the server can recognise and discard the duplicate.

### "Why are the batches sequential?"

**L0** — Deliberate. Firing them all concurrently is the fastest possible way to trigger the rate
limit the retry logic exists to respect.

**L1 · "So how would you speed it up safely?"** — Bounded concurrency: an `asyncio.Semaphore`
capping in-flight batches at 3–5 rather than unbounded. Better still, adaptive — raise concurrency
while responses are clean, drop it on a 429.

### "Why async?"

**L0** — The work is I/O-bound. Each batch is mostly time spent *waiting* on the network, and
`async`/`await` with `httpx.AsyncClient` lets the event loop do other work during that wait
instead of blocking.

**L1 · "Would async help a CPU-bound task?"** — No. `asyncio` is single-threaded concurrency, and
the **GIL** means Python threads don't execute bytecode in parallel either. CPU-bound work needs
`multiprocessing`.

**L1 · "Why one `AsyncClient` for all the batches?"** — Connection pooling and keep-alive.
Creating a client per request throws away the TCP and TLS handshake every time.

### "Why Pydantic instead of checking the fields yourself?"

**L0** — One declarative definition of "valid", in one place. Type coercion, `EmailStr`, and
constraints (`min_length`, `max_length`, `ge=0`) for free — and critically,
`ValidationError.errors()` returns **structured** errors with `loc` and `msg`, which map straight
onto a per-row report. Hand-rolled validation gives you a stack trace instead.

**L1 · "What does `mode='before'` do on your validator?"** — Runs *before* type validation and
coercion. I use it to strip whitespace, so a row isn't rejected for trailing spaces no human would
notice in a spreadsheet.

**L1 · "Pydantic v1 vs v2?"** — v2 renamed `@validator` → `@field_validator` and `.dict()` →
`.model_dump()`, and rewrote the core in Rust, so it's substantially faster.

### "How do you make the error report actually usable?"

**L0** — `row_number = index + 2`. **+2** because the DataFrame is zero-indexed *and* line 1 of the
file is the header — so the number I report matches the line the user sees in Excel. A report
saying "row 1" when Excel says "row 3" is worse than useless.

**L1 · "Can one row produce more than one error?"** — Yes. I loop over `exc.errors()` and emit one
`RowError` per failing field, so a row with a bad email *and* a negative amount reports both.

**L1 · "Why `keep_default_na=False` on the CSV read?"** — Without it pandas turns an empty cell
into a float `NaN`, which sneaks past a `min_length` string rule. With it, the empty cell arrives
as `""` and the schema rejects it properly.

### "Walk me through your database."

**L0** — Two tables. `jobs` holds the summary plus per-batch outcomes serialised as JSON;
`row_errors` holds `(job_id, row_number, field, message)`. Index on `row_errors(job_id)` because
the report is only ever fetched by job.

**L1 · "Why store batches as JSON instead of a third table?"** — Batches are only ever read as a
whole, together with their job — never queried independently. If I needed "show me every failed
batch across all jobs", that JSON blob becomes wrong and I'd normalise it.

**L1 · "Why raw `sqlite3` and not an ORM?"** — Two tables. The point of the project is the sync
pipeline, not the data layer. An ORM would have been ceremony.

**L1 · "What's `executemany` doing?"** — A 5,000-error report becomes one statement instead of
5,000 round trips to SQLite.

### "How did you test it?"

**L0** — Unit-tested the pure pieces with no server and no network: `chunk` splitting into
full-plus-partial batches, `chunk` rejecting size 0, backoff doubling then capping, and
`validate_rows` collecting errors instead of raising.

**L1 · "What isn't tested?"** — The retry loop itself and the HTTP routes. I'd use `respx` or
`httpx.MockTransport` to fake a 429-then-200 sequence, and FastAPI's `TestClient` for the
endpoints. Right now the retry path is only verified by hand through the mock endpoint.

### ⭐ "What would you do differently?" — have all three ready

1. **Idempotency keys** per batch, so a retry after a lost response can't double-write.
2. **A dead-letter store** for batches that exhaust their retries, so they can be replayed rather
   than silently lost.
3. **Background processing.** The upload request currently blocks until the whole sync finishes.
   Fine at ten rows, wrong at fifty thousand — it should return a job id immediately and process
   asynchronously, with the client polling `GET /jobs/{id}`.

If pushed on *how*: `BackgroundTasks` for something simple, Celery or RQ with Redis for anything
real.

### Flaws to volunteer before they find them

- No jitter in the backoff (thundering herd).
- `Retry-After` is commented but not implemented.
- POST retries aren't idempotent.
- The mock endpoint keeps a module-level `_seen_batches` dict keyed on the first record's
  `external_id` — fine for a demo, global mutable state in anything real.

---

# 2. Mocha Leads — Multi-Tenant Lead Management CRM

React 18, TypeScript, Firebase (Auth + Firestore), Cloudinary, Capacitor, Tailwind, Vitest
· ~12,000 lines · **solo**

Ten more drill-downs already exist in `../valorx-prep/06-defending-your-code.md` — the unused
react-query dependency, client-side filtering vs security rules, Firestore composite indexes, the
`readBy` race condition, the unsigned Cloudinary preset, the hooks bug, behaviour at a million
records. Reread that file; it isn't duplicated here.

## The 60-second pitch

> "Mocha Leads is a multi-tenant CRM for trade-show lead capture, built solo — about 12,000 lines.
> The model is organisations → event folders → leads → tasks, assignments, activity logs and
> attachments, with a realtime team chat per lead.
>
> The part I'd point at is the authorization. There are four roles and four route guards on the
> client, but those guards are only UX — the real enforcement is mirrored in Firestore security
> rules, so a member can't read leads they aren't assigned to even straight from devtools.
>
> And it ships as an Android app from the same codebase via Capacitor — safe-area insets,
> hardware back-button handling, push notifications behind a feature flag."

## Two depth questions not covered in the other file

**"What does multi-tenant actually mean here — how are two organisations isolated?"**
Every document carries an `organizationId`, every query is scoped by it, and the security rules
check membership through an `isOrgMember(orgId)` helper that does a cross-document lookup on the
user record. The honest caveat: isolation is **logical, not physical** — one Firestore database
separated by a field and by rules. A rules mistake is a cross-tenant data leak, which is why the
rules file is the part I'd want reviewed hardest.

**"Why Firestore rather than a relational database?"**
The app is push-based — realtime chat, live lead updates — and `onSnapshot` gives that without me
building a websocket layer. The cost is that I gave up joins and paid for it: filtering a SQL
`WHERE` would do on the server happens on the client in places. For a lead pipeline with real
reporting needs, Postgres would have been the better call.

> **eTech note:** they run MySQL and MSSQL. If you say "I'd have used Postgres," expect
> *"why not MySQL?"* — answer honestly: for this workload either would do; Postgres is what I
> know best, and the deciding factor would be what the team already runs.

---

# 3. QuickCourt — Sports Facility Booking Platform

Next.js 15, TypeScript, PostgreSQL, Prisma ORM, NextAuth.js v5, React Query, Tailwind
· Odoo Hackathon 2025

> ⚠️ **This repo is not on your machine** — it only lives at `github.com/Jainishcodee/quickcourt`.
> **Clone it and reread the schema and the booking route before the interview.** Everything below
> is reconstructed from your resume bullets and must be checked against the actual code.

## The 60-second pitch

> "QuickCourt is a sports-facility booking platform built in a hackathon. Three roles — a user who
> books, a facility owner who lists courts and sees earnings, and an admin who approves facilities.
> Six-table relational schema in Postgres through Prisma; auth and role-based authorization with
> NextAuth v5, routes protected in middleware; React Query on the client for fetching and caching."

## Depth tree

### ⭐ "Two users book the same court for the same slot at the same moment. What happens?"

This is **the** question for any booking system and it will be asked. Answer honestly.

**The correct answer:** checking availability and then inserting is a **race condition** — both
requests can read "free" before either writes. Application-level checking cannot fix it. The fix
is at the database: a **unique constraint** on `(courtId, startTime)` so the second insert fails
at the DB level, wrapped in a **transaction** so the check and the write are atomic. Postgres
rejects the duplicate and you translate that error into a "slot just got taken" response.

If your code doesn't do this — **say so.** "I checked availability in the handler, which holds up
under hackathon load and is a genuine race under real load; the fix is a unique constraint plus a
transaction" is a *strong* answer. Claiming it's safe when it isn't is a weak one.

**L2 · "What isolation level would you need?"** — With a unique constraint, none special —
the constraint does the work at `READ COMMITTED`. Without one you'd need `SERIALIZABLE`, or an
explicit row lock (`SELECT ... FOR UPDATE`) on the court row.

### "Why Prisma over raw SQL?"

Type safety end to end — the schema generates TypeScript types, so a renamed column is a compile
error rather than a runtime one. Migrations are versioned. The cost is less control over the
generated query, and the N+1 problem if you're careless with relations.

**L1 · "What's the N+1 problem?"** — Fetching 50 bookings then looping to fetch each booking's
court is 51 queries. Fix: `include`/`select` so Prisma issues one query with a join.

### "How does role-based authorization work?"

NextAuth v5 with credentials; the role lives in the session/JWT; `middleware.ts` intercepts
requests and redirects by role before the page renders.

**L1 · "Is middleware enough?"** — No. Middleware protects *pages*. Every API route must re-check
the session server-side, because anyone can call the route directly with curl.

### "Why is the schema normalized — and where would you denormalize?"

Six tables (Users, Facilities, Courts, Bookings, Reviews, Amenities) with foreign keys, so a
facility's name lives in exactly one row. I'd denormalize for the owner earnings dashboard —
recomputing revenue by aggregating every booking on each page load doesn't scale; a maintained
running total or a materialized view would.

### "What does React Query give you that `useEffect` + `fetch` doesn't?"

Caching, deduplication of identical in-flight requests, background refetch, and loading/error
states without hand-rolling them. The real answer: it removes a whole class of "stale data on
screen" bugs.

---

# 4. Angular Admin Dashboard

Angular 18, Angular Material, PrimeNG, RxJS, TypeScript · **team codebase**
`g:\Internship\Salesforce_admin_web\admin-website`

> **For eTech this matters more than usual** — Angular is named in both their full-stack variants.
> Give it more airtime than you would elsewhere, while staying precise about your share.

## Claim it precisely — this is the honesty risk on your resume

You have **4 commits** here: `loader-feature-implemented-all-pages`, table alignment and spacing,
text justification, plus a merge. A senior did the rest. Your resume already says *"contributed
to"* — keep it that way and **never say "I built."**

> "That one's a team codebase — I contributed, I didn't build it. What I owned was a global
> loading state across all the pages, plus data-table layout work. I can talk through the
> architecture because I worked inside it, but I want to be clear about the size of my part."

Interviewers catch inflation instantly, and it colours everything else you said. Volunteering the
limit buys you credibility for the rest of the conversation.

## What you actually built — know this in detail

A **standalone** `LogoLoaderComponent` (`src/app/shared/components/logo-loader/`) with three
`@Input()`s — `message`, `logoSrc`, `logoAlt` — plus the global loading state in
`app.component.ts` that drives it:

- Subscribes to `router.events`; sets `isRouteLoading = true` on `NavigationStart`
- Clears it on `NavigationEnd`, `NavigationCancel` **and** `NavigationError` — not just the happy
  path, so a failed navigation can't leave the loader stuck on screen
- Enforces a **1-second minimum display time** via `minLoaderMs`
- Unsubscribes both subscriptions and clears the pending timeout in `ngOnDestroy`
- Rendered with Angular 17+ control flow: `@if (isRouteLoading) { ... }`

## Depth tree

### ⭐ "Why the minimum display time?"

Without it a fast navigation flashes the loader for ~40ms — visually that reads as a glitch, not
as loading. Holding it for at least a second makes it feel deliberate.

**L1 · "Isn't that making your app artificially slower?"** — Yes, and that's the honest trade-off.
The better pattern is the inverse: **delay showing** the loader by ~200ms, so fast navigations
never show one at all and only genuinely slow ones do. Same anti-flicker benefit without
penalising speed. If I redid it, that's what I'd do.

*This self-critique is your strongest Angular moment. It shows judgment, not just syntax.*

### "Why unsubscribe in `ngOnDestroy`?"

`router.events` is a long-lived observable. Without unsubscribing, the subscription holds a
reference to a destroyed component — a memory leak, and the callback keeps firing on every
navigation for a component that no longer exists.

**L1 · "What are the alternatives?"** — The `async` pipe in the template (auto-unsubscribes),
`takeUntil(destroy$)`, or `takeUntilDestroyed()` in Angular 16+.

### "What's a standalone component?"

One that declares `standalone: true` and imports its own dependencies through an `imports` array
instead of being declared in an NgModule. Less boilerplate, simpler lazy loading. Default from
Angular 19.

### "Why `@Input()` on the loader?"

So it's reusable — the message and the logo are configurable by the caller rather than hardcoded,
which is what let the same component drop into every page.

### "You clear the loader on Cancel and Error too — why does that matter?"

A guard rejecting navigation fires `NavigationCancel`, not `NavigationEnd`. If I only listened for
`NavigationEnd`, hitting a route your role can't access would leave the loading overlay on screen
permanently with no way out.

### If asked about the wider architecture (you can speak to it — you worked in it)

`core/` holds 4 route guards (`auth`, `super-admin`, `dms-auth`, `dms-v2-auth`), an HTTP
interceptor (`dms-auth.interceptor.ts`), and 6 injectable services (`api`, `auth`, `dms-api`,
`search`, …). `features/` has ~31 feature folders. Angular Material and PrimeNG for components,
Chart.js for charts, Leaflet for maps, RxJS 7.8.

**Say "I worked inside this structure," not "I designed this structure."**

---

# Rehearsal — ten minutes, standing up, timed

| Project | Lead with |
|---|---|
| **Angular Admin** | "Team codebase — I contributed a global loading state; I didn't build it." |
| **QuickCourt** | "Three roles, six tables, and a booking race I'd fix with a unique constraint." |
| **Mocha Leads** | "Authorization enforced at the database, not just the UI." |
| **SFSync** | "One bad row must never sink the job." |

If a pitch runs past 90 seconds, cut it.

## Before eTech specifically

- [ ] **Clone QuickCourt** and reread the Prisma schema and booking route — it's on your resume
      and not on your machine.
- [ ] Re-open `app/sync.py` in sfsync. It's 90 lines and it's the part they ask about.
- [ ] Re-open `app.component.ts` in the Angular admin — the router-events block.
- [ ] Drill **Nth-highest salary** and **ACID** until they're automatic. Both were in your prep
      last time and both were lost under pressure. Coverage without rehearsal doesn't survive.
- [ ] Add to the SQL drill: MySQL vs MSSQL syntax for row limiting — `LIMIT n OFFSET m` in MySQL
      vs `OFFSET m ROWS FETCH NEXT n ROWS ONLY` in SQL Server. They run both.
