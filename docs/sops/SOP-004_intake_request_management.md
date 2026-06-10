# SOP-004: LMS Intake Request Management

| Field | Value |
|-------|-------|
| **Trigger** | End-user or stakeholder submits LMS support/enhancement request |
| **Owner** | Learning Analytics Intern |
| **SLA Target** | Resolve within 5 business days |

## Request Types

| Type | Example | Default Owner |
|------|---------|---------------|
| New Course Request | "We need a battery safety course for Manufacturing" | Learning Tech Team |
| Enrollment Exception | "Contractor needs temporary access to FAA Safety" | LMS Admin |
| Access Issue | "User cannot log into Moodle" | LMS Admin |
| Completion Override | "User completed training offline — needs credit" | HR Partner |
| Report Request | "Need Q2 compliance report for Flight Ops" | Learning Analytics Intern |

## Workflow

1. **Receive** request via email, Smartsheet, or intake form
2. **Log** in `mdl_intake_requests` table with status = `Open`
3. **Triage** within 24 hours — assign owner and priority
4. **Update** status to `In Progress` when work begins
5. **Resolve** — complete action, update status to `Resolved`
6. **Close** — confirm with requester, set status to `Closed`, record `resolved_date`
7. **Report** weekly SLA metrics in Power BI Page 5

## SLA Calculation

```
SLA Days = resolved_date - created_date
On-Time = SLA Days <= 5 business days
```
