# Unit 3 — System Requirements Engineering, Elicitation Techniques & Analysis Paradigms
## Lesson 2 — Functional, Non-Functional (ISO 25010) & Domain Requirements: Rigorous Quantification & Prioritization

### 1. Functional Requirements (FR): The Behavioral Core

**Functional Requirements (FR)** define the fundamental behavioral capabilities, services, and transformations that a software system must execute. They capture *what* the system does in response to specific operational stimuli, independent of runtime technologies or hosting infrastructure.

In formal systems engineering, any functional requirement can be modeled as a mathematical transformation function mapping an input state and domain stimulus to a deterministic output state and response:

$$f_{\text{req}}: (S_{\text{current}} \times I_{\text{stimulus}}) \longrightarrow (S_{\text{next}} \times O_{\text{response}})$$

Where:
- $S_{\text{current}} \in \mathcal{S}$ represents the valid internal state of the system before invocation (e.g., user is authenticated, cart has items, database connection is active).
- $I_{\text{stimulus}} \in \mathcal{I}$ represents the external trigger (e.g., HTTP POST payload, sensor interrupt, cron timer tick).
- $S_{\text{next}} \in \mathcal{S}$ represents the mutated persistent state (e.g., transaction record persisted with status `COMMITTED`).
- $O_{\text{response}} \in \mathcal{O}$ represents the emitted artifact (e.g., JSON response, TCP ACK, physical actuator trigger).

```
+---------------------------------------------------------------------------------------------------+
|                           CANONICAL FUNCTIONAL REQUIREMENT STRUCTURE                              |
|                                                                                                   |
|  [ PRECONDITIONS ] ---> [ STIMULUS / INPUT ] ---> [ ALGORITHMIC LOGIC ] ---> [ POSTCONDITIONS ]   |
|  (System State S)       (Valid Ingestion)          (Invariant Rules)         (State S' & Output O)|
|                                                                                                   |
|  * Precondition: User account has status 'ACTIVE' and available balance >= $X.                   |
|  * Stimulus: User submits withdrawal request for amount $X.                                       |
|  * Processing: Verify idempotency key; atomically deduct $X; record double-entry ledger entry.     |
|  * Postcondition: Account balance reduced by $X; audit record appended; SMS alert emitted.        |
+---------------------------------------------------------------------------------------------------+
```

#### 1.1 Complete Functional Coverage via CRUD Invariants
A common failure in amateur requirements specifications is specifying the "happy path creation" of an entity while omitting the remaining lifecycle operations. Every domain entity specified in an SRS must have explicit requirements addressing the full **CRUD** (Create, Read, Update, Delete) lifecycle and its edge cases:

| Lifecycle Action | Formal Functional Requirement (Example: Medical Prescription) | Boundary / Error Condition Requirement |
| :--- | :--- | :--- |
| **Create (C)** | `FR-RX-01`: Physician creates a new electronic prescription with drug ID, dosage, and duration. | `FR-RX-01.1`: Reject if dosage exceeds Maximum Daily Dose (MDD) in pharmacopeia database. |
| **Read (R)** | `FR-RX-02`: Pharmacist queries active prescriptions by patient national ID and date range. | `FR-RX-02.1`: Return masked PHI if requesting user lacks `PHARMACIST_LICENSE` role. |
| **Update (U)** | `FR-RX-03`: Attending physician amends dosage prior to pharmacy fulfillment. | `FR-RX-03.1`: Reject update with HTTP 409 Conflict if prescription status is `DISPENSED`. |
| **Delete / Void (D)**| `FR-RX-04`: Medical director voids a fraudulent prescription, marking status `REVOKED`. | `FR-RX-04.1`: Hard physical deletion is strictly prohibited; cryptographically log void reason. |

---

### 2. Non-Functional Requirements (NFR): The ISO/IEC 25010 Quality Model

While functional requirements define *what* a system does, **Non-Functional Requirements (NFR)**—often referred to as system quality attributes or the "-ilities"—define *how well* the system executes those functions under operational constraints.

The modern international standard governing software product quality is **ISO/IEC 25010:2011** (Systems and software engineering — Systems and software Quality Requirements and Evaluation [SQuaRE]). ISO 25010 categorizes system quality into **eight primary characteristics**:

{{ media:sam-iso25010-matrix-diagram }}

