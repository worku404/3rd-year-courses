# Unit 6 — Object-Oriented Structural Modeling, Class & Deployment Architecture
## Lesson 1 — UML Class Diagrams & The Entity-Boundary-Control (BCE) Architecture

### 1. The Class Diagram: The Backbone of Structural Modeling

In the Unified Modeling Language (UML 2.5), the **Class Diagram** is the primary artifact of static structural modeling. It defines the vocabulary of the problem domain, depicting the classes, interfaces, collaborations, attributes, operations, and multi-dimensional relationships that constitute the system's static architecture.

Unlike dynamic behavioral diagrams (such as Sequence or State Machine diagrams) that trace operations across temporal timelines, a Class Diagram represents the **time-invariant schema** of the software.

```
+---------------------------------------------------------------------------------------------------+
|                            THE THREE-COMPARTMENT CLASS ANATOMY                                    |
|                                                                                                   |
|  +-------------------------------------------------------------+                                  |
|  | 1. CLASSIFIER NAME COMPARTMENT:                             |                                  |
|  |    <<Entity>> BankAccount                                   |  * Name in bold centered.        |
|  |    {abstract}                                               |  * Stereotypes in guillemets.    |
|  +-------------------------------------------------------------+                                  |
|  | 2. ATTRIBUTE STATE COMPARTMENT:                             |                                  |
|  |    - account_id: UUID                                       |  * Visibility: - private         |
|  |    - balance: Decimal = 0.00                                |  * Type after colon              |
|  |    # daily_limit: Decimal                                   |  * Optional default value        |
|  +-------------------------------------------------------------+                                  |
|  | 3. BEHAVIORAL OPERATIONS COMPARTMENT:                       |                                  |
|  |    + deposit(amount: Decimal): Result                       |  * Visibility: + public          |
|  |    + withdraw(amount: Decimal): Result                      |  * Parameters with types         |
|  |    + get_balance(): Decimal {query}                         |  * Return type after colon       |
|  +-------------------------------------------------------------+                                  |
+---------------------------------------------------------------------------------------------------+
```

---

### 2. Visibility Modifiers and Multiplicity Semantics

#### 2.1 Visibility Modifiers
UML specifies four standardized access levels that enforce the principle of **Information Hiding**:

| Symbol | Visibility Name | Operational Scope & Accessibility Invariant |
| :---: | :--- | :--- |
| `+` | **Public** | Accessible by any classifier across any package in the entire application. |
| `-` | **Private** | Accessible *strictly and exclusively* by methods declared inside this exact class. |
| `#` | **Protected** | Accessible only by this class and its generalized specialized subclasses. |
| `~` | **Package** | Accessible by any classifier that shares the same enclosing UML package namespace. |

#### 2.2 Multiplicity (Cardinality) Bounds
Multiplicity specifies the exact lower and upper boundaries of object instances that participate in a relationship:

$$\text{Multiplicity Syntax: } [\text{Lower\_Bound} \dots \text{Upper\_Bound}]$$

- `1` (or `1..1`): Exactly one instance mandatory.
- `0..1`: Optional instance (zero or one; represents a nullable foreign key reference).
- `*` (or `0..*`): Zero to many instances (unbounded dynamic array or collection).
- `1..*`: At least one instance mandatory (one or more; cannot be empty).
- `m..n` (e.g., `2..4` or `11`): Precise integer range (e.g., a soccer team has exactly 11 players on the field).

---

### 3. The Boundary-Control-Entity (BCE) Architectural Pattern

In robust software engineering, unstructured class diagrams quickly deteriorate into a tangled web of circular dependencies where UI buttons directly mutate database rows. To prevent this architectural decay, Ivar Jacobson introduced the **Boundary-Control-Entity (BCE)** pattern (standardized in the Unified Process and widely known as the conceptual precursor to Model-View-Controller [MVC]).

{{ media:sam-class-diagram-bce-diagram }}

```
+---------------------------------------------------------------------------------------------------+
|                        THE BOUNDARY-CONTROL-ENTITY (BCE) TOPOLOGY                                 |
|                                                                                                   |
|  [ EXTERNAL ACTOR ]                                                                               |
|       |                                                                                           |
|       v                                                                                           |
|  ( BOUNDARY <<view>> ) <=======> ( CONTROL <<controller>> ) <=======> ( ENTITY <<model>> )        |
|  [ User Interface ]               [ Business Logic Engine ]            [ Persistent Data Store ]  |
+---------------------------------------------------------------------------------------------------+
```

