# Unit 3 — System Requirements Engineering, Elicitation Techniques & Analysis Paradigms
## Lesson 1 — The Requirements Engineering Pipeline & Specification Taxonomy (IEEE 830 / ISO 29148)

### 1. The Requirements Engineering Discipline: Foundational Principles

In software engineering, a **requirement** is defined as:
> *A condition or capability needed by a user to solve a problem or achieve an objective, or a condition/capability that must be met or possessed by a system or system component to satisfy a contract, standard, specification, or other formally imposed document.* (IEEE 610.12 / ISO/IEC/IEEE 29148).

At its core, a software requirement encapsulates:
1. **Data Ingestion and Processing:** The precise input data structures, validation rules, state transformations, and persistence policies.
2. **Business Process Control:** Enforcing business rules, transactional boundaries, audit trails, and multi-actor operational workflows.
3. **Information Generation:** The timely synthesis of raw transactional data into deterministic reports, operational dashboards, and downstream API payloads.
4. **Decision & Management Support:** Supplying strategic analytical signals, predictive trends, and compliance metrics to organizational leadership.

**Requirements Engineering (RE)** is the disciplined, systematic application of scientific, mathematical, and management principles to discover, analyze, document, validate, and maintain software requirements throughout the system lifecycle. Empirical research across the software industry (e.g., Standish Group CHAOS studies) reveals that over **60% of all software defects** originate during the requirements phase, while fixing an error during requirements analysis costs **up to 100 to 200 times less** than refactoring that same defect once the system has been deployed to production.

```
+---------------------------------------------------------------------------------------------------+
|                        THE RELATIVE COST OF REPAIRING SOFTWARE DEFECTS                           |
|                                                                                                   |
|  Phase Detected:          Relative Cost Multiplier:                                               |
|  [ Requirements ]         1x       (Baseline: Minutes of text editing / diagram revision)        |
|  [ Architecture/Design ]  3x - 5x  (Hours of architectural refactoring)                           |
|  [ Implementation ]       10x      (Days of code rewriting and unit re-testing)                  |
|  [ System Testing ]       30x - 50x(Weeks of integration debugging, regression cycles)           |
|  [ Post-Deployment ]      100x - 200x+ (Disaster recovery, data corruption, legal liability)     |
+---------------------------------------------------------------------------------------------------+
```

---

### 2. The Three-Tier Requirements Hierarchy

Requirements do not exist in a flat, homogeneous list. Rather, they form an ontological pyramid spanning three distinct levels of abstraction: **Business Requirements**, **User Requirements**, and **Software/System Requirements**.

```
                           / \
                          /   \
                         /     \
                        /  BRD  \          <--- TIER 1: BUSINESS REQUIREMENTS
                       /---------\              (Why build it? Value proposition & ROI)
                      /           \
                     /    USER     \       <--- TIER 2: USER REQUIREMENTS
                    / REQUIREMENTS  \           (Who uses it? Operational workflows & user stories)
                   /-----------------\
                  /     SYSTEM &      \    <--- TIER 3: SOFTWARE / SYSTEM REQUIREMENTS (SRS)
                 /   FUNCTIONAL (SRS)  \        (What specifically must the software execute?)
                /-----------------------\
```

#### 2.1 Tier 1: Business Requirements (The "Why")
Authored by executive sponsors, product strategists, and lead business analysts at project inception, business requirements are synthesized into the **Business Requirements Document (BRD)**. The BRD formalizes the commercial rationale, strategic vision, competitive differentiator, and measurable financial return on investment (ROI).

Every business requirement statement must link a tangible software capability to a measurable organizational outcome:
$$\text{BRD Statement Format: } \text{"The [System Name] shall [achieve objective] in order to [realize measurable business value]."}$$

* **Example:** *"The Autonomous Healthcare Logistics Platform shall automate inpatient medication replenishment in order to decrease medication administration delays by $35\%$ and reduce expired drug inventory write-offs by $\$1.2\text{M}$ annually."*

#### 2.2 Tier 2: User Requirements (The "Who & How")
User requirements articulate the specific operational tasks, interaction scenarios, and workflow goals that human actors and external systems must achieve when interfacing with the platform. They describe the system strictly from an external operational perspective, abstracting away relational schemas, database engines, or low-level protocols.

* **Format:**
  $$\text{"The [User Role] shall [interact with the software] in order to [fulfill a specific task]."}$$
* **Common Representations:**
  - **Agile User Stories:** *"As an On-Duty Triage Nurse, I want to scan a patient's biometric wristband with a handheld terminal so that I can instantly retrieve their verified allergy contraindications before administering emergency therapy."*
  - **Structured Use Case Narratives (Cockburn Format):** Defining primary actors, preconditions, postconditions, sunny-day main success scenarios, and alternative error flows (e.g., Mental Health Clinic [MHC] patient intake and crisis alert dispatch).

