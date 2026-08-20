# Angular

**Your anchor:** you contributed to `g:\Internship\Salesforce_admin_web\admin-website` — Angular
18.2, Angular Material + PrimeNG, 31 feature modules, 4 route guards, an HTTP interceptor, 6
injectable services, RxJS 7.8. Spend 15 minutes opening these files so you can speak from
something real:

- `src/app/app.config.ts` and `app.routes.ts` — standalone bootstrap and route table
- any `*.guard.ts` — how `CanActivate` blocks navigation
- `dms-auth.interceptor.ts` — how the token gets attached to every request
- `api.service.ts` / `auth.service.ts` — `@Injectable`, `HttpClient`, an RxJS pipe

**How to frame your depth, once, confidently:**
> "My deepest work is React and Flutter. I've worked inside a production Angular 18 codebase — I'm
> solid on the component/service/guard/interceptor model and RxJS, and the concepts map closely to
> what I do in React. I'd be productive quickly."

---

## Core

**What is Angular?** A TypeScript-based, component-driven SPA framework by Google. AngularJS (1.x)
was JavaScript with controllers and `$scope`; Angular 2+ uses components, hierarchical DI, and AOT.

**Component vs directive vs module** — a **component** is a directive *with a template*; a
**directive** adds behaviour to an existing element; an **NgModule** groups components, directives,
pipes and services.

**`@Component` metadata** — `selector`, `template`/`templateUrl`, `styles`/`styleUrls`, `providers`,
`standalone`, `imports`.

**⭐ Four types of data binding**
- **Interpolation** `{{ value }}` — component → view
- **Property** `[value]="x"` — component → view
- **Event** `(click)="fn()"` — view → component
- **Two-way** `[(ngModel)]="x"` — both; it's property binding + event binding combined

**⭐ Structural vs attribute directives** — **structural** change DOM layout, prefixed `*`:
`*ngIf`, `*ngFor`, `*ngSwitch`. **Attribute** change appearance/behaviour: `ngClass`, `ngStyle`,
`ngModel`. *(Angular 17+ has built-in `@if` / `@for` / `@switch` blocks instead.)*

**Why `trackBy` on `*ngFor`?** Without it Angular re-renders the whole list on any change. `trackBy`
returns a unique id so only changed rows re-render.

---

## Services & DI

**Why services?** Reusable business logic and data access shared across components. Keeps components
thin and logic testable.

**⭐ Dependency Injection** — a class *receives* its dependencies instead of creating them. Angular's
injector supplies instances; you declare them in the constructor:
`constructor(private http: HttpClient) {}`. Benefits: loose coupling, easy mocking, singletons.
*(This is the Dependency Inversion principle in SOLID — nice link to make.)*

**`@Injectable({ providedIn: 'root' })`** — registers the service on the root injector as an
app-wide singleton, and makes it **tree-shakable**.

**Sharing data between components** — parent→child `@Input()`; child→parent `@Output()` +
`EventEmitter`; unrelated components → a shared service with a `BehaviorSubject`.

---

## Lifecycle

**Order:** `ngOnChanges` → `ngOnInit` → `ngDoCheck` → `ngAfterContentInit` → `ngAfterContentChecked`
→ `ngAfterViewInit` → `ngAfterViewChecked` → `ngOnDestroy`.

**⭐ constructor vs `ngOnInit`** — the **constructor** is a TypeScript feature; use it **only for
DI**. **`ngOnInit`** runs after the first `ngOnChanges`, once `@Input()` values are set — put
initialization and API calls there.

**`ngOnDestroy`** — cleanup: **unsubscribe from Observables**, clear timers, remove listeners.

---

## RxJS

**⭐ Observable vs Promise**

| Observable | Promise |
|---|---|
| emits **many** values over time | resolves **once** |
| **lazy** — runs on `.subscribe()` | **eager** — runs immediately |
| **cancellable** via `unsubscribe()` | not cancellable |
| rich operators | `.then()` / `.catch()` only |

Angular's `HttpClient` returns Observables.

**Operators worth naming** — `map`, `filter`, `switchMap` (cancels the previous inner request —
perfect for typeahead search), `mergeMap`, `debounceTime`, `distinctUntilChanged`, `catchError`,
`takeUntil`, `tap`.

**Subject vs BehaviorSubject** — both are Observable *and* Observer. `BehaviorSubject` needs an
initial value and immediately emits the **current** value to new subscribers; a plain `Subject`
emits nothing until the next `next()`.

