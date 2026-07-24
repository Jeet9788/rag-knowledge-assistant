# Northwind Labs — Incident Response Runbook

## Severity levels
SEV-1 means a complete outage or data loss affecting many customers. SEV-2 means a major
feature is broken or degraded for a significant number of users. SEV-3 covers minor issues
that have a workaround. The severity is set by the responding engineer and can be raised
later as impact becomes clear.

## Declaring an incident
Anyone can declare an incident. Declaring early is encouraged; it is better to open an
incident and stand it down than to delay. Opening an incident creates a dedicated channel
and notifies the responsible team.

## Roles during an incident
The incident commander coordinates the response and owns communication. A separate
engineer investigates the technical cause so the commander can focus on coordination. For
large incidents a communications lead posts customer updates.

## Communication
Post a status update at a regular cadence even when there is nothing new, so stakeholders
know the incident is being handled. Keep customer-facing language factual and free of
internal jargon.

## Mitigation and rollback
Prefer mitigating customer impact first — for example by rolling back the most recent
deployment — before spending time on a full root-cause fix. A clean rollback is almost
always faster than a forward fix under pressure.

## After the incident
Every significant incident gets a written review focused on contributing causes and
process, not individual blame. Action items from the review are tracked to completion like
any other work.
