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

1. [Issue #9](https://github.com/suryamanoj4/openmeet/issues/9) tracks
   compatibility-tested remediation of frontend dependency advisories.
2. [Issue #10](https://github.com/suryamanoj4/openmeet/issues/10) tracks real
   PostgreSQL concurrency coverage for checkout, inventory, and capacity locks.
3. [Issue #11](https://github.com/suryamanoj4/openmeet/issues/11) tracks
   database-enforced payment webhook replay protection.
4. [Issue #12](https://github.com/suryamanoj4/openmeet/issues/12) tracks
   end-to-end browser coverage for critical user journeys.
5. [Issue #13](https://github.com/suryamanoj4/openmeet/issues/13) tracks rate
   limiting for authentication, checkout, webhooks, and public GraphQL traffic.
6. [Issue #14](https://github.com/suryamanoj4/openmeet/issues/14) tracks
   production observability and backup/restore validation.
7. [Issue #15](https://github.com/suryamanoj4/openmeet/issues/15) tracks
   migration scope, review, and reversibility enforcement.

## Verification baseline

- backend unit/GraphQL tests
- frontend Node tests
- `svelte-check` with zero diagnostics
- SvelteKit production build using adapter-node
- Docker Compose configuration rendering
- explicit process-liveness and database-readiness checks
- whitespace/error checks on every staged patch

This is a targeted engineering audit, not a claim that arbitrary software is
defect-free. The residual list is deliberately explicit so remaining risk can
be prioritized and tracked.
