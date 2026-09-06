---
apply: when-coding
---

# NAMING — Packaged Conventions

Applies to all code in any language. Project-specific naming layers may extend or override this in `./NAMING.md`.

## 1. Intention-revealing names

A name that needs a comment to explain it is the wrong name. Replace the name; delete the comment.

- `chunked_sections` not `cs`.
- `inline_payload_bytes` not `b`.
- `retry_delay_seconds` not `delay`.

If you find yourself writing a comment to clarify a variable's meaning, rename the variable instead.

## 2. Acronym casing

Treat acronyms as words in identifiers, not as runs of capitals.

| Wrong | Right |
|---|---|
| `APIKey` | `ApiKey` |
| `OSClient` | `OpensearchClient` (spell it out) |
| `URLBuilder` | `UrlBuilder` |
| `AIService` | `AiService` |
| `DBSession` | `DatabaseSession` |
| `HTTPRequest` | `HttpRequest` |

Single letter + digit is allowed where the acronym is a recognized identifier on its own: `S3Storage`, `H2Connection`.

Spell out acronyms that are domain-specific or ambiguous (`OS` → `Opensearch`, `DB` → `Database`).

Module / package / file names: no internal underscores within an acronym (`opensearch/` not `open_search/`). Case follows the language — `snake_case` in Python and Rust, `camelCase` in TypeScript (see Section 3).

## 3. Per-language case conventions

| Element              | Python                 | TypeScript             | Rust                          |
|----------------------|------------------------|------------------------|-------------------------------|
| Classes / types      | `PascalCase`           | `PascalCase`           | `PascalCase`                  |
| Enum members         | `SCREAMING_SNAKE_CASE` | `PascalCase`           | `PascalCase`                  |
| Functions / methods  | `snake_case`           | `camelCase`            | `snake_case`                  |
| Variables / fields   | `snake_case`           | `camelCase`            | `snake_case`                  |
| Constants            | `SCREAMING_SNAKE_CASE` | `SCREAMING_SNAKE_CASE` | `SCREAMING_SNAKE_CASE`        |
| Files                | `snake_case.py`        | `camelCase.ts`         | `snake_case.rs`               |
| Private members      | `_leading_underscore`  | `#privateField`        | private by default (no `pub`) |

**Enum members:** this is the row where the three languages genuinely disagree, so check it instead of reusing habits from another language. Python writes `Color.RED`. Rust writes `Color::Red`, and rustc's `non_camel_case_types` lint warns if you write `Color::RED` instead. Carrying the Python shape into Rust produces a compiler warning, not just an inconsistency.

**Rust private:** privacy is a keyword, not a name shape. A struct field is private unless you write `pub` in front of it, and the compiler enforces that. So there is nothing for a naming convention to signal. Do not carry the Python leading underscore across — in Rust a leading underscore already means "intentionally unused" and silences the unused-variable warning.

**TypeScript private:** use `#privateField` (ECMAScript native private), never the `private` keyword. The `private` keyword is compile-time only and erased at runtime — anyone can reach the field via `(obj as any).field`. `#privateField` is enforced by the JavaScript engine at runtime. This is the same runtime-presence reasoning that picks `class` over `interface` for our own abstractions (see the TypeScript polymorphism rules in `CODE_STYLE.md`).

## 4. Locals and parameters

- **No single-letter identifiers, outside the established language idioms listed below.**
  - Loops: `for index in range(count)` / `for (let index = 0; ...)` — never `for i`.
  - Comprehensions / `map` / `filter`: `[row.id for row in rows]` / `rows.map(row => row.id)` — never `x`, `e`, `r`.
  - **Error bindings: never `e`. Write `error`.** This applies everywhere the language hands you an error to bind: Rust's `Err(error)` never `Err(e)`, Python's `except ValueError as error`, TypeScript's `catch (error)`. Rust's `Err(e)` is common in the wild and is banned here anyway — `Err` is the variant name and is fixed by the language, but the binding inside it is a name you chose, so it follows the rule.
  - Tuple / destructuring discards: name them explicitly (`unused_index`) or refactor. Python's `_` is a single-letter name and is also banned.
  - **Rust `_` is grammar, not a name, and is allowed in pattern position.** A pattern is the shape you match a value against. This covers the catch-all `match` arm (`_ => ...`), field skipping in destructuring (`let Point { x: horizontal, .. } = point`), and unused closure parameters (`.map(|_| default_value)`).
  - `let _ = expression;` is also allowed and means something specific: evaluate the expression, then drop the result immediately. It is the standard way to deliberately ignore a `Result` the compiler insists you handle. Use it only when ignoring the value is the intent, not as a shortcut to silence a warning you have not thought about.
  - A binding you keep but never read still needs a real name: `let _unused_index = compute_index();`, never a bare underscore. The two are not interchangeable — `let _guard = mutex.lock()` holds the lock to the end of the scope, while `let _ = mutex.lock()` releases it on the spot.
  - Parameters: `def parse(query)` / `function parse(query)` — never `q`.
  - Locals: `digest = hash(...)` — never `d`.