#### 3.1 The Three Stereotypes
1. **Boundary Classes (`<<Boundary>>`):** Intermediaries that mediate between the system and external actors (human users, peripheral hardware, external REST APIs). Examples: `PatientAdmissionForm`, `BarcodeScannerAdapter`, `PaymentGatewayClient`.
2. **Control Classes (`<<Control>>`):** The operational coordinators and business logic orchestrators. They encapsulate transactional workflows, coordinate calculations, enforce domain rules, and sequence operations across entities. Examples: `TriageManager`, `BillingEngine`, `AuthenticationCoordinator`.
3. **Entity Classes (`<<Entity>>`):** The persistent domain data models representing business information. They encapsulate state and fundamental data invariants. Examples: `Patient`, `Prescription`, `MedicalRecord`, `Invoice`.

#### 3.2 The Four Invariant Communication Rules of BCE
To maintain strict architectural decoupling, BCE enforces **four inviolable communication rules**:

```
+---------------------------------------------------------------------------------------------------+
|                        THE FOUR STRICT BCE COMMUNICATION INVARIANTS                               |
+---------------------------------------------------------------------------------------------------+
| RULE 1: ACTOR <---> BOUNDARY ONLY                                                                 |
| External actors can ONLY communicate with Boundary objects. Actors NEVER touch Controllers        |
| or Entities directly. (Prevents external actors from bypassing validation).                       |
|                                                                                                   |
| RULE 2: BOUNDARY <---> CONTROLLER & ACTOR                                                         |
| Boundary objects translate actor events to Controllers, and present Controller outputs to Actors.|
| Boundaries NEVER communicate directly with Entities!                                              |
|                                                                                                   |
| RULE 3: ENTITY <---> CONTROLLER ONLY                                                              |
| Entity objects can ONLY be manipulated by Controllers. Entities NEVER talk to Boundaries          |
| or Actors directly! (Decouples data models completely from UI presentation).                      |
|                                                                                                   |
| RULE 4: CONTROLLER ORCHESTRATION                                                                  |
| Controllers can communicate with Boundaries, Entities, and other Controllers, coordinating       |
| complex cross-entity workflows without UI coupling.                                               |
+---------------------------------------------------------------------------------------------------+
```

---

### 4. Class Diagrams vs. Entity-Relationship Diagrams (ERDs)

Novice analysts often question why software engineering requires Class Diagrams when Entity-Relationship Diagrams (ERDs) already model data tables.

| Dimension | UML Class Diagram | Entity-Relationship Diagram (ERD) |
| :--- | :--- | :--- |
| **Architectural Scope** | **Object-Oriented System Architecture:** Encapsulates both state and executable behavior. | **Relational Database Schema:** Models passive persistent storage structures at rest. |
| **Behavior / Methods** | **First-Class Citizen:** Operations, constructors, polymorphic method overrides, query contracts. | **Non-Existent:** ERDs have zero concept of methods, subroutines, or behavioral algorithms. |
| **Encapsulation** | **Strict Information Hiding:** Attributes are private (`-`); mutated solely via validated public methods. | **Open Exposure:** All table columns are publicly accessible relational attributes. |
| **Polymorphism** | **Supported:** Dynamic late-binding, abstract superclasses, interface contracts (`vtable`). | **Unsupported:** Relational algebra lacks dynamic polymorphic method dispatch. |
| **Relationship Depth** | Association, Aggregation (white diamond), Composition (black diamond), Generalization, Dependency. | Binary/Ternary Relationships, Foreign Keys, Associative Tables. |

---

### 5. Advanced Structural Couplings: Association, Aggregation & Composition