```
+---------------------------------------------------------------------------------------------------+
|                        ISO/IEC 25010 SOFTWARE PRODUCT QUALITY MODEL                               |
+---------------------------------------------------------------------------------------------------+
| 1. FUNCTIONAL SUITABILITY : Completeness, Correctness, Appropriateness.                          |
| 2. PERFORMANCE EFFICIENCY : Time Behavior (Latency), Resource Utilization, Capacity/Throughput.   |
| 3. COMPATIBILITY          : Co-existence, Interoperability (APIs, Open Standards).                |
| 4. USABILITY              : Learnability, Operability, User Error Protection, Accessibility.      |
| 5. RELIABILITY            : Maturity, Availability, Fault Tolerance, Recoverability (MTTR).      |
| 6. SECURITY               : Confidentiality, Integrity, Non-repudiation, Accountability, Auth.    |
| 7. MAINTAINABILITY        : Modularity, Reusability, Analyzability, Modifiability, Testability.   |
| 8. PORTABILITY            : Adaptability, Installability, Replaceability across platforms.        |
+---------------------------------------------------------------------------------------------------+
```

#### 2.1 The Deep Anatomy of Key ISO 25010 Quality Attributes

##### Characteristic 2: Performance Efficiency
- **Time Behavior (Latency):** The distribution of time elapsed from request ingestion to response delivery. Must never be expressed as an average (mean), because averages conceal extreme tail latency experienced by hundreds of users. It must be specified using **percentiles** ($p50, p95, p99, p99.9$).
- **Throughput (Capacity):** The sustained number of transactional operations processed per unit of time (e.g., $15,000\text{ transactions per second}$ [TPS] at peak load).
- **Resource Utilization:** CPU utilization must not exceed $70\%$ sustained over a 15-minute sliding window; memory leak rate must be $0.0\text{ bytes/hour}$.

##### Characteristic 5: Reliability & Availability
- **Mean Time Between Failures (MTBF):** The statistical expected operational lifespan between consecutive unplanned system outages.
- **Mean Time to Repair (MTTR):** The duration required to diagnose, hot-patch, reboot, or failover an outage back to full operational readiness.
- **Operational Availability ($A$):**
  $$A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}}$$

##### Characteristic 6: Security
- **Confidentiality:** State and in-transit encryption (AES-256-GCM, TLS 1.3 with forward secrecy).
- **Integrity:** Cryptographic SHA-256 HMAC or digital signatures ensuring zero unauthorized modification of records.
- **Non-Repudiation:** Asymmetric public-key signed audit logs establishing undeniable proof of who initiated a transaction.

---

### 3. Quantifying the "Ilities": SLAs, SLOs, and Availability Math

In professional software engineering, subjective phrases like "high availability" or "low latency" are completely unacceptable. Engineers use the formal Google Site Reliability Engineering (SRE) triad:

$$\text{SLI (Service Level Indicator)} \longrightarrow \text{SLO (Service Level Objective)} \longrightarrow \text{SLA (Service Level Agreement)}$$

1. **Service Level Indicator (SLI):** A quantifiable, directly measurable metric tracking service health:
   $$\text{SLI}_{\text{latency}} = \frac{\text{Count of HTTP requests processed in } \le 200\text{ ms}}{\text{Total count of valid HTTP requests}} \times 100\%$$
2. **Service Level Objective (SLO):** The internal target boundary agreed upon by the engineering team:
   $$\text{Target SLO: } \text{SLI}_{\text{latency}} \ge 99.9\% \text{ over any rolling 30-day window.}$$
3. **Service Level Agreement (SLA):** The legally binding commercial contract with clients, carrying financial penalties (refund credits) if breached:
   $$\text{Contractual SLA: } \text{Monthly uptime } \ge 99.5\%; \text{ penalty of } 10\% \text{ billing credit per } 0.1\% \text{ deficit.}$$

#### 3.1 The "Nines" of Availability and Unplanned Downtime Budgets
Availability is mathematically measured in "nines". Each additional "nine" exponentially reduces allowed downtime and drives architectural complexity (e.g., moving from active-passive database failover to multi-region active-active distributed consensus).

$$\text{Unplanned Downtime per Year } = 365.25 \times 24 \times 3600 \times (1 - A)$$

