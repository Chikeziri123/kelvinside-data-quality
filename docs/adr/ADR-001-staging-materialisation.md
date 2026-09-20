# ADR-001: Materialise the staging layer as tables rather than views

Status: Accepted
Date: 21 September 2026

## Context

Source data arrives as CSV extracts read directly from disk by DuckDB.
The staging layer casts and standardises those extracts for the rule
suite to run against.

Views were the initial choice. They cost nothing to build, and they always
reflect the current contents of the extract files, which suits a nightly
process where the data changes underneath you.

## Problem

A view definition carries the CSV path inside it. That path is relative to
the dbt project directory, so any query against a staging view only
resolves when the querying process happens to be running from that
directory. Querying the warehouse from the project root failed, and Power
BI, a scheduler, or anyone cloning the repository would hit the same wall.

The dependency was invisible until exercised, which is the worst kind.

## Decision

Materialise staging models as tables. The CSVs are read once during
`dbt run` and the results are persisted into the DuckDB file.

## Consequences

Positive:
- The warehouse is self-contained and can be queried from any working
  directory, by any tool, without the source files being present.
- Downstream rule execution runs against persisted data rather than
  re-parsing CSVs on every query.
- Power BI connects to the database without needing the raw extracts.

Negative:
- Staging is only as fresh as the last `dbt run`, so the pipeline order
  now matters. Generation, then run, then test.
- Storage is duplicated between the CSVs and the database. At this volume,
  a few megabytes, that is immaterial.

## Alternatives considered

**Absolute paths in the source definition.** Would have worked on one
machine and broken on every other. Rejected as portability theatre.

**Loading the CSVs with a Python script before dbt.** Adds a step outside
the dbt lineage graph, so the dependency between extract and model stops
being visible in the DAG. Rejected in favour of keeping one orchestration
tool.

## Revisit when

Source volumes reach a scale where full rebuild time becomes noticeable,
at which point incremental materialisation on the invoice and opportunity
models becomes the sensible next step.