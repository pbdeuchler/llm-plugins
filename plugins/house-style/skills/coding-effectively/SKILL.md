---
name: coding-effectively
description: ALWAYS use before any implementation work or planning: designing, writing, editing, refactoring, debugging, or generating source code, tests, scripts, config-as-code, or behavior-affecting files. This is a baseline engineering skill and should be invoked even when a more specific language, framework, testing, or database skill also applies.
---

# Coding Effectively

## Required Sub-Skills

**ALWAYS REQUIRED:**

- `defense-in-depth` - Validate at every layer data passes through

**CONDITIONAL:** Use these sub-skills when applicable:

- `howto-develop-with-postgres` - PostgreSQL database code
- `writing-good-tests` - Writing or reviewing tests
- `property-based-testing` - Tests for serialization, validation, normalization, pure functions

## Thinking About Dependencies

#### A working guide to dependencies-as-parameters — practiced, not preached

Currying, dependency injection, and interfaces are one move: **turn a hidden coupling into an explicit parameter, give it the narrowest useful type, and bind it as late as the budget allows.** This guide is about doing that _successfully_, which means knowing when **not** to.

The first principle is economic, not moral: **every seam costs indirection** — a cognitive hop for the reader and often a dispatch for the machine. So the default is **concrete**, and you buy a seam only when it pays rent. "Program to an interface" is advice, not a commandment; applied dogmatically it produces codebases that are abstract everywhere and flexible nowhere.

---

### What a good seam buys you

A unit whose dependencies are all parameters is a **pure function**: output determined by input, nothing else. That single property gives you everything downstream — it's testable (pass a different value), reasoned-about (substitute equals for equals), and swappable (the boundary varies independently of the core). The goal is always the same shape: **determinism in the middle, substitutability at the edge.**

You do not get that shape by abstracting everything. You get it by abstracting the _right_ things and leaving the rest concrete.

---

### When to add a seam

Add one only when the dependency has a **real axis of variation**. In practice that's a short list:

| Add a seam                                                                                  | Because                                                                                                                |
| ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **Nondeterminism** — clock, randomness, UUIDs                                               | The real value is uncontrollable; a parameter makes the unit deterministic and testable.                               |
| **I/O & external systems** — DB, network, filesystem, queues                                | This is your **failure/latency boundary** — the seam lets you inject retries, breakers, timeouts, and fault injectors. |
| **Genuine deployment variation** — payment provider, storage backend, config, feature flags | More than one implementation actually ships or is imminent.                                                            |

That's roughly it. Note the unifying trait: each is **nondeterministic, effectful, external, or genuinely plural.** If a dependency is none of those, it does not need a seam.

---

### When _not_ to — the anti-dogma rules

1. **Don't abstract pure logic.** A pure function or value object has no axis of variation. Don't inject your data structures; just call the function and `new` the value.
2. **One permanent implementation = no interface.** An interface with a single forever-implementation is pure indirection. Delete it and use the concrete type. The interface is noise the reader has to trace through to discover there was never a choice.
3. **Apply the rule of three.** Two call sites isn't a pattern. Wait for the third real case before extracting the abstraction — _unless_ the dependency is on the list above, where the test fake is a guaranteed second case and justifies the seam immediately. (That exception is the whole reason `Clock` is worth it and `UserNameFormatter` isn't.)
4. **Reach for the language feature before the framework.** A runtime DI container with reflection is a re-implementation of function application. If passing an argument works, pass an argument. Containers move "is this wired correctly?" from compile time to startup time — or to the first request that hits the cold path.
5. **Don't inject the world.** A dependency typed as `System` (touches everything) is explicit but useless — the type no longer bounds the blast radius. Inject the _capability_, not the container.
6. **Collapsing a premature abstraction is normal maintenance.** Abstractions aren't sacred. If a seam never flexed, inline it. Backing out is cheaper than the standing tax.

---

### How to do it well when you do