| Availability $A$ | Common Name | Allowed Downtime / Year | Allowed Downtime / Month | Architectural Implications |
| :--- | :--- | :--- | :--- | :--- |
| $99.0\%$ | "Two Nines" | $3.65\text{ days}$ | $7.31\text{ hours}$ | Single server, manual reboots, off-site daily backups. |
| $99.9\%$ | "Three Nines" | $8.77\text{ hours}$ | $43.83\text{ minutes}$ | Redundant app servers, automated health checks, RDBMS failover. |
| $99.99\%$ | "Four Nines" | $52.60\text{ minutes}$ | $4.38\text{ minutes}$ | Automated multi-AZ clustering, sub-second failover, zero downtime CI/CD. |
| $99.999\%$ | "Five Nines" | $5.26\text{ minutes}$ | $26.30\text{ seconds}$ | Multi-region active-active geo-distribution, Paxos/Raft consensus. |
| $99.9999\%$ | "Six Nines" | $31.56\text{ seconds}$ | $2.63\text{ seconds}$ | Telecom carrier-grade / aerospace avionics, lockstep fault tolerance. |

---

### 4. Domain Requirements: Non-Negotiable Invariants

**Domain Requirements** are neither derived from individual user stories nor generated by product managers. Rather, they are fundamental axioms, legal mandates, physical laws, or mathematical invariants dictated by the operational domain itself:

```
+---------------------------------------------------------------------------------------------------+
|                              DOMAINS AND THEIR FORMAL INVARIANTS                                  |
+---------------------------------------------------------------------------------------------------+
| 1. BANKING & FINTECH       : ACID Transactions, Double-entry bookkeeping balance = 0,             |
|                              PCI-DSS Level 1 compliance, SWIFT MT/MX protocol standards.          |
| 2. HEALTHCARE (EHR / PACS) : HIPAA Title II Security Rule, HL7 FHIR v4.0 JSON interoperability,   |
|                              DICOM medical imaging standard, 21 CFR Part 11 electronic records.   |
| 3. AEROSPACE & AVIONICS    : DO-178C Level A certification, worst-case execution time (WCET),    |
|                              zero dynamic memory allocation (no malloc/new) after boot.           |
| 4. TELECOMMUNICATIONS     : 3GPP 5G Core signaling latency <= 1ms, ETSI NFV MANO standards.     |
+---------------------------------------------------------------------------------------------------+
```

* **Example Violation Disaster:** In 1999, the **Mars Climate Orbiter** was lost ($ \$327\text{M} $ failure) because ground software generated thrust output in Imperial pound-seconds ($\text{lbf}\cdot\text{s}$), while on-board orbital flight software expected metric Newton-seconds ($\text{N}\cdot\text{s}$). This was a catastrophic failure of a fundamental **Domain Requirement: Unit of Measure Invariance**.

---

### 5. Multi-Criteria Requirement Prioritization Frameworks

In any realistic software project, stakeholder desires always exceed finite engineering budgets and timeline constraints. Requirements must be rigorously prioritized.

```
+---------------------------------------------------------------------------------------------------+
|                        REQUIREMENTS PRIORITIZATION METHODOLOGIES                                  |
|                                                                                                   |
|  [ MoSCoW Method ]       Categorical triage: Must, Should, Could, Won't.                          |
|  [ Kano Model ]          Customer psychology: Must-be, Performance, Delighters.                   |
|  [ Analytic Hierarchy ]  Mathematical rigor: Eigenvector pairwise comparison matrix (Saaty).      |
+---------------------------------------------------------------------------------------------------+
```

#### 5.1 The MoSCoW Method
- **Must Have (M):** Non-negotiable MVP baseline. Without these, the software cannot launch legally, safely, or functionally.
- **Should Have (S):** Critical features with high business value; important, but a viable workaround exists for a temporary release window.
- **Could Have (C):** Desirable enhancements with low development effort; included only if time and budget permit.
- **Won't Have this time (W):** Explicitly agreed out-of-scope for the current release milestone, preventing scope creep.

#### 5.2 The Kano Model of Customer Satisfaction
Developed by Professor Noriaki Kano, this model evaluates requirements across two axes: **Degree of Implementation** ($0\%$ to $100\%$) versus **Customer Satisfaction** (Dissatisfied to Delighted):
1. **Must-Be (Basic / Dissatisfier):** Taken for granted. If absent (e.g., login fails, data is lost), the user is furious. If present $100\%$, satisfaction remains neutral.
2. **One-Dimensional (Performance):** Linear satisfaction. Faster queries, longer battery life, lower bandwidth consumption directly increase satisfaction.
3. **Attractive (Delighter):** Unexpected features that create immense customer joy (e.g., automated AI reconciliation). Their absence causes zero dissatisfaction because users did not anticipate them.

