# Unit 5 — Object-Oriented Analysis, UML 2.5 Metamodel & Use Case Engineering
## Lesson 2 — Use Case Modeling, System Boundary Specification & Advanced Stereotypes

### 1. The Use Case Paradigm: Scoping Functional Dialogue

In software engineering, a **Use Case** is a formalized, scenario-based modeling technique that captures the dynamic functional dialogue between an external actor and the software system to achieve a discrete, measurable goal of value.

Pioneered by Ivar Jacobson in 1987 and standardized within the UML specification by the Object Management Group (OMG), use cases serve as the foundational bridge connecting ambiguous stakeholder desires to concrete engineering architectures.

```
+---------------------------------------------------------------------------------------------------+
|                            THE USE CASE DIALOGUE MODEL                                            |
|                                                                                                   |
|  [ EXTERNAL ACTOR ]                  SYSTEM BOUNDARY                     [ SYSTEM PLATFORM ]      |
|  (User, Device, API)   ============================================      (Internal Services)      |
|           |                                                                       |               |
|           | 1. Stimulus: Ingests command & payload                                |               |
|           |---------------------------------------------------------------------->|               |
|           |                                                                       |               |
|           |                                 2. Internal Invariant State Transform |               |
|           |                                    (Validates rules, commits to DB)   |               |
|           |                                                                       |               |
|           | 3. Response: Emits confirmed value / artifact                         |               |
|           |<----------------------------------------------------------------------|               |
|           |                                                                                       |
+---------------------------------------------------------------------------------------------------+
```

#### 1.1 The Golden Rule of Use Cases: Focus on "What", Never "How"
A use case must specify **what value** the system delivers to the actor, strictly abstracting away internal design details:
- **Flawed (Prescriptive "How"):** *"The user clicks the blue submit button on screen 4, the JavaScript frontend serializes the JSON to an Express.js router, which executes an SQL `INSERT` statement into PostgreSQL."*
- **Production-Grade (Behavioral "What"):** *"The Inpatient Nurse submits an emergency medication request; the system validates the physician's license signature, checks for patient allergy contraindications, and reserves the medication in the pharmacy inventory."*

---

### 2. Actor Taxonomies: Primary vs. Secondary Supporting Entities

An **Actor** represents a coherent set of roles that external users or systems play when interfacing with the platform. Actors reside **strictly outside the system boundary**.

```
+---------------------------------------------------------------------------------------------------+
|                                  THE THREE TYPES OF ACTORS                                        |
+---------------------------------------------------------------------------------------------------+
| 1. HUMAN USERS           : Clinical Nurses, Radiologists, System Administrators, Compliance Officers|
| 2. PERIPHERAL HARDWARE   : Barcode Scanners, Automated Pill Dispensers, RFID Sensor Gates, ECG Hub|
| 3. EXTERNAL SUBSYSTEMS   : Stripe Payment Gateway, National Prescription Database, Twilio SMS API|
+---------------------------------------------------------------------------------------------------+
```

{{ media:sam-use-case-boundary-diagram }}

#### 2.1 Primary vs. Secondary Actors
- **Primary Actor ("Who knocks?"):** Initiates the use case to achieve a personal or business goal (e.g., `Patient` initiates *"Schedule Appointment"*).
- **Secondary Supporting Actor:** Invoked by the system to assist in fulfilling the primary actor's goal (e.g., `Stripe Gateway` is called by the system to process the payment during *"Checkout Cart"*). Secondary actors never initiate the primary use case.

---

### 3. Formal Cockburn Use Case Specification Anatomy

While UML Use Case Diagrams provide a high-level visual index, the true engineering specification is authored in structured prose. The industry standard format was formulated by Dr. Alistair Cockburn:

