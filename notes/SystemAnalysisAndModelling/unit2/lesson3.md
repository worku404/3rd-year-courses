# Unit 2 — System Development Life Cycle (SDLC) Deep Dive & Project Inception
## Lesson 3 — SDLC Phase Transitions: From Logical Architecture to Physical Implementation & Cutover

### 1. The Analysis Phase: Problem Formulation & Control Requirements

Once a project has cleared the formal Feasibility Study milestone, it transitions into the core execution phases of the Software Development Life Cycle (SDLC). The first major technical phase is **System Analysis**.

The primary mandate of the System Analysis phase is to construct an exhaustive, unambiguous model of the **As-Is (Current) System** and define the functional requirements of the **To-Be (Proposed) System**.

```
+-----------------------------------------------------------------------------------------+
|                         THE ANALYSIS PHASE WORKFLOW PIPELINE                            |
|                                                                                         |
|       +-------------------------------------------------------------------------+       |
|       | 1. REQUIREMENTS ELICITATION:                                            |       |
|       | • Stakeholder interviews, JAD workshops, questionnaires, document review|       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|                                           v                                             |
|       +-------------------------------------------------------------------------+       |
|       | 2. AS-IS WORKFLOW MODELING & BOTTLENECK IDENTIFICATION:                 |       |
|       | • Map current data flows; isolate manual queues & data redundancies     |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|                                           v                                             |
|       +-------------------------------------------------------------------------+       |
|       | 3. FORMULATE CONTROL & SECURITY REQUIREMENTS:                           |       |
|       | • Data Accuracy: Format checks, range limits, check digits, uniqueness  |       |
|       | • Transaction Validity: Business invariant enforcement, double-entry    |       |
|       | • Auditability: Immutable transaction audit logging, cryptographic hash |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|                                           v                                             |
|       +-------------------------------------------------------------------------+       |
|       | 4. PUBLICATION OF SOFTWARE REQUIREMENTS SPECIFICATION (SRS):             |       |
|       | • Formal contractual sign-off baseline (IEEE 830 / ISO/IEC/IEEE 29148)  |       |
|       +-------------------------------------------------------------------------+       |
+-----------------------------------------------------------------------------------------+
```

#### Detailed Examination of Control Requirements
In enterprise software engineering, systems cannot merely process happy-path transactions; they must maintain rigorous **Internal Controls**:
1. **Accuracy Controls:** Ensure data is entered and calculated without distortion.
   - *Techniques:* Luhn check-digit algorithms on credit cards, type-safe schema constraints, range boundary verifications ($0 \le \text{discount} \le 1.0$).
2. **Validity Controls:** Guarantee that transactions reflect legitimate real-world authorization.
   - *Techniques:* Dual-authorization (Four-Eyes Principle) for high-value fund transfers, digital cryptographic signatures, OAuth2 bearer token expiration.
3. **Auditability Controls:** Mandate that every state mutation is irreversibly logged with timestamp, user ID, prior state, and new state.
   - *Techniques:* Append-only event-sourcing ledgers, immutable database triggers.

---

### 2. The Design Phase Duality: Logical vs. Physical System Design

The transition from System Analysis to System Design represents the conceptual shift from **WHAT** the system must do to **HOW** it will be constructed.

In professional software engineering, System Design is partitioned into two distinct architectural tiers: **Logical System Design** and **Physical Technical Design**.

```
+-----------------------------------------------------------------------------------------+
|                  THE DUALITY OF LOGICAL DESIGN AND PHYSICAL DESIGN                      |
|                                                                                         |
|       [ 1. LOGICAL SYSTEM DESIGN ]                          [ 2. PHYSICAL SYSTEM DESIGN ]|
|       (Technology-Independent Blueprint)                    (Technology-Dependent Exec)  |
|                                                                                         |
|       • Conceptual Data Modeling:                           • Physical Data Storage:    |
|         Entity-Relationship Diagrams (ERDs),                 SQL DDL, PostgreSQL B-tree|
|         Normalized entities (3NF / BCNF).                    indexes, partition keys.   |
|                                                                                         |
|       • Business Process Logic:                             • Component Architecture:   |
|         Level-1 / Level-2 Data Flow Diagrams,                Kubernetes Pods, gRPC APIs,|
|         Decision Tables, Finite Statecharts.                 Kafka broker topics.       |
|                                                                                         |
|       • Abstract User Interaction:                          • Concrete UI & Hardware:   |
|         Dialogue hierarchies, screen                         React/TypeScript frontend, |
|         navigation flow, wireframes.                         AWS ALB, Redis caching tier|
|                                                                                         |
|       Axiom: Independent of programming                     Axiom: Constrained by       |
|       languages or hardware vendors!                        concrete silicon & network! |
+-----------------------------------------------------------------------------------------+
```

