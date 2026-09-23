# FinPilot AI --- Minimal 30-Day MVP Plan

## 1. Project Goal

Build a small but technically strong AI fintech project in approximately
30 days.

### One-line description

> FinPilot is an AI payment investigation assistant that analyzes a
> failed payment's transaction data, events, logs, and internal
> documentation to identify the likely root cause and provide
> evidence-backed recommendations.

### Core question the product answers

> **Why did this payment fail?**

The project should demonstrate:

-   Backend development
-   Fintech/payment-domain knowledge
-   LLM integration
-   AI tool calling
-   Simple RAG
-   Evidence-based answers
-   Basic frontend development
-   Testing
-   Docker
-   Deployment

## 2. Scope Rule

This is an MVP.

The goal is **not** to build a complete payment operations platform.

The project is finished when this flow works reliably:

``` text
Payment
   ↓
Investigate
   ↓
AI reads payment + events + logs + documentation
   ↓
Root Cause
   ↓
Evidence
   ↓
Recommendation
```

Do not add new infrastructure unless the core flow requires it.

------------------------------------------------------------------------

# 3. Final MVP Architecture

``` text
                    React UI
                       |
                    REST API
                       |
                    FastAPI
                       |
                  AI Agent
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
  Payment Tool     Event Tool      Log Tool
        |              |              |
        +--------------+--------------+
                       |
                       v
                 PostgreSQL
                       |
                 Payment Data
                 Event Data
                 Log Data

                       +
                       |
                       v
                 Simple RAG
                       |
                   pgvector
                       |
                  Documentation

                       |
                       v
                 Evidence Set
                       |
                       v
                    AI RCA
```

------------------------------------------------------------------------

# 4. Technology Stack

Keep the stack intentionally small.

## Frontend

-   React
-   TypeScript
-   Vite

## Backend

-   Python
-   FastAPI
-   Pydantic
-   SQLAlchemy

## Database

-   PostgreSQL
-   pgvector

## AI

-   One LLM provider/model initially
-   Optional local MLX model through an adapter

## Deployment

-   Docker
-   Docker Compose

## Version Control

-   Git
-   GitHub

------------------------------------------------------------------------

# 5. Do NOT Build These

These are explicitly outside the MVP.

-   Redis
-   Kafka
-   Kubernetes
-   Multiple microservices
-   Complex authentication
-   Complex RBAC
-   Jev
-   OKF
-   Multiple vector databases
-   Custom model training
-   Fine-tuning
-   Mobile application
-   Real payment processing
-   Real customer data
-   Complex fraud detection
-   Large analytics dashboards
-   Complex incident-management system

If everything is finished early, these can become future experiments.

------------------------------------------------------------------------

# 6. Core User Flow

``` text
Dashboard
    ↓
Search Payment
    ↓
Payment Details
    ↓
Click "Investigate"
    ↓
AI Investigation
    ↓
Root Cause
    ↓
Evidence
    ↓
Recommendation
```

This is the only flow that must be excellent.

------------------------------------------------------------------------

# 7. UI Design

Build only three primary screens.

## Screen 1 --- Payments Dashboard

Example:

``` text
FinPilot

Payment Search
--------------------------------
[ PAY-1001                    ]

Recent Payments
--------------------------------
PAY-1001   $2,450   FAILED   R01
PAY-1002   $800     SUCCESS
PAY-1003   $120     FAILED   TIMEOUT
```

Keep it simple.

No complicated analytics.

------------------------------------------------------------------------

# 8. Screen 2 --- Payment Details

Example:

``` text
PAY-1001

$2,450 USD
FAILED
Gateway: ExamplePay
Error: R01

--------------------------------

Payment Timeline

Created
   ↓
Validated
   ↓
Gateway Request
   ↓
Gateway Response: R01
   ↓
Payment Failed

--------------------------------

Events

14:31:52 PAYMENT_CREATED
14:31:53 VALIDATED
14:32:17 GATEWAY_REQUEST
14:32:18 GATEWAY_RESPONSE
14:32:18 PAYMENT_FAILED

--------------------------------

Logs

14:32:17 Sending payment to gateway
14:32:18 Gateway returned R01
14:32:18 Marking payment as failed

--------------------------------

[ Investigate with FinPilot ]
```

------------------------------------------------------------------------

# 9. Screen 3 --- Investigation

Example:

