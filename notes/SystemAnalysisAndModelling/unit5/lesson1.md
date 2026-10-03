# Unit 5 — Object-Oriented Analysis, UML 2.5 Metamodel & Use Case Engineering
## Lesson 1 — Object-Oriented Paradigms & UML 2.5 Metamodel Architecture

### 1. The Object-Oriented Paradigm: Unifying State and Behavior

In classical Structured Analysis, software architectures enforced a strict, artificial dichotomy between **Data** (passive records stored in data dictionaries and relational tables) and **Processes** (active subroutines that manipulated those records). While effective for batch accounting pipelines, this separation breaks down under modern, highly concurrent, distributed enterprise software. When a shared data structure changes, ripple-effect bugs cascade across hundreds of independent subroutines.

**Object-Oriented Analysis (OOA)** reorganizes software architecture around real-world problem domain entities called **Objects**. An object is a discrete, autonomous computational entity that seamlessly encapsulates both **State** (attributes and instance variables) and **Behavior** (methods, operations, and state machine transitions).

```
+---------------------------------------------------------------------------------------------------+
|                        STRUCTURED PARADIGM VS. OBJECT-ORIENTED PARADIGM                           |
|                                                                                                   |
|  [ STRUCTURED ANALYSIS: SEPARATION OF CONCERNS ]                                                  |
|  +---------------------------+         +-------------------------------+                          |
|  | PASSIVE DATA STORE:       | <-----> | DISPARATE MUTATING FUNCTIONS: |                          |
|  | { id, balance, status }   |         | deduct_balance(), audit_txn(),|                          |
|  +---------------------------+         | freeze_account(), transfer()  |                          |
|  (Data structure changes break all functions!)                                                    |
|                                                                                                   |
|  [ OBJECT-ORIENTED ANALYSIS: UNIFIED ENCAPSULATED ENTITY ]                                        |
|  +-------------------------------------------------------------+                                  |
|  | CLASS: BankAccount                                          |                                  |
|  | * Private State    : - balance: Decimal, - status: AccountStatus                              |
|  | * Public Contract  : + deposit(amount), + withdraw(amount)  |                                  |
|  |                      + freeze(reason), + get_audit_trail()  |                                  |
|  +-------------------------------------------------------------+                                  |
|  (State is inaccessible from the outside except through validated method invocations!)             |
+---------------------------------------------------------------------------------------------------+
```

---

### 2. The Core Pillars of Object-Oriented Architecture

To build robust, maintainable domain models, systems analysts apply **four foundational pillars**:

{{ media:sam-uml-metamodel-diagram }}

#### 2.1 Encapsulation and Information Hiding
Encapsulation binds internal data representations and concrete algorithmic logic inside an isolated boundary. Under **Information Hiding** (pioneered by David Parnas), the internal layout of an object is completely hidden from external clients.
- **Access Modifiers / Visibility Notation in UML:**
  - `+` **Public:** Accessible by any client entity in the system.
  - `-` **Private:** Accessible *only* by operations declared within this immediate class.
  - `#` **Protected:** Accessible only by this class and its generalized subclasses.
  - `~` **Package:** Accessible by any classifier residing within the same UML package namespace.

#### 2.2 Abstraction
Abstraction is the intellectual discipline of isolating the **essential, invariant characteristics** of an entity while filtering out ephemeral implementation noise. In analysis modeling, abstraction answers *"what does the entity guarantee to the domain?"* before architects decide *"how is it coded in a runtime framework?"*.

#### 2.3 Generalization, Specialization, and Inheritance
- **Generalization:** Extracting shared attributes and behaviors from multiple specific classes into a generalized superclass (an *"is-a-kind-of"* relationship).
- **Specialization:** The inverse process: creating refined subclasses that extend the capabilities of the superclass.
- **Inheritance:** The structural language mechanism enabling a subclass to inherit the state schema and operational signatures of its parent class, while providing specialized method overrides.

#### 2.4 Polymorphism and Dynamic Late Binding
Polymorphism (Greek: *"many forms"*) allows a single abstract message to trigger different behaviors depending on the concrete runtime type of the receiver:

