# Lesson 2 — Object Diagrams: Temporal Memory Snapshots & Multiplicity Verification

## Executive Summary & Academic Orientation

In software engineering modeling according to the Unified Modeling Language (UML 2.5) metamodel, **Class Diagrams** establish the static ontological grammar of an application—defining classifications, invariants, attribute types, and permissible structural associations. However, static schemas cannot capture runtime behavior, transient memory configurations, dynamic pointer graphs, or the exact state vector of an execution heap at a deterministic timestamp $t_0$.

**Object Diagrams** (also formally designated as **Instance Specifications** within the UML 2.5 metamodel kernel) bridge this analytical divide. An object diagram depicts a discrete, frozen slice of runtime execution: concrete instantiated objects, their explicit bound attribute values, and the realized pointer or reference associations connecting them, termed **Links**.

This lesson explores the theoretical foundations, metamodel semantics, formal graph properties, and validation algorithms that govern object diagrams. We analyze how object graphs serve as rigorous constructive proofs that validate or refute class diagram multiplicity bounds, detect cyclical memory topologies and memory leaks, and provide empirical evidence during architectural inspections.

```
+-------------------------------------------------------------------------+
|                  UML 2.5 METAMODEL INSTANCE LAYER MAPPING               |
|                                                                         |
|  Metamodel Layer M2:  [ Class ] <------ 1:N Association ------> [ Class ]|
|                             |                                       |   |
|     Conforms To            |                                       |   |
|                             v                                       v   |
|  Model Layer M1:     [ :Order ] <------- Concrete Link -------> [ :Item ]|
|                         |                                           |   |
|  Runtime Memory M0:  Heap Addr: 0x7ffd...                 Heap Addr: 0x7ffd...|
|                      id = 10492                           sku = "SKU-99"|
|                      status = CONFIRMED                   price = $420.00|
+-------------------------------------------------------------------------+
```

---

## 2.1 The Object Diagram Mandate: Temporal Memory Snapshots at Specific Instants (Time $t_0$)

### Theoretical Justification of Instance Modeling

A class diagram is an intensional definition: it characterizes the infinite set of possible system configurations through generic constraints and types. An object diagram is an extensional snapshot: it manifests a finite, concrete subset of instances at a distinct epoch:

$$\mathcal{S}(t) = \langle \mathcal{O}(t), \mathcal{L}(t), \sigma_t \rangle$$

Where:
- $\mathcal{O}(t) = \{o_1, o_2, \dots, o_n\}$ is the set of instantiated objects allocated in addressable memory space at time $t$.
- $\mathcal{L}(t) \subseteq \mathcal{O}(t) \times \mathcal{O}(t)$ is the set of realized links (runtime references, pointers, or foreign keys).
- $\sigma_t : \mathcal{O}(t) \times \mathcal{A} \to \mathcal{V}$ is the state mapping function assigning a concrete literal value $v \in \mathcal{V}$ to each attribute $a \in \mathcal{A}$ of object $o$.

```
+-------------------------------------------------------------------------+
|                      TEMPORAL LIFECYCLE SNAPSHOTS                       |
|                                                                         |
|  Instant t_0 (Pre-Checkout):                                            |
|    c1:Customer [id=101] ---> cart:ShoppingCart [itemCount=0]           |
|                                                                         |
|  Instant t_1 (Item Added):                                              |
|    c1:Customer [id=101] ---> cart:ShoppingCart [itemCount=1]           |
|                                    |                                    |
|                                    +---> line1:Item [sku="KB-01"]       |
|                                                                         |
|  Instant t_2 (Post-Checkout & Archive):                                 |
|    c1:Customer [id=101] ---> cart:ShoppingCart [itemCount=0]           |
|         |                                                               |
|         +---> ord1:Order [total=$85.00] ---> inv1:Invoice [status=PAID] |
+-------------------------------------------------------------------------+
```

### Static Schema vs. Dynamic Temporal Snapshot

| Dimension | Class Diagram (M1 Specification) | Object Diagram (M1 Instance Snapshot) |
| :--- | :--- | :--- |
| **Temporal Nature** | Timeless, time-invariant invariant schema | Frozen at exact execution instant $t_k$ |
| **Node Semantics** | Classifier / Type abstraction (`ClassName`) | Specific instance allocation (`name : ClassName`) |
| **Edge Semantics** | General association with multiplicity $(m..n)$ | Concrete reference Link without multiplicities |
| **Attribute State** | Type declarations (`balance : Decimal`) | Explicit literal bindings (`balance = $1,450.25`) |
| **Metamodel Element** | `UML::Classification::Class` | `UML::Classification::InstanceSpecification` |
| **Analytical Role** | Design blueprints, compile-time structure | Validation, heap debugging, design pattern verification |