``` text
FinPilot Investigation

Payment: PAY-1001

Question:
Why did this payment fail?

--------------------------------

Investigation Progress

✓ Payment retrieved
✓ Events retrieved
✓ Logs searched
✓ Documentation searched

--------------------------------

ROOT CAUSE

Insufficient funds.

--------------------------------

EVIDENCE

• Gateway returned R01.
• Payment changed to FAILED immediately
  after the gateway response.
• No application error was found in the logs.

--------------------------------

SOURCE

ACH Error Codes — R01

--------------------------------

RECOMMENDATION

Do not retry immediately.
Ask the customer to fund the account first.

--------------------------------

Confidence: High
```

------------------------------------------------------------------------

# 10. Database

Keep the schema minimal.

## payments

``` text
id
customer_id
amount
currency
payment_method
status
gateway
error_code
created_at
updated_at
```

## payment_events

``` text
id
payment_id
event_type
status
metadata
created_at
```

## payment_logs

``` text
id
payment_id
service
level
message
metadata
created_at
```

## documents

``` text
id
name
category
content
created_at
```

## document_chunks

``` text
id
document_id
content
embedding
metadata
created_at
```

## investigations

``` text
id
payment_id
question
root_cause
evidence
recommendation
confidence
created_at
```

That's enough.

------------------------------------------------------------------------

# 11. Synthetic Payment Data

Never use real customer/payment information.

Generate synthetic data.

Create approximately:

``` text
100–500 payments
```

Include:

-   Successful payments
-   Insufficient funds
-   Invalid account
-   Gateway timeout
-   Gateway error
-   Card decline
-   Duplicate payment

Create a few carefully designed investigation cases.

## Case 1 --- Insufficient funds

``` text
Gateway response:
R01

Expected RCA:
Insufficient funds
```

## Case 2 --- Gateway timeout

``` text
Gateway:
No response

Expected RCA:
Gateway timeout
```

## Case 3 --- Application error

``` text
Application:
Database/processing error

Expected RCA:
Internal application failure
```

## Case 4 --- Gateway outage

``` text
Many payments fail during the same period

Expected RCA:
Possible gateway outage
```

The AI should be able to distinguish these scenarios using evidence.

------------------------------------------------------------------------

# 12. Backend API

Keep APIs minimal.

## Payments

``` http
GET /api/payments
GET /api/payments/{payment_id}
GET /api/payments/{payment_id}/events
GET /api/payments/{payment_id}/logs
```

## Investigation

``` http
POST /api/investigations
GET /api/investigations/{id}
```

## Documents

Only if needed for ingestion:

``` http
POST /api/documents
```

------------------------------------------------------------------------

# 13. AI Architecture

Do not build a complicated autonomous agent.

Use a small tool-based investigation workflow.

``` text
User
  |
  v
AI Agent
  |
  +---- get_payment()
  |
  +---- get_events()
  |
  +---- search_logs()
  |
  +---- search_docs()
  |
  v
Evidence
  |
  v
RCA Generator
  |
  v
Structured Result
```

The AI should never invent payment information.

------------------------------------------------------------------------

# 14. AI Tools

Implement only four tools.

## Tool 1 --- get_payment

``` text
get_payment(payment_id)
```

Returns:

-   amount
-   currency
-   status
-   gateway
-   error code
-   timestamps

## Tool 2 --- get_events

``` text
get_payment_events(payment_id)
```

Returns payment lifecycle events.

## Tool 3 --- search_logs

``` text
search_logs(payment_id, query)
```

Returns relevant application logs.

## Tool 4 --- search_docs

``` text
search_payment_docs(query)
```

Returns relevant documentation.

That's the complete tool set for the MVP.

------------------------------------------------------------------------

# 15. RAG

Use **simple RAG**.

Do not introduce OKF or another knowledge format into the first version.

Create approximately 5--10 Markdown documents.

Example:

``` text
docs/
├── ach-error-codes.md
├── card-decline-codes.md
├── retry-policy.md
├── gateway-runbook.md
├── payment-processing.md
├── timeout-handling.md
└── incident-basics.md
```

Pipeline:

``` text
Markdown
   ↓
Chunk
   ↓
Embedding
   ↓
pgvector
   ↓
Similarity Search
   ↓
Relevant Content
   ↓
LLM
```

------------------------------------------------------------------------

# 16. Example Documentation

## ach-error-codes.md

``` text
R01 — Insufficient Funds
R02 — Account Closed
R03 — No Account
R04 — Invalid Account
```