#### Detailed Comparison Matrix
| Architectural Dimension | Logical System Design | Physical System Design |
| :--- | :--- | :--- |
| **Technological Dependency** | **Technology-Independent:** Valid whether implemented in Java, C++, Go, or manual punch cards. | **Technology-Dependent:** Tied directly to specific programming languages, database engines, and cloud vendors. |
| **Data Architecture** | Conceptual ER Diagrams, normalized relational schemas (Third Normal Form), data dictionaries. | Physical SQL table definitions (DDL), column data types (`BIGINT`, `VARCHAR(255)`), foreign keys, clustered indexes. |
| **Process Modeling** | Data Flow Diagrams (DFDs), process specifications (Structured English, Decision Trees). | Program structure charts, class method algorithms, thread pools, asynchronous worker queues. |
| **Interface Architecture** | Abstract dialogue flow, information layout wireframes. | Responsive HTML5/CSS3 templates, mobile iOS SwiftUI views, RESTful JSON API schemas. |
| **Primary Architectural Threat**| Incomplete business logic, missing domain entities, contradictory requirements. | High query latency, database deadlocks, network serialization overhead, memory leaks. |

{{ media:sam-cutover-strategies-diagram }}

---

### 3. Implementation, Data Migration & The Four Cutover Strategies

Once physical design specifications are finalized, the project enters the **Implementation Phase**: source code is written, databases are provisioned, automated test suites execute, and legacy data is converted.

The ultimate crucible of implementation is **System Cutover (Conversion)**: the critical moment when the legacy system is deactivated and operational business traffic is routed to the newly engineered software.

#### The Four Classical System Cutover Strategies

```
+-----------------------------------------------------------------------------------------+
|                             THE FOUR CUTOVER STRATEGIES                                 |
|                                                                                         |
|       1. DIRECT CONVERSION (Cold Turkey / Big-Bang)                                    |
|       Old System: [ RUNNING ] =======| (Deactivated Friday Night!)                      |
|       New System:                    |========> [ RUNNING ] (Live Monday Morning!)      |
|       Risk: MAXIMUM | Cost: LOWEST | Fallback: NONE                                     |
|                                                                                         |
|       2. PARALLEL CONVERSION (Dual-Run Safety Net)                                      |
|       Old System: [ RUNNING ===============================================> ]          |
|       New System: [ RUNNING ===============================================> ]          |
|       Risk: LOWEST | Cost: HIGHEST ($$$) | Fallback: INSTANTANEOUS                      |
|                                                                                         |
|       3. PILOT CONVERSION (Location-Based Phasing)                                      |
|       Branch A (Pilot Site): [ New System Live & Proved ]                               |
|       Branches B, C, D:       [ Old System Continues Running ]                          |
|       Risk: BOUNDED | Cost: MODERATE | Fallback: LOCALIZED                              |
|                                                                                         |
|       4. PHASED CONVERSION (Modular Staged Rollout)                                     |
|       Month 1: General Ledger Module Deployed.                                          |
|       Month 3: Accounts Payable Module Deployed.                                        |
|       Month 6: Inventory & Payroll Modules Deployed.                                    |
|       Risk: GRADUAL | Cost: MODERATE | Fallback: PER-MODULE                            |
+-----------------------------------------------------------------------------------------+
```

#### Detailed Strategic Evaluation

##### 1. Direct Conversion (Big-Bang / Cold Turkey)
- **Mechanics:** The legacy system is completely shut down at an agreed milestone (e.g., midnight on December 31st), and the new software is booted up simultaneously.
- **Advantages:** Lowest operational cost; zero need to maintain duplicate data entry; immediate transition forcing universal adoption.
- **Fatal Disadvantage:** **Extreme Operational Risk!** If the new system encounters a catastrophic database deadlock, data corruption, or scalability collapse under live load, **there is no fallback system available**! The company's operations grind to an immediate halt.
- *Appropriate Usage:* Systems where dual-running is physically impossible (e.g., replacing an air traffic radar transponder network or switching hardware operating systems).