- **Narrow the contract to a capability.** `() => number`, not `Clock`, when all you need is the time. `Clock`, not `System`, when you need a small set of related operations. The type should be a manifest of exactly what the unit can touch — and therefore a guarantee of what it _can't_.
- **The consumer owns the interface.** Define the port on the high-level side, shaped to what the policy needs; let the low-level module implement it. Don't import the provider's surface. This is what makes the dependency arrow point _inward_ toward stable policy instead of outward toward volatile detail.
- **Wire in one boring function.** Construct the graph explicitly at the top of the program (constructor injection / explicit `main`), where a human can read the whole thing at a glance. No magic, no scanning, no annotations resolved at runtime.
- **Keep the core pure; push effects to the edge.** The deterministic middle is where logic, tests, and (if you ever need it) proofs live. I/O lives in a thin shell around it.
- **Bind early on hot paths.** A seam you kept for testing can be specialized away in production via partial application or monomorphization/devirtualization. Keep the flexibility at the source level; pay nothing for it at runtime where it matters.

---

### Worked examples

**Nondeterminism — and notice the seam is a plain parameter, not an interface.**

```ts
// Hidden dependency on the wall clock: nondeterministic, untestable.
function isExpired(token: Token): boolean {
  return token.expiresAt < Date.now();
}

// The clock is now an input. Deterministic, trivially testable, zero ceremony.
function isExpired(token: Token, now: number): boolean {
  return token.expiresAt < now;
}
```

You needed a number, so you passed a number. Reach for an `interface` only when the dependency has _behavior_ worth faking (several methods, state, real swap). Not everything that gets injected deserves a type with a name.

**Over-abstraction — the seam that buys nothing.**

```ts
// Speculative: one implementation, no axis of variation, wired through a container.
interface UserNameFormatter {
  format(u: User): string;
}
class DefaultUserNameFormatter implements UserNameFormatter {
  format(u: User) {
    return `${u.first} ${u.last}`;
  }
}

// It was always just a function.
const formatUserName = (u: User) => `${u.first} ${u.last}`;
```

**Inject the capability, not the world.**

```ts
// `system` can reach the clock, the filesystem, the network, env... blast radius = everything.
class Report {
  constructor(private system: System) {}
  build() {
    const t = this.system.clock.now(); /* ... */
  }
}

// The type now tells you the entire surface this class can touch.
class Report {
  constructor(private now: () => number) {}
  build() {
    const t = this.now(); /* ... */
  }
}
```

---

### Pre-commit checklist

- Is this dependency **nondeterministic, effectful, external, or genuinely plural**? If no → call it directly, don't abstract it.
- Does the seam have a **real second case**? (A test fake counts only when the real dependency is one of the above.) If no → rule of three; wait.
- Is the contract the **narrowest capability** that does the job? (`() => number` over `Clock`; `Clock` over `System`.)
- Did the **consumer** define the interface to fit its need, or did you import the provider's surface?
- Can you read the **entire wiring graph in one function**, with no framework?
- Is the **core pure**, with effects pushed to the boundary?
- On a hot path, can you **bind early** after keeping the seam for tests?
- Does every existing abstraction still **flex**? If one never has, collapse it.

---

> **North star.** Default to concrete. Add a seam when a dependency is nondeterministic, effectful, external, or genuinely varies — give it the narrowest type that does the job, wire it in plain code, and keep the core pure. Abstractions are bought with indirection; make each one pay rent. Everything called "good design" — testable, readable, swappable, provable — falls out of that one discipline, applied with judgment rather than reflex.

## Writing Good Code with Types, Invariants, and Classes

#### A practical, non-dogmatic guide

**The one idea.** A _type_ is a predicate over values, an _invariant_ a predicate over states, a _class_ the machinery that establishes and preserves an invariant by owning every door into its state. All three separate valid from invalid and keep you in the valid region _inductively_: establish the property at a boundary, preserve it under every permitted operation, and then assume it everywhere else for free. That "assume it for free" is the prize — it's where readable, testable, low-bug code comes from, because it lets every other line reason **locally**.

This guide is about applying that idea with judgment. The principles are a gradient of effort, not a set of commandments. The goal is correctness you can afford, not maximal encoding. Most of the wins come from the cheapest rungs; the expensive ones are for code that has earned them.

---

### The workflow: six moves