#### 2.3 Tier 3: Software & System Requirements (The "What")
Software Requirements translate the high-level business goals and user workflows into an exhaustive, unambiguous engineering specification known as the **Software Requirements Specification (SRS)**. The SRS is the formal legal and technical contract between the commissioning client and the software engineering organization.

Under modern standards, software requirements are bifurcated into:
1. **Functional Requirements (FR):** Mathematical formulations of inputs, algorithmic state transformations, and output structures.
2. **Non-Functional Requirements (NFR):** The quantitative quality attributes, service level objectives (SLOs), security boundaries, and environmental constraints.
3. **Domain Requirements:** Invariant constraints dictated by the laws, mathematics, or regulatory bodies of the specific industry (e.g., ACID transactional isolation in banking; 21 CFR Part 11 electronic signatures in biomedical software).

---

### 3. Architecture of the Requirements Engineering Process

The Requirements Engineering lifecycle is not an ad-hoc conversation; it is a closed-loop cybernetic feedback process consisting of six interconnected phases:

{{ media:sam-requirements-hierarchy-diagram }}

```
+---------------------------------------------------------------------------------------------------+
|                        THE SIX-STAGE REQUIREMENTS ENGINEERING PIPELINE                            |
|                                                                                                   |
|  +--------------------+      +----------------------+      +----------------------+               |
|  | 1. FEASIBILITY     | ---> | 2. ELICITATION &     | ---> | 3. ANALYSIS &        |               |
|  |    ASSESSMENT      |      |    DISCOVERY         |      |    NEGOTIATION       |               |
|  +--------------------+      +----------------------+      +----------------------+               |
|                                                                       |                           |
|                                                                       v                           |
|  +--------------------+      +----------------------+      +----------------------+               |
|  | 6. REQUIREMENTS    | <--- | 5. VERIFICATION &    | <--- | 4. FORMAL            |               |
|  |    MANAGEMENT (RTM)|      |    VALIDATION        |      |    SPECIFICATION(SRS)|               |
|  +--------------------+      +----------------------+      +----------------------+               |
|            ^                             | (Defect Discovered)                                    |
|            |                             +---------------------------------+                      |
|            +---------------------------------------------------------------+                      |
+---------------------------------------------------------------------------------------------------+
```

#### Stage 1: Feasibility Assessment
Prior to committing engineering capital, analysts perform a multi-dimensional feasibility study (evaluating **TELOS**: Technical, Economic, Legal, Operational, and Schedule constraints). The primary deliverable is the formal *Feasibility Report*, establishing the initial scope boundary and Go/No-Go project milestone.

#### Stage 2: Requirements Elicitation & Gathering
Deriving the real needs of diverse stakeholders through active fact-finding techniques:
- Structured and Unstructured Interviews with subject matter experts.
- Joint Application Development (JAD) cross-functional design workshops.
- Field observation of existing manual and automated workflows (accounting for the *Hawthorne Effect*).
- Archival document analysis, regulatory review, and reverse engineering legacy forms.

#### Stage 3: Requirements Analysis & Negotiation
Raw elicited statements are rarely complete, consistent, or harmonious. This stage resolves:
- **Requirement Conflicts:** Balancing conflicting stakeholder interests (e.g., Marketing demanding instant page load times vs. Compliance demanding client-side encryption and multi-factor biometric auth).
- **Classification & Clustering:** Grouping requirements into functional feature domains.
- **Prioritization:** Applying formal ranking methodologies (MoSCoW, Kano Model, Analytic Hierarchy Process).
- **Win-Win Negotiation:** Achieving consensus where all primary stakeholder groups preserve core value without compromising architectural viability.

#### Stage 4: Formal Requirements Specification (The SRS)
Transforming analyzed requirements into a rigorously structured document adhering to **IEEE 830-1998** or its modern harmonization **ISO/IEC/IEEE 29148:2018**. Requirements must be drafted using precise, structured natural language (RFC 2119 keywords: `SHALL`, `MUST`, `SHOULD`, `MAY`), augmented with formal mathematical notations, state transition tables, and data dictionaries.

#### Stage 5: Requirements Verification and Validation (V&V)
Ensuring that the specification satisfies two fundamental software engineering axioms:
- **Verification ("Are we building the system right?"):** Confirming that the SRS conforms to stylistic standards, contains zero internal contradictions, and is mathematically complete.
- **Validation ("Are we building the right system?"):** Confirming with clients, end-users, and domain experts that the written specifications accurately reflect their real-world operational needs.
- **Key Techniques:** Formal peer inspections, pseudo-code walk-throughs, executable prototyping, and automated consistency checkers.

#### Stage 6: Requirements Management & Traceability
Requirements are inherently volatile; business environments evolve, regulations shift, and competitors emerge. Requirements Management establishes:
- **Baselines:** Frozen, cryptographically hashed versions of the SRS approved by the Change Control Board (CCB).
- **Change Impact Analysis:** Formally estimating the architectural, financial, and schedule impact of any proposed change request (CR).
- **Requirements Traceability Matrix (RTM):** Maintaining bidirectional forward and backward links from business goals down to unit test cases.

---

