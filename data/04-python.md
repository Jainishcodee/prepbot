# Python

## Data structures ⭐

| | Syntax | Mutable | Ordered | Duplicates |
|---|---|---|---|---|
| **List** | `[]` | ✅ | ✅ | ✅ |
| **Tuple** | `()` | ❌ | ✅ | ✅ |
| **Set** | `set()` | ✅ | ❌ | ❌ |
| **Dict** | `{k:v}` | ✅ | ✅ (3.7+) | keys unique |

Tuples are faster and **hashable**, so they can be dict keys. Sets give O(1) membership tests.

**Immutable:** `int`, `float`, `str`, `tuple`, `bool`, `frozenset`, `bytes`.
**Mutable:** `list`, `dict`, `set`, most custom objects.

**⭐ Shallow vs deep copy** — `copy.copy()` makes a new outer object but **shares nested
references**; `copy.deepcopy()` recursively copies everything.

**The mutable default trap** — `def f(lst=[])` creates the list **once** at definition and it
persists across calls. Fix: `def f(lst=None): lst = lst or []`.

---

## Functions

**⭐ `*args` vs `**kwargs`** — `*args` collects extra **positional** args into a **tuple**;
`**kwargs` collects extra **keyword** args into a **dict**.

**⭐ Decorator** — a function that takes another function and returns an enhanced version, without
modifying the original. Applied with `@name`.
```python
def log(fn):
    def wrapper(*a, **kw):
        print("calling", fn.__name__)
        return fn(*a, **kw)
    return wrapper
```
Real uses: logging, timing, `functools.lru_cache`, auth checks, **FastAPI route decorators** —
which you now use in SFSync, so say that.

**Lambda** — a single-expression anonymous function, typically as `key=` to `sorted()`/`max()`.

**`map` / `filter` / `reduce`** — apply to every element / keep where truthy / fold to one value.

**Closure** — an inner function capturing variables from the enclosing scope, kept alive after the
outer function returns. `nonlocal` to modify.

---

## Generators ⭐

**`yield`** makes a function return a generator — it produces values **lazily**, one at a time,
pausing and resuming its state. Massively memory-efficient: you can stream a 10 GB log file line by
line without loading it into RAM.

**Generator expression vs list comprehension** — `[x*x for x in r]` builds the whole list;
`(x*x for x in r)` computes on demand, O(1) memory, single-pass, no indexing.

**Iterable vs iterator** — an **iterable** implements `__iter__()`; an **iterator** implements
`__iter__()` **and** `__next__()` and is consumed once.

---

## OOP

The four pillars are in `02-fundamentals.md` — they matter more there. Python specifics:

**`self`** — a reference to the current instance, passed explicitly as the first parameter.

**`__init__` vs `__new__`** — `__new__` **creates** the object; `__init__` **initializes** it. You
almost always only write `__init__`.

**Dunder methods** — `__init__`, `__str__` (user-facing), `__repr__` (developer/debug), `__len__`,
`__eq__`, `__add__`, `__iter__`, `__call__`. They enable operator overloading.

**`@staticmethod` vs `@classmethod`** — `@classmethod` takes `cls` (good for alternative
constructors); `@staticmethod` takes neither and is just a namespaced utility.

**MRO** — Method Resolution Order, the order Python searches classes under multiple inheritance,
computed by **C3 linearization**. `ClassName.__mro__`. It solves the diamond problem.

**`super()`** — calls the next class in the MRO, usually `super().__init__(...)`.

---

## Language semantics

**⭐ `is` vs `==`** — `==` compares **values** (`__eq__`); `is` compares **identity** — the same
object in memory. Use `is` only for `None`, `True`, `False`. *(Small ints −5..256 are interned,
which is why `a is b` sometimes surprisingly returns True.)*

**⭐ The GIL** — the Global Interpreter Lock, a mutex in **CPython** letting only **one thread
execute Python bytecode at a time**. It prevents true parallelism for **CPU-bound** threading.
Workarounds: `multiprocessing`, C extensions, `asyncio`. Threads are still fine for **I/O-bound**
work, because the GIL is released while waiting.

**Memory management** — a private heap with **reference counting** plus a **generational garbage
collector** to break reference cycles.

**Exceptions** — `try` / `except SpecificError as e` / `else` (no exception) / `finally` (always).
Never bare `except:`. Custom exceptions subclass `Exception`.

**Context manager / `with`** — guarantees setup and teardown even on exception. `with open(f) as
fh:` auto-closes. Implemented via `__enter__`/`__exit__` or `@contextlib.contextmanager`.

**`venv` + `pip`** — isolates project dependencies. `python -m venv .venv` → activate →
`pip install -r requirements.txt`. `pip freeze > requirements.txt`.

**PEP 8** — 4-space indents, `snake_case` functions/variables, `PascalCase` classes.

**`append` vs `extend`** — `append(x)` adds one element; `extend(it)` adds each element of an
iterable.

**`sort()` vs `sorted()`** — `list.sort()` sorts in place and returns `None`; `sorted(it)` returns a
new list and works on any iterable.

**`zip()` / `enumerate()`** — pair multiple iterables / yield `(index, value)`.

---

## Snippets to write cold

```python
s[::-1]                                   # reverse a string
s == s[::-1]                              # palindrome (after cleaning)
sorted(a) == sorted(b)                    # anagram
list(dict.fromkeys(lst))                  # dedupe, preserve order
sorted(set(lst))[-2]                      # second largest
max(set(s), key=s.count)                  # most frequent char
a, b = b, a                               # swap
Counter(text.lower().split())             # word count

a, b = 0, 1                               # fibonacci
for _ in range(n):
    print(a); a, b = b, a + b

def is_prime(n):                          # prime check
    if n < 2: return False
    return all(n % i for i in range(2, int(n**0.5) + 1))

seen = {}                                 # two sum, O(n)
for i, n in enumerate(nums):
    if target - n in seen: return [seen[target - n], i]
    seen[n] = i
```

---

## Talking about SFSync (tonight's build)

If they ask what you've done in Python, lead with this — it's a backend service, not a notebook:

> "I built a small FastAPI service that takes a spreadsheet upload, validates every row against a
> Pydantic schema, and pushes the valid rows to a downstream API in batches. The interesting parts
> were the failure modes: I didn't want one bad row to sink a 5,000-row upload, so invalid rows get
> collected into a per-row error report instead of raising. And when the downstream API returns 429
> or a 5xx, the batch retries with exponential backoff rather than being dropped."

**Then connect it:** *"I built it after reading what Wave and Fusion do — bulk spreadsheet edits
pushed into Salesforce under governor limits. I wanted to understand that shape of problem."*

**Be ready for:** why Pydantic over manual validation (declarative, typed, one place, automatic
error messages); why batching (fewer round trips, and API rate limits are per-request); why
exponential backoff (retrying immediately makes throttling worse — you back off to let the window
reset); what you'd add next (idempotency keys so a retry doesn't double-write, and a dead-letter
queue for permanently failed batches).
