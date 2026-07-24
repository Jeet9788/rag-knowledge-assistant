# Northwind Labs — Engineering Handbook

## 1. Onboarding

Every new engineer completes a 30-day onboarding period. During onboarding you are
paired with an onboarding buddy, given access to the internal documentation, and
expected to ship at least one small production change by the end of week two. Your
manager schedules a formal 30-day check-in to confirm you have completed onboarding
before any remote-work or on-call eligibility begins.

## 2. Remote work policy

New engineers may work remotely up to three days per week after completing the 30-day
onboarding period. Before onboarding is complete, engineers are expected to be in the
office so they can pair closely with their team.

Fully remote arrangements require written approval from a director and a documented
overlap of at least four hours per day with the team's core timezone. Requests for a
fully remote arrangement are reviewed once per quarter.

Core hours are 10:00 to 15:00 local team time. Engineers may set the rest of their
schedule flexibly as long as they cover core hours and attend standups.

## 3. Equipment and stipends

Each engineer receives a home-office equipment stipend once per employment term. The
stipend covers a monitor, keyboard, mouse, and an ergonomic chair. Laptops are issued
separately by IT and are refreshed every three years. Software licenses needed for your
role are expensed through your manager rather than the stipend.

## 4. Code review and quality

Every change must be reviewed by at least one other engineer before it is merged. Pull
requests should be small enough to review in under thirty minutes; larger changes should
be split. A change may not be merged while continuous integration is failing. Any change
that touches authentication, billing, or data deletion requires review by a second
senior engineer.

Every merged change must include tests. A pull request that lowers overall test coverage
is blocked automatically and requires an explicit override from a tech lead.

## 5. Deadlines and delivery

Teams commit to deadlines at the start of each two-week sprint. If a deadline is at risk,
the owning engineer is expected to raise it in the daily standup at least three working
days before the deadline, not on the deadline itself. Deadlines are treated as team
commitments: a slipping deadline is a planning signal, not an individual failure, but
silence about a known slip is treated as a serious process problem.

## 6. On-call

On-call rotation begins only after an engineer has completed onboarding and shadowed at
least two on-call shifts. Each rotation lasts one week. The primary on-call engineer must
acknowledge a page within fifteen minutes. Any incident rated SEV-1 or SEV-2 requires a
written post-incident review within three business days.

## 7. Security policy

All engineers must enable two-factor authentication on every company account. Passwords
must be at least sixteen characters and are managed through the company password manager;
sharing passwords over chat or email is prohibited.

Customer data may only be accessed for a documented support or engineering reason, and
production database access is logged and reviewed monthly. Company laptops must have full
disk encryption enabled. A lost or stolen device must be reported to security within one
hour of discovery.

## 8. Expenses and travel

Routine expenses under $100 can be approved by your manager. Anything above $100, and all
travel, requires approval before the expense is incurred. Conference attendance is
supported once per year per engineer, subject to manager approval and available budget.

## 9. Time off

Engineers accrue paid time off from their start date and may begin taking it after the
30-day onboarding period. Time off should be requested at least two weeks in advance for
anything longer than two consecutive days. There is no cap on sick leave, but absences
longer than three consecutive days may require a note per local regulations.