- Established language idioms are the only exceptions: `self` and `cls` in Python, `this` in TS, `self` in Rust (the method receiver), and Rust generic type parameters and lifetimes.
  - **Rust generics:** the conventional single letters are allowed — `T` (a general type), `E` (an error type), `K` and `V` (a map's key and value), `I` (an iterator), `F` (a closure). Lifetimes follow the same allowance: `'a`, `'b`.
  - When a type parameter carries a domain meaning rather than being fully generic, spell it out in `PascalCase`: `struct Cache<Payload, Key>`, not `struct Cache<P, K>`.
- Loop accumulators: `total`, `count`, `seen` are fine. Avoid `n`, `cnt`, `tot`.

## 5. Functions and methods

- Methods are verbs or verb phrases: `create_pending_document`, `revoke_api_key`, `parseConfig`. Not nominalized forms like `pending_document_creation` or `configParsing`.
- **Rust conversion prefixes override "methods are verbs."** The Rust API Guidelines fix three prefixes by cost and ownership: `as_` for a cheap borrow-to-borrow view (`as_str`, `as_bytes`), `to_` for a conversion that allocates or is otherwise expensive (`to_string`, `to_owned`), and `into_` for one that consumes the receiver (`into_bytes`, `into_iter`). `as_str` is not a verb phrase and is still correct — pick the prefix that matches the cost, not the one that sounds like a verb.
- **Rust getters drop `get_`.** Write `fn name(&self) -> &str`, not `fn get_name(&self) -> &str`. The guidelines keep `get_` only for types with one obvious thing to get (`Cell::get`) and for the `get_mut` / `get_unchecked` variants. Here the noun is the name, and the verb rule does not apply.
- Boolean-returning predicates start with `is_`, `has_`, `should_`, or `can_` (adapted to language case): `is_expired`, `hasChunks`, `shouldRetry`, `canPublish`.
- Async functions get no special suffix. `async def` / `async function` / `async fn` is the marker; do not append `Async` to the name.
- No `and` in function names — `create_and_publish_event` means the function does two things; split it or rename to a single verb that describes the combined operation (`enqueue_event`, `dispatch_event`).

## 6. Classes, structs, and traits

Classes and structs are nouns or noun phrases: `IngestionPipeline`, `ApiKeyService`, `EventConsumer`.

**Allowed suffixes that carry meaning:**

`Service`, `Repository`, `Pipeline`, `Strategy`, `Client`, `Storage`, `Producer`, `Consumer`, `Worker`, `Handler`, `Builder`, `Factory`, `Adapter`, `Gateway`.

Pick one and stick with it within a layer — don't have `UserService` and `OrderManager` in the same codebase.

**Banned vague suffixes:**

`Util`, `Utils`, `Helper`, `Helpers`, `Manager`, `Processor`, `Doer`, `Stuff`, `Misc`.

These signal "I couldn't think of what this type actually does." Name the actual responsibility. If the class or struct genuinely has no cohesive responsibility, the type is wrong (see Single Responsibility Principle in `CODE_STYLE.md`).

**Rust traits are the exception — they name a capability, not a thing.** A trait declares "a type with this can do X," roughly what an interface is in TypeScript. Rust's standard library names traits with verbs (`Clone`, `Copy`, `Display`, `Read`, `Write`, `Serialize`) and adjectives (`Sized`, `Send`, `Sync`), not nouns. So name the trait after the ability: `Serialize`, not `Serializer`; `Read`, not `Reader`. The noun form belongs to the concrete type that implements the trait, and there the suffix list above applies as normal.

## 7. Constants

- Module / namespace level only when truly immutable and configured at import / load time.
- Include the unit in the name when the value has one: `RETRY_DELAY_SECONDS`, `MAX_PAYLOAD_BYTES`, `CONNECTION_TIMEOUT_MS`. Bare `RETRY_DELAY` is a bug waiting to happen.
- Tunable runtime settings belong in config (Pydantic Settings, environment-driven config objects, etc.), not as module-level constants.

## 8. Banned abbreviations

Outside the established language idioms listed in Section 4 (`self`, `cls`, `this`, and Rust generic type parameters and lifetimes), these are banned. Spell them out.

| Banned | Use instead |
|---|---|
| `svc` | `service` |
| `repo` | `repository` |
| `mgr` | name the actual responsibility (don't use `manager` either) |
| `cfg`, `cnf`, `conf` | `config` |
| `ctx` | `context` |
| `req` | `request` |
| `resp` | `response` |
| `res` | `response` or `result` — pick the one that is true. In Rust, `res` almost always means a `Result`, so `result` is usually correct. |
| `err`, `e` | `error` — lowercase only. Uppercase `E` as a Rust generic type parameter is allowed (Section 4). |
| `exc` | `exception` |
| `attr` | `attribute` |
| `fn` | `function` |
| `cb` | `callback` |
| `hdlr` | `handler` |
| `proc` | name the actual responsibility (don't use `processor` either — see Section 6) |
| `tmp` | `temporary` (or rename — usually a code smell) |
| `val` | `value` |
| `ret` | `return_value` / `result` |

`config` (full word) is allowed. `cfg` is not. `manager` is also banned — name what the class or variable actually does.

This table constrains identifiers you choose. It does not touch language keywords or standard-library names that happen to look like abbreviations: Rust's `fn`, `mod`, `impl`, `pub`, and `dyn`, and the `Ok` / `Err` variants of `Result`, are reserved vocabulary, not naming decisions. The rule reaches the names you bind inside them — `Err(error)`, not `Err(e)`.

## 9. Files and modules

- Module file names mirror their primary export, in the language's case convention. Where a module has no single primary export — common in Rust — name it after the concept the module covers.
- Package / module index files (`__init__.py`, `index.ts`, `lib.rs`, etc.) re-export the public symbols of the package; nothing else.
  - **Rust:** `lib.rs` is the crate root for a library and holds only `mod` declarations plus `pub use` re-exports. A crate is Rust's unit of compilation — roughly one library or one binary. The `mod foo;` lines do not violate "nothing else": they are what attaches a file to the module tree, and without them the module does not exist as far as the compiler is concerned.
  - **Rust:** `main.rs` is exempt. It is the entry point for a binary and must contain `fn main()`.
  - **Rust module layout:** prefer `foo.rs` sitting next to a `foo/` directory over `foo/mod.rs`. Both are valid and neither is deprecated, but the first gives every file a distinct name instead of leaving you with a dozen editor tabs all labelled `mod.rs`.
- **Rust crate names:** Cargo replaces hyphens with underscores, so a package declared as `name = "my-lib"` in `Cargo.toml` is referenced in code as `my_lib` (`use my_lib::...`). Both spellings are common on crates.io and neither is wrong. Prefer the underscore form in `Cargo.toml` so the name in the manifest matches the name in every `use` statement, and the reader never has to translate.
- Test files mirror the module under test: `test_<module>.py`, `<module>.test.ts`, `tests/<module>.rs` for Rust integration tests (per language convention).
  - **Rust:** unit tests live in a `#[cfg(test)] mod tests` block inside the module they test, not in a separate file. The `#[cfg(test)]` attribute tells the compiler to build that block only when running tests, so it costs nothing in a release build. Only integration tests — tests that exercise the crate from the outside, through its public API — get their own file under `tests/`.

## 10. Negative space — what NOT to do

- **No Hungarian notation.** `s_name`, `i_count`, `b_active` — banned. The type is in the type system, not the name.
- **No type-suffixed names.** `user_dict`, `result_list`, `config_obj` — banned. The type is in the type hint / declaration.
- **No leading underscore on locals in Python or TypeScript.** There, a leading underscore is reserved for "private to module / class."
- **Rust is the exception, because the underscore means something different.** A leading underscore marks a binding as intentionally unused and silences the compiler's unused-variable warning. `let _unused_index = ...` is correct Rust for a binding you must create but never read. It says nothing about privacy — privacy is the `pub` keyword (see Section 3).
- **No "and" in function names** (see Section 5).
- **No bare `data`, `info`, `obj`, `item`, `thing`, `stuff`** — anywhere. Comprehensions, callbacks, and lambdas are not exemptions. If you have an `item`, name what kind of item it is.

---

## How to think about this

The rule of thumb behind every section: **a reader should be able to understand what a name refers to without context.** Single letters, abbreviations, and vague nouns all force the reader to reconstruct meaning from surrounding code. That's a cost paid on every read. The cost of typing a longer name is paid once.