```
+---------------------------------------------------------------------------------------------------+
|                        STRUCTURAL COUPLING COMPARISON TABLE                                       |
+---------------------------------------------------------------------------------------------------+
| RELATIONSHIP   | GRAPHICAL NOTATION   | SEMANTIC COUPLING | CASCADE DESTRUCTION RULE              |
| -------------- | -------------------- | ----------------- | ------------------------------------- |
| 1. ASSOCIATION | Solid directed line  | Peer link         | Independent lifecycles.               |
|                                                                                                   |
| 2. AGGREGATION | White hollow diamond | Shared whole-part | Non-cascade: Deleting whole leaves    |
|    (Shared)    | at Whole end: ◇----- | (Weak ownership)  | constituent parts intact.             |
|                                                                                                   |
| 3. COMPOSITION | Black filled diamond | Exclusive part-of | Mandatory Cascade Destruction: Part   |
|    (Composite) | at Whole end: ◆----- | (Strong ownership)| lives and dies with the parent whole.  |
+---------------------------------------------------------------------------------------------------+
```

---

### 6. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

An architectural review is auditing a proposed Class Diagram for a Cloud Hospital Inpatient Telemetry System. The diagram contains the following structural links:
1. `Link 1: Actor [ On-Duty Nurse ]` connects directly via an association line to `Entity [ PatientMedicalRecord ]`.
2. `Link 2: Boundary [ AdmissionForm ]` connects directly to `Entity [ Patient ]` and calls `set_ssn(ssn)`.
3. `Link 3: Entity [ HospitalDepartment ]` has a black-diamond Composition relationship with `Entity [ Physician ]`.
4. `Link 4: Entity [ Prescription ]` has a white-diamond Aggregation relationship with `Entity [ DrugDosageItem ]`.

**Architectural Audit Tasks:**
1. Identify all BCE communication rule violations in Link 1 and Link 2.
2. Critique Link 3: Explain why black-diamond Composition between a hospital department and a physician is a catastrophic domain modeling defect.
3. Critique Link 4: Evaluate whether a prescription dosage line item can exist if the prescription is deleted.

<details>
<summary>Click to view Level 1 Solution & Architectural Analysis</summary>

##### 1. BCE Violations in Link 1 & Link 2:
- **Link 1 Violates Rule 1 & Rule 3:** The external Actor (`On-Duty Nurse`) is directly linked to an Entity (`PatientMedicalRecord`). External actors can *only* interact with Boundary objects. Entities can *only* be accessed by Controllers. Direct coupling bypasses all authentication, HIPAA access auditing, and business invariant checking.
- **Link 2 Violates Rule 2 & Rule 3:** The Boundary view (`AdmissionForm`) is directly mutating the Entity (`Patient`). A Boundary must pass user inputs to a Controller (e.g., `AdmissionController`), which validates the input parameters, enforces business logic, and mutates the Entity.

##### 2. Critique of Link 3 (Composition on Physician):
- **Catastrophic Composition Defect:** Black-diamond Composition implies **exclusive ownership and cascade destruction**.
  If `HospitalDepartment` has a composition relationship with `Physician`, deleting a department (e.g., closing the "Pediatric Dermatology" wing) would automatically trigger a cascade delete in the database, destroying all records of the employed `Physician`!
  **Correction:** The relationship is **Aggregation** (white diamond) or a standard peer **Association**: physicians have independent legal lifecycles and can be reassigned to other departments.

##### 3. Critique of Link 4 (Aggregation on DrugDosageItem):
- **Incorrect Weak Aggregation:** A `DrugDosageItem` (e.g., "500 mg Amoxicillin, twice daily") has no autonomous meaning or existence outside of the parent `Prescription` that authorized it.
  If the `Prescription` is deleted or voided, the child line item cannot float in isolation.
  **Correction:** Use **Composition** (black diamond) from `Prescription` to `DrugDosageItem`.

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The BCE Architectural Compliance Linter

A software engineering team built an automated AST linter to verify that UML models adhere to the four BCE communication rules. However, the script is allowing Boundaries to talk directly to Entities and crashes when encountering undirected association links.

Examine the flawed script below:

```python
# FLAWED BCE COMPLIANCE LINTER (PYTHON)
def audit_bce_rules(classes, associations):
    violations = []
    
    for assoc in associations:
        src = classes[assoc["source"]]
        dst = classes[assoc["target"]]
        
        # Check: Actor communication
        if src["stereotype"] == "ACTOR" and dst["stereotype"] != "BOUNDARY":
            violations.append(f"Actor {src['name']} illegally talks to {dst['stereotype']}")
            
        # BUG 1: Fails to check bidirectional associations!
        # If assoc is undirected, dst talking to src is also a violation!
        # If dst is ACTOR and src is ENTITY, it slips through completely!
        
        # BUG 2: Completely misses Rule 2 & Rule 3!
        # Does NOT check if BOUNDARY is connected directly to ENTITY!
        
        # BUG 3: Crashes with KeyError if class dictionary has missing stereotypes!
        
    return violations
```