1. **Name the invariant precisely.** Before building an abstraction, state what must always be true — in words. If you can't name one, you don't have an abstraction yet; you have a data structure, and that's fine — call it that.
2. **Find the boundary where validity enters.** Parse points, constructors, deserialization, the network edge, the FFI seam. This is where the predicate gets checked. Everything past it should be able to trust the result.
3. **Pick the cheapest enforcement that's actually adequate** (see the cost ladder). Default low; climb only when the invariant is load-bearing and realistically gets violated.
4. **Make the signatures honest.** Shape the types so a caller _cannot express_ the invalid call, or so the failure mode is visible in the return type. Stop functions from lying about their domain.
5. **Keep operations closed over the valid set.** If `insert` on a sorted structure returns a sorted structure, callers compose without re-checking. Closure is what lets you avoid re-validation.
6. **Test the boundary and the preservation.** Exhaustively test the one door; property-test that operations keep the invariant. That's the inductive step run as an experiment.

---

### The toolbox

**Make illegal states unrepresentable** — _when the distinction drives behavior._
Replace flag soup with a sum type. `bool loading; bool error; T? data` (which permits nonsense like loading-and-errored) becomes `Loading | Failed(e) | Loaded(data)`. Use distinct newtypes for things that shouldn't mix (`UserId` vs `OrderId`, not both `string`). Use `NonEmptyList`, `NonZero`, `Positive` so the empty/zero/negative case is gone from the body rather than guarded in it.

**Parse, don't validate** — _at every point where untrusted shape becomes trusted shape._
A validator returns `bool` and throws the knowledge away; a parser returns the refined type and keeps it. `parseEmail(s) -> Option<Email>`; then everything downstream takes `Email`, never re-checking a raw `string`. The type is the proof the check happened.

**Smart constructors** — _when the type system can't express the invariant._
Sorted, balanced, in-range-across-fields, summing-to-100 — make the raw constructor private, expose one factory that establishes and asserts the invariant. One door, checked once.

**Encapsulate for the invariant, not reflexively.**
Hide exactly what protects the invariant; expose the rest plainly. A class with a getter and setter for every field protects nothing — it's a struct wearing a disguise, and a plain record is more honest and more readable.

**Assertions for the un-typeable.**
For invariants the language won't carry, `assert`/`debug_assert` at construction and after mutation. Executable documentation that fails near the cause. Cheap, removable in release, invaluable in debug.

**Closure and total functions.**
Prefer operations that return the same refined type. Make partiality explicit with `Result`/`Option` rather than throwing — but only when you actually handle it; a swallowed error is a lie wearing an honest type's clothes.

**At trust and process boundaries.**
Validate untrusted input **once** at the edge, convert to trusted types, trust within. For invariants that span processes, you have no shared memory and no atomic method call — design for **idempotency, monotonicity, and commutativity** (CRDTs are the clean version: convergence preserved by construction). Don't pretend a class invariant crosses the network.

---

### The cost ladder

Spend the _least_ that's adequate. Climb only when stakes and violation-likelihood justify it.

| Rung | Mechanism                                 | Use when                                                                                                                |
| ---- | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 1    | **Unrepresentable** (types)               | The invariant is cheap to encode and the language carries it naturally. Best ROI when it fits.                          |
| 2    | **Enforced at one constructor / parser**  | Can't be static, but there's a natural single entry point.                                                              |
| 3    | **Asserted + property-tested**            | No clean static or constructor enforcement; you want it caught in CI and debug builds.                                  |
| 4    | **Documented + tested at the chokepoint** | Spans systems you don't own (distributed, third-party, eventual consistency). Name the limit of the guarantee honestly. |

Climbing past the rung an invariant deserves is itself a defect: it costs compile time, comprehension, and hiring, and it buries the load-bearing constraints under ceremony.

---

### Staying non-dogmatic

These are the ways the discipline turns against itself. Watch for them.

