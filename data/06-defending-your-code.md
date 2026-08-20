# Defending your own code

40–60% of a fresher technical round is resume drilling, and this is where candidates get
eliminated. These are the ten hardest questions someone who actually opens your repo could ask —
with answers that turn each one into a point in your favour.

**The meta-rule:** when you know a weakness in your own code, **say it before they find it.** A
candidate who volunteers "here's what's wrong with my design" reads as an engineer. One who defends
everything reads as someone who doesn't understand what they built.

---

### 1. "You have react-query, Zod and react-hook-form in `package.json`. Where are they used?"

They aren't. shadcn/ui scaffolded them in. `QueryClientProvider` wraps the app in `App.tsx` but
there is not a single `useQuery` or `useMutation`; validation is hand-rolled in `src/lib/validation.ts`.

> "They're not used — shadcn scaffolds them in when you initialize it. And I'd actually defend not
> using react-query here: my data is push-based over Firestore snapshot listeners, so a fetch-cache
> layer would be redundant. The listener *is* the cache. I should clean those deps out."

**Do not list them on your resume.** That's the trap.

---

### 2. "What stops a member from opening devtools and reading leads they aren't assigned to?"

Your `useLeads` hook streams the whole org's leads and filters **in the browser**. Client-side
filtering is not security. But you did write the server-side rules — lead with those.

> "Nothing on the client — the filtering in the hook is for UX, not security. The actual enforcement
> is in `firestore.rules`: `isOrgMember` checks the requesting user's org against the document's,
> and `leadInOrg` does a cross-document lookup. If you tamper with the client, the read is rejected
> at the database. That said, I'm still streaming the whole org collection and filtering down —
> which works at my scale but is wasteful, and I'd move that filter into the query."

---

### 3. "Your queries have multiple `where` clauses plus an `orderBy`. Doesn't Firestore need an index?"

Yes — composite indexes.

> "It does. Every query builder appends `orderBy('createdAt','desc')` on top of `organizationId`
> and sometimes `folderId`, and Firestore rejects that until you create the composite index. The
> first time it happens you get an error with a direct link to create it. The cost is on writes —
> every index has to be updated on every write, so more indexes means slower writes and more
> storage."

---

### 4. "Walk me through how a chat message gets marked as read."

This one has a real bug. **Volunteer it.**

> "It fetches all messages for the lead, then fires parallel updates to add the user to each
> `readBy` array. Two problems I'd fix. It's a read-modify-write, so if two people open the thread
> at the same moment they can clobber each other's `readBy` — it should be an atomic `arrayUnion`.
> And it's O(N) writes every time someone opens a chat; I have a `writeBatch` helper in
> `firestore.ts` that I didn't use here."

This single answer is worth more than any correct answer you'll give all day.

---

### 5. "Your Cloudinary upload preset is unsigned. What's the risk?"

> "The preset is public — it ships in the client bundle — so anyone who reads it can upload to my
> account. I scoped it with a folder and tags per lead, which limits the mess but not the abuse.
> The real fix is signed uploads: a backend endpoint or Cloud Function generates a signature per
> upload so only my server can authorize one."

---

### 6. "Why did you move off Firebase Storage to Cloudinary?"

You documented this in `CLOUDINARY_MIGRATION.md` — so say you documented it.

> "Firebase Storage rules and CORS were fighting me, and Cloudinary gave me on-the-fly image
> transformations, which mattered for chat thumbnails. I wrote the reasoning up in
> `CLOUDINARY_MIGRATION.md` in the repo so the decision wasn't just in my head."

"I documented the architectural decision" is a strong signal at this level.

---

### 7. "How does a React web app become an Android APK?"

> "Capacitor. `vite build` produces `dist/`, Capacitor's config points `webDir` at it, `npx cap
> sync` copies it into a native Android project, then Gradle builds the APK. The app runs in a
> WebView, so React Router still works normally. The platform-specific work was the interesting
> part — safe-area insets for notched devices via CSS variables, and intercepting the hardware back
> button so it minimizes the app at the root instead of exiting."

---

### 8. "Only 17 commits — is that the whole project?"

> "Yes, and my commits are too big — I batched a lot of work into each one. It's about twelve
> thousand lines over five months, solo. On the team project at Ibamaa I commit far more granularly
> because other people have to review it."

Own it plainly. Don't get defensive about commit count.

---

### 9. "There's a bug in your hooks — spot it."

`useOrganizationTasks` in `src/hooks/useFirebaseData.ts` has an early `return` **before** a
`useMemo`. `useFolders` and `useUsers` have the same shape. That violates the Rules of Hooks and
will crash when the guard condition flips between renders.

> "That's a Rules of Hooks violation — I return early before a `useMemo`, so the hook count changes
> between renders and React will throw. The fix is to move the guard after all the hooks, or push
> the condition inside the memo."

**If they find this and you already know it, you win the round.** Read those three hooks tonight.

---

### 10. "How would this behave with a million records?"

The single most ValorX-relevant question you can get. They *are* a bulk-data company.

> "It would break, in three specific places. I stream the org's whole lead collection to the client
> and filter there — that has to become a server-side query with pagination. My chat read-receipt
> update is O(N) writes — that needs batching. And the composite indexes get expensive on write at
> that volume. Honestly it's the same shape of problem your Wave grid has: you can't render or
> transfer everything, so it becomes virtualization on the client and batching on the wire."

---

## Before you sleep — 10 minutes

Open these four files and skim them so nothing is a surprise:

1. `src/hooks/useFirebaseData.ts` — find the early-return-before-`useMemo` in `useOrganizationTasks`
2. `firestore.rules` — read `isSuperAdmin`, `isOrgAdmin`, `isOrgMember`, `leadInOrg`
3. `src/auth/ProtectedRoute.tsx` — the four guards
4. `src/lib/firestore.ts` — the query builders and the `writeBatch` helper you didn't use

**Then sketch the architecture on paper once:** React app → `useFirebaseData` hooks →
`lib/api.ts` domain APIs → `lib/firestore.ts` generic CRUD → Firestore, with `firestore.rules`
sitting on the database enforcing access, and Cloudinary off to the side for media. Being able to
draw that in 30 seconds is worth more than any memorized definition.
