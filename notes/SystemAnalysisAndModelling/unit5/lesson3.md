# Unit 5 — Object-Oriented Analysis, UML 2.5 Metamodel & Use Case Engineering
## Lesson 3 — Systematic Use Case Discovery: User Goal, Event Decomposition & CRUD Matrix Verification

### 1. The Challenge of Comprehensive Requirements Discovery

One of the most persistent hazards in software systems analysis is **omission**—the failure to discover critical functional capabilities until the system is already undergoing user acceptance testing (UAT) or running in production. Informal interviews and ad-hoc brainstorming sessions rarely uncover subtle edge cases, background temporal tasks, or system-level state triggers.

To guarantee $100\%$ functional completeness without omission, software engineers apply **three rigorous, complementary use case discovery techniques**:

{{ media:sam-use-case-discovery-diagram }}

```
+---------------------------------------------------------------------------------------------------+
|                        THE THREE USE CASE DISCOVERY METHODOLOGIES                                 |
+---------------------------------------------------------------------------------------------------+
| 1. USER GOAL TECHNIQUE       : User-centric & role-driven; discovers human operational tasks      |
|                                and direct business interactions.                                  |
|                                                                                                   |
| 2. EVENT DECOMPOSITION       : Stimulus-response comprehensive modeling; captures external,       |
|                                temporal (time-driven), and internal state events.                 |
|                                                                                                   |
| 3. CRUD CROSS-CHECK MATRIX   : Data-centric mathematical verification; ensures every persistent   |
|                                domain entity possesses complete Create, Read, Update, Delete flows|
+---------------------------------------------------------------------------------------------------+
```

---

### 2. Technique 1: The User Goal Technique

The **User Goal Technique** is the most intuitive and widespread elicitation method. It approaches the system through the eyes of the human users, identifying the specific goals that each stakeholder role must achieve using the software.

#### 2.1 The 8-Step Canonical User Goal Procedure
1. **Identify Potential User Classes:** Catalog all human roles interfacing with the platform (e.g., Clinical Nurses, Attending Physicians, Billing Specialists, System Administrators).
2. **Classify Users by Functional Domain:** Segment roles into operational boundaries (e.g., Triage, Pharmacy, Inpatient Wards, Finance, Auditing).
3. **Classify by Organizational Hierarchy:** Stratify users by administrative tier:
   - *Operational Tier:* Daily frontline task execution (e.g., bedside barcode scanning).
   - *Managerial Tier:* Operational supervision and approval overrides (e.g., schedule staffing, sign off on narcotic inventory).
   - *Executive Tier:* Strategic governance and compliance reporting (e.g., hospital readmission rates, gross margin analytics).
4. **Conduct Targeted Goal Interviews:** Ask stakeholders: *"What specific tasks do you need the software to help you complete?"*
5. **Synthesize Preliminary Use Cases:** Draft candidate use cases named with active verb-noun phrases (e.g., *"Admit Patient"*, *"Dispense Medication"*).
6. **Eliminate Synonyms and Disambiguate Duplicates:** Merge identical tasks called different names across departments.
7. **Identify Shared Multi-User Cases:** Determine where multiple user roles participate in the same workflow (e.g., both Physician and Nurse review the medical chart).
8. **Review and Baseline with Executive Sponsors:** Secure formal sign-off on the candidate catalog.

* **Structural Limitation of User Goal Technique:** It is inherently human-centric. It is completely blind to automated background server routines, scheduled batch reconciliations, and embedded hardware sensor interrupts.

---

### 3. Technique 2: The Event Decomposition Technique

The **Event Decomposition Technique** is the most comprehensive and mathematically sound elicitation methodology. Rather than focusing solely on user desires, it models the system as a stateful computational engine that continuously reacts to **Events** occurring in its environment.

An **Event** is defined as:
> *An occurrence at a specific point in time and space that can be precisely described, disrupts the system's equilibrium, and demands an immediate, stateful operational response.*