- **Match effort to stakes.** A throwaway script, a prototype, glue code: a comment and an assert is often the entire correct answer. Don't build a refinement-type cathedral around code that won't outlive the week.
- **The encoding can cost more than the bug.** If making a state unrepresentable demands GADTs, dependent types, or three layers of generics, weigh the next reader's comprehension and your team's reality against the bug you're preventing. A `// INVARIANT:` plus an assert plus a focused test is sometimes _more_ readable and just as safe. Clever types carry the same liability as clever anything.
- **Don't validate everywhere — validate at the boundary.** Defensive checks in every layer are the _opposite_ of this discipline: they announce that you don't trust your own types. Each redundant check can rot and diverge. Validate once; trust within. (Real trust boundaries are the exception, not the rule.)
- **Encode distinctions that matter to behavior, not every distinction that exists.** Minting a separate type for every conceptual nuance fragments code into near-identical types and conversion boilerplate. If two states are interchangeable for all current callers, one type is correct.
- **Anemic encapsulation is fake encapsulation.** No invariant, no reason to hide the representation. Reach for a plain data structure and stop apologizing for it.
- **"Total" can still be dishonest.** Returning a default to dodge a throw, or dropping errors into an ignored `Result`, hides failure rather than handling it. Honest means the signature tells the truth about _how_ it fails, not that it never does.
- **Some invariants are genuinely non-local — say so.** A type can't guarantee what the runtime can violate across services. Enforce at the chokepoint, document the edge of the guarantee, test the protocol. Pretending otherwise is worse than admitting it.
- **Refactor toward this; don't rewrite for it.** Tighten the highest-traffic, highest-risk boundary first — the parser, the public constructor, the recurring bug. Let everything else stay until it earns the change.
- **Friction is information.** If the language fights you at every turn to encode an invariant, don't power through on principle. Maybe the invariant is wrong, the boundary is misplaced, or this isn't the layer to encode it. Listen before you reach for type gymnastics.

---

### Quick decision heuristics

- _Can a caller construct an invalid value, and would that matter?_ → If yes, close the door (rung 1 or 2).
- _Am I checking the same thing in three places?_ → Push it to one boundary and carry a type past it.
- _Does this type's name promise something its operations can break?_ → Enforce it, or rename it to stop lying.
- _Type, or comment-plus-assert?_ → Pick whichever the next engineer reads faster. Both are legitimate.
- _What breaks if a message is duplicated, reordered, or lost?_ → Design for idempotency/monotonicity, not for walls that don't exist across the network.
- _Load-bearing or throwaway?_ → Calibrate everything above to the answer.

---

### Checklist

- [ ] I can state this abstraction's invariant in one sentence (or I've admitted it's just data).
- [ ] There is a single boundary where invalid input becomes a valid, typed value.
- [ ] Past that boundary, nothing re-validates what the type already guarantees.
- [ ] Signatures exclude invalid inputs or make failure visible in the return type.
- [ ] Operations are closed over the valid set, or the gap is asserted and tested.
- [ ] I chose the lowest adequate rung on the cost ladder, not the fanciest.
- [ ] Cross-process invariants are handled as protocols, with the guarantee's limits documented.
- [ ] The boundary is exhaustively tested; preservation is property-tested.
- [ ] I removed redundant defensive checks that exist only because I didn't trust my own types.

> **In one line:** find the invariant, establish it at one door, keep every operation from breaking it, let the rest of the program assume it for free — and spend no more than the invariant is worth.

## A Working Guide to State, Effects, and Honest Interfaces

How to use functional discipline to write good code — and how to know when to stop applying it.

The point of all of this is not purity. It is **honesty about state and effects, kept local**. You reach for each practice below because it removes more complexity than it adds. When it stops doing that, you stop. Every rule here ships with the condition under which you break it.

---

### The one operating principle

Make the hidden dependencies in your code — mutation, failure, absence, I/O, time — **explicit and local**. A function should be honest about what it touches, and what it touches should be as small as possible. Everything else is tactics.

The dogma trap is treating "pure" as the goal. The goal is _reasoning_ — yours, the next person's, and the compiler's. Spend discipline where reasoning pays off (concurrency, security boundaries, money, the long-lived core domain) and relax it where it doesn't (scripts, glue, prototypes, hot inner loops behind a clean interface).

---

### 1. Put failure and absence in the type

**Do it:** Expected, recoverable failure returns `Result<T, E>`. Possible absence returns `Option<T>`. The caller is forced to confront both at compile time instead of discovering them in production.

