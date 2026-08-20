# Scripts — say every one of these OUT LOUD five times

Reading these silently does nothing. The #1 cause of fresher rejection is rambling, and you only
fix that with your mouth, not your eyes.

---

## 1. "Tell me about yourself" — 75 seconds, memorize the shape

> "I'm a Computer Science undergrad at CHARUSAT — I came in through a diploma, where I finished at
> 9.33.
>
> For the last six months I've been a developer intern at Ibamaa, working on Japaate — a
> field-sales-automation app that's live on the Play Store. I shipped five feature modules there:
> catalog, cart and orders, outlet visits, attendance, and sales-target tracking. That's where I
> learned what production actually means — API contracts, offline-first caching, code review,
> shipping to real users.
>
> Alongside that I built a multi-tenant lead-management CRM entirely on my own — about twelve
> thousand lines — with four-level role-based access, realtime team chat, and I packaged it as an
> Android app. That's the project I'm proudest of, because I owned every decision in it.
>
> What draws me to ValorX specifically is that it's a product company solving a real, unglamorous
> data problem, and it's small enough that an intern actually owns things."

**Traps:** don't start with where you were born. Don't recite the resume line by line. Don't run
past 90 seconds. **End by pivoting to them** — that hands them the next question.

---

## 2. "What do you know about ValorX?" — 30 seconds, memorize almost verbatim

> "Valorx builds the spreadsheet layer for Salesforce. Companies use Salesforce as their system of
> record, but editing records one at a time is painful — so teams export to Excel, work offline,
> break the sync, and re-import errors. You have two products that fix that: **Wave**, a
> spreadsheet-style grid that runs inside Salesforce, and **Fusion**, which turns Excel or Google
> Sheets into a live two-way editor for Salesforce data. The point is the data never leaves
> Salesforce, so sharing rules and field-level security still apply. NVIDIA, Adobe, Qualcomm and BP
> use it."

Almost nobody else in the 112 will be able to say this. **This is your single biggest
differentiator.** Say it in the technical round *and* the HR round.

**Safe extra facts:** bootstrapped, roughly 60–70 people, India office in Bodakdev Ahmedabad,
AppExchange ISV.
**Do NOT say a founding year** — sources conflict (2015 vs 2019). Don't claim a partner tier.

---

## 3. "Do you know Salesforce?" — the honest script

Near-certain question. **Do not bluff. Do not apologize.** Three parts:

> "Honest answer — I haven't worked on the Salesforce platform professionally. What I have done is
> understand it well enough to know what I'd be joining: it's the leading cloud CRM, everything is
> object-based — standard objects like Account, Contact and Opportunity plus custom objects — and
> you query it with SOQL, which looks like SQL but is scoped to one object because it's
> multi-tenant with governor limits.
>
> What made me actually interested rather than just curious is what you do with it. Bulk edits
> against an API with hard governor limits is a genuinely interesting engineering problem — I'd
> guess Bulk API rather than per-record REST, to stay under the limits.
>
> And the piece that transfers directly: Lightning Web Components is built on web standards, and
> the mental model is very close to Angular — a JS class, an HTML template, decorators for inputs,
> lifecycle hooks. I've started on Trailhead to close the gap."

---

## 4. ⚠️ THE TRAP — never say "I worked on Salesforce"

Your folders are named `Salesforce_app` and `Salesforce_admin_web`, but that product is
**sales-force automation**, not Salesforce.com. There is no Apex, no LWC, no SOQL in it. If you say
"I worked on Salesforce," the very next question is about Apex and you are finished.

**Say this instead:**

> "I worked on a sales-force-automation platform — the same CRM problem domain as Salesforce:
> accounts, territories, targets, order capture — but it's a custom Angular and Flutter product,
> not the Salesforce.com platform. I haven't written Apex."

This is honest *and* keeps all the domain relevance. It is a strong answer, not a weak one.

---

## 5. Project pitch — Mocha Leads (90 seconds)

> **Problem:** "Sales teams collect leads at trade shows on paper and in spreadsheets, and by the
> time anyone follows up the context is gone — who met them, what they wanted, who owns it now.
>
> **What I built:** A multi-tenant CRM. An organization creates a folder per event, leads go into
> that folder, and each lead carries its own tasks, assignments, activity log, attachments and a
> team chat thread.
>
> **Stack and why:** React and TypeScript on the front, Firebase Auth and Firestore behind it. I
> chose Firestore specifically because the data is push-based — several reps look at the same lead
> at once and everyone should see updates live. Firestore's snapshot listeners give you that for
> free, which is also why I *didn't* add react-query; a fetch-cache layer would have been
> redundant.
>
> **My role:** All of it. Seventeen commits over five months, solo, about twelve thousand lines.
>
> **Hardest part:** Authorization. I started with role checks in the components, then realized
> that's cosmetic — anyone can open devtools. So I wrote the same model a second time as Firestore
> security rules on the server: `isSuperAdmin`, `isOrgAdmin`, `isOrgMember`, `leadInOrg`. The
> client guards are for UX; the rules are what actually enforce it.
>
> **What I'd change:** My read receipts do a read-modify-write on an array, so two people marking
> read at the same moment can clobber each other. It should be an atomic `arrayUnion`. I'd also
> move member-lead filtering to the server — right now I stream the org's leads and filter in the
> browser, which won't scale past a few thousand."