```
+---------------------------------------------------------------------------------------------------+
|                            THE THREE CANONICAL EVENT TAXONOMIES                                   |
+---------------------------------------------------------------------------------------------------+
| EVENT TYPE            | TRIGGERING MECHANISM                  | CONCRETE SYSTEM USE CASE          |
| --------------------- | ------------------------------------- | --------------------------------- |
| 1. EXTERNAL EVENT     | Initiated by an external actor, user, | * Event: Patient scans wristband. |
|                       | sensor, or external API subsystem.    | -> UC: "Register Patient Arrival" |
|                                                                                                   |
| 2. TEMPORAL EVENT     | Triggered automatically by reaching a | * Event: Daily clock hits 23:59.  |
|                       | specific point in time or calendar.   | -> UC: "Generate Billing Ledger"  |
|                                                                                                   |
| 3. STATE EVENT        | Triggered when an internal variable   | * Event: ICU Oxygen tank < 15%.   |
|                       | breaches a critical threshold.        | -> UC: "Dispatch Refill Alert"    |
+---------------------------------------------------------------------------------------------------+
```

#### 3.1 External Events
External events occur outside the system boundary. They fall into three primary categories:
- *Transaction Requests:* An actor wants to complete an action (e.g., *"Customer authorizes credit card payment"*).
- *Information Queries:* An actor requests synthesized data (e.g., *"Surgeon requests 3D CT-scan rendering"*).
- *Data Updates:* External information has changed (e.g., *"Insurance clearinghouse updates patient deductible"*).

#### 3.2 Temporal Events
Temporal events do not have an external actor pushing a button. They are driven by internal clocks and timers:
- *Batch Reconciliations:* End-of-day bank clearinghouse settlements at 17:00 EST.
- *Periodic Operational Summaries:* Weekly narcotic inventory variance reports.
- *Expiration Sweeps:* Purging abandoned shopping carts after 30 minutes of user inactivity.

#### 3.3 State Events
State events are triggered when an internal system condition or physical physical metric changes state:
- *Safety Invariant Breaches:* Reactor core temperature exceeds $650^\circ\text{C}$.
- *Reorder Points:* Warehouse stock drops below Safety Stock threshold ($\text{Inventory} \le \text{ROP}$).
- *Heart Telemetry Dropouts:* Sensor packet loss persists for $> 500\text{ ms}$.

#### 3.4 The Perfect Technology Assumption
When executing Event Decomposition, software analysts apply the **Perfect Technology Assumption**:
> *Assume that all hardware processors are infinitely fast, memory storage capacity is infinite, networks have zero latency and 100% reliability, and software never crashes.*

Why apply this assumption during analysis?
If analysts worry about database connection pooling, disk space, or network retry loops during the requirements phase, they become bogged down in technical infrastructure before defining the business problem. Technical exceptions (e.g., handling server offline mode) are deferred to System Architecture and Design.

---

### 4. Technique 3: The CRUD Cross-Verification Matrix

The **CRUD Technique** provides a rigorous mathematical sanity check against the system's persistent domain data model. Derived from database theory, **CRUD** stands for:
- **C**reate: Instantiate and persist a new record.
- **R**ead / Report: Retrieve, search, display, or summarize existing records.
- **U**pdate: Mutate the attributes or state of an existing record.
- **D**elete: Retire, soft-delete, or archive an obsolete record.

```
+---------------------------------------------------------------------------------------------------+
|                        CANONICAL CRUD-TO-USE-CASE CROSS-CHECK MATRIX                              |
+---------------------------------------------------------------------------------------------------+
| DOMAIN ENTITY         | CREATE (C)         | READ (R)           | UPDATE (U)         | DELETE (D) |
| --------------------- | ------------------ | ------------------ | ------------------ | ---------- |
| Patient               | Admit Patient      | Query Patient Chart| Update Demographics| Archive Rx |
| Prescription          | Prescribe Drug     | Display Active Rx  | Amend Rx Dosage    | Void Rx    |
| TelemetrySample       | Ingest Sensor Feed | Render Waveform    | Filter Artifact    | Purge Data |
| BillingInvoice        | Generate Invoice   | Audit Accounts     | Apply Discount     | Write-Off  |
+---------------------------------------------------------------------------------------------------+
```