---

## 2.2 Underlined Instance Notation, Literal Attribute Bindings, and Links

```
+-------------------------------------------------------------------------+
|                       UML 2.5 INSTANCE NOTATION                         |
|                                                                         |
|   Named Instance:         Anonymous Instance:       Orphan/Unlinked:    |
|   +-------------------+   +-------------------+    +------------------+ |
|   | <u>order1:Order</u>   |   | <u>:Customer</u>    |    | <u>log:Logger</u>| |
|   +-------------------+   +-------------------+    +------------------+ |
|   | id = "ORD-9021"   |   | id = 8841         |    | level = "DEBUG"  | |
|   | total = 185.50    |   | tier = GOLD       |    +------------------+ |
|   | status = PENDING  |   +-------------------+                         |
|   +-------------------+                                                 |
|             \                       /                                   |
|              \                     /                                    |
|               \                   /                                     |
|                +-----------------+                                      |
|                |  Concrete Link  |  (Solid line, NO multiplicity labels)|
+-------------------------------------------------------------------------+
```

### UML Underlined Identity Metamodel

In UML 2.5, instances are formally denoted by underlining their header: `<u>instanceName : ClassName</u>`. This syntactic convention prevents ambiguity between classifiers and heap instances.

1. **Named Instance (`<u>objName : ClassName</u>`)**: Used when the exact reference identifier is analytically relevant (e.g., distinguishing `primaryDb : DatabaseConnection` from `replicaDb : DatabaseConnection`).
2. **Anonymous Instance (`<u>:ClassName</u>`)**: Used when the classifier type is significant but individual instance identification is arbitrary (e.g., auxiliary collection items or subscriber observers).
3. **Implicitly Typed Instance (`<u>instanceName</u>`)**: Rare form where the type is inferred from environmental context or dynamic duck typing.

### Attribute Value Compartment

Unlike class diagrams that define visibility and data types (`- balance : float`), object diagrams display runtime assignment expressions:
$$\text{attributeIdentifier} = \text{literalValue}$$
- Values must be fully resolved literals: `status = OrderStatus::SHIPPED`, `retryCount = 3`, `timestamp = "2026-10-03T14:30:00Z"`.
- Complex embedded value objects (structs) can either be nested or represented via directed links to child instance specifications.

### Links vs. Associations

A **Link** is a direct instance of an **Association**.
- **No Multiplicity Ranges**: While an association between `Customer` and `Order` specifies `1` to `0..*`, a link connects exactly two concrete instances (or $k$ instances in an $n$-ary link). Multiplicity labels like `1..*` on an object link are illegal in UML.
- **Link Names**: If an association has a name or role name, the link may be decorated with an underlined role name: `<u>placedBy</u>`.
- **Navigability**: If the underlying association has directed navigability (`-->`), the link manifests as a directed pointer. If bidirectional, it appears as an undirected solid segment.

---

## Visual Architecture: Object Diagrams and Instance Graph Proofs

{{ media:sam-object-diagrams-diagram }}

### Multimedia Deep-Dive: Object Modeling & Instance Verification
Enhance your understanding of how object modeling and instance configurations are represented in software architectures:

{{ media:object-diagram-video }}

---

## 2.3 Multiplicity Invariant Proofs: Verifying & Disproving Class Schemas

```
+-------------------------------------------------------------------------+
|                  MULTIPLICITY VALIDATION & COUNTER-EXAMPLES             |
|                                                                         |
|  Class Diagram Invariant Under Test:                                    |
|  [ Department ] 1 <---------- 1..* ----------> [ Professor ]            |
|                                                                         |
|  Scenario A: VALID INSTANCE GRAPH                                       |
|  +--------------------+             +--------------------+              |
|  | <u>cs:Department</u> |<--- link ---| <u>drSmith:Prof</u>|              |
|  +--------------------+ \           +--------------------+              |
|                          \          +--------------------+              |
|                           +-- link -| <u>drJones:Prof</u>|              |
|                                     +--------------------+              |
|                                                                         |
|  Scenario B: INVALID INSTANCE GRAPH (Violation of 1..* Lower Bound)     |
|  +--------------------+                                                 |
|  | <u>art:Department</u>|  (Zero linked professors! Invariant Broken)   |
|  +--------------------+                                                 |
|                                                                         |
|  Scenario C: INVALID INSTANCE GRAPH (Violation of Upper Bound 1)        |
|  +--------------------+             +--------------------+              |
|  | <u>cs:Department</u> |<--- link ---| <u>drTuring:Prof</u>|              |
|  +--------------------+             +---------+----------+              |
|  +--------------------+                       |                         |
|  | <u>ee:Department</u> |<------- link -------+ (Prof has 2 Depts!)     |
|  +--------------------+                                                 |
+-------------------------------------------------------------------------+
```

