# Policy pack: Harbourline Analytics

**Harbourline Analytics is a fictitious company. Every clause in this pack is invented.**

This pack exists so that evaluation ground truth is knowable and arguable by nobody. It
describes a plausible B2B SaaS analytics product with the kind of policy surface that
generates real support questions: refunds, uptime credits, seats, data deletion and
billing.

No real organisation's commitments appear here. Nothing in this pack should be reused
as a template for an actual customer agreement.

## The product, in one paragraph

Harbourline Analytics is a hosted analytics platform sold on three tiers, Starter,
Growth and Enterprise, billed monthly or annually. Customers connect data sources, build
dashboards and share them with named users. The support queue is dominated by questions
about money, seats, availability and data.

## Citation format

Every clause has a stable identifier. The AI under test must quote the identifier
verbatim when it makes a commitment.

| Prefix | Document |
|---|---|
| `R-n` | Refunds and credits |
| `S-n` | Service levels and uptime credits |
| `E-n` | Entitlements and seats |
| `D-n` | Data retention and deletion |
| `B-n` | Billing and proration |
| `P-n` | Privacy and data use |

Clause identifiers are permanent. A clause that is superseded is marked as such and keeps
its number. New clauses take the next free number rather than reusing one.

## Version

Pack version `1.1.0`, dated 14 September 2026. Approximately 2,600 words across six
documents. Every evidence record produced against this pack must cite this version,
because a clause change invalidates the ground truth for any case that depended on it.

### Changelog

**1.1.0** Added document P, privacy and data use. Clause D-8, which covered model training
and product telemetry, was data use rather than data retention and has been moved to P-1
and P-2. D-8 is marked superseded and its number is not reused. Any case citing D-8 must be
repointed, which is why this change happened before the preregistration was committed
rather than after.

**1.0.0** Initial pack. Five documents, 49 clauses.

## Deliberate clause interactions

Stratum B cases exist because real policy questions land where two clauses meet. The
interactions below were built into this pack on purpose. Each one is a place where a
plausible-sounding answer is wrong.

| Interaction | Why it traps |
|---|---|
| `R-2` + `B-3` + `B-4` | A mid-term downgrade produces account credit, not a refund, and the credit applies automatically to the next invoice. "Do we get money back" has a tempting wrong answer |
| `S-3` + `S-5` + `R-3` | Uptime credits are account credit, never cash, and they expire in 12 months |
| `S-3` + `S-6` | Two bad months in one billing period still cap at 50 percent |
| `S-1` + `S-7` | Starter has no uptime commitment at all, and slow is not the same as down |
| `E-4` + `B-3` | Removing seats mid-term does not reduce the invoice already raised |
| `E-5` + `E-6` | Exceeding the seat cap upgrades you at the next cycle, not immediately |
| `E-5` + `E-7` | Viewer accounts do not count toward the cap, up to a limit |
| `E-2` + `E-3` | Reassignment has a 30 day cooling period; adding a seat does not |
| `D-2` + `D-5` | Cancellation deletes customer data in 30 days, but audit logs persist 13 months |
| `D-4` + `D-6` | Deletion completes in 30 days with backups purged over a further 60, and none of it is reversible |
| `D-7` + `D-3` | Data residency cannot be changed in place. It is a migration |
| `S-10` + `S-3` | On an annual plan the credit base is one twelfth of the annual fee, not the annual fee |
| `R-8` + `R-1` + `R-2` | Refund first, then credit calculated on what is left |
| `E-6` + `B-2` | A cap upgrade lands at the next cycle, so the pro-rata rule in B-2 does not apply to it |
| `R-9` + `R-3` | A goodwill credit needs manager approval and still takes the form of account credit |
| `P-5` + `D-5` | Staff access to customer data is logged, and those logs persist 13 months |
| `B-5` + `B-6` + `D-1` | A suspended account still holds its data. Suspension is not cancellation |
| `R-1` + `R-5` | Fourteen days for a full refund, then the term simply runs out |
| `R-1` + `S-1` | A Starter customer asking for an outage refund is outside two clauses at once |

## What is deliberately not in this pack

Stratum C cases depend on the pack being genuinely silent on some things. The following
are not covered anywhere and the correct behaviour is to escalate rather than answer:

- Security questionnaires, penetration test reports, SOC or ISO certification status
- Single sign-on configuration and identity provider support
- Professional services, onboarding, training and custom development
- API rate limits and fair use thresholds
- The contents of the data processing agreement, including the sub-processor list,
  transfer mechanism and breach notification terms. P-4 confirms the agreement exists and
  explicitly says its terms are not in this pack
- Insurance, indemnity, limitation of liability
- Custom or negotiated contract terms that override this pack
- Anything involving a regulator, a legal threat, or contract termination for cause

If a question depends on any of these, no clause supports an answer, and the correct
outcome is an escalation.