**That last paragraph is the most valuable thing in this document.** Volunteering a real flaw in
your own code, unprompted, is what separates a candidate who *wrote* the code from one who
*collected* it. It is also a direct bridge to ValorX's world — bulk data, scale, API limits.

---

## 6. The one bug story — have this ready

> "In the CRM, browser notifications replayed the entire backlog every time the app loaded — open
> the tab, get thirty notifications for things you'd already seen. The listener was firing for
> every existing unread document, not just new ones. I fixed it by recording the mount timestamp
> and only notifying for documents created after it. It's a small fix, but it taught me that a
> realtime listener's first emission is the whole current state, not a change — which is a
> genuinely easy thing to get wrong."

Concrete, technical, shows debugging reasoning, ends with a transferable lesson. 45 seconds.

---

## 7. HR answers

**"Why ValorX?"**
> "Two reasons. The product — it solves a real, unglamorous problem, and the engineering underneath
> it is interesting: bulk operations against an API with hard limits. And the size — around sixty
> people means an intern actually owns things instead of watching. Your careers page says
> 'ownership is encouraged,' and that's genuinely what I want out of a first job."

**"Your strengths?"** — two, each with proof:
> "I finish things on my own. The CRM is twelve thousand lines I wrote solo over five months, and
> nobody was checking on me. And I pick things up fast — I was writing production Flutter within a
> few weeks of starting at Ibamaa, having never used Dart."

**"Your weakness?"** — real, non-fatal, with a fix:
> "I over-build before I validate. On the CRM I spent a long time on the data layer before there
> was a single working screen. I've switched to getting one path working end-to-end first, then
> going back to make it good — it's made me much faster."

Never say "I'm a perfectionist." Never say a weakness core to the job.

**"Where in 5 years?"**
> "First couple of years I want to get genuinely strong — own features end to end, not just
> tickets. By year five, be the person a team relies on for a product area and be mentoring people.
> Ideally here, because a product company is where you build that depth."

Never mention MS, GATE, or starting a company.

**"Why should we hire you?"**
> "Three things. I have the fundamentals — OOP, SQL, JavaScript — and I've shipped with them, not
> just studied them. I've done the work to understand what you actually build, so I'd ramp on the
> domain fast. And I take ownership: my main project is twelve thousand lines nobody asked me to
> write."

**"You scored 50 — why not higher?"** (be ready, you are #63)
> "I lost time in the last section. Looking back, my gaps were in [subject]. I've been working on
> it since. I'd rather be judged on what I can build and explain than on that test."

Say it calmly. **Never defensive.**

**"Willing to relocate to Ahmedabad?"** — **Yes.** Unhedged. Any wobble here is a silent rejection.

**"Salary expectations?"**
> "For an internship I'm focused on the work and the team, not the number — whatever's standard
> for the role is fine with me."

**"Bond / service agreement?"**
> "I'd want to read the terms, but in principle it's not a problem — I'm not looking to leave
> quickly."

---

## 8. Questions to ask them — write these on paper and take it in

**Never** answer "no" to "do you have questions for us?"

1. "Wave renders a spreadsheet grid over thousands of Salesforce records — is the harder problem
   grid virtualization in the browser, or batching against the Salesforce API limits?"
2. "I saw the Ahmedabad postings mention .NET Core alongside Angular, and there's a recent Golang
   microservices role — would an intern get exposure to the backend, or is it frontend-focused?"
3. "What would 'this intern crushed it' look like at the three-month mark?"

Question 1 will visibly change how they look at you. Nobody else will ask it.

---

## 9. Rules for the room

- **Say "I" not "we."** Interviewers hear "we" and assume you did nothing.
- **Never say "it was just a college project."** It kills ~31% of chances. Say: "It was a college
  project, and the decision I'm most proud of in it was…"
- **Think out loud in the coding question.** Silence fails people; messy-but-narrated reasoning
  passes them. State the brute force and its complexity first, *then* improve it.
- **Volunteer time complexity unprompted.** It signals maturity.
- **"I don't know, but here's how I'd find out"** is a good answer. A caught bluff is fatal.
- Slow your speech about 20%. Smile at the start and the end.