## retry-policy.md

Explain:

``` text
Which errors can be retried?
Which errors should not be retried?
How long should the system wait?
```

## gateway-runbook.md

Explain:

``` text
Gateway timeout
Gateway rejection
Gateway unavailable
Gateway response mapping
```

Keep the documents short and realistic.

------------------------------------------------------------------------

# 17. AI Response Format

Do not let the frontend depend on arbitrary AI text.

Ask the model to return structured output.

Example:

``` json
{
  "root_cause": "Insufficient funds",
  "confidence": "high",
  "evidence": [
    "Gateway returned R01",
    "Payment changed to FAILED",
    "No application error found"
  ],
  "recommendation": "Do not retry immediately",
  "sources": [
    "ach-error-codes.md"
  ]
}
```

The frontend renders these fields.

------------------------------------------------------------------------

# 18. Investigation Workflow

When the user clicks:

``` text
Investigate
```

The backend starts:

``` text
1. Identify payment
2. Get payment details
3. Get events
4. Search relevant logs
5. Search documentation
6. Collect evidence
7. Determine root cause
8. Generate recommendation
9. Save investigation
10. Return result
```

The model should choose relevant tools rather than blindly calling every
tool when possible.

------------------------------------------------------------------------

# 19. Evidence Rules

The AI should follow these rules:

### Rule 1

Do not claim something that is not supported by retrieved data.

### Rule 2

Separate:

``` text
Observed fact
```

from:

``` text
Inference
```

### Rule 3

If evidence is insufficient, say:

``` text
Insufficient evidence to determine the root cause.
```

### Rule 4

Every documentation-based claim should reference the source.

------------------------------------------------------------------------

# 20. 30-Day Schedule

# Week 1 --- Backend Foundation

## Day 1

-   [ ] Create GitHub repository
-   [ ] Create project structure
-   [ ] Create FastAPI app
-   [ ] Create React app
-   [ ] Create Docker Compose
-   [ ] Start PostgreSQL
-   [ ] Add `.env.example`

Goal:

``` text
Frontend + Backend + PostgreSQL running
```

------------------------------------------------------------------------

## Day 2

-   [ ] Create SQLAlchemy models
-   [ ] Create database tables
-   [ ] Add migrations
-   [ ] Verify database connection

Goal:

``` text
Database schema working
```

------------------------------------------------------------------------

## Day 3

-   [ ] Implement payment repository
-   [ ] Implement payment service
-   [ ] Implement payment APIs
-   [ ] Add API tests

Goal:

``` text
GET /payments
GET /payments/{id}
```

working.

------------------------------------------------------------------------

## Day 4

-   [ ] Generate synthetic payment data
-   [ ] Generate events
-   [ ] Generate logs
-   [ ] Create failure scenarios

Goal:

``` text
Realistic test data available
```

------------------------------------------------------------------------

## Day 5

-   [ ] Build payment list UI
-   [ ] Add search
-   [ ] Display status
-   [ ] Display gateway
-   [ ] Display error code

Goal:

``` text
User can find a payment
```

------------------------------------------------------------------------

## Day 6

-   [ ] Build payment details
-   [ ] Build timeline
-   [ ] Display events
-   [ ] Display logs
-   [ ] Add Investigate button

Goal:

``` text
User can understand a payment manually
```

------------------------------------------------------------------------

## Day 7

-   [ ] Connect frontend and backend
-   [ ] Fix UI/API issues
-   [ ] Clean project structure
-   [ ] Commit milestone

Milestone:

> Payment investigation data is visible end-to-end.

------------------------------------------------------------------------

# Week 2 --- AI

## Day 8

-   [ ] Connect LLM
-   [ ] Create model adapter
-   [ ] Test basic prompt
-   [ ] Add environment configuration

Goal:

``` text
Backend can communicate with model
```

------------------------------------------------------------------------

## Day 9

-   [ ] Implement `get_payment`
-   [ ] Implement `get_events`
-   [ ] Implement `search_logs`
-   [ ] Test tools independently

------------------------------------------------------------------------

## Day 10

-   [ ] Implement basic tool calling
-   [ ] Let model choose tools
-   [ ] Return tool results to model

Goal:

``` text
Question
 ↓
Tool
 ↓
Data
 ↓
Answer
```

------------------------------------------------------------------------

## Day 11

-   [ ] Create documentation
-   [ ] Create 5--10 Markdown files
-   [ ] Add payment error information
-   [ ] Add retry policy
-   [ ] Add gateway information