#### 5.3 Mathematical Prioritization: The Analytic Hierarchy Process (AHP)
Pioneered by Thomas Saaty, AHP removes subjective bias by establishing a pairwise comparison matrix of criteria ($C_1, C_2, \dots, C_n$). For $n$ criteria, stakeholders compare every pair $(i, j)$ using a fundamental scale from $1$ (Equal importance) to $9$ (Extreme importance):

$$A = \begin{bmatrix}
1 & a_{12} & \cdots & a_{1n} \\
1/a_{12} & 1 & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
1/a_{1n} & 1/a_{2n} & \cdots & 1
\end{bmatrix}$$

The priority vector $w$ corresponds to the normalized principal right eigenvector of matrix $A$:
$$A w = \lambda_{\max} w$$

AHP enforces mathematical discipline by computing the **Consistency Ratio (CR)**:
$$\text{CI} = \frac{\lambda_{\max} - n}{n - 1}, \quad \text{CR} = \frac{\text{CI}}{\text{RI}}$$
Where $\text{RI}$ is the Random Consistency Index. If $\text{CR} < 0.10$, the stakeholders' pairwise judgments are mathematically consistent and the calculated priority weights are validated.

---

### 6. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

An enterprise health-tech consortium is drafting the specification for a next-generation Cloud Telemedicine & Remote Surgical Consultation System. Below are six draft requirement statements:

1. *"Req-A: The platform shall transmit end-to-end encrypted video streams using WebRTC over DTLS-SRTP."*
2. *"Req-B: The platform shall be accessible 24 hours a day, 7 days a week, with zero unplanned downtime during active surgical sessions."*
3. *"Req-C: The surgeon shall be able to digitally annotate MRI scans and save snapshots to the consultation file."*
4. *"Req-D: All patient medical records must comply with HIPAA Privacy Rule 45 CFR Part 164 and be retained for exactly 7 years."*
5. *"Req-E: Under peak network load, the 99th percentile (p99) glass-to-glass surgical stylus haptic feedback latency shall not exceed $15\text{ ms}$."*
6. *"Req-F: The system shall support simultaneous user interfaces in English, Spanish, and Amharic."*

**Architectural Analysis Assignment:**
1. Classify each requirement into: **Functional Requirement (FR)**, **Non-Functional Requirement (NFR)** (identify the specific ISO 25010 characteristic), or **Domain Requirement**.
2. For Req-B and Req-E, specify the exact mathematical SLI, SLO, and measurement instrumentation required.

<details>
<summary>Click to view Level 1 Solution & Classification</summary>

##### 1. Formal Classification:
- **Req-A:** **Non-Functional Requirement (Security - Confidentiality & Integrity / ISO 25010 §6.1).** While transmitting video is a functional capability, mandating specific cryptographic transport protocols (DTLS-SRTP) enforces an architectural security constraint.
- **Req-B:** **Non-Functional Requirement (Reliability - Availability / ISO 25010 §5.2).** Mandates continuous operational uptime without service degradation.
- **Req-C:** **Functional Requirement (FR).** Specifies a direct user capability: inputting digital annotations, executing graphical transformation, and persisting snapshot artifacts to storage.
- **Req-D:** **Domain Requirement (Regulatory Healthcare Law).** Imposed by federal statutory law (HIPAA 45 CFR §164) and healthcare document retention statutes, non-negotiable by developers or users.
- **Req-E:** **Non-Functional Requirement (Performance Efficiency - Time Behavior / ISO 25010 §2.1).** Dictates a hard real-time latency deadline ($p99 \le 15\text{ ms}$) for haptic sensory feedback.
- **Req-F:** **Non-Functional Requirement (Usability - Operability / ISO 25010 §4.2 & Portability - Adaptability).** Dictates internationalization and localization (i18n/l10n) capabilities.

##### 2. Mathematical SLI/SLO Instrumentation:
- **Req-B (Availability SLI/SLO):**
  $$\text{SLI}_{\text{avail}} = \frac{\text{Uptime Minutes during active surgical sessions}}{\text{Total Scheduled Surgical Session Minutes}} \times 100\%$$
  $$\text{Target SLO: } \text{SLI}_{\text{avail}} = 100.0\% \text{ (Zero allowed outages during active procedures). Failover MTTR } \le 500\text{ ms.}$$
- **Req-E (Haptic Latency SLI/SLO):**
  $$\text{SLI}_{\text{haptic}} = \text{Percentile}_{99}\left(\{t_{\text{display}} - t_{\text{stylus\_sensor}}\} \text{ over sliding 60-second window}\right)$$
  $$\text{Target SLO: } \text{SLI}_{\text{haptic}} \le 15.0\text{ ms at } 1000\text{ Hz sampling rate.}$$

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The Flawed SLA & Error Budget Engine

