# Fundamentals — this is what ValorX actually tests

Verified from Glassdoor interview reports, ValorX Ahmedabad: their rounds cover **OOP, simple DSA,
DBMS/SQL, and JavaScript**. Difficulty 2.8/5. **Study this file before anything else.**

---

# 1. OOP — asked in essentially every round

**The four pillars** — have a one-line example for each from your own code:

- **Encapsulation** — bundle data with the methods that act on it, and restrict direct access.
  *"My `leadsAPI` module wraps all Firestore access for leads. Components never touch the database
  directly — they call `leadsAPI.update()`. If I change the storage layer, nothing above it breaks."*
- **Abstraction** — expose *what* something does, hide *how*.
  *"My `useLeads()` hook returns leads and a loading flag. The caller has no idea there's a realtime
  listener, a query builder and role filtering underneath."*
- **Inheritance** — a child class reuses and extends a parent. `class Dog(Animal)`.
- **Polymorphism** — one interface, many implementations. Same call, different behaviour by type.

**Overloading vs overriding**
- **Overriding** — subclass redefines a parent method, same signature. **Runtime** polymorphism.
- **Overloading** — same name, different parameters. **Compile-time** polymorphism. Python doesn't
  truly support it; you simulate with default args or `functools.singledispatch`.

**Abstract class vs interface** — an abstract class can hold state and partial implementation, and
a class extends one; an interface is a pure contract and a class can implement many.

**SOLID** — ValorX job ads name this explicitly:
- **S**ingle Responsibility — one reason to change
- **O**pen/Closed — open for extension, closed for modification
- **L**iskov Substitution — a subtype must be usable anywhere its base type is
- **I**nterface Segregation — many small interfaces beat one fat one
- **D**ependency Inversion — depend on abstractions, not concretions. *This is exactly why Angular
  has dependency injection* — good line to drop.

---

# 2. SQL / DBMS — tested in BOTH their technical rounds

### JOINs
- **INNER** — only rows matching in both tables
- **LEFT** — all rows from the left, plus matches; NULLs where there's no match
- **RIGHT** — mirror of LEFT
- **FULL OUTER** — everything from both sides
- **CROSS** — cartesian product
- **SELF** — a table joined to itself (employee → manager)

### DELETE vs TRUNCATE vs DROP ⭐

| | DELETE | TRUNCATE | DROP |
|---|---|---|---|
| Type | **DML** | **DDL** | **DDL** |
| Removes | rows, with `WHERE` | **all** rows | table **+ structure** |
| Rollback | ✅ | ❌ | ❌ |
| Speed | slow, logs each row | **fast**, deallocates pages | fast |
| Fires triggers | ✅ | ❌ | ❌ |
| Resets identity | ❌ | ✅ | n/a |

### Keys
- **Primary key** — uniquely identifies a row, **not null**, **one per table**.
- **Foreign key** — references a PK in another table, enforces **referential integrity**, can be
  null, can repeat.
- **Unique key** — enforces uniqueness but **allows one NULL**, and you can have many per table.

### Normalization
Reducing redundancy to avoid insert/update/delete anomalies.
- **1NF** — atomic values, no repeating groups
- **2NF** — 1NF + no **partial** dependency on part of a composite key
- **3NF** — 2NF + no **transitive** dependency (non-key depending on another non-key)
- **Denormalization** — deliberately adding redundancy back to speed up reads

*Your QuickCourt six-table schema is a live example — use it as your answer.*

### Indexes
A **B-tree** structure that speeds lookups, like a book's index.
- **Clustered** — determines the **physical row order**; **one per table** (usually the PK)
- **Non-clustered** — separate structure with pointers; many allowed
- **Trade-off** — faster `SELECT`, **slower INSERT/UPDATE/DELETE**, extra storage