### Mathematical Foundations of Multiplicity Verification

Let a class diagram define an association $A \subseteq C_1 \times C_2$ with multiplicity bounds $\mu_1 = [\alpha_1, \beta_1]$ on $C_1$ and $\mu_2 = [\alpha_2, \beta_2]$ on $C_2$, where $\alpha \in \mathbb{N}$ and $\beta \in \mathbb{N} \cup \{\infty\}$.

At runtime, an object diagram defines a bipartite graph $G = (V_1, V_2, E)$, where $V_1 \subseteq C_1$, $V_2 \subseteq C_2$, and $E \subseteq A$.
The object diagram satisfies the class schema invariants if and only if:

$$\forall v_1 \in V_1: \alpha_2 \le \mathrm{deg}(v_1) \le \beta_2$$

$$\forall v_2 \in V_2: \alpha_1 \le \mathrm{deg}(v_2) \le \beta_1$$

Where $\mathrm{deg}(v)$ represents the degree (number of incident links) of vertex $v$.

### Object Diagrams as Constructive Proofs
1. **Satisfiability Proof**: To prove that a complex class diagram with multiple associations, inheritance hierarchies, and OCL (Object Constraint Language) constraints is structurally satisfiable (non-vacuous), the modeler must construct at least one valid object diagram containing non-empty sets of instances that satisfy all constraints simultaneously.
2. **Refutation / Counterexample**: If a domain expert claims that an employee can temporarily operate without a manager, but the class diagram specifies `[Employee] * ---- 1 [Manager]`, the modeler draws an object diagram showing `<u>emp1:Employee</u>` with $\mathrm{deg}(emp1) = 0$. This visual counterexample demonstrates that the static schema rejects valid business states.

---

## 2.4 Mapping Class Schemas to Runtime Heap Graphs

In high-reliability enterprise systems, inconsistencies between class designs and runtime object topologies lead to fatal bugs: dangling references, broken bidirectional invariants, and cyclic pointer chains that break garbage collectors or reference-counting pointer topologies (`std::shared_ptr`).

```
+-------------------------------------------------------------------------+
|                  HEAP TOPOLOGY ANOMALIES IN OBJECT GRAPHS               |
|                                                                         |
|  1. Asymmetric Bidirectional Link:                                      |
|     <u>o1:Order</u>.customerRef = 0xAA (Points to <u>c1:Customer</u>)   |
|     <u>c1:Customer</u>.ordersList = [] (Customer has NO record of o1!)  |
|                                                                         |
|  2. Dangling Reference:                                                 |
|     <u>pay:Payment</u>.orderRef = 0xDEADBEEF (Target destroyed!)        |
|                                                                         |
|  3. Strong Reference Cycle (Memory Leak in C++ Ref Counting):           |
|     <u>parent:Node</u> ---> (shared_ptr) ---> <u>child:Node</u>         |
|           ^                                        |                    |
|           +-------------- (shared_ptr) ------------+                    |
|     (Cycle prevents ref_count from reaching 0 -> Leak!)                 |
+-------------------------------------------------------------------------+
```

---

## 2.5 Class-to-Object Conformance Validator in Modern C++17

The following industrial-grade C++17 simulation engine implements a formal metamodel validator. It accepts class specifications (with multiplicity bounds) and evaluates runtime object graphs for invariant compliance, detecting dangling links, multiplicity violations, and cyclic pointer leaks.

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <optional>
#include <variant>
#include <cassert>
#include <iomanip>

// ============================================================================
// METAMODEL LAYER (M1): Class Schema Definitions & Multiplicities
// ============================================================================

struct Multiplicity {
    size_t minBound;
    size_t maxBound; // SIZE_MAX represents infinity (*)

    bool isInRange(size_t count) const {
        return count >= minBound && count <= maxBound;
    }