A cloud infrastructure company developed an automated microservice to calculate customer uptime SLAs, error budget burn rates, and financial penalty credits. The script is experiencing catastrophic calculation discrepancies during leap years and precision errors when computing four-nines availability.

Review the flawed Python script below:

```python
# FLAWED SLA & ERROR BUDGET CALCULATOR (PYTHON)
def calculate_sla_penalties(target_sla_percent, recorded_downtime_seconds, monthly_fee):
    # BUG 1: Assumes every month has exactly 30 days of 86400 seconds!
    total_monthly_seconds = 30 * 24 * 3600  # 2,592,000 seconds
    
    # Calculate actual availability percentage
    # BUG 2: Severe floating-point cancellation / precision error when dealing with 99.99%
    uptime_seconds = total_monthly_seconds - recorded_downtime_seconds
    actual_availability = (uptime_seconds / total_monthly_seconds) * 100
    
    allowed_downtime_seconds = total_monthly_seconds * (1.0 - (target_sla_percent / 100.0))
    error_budget_remaining = allowed_downtime_seconds - recorded_downtime_seconds
    
    penalty_credit = 0.0
    # BUG 3: Flawed condition allows tiny floating point epsilon to trigger false penalty!
    if actual_availability < target_sla_percent:
        # Contract: For every 0.1% breach below SLA, refund 10% of monthly fee up to 100%
        deficit_percent = target_sla_percent - actual_availability
        increments = int(deficit_percent / 0.1)
        penalty_credit = min(monthly_fee, increments * 0.10 * monthly_fee)
        
    return {
        "actual_availability": actual_availability,
        "error_budget_remaining_seconds": error_budget_remaining,
        "penalty_credit": penalty_credit
    }
```

**Debug Assignment:**
1. Identify all numerical, astronomical, and business logic flaws in this calculation engine.
2. Refactor the implementation using arbitrary-precision `decimal.Decimal` to eliminate binary floating point imprecision.
3. Dynamically calculate exact month seconds (handling 28, 29, 30, and 31 days with calendar awareness).
4. Correct the penalty credit tiers to account for partial decimal fractions.

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. Identified Flaws:
- **Hardcoded 30-Day Month:** Months vary from 28 to 31 days ($2,419,200\text{ s}$ in February non-leap to $2,678,400\text{ s}$ in March/July). In February, calculating allowed downtime against 30 days gives customers $7.2$ extra minutes of unearned error budget!
- **Binary Floating Point Cancellation:** Using 64-bit IEEE 754 floats (`1.0 - (99.99 / 100.0)`) yields `0.000099999999999989` instead of `0.000100000000000000`. Over millions of transactions, this float fuzz triggers false SLA breach alerts.
- **Trunctation via `int()` in Penalty Math:** Using `int(deficit_percent / 0.1)` truncates a deficit of $0.0999\%$ to $0$ increments, depriving the customer of legitimate contract credits.

##### 2. Corrected Production Implementation:

```python
import calendar
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

def calculate_exact_sla(
    year: int,
    month: int,
    target_sla_str: str,
    recorded_downtime_sec: Decimal,
    monthly_fee: Decimal
) -> Dict[str, Decimal]:
    # 1. Precise calendar month duration
    days_in_month = calendar.monthrange(year, month)[1]
    total_month_seconds = Decimal(days_in_month * 86400)
    
    target_sla = Decimal(target_sla_str) # e.g. Decimal("99.99")
    target_ratio = target_sla / Decimal("100")
    
    # 2. Exact Decimal Availability
    uptime_seconds = total_month_seconds - recorded_downtime_sec
    actual_availability_ratio = uptime_seconds / total_month_seconds
    actual_availability_percent = (actual_availability_ratio * Decimal("100")).quantize(
        Decimal("0.0001"), rounding=ROUND_HALF_UP
    )
    
    # 3. Error budget calculation
    allowed_downtime_seconds = (total_month_seconds * (Decimal("1") - target_ratio)).quantize(
        Decimal("0.001"), rounding=ROUND_HALF_UP
    )
    error_budget_remaining = allowed_downtime_seconds - recorded_downtime_sec
    
    # 4. Financial Penalty Credit
    penalty_credit = Decimal("0.00")
    if actual_availability_percent < target_sla:
        deficit_percent = target_sla - actual_availability_percent
        # 10% credit for each 0.1% deficit, rounded up
        ten_pct_step = Decimal("0.1")
        increments = (deficit_percent / ten_pct_step).to_integral_value(rounding=ROUND_HALF_UP)
        refund_factor = min(Decimal("1.0"), increments * Decimal("0.10"))
        penalty_credit = (monthly_fee * refund_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
    return {
        "total_month_seconds": total_month_seconds,
        "actual_availability_percent": actual_availability_percent,
        "allowed_downtime_seconds": allowed_downtime_seconds,
        "error_budget_remaining_seconds": error_budget_remaining,
        "penalty_credit": penalty_credit
    }
```