**Debug Assignment:**
1. Identify all security gaps, unchecked BCE invariants, and runtime exception bugs in this script.
2. Implement bidirectional relationship checks handling both directed and undirected associations.
3. Formulate the complete BCE validation matrix that rigorously enforces:
   - Actors $\leftrightarrow$ Boundary ONLY.
   - Boundary $\leftrightarrow$ Controller & Actor ONLY (Never Entity).
   - Entity $\leftrightarrow$ Controller ONLY (Never Boundary or Actor).

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. Identified Flaws:
- **Missing Invariant Coverage:** The script only checked if an Actor was the source, completely ignoring the fact that Boundaries were directly coupled to Entities (the most common violation in amateur MVC codebases).
- **Directional Blindness:** An undirected link represents bidirectional communication. If an association links `PatientForm` (Boundary) and `Patient` (Entity), checking only `source == ACTOR` let the violation pass silently.
- **Missing Stereotype Validation Guards:** Attempting `src["stereotype"]` without a `.get()` fallback crashes if a class lacks an explicit stereotype tag.

##### 2. Corrected Production Implementation:

```python
from typing import Dict, List, Set, Tuple

class ProductionBceLinter:
    VALID_COMMUNICATIONS = {
        ("ACTOR", "BOUNDARY"): True,
        ("BOUNDARY", "ACTOR"): True,
        ("BOUNDARY", "CONTROL"): True,
        ("CONTROL", "BOUNDARY"): True,
        ("CONTROL", "ENTITY"): True,
        ("ENTITY", "CONTROL"): True,
        ("CONTROL", "CONTROL"): True
    }

    def __init__(self, class_registry: Dict[str, Dict]):
        self.classes = class_registry

    def audit_associations(self, associations: List[Dict]) -> List[str]:
        violations = []

        for assoc in associations:
            src_name = assoc["source"]
            dst_name = assoc["target"]
            is_directed = assoc.get("directed", False)

            src_cls = self.classes.get(src_name)
            dst_cls = self.classes.get(dst_name)

            if not src_cls or not dst_cls:
                violations.append(f"[DANGLING LINK] Association '{assoc.get('id')}' references undefined class!")
                continue

            src_st = src_cls.get("stereotype", "UNSTEREOTYPED").upper()
            dst_st = dst_cls.get("stereotype", "UNSTEREOTYPED").upper()

            # 1. Forward Communication Check
            if (src_st, dst_st) not in self.VALID_COMMUNICATIONS:
                violations.append(
                    f"[BCE VIOLATION] Illegal coupling: {src_st} '{src_name}' cannot communicate with {dst_st} '{dst_name}'!"
                )

            # 2. Backward Check (if association is bidirectional / undirected)
            if not is_directed:
                if (dst_st, src_st) not in self.VALID_COMMUNICATIONS:
                    violations.append(
                        f"[BCE VIOLATION] Illegal reverse coupling: {dst_st} '{dst_name}' cannot communicate with {src_st} '{src_name}'!"
                    )

        return violations
```

</details>

---

#### Level 3 — High-Scale System Design: BCE Architecture & Multiplicity Compliance Engine in C++

Design and implement a complete, production-grade C++17 **Boundary-Control-Entity (BCE) Architecture & Multiplicity Compliance Engine**. The system must:
1. Model structural class diagrams using formal AST objects:
   - `ClassNode` (Name, Stereotype: `ACTOR`, `BOUNDARY`, `CONTROL`, `ENTITY`, Attributes, Operations).
   - `AssociationEdge` (Source, Target, MultiplicityLower, MultiplicityUpper, IsDirected).
2. Implement **BCE Communication Rule Auditing**:
   - Enforce the 4 canonical BCE invariants across all directed and bidirectional links.
   - Detect direct Entity-to-Boundary and Entity-to-Actor coupling.
3. Implement **Multiplicity Cardinality Boundary Verification**:
   - Validate that multiplicity expressions are mathematically valid ($\text{Lower} \le \text{Upper}$, $\text{Lower} \ge 0$).
   - Detect impossible multiplicity constraints (e.g., lower bound $> 0$ on self-referential tree roots).