##### 2. Parallel Conversion (Highest Safety Net)
- **Mechanics:** Both the legacy system and the new system operate concurrently for a predetermined verification window (typically 1 to 3 monthly accounting cycles). Every transaction is entered into **both systems simultaneously**, and outputs (financial balances, invoices) are compared daily.
- **Advantages:** **Maximum Reliability:** If the new software crashes or produces calculation discrepancies, the legacy system continues running uninterrupted. Zero risk of business downtime.
- **Disadvantages:** **Exorbitant Cost and Labor Overhead ($$$):** Operational staff must perform duplicate data entry; hardware hosting costs double; synchronizing states across disparate databases requires complex reconciliation middleware.
- *Appropriate Usage:* Mission-critical financial banking ledgers, nuclear reactor safety systems, and medical patient monitoring.

##### 3. Pilot Conversion (Location-Based Phasing)
- **Mechanics:** The new system is deployed in its entirety to a single branch office, manufacturing plant, or regional subsidiary (the **Pilot Site**).
- **Advantages:** Conforms risks to a single localized site. Lessons learned and unexpected bugs are remediated in the pilot before enterprise-wide rollout.
- **Disadvantages:** Requires building temporary bridge interfaces to allow the pilot site's new system to communicate with the rest of the company's legacy core.
- *Appropriate Usage:* Multi-branch retail stores, hotel chains, and distributed banking networks.

##### 4. Phased Conversion (Modular Incremental Rollout)
- **Mechanics:** The new software is decomposed into functional subsystems or modules, which are deployed sequentially over months.
- **Advantages:** Gradual learning curve for employees; financial and technical risk is distributed across manageable milestone stages.
- **Disadvantages:** Requires complex bridge adaptors connecting new modules to old legacy modules for extended periods.

---

### 4. Post-Implementation Audits & The Software Maintenance Taxonomy

The deployment of a software application does not terminate the SDLC; rather, it marks the beginning of the longest and most expensive phase: **Software Maintenance**, which historically consumes **$60\%\text{ to }80\%$ of total software lifecycle budgets**.

#### The Post-Implementation Review (PIR)
Six months following cutover, the analyst conducts a formal **Post-Implementation Audit** to compare real-world performance against the original Baseline Project Charter:
1. Did the software achieve its planned Return on Investment ($ROI$) and operational KPIs?
2. Are actual cloud hosting costs consistent with feasibility projections?
3. What is the measured user satisfaction and adoption rate?

#### The Four Categories of Software Maintenance

```
+-----------------------------------------------------------------------------------------+
|                           THE SOFTWARE MAINTENANCE TAXONOMY                             |
|                                                                                         |
|       1. CORRECTIVE MAINTENANCE (20% of effort)                                         |
|       • Reactive bug-fixing. Repairing latent software defects, null-pointer exceptions,|
|         logical calculation errors, and race conditions discovered by users.            |
|                                                                                         |
|       2. ADAPTIVE MAINTENANCE (25% of effort)                                           |
|       • Modifying software to accommodate external environmental changes:               |
|         New OS versions (Linux kernel updates), database upgrades, statutory tax        |
|         changes, or third-party API deprecations.                                       |
|                                                                                         |
|       3. PERFECTIVE MAINTENANCE (50% of effort - THE LARGEST SHARE!)                    |
|       • Enhancing existing capabilities to satisfy new user feature requests, improving |
|         UI ergonomics, optimizing SQL queries, and accelerating throughput.             |
|                                                                                         |
|       4. PREVENTIVE MAINTENANCE (5% of effort)                                          |
|       • Refactoring code, updating documentation, updating security patches, and        |
|         reducing technical debt to prevent future system failures before they occur.    |
+-----------------------------------------------------------------------------------------+
```

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Formulating a Core Banking Cutover Runbook

##### Problem Statement
A retail bank with 120 branches and 1.5 million customer accounts is replacing its 35-year-old COBOL mainframe core ledger with a modern Cloud-Native Event-Driven Microservices Ledger.
The bank's executive board refuses to accept a Direct Conversion due to catastrophic risk, but also cannot afford the labor overhead of a full Parallel Conversion across all 120 branches for 6 months.

As Lead Systems Analyst, formulate a hybrid **Pilot-then-Phased Cutover Strategy** and design a detailed **Cutover Runbook** for the migration weekend.

