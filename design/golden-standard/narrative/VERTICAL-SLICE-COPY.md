# Final vertical-slice copy

Status: accepted P1R2 source of truth
Authority: `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Instruction: use visible copy verbatim in every P4 direction. Layout may change; wording may not.

---

## Global navigation

**Logo accessible name**  
Dagg — Home

**Links**  
Transformation  
WorkGraph  
Build  
Impact  
Company

**Primary navigation action**  
Start an assessment

**Mobile control**  
Menu

---

## 1 · Hero

**Eyebrow**
AI-native transformation

**H1**  
We redesign how your company works — then build what makes it AI-native.

**Body**  
Dagg combines strategic foresight, company-building experience and engineering to decide what should change, build the agents or software the decision requires, and create a governed path into operation and learning.

**Primary action**  
Start an assessment

**Secondary action**  
See the decision model

**Artifact title**  
Supplier payment exception

**Artifact provenance**  
Representative WorkGraph record · synthetic data

**One-pass lifecycle sequence**  
Mismatch found → Draft prepared → Release withheld → Finance decides → Record updated

**Motion controls**  
Pause motion  
Replay

**Default state summary**  
A payment mismatch is found. The agent may prepare a draft, but it stays withheld until Finance resolves the exception.

**Artifact caption**  
The same company context moves from evidence to decision, build and governed operation.

**Artifact disclosure**  
All artifacts on this page are constructed examples, not client data or production deployments.

---

## 2 · Stakes

**H2**
A company moves at the speed of its handoffs.

**Body**
Machines can execute continuously. A company still slows where context, ownership and decisions must be reconstructed by hand. Those handoffs are where the gap compounds.

---

## 3 · Transform and decide

**Eyebrow**  
The strategic decision

**H2**  
The first decision is what not to automate.

**Body**  
We map how work actually moves, then choose what to preserve, simplify, automate, rebuild or retire. The smallest justified intervention wins.

**Outcome summary**  
Five outcomes. The build is a result, never a premise.

### Preserve

**Title**  
Keep the work as it is.

**Choose when**  
The work is proportionate to its value, and human judgment is essential.

**Do not choose when**  
Delay, rework or unclear ownership is quietly compounding.

### Simplify

**Title**  
Remove work before automating it.

**Choose when**  
The outcome matters but steps or approvals no longer do.

**Do not choose when**  
A control or exception protects something material.

### Automate

**Title**  
Let agents execute a stable path.

**Choose when**  
Inputs, rules, exceptions and success criteria can be made explicit.

**Do not choose when**  
The operating logic is still contested or changing.

### Rebuild

**Title**  
Redesign the workflow and its software together.

**Choose when**  
The current system preserves the wrong process or blocks the target operating model.

**Do not choose when**  
A bounded automation is enough.

### Retire

**Title**  
Stop doing the work.

**Choose when**  
The activity no longer changes a decision, protects a requirement or serves the customer.

**Do not choose when**  
The value is merely hidden or poorly measured.

**Closing line**  
A recommendation is not complete until it names an owner and the evidence that would change it.

**Human role**  
People set intent, define requirements, decide material exceptions and verify outcomes. AI carries routine execution inside those boundaries.

**Contextual text link**  
Explore Transformation

---

## 4 · WorkGraph

**Eyebrow**  
Company context

**H2**  
The map becomes part of the system.

**Body**  
WorkGraph keeps the workflow, evidence, decisions, exceptions and controls behind an intervention in one company-specific context layer. The same record informs strategy, the Factory build and what happens in operation.

**Artifact provenance**  
Representative WorkGraph record · synthetic data

**Record fields**

- Source: purchase order, goods receipt, invoice, payment policy.
- Captured state: invoice and receipt disagree; release is awaiting review.
- System: finance platform.
- Work item: payment exception.
- Owner: Finance owner.
- Exception: source mismatch.
- Decision state: automate preparation; human approval for release.
- Permission: agent prepares; Finance releases.
- Provenance: this synthetic record.

### Map

Approved sources reveal an invoice-receipt mismatch requiring Finance review.

### Decide

Automate preparation; preserve human approval for release. Finance owns the decision and the exception evidence that could reverse it.

### Build

Factory receives the purchase order, goods receipt, invoice, payment policy, permission boundary and evaluation cases.

### Govern

The agent may prepare a payment draft from approved sources. Only the accountable Finance owner may release it.

### Operate

When source records disagree, the draft is withheld from release. Finance chooses whether to correct, reject or return the item to the manual path. The decision and evidence return to WorkGraph.

**Closing line**  
Each decision, evaluation and operating record can strengthen the next intervention. Models can change; company context and learning need not restart from zero.

**Contextual text link**  
Explore WorkGraph

---

## 5 · Factory

**Eyebrow**  
From decision to execution

**H2**  
The decision becomes a build with a boundary.

**Body**  
Dagg Factory turns the intervention into an agent or software with the context, tools, permissions and evaluations needed to act within the decision.

Reusable tools and evaluations are designed to improve the next build. The delivery system is designed to keep client-specific context out of reusable cross-engagement patterns.

### Automate what stays

**Build-plan provenance**  
Illustrative Factory build plan · not a client deployment

**Build-plan states**  
Context received  
Build plan  
Evaluation  
Ready for governed review

**Build plan**

- Intervention: prepare the payment draft; preserve human approval for release.
- Context: purchase order, goods receipt, invoice and payment policy.
- Tools: approved finance-system read and payment-draft tool.
- Permission: prepare only; never release.
- Evaluation: when source records disagree, the draft is withheld from release and the exception is routed to the Finance owner.
- Release owner: Finance owner.
- Way back: disable the agent, remove the draft and return the item to the manual queue.

### Rebuild what should change

**Build plan**

- Intervention: purpose-built exception workspace.
- Target workflow: a mismatch opens review; the draft cannot advance until resolved.
- Application boundary: exception review and draft state; finance remains the system of record.
- Interfaces: read source records; return the reviewed decision.
- Behavior: show the conflict, capture the owner decision and update draft state.
- Acceptance test: a mismatch blocks release; only the Finance owner resolves it.
- Release owner: Finance owner.
- Way back: disable the write path; return the item to the manual queue.

**Contextual text link**  
Explore Build

---

## 6 · Two surfaces of impact

**Eyebrow**
One transformation, two surfaces

**H2**
AI-native changes how the company works — and how customers work with it.

**Body**
Inside the company, agents carry stable execution while people direct, decide and verify. Outside it, the same governed capabilities can meet customers wherever they work — without leaving the company’s rules, permissions or source of truth behind.

**Product-moment title**
The product meets the customer where the customer works.

**Product-moment provenance**
Illustrative capability · synthetic data · not a client deployment

**Customer request**
Which parts of my month-end close need attention, and what can be resolved now?

**Context resolved**
Two supporting documents are missing. One VAT discrepancy needs accountant review. The filing deadline is in five days.

**Permissioned response**
Prepare the two document requests. Route the VAT discrepancy to the accountable adviser before any tax decision or external communication.

**Boundary**
The agent may assemble evidence and prepare drafts. The adviser approves external requests and resolves the material tax exception.

**Evidence returned**
Every source, proposed action, permission check and owner returns to the company system of record.

**Closing line**
The interface can change. The company’s context, rules and accountability do not.

---

## 7 · Govern, operate and prove

**Eyebrow**  
Human control

**H2**  
Execution is not complete until it runs within bounds.

**Body**  
The client can run the result, or Dagg can take a defined operating role. In either model, action stops at material exceptions, accountable people decide and the record returns evidence to the next cycle.

**Operating-record title**  
One material exception

**Operating-record provenance**  
Illustrative operating record · constructed example

### Intent received

Prepare a supplier payment draft for Finance review from approved company records.

### Context resolved

The purchase order, goods receipt, invoice and payment policy are resolved from approved sources.

### Action proposed

The agent prepares a payment draft from approved sources. It remains withheld from release.

### Boundary triggered

The invoice and goods receipt disagree. The draft remains withheld and the exception is routed to Finance.

### Human decision recorded

The Finance owner confirms the exception and returns the item for source correction.

### Outcome and way back recorded

No payment proceeds. The decision and evidence remain recorded; the agent can be disabled and the item returned to the manual queue.

**Control rail**

- Boundary: approved sources and tools only.
- Escalation: material exceptions require an accountable owner.
- Way back: each permitted action needs a defined pause, inspection or reversal path.

**Closing line**  
Speed matters only when the company can see what happened, why it happened and who remains accountable.

**Eyebrow**  
Impact

**Gateway title**  
How we evidence change — and where the evidence stops.

**Body**  
Impact distinguishes companies built from companies transformed. Evidence is published only with a verified starting condition, strategic thesis, operating change, outcome, timeframe, source and limits.

**Contextual text link**  
Explore Impact

---

## 8 · Assessment close

**Eyebrow**  
Start with one path

**H2**  
Make the first decision before making the first build.

**Body**  
An assessment follows one material path to a decision. You leave with the evidence to act — or the reason not to.

**Deliverable strip**  
Operating map · Recommendation or refusal · Intervention brief · Accountable owner · Evidence that would change the decision

**Boundary**  
The assessment is a decision instrument, not a commitment to a build.

**Primary action**  
Start an assessment