------------------------------------------------------------------------

## Day 12

-   [ ] Configure pgvector
-   [ ] Implement document chunking
-   [ ] Generate embeddings
-   [ ] Store embeddings

------------------------------------------------------------------------

## Day 13

-   [ ] Implement `search_payment_docs`
-   [ ] Test semantic search
-   [ ] Add source references

------------------------------------------------------------------------

## Day 14

-   [ ] Combine all tools
-   [ ] Implement investigation workflow
-   [ ] Generate structured RCA

Milestone:

> FinPilot can investigate a payment from backend data and
> documentation.

------------------------------------------------------------------------

# Week 3 --- Product Experience

## Day 15

-   [ ] Build investigation page
-   [ ] Display question
-   [ ] Display root cause
-   [ ] Display evidence
-   [ ] Display recommendation
-   [ ] Display confidence

------------------------------------------------------------------------

## Day 16

-   [ ] Add investigation progress
-   [ ] Show tool execution steps
-   [ ] Add loading state

Example:

``` text
✓ Payment retrieved
✓ Events retrieved
✓ Logs searched
✓ Documentation searched
→ Generating RCA
```

------------------------------------------------------------------------

## Day 17

-   [ ] Save investigations
-   [ ] Add investigation history
-   [ ] Display previous investigations

------------------------------------------------------------------------

## Day 18

-   [ ] Improve error handling
-   [ ] Handle payment not found
-   [ ] Handle model failure
-   [ ] Handle database failure
-   [ ] Handle insufficient evidence

------------------------------------------------------------------------

## Day 19

-   [ ] Improve AI prompts
-   [ ] Improve tool descriptions
-   [ ] Improve structured response
-   [ ] Add evidence requirements

------------------------------------------------------------------------

## Day 20

-   [ ] Add SSE streaming if useful
-   [ ] Stream investigation progress
-   [ ] Improve user experience

If SSE starts consuming too much time, skip it.

------------------------------------------------------------------------

## Day 21

-   [ ] UI cleanup
-   [ ] Typography
-   [ ] Spacing
-   [ ] Empty states
-   [ ] Loading states
-   [ ] Error states

Milestone:

> A user can complete the entire investigation flow comfortably.

------------------------------------------------------------------------

# Week 4 --- Quality and Portfolio

## Day 22

-   [ ] Backend tests
-   [ ] Payment API tests
-   [ ] Tool tests
-   [ ] Investigation tests

------------------------------------------------------------------------

## Day 23

-   [ ] RAG evaluation
-   [ ] Create 10--20 known questions
-   [ ] Check retrieved documents
-   [ ] Check final answers

Example:

``` text
Question:
What does R01 mean?

Expected:
Insufficient funds
```

------------------------------------------------------------------------

## Day 24

-   [ ] Security review
-   [ ] Validate inputs
-   [ ] Keep tools read-only
-   [ ] Check environment variables
-   [ ] Remove secrets from Git

------------------------------------------------------------------------

## Day 25

-   [ ] Docker cleanup
-   [ ] Verify fresh installation
-   [ ] Test:

docker compose up


    Goal:

    > A new machine can start the application easily.

    ---

    ## Day 26

    - [ ] Improve README
    - [ ] Add architecture diagram
    - [ ] Add screenshots
    - [ ] Add setup instructions
    - [ ] Add sample investigation

    ---

    ## Day 27

    - [ ] Deploy application
    - [ ] Verify production environment
    - [ ] Test complete investigation

    ---

    ## Day 28

    - [ ] Fix production issues
    - [ ] Clean Git history
    - [ ] Clean unused code
    - [ ] Remove unused dependencies

    ---

    ## Day 29

    Record a 3–5 minute demo:

    ```text
    1. Open FinPilot
    2. Search PAY-1001
    3. Open payment
    4. Show timeline
    5. Click Investigate
    6. Show AI investigation
    7. Show evidence
    8. Show documentation source
    9. Show root cause
    10. Show recommendation

------------------------------------------------------------------------

## Day 30

Prepare:

-   [ ] GitHub README
-   [ ] Resume project entry
-   [ ] LinkedIn post
-   [ ] Architecture diagram
-   [ ] Demo video
-   [ ] Interview explanation

Then stop adding features.

------------------------------------------------------------------------

# 21. Cursor + Agent Workflow

Use both.

## Cursor IDE

Use Cursor for:

-   Understanding code
-   Reviewing changes
-   Debugging
-   Navigating files
-   Architecture
-   Manual edits

## Cursor Agent

Use Agent for:

-   Implementing focused features
-   Multi-file changes
-   Running tests
-   Fixing test failures
-   Repetitive code

Recommended workflow:

``` text
You define feature
       ↓