```
====================================================================================================
               FORMAL COCKBURN USE CASE SPECIFICATION (CANONICAL TEMPLATE)
====================================================================================================
USE CASE ID             : UC-CLINIC-042
USE CASE NAME           : Dispense Emergency Inpatient Medication
PRIMARY ACTOR           : On-Duty Triage Nurse
SCOPE                   : Hospital Inpatient Management System (HIMS)
LEVEL                   : User Goal Level (Sea Level)
STAKEHOLDERS & INTERESTS: 
  * Patient: Demands rapid, safe medication delivery with zero adverse drug interactions.
  * Pharmacy Director: Demands strict inventory ledger balance and DEA compliance auditing.
  * Hospital Legal: Demands immutable cryptographic audit logging of all narcotic dispensing.

PRECONDITIONS           :
  1. Nurse is authenticated with biometric SmartCard and active clinical session.
  2. Patient has an active inpatient bed assignment in the HIMS database.
  3. Medication order has status 'AUTHORIZED' by an attending physician.

MINIMAL GUARANTEES (Rollback):
  * If dispensing fails, inventory counts remain unchanged; failure event logged with error code.

SUCCESS GUARANTEES (Postconditions):
  * Medication status transitioned to 'DISPENSED'.
  * Pharmacy automated vault releases physical drug vial.
  * Patient electronic health record (EHR) reflects dosage and administration timestamp.

MAIN SUCCESS SCENARIO (Sunny-Day Path):
  1. Nurse scans patient biometric wristband using mobile bedside barcode terminal.
  2. System retrieves patient active authorized medication queue.
  3. Nurse selects authorized drug order and confirms physical medication unit barcode.
  4. System verifies dosage match and queries Interaction_Engine for acute contraindications.
  5. System triggers automated dispensing vault actuator (Secondary Actor: Hardware Dispenser).
  6. System commits transaction, updates inventory balance, and appends audit ledger entry.
  7. System displays green confirmation banner on nurse terminal.

EXTENSIONS (Alternative / Rainy-Day Paths):
  4a. Drug-Drug Interaction Detected:
      4a1. System flashes critical red alert banner with contraindication severity score.
      4a2. System locks dispensing actuator.
      4a3. Nurse overrides only upon entering secondary Attending Physician authorization PIN.
  5a. Vault Actuator Mechanical Jam:
      5a1. Dispenser hardware reports error code `ERR_JAM_ACTUATOR`.
      5a2. System executes atomic transaction rollback; reverses status to 'PENDING_PHYSICAL'.
      5a3. System dispatches urgent maintenance ticket to on-call biomedical engineering staff.
====================================================================================================
```

---

### 4. Stereotype Semantics: `<<include>>` vs. `<<extend>>`

Novice software engineers frequently confuse the direction and semantics of UML use case relationships. In UML 2.5, **`<<include>>`** and **`<<extend>>`** represent two completely distinct dependency concepts:

```
+---------------------------------------------------------------------------------------------------+
|                        <<include>> VS. <<extend>> ARCHITECTURAL COMPARISON                        |
+---------------------------------------------------------------------------------------------------+
| DIMENSION               | <<include>> (Mandatory Subroutine) | <<extend>> (Optional / Conditional)|
| ----------------------- | ---------------------------------- | ---------------------------------- |
| Execution Invariant     | **Always:** Executes every single  | **Conditional:** Executes only if  |
|                         | time the base use case runs.       | an extension point predicate is met|
| Arrow Direction         | **BASE ---> INCLUDED**             | **EXTENSION ---> BASE**            |
| Base Use Case Awareness | Base *knows* about the included    | Base is *completely unaware* of    |
|                         | subroutine explicitly.             | the extension; stays unmodified!   |
| Primary Purpose         | Factor out common duplicate logic  | Add optional, exceptional, or      |
|                         | across multiple use cases (DRY).   | plug-in behaviors non-invasively.  |
| Concrete Example        | 'Place Order' <<include>>          | 'Process Return' <<extend>>        |
|                         | 'Authenticate User'.               | 'Issue Cash Refund' (if receipt).  |
+---------------------------------------------------------------------------------------------------+
```

#### 4.1 The Arrow Direction Rule (Mnemonic)
- **`<<include>>` (Base $\longrightarrow$ Included):** The Base use case *requires* the included sub-case. Think: *"Base points to what it needs."*
- **`<<extend>>` (Extension $\longrightarrow$ Base):** The Extension use case points back to the base case it hooks into. Think: *"The extension hooks into the base at an Extension Point."*

---