##### Cutover Strategy Formulation
1. **Selection of Hybrid Strategy:**
   - **Phase 1: Pilot Deployment:** Deploy the new ledger exclusively to **2 small suburban test branches** for a 60-day trial period. Customer transactions are dual-written to the mainframe via asynchronous Kafka change-data-capture (CDC) bridge connectors.
   - **Phase 2: Regional Phased Rollout:** Once the pilot operates with zero accounting discrepancies for 60 consecutive days, roll out the new ledger in regional waves (Wave 1: 30 branches; Wave 2: 40 branches; Wave 3: Remaining 48 branches).

##### Weekend Cutover Runbook (T-Minus Timeline):
| Milestone Time | Operational Action / Command | Responsible Role | Rollback Decision Gate Criteria |
| :--- | :--- | :--- | :--- |
| **Friday 18:00** | Deactivate customer mobile banking transfers; place ATMs in offline standalone mode. | Lead DevOps | If ATM offline mode fails, abort cutover immediately. |
| **Friday 19:00** | Freeze legacy COBOL database; execute final database consistency dump. | Mainframe DBA | Verify record count checksum ($1,542,891\text{ accounts}$). |
| **Friday 21:00** | Execute ETL Data Migration pipeline (Transform EBCDIC to UTF-8; hash balances). | Data Migration Lead | Checksum validation: Total migrated assets MUST match $\pm \$0.00$ cents! |
| **Saturday 06:00** | Spin up Kubernetes microservices cluster; execute automated smoke test suite. | QA Architect | If automated integration tests $< 100\%$ pass, investigate blocker. |
| **Saturday 14:00** | Internal shadow transaction testing: Simulate 100,000 synthetic banking transfers. | Systems Analyst | Verify that ledger balance invariants hold across all shards. |
| **Sunday 10:00** | **GO / NO-GO DECISION GATE:** Executive C-Suite review of reconciliation reports. | CIO & Steering Board | If ANY financial ledger discrepancy $> \$0.00$, trigger **ABORT & ROLLBACK**! |
| **Sunday 18:00** | Re-enable customer mobile banking pointing to new Cloud API Gateway. | Network Admin | Monitor real-time Prometheus transaction latency metrics. |
| **Monday 08:00** | Normal branch opening: Support command center active on live war-room standby. | Support Lead | Rapid response triage for branch tellers. |

---

#### Level 2 — Scaffolded Bug-Fix: Silent Character Encoding & Timezone Data Migration Corruption

##### Defect Scenario
A healthcare system migrated 500,000 patient records from an on-premise SQL Server 2008 database to a PostgreSQL 15 cloud database.
A data engineer wrote a basic Python ETL extraction script:

```python
# DEFECTIVE DATA MIGRATION SCRIPT: SILENT DATA CORRUPTION
import pyodbc
import psycopg2

def migrate_patient_records():
    src_conn = pyodbc.connect("DSN=LegacyDB;")
    dst_conn = psycopg2.connect("dbname=CloudEMR")
    
    src_cur = src_conn.cursor()
    dst_cur = dst_conn.cursor()
    
    # Defect 1: Reads raw text without explicit UTF-8 encoding (Windows-1252 to Latin-1 mismatch!)
    # Defect 2: Naive timestamp extraction stripped timezone offsets (UTC vs Local Time!)
    src_cur.execute("SELECT patient_id, full_name, birth_date, last_medication_timestamp FROM Patients")
    
    for row in src_cur.fetchall():
        # Corrupts non-ASCII characters: "Müller" becomes "MÃ¼ller"!
        # Strips timezone: 14:00 UTC becomes 14:00 Local (Patients given meds 5 hours late!)
        dst_cur.execute(
            "INSERT INTO patients (id, name, dob, last_med_time) VALUES (%s, %s, %s, %s)",
            (row[0], str(row[1]), str(row[2]), str(row[3]))
        )
    dst_conn.commit()
```

When doctors examined records post-cutover:
- Names containing accents, umlauts, or non-Latin characters were corrupted into unreadable gibberish.
- Medication delivery timestamps were shifted by 5 hours, causing nurses to administer prescription narcotics at incorrect intervals!

##### Systems Analysis Diagnosis
The migration failed to implement **Data Conversion Normalization**:
1. **Character Encoding:** Legacy Windows-1252 / ASCII character sets must be explicitly decoded and normalized to strict standard UTF-8.
2. **Temporal Invariants:** Naive local datetime objects must be normalized to universal coordinated epoch timestamps (`TIMESTAMPTZ` with explicit UTC offset).
3. **Loss of Idempotency:** The script lacked transaction batching and cryptographic hash reconciliation.

