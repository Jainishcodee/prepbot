# Odysseus Solutions — Gen AI-First AI/ML Developer · Campus Drive

Rounds you were told to expect:
**1.** Aptitude / quant + **RAG-based questions** → **2.** GD on AI topics → **3.** Coding round
**where AI use is allowed** → **4.** Interview → selection.

---

## 1. The company — what to say out loud

**Odysseus Solutions** — Miami-based **travel technology** company, founded **2005**. They build
online booking engines for travel businesses across B2B, B2C and B2B2C.

The 20-second version:

> "Odysseus builds booking engines for the travel industry — air, hotel and especially **cruise**.
> Their founder built what became the cruise industry's leading booking engine, with live
> connections to 30+ of the world's top cruise lines plus the major GDSs. So it's deep
> integration work: pulling live inventory and pricing from a lot of external systems and making
> it bookable in one place."

Facts worth knowing:

| | |
|---|---|
| Founded | 2005, HQ **Miami** |
| Size | **~150–157 people**, across 4 continents |
| India | **Vadodara** (main dev centre), **Anand**, Bengaluru, expanding to Ahmedabad |
| Founder | **Monish Luthra** — built the cruise booking engine |
| India lead | **Rignesh Dave** — heads all development and operations at Vadodara; joined 2009 as the **5th employee** |
| Products | Cruise / air / hotel booking engines, **GDS integration**, business process automation |
| Stack | Heavy **Microsoft .NET / ASP.NET** |
| Glassdoor | **3.4 / 5** (54 reviews) |

**Two things this tells you:**

1. **They are a .NET shop.** Their normal interviews are C#/.NET-heavy. You don't have C# — but
   this drive is explicitly a *Gen AI-first* role open to "any engineering background," and the
   required-skills list says **"preferably Python."** Play Python, not .NET. If .NET comes up:
   *"I haven't worked in C#. My backend work is Python and Node — the OOP and REST concepts
   transfer, and I'd expect to pick up the syntax quickly."*
2. **GDS integration is their hard problem** — many external systems, rate limits, partial
   failures, retries. **That is literally SFSync.** Make that connection; it's your best bridge
   into their domain.

---

## 2. Which resume — and the gap you must close tonight

**Use the AI/ML resume.** It's the only one that leads with Python, scikit-learn, TensorFlow and
real ML projects with metrics.

⚠️ **But it has zero Gen AI on it.** The JD calls Gen AI familiarity *"a non-negotiable, evaluated
component"* and says candidates with **"academic projects, hackathon work, internships, or
self-driven learning involving Gen AI/LLMs will be given strong preference."*

Right now your AI/ML resume says nothing about LLMs, prompting, or AI-assisted engineering — and
you genuinely do this every day. Add one line tonight. Suggested, and true:

> **Gen AI & LLMs:** LLM-assisted development (Claude Code, ChatGPT) for feature build, debugging
> and test generation · Prompt engineering · RAG concepts · LLM API integration

And consider a project line for **kaggriculture** — the JD explicitly lists *"Kaggle competitions"*
under Good to Have, and it's real Python engineering:

> **Kaggriculture — Kaggle Simulation Competition Agent** · Python
> • Built a competition agent plus a benchmarking harness — instrumented the simulator's internals
>   for exact accounting, ran parameter sweeps and head-to-head duels across seeds
> • Final agent reached **$30,880 mean vs the starter baseline's $3,477 — 8–0 head-to-head**
> • Verified the official rules against simulator source and documented six errors in them

---

## 3. Round 1 — RAG, embeddings and LLM fundamentals

This is your biggest knowledge gap and it's being tested directly. Learn it in this order.

### RAG — the core

**What is RAG?**
Retrieval-Augmented Generation. Instead of relying only on what the model learned in training,
you **retrieve relevant text from an external knowledge source at query time and put it into the
prompt**, so the model answers from provided facts rather than memory.

**Why does it exist?** Three problems it solves:
1. **Knowledge cutoff** — the model doesn't know anything after its training date.
2. **Private data** — it has never seen your company's documents.
3. **Hallucination** — grounding the answer in retrieved text makes it verifiable, and lets you
   **cite sources**.

**The pipeline — be able to draw this:**

```
INGEST (offline, once)
  documents → chunk → embed each chunk → store vectors + text in a vector DB

QUERY (per request)
  user question → embed the question
                → similarity search in the vector DB → top-k chunks
                → build prompt: [system] + [retrieved context] + [question]
                → LLM generates a grounded answer + citations
```

### Depth tree — where they'll drill

**"What is an embedding?"**
A dense numeric vector representing the *meaning* of a piece of text. Text with similar meaning
lands close together in vector space — so "cheap flight" and "low-cost airfare" are near each
other even with no shared words. That's why it beats keyword search.