$$\forall x \in \text{Vehicles}, \quad x.\mathtt{calculate\_toll}() \implies \begin{cases}
\text{Automobile}: & \text{flat fee of } \$5.00 \\
\text{FreightTruck}: & \$5.00 + (\$2.50 \times \text{axles}) \\
\text{Motorcycle}: & \text{discounted fee of } \$2.00
\end{cases}$$

Under **Dynamic Late Binding**, the exact memory pointer to the executable method is resolved at runtime via a Virtual Method Table (`vtable`), eliminating brittle, monolithic `switch-case` statements across the codebase.

---

### 3. Advanced Structural Relationships: Association, Aggregation, and Composition

Classes do not exist in isolation. In the real world, entities interact through three distinct structural couplings:

```
+---------------------------------------------------------------------------------------------------+
|                        STRUCTURAL RELATIONSHIPS IN OBJECT MODELING                                |
+---------------------------------------------------------------------------------------------------+
| RELATIONSHIP   | UML NOTATION         | COUPLING STRENGTH | LIFECYCLE DEPENDENCY                  |
| -------------- | -------------------- | ----------------- | ------------------------------------- |
| 1. ASSOCIATION | Solid directed line  | Loose Reference   | Completely independent lifecycles.   |
|                |                      |                   | e.g. Doctor treats Patient.           |
|                                                                                                   |
| 2. AGGREGATION | White / Hollow       | Whole-Part (has-a)| Independent lifecycles. If whole is   |
|    ("Shared")  | Diamond at Whole end | Weak Ownership    | destroyed, parts survive.             |
|                | ◇------------------- |                   | e.g. Department has Professors.       |
|                                                                                                   |
| 3. COMPOSITION | Black / Filled Solid | Whole-Part (has-a)| Dependent lifecycles. If whole is     |
|    ("Composite")Diamond at Whole end | Strong Ownership  | destroyed, parts are destroyed too!   |
|                | ◆------------------- |                   | e.g. Hospital Building has Rooms.     |
+---------------------------------------------------------------------------------------------------+
```

#### 3.1 Aggregation vs. Composition: The Architectural Acid Test
To differentiate between Aggregation and Composition during system analysis, apply the **Destruction / Cascade Invariant**:
> *"If the parent whole is deleted from the database, do the constituent child parts have an independent legal and operational existence?"*
- If **YES** $\implies$ **Aggregation (Shared Whole-Part):** If a `University` closes down, the `Professors` continue to exist as autonomous individuals.
- If **NO** $\implies$ **Composition (Composite Whole-Part):** If a `Customer_Order` is permanently deleted, its internal `Order_Line_Items` cannot exist floating in vacuum; they are destroyed concurrently.

---

### 4. The UML 2.5 Metamodel Framework

Standardized by the **Object Management Group (OMG)**, the Unified Modeling Language (UML) is a graphical language for visualizing, specifying, constructing, and documenting the artifacts of distributed software systems.

The core architecture of UML 2.5 is built upon **three foundational building blocks**:

```
+---------------------------------------------------------------------------------------------------+
|                            THE THREE UML BUILDING BLOCKS (OMG STANDARD)                           |
|                                                                                                   |
|  1. THINGS (The Abstractions / Nouns of Models):                                                  |
|     * Structural Classifiers : Class, Interface, Use Case, Component, Node (Hardware).            |
|     * Behavioral Dynamisms   : Interaction (Messages), State Machine (States/Events).             |
|     * Grouping Containers    : Package (Hierarchical namespaces and modules).                     |
|     * Annotational Remarks   : Note (Dangling dog-eared comment box).                             |
|                                                                                                   |
|  2. RELATIONSHIPS (The Connections / Verbs of Models):                                            |
|     * Association            : Semantic structural link between classifiers.                      |
|     * Generalization         : Subclass to superclass inheritance link (hollow triangle).          |
|     * Realization            : Class implementing an Interface contract (dashed hollow triangle).|
|     * Dependency             : Supplier-client using relationship (dashed arrow).                 |
|                                                                                                   |
|  3. DIAGRAMS (The Graphical Views):                                                               |
|     * Groupings of Things and Relationships capturing a specific architectural perspective.        |
+---------------------------------------------------------------------------------------------------+
```

