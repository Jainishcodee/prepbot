# Resume edits — copy-paste text

Open `Jainish_Shah_SWE_Resume.docx`. Make these four changes, export to PDF, print 3 copies.
**Also bring a printout of the original `Jainish_Shah_SWE_Resume.pdf` you submitted.**

---

## 1. SUMMARY — replace the whole block

> CS undergraduate with six months shipping production modules on a live sales-force-automation
> product (Japaate, on the Play Store) — the same CRM problem domain Salesforce serves. Full-stack
> across React, TypeScript, Python and PostgreSQL, with production Angular 18 exposure. Built a
> multi-tenant lead-management CRM end to end, solo, and shipped it to Android.

---

## 2. EXPERIENCE — Ibamaa Pvt. Ltd

Keep the header line and dates as they are. Replace the bullets:

> • Shipped five production feature modules for Japaate — catalog, cart/orders, outlet visits,
>   attendance and sales-target tracking — inside a 24-module field-sales-automation platform
>   (distributors, retailers, beat routes, order capture)
> • Integrated type-safe REST APIs (Dio + Retrofit) with centralized error handling, token-refresh
>   interceptors and strongly-typed request/response models
> • Implemented offline-first caching with Hive and reactive state management with Riverpod so
>   field reps keep working with no connectivity, cutting redundant network calls
> • One of the primary contributors to the codebase by commit volume, working in an Agile,
>   Git-based team — feature branches, pull requests and code reviews

**Before you use that last bullet, verify it.** Run this and check the number next to your name:

```bash
git -C "g:/Internship/App/Salesforce_app" shortlog -sn --all
```

If you are clearly top or second, the bullet is fair. If not, delete it.

---

## 3. PROJECTS — replace the whole section

### Entry 1 — replaces "Leads Pipeline" (the Kanban claim was not in your code)

> **Mocha Leads — Multi-Tenant Lead Management CRM**  ·  Solo build
> *React 18, TypeScript, Firebase (Auth + Firestore), Cloudinary, Capacitor, Tailwind, Vitest*
> • Built a multi-tenant CRM end to end and solo (~12,000 lines): organizations → event folders →
>   leads → tasks, assignments, activity logs and file attachments
> • Implemented four-role access control with four route guards on the client, mirrored
>   server-side in Firestore security rules (`isSuperAdmin`, `isOrgAdmin`, `isOrgMember`,
>   `leadInOrg`) so authorization is enforced at the database, not just the UI
> • Built realtime per-lead team chat on Firestore snapshot listeners — text, image and
>   MediaRecorder voice notes, upload progress, reply-to, pinned messages and read receipts
> • Shipped the same React app as an Android app via Capacitor: safe-area insets, hardware
>   back-button handling, and push notifications behind a feature flag

### Entry 2 — tonight's Python build

> **SFSync — Bulk Spreadsheet-to-API Sync Service**
> *Python, FastAPI, Pydantic, pandas, httpx, SQLite*
> • Built a REST service that ingests a CSV/Excel upload, validates every row against a Pydantic
>   schema, and pushes valid rows to a downstream API in batches
> • Implemented exponential-backoff retry on rate-limit and server errors, with a max-attempt cap,
>   so a throttled batch is retried rather than lost
> • Designed for partial failure — invalid rows are collected and returned as a per-row error
>   report instead of failing the whole job

### Entry 3 — QuickCourt, keep exactly as it is

Do not touch it. It is your strongest relational-database story, and **DBMS is tested in both of
ValorX's technical rounds.**

### Entry 4 — Angular, worded precisely

> **Angular Admin Dashboard**  ·  *Team codebase*
> *Angular 18, Angular Material, PrimeNG, RxJS, TypeScript*
> • Contributed to a 31-module Angular 18 admin dashboard (route guards, HTTP interceptor,
>   injectable service layer): implemented a global loading-state feature across all pages and
>   refined data-table layout and alignment

**Say "contributed to", never "built".** If they ask how much was yours, answer straight:
*"A senior engineer built most of it. My work was the loading-state feature across the pages and
the table layout fixes. I know the codebase — the guards, the interceptor, the services — but I
wouldn't claim I architected it."* That answer earns more trust than the work itself.

**Drop MicroLink.** It is a team repo, it is not on your GitHub, and you cannot show it if asked.

---

## 4. SKILLS — two small fixes

- Move **Python** to the front of the Languages line: `Python, TypeScript, Java, C, C++, Dart, SQL`
- Add to Backend: `FastAPI, Pydantic`
- **Do not add** react-query, Zod or react-hook-form. They are installed in Mocha Leads but
  unused — shadcn scaffolded them in.

---

## 5. Ten minutes, high leverage — do these too

1. **Pin 6 repos on GitHub** (Customize your pins on your profile): `Leads_pipeline`, `quickcourt`,
   `CraftNest`, `Hospital-length-of-stay-prediction`, `Energy-consumption-prediction`, and
   tonight's `sfsync`. Right now your profile lists 17 repos newest-first, so the first thing a
   visitor sees is `NAHAR_REPORTS`.
2. **Open `portfolio.jainish.workers.dev` in a browser.** When fetched it returned only a bare
   header with no projects or contact. If it is genuinely that empty, **delete the link from the
   resume** — a dead link at the top of the page is worse than no link.
3. Fix the description on `face-detection-attendance-system`. It currently reads *"The is for my
   analysis purpose in the web and app development"*, and that repo is linked from your AI/ML
   resume.
4. Also remove the Kanban/drag-and-drop line from **`Jainish_Shah_QA_Resume.docx`** — same false
   claim is in there.