### ACID
**A**tomicity (all-or-nothing) · **C**onsistency (valid state to valid state) ·
**I**solation (concurrent transactions don't interfere) · **D**urability (committed survives crash)

### WHERE vs HAVING
`WHERE` filters **rows before** grouping, can't use aggregates. `HAVING` filters **groups after**
`GROUP BY`, can use aggregates.

### DDL / DML / DCL / TCL
CREATE-ALTER-DROP-TRUNCATE / SELECT-INSERT-UPDATE-DELETE / GRANT-REVOKE / COMMIT-ROLLBACK-SAVEPOINT

### ⭐ Queries to be able to write cold

```sql
-- Second highest salary
SELECT MAX(salary) FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- Nth highest
SELECT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) rk FROM employees
) t WHERE rk = N;

-- Find duplicates
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
```

**⭐ The question ValorX actually asked** — given employee numbers `1, 3, 7, 9`, return `2,4,5,6,8`:

```sql
WITH nums AS (
  SELECT 1 AS n
  UNION ALL SELECT n+1 FROM nums WHERE n < (SELECT MAX(emp_no) FROM employees)
)
SELECT n FROM nums
WHERE n NOT IN (SELECT emp_no FROM employees)
OPTION (MAXRECURSION 0);
```

**If you blank, say the idea out loud:** *"I'd generate the full number series from 1 to the max,
then anti-join it against the table — LEFT JOIN and keep rows where the table side is NULL."*
Stating the approach scores most of the marks.

---

# 3. JavaScript — verified in their technical round

**`var` vs `let` vs `const`** — `var` is function-scoped and hoisted as `undefined`; `let`/`const`
are block-scoped and in the temporal dead zone until declared. `const` can't be **reassigned**, but
an object's contents can still be mutated.

**`==` vs `===`** — `==` coerces types (`'5' == 5` is true); `===` compares value **and** type.
Always use `===`.

**Closure** — a function that remembers its outer lexical scope even after the outer function has
returned.
```js
function counter(){ let c = 0; return () => ++c; }
const inc = counter(); inc(); // 1 — `c` survives
```

**Hoisting** — declarations move to the top of scope at compile time. `var` and function
declarations are hoisted; `let`/`const` are hoisted but uninitialized (TDZ → ReferenceError).

**Event loop** — one call stack. Async work goes to Web APIs; finished callbacks queue up; the
event loop moves them onto the stack when it's empty. **Microtasks (Promises) run before macrotasks
(setTimeout).**

**`this`** — depends on *how the function is called*. Method call → the object. `new` → the
instance. **Arrow functions have no own `this`** — they inherit it lexically.

**`null` vs `undefined`** — `undefined` = never assigned (JS's default). `null` = deliberately
empty. `typeof null` is `"object"` — a famous language bug.

**map / forEach / filter / reduce** — `map` returns a new transformed array; `forEach` returns
undefined (side effects only); `filter` returns items passing a test; `reduce` folds to one value.

**Shallow vs deep copy** — `{...obj}` shares nested references; `structuredClone(obj)` is a true
deep copy.

**Why TypeScript?** — static typing catches errors at compile time, better tooling, interfaces and
generics, compiles to plain JS.

---

# 4. OS / Networking — lighter, but asked

**Process vs thread** — a process has its **own memory space**, expensive to switch, crash-isolated.
A thread lives inside a process and **shares heap memory** with siblings (own stack/registers),
cheap to switch, but shared state needs synchronization.

**Deadlock** — four Coffman conditions: mutual exclusion, hold and wait, no preemption, circular
wait. Break any one to prevent it.

**Mutex vs semaphore** — a mutex is a lock owned by one thread; a semaphore is a counter allowing N
concurrent accesses, with no ownership.

**TCP vs UDP** — TCP is connection-oriented, reliable, ordered, slower. UDP is connectionless,
unreliable, fast (streaming, DNS, gaming).

**HTTP codes** — 200 OK · 201 Created · 301 Moved · 400 Bad Request · 401 Unauthorized ·
403 Forbidden · 404 Not Found · **429 Too Many Requests** · 500 Server Error.
*(429 matters — it's what your SFSync retry logic handles.)*

**REST** — stateless, resource-based URLs, standard verbs (GET/POST/PUT/PATCH/DELETE), usually JSON.
**GET** retrieves, params in URL, idempotent and cacheable. **POST** sends a body, not idempotent.

**Git** — clone, add, commit, push, pull, branch, checkout, merge, rebase, stash. **Merge vs
rebase:** merge keeps history with a merge commit; rebase replays commits for a linear history.

---

# 5. DSA — "simple DSA" per their own reports

Easy to easy-medium. You do **not** need hard problems.

**Hand-write these four on paper tonight** — no IDE:

```python
# Palindrome
def is_pal(s):
    s = ''.join(c.lower() for c in s if c.isalnum())
    return s == s[::-1]

# Two Sum — O(n) with a hashmap
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return [seen[target - n], i]
        seen[n] = i

# Reverse a string in place — two pointers
def rev(a):
    i, j = 0, len(a) - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i, j = i + 1, j - 1
    return a

# Character frequency
from collections import Counter
def freq(s): return Counter(s)
```

**Also know the shape of:** missing number (`n(n+1)/2 - sum`), first non-repeating char, valid
parentheses (stack), binary search, merge two sorted arrays, reverse a linked list (prev/curr/next).

**Complexities to state unprompted:** hashmap lookup O(1) avg · binary search O(log n) ·
merge sort O(n log n) stable, O(n) space · quick sort O(n log n) avg / O(n²) worst, in-place.

**Array vs linked list** — array: contiguous, O(1) random access, O(n) insert/delete. Linked list:
O(n) access, O(1) insert/delete given the node.

**Stack vs queue** — LIFO (undo, call stack) vs FIFO (BFS, scheduling).

**Behaviour in the coding round, in order:**
1. Repeat the question back; state your assumptions
2. Say the brute force **and its complexity** first
3. *Then* improve it — "but I can do this in O(n) with a hashmap"
4. Narrate while you write. Silence is what fails people.
5. Dry-run on a small example before saying "done"
6. Name edge cases: empty, single element, all duplicates, negatives
