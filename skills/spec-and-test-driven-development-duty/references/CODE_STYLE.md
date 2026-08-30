---
apply: when-coding
---

# CODE STYLE — Packaged Engineering Standard

These rules apply whenever writing, reviewing, modifying, or discussing code in any language. Mandatory, not advisory.

---

## Paradigm

OOP only. I do not use non-OOP languages. Functional idioms, procedural shortcuts, and "language X lets you do it this way" pleas are not arguments here.

## Languages

Python, TypeScript, Rust. Rules below apply per-language where they differ.

---

## OOP — Maximize Structure

Default to polymorphic, abstracted, enterprise-structured designs. Prefer interfaces / protocols / abstract bases over concrete types in signatures. Prefer composition over inheritance; use inheritance only for genuine is-a relationships with shared behavior worth inheriting. Inheritance depth ≤ 3 levels.

Caveat: "prefer abstraction" does not mean single-implementation-interface theater for its own sake. If you would be inventing an abstraction with no current or foreseeable second implementation purely to satisfy the rule, flag it and ask.

---

## Polymorphism — Per Language

### Python

- **Primary:** Protocol-based polymorphism via `typing.Protocol`. ABCs (`abc.ABC`) when runtime enforcement or shared base behavior is needed.
- **Subtype:** Inheritance via ABCs only when there is genuine shared implementation (template method, shared state, shared invariants).
- **Parametric:** Generics aggressively. Use **PEP 695 syntax** (`class Repository[T]:`, `type UserId = int`) when on Python 3.12+; fall back to `TypeVar` / `Generic` on older runtimes.
- **Ad-hoc:** `functools.singledispatch` over `isinstance` chains. `@overload` for type-checker hints.
- **Never:** Bare duck typing without a declared `Protocol` or `ABC`. If something is polymorphic, the contract is explicit.

### TypeScript

- **Primary:** `class` and `abstract class` over `interface` for my own abstractions. Interfaces are compile-time only; classes give runtime identity (`instanceof`, decorators, introspection).
- **Exception:** `interface` and `type` are correct for **external data shapes** — API responses, config files, third-party library inputs, anything not my abstraction.
- **Parametric:** Generics aggressively — `Repository<T>`, `Result<T, E>`, `EventHandler<T>`.
- **Discriminated unions vs class hierarchy:**
  - Class hierarchy when **behavior** varies by type (each subclass has its own logic, state, lifecycle).
  - Discriminated union when only **data shape** varies and consumers pattern-match centrally (API response variants, parser tokens, event payloads).
- **Ad-hoc:** Method overloading via overload signatures for API ergonomics.

### Rust

Rust has no inheritance. All polymorphism is trait-based, so "composition over inheritance" isn't a preference here — it's the only option. Shared behavior comes from trait default methods and supertraits, never from a base class.

- **Primary:** trait-based polymorphism. The trait is the abstraction surface; concrete types `impl` it. Prefer trait bounds and trait objects in signatures over concrete types — the same instinct as protocols in Python and abstract classes in TypeScript.
- **Default to dynamic dispatch (`dyn Trait`) when in doubt.** The reasoning is refactorability: it is easier to monomorphize a `dyn`-based design into generics later than to retrofit a generics-saturated trait back into object safety. Reach for generics when you have a concrete generic-container, algorithm, or hot-path reason — not by default.
- **Static dispatch — generics with trait bounds, `impl Trait`** for: generic containers, generic algorithms, numerical code, and hot paths where the vtable indirection is measurably significant. Monomorphization is the zero-cost path, paid for in compile time and binary size.
- **Dynamic dispatch — `Box<dyn Trait>`, `&dyn Trait`, `Arc<dyn Trait>`** for: heterogeneous collections, plugin / strategy patterns, runtime-decided types, anything crossing a module boundary, and anywhere monomorphization bloat outweighs the dispatch cost.
- **Always profile before optimizing.** Do not pick generics over `dyn` for "performance" without numbers. For non-hot-path code the dispatch difference sits below measurement noise — and `dyn` keeps compile times and binary size down, which is a real cost in the other direction.
- **Parametric:** generics aggressively — `Repository<T>`, `Result<T, E>`, `EventHandler<T>` — always with explicit trait bounds. An unconstrained `T` standing in for "any type with the methods I happen to call" is the Rust form of bare duck typing; the bound is the contract, stated explicitly.
- **Ad-hoc:** trait impls for your own types; blanket impls (`impl<T: Display> MyTrait for T`) over hand-repeated impls; `impl Trait` in argument and return position for opaque types; newtype wrappers (`struct UserId(u64)`) to attach behavior to foreign or primitive types.
- **Enum + `match` vs trait objects** — the Rust version of the discriminated-union-vs-class-hierarchy split from the TypeScript rules:
  - **Trait object** when **behavior** varies by type: each implementor has its own logic, state, and lifecycle, and the set of implementors is open.
  - **Enum with centralized `match`** when only **data shape** varies and the variant set is closed and known — parser tokens, state-machine states, message payloads. Exhaustive `match` then turns "added a variant, forgot to handle it" into a compile error, which is the entire reason to choose the enum.