```rust
fn charge(account: &Account, cents: u64) -> Result<Receipt, ChargeError>;
//                                          ^ the contract names what can go wrong
```

**Relax it when:**

- The failure is a _bug_, not a domain outcome. Invariant violations should panic/throw, not return `Result`. Don't make callers handle "this can't happen."
- Wrapping adds no information. If nothing can fail, don't return `Result<T, Infallible>` to look consistent.
- An `Option` would propagate ten layers unchanged — supply a default at the boundary and pass the plain value inward.

**Smell:** a signature that lies — returns `T` but throws, or claims to be infallible while reading a mutable global.

---

### 2. Errors as values vs. exceptions — the dividing line

The test is one question: **will the caller do something different because of this?**

- **Yes → value.** Insufficient funds, parse failure, not-found. Part of the domain. Make it a `Result`/`Option`.
- **No → throw/panic.** Out of memory, broken invariant, programmer error. Unrecoverable. Crashing loudly beats limping on with corrupt state.

**Relax it when:** you're at a top-level boundary — a request handler, a CLI `main`, a job runner. Collapsing many possible failures into one error boundary there is fine; you don't need to thread `Result` through code whose only response is "log it and return 500." Push the ceremony to where decisions actually branch.

---

### 3. Functional core, imperative shell

**Do it:** Computation and decisions live in a pure core that takes data and returns data. I/O lives in a thin shell that feeds the core and performs whatever the core decided.

```rust
// core: pure, returns a description of what to do — trivially testable
fn plan(order: &Order, inventory: &Inventory) -> Vec<Command> { /* ... */ }

// shell: performs the effects, holds the danger, stays thin
for cmd in plan(&order, &inventory) {
    execute(cmd)?; // the only place that touches the world
}
```

This is the highest-leverage pattern here: the core needs no mocks, and the effects are concentrated where you can watch them.

**Relax it when:** the program _is_ mostly effects (an ETL job, a device driver, a streaming pipeline). The shell can be thick when the domain is genuinely effectful. Don't contort an inherently stateful thing — a parser, a connection pool, an allocator — into a pure shape it doesn't want. A stateful object with a clean interface is sometimes the honest model.

---

### 4. Immutable by default — but mutation isn't the sin

The sin is **shared, observable** mutable state, not mutation itself. A local mutation that no caller can observe is still referentially transparent.

```rust
fn checksum(bytes: &[u8]) -> u32 {
    let mut acc = 0u32;             // local mutation, invisible outside
    for &b in bytes { acc = acc.wrapping_mul(31).wrapping_add(b as u32); }
    acc                            // caller sees a pure function
}
```

**Do it:** Default to immutable values and transformations. Share nothing across threads/modules by default.

**Relax it when:** you're in a hot path. Mutate a local buffer or accumulator, reuse allocations, avoid building a fresh collection per element — all fine, provided the mutation stays inside the function and the interface stays honest. Persistent data structures are a tool, not a tax you must always pay.

---

### 5. Make illegal states unrepresentable; parse, don't validate

**Do it:** Encode invariants in types so wrong states won't compile. Parse untrusted input _once_, at the boundary, into a precise type that carries the proof inward.

```rust
struct Email(String);
impl Email {
    fn parse(s: &str) -> Result<Email, EmailError> { /* validate once */ }
}
// everything downstream takes Email, never re-checks a raw &str
```

Prefer sum types over flag soup (`enum State` beats three correlated `bool`s), and `NonEmpty<T>` over "a Vec that must not be empty, see comment."

**Relax it when:** the type costs more than the bug it prevents. A 30-line script doesn't need a type lattice. Some invariants are cheaper as a runtime check in one smart constructor than as a type-level proof. Stop when the types get harder to read than the rule they encode.

**Smell:** the same validation repeated at many call sites; boolean-blind parameters; comments saying "this string is really a path / JSON / an ID."

---

### 6. Encapsulate at the interface: disclose the effect, hide the mechanism

**Do it:** A public contract tells the truth about _what_ it does — can it fail, does it do I/O — and nothing about _how_. The interface can be pure even when the implementation mutates a local arena.