---

### 5. The Three Complementary Modeling Perspectives

No single diagram can represent an entire non-trivial software system. UML 2.5 partitions system models across **three orthogonal perspectives**:

```
+---------------------------------------------------------------------------------------------------+
|                        THE THREE ORTHOGONAL OO MODELING PERSPECTIVES                              |
+---------------------------------------------------------------------------------------------------+
| 1. THE CLASS MODEL (Structural / Static Perspective):                                             |
|    * Represents the static vocabulary, classes, attributes, methods, and associations.            |
|    * Primary Diagrams: Class Diagrams, Object Diagrams, Package Diagrams, Component Diagrams.     |
|                                                                                                   |
| 2. THE STATE MODEL (Dynamic / Temporal Perspective):                                              |
|    * Represents the lifecycle states of an individual object over time in response to events.    |
|    * Primary Diagrams: State Machine Diagrams (Harel Statecharts).                                |
|                                                                                                   |
| 3. THE INTERACTION MODEL (Functional / Scenario Perspective):                                     |
|    * Represents how clusters of objects collaborate and pass messages to fulfill user goals.     |
|    * Primary Diagrams: Use Case Diagrams, Sequence Diagrams, Communication Diagrams, Activity.    |
+---------------------------------------------------------------------------------------------------+
```

---

### 6. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

A junior software analyst submits a draft UML Class Diagram for a mission-critical Cloud Airline Flight Reservation Platform. The design document contains the following four structural proposals:

1. *"Relationship 1: Airplane has an Aggregation relationship (white diamond) with Airplane_Engine."*
2. *"Relationship 2: Flight_Reservation has an Association relationship with Passenger and a Composition relationship (black diamond) with Seat_Assignment."*
3. *"Proposal 3: To handle passenger frequent flyer tiers (Standard, Silver, Gold, Platinum), the analyst creates four concrete subclasses inheriting from Passenger: `class SilverPassenger : public Passenger`, `class GoldPassenger : public Passenger`, etc."*
4. *"Proposal 4: Flight_Schedule class declares all attributes (`flight_number`, `departure_time`, `origin`, `destination`) with public visibility (`+`) so that UI controllers can mutate them directly without getter/setter overhead."*

**Architectural Audit Tasks:**
1. Evaluate Relationship 1: Is white-diamond Aggregation appropriate for an aircraft and its engine? Justify why Composition is or is not applicable.
2. Critique Proposal 3: Identify the fatal object-oriented design anti-pattern (Subclassing Dynamic State) and explain why inheritance fails when a customer upgrades their tier.
3. Critique Proposal 4: Identify the violation of Encapsulation and Information Hiding, explaining how direct public mutation causes architectural corruption.

<details>
<summary>Click to view Level 1 Solution & Architectural Critique</summary>

##### 1. Evaluation of Relationship 1 (Airplane vs. Airplane_Engine):
- **White Diamond Aggregation is ARCHITECTURALLY CORRECT:**
  In commercial aviation, jet engines are high-value independent assets with their own serial numbers, maintenance cycles, and flight-hour logs. Engines are routinely detached from one airframe, overhauled in a test hangar, and remounted onto a completely different airplane.
  If the analyst had used black-diamond Composition, deleting a decommissioned `Airplane` instance from the database would automatically cascade-delete its multimillion-dollar `Airplane_Engine` records! Aggregation preserves independent lifecycles.

##### 2. Critique of Proposal 3 (Inheritance for Dynamic State):
- **Anti-Pattern: Subclassing Dynamic State / Lifecycle Roles:**
  Inheritance (`is-a`) represents a permanent, compile-time identity. A passenger's frequent flyer tier is a **dynamic, temporal role** that changes frequently as miles are accrued or expired.
  If `GoldPassenger` is a subclass of `Passenger`, upgrading a passenger from Silver to Gold requires destroying the existing `SilverPassenger` object in memory and instantiating a new `GoldPassenger` object, copying all booking history and ticket references.
  **Correct Architectural Solution:** Apply the **State Pattern** or **Strategy Pattern**: `Passenger` holds a private composition reference to an abstract `FrequentFlyerTier` interface (`StandardTier`, `SilverTier`, `GoldTier`), enabling polymorphic runtime tier swaps without object reallocation.