### 4. The IEEE 830 / ISO 29148 Standard SRS Template

The IEEE 830 standard specifies a canonical structural framework to ensure that no critical architectural dimension is omitted:

```
====================================================================================================
                  IEEE 830-1998 / ISO 29148 CANONICAL SRS DOCUMENT STRUCTURE
====================================================================================================
1. INTRODUCTION
   1.1 Purpose (Audience, intended use, lifecycle stage)
   1.2 Document Conventions (Typography, RFC 2119 keyword meanings, priority notation)
   1.3 Intended Audience and Reading Suggestions
   1.4 Project Scope (System boundary, explicit out-of-scope declarations)
   1.5 References (Industry standards, corporate policies, architectural guidelines)

2. OVERALL DESCRIPTION
   2.1 Product Perspective (Autonomous system vs. component in a larger ecosystem)
   2.2 Product Functions (High-level functional decomposition summary)
   2.3 User Classes and Characteristics (Personas, technical proficiency, access tiers)
   2.4 Operating Environment (Hardware platforms, OS, container runtimes, network topology)
   2.5 Design and Implementation Constraints (Language runtimes, regulatory mandates, database engines)
   2.6 User Documentation (Manuals, online tutorials, interactive OpenAPI/Swagger portals)
   2.7 Assumptions and Dependencies (Third-party SLA uptime, network bandwidth guarantees)

3. SPECIFIC REQUIREMENTS
   3.1 External Interface Requirements
       3.1.1 User Interfaces (Screen layouts, accessibility standards [WCAG 2.1 AA], keyboard navigation)
       3.1.2 Hardware Interfaces (Sensor buses, GPIO, RFID readers, memory-mapped registers)
       3.1.3 Software Interfaces (RESTful endpoints, gRPC microservices, message queues, RDBMS)
       3.1.4 Communications Interfaces (TLS 1.3, WebSockets, HTTP/2, MTU constraints)
   3.2 Functional Requirements (Decomposed by feature, actor, or use case)
       3.2.x Feature X: [Stimulus/Response Sequences, Inputs, Algorithmic Rules, State Outputs]
   3.3 Non-Functional Requirements
       3.3.1 Performance Requirements (p99 latency, transactions per second, batch throughput)
       3.3.2 Safety & Reliability (MTBF, MTTR, fail-safe modes, redundancy)
       3.3.3 Security Requirements (Authentication, RBAC, encryption at rest/in transit, audit logs)
       3.3.4 Software Quality Attributes (Maintainability, testability, portability, extensibility)
   3.4 Business Rules & Domain Invariants (Tax tables, interest calculations, legal disclaimers)

4. SUPPORTING INFORMATION
   Appendix A: Glossary of Terms & Domain Ontologies
   Appendix B: Analysis Models (Context DFDs, Domain UML Class Diagrams, Entity Relationship Diagrams)
   Appendix C: Requirements Traceability Matrix (RTM) Baseline
====================================================================================================
```

---

### 5. Quality Attributes of Professional Requirements

To be considered production-grade under ISO 29148, every requirement statement in an SRS must exhibit **eight fundamental quality criteria**:

| Quality Attribute | Definition | Violation Example (Bad Requirement) | Corrected Production Requirement |
| :--- | :--- | :--- | :--- |
| **Unambiguous** | Interpretable in exactly one way by all readers. | *"The application UI shall be intuitive, modern, and user-friendly."* | *"The checkout workflow shall require no more than 3 consecutive screen interactions, achieving a System Usability Scale (SUS) score $\ge 85$ during formal user testing."* |
| **Complete** | Specifies all inputs, all outputs, and handling of every edge case / error. | *"The system shall calculate monthly interest on customer loan accounts."* | *"On the final calendar day of each month at 23:59:59 UTC, the system shall compute compounding daily interest for all accounts in status `ACTIVE`, applying the formula $I = P \times \frac{r}{365} \times t$, rounding down to 2 decimal places, and generating an error log entry if an account has a negative principal balance."* |
| **Consistent** | Contains no internal contradictions with other requirements or standards. | *Req 12: "System shall purge inactive accounts after 90 days." vs Req 88: "System shall retain all account history for 7 years for tax audits."* | *"System shall mark accounts inactive after 90 days of dormancy; inactive accounts shall be archived to immutable cold storage and retained for exactly 7 years before cryptographic shredding."* |
| **Verifiable (Testable)**| There exists a finite, cost-effective process by which a machine or human can prove compliance. | *"The platform must be blazing fast under heavy production load."* | *"Under a concurrent load of 15,000 HTTP requests per second, the 99th percentile (p99) server response latency for `GET /api/v1/catalog` shall not exceed $120\text{ ms}$ over a continuous 1-hour soak test."* |
| **Modifiable** | Structured and indexed so that changes can be made easily, completely, and consistently. | Unstructured prose paragraphs blending data formats, business logic, and UI design. | Hierarchically numbered atomic statements (`FR-PAY-001`, `FR-PAY-002`) with cross-references. |
| **Traceable** | Bidirectionally traceable from business source to design, code, and test cases. | Orphan requirements with unknown origin or untestable implementation blocks. | Tagged with `Source: BRD-04`, `Component: PaymentService`, `Test: TC-PAY-882`. |
| **Feasible** | Technically and financially achievable within platform constraints. | *"The client app shall train a 70B parameter LLM locally on an entry-level smartphone."* | *"The client app shall stream quantized inference prompts to a cloud GPU cluster over TLS 1.3."* |
| **Correct** | Faithfully represents the true operational intent of the stakeholders. | System specifies calculation of tax based on buyer address when the law requires seller jurisdiction. | Cross-validated against current municipal tax code regulations. |