**Relax it when:** the caller needs to control the mechanism. If latency, ordering, or batching matters to the caller, hiding it is the _wrong_ encapsulation — you've concealed what matters and exposed what doesn't. And don't build an abstraction boundary around something with one caller; that's ceremony, not design.

---

### 7. Compose with the uniform interface — but don't build towers

`?`, `flatMap`, and do-notation let you chain context-carrying computations and refactor the pipeline fearlessly; the monad laws are why the refactor is safe.

**Relax it when:** the abstraction is harder to read than the code it abstracts. Deep monad-transformer stacks and six-layer effect towers are a smell. Flatten them: a concrete application type, a small effect enum, or language-level effects/async beats a generic tower nobody on the team can read. Generality that isn't used is just cost.

---

### 8. Test the core directly; concentrate the rest at the seam

**Do it:** Unit-test the pure core with plain values and property tests over invariants. Integration-test the thin shell where it meets the world.

**Relax it / read the signal:** if testing the core requires mocking the universe, the effects have leaked into the core. The fix is the design, not more mocks — pull the I/O back out to the shell. A handful of real integration tests at the seam beat a hundred brittle mock-heavy ones.

---

### 9. Know the taxes, and choose where to pay them

Every practice here has a cost: async colors every caller, immutability allocates, effect towers obscure, and all of it loads the team's working memory. None of that means don't do it — it means **spend it deliberately**.

- **Pay it** at concurrency boundaries, security/trust boundaries, anything handling money, and the core domain you'll maintain for years.
- **Skip it** in throwaway scripts, prototypes, one-shot glue, and perf-critical inner loops (behind a clean interface).

---

### Field rules

- Make effects honest; make state local; reach for machinery only when it removes more complexity than it adds.
- Failure the caller handles → value. Failure that's a bug → crash.
- Big pure core, thin honest shell. If the core needs mocks, it isn't pure yet.
- Mutate freely where no one can observe it; never share mutable state by default.
- Parse untrusted input once into a precise type; let the type carry the proof.
- Disclose what a function does; hide how it does it — unless the how is what the caller must control.
- If the abstraction is harder to read than the thing, delete the abstraction.

The mature version of this discipline doesn't look maximally functional. It looks **honest**: minimal effects, kept at the edges, around a core you can actually reason about — and pragmatic mutation everywhere that honesty isn't at stake.

## Property-Driven Design

When designing features, think about properties upfront. This surfaces design gaps early.

**Discovery questions:**

| Question                               | Property Type  | Example                        |
| -------------------------------------- | -------------- | ------------------------------ |
| Does it have an inverse operation?     | Roundtrip      | `decode(encode(x)) == x`       |
| Is applying it twice the same as once? | Idempotence    | `f(f(x)) == f(x)`              |
| What quantities are preserved?         | Invariants     | Length, sum, count unchanged   |
| Is order of arguments irrelevant?      | Commutativity  | `f(a, b) == f(b, a)`           |
| Can operations be regrouped?           | Associativity  | `f(f(a,b), c) == f(a, f(b,c))` |
| Is there a neutral element?            | Identity       | `f(x, 0) == x`                 |
| Is there a reference implementation?   | Oracle         | `new(x) == old(x)`             |
| Can output be easily verified?         | Easy to verify | `is_sorted(sort(x))`           |

**Common design questions these reveal:**

- "What about deleted/deactivated entities?"
- "Case-sensitive or not?"
- "Stable sort or not? Tie-breaking rules?"
- "Which algorithm? Configurable?"

Surface these during design, not during debugging.

## Core Engineering Principles

### Correctness Over Convenience

Model the full error space. No shortcuts.

- Handle all edge cases: race conditions, timing issues, partial failures
- Use the type system to encode correctness constraints
- Prefer compile-time guarantees over runtime checks where possible
- When uncertain, explore and iterate rather than assume

**Don't:**

- Simplify error handling to save time
- Ignore edge cases because "they probably won't happen"
- Use `any` or equivalent to bypass type checking

### Error Handling Philosophy

**Two-tier model:**

1. **User-facing errors**: Semantic exit codes, rich diagnostics, actionable messages
2. **Internal errors**: Programming errors that may panic or use internal types