#### 4.1 The CRUD Verification Rules
1. **The Orphan Entity Invariant:** Every domain class in the data model must have at least one Use Case for each of the four CRUD operations ($C, R, U, D$).
2. **The Immutable Trap Defect:** If an entity has a Create use case and Read use case, but lacks an Update or Delete use case, the entity can never be corrected if a data entry error occurs, and can never be archived.
3. **The Spontaneous Manifestation Defect:** If an entity has an Update or Delete use case, but has zero Create use cases, the system attempts to manipulate records that can never be instantiated!

---

### 5. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

An architectural team is drafting the software requirements specification for a Smart Autonomous Greenhouse Agricultural Platform. The greenhouse is equipped with soil moisture sensors, climate control actuators, automated nutrient drip feeds, and commercial buyer portal access.

Below are six candidate operational requirements:
1. *"Requirement 1: Soil moisture level drops below 28% volumetric water content."*
2. *"Requirement 2: Greenhouse Facility Manager logs in to adjust target CO2 enrichment thresholds."*
3. *"Requirement 3: The clock strikes 06:00:00 AM local sunrise time."*
4. *"Requirement 4: Commercial wholesale distributor submits an order for 500 kg of hydroponic tomatoes."*
5. *"Requirement 5: Ambient greenhouse temperature exceeds 38°C for more than 5 consecutive minutes."*
6. *"Requirement 6: Weekly Sunday midnight timer triggers automated billing invoices for water/power consumption."*

**Architectural Analysis Assignment:**
1. Classify each requirement using the **Event Decomposition Technique** into: **External Event**, **Temporal Event**, or **State Event**.
2. Formulate the precise, active verb-noun **Use Case Name** corresponding to each event.
3. Construct a mini CRUD matrix for the `NutrientBatch` entity, proving that all four lifecycle operations are addressed.

<details>
<summary>Click to view Level 1 Solution & Architectural Analysis</summary>

##### 1. Event Classification & Use Case Mapping:
- **Requirement 1:** **State Event** (Triggered when internal physical telemetry variable breaches threshold: $\text{Moisture} < 28\%$).
  $\implies$ **Use Case:** *"Dispense Automated Irrigation Drip"*.
- **Requirement 2:** **External Event** (Initiated by human Facility Manager actor interfacing with the UI).
  $\implies$ **Use Case:** *"Configure Climate Control Thresholds"*.
- **Requirement 3:** **Temporal Event** (Triggered by real-time clock reaching designated sunrise hour).
  $\implies$ **Use Case:** *"Engage Photosynthetic Light Deployment"*.
- **Requirement 4:** **External Event** (Initiated by external commercial buyer submitting a purchasing transaction).
  $\implies$ **Use Case:** *"Process Wholesale Produce Order"*.
- **Requirement 5:** **State Event** (Triggered by internal ambient sensor condition: $\text{Temp} > 38^\circ\text{C}$ for $t > 300\text{ s}$).
  $\implies$ **Use Case:** *"Activate Emergency Cooling Louvers"*.
- **Requirement 6:** **Temporal Event** (Triggered by recurring weekly calendar schedule: Sunday 23:59:59 UTC).
  $\implies$ **Use Case:** *"Generate Utility Consumption Invoices"*.

##### 2. CRUD Matrix for `NutrientBatch` Entity:
- **Create (C):** *"Formulate Nutrient Batch"* (Manager mixes chemical nitrogen/phosphorus formulation).
- **Read (R):** *"Inspect Nutrient Chemical Density"* (Sensors query PPM electrical conductivity).
- **Update (U):** *"Titrate Nutrient pH Balance"* (System injects acidic/alkaline buffer solution).
- **Delete / Archive (D):** *"Purge Exhausted Reservoir"* (System drains and flushes irrigation tanks).
*Verification Result: All four CRUD operations are covered. Zero immutable traps.*

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The Flawed CRUD Matrix Auditor

A software engineering team wrote an automated Python script to cross-reference domain entity classes with the use case catalog to verify CRUD completeness. However, the script is generating false 100% compliance reports because it counts soft-delete/void actions as hard deletes and misses entities that lack Create operations.

Examine the flawed script below:

```python
# FLAWED CRUD MATRIX AUDITOR (PYTHON)
def audit_crud_coverage(entities, use_case_catalog):
    crud_matrix = {e: {"C": False, "R": False, "U": False, "D": False} for e in entities}

    for uc in use_case_catalog:
        name_lower = uc["name"].lower()
        for e in entities:
            e_lower = e.lower()
            if e_lower in name_lower:
                # BUG 1: Naive substring matching!
                # "Update" matches inside "Update" but misses "Amend", "Modify", "Edit"!
                # "Delete" misses "Archive", "Retire", "Void", "Purge"!
                if "create" in name_lower or "add" in name_lower:
                    crud_matrix[e]["C"] = True
                if "read" in name_lower or "view" in name_lower:
                    crud_matrix[e]["R"] = True
                if "update" in name_lower:
                    crud_matrix[e]["U"] = True
                if "delete" in name_lower:
                    crud_matrix[e]["D"] = True

    # BUG 2: Calculates coverage percentage as a flat average across all entities,
    # concealing that a critical core entity (e.g. 'Prescription') has 0% Delete capability!
    total_checks = len(entities) * 4
    passed_checks = sum(sum(1 for v in c.values() if v) for c in crud_matrix.values())
    coverage_score = (passed_checks / total_checks) * 100
    
    return crud_matrix, coverage_score
```

**Debug Assignment:**
1. Identify all semantic vocabulary gaps, false negatives, and reporting flaws in this script.
2. Implement formal synonym classification dictionaries for CRUD actions:
   - Create: `create, add, register, admit, instantiate, draft, new, ingest`
   - Read: `read, view, query, display, search, render, report, inspect, fetch`
   - Update: `update, amend, modify, revise, edit, titrate, change, recalculate`
   - Delete: `delete, archive, void, purge, cancel, decommission, retire, remove`
3. Refactor the auditor to flag every specific entity that has an incomplete CRUD lifecycle.

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. Identified Flaws:
- **Brittle Substring Matching:** Natural language use case names rarely use textbook words like *"Read"* or *"Delete"*. Real systems use *"Prescribe Medication"* (Create), *"Query Patient Chart"* (Read), *"Amend Dosage"* (Update), and *"Void Prescription"* (Delete). The original script failed to identify these, flagging valid systems as defective.
- **Aggregate Masking Defect:** Reporting a 75% overall coverage score conceals critical system vulnerabilities. If 3 entities have 100% coverage, but the most vital entity (`Patient`) has zero Delete or Archive capability, the platform violates GDPR/HIPAA "Right to be Forgotten" mandates!

##### 2. Corrected Production Implementation:

```python
import re
from typing import Dict, List, Set, Tuple

class ProductionCrudAuditor:
    CRUD_VOCABULARY = {
        "C": {"create", "add", "register", "admit", "instantiate", "draft", "new", "ingest", "prescribe", "book"},
        "R": {"read", "view", "query", "display", "search", "render", "report", "inspect", "fetch", "check"},
        "U": {"update", "amend", "modify", "revise", "edit", "titrate", "change", "recalculate", "reschedule"},
        "D": {"delete", "archive", "void", "purge", "cancel", "decommission", "retire", "remove", "discharge"}
    }

    def __init__(self, entities: List[str]):
        self.entities = entities

    def tokenize_name(self, text: str) -> Set[str]:
        return set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))

    def audit_catalog(self, use_cases: List[Dict]) -> Tuple[Dict, List[str]]:
        matrix = {e: {"C": set(), "R": set(), "U": set(), "D": set()} for e in self.entities}
        defects = []

        for uc in use_cases:
            uc_tokens = self.tokenize_name(uc["name"])
            
            # Check which entity is referenced
            for e in self.entities:
                if e.lower() in uc_tokens:
                    # Check which CRUD operation matches
                    for op_code, vocab in self.CRUD_VOCABULARY.items():
                        if not uc_tokens.isdisjoint(vocab):
                            matrix[e][op_code].add(uc["name"])

        # Validate completeness for each entity individually
        for e in self.entities:
            missing_ops = [op for op, ucs in matrix[e].items() if len(ucs) == 0]
            if missing_ops:
                defects.append(
                    f"[CRUD INCOMPLETE] Domain Entity '{e}' is missing required operations: {missing_ops}"
                )

        return matrix, defects
```

</details>

---

#### Level 3 — High-Scale System Design: Interactive Event Decomposition & CRUD Lifecycle Coverage Engine in C++

