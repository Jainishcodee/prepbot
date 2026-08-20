# Salesforce — the 15-term survival kit

**Reality check:** ValorX builds a product *on top of* Salesforce. No intern is expected to write
Apex. Nobody else interviewing will know these terms either — which is exactly why knowing 15 of
them makes you memorable.

**Read `01-scripts.md` §3 for the scripted answer to "Do you know Salesforce?" and §4 for the
sales-force-automation naming trap. Those two matter more than this whole file.**

---

**CRM** — software to manage a company's interactions with customers and prospects (leads, deals,
support cases) in one place. **Salesforce** is the leading cloud CRM, delivered as **SaaS**, and
also a **PaaS** you can build custom apps on.

**Object** — effectively a database table. A **record** is a row, a **field** is a column.
**Standard objects** ship with Salesforce; **custom objects** you create end in `__c`.

**Core standard objects** — **Account** (a company), **Contact** (a person at it), **Lead**
(unqualified prospect), **Opportunity** (a potential deal), **Case** (a support ticket), Campaign.

**⭐ Lookup vs Master-Detail** — the most-asked Salesforce fresher question:

| Lookup | Master-Detail |
|---|---|
| loosely coupled | tightly coupled |
| parent optional | parent **required** |
| delete parent → child survives | delete parent → **child deleted** |
| child has own owner & sharing | child **inherits** parent's security |
| no roll-up summary | **roll-up summary allowed** |

**Junction object** — a custom object with **two master-detail relationships**, used to model
**many-to-many**.

**⭐ SOQL vs SQL** — SOQL queries **one object at a time** (plus related objects by traversing
relationships like `Contact.Account.Name`). **No `SELECT *`** — you name every field. No SQL-style
JOINs. Otherwise familiar: `SELECT Id, Name FROM Account WHERE Industry='Tech' LIMIT 10`.

**SOQL vs SOSL** — SOQL when you know the object; **SOSL** for full-text search across many objects
at once: `FIND {Acme} IN ALL FIELDS RETURNING Account, Contact`.

**Apex** — Salesforce's proprietary, strongly-typed, **Java-like** language running **on their
servers**. Used for triggers, controllers, batch jobs. Needs **75% test coverage** to deploy.

**⭐ Trigger — before vs after** — Apex that runs automatically on a DML event.
- **`before`** — validate or **modify the record itself** (not saved yet, no DML needed)
- **`after`** — the record has an **Id**; use for related records, roll-ups, integrations

Context variables: `Trigger.new`, `Trigger.old`, `Trigger.newMap`, `Trigger.oldMap`, plus
`isInsert`/`isUpdate`/`isBefore`/`isAfter`. Best practice: **one trigger per object**, logic in a
handler class.

**⭐ Governor limits** — Salesforce is **multi-tenant**, so per-transaction caps stop one customer
starving others. Key ones: **100 SOQL queries**, **150 DML statements**, 50,000 records retrieved,
10s CPU. **The #1 rule: never put SOQL or DML inside a for loop.**

**Bulkification** — writing code that handles **collections** (up to 200 records per trigger
invocation) rather than one at a time: query once into a Map, loop in memory, single DML at the end.

**LWC vs Aura** — **Lightning Web Components** is the modern framework built on **native web
standards** (web components, ES6 modules) — faster and less proprietary. **Aura** is the older
proprietary one. New development should be LWC.

> **Your best line:** *"LWC is a component framework built on web standards, and the mental model is
> very close to Angular — a JS class, an HTML template, decorators for inputs, lifecycle hooks.
> That's the part of my background that transfers directly."*

**Profile vs Role vs Permission Set** —
- **Profile** — what a user **can do** (object/field CRUD, layouts). Exactly **one** per user.
- **Permission Set** — **additive** extra permissions on top. Many per user.
- **Role** — what a user **can see** (record visibility via the role hierarchy).
- Memory hook: **Profile = what you can DO. Role = what you can SEE.**

**OWD / sharing** — **Org-Wide Defaults** set the most restrictive baseline (Private / Public Read
Only / Public Read-Write); access is then opened up by role hierarchy → sharing rules → manual
sharing. Security is layered: **object level → field level → record level**.

**Sandbox vs Production** — production is live with real data; a sandbox is an isolated copy for
dev/test (Developer, Developer Pro, Partial Copy, Full Copy).

**⭐ APIs — the one that matters for ValorX** — **REST** (per-record CRUD, JSON), **SOAP** (XML),
**Bulk API 2.0** (**asynchronous, for loading or extracting large volumes — exactly what a
spreadsheet product needs**), Streaming, Metadata, Composite.

> **Killer connection:** *"Given Wave and Fusion push bulk spreadsheet edits back into Salesforce,
> I'd guess Bulk API 2.0 rather than per-record REST — otherwise you'd burn through the API limits
> immediately."* Ask it as a question, don't assert it.

**Trailhead** — Salesforce's free gamified learning platform. Badges, hands-on challenges, a free
Playground org.

**AppExchange** — Salesforce's app marketplace, where ISVs like ValorX publish managed packages.
*(ValorX Fusion is rated 5.0★ there.)*

---

## Trailhead — do this on your phone while waiting between rounds

Sign up free at **trailhead.salesforce.com**. Being able to say *"I did these last night"* is a
genuine differentiator.

| Order | Module | Time |
|---|---|---|
| 1 | **CRM Basics** | ~25 min |
| 2 | **Salesforce Platform Basics** | ~45 min |
| 3 | **Data Modeling** — covers lookup vs master-detail | ~40 min |

Screenshot the badges. Then in the room: *"I worked through CRM Basics and Platform Basics on
Trailhead to get the fundamentals — objects, fields, the data model — and I'm on Data Modeling
next."*