- **Non-negotiable:** keep `dyn` traits object-safe unless you've decided otherwise on purpose and written down why. Generic methods, `impl Trait` in return position, and by-value `self` receivers silently break object safety — those are the ones to watch before a trait stops being usable as `dyn`.

---

## Idiomatic Rust — Mandatory

Writing Rust that a Rust developer would recognize as natural is a first-class requirement here, not a nicety. One ordering rule resolves the obvious tension with the Zen section below: where Rust idiom and the rules in this document (OOP, SOLID, Zen, and `NAMING.md`) genuinely conflict, the document wins — the same stance the Zen section takes on idiom in general. Those conflicts are rare and named at the end of this section. Everything that is *not* a named conflict — the overwhelming majority of what "idiomatic Rust" means — is required.

### Error handling

- Fallible operations return `Result<T, E>`; absence is `Option<T>`. Propagate with `?` rather than hand-rolled match-and-return ladders.
- **No `unwrap()`, `expect()`, or `panic!` in library code.** Return the error and let the caller decide. `expect()` is allowed only at a genuine program invariant — a `OnceCell` known-initialized at startup, a regex literal known-valid — and the message must state that invariant. That message *is* the explicit-silencing comment the Zen rule already demands.
- Define real error types for libraries (an error `enum`, typically via `thiserror`), not stringly-typed errors. Application and binary edges may use a `Box<dyn Error>`-style aggregate (`anyhow`) where exhaustive matching on the error buys nothing.

### Ownership and borrowing

- Take `&T` / `&mut T` in signatures by default; take ownership only when the function actually consumes or stores the value. Owning "just in case" forces a needless clone on every caller.
- Don't reach for `.clone()` to silence a borrow-checker error you haven't understood — understand the lifetime first. A clone is a deliberate cost, not an escape hatch.
- Let lifetimes be elided where the rules allow; annotate explicitly only where the relationship is real and the compiler needs it.

### Types and conversions

- Newtypes over primitive obsession: `struct UserId(u64)`, not a bare `u64` threaded through signatures. This reinforces the intention-revealing-names rule and the "don't pass meaningless primitives" half of Dependency Inversion.
- Conversions go through `From` / `Into` / `TryFrom`, not bespoke `to_x()` constructors, so the standard machinery (`?` on a `TryFrom` error, `.into()` at call sites) works for free.
- Derive `Debug` on essentially every type; implement `Display` for anything that crosses a user-facing or error boundary. Derive `Clone`, `PartialEq`, and friends when they are meaningful — not reflexively.

### Expression style

- Iterator combinators (`.iter().map().filter().collect()`) over manual index loops — but honor `NAMING.md`: name the closure binding (`.map(|row| row.id)`), never `|x|`.
- `if let` / `let ... else` / `match` over `is_some()`-then-`unwrap()` and `is_ok()`-then-`unwrap()`.
- Prefer expression-valued `if` / `match` / blocks over mutable-accumulator scaffolding where it reads cleanly.

### Named conflicts — where this document overrides idiom

- **Single-letter bindings.** Rust idiom is full of `i`, `e`, `n`, `|x|`. `NAMING.md` bans all of those — spell them out (`index`, `error`, `count`, `|row|`). The naming rule wins. The exceptions are named in `NAMING.md` Section 4 and are narrow: generic type parameters (`T`, `E`, `K`, `V`, `I`, `F`), lifetimes (`'a`), and `_` in pattern position. So `Result<T, E>` is fine and `Err(e)` is not.
- **Dispatch default.** Common Rust idiom leans generics-first for zero-cost abstraction; the `### Rust` polymorphism rules above default to `dyn` when in doubt and optimize toward generics with profiling. The house default wins. This is the one place where preserving the house dispatch principle and writing idiomatic Rust pull apart, and it is resolved in favor of the house principle.