    std::string toString() const {
        std::string s = std::to_string(minBound) + "..";
        if (maxBound == SIZE_MAX) s += "*";
        else s += std::to_string(maxBound);
        return s;
    }
};

struct AssociationSchema {
    std::string associationName;
    std::string sourceClass;
    std::string targetClass;
    Multiplicity sourceMultiplicity; // Allowed instances of Source connected to 1 Target
    Multiplicity targetMultiplicity; // Allowed instances of Target connected to 1 Source
};

// ============================================================================
// INSTANCE LAYER (M0): Runtime Object Graph Specifications
// ============================================================================

using AttributeValue = std::variant<int, double, std::string, bool>;

struct ObjectInstance {
    std::string instanceName;
    std::string className;
    std::unordered_map<std::string, AttributeValue> attributes;
};

struct RuntimeLink {
    std::string associationName;
    std::string sourceInstance;
    std::string targetInstance;
};

// ============================================================================
// VALIDATION ENGINE
// ============================================================================

class ObjectGraphValidator {
private:
    std::unordered_map<std::string, std::unordered_set<std::string>> classRegistry; // ClassName -> Registered Attributes
    std::unordered_map<std::string, AssociationSchema> associationSchemas;           // AssocName -> Schema
    std::unordered_map<std::string, ObjectInstance> objectHeap;                     // InstanceName -> Object
    std::vector<RuntimeLink> activeLinks;

public:
    void registerClass(const std::string& className, const std::unordered_set<std::string>& validAttributes) {
        classRegistry[className] = validAttributes;
    }

    void registerAssociation(const AssociationSchema& schema) {
        associationSchemas[schema.associationName] = schema;
    }

    bool instantiateObject(const ObjectInstance& instance) {
        if (classRegistry.find(instance.className) == classRegistry.end()) {
            std::cerr << "[ERROR] Unknown class: " << instance.className << " for instance: " << instance.instanceName << "\n";
            return false;
        }
        objectHeap[instance.instanceName] = instance;
        return true;
    }

    bool addLink(const std::string& assocName, const std::string& srcInstance, const std::string& tgtInstance) {
        if (associationSchemas.find(assocName) == associationSchemas.end()) {
            std::cerr << "[ERROR] Unknown association schema: " << assocName << "\n";
            return false;
        }
        activeLinks.push_back({assocName, srcInstance, tgtInstance});
        return true;
    }

    struct ConformanceReport {
        bool isValid = true;
        std::vector<std::string> violations;
        std::vector<std::string> warnings;
    };