**Avoiding memory leaks** — the **`async` pipe** (auto-unsubscribes), `takeUntil(this.destroy$)`,
or `takeUntilDestroyed()` in Angular 16+.

---

## HTTP

**Calling an API** — inject `HttpClient`, call `this.http.get<T>(url)`, which returns an Observable.
Put the call in a **service**, not the component. Subscribe in the component or use the `async` pipe.

**⭐ HTTP Interceptor** — a service implementing `HttpInterceptor` that sits in the middle of every
request/response. Used for **attaching auth tokens**, global error handling, loading spinners,
logging, retries. *You have one in `admin-website` — say so.*

**Error handling** — `catchError` in the pipe, or globally in an interceptor; `retry(n)` before
failing.

---

## Forms

**⭐ Template-driven vs Reactive**

| Template-driven | Reactive |
|---|---|
| logic in the HTML (`ngModel`) | logic in TypeScript (`FormGroup`/`FormControl`) |
| `FormsModule` | `ReactiveFormsModule` |
| asynchronous, implicit | synchronous, explicit |
| simple forms | complex/dynamic forms, easier to unit test |

**Validation** — `new FormControl('', [Validators.required, Validators.email])`; check
`form.valid`, `control.errors`, `control.touched`. A custom validator is a function returning
`null` or an error object.

---

## Routing

**How it works** — a `Routes` array maps `path` → `component`, registered via `provideRouter()` or
`RouterModule.forRoot()`, rendered into `<router-outlet>`. Navigate with `routerLink` or
`Router.navigate()`.

**Route params** — inject `ActivatedRoute`; `this.route.snapshot.paramMap.get('id')` for one-time,
or subscribe to `this.route.paramMap` to react to changes on the same route.

**⭐ Lazy loading** — load a feature only when its route is hit:
`loadChildren: () => import('./x/x.routes').then(m => m.routes)`. Cuts initial bundle size.

**⭐ Route guards** — run before navigation. `CanActivate` (auth), `CanDeactivate` (unsaved changes),
`Resolve` (prefetch), `CanMatch`. *`admin-website` has four — `auth.guard.ts`,
`super-admin.guard.ts`, `dms-auth.guard.ts`, `dms-v2-auth.guard.ts`.*

> **Strong connection to make:** *"The four guards in that Angular app are the same pattern as the
> four route guards in my own CRM — ProtectedRoute, AdminRoute, SuperAdminRoute, PublicOnlyRoute.
> Different framework, identical idea."*

---

## Pipes, change detection, compilation

**Pipe** — transforms data in the template: `{{ date | date:'short' }}`. **Pure** pipes (default)
re-run only when the input **reference** changes. **Impure** pipes run every change-detection cycle
— expensive; the `async` pipe is impure.

**Custom pipe** — `@Pipe({name:'myPipe'})` implementing `PipeTransform.transform()`.

**⭐ Change detection — Default vs OnPush** — Default checks the whole component tree every cycle.
**OnPush** re-checks only when an `@Input` **reference** changes, an event fires inside the
component, or an `async` pipe emits. Major performance lever.

**AOT vs JIT** — **AOT** compiles templates at **build time**: smaller bundles, faster rendering,
template errors caught early — the production default. **JIT** compiles in the browser at runtime.

**Ivy** — Angular's rendering/compilation engine since v9; better tree-shaking, smaller bundles.

**ViewEncapsulation** — `Emulated` (default, scopes CSS via attributes), `None` (global),
`ShadowDom` (native).

---

## Modern Angular — bonus, not expected of you

**Standalone components** — `standalone: true`, imports its own dependencies, no NgModule needed.
Default from Angular 19.

**Signals** (16+) — a reactive primitive: `signal()`, `computed()`, `effect()`. Fine-grained
reactivity without zone.js. **Signals for synchronous local state; RxJS for async streams.**

**New control flow** (17+) — `@if`, `@for (item of items; track item.id)`, `@switch`, `@defer`.

---

## ⭐ The ValorX-specific Angular question

They will likely probe performance, because their product renders spreadsheet grids over thousands
of Salesforce records. If rendering large data comes up:

> "For a grid that size I wouldn't render every row — I'd use virtual scrolling, so only the visible
> window plus a buffer is in the DOM. Beyond that: `OnPush` change detection so the grid doesn't
> re-check on unrelated events, `trackBy` so edits don't re-render the whole list, and on the data
> side, paginate or batch server-side rather than pulling everything at once."

That answer lands directly on what they build.
