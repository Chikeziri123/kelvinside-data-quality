# Kelvinside Professional Services: business and systems context

## The organisation

Kelvinside Professional Services is a UK mid-market consultancy of roughly
400 staff across Newcastle, Manchester and Glasgow. It bills clients on a
mix of time and materials and fixed fee engagements. Revenue recognition,
resource planning and supplier payments all depend on data that is spread
across three systems that were bought at different times by different
departments.

## Systems landscape

| System | Owner | Holds | Extract |
|---|---|---|---|
| Halstead CRM | Commercial Director | Clients, contacts, opportunities, engagements | Nightly CSV |
| Trentmoor Finance | Finance Director | Suppliers, invoices, cost centres, billing | Nightly CSV |
| Brackenhill HR | HR Director | Employees, roles, cost centre assignment, leavers | Nightly CSV |

No master data management layer exists. Client records are keyed differently
in CRM and Finance, and cost centres are maintained independently in Finance
and HR.

## Why this matters commercially

Four recurring problems were raised at the last Operations Board:

1. Invoices have been raised against clients whose finance account was
   closed, creating write-offs and client relationship damage.
2. Time has been booked by employees to cost centres that no longer exist,
   so project profitability is understated in some practices and
   overstated in others.
3. Leavers have remained active in CRM as opportunity owners, so the
   pipeline report overstates coverage and opportunities go unworked.
4. Duplicate client records mean credit exposure is understated, because
   no single view of a client's outstanding balance exists.

## Data owners

Data quality is not an IT problem in this model. Each domain has a named
business owner accountable for the score and for clearing issues.

| Domain | Accountable owner | Operational steward |
|---|---|---|
| Client and contact | Commercial Director | CRM Administrator |
| Supplier and invoice | Finance Director | Accounts Payable Lead |
| Employee and organisation | HR Director | HR Systems Officer |
| Cost centre (shared) | Finance Director | Management Accountant |

Cost centre is deliberately shared, which is where most cross-system
failures originate and where escalation rules matter.

## Scope of this project

In scope: automated rule execution across the three extracts, a scorecard
by domain and by owner, an issue lifecycle with ownership and SLA, and
trend reporting.

Out of scope: fixing data at source, master data management tooling, and
any change to the source systems themselves. The platform detects,
quantifies, assigns and tracks. Remediation stays with the owning business
function.