### 5. Common Use Case Modeling Anti-Patterns

```
+---------------------------------------------------------------------------------------------------+
|                              FATAL USE CASE MODELING ANTI-PATTERNS                                |
+---------------------------------------------------------------------------------------------------+
| ANTI-PATTERN                  | DESCRIPTION & VIOLATION             | ARCHITECTURAL REFACTORING   |
| ----------------------------- | ----------------------------------- | --------------------------- |
| 1. Functional Decomposition   | Breaking a use case into microscopic| Collapse into a single goal-|
|    ("CRUD Micro-Cases")       | UI buttons: 'Enter Username',       | level use case:              |
|                               | 'Click Login', 'Display Error'.     | 'Authenticate User'.        |
|                               |                                     |                             |
| 2. Inverted Arrow Directions  | Drawing <<extend>> arrows from base | Strictly enforce:           |
|                               | to extension, or <<include>> backwards.| Base -> <<include>> -> Child|
|                               |                                     | Ext -> <<extend>> -> Base.  |
|                               |                                     |                             |
| 3. Internal System Actor      | Modeling internal hardware/services | External actors only; remove|
|                               | (e.g. CPU, MySQL, CronDaemon) as    | database and background     |
|                               | external stick-figure actors.       | threads from outside boundary|
|                               |                                     |                             |
| 4. Infinite Include Cycles    | UC-A <<include>> UC-B, and          | Factor shared logic into a  |
|                               | UC-B <<include>> UC-A.              | separate atomic third case. |
+---------------------------------------------------------------------------------------------------+
```

---

### 6. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

An architectural audit is reviewing a proposed Use Case Diagram for an Online Banking Web Portal. The diagram depicts:
1. An external stick figure labeled `MySQL_Database` initiating a use case called *"Store Password Hash"*.
2. A use case called *"Transfer Funds"* connected via a dashed arrow labeled `<<extend>>` pointing toward a use case called *"Verify Insufficient Funds Alert"*.
3. A use case called *"Login to Portal"* decomposed into four separate use cases connected with `<<include>>`:
   - *"Enter Username"*
   - *"Enter Password"*
   - *"Validate Captcha"*
   - *"Redirect to Dashboard"*

**Architectural Audit Tasks:**
1. Identify all four structural and semantic anti-patterns in this diagram.
2. Explain why `MySQL_Database` is not an external actor.
3. Correct the arrow direction and stereotype between *"Transfer Funds"* and *"Verify Insufficient Funds Alert"*.
4. Refactor the four microscopic login use cases into an authentic user-goal specification.

<details>
<summary>Click to view Level 1 Solution & Architectural Audit</summary>

##### 1. Identified Anti-Patterns:
- **Internal Component Modeled as Actor:** `MySQL_Database` is an internal persistent storage component residing *inside* the system boundary, not an external autonomous actor.
- **Inverted / Misused `<<extend>>` Relationship:** The arrow was drawn from base *"Transfer Funds"* to the extension. In UML, `<<extend>>` must point from the extension case *back* to the base. Furthermore, handling insufficient funds is an alternate flow/extension of the transfer, triggered only when `balance < amount`.
- **Functional Decomposition Anti-Pattern:** Treating individual keyboard inputs (*"Enter Username"*, *"Enter Password"*) as separate use cases. Use cases must represent complete user goals of measurable value, not individual GUI keystrokes or UI button clicks.

##### 2. Corrected Architectural Topology:
1. **Remove `MySQL_Database` Actor:** Data persistence is an internal system responsibility executed inside the postconditions of use cases.
2. **Refactor Login Flow:** Consolidate the four micro-cases into a single goal-level use case: **"Authenticate User"**. The capture of username, password, and Captcha are documented internally within Cockburn Main Success Scenario steps 1–3.
3. **Correct Stereotype Relationship:**
   - Base Use Case: **"Transfer Funds"**
   - Extension Use Case: **"Handle Insufficient Funds Exception"**
   - Dependency Arrow: `[ Handle Insufficient Funds Exception ] ---<<extend>>---> [ Transfer Funds ]` with Extension Point: `Point: Overdraft_Triggered (Condition: Account_Balance < Transfer_Amount)`.

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The Mutually Recursive Include Cycle Crash

