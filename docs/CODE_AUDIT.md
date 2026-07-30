# Code Audit

This audit covers the event creation/publishing, GraphQL authorization,
checkout/payment, and deployment paths exercised while resolving issues
#1, #3, #5, and #7.

## Resolved in the PR stack

- navigation items and event creation affordances were missing or inert
- event schedules accepted invalid ordering, past publication, invalid
  registration windows, and invalid timezone identifiers
- event status could bypass the publish workflow
- the page builder preview could execute stored raw HTML
- multiple GraphQL queries and attendee/payment operations lacked ownership
  boundaries
- request-scoped database sessions were not reliably closed
- checkout did not consistently validate event state, ticket limits, sales
  windows, inventory, or ownership
- concurrent orders could oversell tickets
- payment completion and attendee creation were not idempotent
- attendee lists queried with the wrong identifier
- the production frontend image changed source and dependencies while building
- deployed browsers could fall back to `localhost` for GraphQL
- CORS and JWT production safety were hard-coded or unenforced
- application services lacked readiness gates and automated CI

## Residual risks and follow-up work

1. `npm audit` currently reports dependency advisories. Upgrade each dependency
   in a separate compatibility-tested change; do not apply a forced audit fix
   blindly.
2. The complete database-backed test suite should be expanded with concurrent
   checkout and real PostgreSQL transaction tests. Current validation/service
   tests do not prove lock behavior on every supported database. In the local
   Python 3.13 sandbox, the suite's SQLite async fixture stalls after 44 tests;
   changed-path tests pass, and CI runs the full suite with a bounded timeout.
3. Payment webhooks should persist provider event IDs and reject replayed
   events at the database boundary, in addition to idempotent service behavior.
4. Add end-to-end browser coverage for registration, login, create, publish,
   free checkout, paid checkout, and check-in.
5. Add rate limiting for authentication, checkout, and public GraphQL traffic.
6. Add structured error reporting, metrics, backup/restore drills, and explicit
   liveness versus readiness endpoints before operating at scale.
7. Review every future Alembic revision before merge for unrelated destructive
   operations; schema changes should be narrowly scoped and reversible.

## Verification baseline

- backend unit/GraphQL tests
- frontend Node tests
- `svelte-check` with zero diagnostics
- SvelteKit production build using adapter-node
- Docker Compose configuration rendering
- whitespace/error checks on every staged patch

This is a targeted engineering audit, not a claim that arbitrary software is
defect-free. The residual list is deliberately explicit so remaining risk can
be prioritized and tracked.