    ConformanceReport validateConformance() const {
        ConformanceReport report;

        // 1. Verify Dangling Links (Objects referenced in links must exist in heap)
        for (const auto& link : activeLinks) {
            bool srcExists = (objectHeap.find(link.sourceInstance) != objectHeap.end());
            bool tgtExists = (objectHeap.find(link.targetInstance) != objectHeap.end());

            if (!srcExists) {
                report.isValid = false;
                report.violations.push_back("Dangling link: Source instance '" + link.sourceInstance + "' not found in heap.");
            }
            if (!tgtExists) {
                report.isValid = false;
                report.violations.push_back("Dangling link: Target instance '" + link.targetInstance + "' not found in heap.");
            }
            if (!srcExists || !tgtExists) continue;

            // Verify Classifier Type Match for Association Ends
            const auto& schema = associationSchemas.at(link.associationName);
            if (objectHeap.at(link.sourceInstance).className != schema.sourceClass) {
                report.isValid = false;
                report.violations.push_back("Type Mismatch: Link '" + link.associationName + "' expects source class '" + 
                    schema.sourceClass + "' but got '" + objectHeap.at(link.sourceInstance).className + "'.");
            }
            if (objectHeap.at(link.targetInstance).className != schema.targetClass) {
                report.isValid = false;
                report.violations.push_back("Type Mismatch: Link '" + link.associationName + "' expects target class '" + 
                    schema.targetClass + "' but got '" + objectHeap.at(link.targetInstance).className + "'.");
            }
        }

        // 2. Verify Multiplicity Invariants via Graph Degree Calculations
        for (const auto& [assocName, schema] : associationSchemas) {
            // Count targets per source instance
            std::unordered_map<std::string, size_t> targetsPerSource;
            // Count sources per target instance
            std::unordered_map<std::string, size_t> sourcesPerTarget;

            // Initialize all relevant objects in the heap with 0 links
            for (const auto& [instName, obj] : objectHeap) {
                if (obj.className == schema.sourceClass) targetsPerSource[instName] = 0;
                if (obj.className == schema.targetClass) sourcesPerTarget[instName] = 0;
            }

            // Accumulate active links
            for (const auto& link : activeLinks) {
                if (link.associationName == assocName) {
                    targetsPerSource[link.sourceInstance]++;
                    sourcesPerTarget[link.targetInstance]++;
                }
            }

            // Check Target Multiplicity (Instances of Target connected to each Source)
            for (const auto& [srcInst, count] : targetsPerSource) {
                if (!schema.targetMultiplicity.isInRange(count)) {
                    report.isValid = false;
                    report.violations.push_back("Multiplicity Violation on Association '" + assocName + "': Instance '" +
                        srcInst + " [" + schema.sourceClass + "]' has " + std::to_string(count) + 
                        " target links; expected " + schema.targetMultiplicity.toString());
                }
            }

            // Check Source Multiplicity (Instances of Source connected to each Target)
            for (const auto& [tgtInst, count] : sourcesPerTarget) {
                if (!schema.sourceMultiplicity.isInRange(count)) {
                    report.isValid = false;
                    report.violations.push_back("Multiplicity Violation on Association '" + assocName + "': Instance '" +
                        tgtInst + " [" + schema.targetClass + "]' has " + std::to_string(count) + 
                        " source links; expected " + schema.sourceMultiplicity.toString());
                }
            }
        }

        // 3. Detect Circular Pointer Chains (Depth-First Search for Directed Cycles)
        std::unordered_map<std::string, std::vector<std::string>> adjacencyList;
        for (const auto& link : activeLinks) {
            adjacencyList[link.sourceInstance].push_back(link.targetInstance);
        }

        std::unordered_map<std::string, int> visitState; // 0=Unvisited, 1=Visiting, 2=Visited
        auto dfsCycle = [&](auto& self, const std::string& current, std::vector<std::string>& path) -> void {
            visitState[current] = 1;
            path.push_back(current);

            for (const auto& neighbor : adjacencyList[current]) {
                if (visitState[neighbor] == 1) { // Back-edge detected!
                    std::string cycleMsg = "Cyclic pointer dependency detected: ";
                    for (const auto& node : path) cycleMsg += node + " -> ";
                    cycleMsg += neighbor;
                    report.warnings.push_back(cycleMsg);
                } else if (visitState[neighbor] == 0) {
                    self(self, neighbor, path);
                }
            }

            path.pop_back();
            visitState[current] = 2;
        };

        for (const auto& [instName, _] : objectHeap) {
            if (visitState[instName] == 0) {
                std::vector<std::string> path;
                dfsCycle(dfsCycle, instName, path);
            }
        }

        return report;
    }

    void printObjectDiagram() const {
        std::cout << "\n====================================================================\n";
        std::cout << "                 RUNTIME OBJECT DIAGRAM SNAPSHOT (t0)               \n";
        std::cout << "====================================================================\n";
        for (const auto& [name, obj] : objectHeap) {
            std::cout << "  <u>" << name << " : " << obj.className << "</u>\n";
            for (const auto& [attrName, attrVal] : obj.attributes) {
                std::cout << "    |-- " << attrName << " = ";
                std::visit([](auto&& arg) { std::cout << arg; }, attrVal);
                std::cout << "\n";
            }
        }
        std::cout << "\n  [Realized Links]:\n";
        for (const auto& link : activeLinks) {
            std::cout << "    (" << link.sourceInstance << ") ---[ " << link.associationName 
                      << " ]---> (" << link.targetInstance << ")\n";
        }
        std::cout << "====================================================================\n";
    }
};