**Error message format:** Lowercase sentence fragments for "failed to {message}".

```
Good: failed to connect to database: connection refused
Bad:  Failed to Connect to Database: Connection Refused

Good: invalid configuration: missing required field 'apiKey'
Bad:  Invalid Configuration: Missing Required Field 'apiKey'
```

Lowercase fragments compose naturally: `"operation failed: " + error.message` reads correctly.

Always use proper logging, and errors should always be logged via the language/framework appropriate methods.

### Pragmatic Incrementalism

- Prefer specific, composable logic over abstract frameworks
- Evolve design incrementally rather than perfect upfront architecture
- Don't build for hypothetical future requirements
- Document design decisions and trade-offs when making non-obvious choices

**The rule of three applies to abstraction:** Don't abstract until you've seen the pattern three times. Three similar lines of code is better than a premature abstraction.

## File Organization

### Descriptive File Names Over Catch-All Files

Name files by what they contain, not by generic categories.

**Don't create:**

- `utils.go` - Becomes a dumping ground for unrelated functions
- `helpers.js` - Same problem
- `common.rs` - What isn't common?
- `misc.go` - Actively unhelpful

**Do create:**

- `formatter.go` - String manipulation utilities
- `calendar/math.go` - Date calculations
- `api/src/error_handling.rs` - API error utilities
- `user-input.ts` - User input validation

**Why this matters:**

- Discoverability: Developers find code by scanning file names
- Cohesion: Related code stays together
- Prevents bloat: Hard to add unrelated code to `string-formatting.ts`
- Import clarity: `import { formatDate } from './date-arithmetic'` is self-documenting

**When you're tempted to create utils.ts:** Stop. Ask what the functions have in common. Name the file after that commonality.

### Module Organization

- Keep module boundaries strict with restricted visibility
- Platform-specific code in separate files: `unix.go`, `windows.go`, `posix.go`
- Use conditional compilation or runtime checks for platform branching
- Test helpers in dedicated modules/files, not mixed with production code

## Cross-Platform Principles

### Use OS-Native Logic

Don't emulate Unix on Windows or vice versa. Use each platform's native patterns.

**Bad:** Trying to make Windows paths behave like Unix paths everywhere.

**Good:** Accept platform differences, handle them explicitly.

```typescript
// Platform-specific behavior
if (process.platform === "win32") {
  // Windows-native approach
} else {
  // POSIX approach
}
```

### Platform-Specific Files

When platform differences are significant, use separate files:

```
process/spawn.go    // Shared interface and logic
process/unix.go     // Unix-specific implementation
process/windows.go  // Windows-specific implementation
```

### Document Platform Differences

When behavior differs by platform, document it in comments:

```typescript
// On Windows, this returns CRLF line endings.
// On Unix, this returns LF line endings.
// Callers should normalize if consistent output is needed.
function readTextFile(path: string): string { ... }
```

### Test on All Target Platforms

Don't assume Unix behavior works on Windows. Test explicitly:

- CI should run on all supported platforms
- Platform-specific code paths need platform-specific tests
- Document which platforms are supported

## Common Mistakes

| Mistake                                | Reality                                            | Fix                                      |
| -------------------------------------- | -------------------------------------------------- | ---------------------------------------- |
| "Just put it in utils for now"         | utils.ts becomes 2000 lines of unrelated code      | Name files by purpose from the start     |
| "Edge cases are rare"                  | Edge cases cause production incidents              | Handle them. Model the full error space. |
| "We might need this abstraction later" | Premature abstraction is harder to remove than add | Wait for the third use case              |
| "It works on my Mac"                   | It may not work on Windows or Linux                | If deploying to a target, test on it     |
| "The type system is too strict"        | Strictness catches bugs at compile time            | Fix the type error, don't bypass it      |

## Red Flags

**Stop and refactor when you see:**

- A `utils.go` or `helpers.rs` file growing beyond 100 lines
- Error handling that swallows errors or uses generic messages
- Platform-specific code mixed with cross-platform code
- Abstractions created for single use cases
- Type assertions (`any`) to bypass the type system