4. Output a comprehensive diagnostic compliance audit report.

<details>
<summary>Click to view complete C++17 BCE Compliance Engine</summary>

```cpp
/**
 * ============================================================================
 * BCE ARCHITECTURE & MULTIPLICITY COMPLIANCE ENGINE (C++17)
 * ============================================================================
 * Implements:
 * 1. Stereotyped Class AST (Boundary, Control, Entity, Actor).
 * 2. Formal BCE 4-Rule Communication Invariant Verifier.
 * 3. Multiplicity Cardinality Bound Consistency Checker.
 * 4. Structural Decoupling Diagnostic Reporter.
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

enum class Stereotype {
    ACTOR,
    BOUNDARY,
    CONTROL,
    ENTITY,
    UNSPECIFIED
};

struct MultiplicityBound {
    int lower = 0;   // e.g. 0, 1
    int upper = -1;  // -1 denotes unbounded '*' (infinity)

    bool is_valid() const {
        if (lower < 0) return false;
        if (upper != -1 && upper < lower) return false;
        return true;
    }

    std::string to_string() const {
        if (upper == -1) {
            return std::to_string(lower) + "..*";
        }
        if (lower == upper) {
            return std::to_string(lower);
        }
        return std::to_string(lower) + ".." + std::to_string(upper);
    }
};

struct BceClassNode {
    std::string id;
    std::string name;
    Stereotype stereotype;
};

struct AssociationLink {
    std::string id;
    std::string source_id;
    std::string target_id;
    MultiplicityBound source_mult;
    MultiplicityBound target_mult;
    bool is_directed = false;
};

// ============================================================================
// BCE COMPLIANCE ENGINE
// ============================================================================

class BceComplianceEngine {
private:
    std::unordered_map<std::string, BceClassNode> classes;
    std::vector<AssociationLink> links;

    bool is_bce_valid_transition(Stereotype src, Stereotype dst) const {
        if (src == Stereotype::ACTOR && dst == Stereotype::BOUNDARY) return true;
        if (src == Stereotype::BOUNDARY && dst == Stereotype::ACTOR) return true;
        if (src == Stereotype::BOUNDARY && dst == Stereotype::CONTROL) return true;
        if (src == Stereotype::CONTROL && dst == Stereotype::BOUNDARY) return true;
        if (src == Stereotype::CONTROL && dst == Stereotype::ENTITY) return true;
        if (src == Stereotype::ENTITY && dst == Stereotype::CONTROL) return true;
        if (src == Stereotype::CONTROL && dst == Stereotype::CONTROL) return true;
        return false;
    }

    std::string stereotype_str(Stereotype st) const {
        switch (st) {
            case Stereotype::ACTOR: return "<<Actor>>";
            case Stereotype::BOUNDARY: return "<<Boundary>>";
            case Stereotype::CONTROL: return "<<Control>>";
            case Stereotype::ENTITY: return "<<Entity>>";
            case Stereotype::UNSPECIFIED: return "<<Unspecified>>";
        }
        return "";
    }

public:
    void add_class(const BceClassNode& cls) {
        classes[cls.id] = cls;
    }

    void add_link(const AssociationLink& link) {
        links.push_back(link);
    }

    void audit_architecture() const {
        std::cout << "\n================================================================================\n";
        std::cout << "        BCE ARCHITECTURAL COMPLIANCE & MULTIPLICITY AUDIT REPORT\n";
        std::cout << "================================================================================\n";

        std::vector<std::string> defects;

        // 1. Audit Multiplicity Integrity
        for (const auto& l : links) {
            if (!l.source_mult.is_valid()) {
                defects.push_back("[INVALID MULTIPLICITY] Link '" + l.id + "' has illegal source bounds: " + 
                                  l.source_mult.to_string());
            }
            if (!l.target_mult.is_valid()) {
                defects.push_back("[INVALID MULTIPLICITY] Link '" + l.id + "' has illegal target bounds: " + 
                                  l.target_mult.to_string());
            }
        }

        // 2. Audit BCE Invariants across all Links
        for (const auto& l : links) {
            auto s_it = classes.find(l.source_id);
            auto t_it = classes.find(l.target_id);

            if (s_it == classes.end() || t_it == classes.end()) {
                defects.push_back("[DANGLING LINK] Link '" + l.id + "' references undefined classifier ID!");
                continue;
            }

            const auto& src = s_it->second;
            const auto& dst = t_it->second;

            // Forward Transition Check
            if (!is_bce_valid_transition(src.stereotype, dst.stereotype)) {
                defects.push_back("[BCE VIOLATION] " + stereotype_str(src.stereotype) + " '" + src.name + 
                                  "' illegally couples to " + stereotype_str(dst.stereotype) + " '" + dst.name + 
                                  "'. Violates strict Layer Decoupling Invariant!");
            }

            // Reverse Transition Check for Undirected Associations
            if (!l.is_directed) {
                if (!is_bce_valid_transition(dst.stereotype, src.stereotype)) {
                    defects.push_back("[BCE VIOLATION] Bidirectional reverse coupling between " + 
                                      stereotype_str(dst.stereotype) + " '" + dst.name + "' and " + 
                                      stereotype_str(src.stereotype) + " '" + src.name + "' is illegal!");
                }
            }
        }

        std::cout << "Total Classifiers Audited : " << classes.size() << "\n";
        std::cout << "Total Associations Audited: " << links.size() << "\n";
        std::cout << "Total Architectural Faults: " << defects.size() << "\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        if (defects.empty()) {
            std::cout << ">>> ARCHITECTURE STATUS: PASSED (100% BCE LAYER ISOLATION COMPLIANT)\n";
        } else {
            std::cout << ">>> ARCHITECTURE STATUS: FAILED (ARCHITECTURAL DEFECTS DETECTED):\n";
            for (const auto& d : defects) {
                std::cout << "  * " << d << "\n";
            }
        }
        std::cout << "================================================================================\n";
    }
};

// ============================================================================
// SIMULATION HARNESS
// ============================================================================

int main() {
    BceComplianceEngine engine;

    // 1. Registered Classifiers
    engine.add_class({"ACT-NURSE", "TriageNurse", Stereotype::ACTOR});
    engine.add_class({"BND-FORM", "InpatientAdmissionForm", Stereotype::BOUNDARY});
    engine.add_class({"CTL-MGR", "AdmissionWorkflowCoordinator", Stereotype::CONTROL});
    engine.add_class({"ENT-PATIENT", "Patient", Stereotype::ENTITY});

    // Classifiers for Testing Violations
    engine.add_class({"BND-KIOSK", "BedsideKioskView", Stereotype::BOUNDARY});
    engine.add_class({"ENT-LEDGER", "FinancialLedger", Stereotype::ENTITY});

    // 2. Valid BCE Chain: Actor -> Boundary -> Control -> Entity
    // Nurse talks to AdmissionForm
    engine.add_link({"L1", "ACT-NURSE", "BND-FORM", {1, 1}, {0, -1}, true});
    // AdmissionForm talks to AdmissionWorkflowCoordinator
    engine.add_link({"L2", "BND-FORM", "CTL-MGR", {1, 1}, {1, 1}, true});
    // AdmissionWorkflowCoordinator talks to Patient
    engine.add_link({"L3", "CTL-MGR", "ENT-PATIENT", {1, 1}, {1, 1}, true});

    // 3. Defective Links for Testing the Engine
    // Defect A: Boundary directly talking to Entity! (Bypasses Controller)
    engine.add_link({"L4_Defect", "BND-KIOSK", "ENT-PATIENT", {1, 1}, {1, 1}, true});

    // Defect B: Actor directly talking to Entity! (Fatal security breach)
    engine.add_link({"L5_Defect", "ACT-NURSE", "ENT-LEDGER", {1, 1}, {0, -1}, true});

    // Defect C: Invalid Multiplicity Bound (Lower bound 5 > Upper bound 2)
    engine.add_link({"L6_Defect", "CTL-MGR", "ENT-LEDGER", {5, 2}, {1, 1}, true});

    // Run Full Architectural Verification
    engine.audit_architecture();

    return 0;
}
```

</details>

---

### 7. Reference Video Lecture

{{ media:class-diagram-video }}

In this video by Telusko, the principles of Class and Object modeling, encapsulation, constructors, and structural associations are explored across enterprise object-oriented architectures.