**L1 · "How do you measure 'close'?"** — **Cosine similarity** most often (angle between vectors,
ignores magnitude). Also dot product and Euclidean distance.

**L1 · "How many dimensions?"** — Depends on the model; commonly 384 to 1,536. More dimensions
capture more nuance but cost more storage and compute.

**"Why chunk the documents? Why not embed the whole file?"**
Two reasons: the embedding of a whole document is an average of everything in it, so it's too
blurry to match a specific question; and you can't fit a whole document into the prompt anyway.

**L1 · "What chunk size?"** — Trade-off. Too small and you lose the surrounding context that made
the passage meaningful; too large and you retrieve noise, waste tokens, and dilute the match.
Typical starting point is a few hundred tokens.

**L1 · "Why overlap between chunks?"** — So a sentence or idea that straddles a boundary isn't cut
in half and lost from both chunks.

**"What is a vector database? Name some."**
A database that stores embeddings and does fast approximate nearest-neighbour search over them.
**FAISS** (Meta's library, local, in-process), **Chroma** (local, easy to start), **Pinecone**
(managed cloud), plus Weaviate, Qdrant, and **pgvector** if you want it inside Postgres.

**L1 · "Why 'approximate' nearest neighbour?"** — Exact search over millions of vectors is too
slow. ANN indexes (HNSW, IVF) trade a little recall for a large speed win.

**"What is `top-k`?"** — How many of the most similar chunks you retrieve and stuff into the
prompt. Too low, you miss the answer; too high, you add noise and burn context.

**⭐ "RAG vs fine-tuning — when would you use which?"** *(near-certain question)*
- **RAG** = giving the model **knowledge**. Facts, documents, anything that changes. Cheap to
  update — you re-index, you don't retrain. Answers can cite sources.
- **Fine-tuning** = changing the model's **behaviour**. Tone, output format, domain style,
  following a specific instruction pattern.
- Rule of thumb: *"if it's facts, retrieve; if it's behaviour, fine-tune."* They're complementary,
  not alternatives.

**⭐ "Where does RAG fail?"**
This is the L2 that separates people who read a blog post from people who thought about it:
- **Retrieval miss** — the right chunk exists but wasn't in the top-k, so the model answers
  confidently from nothing. Bad chunking or a weak embedding model causes this.
- **Lost in the middle** — LLMs attend better to the start and end of a long context; facts buried
  in the middle get overlooked.
- **It still hallucinates** — retrieval reduces hallucination, it doesn't eliminate it. You need
  to instruct the model to answer *only* from context and say "I don't know" otherwise.
- **Stale index** — the source changed and nobody re-indexed.

**"How would you improve retrieval quality?"**
- **Hybrid search** — combine dense/semantic search with sparse keyword search (BM25). Semantic
  search is bad at exact tokens like product codes, error IDs or flight numbers; keyword search
  catches those.
- **Reranking** — retrieve 50 candidates cheaply, then rerank with a cross-encoder and keep the
  best 5. Much better precision.
- **Query rewriting** — expand or clarify the user's question before embedding it.
- **Metadata filtering** — filter by date, source or document type before the vector search.

**"How do you evaluate a RAG system?"**
Two halves, measured separately:
- **Retrieval:** did we fetch the right chunks? — recall@k, precision@k, MRR.
- **Generation:** **faithfulness/groundedness** (is every claim supported by the retrieved
  context?) and **answer relevance**. **RAGAS** is the framework usually named.

### LLM fundamentals

**"How does an LLM work, in one paragraph?"**
It's a transformer trained to predict the next **token** given everything before it. The
**attention** mechanism lets each token weigh every other token in the context, which is how it
captures relationships across a long passage. Trained on huge text corpora (pre-training), then
tuned to follow instructions and align with human preference (fine-tuning / RLHF).

**"What is a token?"** — A chunk of text, roughly ¾ of a word on average. Models bill and limit by
tokens, not characters. The **context window** is the maximum tokens of input + output.

**"What is temperature?"** — Controls randomness in sampling. **0** = near-deterministic, pick the
most likely token — right for extraction, classification, code. **Higher** = more varied — right
for brainstorming and creative writing. **top-p** (nucleus sampling) is the related knob: sample
only from the smallest set of tokens whose probability sums to p.

**⭐ "Why do LLMs hallucinate?"**
Because they're trained to produce the most **plausible continuation**, not the most **true** one.
There's no lookup step and no internal fact-check — a fluent wrong answer and a fluent right
answer look the same to the objective it was trained on. Mitigations: ground it with RAG, ask for
citations, lower the temperature, tell it explicitly to say "I don't know," and verify anything
that matters.

**"What are LLMs bad at?"** — Precise arithmetic and counting, anything after the cutoff,
guaranteed-consistent output across runs, very long-context recall, and knowing what they don't
know. Also: they're non-deterministic by default, which makes testing them harder than testing
normal code.

### Prompt engineering — what to say

They ask for "hands-on prompt engineering." Have concrete technique, not adjectives:

1. **Be specific about role, task and output format.** "Return JSON matching this schema" beats
   "give me the data."
2. **Give context, don't assume it.** Most bad output is a missing-context problem, not a model
   problem.
3. **Few-shot examples** — show two or three input→output pairs when the format matters.
4. **Chain of thought** — ask it to reason step by step before answering for multi-step problems.
5. **Decompose** — split a large task into several prompts instead of one giant one.
6. **Constrain** — say what to do when it doesn't know, and set explicit boundaries.
7. **Iterate** — treat the prompt as code: change one thing, check the output, keep what works.

---

## 4. Round 2 — Group Discussion on AI topics

GD is scored on **contribution quality and behaviour**, not on winning.

### Technique

- **Enter in the first 60 seconds.** People who speak late are often never scored.
- **Open with structure**, not opinion: *"I think there are three angles here — economic, technical
  and ethical. Let me start with…"* Framing the discussion scores higher than adding one more take.
- **Bring a fact or example.** Specifics beat opinions.
- **Bring someone in** — *"Ravi was making a point about jobs, I'd like to hear it."* Panels
  explicitly look for this.
- **Never interrupt or raise your voice.** Being loud reads as aggressive, not confident.
- **Volunteer the summary at the end** if nobody has. Biggest single scoring opportunity.
- Target **3–5 solid contributions**, not the most airtime.

### Likely topics and a position for each

**"Will AI replace software developers?"**
Balanced beats extreme. *"It replaces tasks, not the job. What it removes is boilerplate and the
first draft; what it makes more valuable is judgement — deciding what to build, reviewing whether
the output is right, and owning the consequences when it isn't. I use these tools daily; they
make me faster, they don't make the decisions."*

**"Can we trust AI-generated code?"**
*"Trust but verify. AI-generated code is a fast draft, not a finished artefact. It's confidently
wrong sometimes, it can reproduce insecure patterns, and it doesn't know your codebase's
constraints. The discipline is the same as reviewing a junior's PR — read every line, test it, and
never ship what you can't explain."*

**"Should AI be regulated?"**
Land in the middle: regulate **applications and outcomes** (bias in hiring, medical, credit
decisions; transparency about AI-generated content) rather than research itself; note the
trade-off that heavy regulation favours large incumbents who can afford compliance.

**"AI and jobs / education"**
Acknowledge real displacement rather than dismissing it; argue the response is re-skilling and
changing what we assess — if AI can do the assignment, the assignment was testing the wrong thing.

**⭐ "AI in travel" — prepare this one specially, it's their industry**
Concrete applications: conversational booking (natural-language search instead of forms),
**personalised recommendations**, **dynamic pricing and demand forecasting**, automated customer
support and rebooking during disruptions, **review summarisation**, itinerary generation, fraud
detection, and — most relevant to them — **using LLMs to normalise messy supplier data**, since a
GDS-integration business is constantly reconciling different formats from different providers.

Dropping that last one in a GD, at a travel-tech company, is the kind of thing panels remember.

---

## 5. Round 3 — Coding round with AI allowed ⭐ your biggest edge

**Understand what's actually being measured.** If they let you use AI, they are not testing whether
you can write a loop. They're testing **how you work with the tool** — because that's the job
description. Most candidates will either refuse to use it, or paste output blindly. Both score badly.

### How to win it

1. **Understand and restate the problem first — before touching the AI.** Say your approach out
   loud or in a comment. This proves the thinking is yours.
2. **Prompt specifically.** Not "write a function to do X" but "write a Python function that takes
   *this* input, returns *this*, and handles empty input and duplicates."
3. **Read every line it gives you.** If you can't explain it, don't keep it. You *will* be asked
   "why did you do it this way."
4. **Test it.** Run it on an edge case immediately — empty input, single element, duplicates,
   negatives. Finding a bug in the AI's output in front of them is a *strong* signal.
5. **Iterate visibly.** "This works but it's O(n²) — let me ask for a hashmap version" shows
   exactly the judgement they want.
6. **Say what you verified.** "I checked this handles the empty case and I confirmed the complexity
   is O(n)."

### The three ways people fail this round

- **Refusing to use AI** to prove they're smart. Reads as rigid, and it's the opposite of the JD.
- **Pasting without reading** — then freezing when asked to explain line 7.
- **Over-prompting** — asking the AI to solve the whole problem in one shot instead of decomposing
  it. Produces something big and unexplainable.

> **Your line if asked how you use AI:** *"I use it as a fast pair, not an oracle. I decide the
> approach, use it to accelerate the writing, and then read and test everything before I keep it.
> The failure mode is trusting output you haven't verified — it's confidently wrong often enough
> that you have to check."*

That answer is exactly the JD's *"verifying AI-generated output, recognizing hallucinations, and
applying human judgment."*

### Still drill the fundamentals

AI availability doesn't cover you if they ask **"now explain the time complexity"** — and your
ValorX post-mortem says optimisation follow-ups are your weak spot. Reverse-an-array cost you
there. Re-drill: Two Sum with a hashmap, complexity of everything you write, and the
brute-force → optimised progression said out loud.

---

## 6. Round 4 — The interview

### Your intro for this role

> "I'm Jainish Shah, [final-year] B.Tech Computer Science at Charusat — I came in through the
> diploma route, so I've been writing code about five years.
>
> My core language is **Python**, and most of my project work is machine learning — a hospital
> length-of-stay regression model on a 30,000-record dataset where I got MAE down to 1.32 days, a
> neural-network energy-consumption model in TensorFlow, and a face-recognition attendance system
> in OpenCV that I delivered for a client during an internship. I've also done a Kaggle simulation
> competition, where I wrote the agent and a benchmarking harness to tune it empirically.
>
> Alongside that I've spent six months interning at Ibamaa shipping production modules on a live
> product, so I've worked in a real team with code reviews and releases.
>
> The part that connects to this role: **I build with Gen AI every day** — I use Claude and
> ChatGPT for feature work, debugging and generating test cases, and my most recent project was a
> Python FastAPI service I built that way. I've learned the hard part isn't getting output, it's
> knowing what to verify. That's why this role interested me — it's the way I already work."

### Questions they'll ask, beyond the technical

- **"Give me a concrete example of using AI for a real engineering task."** ← near-certain. Have
  one specific story: what you asked, what came back, **what was wrong with it**, and how you
  caught it. The "what was wrong" part is what makes it credible.
- **"When has AI given you a wrong answer?"** Have a real one ready.
- **"Why travel tech?"** Honest: *"I hadn't worked in travel before, but the problem is
  interesting — you're integrating live inventory and pricing from dozens of external systems that
  all behave differently. I built a service that batches and retries against a rate-limited API,
  so that class of problem is familiar."*
- **Why this company / where do you see yourself** — standard, prepare as usual.

### Questions to ask them

1. "Where is Gen AI actually in production for you today versus internal tooling — is it in the
   booking flow, in customer support, or mostly accelerating the engineering team?"
2. "With GDS and 30+ cruise line integrations, is anyone using LLMs to normalise supplier data
   formats? That seems like a natural fit."
3. "The stack looks .NET-heavy. Where does Python sit — is it the AI/ML side specifically?"
4. "What does the internship-to-FTE conversion actually depend on at the six-month mark?"

---

## 7. Tonight — priority order

| # | Do this | Time |
|---|---|---|
| 1 | Add the **Gen AI line** and **kaggriculture** to the AI/ML resume, export, print | 30 min |
| 2 | **RAG section above** — read twice, then say the pipeline out loud from memory | 45 min |
| 3 | **LLM fundamentals + hallucination + temperature** | 25 min |
| 4 | Prepare your **one specific "AI got it wrong and I caught it"** story | 15 min |
| 5 | **GD positions** — pick your line on 3 topics, especially AI-in-travel | 25 min |
| 6 | Re-drill **complexity + brute-force→optimised** out loud (your known weak spot) | 30 min |
| 7 | Say the **intro** out loud five times | 15 min |
| 8 | Company facts — Monish Luthra, Rignesh Dave, cruise engine, 30+ cruise lines | 10 min |

**Sleep.** Round 2 is a group discussion and round 4 is an interview — both are communication
rounds, and tired people ramble.

---

Sources: [Odysseus Solutions](https://odysseussolutions.com/) · [Management team](https://www.odysseussolutions.com/our-management-team/) · [Careers](https://odysseussolutions.com/careers/) · [Glassdoor interview questions](https://www.glassdoor.co.in/Interview/Odysseus-Solutions-Interview-Questions-E1622386.htm) · [Glassdoor Vadodara reviews](https://www.glassdoor.com/Reviews/Odysseus-Solutions-Vadodara-Reviews-EI_IE1622386.0,18_IL.19,27_IM1089.htm) · [Tracxn profile](https://tracxn.com/d/companies/odysseus-solutions/__8NUMA30z5EjiNjPyQhrbjq7etubrgnLVj1hzIua7-9A) · [Enlyft tech stack](https://enlyft.com/tech/company/odysseussolutions.com)