An enterprise UML parser imports use case relationships from XMI/JSON model files to compute total test execution paths. However, when an analyst improperly connected two use cases with bidirectional `<<include>>` stereotypes (e.g., `UC-A` includes `UC-B`, and `UC-B` includes `UC-A`), the test generator crashed with an infinite recursion loop.

Examine the flawed Python analyzer below:

```python
# FLAWED USE CASE GRAPH ANALYZER (PYTHON)
def get_all_mandatory_subroutines(use_case_id, include_graph):
    # BUG 1: Zero cycle detection / recursion guards!
    # If A includes B and B includes A, this function recurses indefinitely!
    subroutines = []
    direct_includes = include_graph.get(use_case_id, [])
    
    for inc in direct_includes:
        subroutines.append(inc)
        # BUG: Blind recursive call without call stack tracking
        subroutines.extend(get_all_mandatory_subroutines(inc, include_graph))
        
    return subroutines

def validate_use_case_actors(use_cases, actors):
    # BUG 2: Fails to verify that every use case has at least ONE primary actor!
    # Allows orphan use cases that no user can trigger!
    pass
```

**Debug Assignment:**
1. Explain why circular `<<include>>` relationships are an architectural impossibility in UML 2.5 (a mandatory subroutine cannot require its own caller synchronously).
2. Refactor the implementation using iterative topological sorting or depth-first cycle detection with an active recursion stack.
3. Add a validation rule that flags **Orphan Use Cases** (use cases that lack any initiating Primary Actor).

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. The Impossibility of Cyclic Includes:
Under UML 2.5 semantics, $A \xrightarrow{\mathtt{<<include>>}} B$ mandates that whenever $A$ executes, $B$ *must* execute as part of $A$'s synchronous sequence.
If $B \xrightarrow{\mathtt{<<include>>}} A$, then $B$ mandates that $A$ must execute.
This produces an infinite operational regress: $A \to B \to A \to B \dots$, meaning neither use case can ever terminate or satisfy its postconditions. Cyclic inclusion is a fatal architectural defect.

##### 2. Corrected Production Implementation:

```python
from typing import Dict, List, Set, Optional

class CyclicIncludeException(Exception):
    pass

class ProductionUseCaseValidator:
    def __init__(
        self,
        use_cases: Set[str],
        actor_associations: Dict[str, Set[str]], # Actor -> Set of UC IDs
        include_graph: Dict[str, Set[str]]       # Base UC -> Set of Included UC IDs
    ):
        self.use_cases = use_cases
        self.actor_associations = actor_associations
        self.include_graph = include_graph

    def detect_include_cycles(self) -> List[str]:
        # 0: White (Unvisited), 1: Gray (Active in stack), 2: Black (Visited)
        colors = {uc: 0 for uc in self.use_cases}
        cycles_found = []

        def dfs(curr: str, path: List[str]):
            colors[curr] = 1 # Gray
            path.append(curr)

            for target in self.include_graph.get(curr, set()):
                if colors.get(target) == 1:
                    cycle_idx = path.index(target)
                    cycle_str = " -> ".join(path[cycle_idx:] + [target])
                    cycles_found.append(f"[FATAL CYCLIC INCLUDE] {cycle_str}")
                elif colors.get(target) == 0:
                    dfs(target, path)

            path.pop()
            colors[curr] = 2 # Black

        for uc in self.use_cases:
            if colors[uc] == 0:
                dfs(uc, [])

        return cycles_found

    def find_orphan_use_cases(self) -> Set[str]:
        # Identify use cases with NO direct primary actor,
        # AND which are NOT included by any valid parent use case!
        all_triggered_cases = set()
        for ucs in self.actor_associations.values():
            all_triggered_cases.update(ucs)

        # Cases that are targets of <<include>> or <<extend>>
        included_cases = set()
        for targets in self.include_graph.values():
            included_cases.update(targets)

        # An orphan is not triggered by an actor AND not included by another case
        orphans = set()
        for uc in self.use_cases:
            if uc not in all_triggered_cases and uc not in included_cases:
                orphans.add(uc)

        return orphans
```