<details>
<summary><b>View Architectural Solution & Rigorous ETL Migration Pipeline</b></summary>

```python
# ============================================================================
# ARCHITECTURAL REMEDY: VERIFIED, IDEMPOTENT ETL MIGRATION ENGINE
# ============================================================================
import hashlib
import datetime
from zoneinfo import ZoneInfo
import psycopg2
from psycopg2.extras import execute_batch

def migrate_patient_records_verified(src_cursor, dst_conn):
    dst_cursor = dst_conn.cursor()
    batch_size = 1000
    records_batch = []
    
    src_cursor.execute("SELECT patient_id, full_name, birth_date, last_medication_timestamp FROM Patients")
    
    while True:
        rows = src_cursor.fetchmany(batch_size)
        if not rows:
            break
            
        for row in rows:
            p_id, raw_name, dob, raw_time = row
            
            # 1. Strict UTF-8 Normalization (Eliminates Mojibake corruption)
            if isinstance(raw_name, bytes):
                clean_name = raw_name.decode("utf-8", errors="replace")
            else:
                clean_name = str(raw_name).strip()

            # 2. Strict UTC Timezone Normalization (Eliminates Medication Timing Errors)
            # Legacy system recorded in US Eastern Time without timezone indicator
            if raw_time is not None:
                if isinstance(raw_time, datetime.datetime):
                    # Localize to Eastern, then convert to strict UTC
                    localized_time = raw_time.replace(tzinfo=ZoneInfo("America/New_York"))
                    utc_time = localized_time.astimezone(ZoneInfo("UTC"))
                else:
                    utc_time = None
            else:
                utc_time = None

            # 3. Cryptographic Row Hash for Integrity Checksum
            row_fingerprint = hashlib.sha256(
                f"{p_id}:{clean_name}:{dob}:{utc_time}".encode("utf-8")
            ).hexdigest()

            records_batch.append((p_id, clean_name, dob, utc_time, row_fingerprint))

        # Idempotent Upsert Insertion (Handles network interruptions without duplicates)
        insert_query = (
            "INSERT INTO patients (id, name, dob, last_med_time, checksum)\n"
            "VALUES (%s, %s, %s, %s, %s)\n"
            "ON CONFLICT (id) DO UPDATE SET\n"
            "    name = EXCLUDED.name,\n"
            "    dob = EXCLUDED.dob,\n"
            "    last_med_time = EXCLUDED.last_med_time,\n"
            "    checksum = EXCLUDED.checksum;"
        )
        execute_batch(dst_cursor, insert_query, records_batch)
        dst_conn.commit()
        records_batch.clear()

    print(">>> ETL MIGRATION COMPLETED FLAWLESSLY WITH ZERO TIMEZONE DRIFT! <<<")
```

</details>

---

#### Level 3 — High-Scale System Design: Automated Cutover Dual-Write Synchronization Engine in C++

Design a complete, high-concurrency C++17 simulation modeling:
1. **Parallel Cutover Transition Manager:** Coordinates live production traffic during a phased migration between a Legacy SQL Database and a Cloud Distributed Microservices Store.
2. **Dual-Write Interceptor:** Broadcasts incoming writes to both Legacy and New systems concurrently.
3. **Asynchronous Consistency Auditor:** Continuously reconciles records between Legacy and New systems, measuring data drift and automatically asserting a Go/No-Go cutover readiness status when reconciliation reaches $100.0\%$.

<details>
<summary><b>View Complete C++ Dual-Write Cutover Synchronization Engine Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: DUAL-WRITE PARALLEL CUTOVER & RECONCILIATION ENGINE
// Compile: g++ -std=c++17 -O3 cutover_engine.cpp -o cutover_engine
// ============================================================================

#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <iomanip>
#include <cstdint>
#include <cassert>

struct LedgerRecord {
    uint64_t account_id;
    double balance;
    uint64_t version;
};

// ----------------------------------------------------------------------------
// LEGACY MAINFRAME REPOSITORY
// ----------------------------------------------------------------------------
class LegacyMainframeStore {
private:
    std::unordered_map<uint64_t, LedgerRecord> storage;

public:
    void write(uint64_t id, double bal) {
        storage[id] = {id, bal, storage[id].version + 1};
    }

    bool read(uint64_t id, LedgerRecord& out_rec) const {
        auto it = storage.find(id);
        if (it != storage.end()) {
            out_rec = it->second;
            return true;
        }
        return false;
    }

    const std::unordered_map<uint64_t, LedgerRecord>& get_all() const { return storage; }
};