#### 5.1 Quantifying Functional Size: COSMIC Function Points (ISO/IEC 19761)
Modern software engineering replaces subjective "lines of code" (LOC) estimation with the **COSMIC Functional Size Measurement**. COSMIC measures software functional size strictly by counting four fundamental **Data Movements**:
1. **Entry (E):** Data moves from an external functional user across the boundary into the software.
2. **Exit (X):** Data moves from inside the software boundary out to an external user/system.
3. **Read (R):** Data moves from persistent storage into the software's active working memory.
4. **Write (W):** Data moves from active working memory into persistent storage.

$$\text{Functional Size } (CFP) = \sum E + \sum X + \sum R + \sum W$$

Each valid data movement equals exactly $1\text{ CFP}$ (COSMIC Function Point). For example, a "Search & Display Medication" feature that receives search parameters ($1E$), reads the database table ($1R$), and renders the search results ($1X$) represents a functional size of $3\text{ CFP}$.

---

### 6. Bidirectional Traceability: The Requirements Traceability Matrix (RTM)

The **Requirements Traceability Matrix (RTM)** is the primary engineering mechanism for preventing **scope creep**, **orphan requirements** (requirements with no underlying business justification), and **untested features** (code that lacks corresponding test cases).

```
+---------------------------------------------------------------------------------------------------+
|                        BIDIRECTIONAL REQUIREMENTS TRACEABILITY MATRIX (RTM)                       |
|                                                                                                   |
|  Forward Traceability:   [BRD Goal]  ===>  [SRS Spec]  ===>  [Architecture/Code] ===> [Unit Test] |
|                                                                                                   |
|  Backward Traceability:  [Unit Test] <===  [Code Module] <=== [SRS Spec] <=== [BRD Goal]          |
+---------------------------------------------------------------------------------------------------+
```

An engineering RTM tracks four mandatory relationships for every system element:

| Business Need ID | User Story ID | SRS Req ID | System Architecture Component | Code Module / Source File | Acceptance Test ID | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `BRD-REV-01` | `US-CART-04` | `FR-CHECKOUT-101` | `BillingGatewayService` | `src/billing/stripe.cpp` | `TC-PAY-042` | `Verified` |
| `BRD-REV-01` | `US-CART-05` | `FR-CHECKOUT-102` | `TaxCalculationEngine` | `src/billing/tax_engine.cpp` | `TC-TAX-018` | `In Review`|
| `BRD-SEC-09` | `US-AUTH-01` | `NFR-SEC-004` | `OAuth2TokenValidator` | `src/auth/jwt_verifier.cpp` | `TC-SEC-109` | `Verified` |

---

### 7. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

A junior software engineer is reviewing a draft SRS for a hospital intensive care telemetry monitoring platform. The engineer encounters the following requirement statement:

> *Requirement Statement: "The patient monitoring software should be fast, user-friendly, and alert medical personnel if the patient's heart rate becomes abnormal or if anything goes wrong."*

**Architectural Audit Tasks:**
1. Identify all violations of the ISO/IEC/IEEE 29148 quality criteria in this statement.
2. Highlight all subjective, ambiguous adjectives and weak RFC 2119 verbs.
3. Formulate a fully compliant, production-grade engineering requirement specification conforming to IEEE 830, quantifying all parameters, triggers, latency budgets, and error pathways.

<details>
<summary>Click to view Level 1 Model Architectural Audit</summary>

##### 1. Identified Violations of ISO 29148 Criteria:
- **Ambiguity & Subjectivity:** The terms *"fast"* and *"user-friendly"* have no mathematical definition. What one engineer considers fast (500 ms) may cause fatal patient outcome in an arrhythmia episode.
- **Weak Imperative:** The statement uses the weak modal verb *"should"*. In formal requirements standards (RFC 2119), *"should"* denotes an optional recommendation. For safety-critical systems, the mandatory imperative **`SHALL`** or **`MUST`** is legally required.
- **Incompleteness & Unbounded Conditions:** The condition *"if the patient's heart rate becomes abnormal or if anything goes wrong"* fails to specify:
  - What constitutes "abnormal" (upper and lower beats-per-minute thresholds).
  - How long the abnormal condition must persist before triggering an alarm (preventing noise artifacts from sensor dislocation).
  - Who the "medical personnel" are (assigned ward nurse vs. attending cardiologist).
  - What transmission protocol is used (visual dashboard flashing, local audio alarm, pagers, nurse station API).
  - What "anything goes wrong" encompasses (sensor lead disconnect, battery depletion, network packet loss).