</details>

---

#### Level 3 — High-Scale System Design: Use Case Graph Dependency & Stereotype Verifier in C++

Design and implement a complete, production-grade C++17 **Use Case Graph Dependency & Stereotype Verifier**. The engine must:
1. Model a formal Use Case Diagram as a **Directed Attributed Hypergraph**:
   - Classifiers: `Actor` (Primary vs. Secondary, Type: Human/Hardware/System), `UseCase` (Goal level, Cockburn attributes), `SystemBoundary`.
   - Relationships: `COMMUNICATION_LINK` (Actor $\leftrightarrow$ UC), `INCLUDE_RELATION` (Base $\to$ Included), `EXTEND_RELATION` (Extension $\to$ Base with Extension Point), `GENERALIZATION` (Child $\to$ Parent).
2. Implement **Topological Verification Algorithms**:
   - Detect **Cyclic Include Dependencies** using three-color DFS.
   - Detect **Orphan Use Cases** (cases lacking primary actors and unreferenced by any valid include/extend links).
   - Detect **Inverted Stereotype Arrows** (validating that `<<extend>>` arrows hook into a base case with an explicit extension point).
   - Detect **Actor Boundary Leakage** (validating that actors reside strictly outside system boundaries).
3. Output a comprehensive diagnostic compliance audit report.

<details>
<summary>Click to view complete C++17 Use Case Graph Verifier</summary>