</details>

---

#### Level 3 — High-Scale System Design: Multi-Criteria Prioritizer & Monte Carlo SLA Simulator in C++

Design and implement a complete, production-grade C++17 **Requirements Prioritization & SLA Availability Simulator**. The system must:
1. Implement the **Analytic Hierarchy Process (AHP)** pairwise comparison engine:
   - Accept an $N \times N$ reciprocal matrix comparing stakeholder criteria (e.g., Business Value, Technical Feasibility, Regulatory Compliance, User Impact).
   - Compute the normalized principal priority vector using power iteration / geometric mean approximation.
   - Calculate the Maximum Eigenvalue ($\lambda_{\max}$), Consistency Index ($\text{CI}$), and verify that Consistency Ratio ($\text{CR} < 0.10$).
2. Rank requirements by calculating composite utility scores:
   $$\text{Utility}(R) = \sum_{k=1}^N w_k \cdot \text{Score}(R, C_k)$$
3. Implement a **Monte Carlo Reliability Simulation Engine**:
   - Model a distributed multi-component architecture (API Gateway, Microservice Cluster, Distributed Database, Message Broker).
   - Simulate 100,000 operational hours with component MTBF and MTTR distributions.
   - Empirically measure total system availability, verify whether the architecture meets "Four Nines" ($99.99\%$) availability, and compute the simulated downtime distribution.

<details>
<summary>Click to view complete C++17 Prioritization & Monte Carlo Engine</summary>