int main() {
    ObjectGraphValidator engine;

    // 1. Define Static Schema (M1)
    engine.registerClass("Department", {"deptName", "budget"});
    engine.registerClass("Professor", {"facultyId", "rank"});

    // Department 1 <----> 1..* Professor
    // Source: Department, Multiplicity: 1..1
    // Target: Professor, Multiplicity: 1..*
    engine.registerAssociation({
        "Employs",
        "Department",
        "Professor",
        {1, 1},        // Each Professor belongs to exactly 1 Department
        {1, SIZE_MAX}  // Each Department employs at least 1 Professor (1..*)
    });

    // 2. Instantiate Runtime Object Graph (M0)
    std::cout << ">>> Injecting Test Scenario: 1 Department with 2 Professors (Valid)\n";
    engine.instantiateObject({"csDept", "Department", {{"deptName", std::string("Computer Science")}, {"budget", 1500000.0}}});
    engine.instantiateObject({"profKnuth", "Professor", {{"facultyId", 101}, {"rank", std::string("Full Professor")}}});
    engine.instantiateObject({"profHoare", "Professor", {{"facultyId", 102}, {"rank", std::string("Associate Professor")}}});

    engine.addLink("Employs", "csDept", "profKnuth");
    engine.addLink("Employs", "csDept", "profHoare");

    engine.printObjectDiagram();
    auto report1 = engine.validateConformance();
    std::cout << "Validation Result: " << (report1.isValid ? "PASS (Conforms to Class Schema)" : "FAIL") << "\n";

    // 3. Inject Multiplicity Invariant Violation
    std::cout << "\n>>> Injecting Invariant Violation: Creating Empty Department 'mathDept' (0 Professors)\n";
    engine.instantiateObject({"mathDept", "Department", {{"deptName", std::string("Mathematics")}, {"budget", 800000.0}}});
    
    auto report2 = engine.validateConformance();
    std::cout << "Validation Result: " << (report2.isValid ? "PASS" : "FAIL") << "\n";
    for (const auto& err : report2.violations) {
        std::cout << "  [VIOLATION] " << err << "\n";
    }

    return 0;
}
```

---

## 3-Tier Progressive Practice Suite

### Level 1: Guided Architectural Walkthrough & Step-by-Step Analysis

#### Problem Statement
Consider an e-commerce platform specification with the following class diagram association:
`[Order] 1 <---------- 0..* ----------> [Payment]`
The lead architect presents an object diagram snapshot taken during transaction checkout:
- Object 1: `<u>ord99:Order</u> [orderId = 99, status = "PENDING"]`
- Object 2: `<u>payA:Payment</u> [amount = 50.00, gateway = "Stripe"]`
- Object 3: `<u>payB:Payment</u> [amount = 50.00, gateway = "GiftCard"]`
- Link 1 connects `ord99` to `payA`.
- Link 2 connects `ord99` to `payB`.
- Object 4: `<u>payOrphan:Payment</u> [amount = 20.00, gateway = "PayPal"]` (with no links to any `Order`).

#### Architectural Analysis Questions
1. Does the presence of both `payA` and `payB` linked to `ord99` violate the `0..*` multiplicity?
2. Does `payOrphan` represent a permissible state under the class schema? Explain why or why not.

#### Guided Solution
1. **Multiplicity Analysis of `ord99`**: The target multiplicity on `Payment` is `0..*`. This denotes that an `Order` instance can be associated with zero, one, or arbitrarily many `Payment` instances. Linking two payments (`payA` and `payB`) to `ord99` is completely valid and models split-tender payment (e.g., $50 gift card + $50 credit card).
2. **Analysis of `payOrphan`**: The source multiplicity on `Order` is `1` (implicitly `1..1`). This enforces the invariant:
   $$\forall p \in \text{Payment}: \mathrm{deg}_{\text{Order}}(p) = 1$$
   Since `payOrphan` has zero links to any `Order` instance ($\mathrm{deg} = 0$), it is an invalid orphan object that violates the lower bound of multiplicity `1`. In production, this snapshot represents an illegal orphaned charge or a database referential integrity violation.

---

### Level 2: Scaffolded Troubleshooting / Bug-Fix Challenge

#### Challenge Description
An e-health hospital management system models patients, hospital rooms, and medical beds with the following class diagram invariants:
- `[HospitalRoom] 1 <---------- 1..4 ----------> [MedicalBed]`
- `[MedicalBed] 0..1 <---------- 0..1 ----------> [Patient]`

A QA team captures the following object diagram from the intensive care unit (ICU) runtime heap:

```
  +----------------------+             +----------------------+
  | <u>icu_rm1 : HospitalRoom</u> |             | <u>icu_rm2 : HospitalRoom</u> |
  +----------------------+             +----------------------+
       |            |
       | link1      | link2
       v            v
  +----------------------+             +----------------------+
  | <u>bedA : MedicalBed</u>    |             | <u>bedB : MedicalBed</u>    |
  +----------------------+             +----------------------+
       |            \                       |
       | link3       \ link4                | link5
       v              v                     v
  +----------------------+             +----------------------+
  | <u>pat1 : Patient</u>       |             | <u>pat2 : Patient</u>       |
  +----------------------+             +----------------------+