```cpp
/**
 * ============================================================================
 * USE CASE GRAPH DEPENDENCY & STEREOTYPE VERIFIER (C++17)
 * ============================================================================
 * Implements:
 * 1. Attributed Hypergraph of Use Cases, Actors, and System Boundaries.
 * 2. Three-Color DFS Detection for <<include>> Cycles.
 * 3. Orphan Use Case & Unreachable Goal Linter.
 * 4. Stereotype Semantics & Extension-Point Invariant Enforcer.
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
// METAMODEL DATA STRUCTURES
// ============================================================================

enum class ActorCategory {
    PRIMARY,
    SECONDARY
};

enum class ActorKind {
    HUMAN_USER,
    HARDWARE_PERIPHERAL,
    EXTERNAL_SUBSYSTEM
};

struct ActorNode {
    std::string id;
    std::string name;
    ActorCategory category;
    ActorKind kind;
    bool inside_system_boundary = false; // INVARIANT: Must be false!
};

struct UseCaseNode {
    std::string id;
    std::string name;
    std::string goal_description;
    std::vector<std::string> extension_points; // Declared hook points for <<extend>>
};

enum class UseCaseRelKind {
    COMMUNICATION, // Actor <-> UC
    INCLUDE,       // Base -> Included
    EXTEND,        // Extension -> Base
    GENERALIZATION // Child -> Parent
};

struct UseCaseRelation {
    std::string id;
    std::string source_id;
    std::string target_id;
    UseCaseRelKind kind;
    std::string target_extension_point; // Mandatory if kind == EXTEND
};

// ============================================================================
// USE CASE VERIFIER ENGINE
// ============================================================================

class UseCaseVerifierEngine {
private:
    std::unordered_map<std::string, ActorNode> actors;
    std::unordered_map<std::string, UseCaseNode> use_cases;
    std::vector<UseCaseRelation> relations;

    enum class DfsColor { WHITE, GRAY, BLACK };

    bool check_include_cycles_dfs(
        const std::string& curr,
        std::unordered_map<std::string, DfsColor>& colors,
        std::vector<std::string>& path,
        std::vector<std::string>& detected_cycles
    ) const {
        colors[curr] = DfsColor::GRAY;
        path.push_back(curr);

        // Find all outgoing <<include>> targets
        for (const auto& rel : relations) {
            if (rel.kind == UseCaseRelKind::INCLUDE && rel.source_id == curr) {
                const std::string& target = rel.target_id;
                if (colors.find(target) == colors.end()) continue;

                if (colors[target] == DfsColor::GRAY) {
                    std::string c_str = "";
                    auto it = std::find(path.begin(), path.end(), target);
                    while (it != path.end()) {
                        c_str += *it + " -> ";
                        it++;
                    }
                    c_str += target;
                    detected_cycles.push_back(c_str);
                    return true;
                }

                if (colors[target] == DfsColor::WHITE) {
                    check_include_cycles_dfs(target, colors, path, detected_cycles);
                }
            }
        }

        colors[curr] = DfsColor::BLACK;
        path.pop_back();
        return false;
    }

public:
    void add_actor(const ActorNode& actor) {
        actors[actor.id] = actor;
    }

    void add_use_case(const UseCaseNode& uc) {
        use_cases[uc.id] = uc;
    }

    void add_relation(const UseCaseRelation& rel) {
        relations.push_back(rel);
    }

    void audit_use_case_model() const {
        std::cout << "\n================================================================================\n";
        std::cout << "                 USE CASE MODELING ARCHITECTURAL AUDIT REPORT\n";
        std::cout << "================================================================================\n";

        std::vector<std::string> defects;

        // 1. Boundary Violation Check: Actors cannot reside inside the boundary
        for (const auto& [id, actor] : actors) {
            if (actor.inside_system_boundary) {
                defects.push_back("[BOUNDARY LEAK] Actor '" + id + "' (" + actor.name + 
                                  ") is declared INSIDE the system boundary. All actors must be external!");
            }
        }

        // 2. Cyclic <<include>> Detection
        std::unordered_map<std::string, DfsColor> colors;
        for (const auto& [id, _] : use_cases) colors[id] = DfsColor::WHITE;

        std::vector<std::string> include_cycles;
        for (const auto& [id, _] : use_cases) {
            if (colors[id] == DfsColor::WHITE) {
                std::vector<std::string> path;
                check_include_cycles_dfs(id, colors, path, include_cycles);
            }
        }
        for (const auto& c : include_cycles) {
            defects.push_back("[FATAL CYCLIC INCLUDE] " + c);
        }

        // 3. <<extend>> Extension Point Invariant
        // Extension points must exist in the target Base use case!
        for (const auto& rel : relations) {
            if (rel.kind == UseCaseRelKind::EXTEND) {
                auto base_it = use_cases.find(rel.target_id);
                if (base_it == use_cases.end()) {
                    defects.push_back("[DANGLING EXTEND] Extension '" + rel.source_id + "' points to missing Base '" + rel.target_id + "'");
                    continue;
                }

                if (rel.target_extension_point.empty()) {
                    defects.push_back("[MISSING EXTENSION POINT] <<extend>> relation '" + rel.id + 
                                      "' lacks an explicit extension point hook!");
                } else {
                    const auto& pts = base_it->second.extension_points;
                    if (std::find(pts.begin(), pts.end(), rel.target_extension_point) == pts.end()) {
                        defects.push_back("[INVALID EXTENSION POINT] Extension point '" + rel.target_extension_point + 
                                          "' does not exist in Base Use Case '" + rel.target_id + "'!");
                    }
                }
            }
        }

        // 4. Orphan Use Cases
        // Every use case must be either triggered by an Actor or included/extended by another case
        std::unordered_set<std::string> triggered_cases;
        std::unordered_set<std::string> referenced_targets;

        for (const auto& rel : relations) {
            if (rel.kind == UseCaseRelKind::COMMUNICATION) {
                // If source is actor, target is use case
                if (actors.find(rel.source_id) != actors.end()) {
                    triggered_cases.insert(rel.target_id);
                }
            }
            if (rel.kind == UseCaseRelKind::INCLUDE || rel.kind == UseCaseRelKind::EXTEND) {
                referenced_targets.insert(rel.target_id);
            }
        }

        for (const auto& [id, uc] : use_cases) {
            bool is_triggered = (triggered_cases.find(id) != triggered_cases.end());
            bool is_referenced = (referenced_targets.find(id) != referenced_targets.end());

            // A root use case must be triggered by an actor
            // A sub-case can be referenced via include
            if (!is_triggered && !is_referenced) {
                defects.push_back("[ORPHAN USE CASE] Use Case '" + id + "' (" + uc.name + 
                                  ") is completely unlinked! No Actor triggers it and no case includes it.");
            }
        }

        // Diagnostic summary
        std::cout << "Total Actors Audited    : " << actors.size() << "\n";
        std::cout << "Total Use Cases Audited : " << use_cases.size() << "\n";
        std::cout << "Total Relations Audited : " << relations.size() << "\n";
        std::cout << "Total Structural Defects: " << defects.size() << "\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        if (defects.empty()) {
            std::cout << ">>> USE CASE MODEL STATUS: PASSED (100% SPECIFICATION INTEGRITY)\n";
        } else {
            std::cout << ">>> USE CASE MODEL STATUS: FAILED (DEFECTS FOUND):\n";
            for (const auto& d : defects) {
                std::cout << "  * " << d << "\n";
            }
        }
        std::cout << "================================================================================\n";
    }
};

// ============================================================================
// SIMULATION HARNESS: CLINICAL TELEMETRY USE CASE MODEL
// ============================================================================

int main() {
    UseCaseVerifierEngine engine;

    // 1. External Actors
    engine.add_actor({"ACT-NURSE", "ICU Triage Nurse", ActorCategory::PRIMARY, ActorKind::HUMAN_USER, false});
    engine.add_actor({"ACT-STRIPE", "Payment Gateway API", ActorCategory::SECONDARY, ActorKind::EXTERNAL_SUBSYSTEM, false});

    // Actor with Boundary Violation (Inside boundary!)
    engine.add_actor({"ACT-MYSQL", "Internal Database Daemon", ActorCategory::SECONDARY, ActorKind::EXTERNAL_SUBSYSTEM, true});

    // 2. Valid Use Cases
    engine.add_use_case({
        "UC-DISPENSE",
        "Dispense Inpatient Medication",
        "Nurse dispenses medication vial",
        {"Emergency_Overdraft", "Allergy_Alert"} // Extension Points
    });

    engine.add_use_case({
        "UC-AUTH",
        "Authenticate Clinical Session",
        "Verify biometric nurse SmartCard",
        {}
    });

    engine.add_use_case({
        "UC-EMERGENCY-OVERRIDE",
        "Execute Emergency Attending Override",
        "Override physician authorization",
        {}
    });

    // 3. Cyclic Include Use Cases for Testing the Verifier
    engine.add_use_case({"UC-CYCLE-A", "Subroutine A", "Cyclic test", {}});
    engine.add_use_case({"UC-CYCLE-B", "Subroutine B", "Cyclic test", {}});

    // 4. Orphan Use Case (No actor, no include)
    engine.add_use_case({"UC-ORPHAN-99", "Play Video Game Easter Egg", "Developer prank", {}});

    // 5. Connect Relationships
    // Actor -> Use Case
    engine.add_relation({"R1", "ACT-NURSE", "UC-DISPENSE", UseCaseRelKind::COMMUNICATION, ""});

    // Base -> <<include>> -> Subroutine
    engine.add_relation({"R2", "UC-DISPENSE", "UC-AUTH", UseCaseRelKind::INCLUDE, ""});

    // Valid <<extend>>: Extension -> Base with valid extension point
    engine.add_relation({"R3", "UC-EMERGENCY-OVERRIDE", "UC-DISPENSE", UseCaseRelKind::EXTEND, "Emergency_Overdraft"});

    // Defect A: Cyclic Include (A -> B, B -> A)
    engine.add_relation({"R4", "UC-CYCLE-A", "UC-CYCLE-B", UseCaseRelKind::INCLUDE, ""});
    engine.add_relation({"R5", "UC-CYCLE-B", "UC-CYCLE-A", UseCaseRelKind::INCLUDE, ""}); // Cycle!

    // Defect B: Invalid Extension Point
    engine.add_relation({"R6", "UC-AUTH", "UC-DISPENSE", UseCaseRelKind::EXTEND, "NonExistentHookPoint"});

    // Run Full Architectural Model Audit
    engine.audit_use_case_model();

    return 0;
}
```

</details>

---

### 7. Reference Video Lecture

{{ media:system-design-usecase-video }}

In this video by freeCodeCamp, high-scale system design and functional use case scoping are explored, showing how actor boundaries, operational requirements, and domain interfaces are systematically architected.