- **Untestability (Non-Verifiability):** A QA test engineer cannot design a deterministic boolean Pass/Fail test case for *"user-friendly"* or *"fast"*.

##### 2. Production-Grade IEEE 830 Decomposition & Specification:
To achieve full ISO 29148 compliance, the vague statement must be decomposed into three atomic, verifiable requirements:

* **FR-HEART-001 (Arrhythmia Threshold Alarm Trigger):**
  $$\text{The Telemetry Monitoring Engine } \mathbf{SHALL} \text{ sample the patient's ECG heart rate signal at } \ge 250\text{ Hz.}$$
  $$\text{If the calculated heart rate } HR < 45\text{ BPM or } HR > 130\text{ BPM for } \ge 3.0\text{ consecutive seconds,}$$
  $$\text{the system } \mathbf{SHALL} \text{ transition to state } \mathtt{CRITICAL\_ALARM} \text{ within } \le 200\text{ ms of condition detection.}$$

* **FR-HEART-002 (Multi-Channel Alert Dispatch):**
  $$\text{Upon entering state } \mathtt{CRITICAL\_ALARM}\text{, the system } \mathbf{SHALL} \text{ simultaneously:}$$
  1. Trigger the bedside visual indicator (flashing red beacon at $2\text{ Hz}$) and acoustic alert ($\ge 75\text{ dBA}$ at $1\text{ meter}$).
  2. Dispatch an encrypted alert payload over IEEE 802.11ax via WSS to the Central Nursing Station console.
  3. Send an emergency push notification via APNs/FCM to the assigned primary caregiver's registered mobile device within $\le 1.5\text{ seconds}$.

* **FR-HEART-003 (Sensor Fault & Disconnection Invariant):**
  $$\text{If the ECG electrode impedance indicates an open circuit (lead detachment) or signal packet loss exceeds } 500\text{ ms,}$$
  $$\text{the system } \mathbf{SHALL} \text{ emit a distinct } \mathtt{SENSOR\_FAULT} \text{ audible chime and mark all telemetry readings as } \mathtt{INVALID\_DATA}.$$

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The Traceability Gap & Ambiguity Parser

An enterprise banking system failed an external audit because its requirements management tooling allowed ambiguous words to pass into approved baselines and failed to detect "orphan requirements" (features coded in production that had no parent business justification in the BRD).

Examine the flawed requirements verification script below:

```python
# FLAWED REQUIREMENTS VERIFIER (PYTHON)
def audit_requirements(brd_goals, srs_requirements, code_modules):
    ambiguous_words = ["fast", "quick", "user-friendly", "flexible", "robust"]
    issues = []

    # Check 1: Simple substring search for ambiguity
    for req_id, text in srs_requirements.items():
        for word in ambiguous_words:
            if word in text:  # BUG: False positives on 'breakfast', 'steadfast', etc.
                issues.append(f"Ambiguous word '{word}' found in {req_id}")

    # Check 2: Verify all BRD goals have SRS requirements
    for goal in brd_goals:
        # BUG: Relies on substring matching of goal ID in the requirement text,
        # missing structured parent-link metadata!
        found = False
        for req_id, text in srs_requirements.items():
            if goal in text:
                found = True
                break
        if not found:
            issues.append(f"Uncovered BRD goal: {goal}")

    # BUG: Fails to check backward traceability!
    # Does not detect orphan SRS requirements that lack a parent BRD goal!
    # Does not verify if every SRS requirement is mapped to at least one code module!

    return issues
```

**Debug Assignment:**
1. Identify the logical and algorithmic bugs in this verification tool.
2. Implement a robust, regex-tokenized ambiguity detector that only flags whole words.
3. Construct a complete bidirectional graph verification algorithm that reports:
   - Uncovered BRD goals (under-specified business scope).
   - Orphan SRS requirements (scope creep without business justification).
   - Untested / Unimplemented SRS requirements (requirements lacking corresponding code modules).

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. Flaws in the Original Script:
- **Substring Sub-token Collision:** Checking `word in text` triggers false positives on innocent English words (e.g., `"breakfast"` contains `"fast"`, `"steadfast"` contains `"fast"`, `"flexible"` inside `"non-flexible"`). Word-boundary regular expressions (`\b(?i)fast\b`) are required.
- **Informal Traceability Coupling:** Searching for the BRD ID inside the freeform prose of the requirement text is brittle. Formal RTM requires an explicit structured metadata attribute (e.g., `parent_goal_id: "BRD-01"`).
- **Missing Backward Traceability:** The script only checked forward from BRD to SRS. It completely missed **Orphan SRS Requirements** (engineers writing pet features that no stakeholder requested or funded).
- **Missing Downstream Verification:** It ignored the `code_modules` parameter entirely, failing to alert the team when an approved SRS requirement had zero corresponding source files or tests.

##### 2. Corrected Production Implementation (Python):

```python
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

@dataclass
class Requirement:
    id: str
    text: str
    parent_brd_id: str
    cosmic_cfp: int = 1

@dataclass
class CodeModule:
    id: str
    implements_srs_ids: List[str]

class FormalRTMVerifier:
    AMBIGUOUS_TERMS = {
        "fast", "slow", "user-friendly", "intuitive", "flexible",
        "robust", "scalable", "efficient", "modern", "adequate",
        "should", "may", "could", "reasonable", "as fast as possible"
    }

    def __init__(self, brd_ids: Set[str], requirements: Dict[str, Requirement], modules: List[CodeModule]):
        self.brd_ids = brd_ids
        self.requirements = requirements
        self.modules = modules

    def verify_specification_hygiene(self) -> List[str]:
        violations = []
        for req_id, req in self.requirements.items():
            # Exact word-boundary regex check for ambiguous vocabulary
            for term in self.AMBIGUOUS_TERMS:
                pattern = rf"\b{re.escape(term)}\b"
                if re.search(pattern, req.text, re.IGNORECASE):
                    violations.append(
                        f"[AMBIGUITY DEFECT] Requirement '{req_id}' contains forbidden subjective term: '{term}'"
                    )
        return violations

    def verify_bidirectional_traceability(self) -> Dict[str, List[str]]:
        report = {
            "uncovered_brd_goals": [],
            "orphan_srs_requirements": [],
            "unimplemented_srs_requirements": []
        }

        # 1. Forward Traceability: Check every BRD has at least one child SRS requirement
        covered_brds = {req.parent_brd_id for req in self.requirements.values()}
        for brd in self.brd_ids:
            if brd not in covered_brds:
                report["uncovered_brd_goals"].append(brd)

        # 2. Backward Traceability: Check every SRS requirement links to a valid parent BRD
        for req_id, req in self.requirements.items():
            if not req.parent_brd_id or req.parent_brd_id not in self.brd_ids:
                report["orphan_srs_requirements"].append(
                    f"{req_id} (Invalid Parent: '{req.parent_brd_id}')"
                )

        # 3. Downstream Traceability: Check every SRS requirement is implemented in code
        implemented_srs = set()
        for mod in self.modules:
            implemented_srs.update(mod.implements_srs_ids)

        for req_id in self.requirements.keys():
            if req_id not in implemented_srs:
                report["unimplemented_srs_requirements"].append(req_id)

        return report
```

</details>

---

#### Level 3 — High-Scale System Design: Automated Requirements Verification & COSMIC Sizing Engine in C++

Design and implement a complete, standalone C++17 **Requirements Engineering & Traceability Analysis Engine**. The engine must:
1. Model requirements as an interconnected **Directed Bipartite Graph** representing Business Requirements, User Requirements, Software Requirements (SRS), and Verification Test Cases.
2. Implement an automated **Ambiguity Linter** using exact lexical token matching to catch subjective terms (`"fast"`, `"user-friendly"`, `"robust"`, etc.).
3. Compute the **COSMIC Functional Size Measurement (CFP)** across all requirements by calculating Data Movements (Entry, Exit, Read, Write).
4. Perform an automated **Traceability Graph Traversal** to detect:
   - Uncovered Business Goals (Gaps in specification).
   - Orphan Specifications (Unapproved scope creep).
   - Untested Requirements (Zero associated test verification units).
5. Output a formal tabular compliance audit report.

<details>
<summary>Click to view complete C++17 Requirements Engineering Engine</summary>

```cpp
/**
 * ============================================================================
 * SOFTWARE REQUIREMENTS ENGINEERING & TRACEABILITY ENGINE (C++17)
 * ============================================================================
 * Implements:
 * 1. ISO/IEC/IEEE 29148 Specification Quality Verification & Ambiguity Linter.
 * 2. ISO/IEC 19761 COSMIC Functional Size Measurement Engine (CFP).
 * 3. Bidirectional Graph-Based Requirements Traceability Matrix (RTM).
 * ============================================================================
 */

#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <cctype>

// ============================================================================
// DOMAIN MODELS & DATA STRUCTURES
// ============================================================================

enum class RequirementTier {
    BUSINESS_BRD,
    USER_STORY,
    SYSTEM_FUNCTIONAL_SRS,
    SYSTEM_NON_FUNCTIONAL_SRS
};

// COSMIC Functional Size Movements (ISO/IEC 19761)
struct CosmicDataMovement {
    int entries = 0;   // E: Data received across boundary from external user
    int exits = 0;     // X: Data emitted across boundary to external user
    int reads = 0;     // R: Data retrieved from persistent storage
    int writes = 0;    // W: Data written to persistent storage

    int total_cfp() const {
        return entries + exits + reads + writes;
    }
};

struct RequirementNode {
    std::string id;
    RequirementTier tier;
    std::string text;
    std::string parent_id; // For hierarchical link (e.g., SRS -> User Story -> BRD)
    CosmicDataMovement cosmic;
    std::vector<std::string> child_ids;
    std::vector<std::string> test_case_ids;
};

// ============================================================================
// AMBIGUITY LINTER & LEXICAL ANALYZER
// ============================================================================

class AmbiguityLinter {
private:
    std::unordered_set<std::string> forbidden_terms = {
        "fast", "slow", "intuitive", "user-friendly", "flexible",
        "robust", "scalable", "efficient", "adequate", "easy",
        "should", "may", "could", "reasonable", "optimum", "seamless"
    };

    std::string to_lower(const std::string& input) const {
        std::string out = input;
        std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c) {
            return std::tolower(c);
        });
        return out;
    }

public:
    std::vector<std::string> analyze_text(const std::string& text) const {
        std::vector<std::string> findings;
        std::string lower = to_lower(text);
        
        // Tokenize by punctuation and whitespace to isolate whole words
        std::string current_token;
        for (char ch : lower) {
            if (std::isalnum(static_cast<unsigned char>(ch)) || ch == '-') {
                current_token += ch;
            } else {
                if (!current_token.empty()) {
                    if (forbidden_terms.find(current_token) != forbidden_terms.end()) {
                        findings.push_back(current_token);
                    }
                    current_token.clear();
                }
            }
        }
        if (!current_token.empty() && forbidden_terms.find(current_token) != forbidden_terms.end()) {
            findings.push_back(current_token);
        }
        return findings;
    }
};

// ============================================================================
// REQUIREMENTS TRACEABILITY MATRIX (RTM) ENGINE
// ============================================================================

class RequirementsEngine {
private:
    std::unordered_map<std::string, RequirementNode> nodes;
    AmbiguityLinter linter;

public:
    void add_requirement(const RequirementNode& node) {
        nodes[node.id] = node;
        if (!node.parent_id.empty() && nodes.find(node.parent_id) != nodes.end()) {
            nodes[node.parent_id].child_ids.push_back(node.id);
        }
    }

    void link_test_case(const std::string& req_id, const std::string& test_id) {
        if (nodes.find(req_id) != nodes.end()) {
            nodes[req_id].test_case_ids.push_back(test_id);
        }
    }

    void generate_comprehensive_audit_report() const {
        std::cout << "\n================================================================================\n";
        std::cout << "        SOFTWARE REQUIREMENTS SPECIFICATION (SRS) AUDIT REPORT (ISO 29148)\n";
        std::cout << "================================================================================\n";

        int total_cfp = 0;
        std::vector<std::string> ambiguity_defects;
        std::vector<std::string> orphan_requirements;
        std::vector<std::string> uncovered_brd_goals;
        std::vector<std::string> untested_requirements;

        std::cout << std::left 
                  << std::setw(15) << "Req ID"
                  << std::setw(18) << "Tier"
                  << std::setw(12) << "Parent ID"
                  << std::setw(10) << "COSMIC"
                  << std::setw(10) << "Tests"
                  << "Audit Status\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        for (const auto& [id, node] : nodes) {
            std::string tier_str;
            switch (node.tier) {
                case RequirementTier::BUSINESS_BRD: tier_str = "BRD (Goal)"; break;
                case RequirementTier::USER_STORY:   tier_str = "User Story"; break;
                case RequirementTier::SYSTEM_FUNCTIONAL_SRS: tier_str = "SRS (Functional)"; break;
                case RequirementTier::SYSTEM_NON_FUNCTIONAL_SRS: tier_str = "SRS (Quality NFR)"; break;
            }

            int cfp = node.cosmic.total_cfp();
            total_cfp += cfp;

            // Ambiguity check
            auto defects = linter.analyze_text(node.text);
            bool has_ambiguity = !defects.empty();
            if (has_ambiguity) {
                for (const auto& d : defects) {
                    ambiguity_defects.push_back(node.id + ": Contains subjective term '" + d + "'");
                }
            }

            // Traceability checks
            bool is_orphan = false;
            if (node.tier != RequirementTier::BUSINESS_BRD) {
                if (node.parent_id.empty() || nodes.find(node.parent_id) == nodes.end()) {
                    is_orphan = true;
                    orphan_requirements.push_back(node.id + " (Tier: " + tier_str + ")");
                }
            }

            bool is_uncovered_brd = false;
            if (node.tier == RequirementTier::BUSINESS_BRD && node.child_ids.empty()) {
                is_uncovered_brd = true;
                uncovered_brd_goals.push_back(node.id + ": '" + node.text.substr(0, 45) + "...'");
            }

            bool is_untested = false;
            if ((node.tier == RequirementTier::SYSTEM_FUNCTIONAL_SRS || 
                 node.tier == RequirementTier::SYSTEM_NON_FUNCTIONAL_SRS) && 
                node.test_case_ids.empty()) {
                is_untested = true;
                untested_requirements.push_back(node.id);
            }

            // Status label
            std::string status = "PASSED";
            if (has_ambiguity || is_orphan || is_uncovered_brd || is_untested) {
                status = "FAILED [";
                if (has_ambiguity) status += "A";
                if (is_orphan) status += "O";
                if (is_uncovered_brd) status += "U";
                if (is_untested) status += "T";
                status += "]";
            }

            std::cout << std::left 
                      << std::setw(15) << node.id
                      << std::setw(18) << tier_str
                      << std::setw(12) << (node.parent_id.empty() ? "ROOT" : node.parent_id)
                      << std::setw(10) << (cfp > 0 ? std::to_string(cfp) + " CFP" : "N/A")
                      << std::setw(10) << node.test_case_ids.size()
                      << status << "\n";
        }

        std::cout << "\n--------------------------------------------------------------------------------\n";
        std::cout << ">>> TOTAL ESTIMATED SYSTEM FUNCTIONAL SIZE: " << total_cfp << " COSMIC Function Points (CFP)\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        // Summary of Discovered Specification Defects
        std::cout << "\n[!] DEFECT SUMMARY AUDIT:\n";
        std::cout << "  1. Ambiguity & Lexical Defects Found: " << ambiguity_defects.size() << "\n";
        for (const auto& a : ambiguity_defects) {
            std::cout << "     * " << a << "\n";
        }

        std::cout << "\n  2. Orphan Requirements (Scope Creep - Missing Parent Goal): " << orphan_requirements.size() << "\n";
        for (const auto& o : orphan_requirements) {
            std::cout << "     * " << o << "\n";
        }

        std::cout << "\n  3. Uncovered Business Goals (Missing Decomposition): " << uncovered_brd_goals.size() << "\n";
        for (const auto& u : uncovered_brd_goals) {
            std::cout << "     * " << u << "\n";
        }

        std::cout << "\n  4. Untested Requirements (Zero Associated Test Cases): " << untested_requirements.size() << "\n";
        for (const auto& t : untested_requirements) {
            std::cout << "     * " << t << "\n";
        }
        std::cout << "================================================================================\n";
    }
};

// ============================================================================
// SIMULATION HARNESS
// ============================================================================

int main() {
    RequirementsEngine engine;

    // 1. Business Requirements (BRD)
    engine.add_requirement({
        "BRD-REV-01",
        RequirementTier::BUSINESS_BRD,
        "Platform shall increase emergency medication fulfillment speed by 35% to save hospital operational costs.",
        "", // Root
        {0, 0, 0, 0}, {}, {}
    });

    engine.add_requirement({
        "BRD-SEC-02",
        RequirementTier::BUSINESS_BRD,
        "System shall comply with federal HIPAA security omnibus rules to prevent statutory regulatory fines.",
        "", // Root
        {0, 0, 0, 0}, {}, {}
    });

    // 2. User Requirements (User Stories)
    engine.add_requirement({
        "US-NURSE-01",
        RequirementTier::USER_STORY,
        "As an ICU nurse, I want to scan patient barcoded wristbands to dispense medications rapidly without manual data entry.",
        "BRD-REV-01",
        {1, 1, 1, 0}, {}, {} // 1 Entry, 1 Exit, 1 Read = 3 CFP
    });

    // 3. System Functional Requirements (SRS)
    engine.add_requirement({
        "FR-MED-101",
        RequirementTier::SYSTEM_FUNCTIONAL_SRS,
        "The system shall authenticate nurse credentials, query patient allergy history, and log dispensing timestamps.",
        "US-NURSE-01",
        {2, 1, 2, 2}, {}, {} // 2 Entries, 1 Exit, 2 Reads, 2 Writes = 7 CFP
    });

    // 4. Defective Requirements for Testing the Linter
    // Flaw A: Ambiguous vocabulary ("fast", "user-friendly", "should")
    engine.add_requirement({
        "FR-MED-102",
        RequirementTier::SYSTEM_FUNCTIONAL_SRS,
        "The dosage calculator should be fast and user-friendly to avoid clinical delays.",
        "US-NURSE-01",
        {1, 1, 0, 0}, {}, {}
    });

    // Flaw B: Orphan Requirement (No parent goal - unauthorized developer feature)
    engine.add_requirement({
        "FR-DEV-999",
        RequirementTier::SYSTEM_FUNCTIONAL_SRS,
        "The application shall display an animated custom particle splash screen on startup.",
        "", // Orphan!
        {0, 1, 0, 0}, {}, {}
    });

    // Link Test Cases (FR-MED-101 is tested; FR-MED-102 and FR-DEV-999 are untested)
    engine.link_test_case("FR-MED-101", "TC-UNIT-MED-042");
    engine.link_test_case("FR-MED-101", "TC-INT-ALLERGY-088");

    // Execute complete formal audit
    engine.generate_comprehensive_audit_report();

    return 0;
}
```

</details>

---

### 8. Reference Video Lecture

{{ media:requirements-engineering-video }}

In this video by Crash Course Computer Science, the foundations of software engineering and formal specifications are explored, detailing how ambiguous human communication is engineered into deterministic, testable software architectures.