```cpp
/**
 * ============================================================================
 * MULTI-CRITERIA PRIORITIZATION & MONTE CARLO SLA SIMULATOR (C++17)
 * ============================================================================
 * 1. Saaty's Analytic Hierarchy Process (AHP) with Consistency Ratio Check.
 * 2. Composite Multi-Attribute Utility Ranking Engine.
 * 3. Monte Carlo Distributed System Reliability & Availability Simulation.
 * ============================================================================
 */

#include <iostream>
#include <vector>
#include <string>
#include <numeric>
#include <cmath>
#include <random>
#include <iomanip>
#include <algorithm>

// ============================================================================
// PART 1: ANALYTIC HIERARCHY PROCESS (AHP) MATRIX ENGINE
// ============================================================================

class AhpPriorityEngine {
private:
    std::vector<std::string> criteria;
    std::vector<std::vector<double>> matrix;
    size_t n;

    // Saaty's Random Consistency Index (RI) table for n = 1 to 10
    const std::vector<double> RI_TABLE = {0.0, 0.0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49};

public:
    AhpPriorityEngine(const std::vector<std::string>& crit_names)
        : criteria(crit_names), n(crit_names.size()) {
        matrix.resize(n, std::vector<double>(n, 1.0));
    }

    void set_comparison(size_t i, size_t j, double value) {
        if (i < n && j < n && value > 0.0) {
            matrix[i][j] = value;
            matrix[j][i] = 1.0 / value;
        }
    }

    std::pair<std::vector<double>, bool> compute_weights_and_verify_consistency() const {
        std::vector<double> weights(n, 0.0);

        // 1. Column normalization method
        std::vector<double> col_sums(n, 0.0);
        for (size_t j = 0; j < n; ++j) {
            for (size_t i = 0; i < n; ++i) {
                col_sums[j] += matrix[i][j];
            }
        }

        for (size_t i = 0; i < n; ++i) {
            double row_sum = 0.0;
            for (size_t j = 0; j < n; ++j) {
                row_sum += matrix[i][j] / col_sums[j];
            }
            weights[i] = row_sum / static_cast<double>(n);
        }

        // 2. Compute Lambda Max
        double lambda_max = 0.0;
        for (size_t i = 0; i < n; ++i) {
            double weighted_sum = 0.0;
            for (size_t j = 0; j < n; ++j) {
                weighted_sum += matrix[i][j] * weights[j];
            }
            lambda_max += weighted_sum / weights[i];
        }
        lambda_max /= static_cast<double>(n);

        // 3. Consistency Index (CI) & Consistency Ratio (CR)
        double ci = (n > 1) ? (lambda_max - n) / (n - 1) : 0.0;
        double ri = (n < RI_TABLE.size()) ? RI_TABLE[n] : 1.49;
        double cr = (ri > 0.0) ? (ci / ri) : 0.0;

        bool is_consistent = (cr < 0.10);

        std::cout << "\n>>> AHP CRITERIA WEIGHT COMPUTATION <<<\n";
        std::cout << "Principal Eigenvalue (Lambda Max) : " << std::fixed << std::setprecision(4) << lambda_max << "\n";
        std::cout << "Consistency Index (CI)            : " << ci << "\n";
        std::cout << "Consistency Ratio (CR)            : " << cr << " (" << (is_consistent ? "VALID: CR < 0.10" : "INVALID: INCONSISTENT") << ")\n";

        return {weights, is_consistent};
    }
};

// ============================================================================
// PART 2: REQUIREMENT RANKING HARNESS
// ============================================================================

struct ScoredRequirement {
    std::string id;
    std::string title;
    std::vector<double> criteria_scores; // Normalized 0.0 to 10.0
    double composite_utility = 0.0;
};

// ============================================================================
// PART 3: MONTE CARLO RELIABILITY & AVAILABILITY SIMULATOR
// ============================================================================

struct SystemComponent {
    std::string name;
    double mtbf_hours; // Mean Time Between Failures
    double mttr_hours; // Mean Time To Repair
};

class MonteCarloReliabilitySimulator {
private:
    std::vector<SystemComponent> components;

public:
    void add_component(const std::string& name, double mtbf, double mttr) {
        components.push_back({name, mtbf, mttr});
    }

    void run_simulation(uint64_t total_simulation_hours) {
        std::mt19937_64 rng(1337); // Deterministic seed for reproducible testing
        std::vector<double> component_downtimes(components.size(), 0.0);
        double total_system_downtime_hours = 0.0;

        std::cout << "\n================================================================================\n";
        std::cout << "  MONTE CARLO DISTRIBUTED SYSTEM AVAILABILITY SIMULATION (" << total_simulation_hours << " HOURS)\n";
        std::cout << "================================================================================\n";

        for (size_t c = 0; c < components.size(); ++c) {
            const auto& comp = components[c];
            std::exponential_distribution<double> failure_dist(1.0 / comp.mtbf_hours);
            std::exponential_distribution<double> repair_dist(1.0 / comp.mttr_hours);

            double current_time = 0.0;
            double comp_down_hours = 0.0;

            while (current_time < static_cast<double>(total_simulation_hours)) {
                double time_to_fail = failure_dist(rng);
                current_time += time_to_fail;
                if (current_time >= static_cast<double>(total_simulation_hours)) break;

                double repair_time = repair_dist(rng);
                comp_down_hours += repair_time;
                current_time += repair_time;
            }

            component_downtimes[c] = comp_down_hours;
            // Series reliability model: System is down if ANY critical component is down
            total_system_downtime_hours += comp_down_hours;

            double comp_avail = 100.0 * (1.0 - (comp_down_hours / static_cast<double>(total_simulation_hours)));
            std::cout << "Component [" << std::setw(20) << std::left << comp.name << "] "
                      << "MTBF: " << std::setw(6) << comp.mtbf_hours << "h | "
                      << "MTTR: " << std::setw(4) << comp.mttr_hours << "h | "
                      << "Sim Downtime: " << std::setw(8) << std::fixed << std::setprecision(2) << comp_down_hours << "h | "
                      << "Availability: " << std::setprecision(4) << comp_avail << "%\n";
        }

        double system_availability = 100.0 * (1.0 - (total_system_downtime_hours / static_cast<double>(total_simulation_hours)));
        double annual_downtime_minutes = (total_system_downtime_hours / static_cast<double>(total_simulation_hours)) * 365.25 * 24.0 * 60.0;

        std::cout << "--------------------------------------------------------------------------------\n";
        std::cout << ">>> OVERALL SIMULATED SYSTEM AVAILABILITY: " << std::setprecision(5) << system_availability << "%\n";
        std::cout << ">>> EXPECTED ANNUAL UNPLANNED DOWNTIME    : " << std::setprecision(2) << annual_downtime_minutes << " minutes/year\n";
        std::cout << ">>> SLA FOUR-NINES (99.99%) STATUS       : " 
                  << (system_availability >= 99.99 ? "PASSED (COMPLIANT)" : "FAILED (BREACHED - REDESIGN REQUIRED)") << "\n";
        std::cout << "================================================================================\n";
    }
};

// ============================================================================
// MAIN EXECUTION PIPELINE
// ============================================================================

int main() {
    // ------------------------------------------------------------------------
    // STAGE 1: AHP Requirement Prioritization
    // ------------------------------------------------------------------------
    std::vector<std::string> criteria = {
        "Business Value", "Regulatory Compliance", "Security Risk", "Tech Feasibility"
    };
    AhpPriorityEngine ahp(criteria);

    // Pairwise Comparisons:
    // Business Value vs Regulatory: Regulatory is 3x more important (1/3)
    ahp.set_comparison(0, 1, 1.0 / 3.0);
    // Business Value vs Security: Security is 2x more important (1/2)
    ahp.set_comparison(0, 2, 1.0 / 2.0);
    // Business Value vs Tech Feasibility: Business Value is 4x more important (4)
    ahp.set_comparison(0, 3, 4.0);
    // Regulatory vs Security: Regulatory is 2x more important (2)
    ahp.set_comparison(1, 2, 2.0);
    // Regulatory vs Tech Feasibility: Regulatory is 7x more important (7)
    ahp.set_comparison(1, 3, 7.0);
    // Security vs Tech Feasibility: Security is 5x more important (5)
    ahp.set_comparison(2, 3, 5.0);

    auto [weights, is_consistent] = ahp.compute_weights_and_verify_consistency();

    std::cout << "\nCalculated AHP Criterion Weights:\n";
    for (size_t i = 0; i < criteria.size(); ++i) {
        std::cout << "  * " << std::setw(24) << std::left << criteria[i] << ": " 
                  << std::fixed << std::setprecision(4) << weights[i] * 100.0 << "%\n";
    }

    // Rank Candidate Requirements
    std::vector<ScoredRequirement> reqs = {
        {"FR-AUTH-01", "FIDO2 Biometric Authentication", {8.5, 9.5, 9.0, 7.0}},
        {"FR-REPT-02", "Export Monthly PDF Statements",   {6.0, 4.0, 2.0, 9.5}},
        {"FR-AUDT-03", "Immutable Blockchain Audit Trail",{5.0, 9.8, 8.5, 4.0}},
        {"FR-CHCK-04", "One-Click Mobile Checkout",      {9.5, 2.0, 5.0, 8.0}}
    };

    for (auto& r : reqs) {
        r.composite_utility = 0.0;
        for (size_t k = 0; k < weights.size(); ++k) {
            r.composite_utility += weights[k] * r.criteria_scores[k];
        }
    }

    std::sort(reqs.begin(), reqs.end(), [](const ScoredRequirement& a, const ScoredRequirement& b) {
        return a.composite_utility > b.composite_utility;
    });

    std::cout << "\n================================================================================\n";
    std::cout << "                   PRIORITIZED REQUIREMENTS RANKING (AHP)\n";
    std::cout << "================================================================================\n";
    for (size_t rank = 0; rank < reqs.size(); ++rank) {
        std::cout << "Rank #" << (rank + 1) << " | [" << reqs[rank].id << "] " 
                  << std::setw(34) << std::left << reqs[rank].title
                  << "Composite Utility Score: " << std::fixed << std::setprecision(3) << reqs[rank].composite_utility << "\n";
    }

    // ------------------------------------------------------------------------
    // STAGE 2: Monte Carlo Reliability & Four-Nines SLA Simulation
    // ------------------------------------------------------------------------
    MonteCarloReliabilitySimulator sim;
    // Architecture components with realistic MTBF and MTTR in hours
    sim.add_component("API Gateway Cluster", 8760.0,  0.08); // 1 failure/year, 4.8 min MTTR
    sim.add_component("Payment Microservice", 4380.0, 0.15); // 2 failures/year, 9.0 min MTTR
    sim.add_component("Distributed Postgres", 17520.0,0.50); // 1 failure/2 years, 30 min MTTR
    sim.add_component("Kafka Event Broker",   13140.0,0.10); // 1 failure/1.5 years, 6 min MTTR

    // Simulate 500,000 operational hours (~57 years of runtime)
    sim.run_simulation(500000);

    return 0;
}
```

</details>

---

### 7. Reference Video Lecture

{{ media:system-design-nfr-video }}

In this video by freeCodeCamp, high-scale system design and non-functional requirements are deconstructed, showing how latency percentiles, five-nines availability, and architectural trade-offs dictate enterprise software modeling.