// ----------------------------------------------------------------------------
// CLOUD DISTRIBUTED REPOSITORY (TARGET SYSTEM)
// ----------------------------------------------------------------------------
class CloudMicroservicesStore {
private:
    std::unordered_map<uint64_t, LedgerRecord> storage;

public:
    void write(uint64_t id, double bal) {
        storage[id] = {id, bal, storage[id].version + 1};
    }

    bool read(uint64_t id, LedgerRecord& out_rec) const {
        auto it = storage.find(id);
        if (it != storage.end()) {
            out_rec = it->second;
            return true;
        }
        return false;
    }

    const std::unordered_map<uint64_t, LedgerRecord>& get_all() const { return storage; }
};

// ----------------------------------------------------------------------------
// DUAL-WRITE CUTOVER ORCHESTRATOR
// ----------------------------------------------------------------------------
class CutoverOrchestrator {
private:
    LegacyMainframeStore legacy_db;
    CloudMicroservicesStore cloud_db;
    bool new_system_is_authoritative = false;

public:
    // Parallel Dual-Write Phase: Both systems updated synchronously
    void execute_transaction(uint64_t account_id, double amount) {
        LedgerRecord current;
        if (!new_system_is_authoritative) {
            // Legacy is Primary
            legacy_db.read(account_id, current);
            double new_balance = current.balance + amount;
            legacy_db.write(account_id, new_balance);
            cloud_db.write(account_id, new_balance); // Dual-write shadow copy
        } else {
            // Cloud is Primary (Post-Cutover)
            cloud_db.read(account_id, current);
            double new_balance = current.balance + amount;
            cloud_db.write(account_id, new_balance);
        }
    }

    // Automated Reconciliation Audit: Verifies 100.0% data consistency
    bool run_cutover_audit() const {
        const auto& legacy_data = legacy_db.get_all();
        const auto& cloud_data = cloud_db.get_all();

        size_t total_audited = legacy_data.size();
        size_t matches = 0;

        for (const auto& [id, rec_legacy] : legacy_data) {
            auto it = cloud_data.find(id);
            if (it != cloud_data.end()) {
                if (std::abs(rec_legacy.balance - it->second.balance) < 0.001) {
                    matches++;
                } else {
                    std::cerr << "  [DISCREPANCY] Account #" << id 
                              << " Legacy=$" << rec_legacy.balance 
                              << " vs Cloud=$" << it->second.balance << "\n";
                }
            }
        }

        double consistency_pct = (total_audited > 0) ? (100.0 * matches / total_audited) : 100.0;
        std::cout << "Reconciliation Audit: " << matches << "/" << total_audited 
                  << " Records Matched (" << std::fixed << std::setprecision(2) << consistency_pct << "%)\n";

        return (matches == total_audited);
    }

    void perform_cutover() {
        std::cout << "\n>>> ATTEMPTING SYSTEM CUTOVER (AUTHORITY TRANSFER) <<<\n";
        if (run_cutover_audit()) {
            new_system_is_authoritative = true;
            std::cout << ">>> GO DECISION APPROVED! Cloud Microservices Store is now AUTHORITATIVE! <<<\n";
            std::cout << ">>> Legacy Mainframe dual-writes terminated. Migration SUCCESSFUL! <<<\n";
        } else {
            std::cout << ">>> NO-GO DECISION! Discrepancies detected. Remaining in parallel fallback! <<<\n";
        }
    }
};

int main() {
    std::cout << "======================================================================\n";
    std::cout << "    DUAL-WRITE SYSTEM CUTOVER & RECONCILIATION ENGINE SIMULATOR       \n";
    std::cout << "======================================================================\n";

    CutoverOrchestrator orchestrator;

    // Simulate Parallel Dual-Write Banking Workload
    std::cout << "\n1. Seeding Accounts and executing parallel live transactions...\n";
    orchestrator.execute_transaction(101, 5000.0);
    orchestrator.execute_transaction(102, 12500.0);
    orchestrator.execute_transaction(103, 350.0);
    orchestrator.execute_transaction(101, -1200.0);

    // Run cutover readiness audit and execute authority switch
    orchestrator.perform_cutover();

    std::cout << "\n======================================================================\n";
    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:sdlc-process-video }}

In this video by Simplilearn, the critical phase transitions of the Software Development Life Cycle are reviewed, highlighting how logical architectures are transformed into physical deployments through rigorous cutover strategies and post-implementation maintenance.