Design and implement a complete, production-grade C++17 **Event Decomposition & CRUD Lifecycle Coverage Engine**. The system must:
1. Ingest candidate system events classified across the three canonical event categories:
   - `EXTERNAL_EVENT` (Actor stimulus, input parameters)
   - `TEMPORAL_EVENT` (Cron/Timer frequency, scheduled point in time)
   - `STATE_EVENT` (Internal telemetry predicate, threshold condition)
2. Map each event to a formal, active verb-noun **Use Case** definition.
3. Ingest the system's **Domain Class Entities** and maintain a bidirectional **CRUD Cross-Reference Matrix**.
4. Perform automated verification algorithms:
   - Verify that all events map to valid use cases.
   - Assert $100\%$ CRUD lifecycle coverage across all persistent domain entities.
   - Detect **Immutable Traps** (Entities missing Update or Delete).
   - Detect **Phantom Entities** (Entities with Update/Delete but missing Create).
5. Output a formal tabular compliance audit report.

<details>
<summary>Click to view complete C++17 Event Decomposition & CRUD Engine</summary>

```cpp
/**
 * ============================================================================
 * EVENT DECOMPOSITION & CRUD LIFECYCLE COVERAGE ENGINE (C++17)
 * ============================================================================
 * Implements:
 * 1. Event Taxonomy Modeling (External, Temporal, State Events).
 * 2. Event-to-Use-Case Structural Synthesis.
 * 3. Bidirectional Domain Entity CRUD Cross-Reference Matrix.
 * 4. Lifecycle Invariant Verification (Immutable Traps & Phantom Entities).
 * ============================================================================
 */

#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <iomanip>
#include <algorithm>

// ============================================================================
// DOMAIN MODELS & DATA STRUCTURES
// ============================================================================

enum class EventType {
    EXTERNAL_EVENT,
    TEMPORAL_EVENT,
    STATE_EVENT
};

struct SystemEvent {
    std::string id;
    std::string description;
    EventType type;
    std::string triggering_source; // Actor, Cron expression, or Sensor predicate
    std::string resulting_use_case_id;
};

struct UseCaseItem {
    std::string id;
    std::string name;
    std::string primary_actor;
};

enum class CrudOp {
    CREATE,
    READ,
    UPDATE,
    DELETE_ARCHIVE
};

struct CrudBinding {
    std::string entity_name;
    CrudOp operation;
    std::string use_case_id;
};

// ============================================================================
// VERIFICATION & AUDIT ENGINE
// ============================================================================

class EventCrudVerificationEngine {
private:
    std::unordered_map<std::string, SystemEvent> events;
    std::unordered_map<std::string, UseCaseItem> use_cases;
    std::unordered_set<std::string> domain_entities;
    std::vector<CrudBinding> crud_bindings;

public:
    void add_event(const SystemEvent& evt) {
        events[evt.id] = evt;
    }

    void add_use_case(const UseCaseItem& uc) {
        use_cases[uc.id] = uc;
    }

    void register_domain_entity(const std::string& entity_name) {
        domain_entities.insert(entity_name);
    }

    void bind_crud_operation(const std::string& entity_name, CrudOp op, const std::string& uc_id) {
        crud_bindings.push_back({entity_name, op, uc_id});
    }

    void audit_system_specification() const {
        std::cout << "\n================================================================================\n";
        std::cout << "         EVENT DECOMPOSITION & CRUD LIFECYCLE COMPLIANCE AUDIT REPORT\n";
        std::cout << "================================================================================\n";

        std::vector<std::string> defects;

        // 1. Audit Event to Use Case Bindings
        std::cout << ">>> EVENT DECOMPOSITION SUMMARY <<<\n";
        std::cout << std::left 
                  << std::setw(12) << "Event ID"
                  << std::setw(18) << "Category"
                  << std::setw(32) << "Triggering Condition"
                  Mapped Use Case\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        for (const auto& [id, evt] : events) {
            std::string cat_str;
            switch (evt.type) {
                case EventType::EXTERNAL_EVENT: cat_str = "EXTERNAL"; break;
                case EventType::TEMPORAL_EVENT: cat_str = "TEMPORAL (Time)"; break;
                case EventType::STATE_EVENT:    cat_str = "STATE (Threshold)"; break;
            }

            std::string uc_info = "UNMAPPED [DEFECT]";
            auto uc_it = use_cases.find(evt.resulting_use_case_id);
            if (uc_it != use_cases.end()) {
                uc_info = uc_it->second.id + " (" + uc_it->second.name + ")";
            } else {
                defects.push_back("[UNMAPPED EVENT] Event '" + id + "' has no valid corresponding Use Case!");
            }

            std::cout << std::left 
                      << std::setw(12) << id
                      << std::setw(18) << cat_str
                      << std::setw(32) << evt.triggering_source.substr(0, 30)
                      << uc_info << "\n";
        }

        // 2. Audit CRUD Matrix Coverage
        std::cout << "\n--------------------------------------------------------------------------------\n";
        std::cout << ">>> DOMAIN ENTITY CRUD LIFECYCLE MATRIX <<<\n";
        std::cout << std::left 
                  << std::setw(22) << "Domain Entity"
                  << std::setw(14) << "Create (C)"
                  << std::setw(14) << "Read (R)"
                  << std::setw(14) << "Update (U)"
                  << std::setw(14) << "Delete (D)"
                  << "Audit Status\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        for (const auto& entity : domain_entities) {
            bool has_c = false, has_r = false, has_u = false, has_d = false;

            for (const auto& b : crud_bindings) {
                if (b.entity_name == entity) {
                    if (b.operation == CrudOp::CREATE) has_c = true;
                    if (b.operation == CrudOp::READ) has_r = true;
                    if (b.operation == CrudOp::UPDATE) has_u = true;
                    if (b.operation == CrudOp::DELETE_ARCHIVE) has_d = true;
                }
            }

            bool complete = (has_c && has_r && has_u && has_d);
            std::string status = complete ? "PASSED [100%]" : "FAILED [INCOMPLETE]";

            if (!has_c) {
                defects.push_back("[PHANTOM ENTITY DEFECT] Entity '" + entity + 
                                  "' has no CREATE use case! Entity cannot be instantiated.");
            }
            if (!has_u) {
                defects.push_back("[IMMUTABLE TRAP DEFECT] Entity '" + entity + 
                                  "' has no UPDATE use case! Data entry errors cannot be amended.");
            }
            if (!has_d) {
                defects.push_back("[RETENTION DEFECT] Entity '" + entity + 
                                  "' has no DELETE/ARCHIVE use case! Violates storage retention rules.");
            }

            std::cout << std::left 
                      << std::setw(22) << entity
                      << std::setw(14) << (has_c ? "COVERED" : "MISSING [!]")
                      << std::setw(14) << (has_r ? "COVERED" : "MISSING [!]")
                      << std::setw(14) << (has_u ? "COVERED" : "MISSING [!]")
                      << std::setw(14) << (has_d ? "COVERED" : "MISSING [!]")
                      << status << "\n";
        }

        std::cout << "\n--------------------------------------------------------------------------------\n";
        std::cout << "Total Events Analyzed    : " << events.size() << "\n";
        std::cout << "Total Use Cases Analyzed : " << use_cases.size() << "\n";
        std::cout << "Total Entities Analyzed  : " << domain_entities.size() << "\n";
        std::cout << "Total Structural Defects : " << defects.size() << "\n";
        std::cout << "================================================================================\n";

        if (defects.empty()) {
            std::cout << ">>> SPECIFICATION AUDIT STATUS: PASSED (100% LIFECYCLE COVERAGE)\n";
        } else {
            std::cout << ">>> SPECIFICATION AUDIT STATUS: FAILED (DEFECTS DETECTED):\n";
            for (const auto& d : defects) {
                std::cout << "  * " << d << "\n";
            }
        }
        std::cout << "================================================================================\n";
    }
};

// ============================================================================
// SIMULATION HARNESS: INTENSIVE CARE HOSPITAL MANAGEMENT PLATFORM
// ============================================================================

int main() {
    EventCrudVerificationEngine engine;

    // 1. Register Domain Entities
    engine.register_domain_entity("Patient");
    engine.register_domain_entity("Prescription");
    engine.register_domain_entity("TelemetryRecord");
    engine.register_domain_entity("BillingInvoice"); // Defective entity with missing C and D

    // 2. Register Use Cases
    engine.add_use_case({"UC-101", "Admit Inpatient", "Triage Nurse"});
    engine.add_use_case({"UC-102", "Query Patient Chart", "Attending Physician"});
    engine.add_use_case({"UC-103", "Update Patient Demographics", "Ward Clerk"});
    engine.add_use_case({"UC-104", "Discharge & Archive Patient", "Chief Medical Officer"});

    engine.add_use_case({"UC-201", "Prescribe Drug Order", "Attending Physician"});
    engine.add_use_case({"UC-202", "View Active Medication Queue", "Pharmacist"});
    engine.add_use_case({"UC-203", "Amend Drug Dosage", "Attending Physician"});
    engine.add_use_case({"UC-204", "Void Defective Prescription", "Pharmacist"});

    engine.add_use_case({"UC-301", "Ingest Sensor Telemetry", "ECG Sensor Hardware"});
    engine.add_use_case({"UC-302", "Render Real-Time Waveform", "ICU Monitor"});
    engine.add_use_case({"UC-303", "Filter Motion Artifact", "Signal DSP"});
    engine.add_use_case({"UC-304", "Purge Aged Telemetry Data", "System Cron"});

    // Billing Invoice has only Read and Update (Missing Create and Delete!)
    engine.add_use_case({"UC-402", "Query Outstanding Balance", "Patient"});
    engine.add_use_case({"UC-403", "Apply Hardship Discount", "Finance Officer"});

    // 3. Register System Events
    // External Event
    engine.add_event({
        "EVT-01", "Patient presents at ER reception with acute symptoms",
        EventType::EXTERNAL_EVENT, "ER Patient Biometric Wristband", "UC-101"
    });

    // Temporal Event
    engine.add_event({
        "EVT-02", "Daily midnight 23:59:59 UTC purge cycle fires",
        EventType::TEMPORAL_EVENT, "Cron: 59 23 * * *", "UC-304"
    });

    // State Event
    engine.add_event({
        "EVT-03", "ECG sensor reports packet loss exceeding 500ms",
        EventType::STATE_EVENT, "PacketLossDuration > 500ms", "UC-303"
    });

    // 4. Bind CRUD Operations
    // Patient: Complete C, R, U, D
    engine.bind_crud_operation("Patient", CrudOp::CREATE, "UC-101");
    engine.bind_crud_operation("Patient", CrudOp::READ, "UC-102");
    engine.bind_crud_operation("Patient", CrudOp::UPDATE, "UC-103");
    engine.bind_crud_operation("Patient", CrudOp::DELETE_ARCHIVE, "UC-104");

    // Prescription: Complete C, R, U, D
    engine.bind_crud_operation("Prescription", CrudOp::CREATE, "UC-201");
    engine.bind_crud_operation("Prescription", CrudOp::READ, "UC-202");
    engine.bind_crud_operation("Prescription", CrudOp::UPDATE, "UC-203");
    engine.bind_crud_operation("Prescription", CrudOp::DELETE_ARCHIVE, "UC-204");

    // TelemetryRecord: Complete C, R, U, D
    engine.bind_crud_operation("TelemetryRecord", CrudOp::CREATE, "UC-301");
    engine.bind_crud_operation("TelemetryRecord", CrudOp::READ, "UC-302");
    engine.bind_crud_operation("TelemetryRecord", CrudOp::UPDATE, "UC-303");
    engine.bind_crud_operation("TelemetryRecord", CrudOp::DELETE_ARCHIVE, "UC-304");

    // BillingInvoice: Flawed! (Only Read and Update)
    engine.bind_crud_operation("BillingInvoice", CrudOp::READ, "UC-402");
    engine.bind_crud_operation("BillingInvoice", CrudOp::UPDATE, "UC-403");

    // Execute Formal Comprehensive Audit
    engine.audit_system_specification();

    return 0;
}
```

</details>

---

### 7. Reference Video Lecture

{{ media:agile-elicitation-video }}

In this video by Simplilearn, collaborative requirements discovery workshops, cross-functional stakeholder refinement sessions, and event-driven backlog synthesis are explored in depth.