```

Identify all three distinct architectural and multiplicity violations present in this object diagram snapshot and explain the engineering remediations.

<details>
<summary>Click to view solution & walkthrough</summary>

#### Diagnostic Breakdown

1. **Violation 1: Multiplicity Lower Bound on `icu_rm2` (`1..4` requirement violated)**
   - *Symptom*: `icu_rm2` is an instantiated `HospitalRoom` with zero linked `MedicalBed` objects ($\mathrm{deg} = 0$).
   - *Rule*: The static association mandates `1..4` beds per room. An ICU room cannot exist in the domain model without at least one allocated bed.
   - *Fix*: Either allocate at least one bed to `icu_rm2` or adjust the class diagram multiplicity to `0..4` if unassigned empty rooms are legitimate lifecycle states.

2. **Violation 2: Multiplicity Upper Bound on `bedA` (`0..1` requirement violated)**
   - *Symptom*: `bedA` is linked via `link3` to `pat1` and via `link4` to `pat2`.
   - *Rule*: The association `[MedicalBed] 0..1 <--> 0..1 [Patient]` restricts each bed to at most one occupying patient.
   - *Hazard*: Physical impossibility and critical medical hazard—two patients cannot occupy the same single bed concurrently.
   - *Fix*: Sever `link4`; assign `pat2` to an unassigned bed such as `bedB`.

3. **Violation 3: Multiplicity Upper Bound on `pat2` (`0..1` requirement violated)**
   - *Symptom*: `pat2` is linked to both `bedA` (via `link4`) and `bedB` (via `link5`).
   - *Rule*: A single patient cannot occupy more than one bed simultaneously ($\mathrm{deg}_{\text{Bed}}(\text{pat2}) = 2$, exceeding the upper bound of 1).
   - *Fix*: Remove `link4` from `bedA` to `pat2`. `pat2` will then be uniquely and legally assigned to `bedB`.

</details>

---

### Level 3: Production C++17 Runtime Heap Graph Verification Engine

#### Challenge Description
Implement a production C++17 graph analyzer that models bidirectional association integrity. The engine must accept pairs of instances and verify the following:
1. **Referential Symmetry**: If instance $u$ references instance $v$ through association end $R_1$, then $v$ must reference $u$ through inverse association end $R_2$.
2. **Cardinality Verification**: Compute and flag instances violating dynamic upper/lower bound limits.
3. **Deadlock / Strong Ownership Cycle Detection**: Detect whether `shared_ptr` ownership cycles exist between objects without an intervening `weak_ptr` break.

<details>
<summary>Click to view production C++17 implementation</summary>

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <algorithm>
#include <sstream>

// Production-grade Bidirectional Reference and Invariant Checker
class HeapIntegrityVerifier {
public:
    struct InstanceNode {
        std::string id;
        std::string type;
        std::unordered_set<std::string> forwardPointers; // References to other instances
    };

private:
    std::unordered_map<std::string, InstanceNode> heap;
    std::unordered_map<std::string, std::pair<size_t, size_t>> typeDegreeConstraints; // Type -> {min, max}

public:
    void registerTypeConstraint(const std::string& type, size_t minDeg, size_t maxDeg) {
        typeDegreeConstraints[type] = {minDeg, maxDeg};
    }

    void addInstance(const std::string& id, const std::string& type) {
        heap[id] = {id, type, {}};
    }

    void addDirectedReference(const std::string& fromId, const std::string& toId) {
        if (heap.find(fromId) == heap.end() || heap.find(toId) == heap.end()) {
            throw std::runtime_error("Referential Integrity Failure: Invalid Instance ID");
        }
        heap[fromId].forwardPointers.insert(toId);
    }

    // Verifies whether references are reciprocal for symmetric bidirectional associations
    std::vector<std::string> verifyBidirectionalSymmetry() const {
        std::vector<std::string> defects;
        for (const auto& [uId, uNode] : heap) {
            for (const auto& vId : uNode.forwardPointers) {
                const auto& vNode = heap.at(vId);
                if (vNode.forwardPointers.find(uId) == vNode.forwardPointers.end()) {
                    defects.push_back("Asymmetry: Object [" + uId + " : " + uNode.type + 
                                      "] references [" + vId + " : " + vNode.type + 
                                      "], but inverse link is MISSING.");
                }
            }
        }
        return defects;
    }

    // Verifies multiplicity degree limits per instance
    std::vector<std::string> verifyMultiplicityBounds() const {
        std::vector<std::string> defects;
        for (const auto& [id, node] : heap) {
            auto it = typeDegreeConstraints.find(node.type);
            if (it != typeDegreeConstraints.end()) {
                size_t deg = node.forwardPointers.size();
                auto [minDeg, maxDeg] = it->second;
                if (deg < minDeg || deg > maxDeg) {
                    std::ostringstream oss;
                    oss << "Cardinality Violation: [" << id << " : " << node.type 
                        << "] has " << deg << " connections. Required: [" 
                        << minDeg << ".." << maxDeg << "]";
                    defects.push_back(oss.str());
                }
            }
        }
        return defects;
    }

    // Tarjan's Strongly Connected Components (SCC) to detect reference cycles
    std::vector<std::vector<std::string>> findReferenceCycles() const {
        std::unordered_map<std::string, int> indices;
        std::unordered_map<std::string, int> lowlinks;
        std::unordered_set<std::string> onStack;
        std::vector<std::string> stack;
        std::vector<std::vector<std::string>> sccs;
        int index = 0;

        auto strongConnect = [&](auto& self, const std::string& v) -> void {
            indices[v] = index;
            lowlinks[v] = index;
            index++;
            stack.push_back(v);
            onStack.insert(v);

            for (const auto& w : heap.at(v).forwardPointers) {
                if (indices.find(w) == indices.end()) {
                    self(self, w);
                    lowlinks[v] = std::min(lowlinks[v], lowlinks[w]);
                } else if (onStack.find(w) != onStack.end()) {
                    lowlinks[v] = std::min(lowlinks[v], indices[w]);
                }
            }

            if (lowlinks[v] == indices[v]) {
                std::vector<std::string> scc;
                std::string w;
                do {
                    w = stack.back();
                    stack.pop_back();
                    onStack.erase(w);
                    scc.push_back(w);
                } while (w != v);

                if (scc.size() > 1) {
                    sccs.push_back(scc);
                }
            }
        };

        for (const auto& [id, _] : heap) {
            if (indices.find(id) == indices.end()) {
                strongConnect(strongConnect, id);
            }
        }
        return sccs;
    }
};

int main() {
    HeapIntegrityVerifier verifier;

    // Constraints: Order must link to 1..3 Payment items
    verifier.registerTypeConstraint("Order", 1, 3);
    verifier.registerTypeConstraint("Payment", 1, 1);

    verifier.addInstance("ord_101", "Order");
    verifier.addInstance("pay_A", "Payment");
    verifier.addInstance("pay_B", "Payment");

    // Establish bidirectional references
    verifier.addDirectedReference("ord_101", "pay_A");
    verifier.addDirectedReference("pay_A", "ord_101");

    verifier.addDirectedReference("ord_101", "pay_B");
    // Deliberately omit pay_B -> ord_101 to test asymmetry detection!

    std::cout << "--- 1. Testing Symmetry ---\n";
    auto defects = verifier.verifyBidirectionalSymmetry();
    for (const auto& d : defects) std::cout << "  " << d << "\n";

    std::cout << "\n--- 2. Testing Multiplicities ---\n";
    auto bounds = verifier.verifyMultiplicityBounds();
    for (const auto& b : bounds) std::cout << "  " << b << "\n";

    std::cout << "\n--- 3. Testing Reference Cycles ---\n";
    auto cycles = verifier.findReferenceCycles();
    for (const auto& scc : cycles) {
        std::cout << "  Cycle detected between: ";
        for (const auto& node : scc) std::cout << node << " ";
        std::cout << "\n";
    }

    return 0;
}
```

</details>

---

## Pedagogical Review Questions & Examination Problems

1. **Formal Metamodel Distinctions**: Why does UML 2.5 forbid multiplicity specifications (e.g., `0..*`, `1..1`) on links in an object diagram? How does an observer determine if multiplicity rules are obeyed when inspecting an object diagram?
2. **State Vector Representation**: Write the formal mathematical state tuple $\mathcal{S}(t_0)$ for an instance `<u>authSvc:AuthenticationService</u>` with attributes `tokenExpirySec = 3600`, `maxRetries = 5`, and `state = ACTIVE`.
3. **OCL Invariant Verification**: Given an OCL invariant `context Department inv: self.budget >= self.professors.salary->sum()`, describe how an object diagram provides a constructive refutation when a department's budget is overdrawn.