---

## SOLID

The five principles, full names: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. Stance on each below.

### Single Responsibility Principle — Strict

A class has **one and only one reason to change.** Not "does one thing" — *changes for one reason*. One stakeholder, one axis of change. If a class would change for both business-rule reasons and formatting reasons (or persistence reasons, or transport reasons), split it. Flag violations when seen.

### Open/Closed Principle — Dropped

Not enforced. The "never modify, only extend" reading fights how software actually evolves. The salvageable part — "design so changes don't cascade through unrelated code" — is just good design, covered elsewhere.

### Liskov Substitution Principle — Strict

Subclasses must be drop-in replacements for their parent. Callers written against the base must keep working with any subtype without surprise, without `isinstance` / `Any`-downcast checks, without special-case branches.

Mechanically:

- Subtypes cannot strengthen preconditions.
- Subtypes cannot weaken postconditions.
- Subtypes cannot throw exceptions the parent did not.
- Subtypes cannot break invariants the parent established.

Signal of violation: a caller needs to know the concrete subtype to use the object correctly. If that is happening, the hierarchy is wrong — usually the "is-a" was modeling math or taxonomy instead of behavior, or the interface needs splitting (see Interface Segregation).

### Interface Segregation Principle — Strict

Clients do not depend on methods they don't use. Many small focused interfaces beat one fat one; a class can implement several. Signal of violation: stub implementations that `raise NotImplementedError` / `throw new Error("not supported")`. When that appears, the interface needs splitting.

Example: a `Repository` with `save`, `load`, `delete`, `list`, `search`, `bulkInsert`, `migrate` → split into `Readable<T>`, `Writable<T>`, `Searchable<T>`, compose as needed.

### Dependency Inversion Principle — Strict

High-level modules don't depend on low-level modules. Both depend on abstractions. Inject behaviors that talk to the outside world or vary by environment: I/O, persistence, external services, time, randomness, filesystem, network. Construction wires the graph; everything else consumes abstractions.

Do **not** inject primitives or value types (`int`, `str`, `datetime`). The rule is for *behaviors*, not data.

---

## Zen of Python — Strict, All Languages

All nineteen lines apply across Python, TypeScript, and Rust. No exceptions for "but the idiomatic X way is…" — we do not optimize for matching language-community idiom. We optimize for explicit, readable, performant OOP.

The canonical text (Tim Peters, PEP 20):

> Beautiful is better than ugly.
> Explicit is better than implicit.
> Simple is better than complex.
> Complex is better than complicated.
> Flat is better than nested.
> Sparse is better than dense.
> Readability counts.
> Special cases aren't special enough to break the rules.
> Although practicality beats purity.
> Errors should never pass silently.
> Unless explicitly silenced.
> In the face of ambiguity, refuse the temptation to guess.
> There should be one — and preferably only one — obvious way to do it.
> Although that way may not be obvious at first unless you're Dutch.
> Now is better than never.
> Although never is often better than *right* now.
> If the implementation is hard to explain, it's a bad idea.
> If the implementation is easy to explain, it may be a good idea.
> Namespaces are one honking great idea — let's do more of those!

Operational interpretation of the friction points:

- **"There should be one — and preferably only one — obvious way to do it"** — within a codebase or module, pick one form and use it consistently. Not a ban on language features; a ban on stylistic inconsistency within a project.
- **"Sparse is better than dense"** — default to sparse and readable. When density buys measurable performance, flag it and let me decide. Don't silently choose dense for cleverness.
- **"In the face of ambiguity, refuse the temptation to guess"** — applies to code: no implicit defaults, no silent fallbacks, no `try/except: pass`, no swallowed errors, no silent type coercion. If a function can fail or branch, it does so explicitly.
- **"Errors should never pass silently / Unless explicitly silenced"** — silencing requires a comment explaining why.
- **"If the implementation is hard to explain, it's a bad idea"** — if you can't summarize what a class or method does in one sentence, the design is wrong.

---

## Cross-Cutting Defaults

- **Composition over inheritance** unless a real is-a relationship with shared behavior justifies inheritance.
- **Inheritance depth ≤ 3.** Past three, you're rediscovering composition the hard way.
- **No `isinstance` / `Any` downcasting in caller code** to special-case subtypes. If you need that, the polymorphism is broken — fix the hierarchy or split the interface.
- **No stub `NotImplementedError` / "not supported" methods.** Split the interface instead.