##### 3. Critique of Proposal 4 (Public Attribute Visibility):
- **Fatal Violation of Encapsulation (Information Hiding):**
  Marking attributes as public (`+`) exposes internal mutable memory directly to external callers.
  External UI controllers could mutate `departure_time` to a timestamp in the past, or set `origin` and `destination` to the same airport code, bypassing all domain invariant validations, business rules, and audit logging.
  **Correct Architectural Solution:** Mark all attributes private (`-`), and expose controlled, validating public methods (e.g., `+ reschedule_flight(new_time: UTC_Timestamp): Result`).

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The UML Metamodel Graph & Cycle Linter

An enterprise CASE tool parses XMI/JSON exports of UML class models to verify metamodel integrity before generating code. The tool is crashing with infinite recursion during inheritance audits and is failing to detect package visibility violations (e.g., a private method being called across package namespaces).

Examine the flawed Python analyzer below:

```python
# FLAWED UML METAMODEL ANALYZER (PYTHON)
def audit_class_model(classes, inheritance_links):
    issues = []

    # Check 1: Detect multiple inheritance conflicts
    for child, parents in inheritance_links.items():
        # BUG 1: Assumes multiple inheritance is always illegal,
        # falsely flagging valid C++ and interface realization models!
        if len(parents) > 1:
            issues.append(f"Multiple inheritance detected on {child}")

    # Check 2: Cycle detection
    # BUG 2: Infinite recursive loop! Fails to detect circular inheritance
    # (e.g. A extends B, B extends C, C extends A) and crashes with RecursionError!
    def get_ancestors(cls_name):
        ancestors = []
        for p in inheritance_links.get(cls_name, []):
            ancestors.append(p)
            ancestors.extend(get_ancestors(p))
        return ancestors

    for c in classes:
        anc = get_ancestors(c)
        if c in anc:
            issues.append(f"Circular inheritance on {c}")

    return issues
```

**Debug Assignment:**
1. Identify all runtime exceptions, false positive warnings, and infinite loop bugs in this script.
2. Implement a robust cycle detector using a visited stack to detect circular inheritance graphs without crashing.
3. Implement a formal UML Visibility Linter verifying that:
   - Private members (`-`) are never referenced by external classes or subclasses.
   - Protected members (`#`) are referenced only by verified generalized descendants.

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. Flaws in the Original Script:
- **Crash on Cyclic Graphs:** `get_ancestors(cls_name)` recurses infinitely when a cycle exists ($A \to B \to A$), crashing the Python interpreter with a `RecursionError: maximum recursion depth exceeded`.
- **False Multiple Inheritance Rejection:** Conflating class inheritance with interface realization. In UML 2.5, a class can realize unlimited interfaces. Even in languages like C++, multiple class inheritance is structurally permitted.
- **Omission of Member Visibility Verification:** The script completely ignored access modifier invariants (`+`, `-`, `#`, `~`).

##### 2. Corrected Production Implementation:

```python
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

@dataclass
class Member:
    name: str
    visibility: str # '+', '-', '#', '~'

@dataclass
class UmlClass:
    name: str
    package: str
    members: List[Member]
    superclasses: List[str]

class ProductionUmlLinter:
    def __init__(self, class_registry: Dict[str, UmlClass]):
        self.classes = class_registry

    def detect_circular_inheritance(self) -> List[str]:
        # Detects inheritance cycles using 3-color DFS graph traversal
        # 0: Unvisited (White), 1: Visiting (Gray), 2: Visited (Black)
        state: Dict[str, int] = {c: 0 for c in self.classes}
        cycle_errors = []

        def dfs(cls_name: str, path: List[str]):
            state[cls_name] = 1 # Gray
            path.append(cls_name)

            for parent in self.classes[cls_name].superclasses:
                if parent not in self.classes:
                    continue # External framework class
                if state[parent] == 1: # Found gray node -> Cycle!
                    cycle_idx = path.index(parent)
                    cycle_repr = " -> ".join(path[cycle_idx:] + [parent])
                    cycle_errors.append(f"[FATAL INHERITANCE CYCLE] {cycle_repr}")
                elif state[parent] == 0:
                    dfs(parent, path)

            path.pop()
            state[cls_name] = 2 # Black

        for c in self.classes:
            if state[c] == 0:
                dfs(c, [])

        return cycle_errors

    def is_subclass_of(self, child_name: str, target_parent: str) -> bool:
        visited = set()
        queue = [child_name]
        while queue:
            curr = queue.pop(0)
            if curr == target_parent and curr != child_name:
                return True
            if curr in visited:
                continue
            visited.add(curr)
            if curr in self.classes:
                queue.extend(self.classes[curr].superclasses)
        return False

    def verify_member_access(
        self,
        calling_class: str,
        target_class: str,
        member_name: str
    ) -> Optional[str]:
        target = self.classes.get(target_class)
        if not target:
            return f"Target class '{target_class}' not found."

        member = next((m for m in target.members if m.name == member_name), None)
        if not member:
            return f"Member '{member_name}' does not exist on class '{target_class}'."

        if member.visibility == '+':
            return None # Public is always valid

        if member.visibility == '-':
            if calling_class != target_class:
                return (f"[VISIBILITY VIOLATION] Class '{calling_class}' attempted to access "
                        f"PRIVATE (-) member '{member_name}' of class '{target_class}'.")

        if member.visibility == '#':
            if calling_class != target_class and not self.is_subclass_of(calling_class, target_class):
                return (f"[VISIBILITY VIOLATION] Class '{calling_class}' is not a descendant of "
                        f"'{target_class}' and cannot access PROTECTED (#) member '{member_name}'.")

        if member.visibility == '~':
            caller = self.classes.get(calling_class)
            if not caller or caller.package != target.package:
                return (f"[PACKAGE VIOLATION] Class '{calling_class}' (pkg: {caller.package if caller else '?'}) "
                        f"cannot access PACKAGE (~) member '{member_name}' of class '{target_class}' (pkg: {target.package}).")

        return None
```

</details>

---

#### Level 3 — High-Scale System Design: Graph-Based UML Metamodel Consistency & Encapsulation Validator in C++

Design and implement a complete, production-grade C++17 **UML 2.5 Metamodel Consistency & Encapsulation Verifier**. The system must:
1. Represent a complex UML model using formal Object-Oriented AST data structures:
   - `UmlClass` (Name, Namespace/Package, Visibility, Attributes, Operations, Generalizations, Associations).
   - `StructuralRelationship` (Association, Aggregation, Composition, Generalization, Realization).
2. Implement a **Cycle Detection Algorithm** across the generalization hierarchy using three-color depth-first graph traversal.
3. Validate **Encapsulation & Access Modifiers**:
   - Verify that all attributes in domain classes are private (`-`) or protected (`#`).
   - Flag any public (`+`) attributes as architectural encapsulation leaks.
4. Detect **Composition Lifecycle Violations**:
   - Assert that a composite part class cannot participate in more than ONE composition whole (the single-ownership composition invariant).
5. Output a comprehensive diagnostic compliance audit report.

<details>
<summary>Click to view complete C++17 UML Metamodel Verifier</summary>