Agent implements feature
       ↓
Agent runs tests
       ↓
You inspect changes in Cursor
       ↓
You fix/revise
       ↓
Git commit
```

------------------------------------------------------------------------

# 22. Agent Task Size

Do not give Agent:

``` text
Build the entire FinPilot application.
```

Give it focused tasks.

Example:

``` text
Implement the Payment SQLAlchemy model.

First inspect the existing project structure.
Create the model and Pydantic schemas.
Add the migration.
Add unit tests.
Run the tests.
Do not modify unrelated files.
```

Then move to the next task.

------------------------------------------------------------------------

# 23. Git Milestones

Use milestones:

``` text
v0.1 — Payment data
v0.2 — Payment UI
v0.3 — AI integration
v0.4 — Tool calling
v0.5 — RAG
v0.6 — Investigation workflow
v0.7 — Testing
v1.0 — Portfolio release
```

------------------------------------------------------------------------

# 24. Definition of Done

FinPilot is finished when this works:

``` text
PAY-1001
    ↓
Investigate
    ↓
AI retrieves:
    ├── Payment
    ├── Events
    ├── Logs
    └── Documentation
    ↓
Evidence
    ↓
Root Cause
    ↓
Recommendation
```

Example final output:

``` text
Root Cause
----------
Insufficient funds.

Evidence
--------
• Gateway returned R01.
• Payment transitioned to FAILED.
• No application error was found.

Source
------
ACH Error Codes — R01

Recommendation
--------------
Do not retry immediately.
```

------------------------------------------------------------------------

# 25. Interview Talking Points

## Why this project?

Payment failures often require engineers to investigate information
across multiple sources.

FinPilot demonstrates how an AI assistant can bring those sources
together and reduce manual investigation.

## Why an AI agent?

The agent can decide which information it needs instead of receiving a
fixed context every time.

## Why tools?

Tools ground the model in actual payment and application data.

## Why RAG?

Payment operations contain domain-specific documentation that the model
should retrieve rather than assume.

## Why PostgreSQL + pgvector?

It keeps the architecture small and avoids adding a separate vector
database for the MVP.

## How do you reduce hallucination?

-   Tool-based data retrieval
-   Evidence requirements
-   Structured responses
-   Source references
-   Evaluation questions
-   Explicit insufficient-evidence handling

## How would you scale it?

The modular monolith could later be split into:

``` text
Payment Service
Investigation Service
Document Service
Log Service
Event Service
```

But that is intentionally not part of the MVP.

------------------------------------------------------------------------

# 26. Future Ideas --- Only After v1

These are optional future versions:

### v1.1

-   Better evaluation
-   More payment scenarios
-   Better UI

### v1.2

-   Redis
-   Streaming
-   More observability

### v2

-   Kafka/event streaming
-   Incident detection
-   More sophisticated agent orchestration

### v3

-   Decision model/agent routing
-   Advanced knowledge representation
-   Multi-service architecture

Do not build these before the MVP works.

------------------------------------------------------------------------

# 27. Final Scope

The project should contain:

``` text
React
   ↓
FastAPI
   ↓
PostgreSQL
   ├── Payments
   ├── Events
   ├── Logs
   └── Investigations

pgvector
   ↓
Simple RAG

LLM
   ↓
4 Tools
   ├── Payment
   ├── Events
   ├── Logs
   └── Documents

   ↓
Root Cause
   +
Evidence
   +
Recommendation
```

That is enough.

The objective is not to build the biggest project.

The objective is to build a **complete project that works, is
deployable, looks professional, and gives you a strong technical story
in interviews.**

------------------------------------------------------------------------

# 28. First Implementation Task

Before writing backend code:

## Design these three screens

``` text
1. Dashboard
2. Payment Details
3. Investigation Result
```

Focus on this interaction:

``` text
Payment Details
       ↓
[ Investigate ]
       ↓
Investigation Progress
       ↓
Root Cause
       ↓
Evidence
       ↓
Recommendation
```

Once these screens are clear, derive the API and database requirements
from them.

This keeps FinPilot small and prevents unnecessary engineering.