```cpp
/**
 * ============================================================================
 * UML 2.5 METAMODEL CONSISTENCY & ENCAPSULATION VERIFIER (C++17)
 * ============================================================================
 * Implements:
 * 1. Object-Oriented UML AST (Classifiers, Visibility, Relationships).
 * 2. Generalization Hierarchy Cycle Detection (Three-Color DFS).
 * 3. Encapsulation Linter (Zero Public Attribute Leaks).
 * 4. Composition Single-Ownership Invariant Enforcement.
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
// METAMODEL DOMAIN STRUCTURES
// ============================================================================

enum class Visibility {
    PUBLIC,    // '+'
    PRIVATE,   // '-'
    PROTECTED, // '#'
    PACKAGE    // '~'
};

enum class RelationshipKind {
    ASSOCIATION,
    AGGREGATION, // White diamond (Shared ownership)
    COMPOSITION, // Black diamond (Exclusive whole-part ownership)
    GENERALIZATION, // Inheritance
    REALIZATION     // Interface fulfillment
};

struct UmlAttribute {
    std::string name;
    std::string type;
    Visibility visibility;
};

struct UmlOperation {
    std::string name;
    std::string return_type;
    Visibility visibility;
};

struct UmlClassNode {
    std::string name;
    std::string package_name;
    std::vector<UmlAttribute> attributes;
    std::vector<UmlOperation> operations;
    std::vector<std::string> superclass_names;
};

struct RelationshipEdge {
    std::string source_class; // Part or Subclass
    std::string target_class; // Whole or Superclass
    RelationshipKind kind;
};

// ============================================================================
// UML METAMODEL VERIFICATION ENGINE
// ============================================================================

class UmlMetamodelEngine {
private:
    std::unordered_map<std::string, UmlClassNode> classes;
    std::vector<RelationshipEdge> relationships;

    enum class DfsColor { WHITE, GRAY, BLACK };

    bool dfs_cycle(const std::string& curr, 
                   std::unordered_map<std::string, DfsColor>& colors,
                   std::vector<std::string>& path,
                   std::vector<std::string>& detected_cycles) const {
        colors[curr] = DfsColor::GRAY;
        path.push_back(curr);

        auto it = classes.find(curr);
        if (it != classes.end()) {
            for (const auto& parent : it->second.superclass_names) {
                if (classes.find(parent) == classes.end()) continue;

                if (colors[parent] == DfsColor::GRAY) {
                    std::string cycle_str = "";
                    auto p_it = std::find(path.begin(), path.end(), parent);
                    while (p_it != path.end()) {
                        cycle_str += *p_it + " -> ";
                        p_it++;
                    }
                    cycle_str += parent;
                    detected_cycles.push_back(cycle_str);
                    return true;
                }

                if (colors[parent] == DfsColor::WHITE) {
                    dfs_cycle(parent, colors, path, detected_cycles);
                }
            }
        }

        colors[curr] = DfsColor::BLACK;
        path.pop_back();
        return false;
    }

public:
    void add_class(const UmlClassNode& node) {
        classes[node.name] = node;
    }

    void add_relationship(const RelationshipEdge& edge) {
        relationships.push_back(edge);
        if (edge.kind == RelationshipKind::GENERALIZATION) {
            classes[edge.source_class].superclass_names.push_back(edge.target_class);
        }
    }

    void audit_model_integrity() const {
        std::cout << "\n================================================================================\n";
        std::cout << "                 UML 2.5 METAMODEL ARCHITECTURAL AUDIT REPORT\n";
        std::cout << "================================================================================\n";

        std::vector<std::string> defects;

        // 1. Generalization Cycle Detection
        std::unordered_map<std::string, DfsColor> colors;
        for (const auto& [name, _] : classes) colors[name] = DfsColor::WHITE;

        std::vector<std::string> detected_cycles;
        for (const auto& [name, _] : classes) {
            if (colors[name] == DfsColor::WHITE) {
                std::vector<std::string> path;
                dfs_cycle(name, colors, path, detected_cycles);
            }
        }

        for (const auto& c : detected_cycles) {
            defects.push_back("[FATAL INHERITANCE CYCLE] " + c);
        }

        // 2. Encapsulation & Information Hiding Linter
        for (const auto& [name, cls] : classes) {
            for (const auto& attr : cls.attributes) {
                if (attr.visibility == Visibility::PUBLIC) {
                    defects.push_back("[ENCAPSULATION LEAK] Class '" + name + "' exposes PUBLIC (+) attribute '" + 
                                      attr.name + "'. All attributes must be private (-) or protected (#)!");
                }
            }
        }

        // 3. Composition Single-Ownership Invariant
        // A part class cannot belong to more than ONE composition whole!
        std::unordered_map<std::string, std::vector<std::string>> composition_owners;
        for (const auto& rel : relationships) {
            if (rel.kind == RelationshipKind::COMPOSITION) {
                composition_owners[rel.source_class].push_back(rel.target_class);
            }
        }

        for (const auto& [part, wholes] : composition_owners) {
            if (wholes.size() > 1) {
                std::string owners = "";
                for (const auto& w : wholes) owners += w + " ";
                defects.push_back("[COMPOSITION INVARIANT VIOLATION] Part Class '" + part + 
                                  "' is owned by MULTIPLE composition wholes: [" + owners + 
                                  "]. Composition requires exclusive, non-shared lifecycle ownership!");
            }
        }

        // Report output
        std::cout << "Total Classes Audited       : " << classes.size() << "\n";
        std::cout << "Total Relationships Audited : " << relationships.size() << "\n";
        std::cout << "Total Architectural Defects : " << defects.size() << "\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        if (defects.empty()) {
            std::cout << ">>> MODEL AUDIT STATUS: PASSED (100% UML 2.5 COMPLIANT)\n";
        } else {
            std::cout << ">>> MODEL AUDIT STATUS: FAILED (ARCHITECTURAL DEFECTS DETECTED):\n";
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
    UmlMetamodelEngine engine;

    // 1. Valid Classes
    UmlClassNode patient = {"Patient", "Domain.Core", 
        {{"national_id", "String", Visibility::PRIVATE}, {"name", "String", Visibility::PRIVATE}},
        {{"get_medical_history", "History", Visibility::PUBLIC}}
    };
    engine.add_class(patient);

    UmlClassNode record = {"MedicalRecord", "Domain.Clinical",
        {{"record_id", "UUID", Visibility::PRIVATE}},
        {{"sign_record", "void", Visibility::PUBLIC}}
    };
    engine.add_class(record);

    // 2. Class with Encapsulation Violation (Public Attribute)
    UmlClassNode leaking_class = {"BillingAccount", "Domain.Billing",
        {{"account_balance", "Decimal", Visibility::PUBLIC}}, // BUG: Public attribute!
        {{"deduct", "void", Visibility::PUBLIC}}
    };
    engine.add_class(leaking_class);

    // 3. Classes with Circular Inheritance (NodeA -> NodeB -> NodeC -> NodeA)
    UmlClassNode nodeA = {"ClassifierA", "Test", {}, {}};
    UmlClassNode nodeB = {"ClassifierB", "Test", {}, {}};
    UmlClassNode nodeC = {"ClassifierC", "Test", {}, {}};
    engine.add_class(nodeA);
    engine.add_class(nodeB);
    engine.add_class(nodeC);

    engine.add_relationship({"ClassifierA", "ClassifierB", RelationshipKind::GENERALIZATION});
    engine.add_relationship({"ClassifierB", "ClassifierC", RelationshipKind::GENERALIZATION});
    engine.add_relationship({"ClassifierC", "ClassifierA", RelationshipKind::GENERALIZATION}); // Cycle!

    // 4. Classes with Composition Multiple-Ownership Violation
    UmlClassNode room = {"Room", "Facilities", {}, {}};
    UmlClassNode hospital = {"HospitalBuilding", "Facilities", {}, {}};
    UmlClassNode clinic = {"AmbulatoryClinic", "Facilities", {}, {}};
    engine.add_class(room);
    engine.add_class(hospital);
    engine.add_class(clinic);

    // Illegal: Room cannot be composite part of BOTH Hospital and Clinic simultaneously!
    engine.add_relationship({"Room", "HospitalBuilding", RelationshipKind::COMPOSITION});
    engine.add_relationship({"Room", "AmbulatoryClinic", RelationshipKind::COMPOSITION});

    // Execute Comprehensive Formal Verification
    engine.audit_model_integrity();

    return 0;
}
```

</details>

---

### 7. Reference Video Lecture

{{ media:oo-concepts-video }}

In this video by Abdul Bari, the foundational principles of Object-Oriented analysis, encapsulation, dynamic polymorphism, and structural inheritance are explored in technical depth.
