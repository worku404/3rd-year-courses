# Unit 4 — Structured Analysis, Hierarchical Data Flow Modeling & Logic Specifications
## Lesson 1 — The Three Orthogonal Views of Structured Analysis & Hierarchical DFDs (Levels 0, 1, 2)

### 1. Foundations of Structured Analysis: The Three Orthogonal Views

Before the advent of modern object-oriented paradigms, software engineering was revolutionized in the late 1970s and 1980s by **Structured Analysis** (pioneered by Tom DeMarco, Edward Yourdon, Chris Gane, and Trish Sarson). Structured Analysis provides a systematic, top-down, functional decomposition methodology that models complex software architectures strictly as a network of data transformations.

To achieve complete architectural comprehension, Structured Analysis models any software system across **three orthogonal views**:

```
+---------------------------------------------------------------------------------------------------+
|                        THE THREE ORTHOGONAL VIEWS OF STRUCTURED ANALYSIS                         |
+---------------------------------------------------------------------------------------------------+
| 1. THE FUNCTIONAL VIEW   : Modeled by DATA FLOW DIAGRAMS (DFDs).                                  |
|                            Answers: "What work is done? How is data transformed from input to     |
|                            output across the system boundaries?"                                  |
|                                                                                                   |
| 2. THE DATA VIEW         : Modeled by ENTITY RELATIONSHIP DIAGRAMS (ERDs) & DATA DICTIONARIES.    |
|                            Answers: "What persistent information structures exist? What are their |
|                            cardinalities, attributes, and relational foreign-key associations?"   |
|                                                                                                   |
| 3. THE DYNAMIC VIEW      : Modeled by STATE TRANSITION DIAGRAMS (STDs) & CONTROL SPECIFICATIONS.  |
|                            Answers: "When do events occur? Under what discrete triggers and       |
|                            timing conditions does the system alter its operational states?"       |
+---------------------------------------------------------------------------------------------------+
```

These three views are strictly complementary. A Data Flow Diagram shows *what* processes transform data, but cannot define the relational schema of a record (governed by the Data View) nor the event sequence that wakes up an idle daemon (governed by the Dynamic View).

---

### 2. Data Flow Diagrams (DFDs) vs. Program Flowcharts

A ubiquitous conceptual error among novice analysts is confusing a **Data Flow Diagram (DFD)** with a **Program Flowchart**. While both use graphical boxes and connecting lines, they represent fundamentally opposite computer science abstractions:

| Dimension | Data Flow Diagram (DFD) | Program Flowchart |
| :--- | :--- | :--- |
| **Primary Focus** | The flow, transformation, and storage of **Data**. | The sequence of **Control Execution** and instruction pointers. |
| **Temporal Concept** | **Asynchronous & Concurrent:** Multiple processes in a DFD can execute in parallel whenever input data arrives. | **Strictly Sequential:** Exactly one instruction executes at time $t$; follows program counter ($\text{PC}$). |
| **Decisions & Loops** | **Omitted:** A DFD does *not* display `IF-ELSE` branches or `WHILE` loops; internal branching is encapsulated in Process Specifications (P-Specs). | **Explicit:** Diamond symbols explicitly model binary branching conditions and loop cycles. |
| **Component Types** | External Entities, Processes, Data Stores, Data Flows. | Start/Stop terminals, Operations, Decision Diamonds, Subroutines. |
| **System Scope** | Can model an entire multi-nation banking ecosystem down to a database write. | Models a specific algorithmic function or module's internal code logic. |

---

### 3. Canonical DFD Elements & Graphical Notations

A formal Data Flow Diagram is constructed using exactly **four fundamental building blocks**. In software engineering history, two major graphic standards exist: **DeMarco & Yourdon** (using circles for processes) and **Gane & Sarson** (using rounded rectangles with a top header bar).

{{ media:sam-dfd-hierarchy-diagram }}

```
+---------------------------------------------------------------------------------------------------+
|                                  THE FOUR CANONICAL DFD ELEMENTS                                  |
|                                                                                                   |
|  1. EXTERNAL ENTITY (TERMINATOR / SOURCE / SINK):                                                 |
|     +-----------------------+     * Outside the boundary of the system being modeled.             |
|     |  CUSTOMER / SENSOR    |     * Sources inject raw data into the system.                      |
|     +-----------------------+     * Sinks receive transformed outputs, notifications, or reports. |
|                                                                                                   |
|  2. PROCESS (BUBBLE / FUNCTIONAL TRANSFORM):                                                      |
|     DeMarco/Yourdon:  ( 2.1 )     * Action verb + Object phrase (e.g., "Verify Credit Card").     |
|     Gane/Sarson:      +-----+     * Takes incoming data flows, transforms them according to       |
|                       | 2.1 |       business logic, and emits output data flows.                  |
|                       +-----+                                                                     |
|                                                                                                   |
|  3. DATA STORE (PERSISTENT REPOSITORY):                                                           |
|     DeMarco/Yourdon:  =======     * Represents persistent data at rest (RDBMS table, disk file,   |
|                       D1 Pat.       memory cache, physical filing cabinet).                       |
|     Gane/Sarson:      +--+--+     * Open-ended rectangle labeled with store identifier (e.g., D1).|
|                       |D1|..|                                                                     |
|                                                                                                   |
|  4. DATA FLOW (DIRECTED ARROW):                                                                   |
|     ----------------------->      * Directed vector named with a singular noun phrase.            |
|          Valid_Payload            * Represents data packets in motion along a pipeline.           |
+---------------------------------------------------------------------------------------------------+
```

---

### 4. Hierarchical Decomposition: Levels 0, 1, and 2

To prevent visual clutter and manage cognitive load, Structured Analysis enforces **hierarchical leveling**. A massive enterprise architecture containing 5,000 discrete functions is decomposed top-down across multiple abstraction tiers:

```
+---------------------------------------------------------------------------------------------------+
|                        THE DFD HIERARCHICAL DECOMPOSITION PIPELINE                                |
|                                                                                                   |
|  [ LEVEL 0: CONTEXT DIAGRAM ]                                                                     |
|  * Single master process (Node 0.0) representing the total system.                                |
|  * All External Entities (Terminators) and net boundary data flows.                               |
|  * NO INTERNAL DATA STORES ALLOWED AT LEVEL 0!                                                    |
|                                     |                                                             |
|                                     v                                                             |
|  [ LEVEL 1: SUBSYSTEM OVERVIEW ]                                                                  |
|  * Explodes Process 0.0 into 3 to 7 major functional subsystems (Processes 1.0, 2.0, 3.0, etc.).  |
|  * First appearance of internal Data Stores (D1, D2, D3) connecting the subsystems.               |
|  * Exposes inter-subsystem data pipelines.                                                        |
|                                     |                                                             |
|                                     v                                                             |
|  [ LEVEL 2: DEEP DIVE PRIMITIVES ]                                                                |
|  * Explodes a single Level 1 process (e.g., Process 2.0) into granular child nodes:               |
|    (Processes 2.1, 2.2, 2.3, 2.4).                                                                |
|  * Reaches Functional Primitives: Atomic processes that cannot be decomposed further without      |
|    algorithmic logic. Formally specified via Process Specifications (P-Specs).                    |
+---------------------------------------------------------------------------------------------------+
```

#### 4.1 Numbering Conventions
- Level 0: The single root process is numbered `0` or `0.0`.
- Level 1: Subsystems are numbered with single integers: `1.0, 2.0, 3.0, 4.0`.
- Level 2: Children of process `2.0` are numbered `2.1, 2.2, 2.3, 2.4`.
- Level 3: Children of process `2.3` are numbered `2.3.1, 2.3.2, 2.3.3`.

---

### 5. Flow Conservation Invariants & DFD Anti-Patterns

A valid DFD must adhere to mathematical conservation laws analogous to Kirchhoff's Current Laws in electrical engineering. Any violation constitutes a critical architectural defect.

#### 5.1 The Three Fatal Process Anti-Patterns
1. **The Black Hole:** A process has incoming data flows, but **zero outgoing data flows**. In physical and information systems, data cannot simply vanish from existence without producing an output or mutating a data store. If a process does not emit an output, it serves no operational purpose.
2. **The Miracle Source:** A process emits outgoing data flows, but has **zero incoming data flows**. A process cannot spontaneously generate information out of the quantum vacuum without receiving an input stimulus or reading a persistent store.
3. **The Grey Hole:** A process receives inputs, and produces outputs, but the output data elements **could not possibly be derived from the inputs**. For example, a process receives an input flow containing only `Student_ID`, but emits an output flow containing `Flight_Manifest_Passenger_List + FAA_Security_Clearance`.

```
    [ BLACK HOLE ]              [ MIRACLE SOURCE ]               [ GREY HOLE ]
    
    Data_In_1 ---> ( 1.1 )      ( 1.2 ) ---> Data_Out_1         StudentID ---> ( 1.3 ) ---> Full_FAA_Record
    Data_In_2 ---> (     )      (     ) ---> Data_Out_2                       (     )
           (NO OUTPUT!)                (NO INPUT!)                      (Output impossible from input!)
```

#### 5.2 Illegal Direct Transfers
- **Direct Store-to-Store Flow ($D_1 \longrightarrow D_2$):** Strictly prohibited! A data store is a passive resting place for data; it has no execution CPU or algorithm to read from itself and write to another store. An active **Process node** must mediate all data movements between stores.
- **Direct Entity-to-Store Flow ($E_1 \longrightarrow D_1$):** Strictly prohibited! External entities reside outside the system boundary. Permitting external actors to write directly into internal data stores bypasses security validation, format sanity checks, and audit logging. An intermediary **Process** must ingest, sanitize, and persist the entity's data.

#### 5.3 The Invariant Balancing Rule (Horizontal & Vertical Consistency)
> **The DFD Balancing Invariant:**
> *All net input data flows entering a parent process node at Level $N$, and all net output data flows exiting that parent node, must appear at the boundary of the child Level $N+1$ diagram.*

If Process `2.0` at Level 1 receives input `Order_Form` and outputs `Invoice` and `Shipping_Label`, then the child Level 2 DFD (decomposing Process `2.0` into `2.1, 2.2, 2.3`) must have `Order_Form` as its net input from the external boundary, and must emit `Invoice` and `Shipping_Label` as its net outputs to the boundary.

---

### 6. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

An architectural review committee is auditing a draft Level 1 DFD for an automated Pharmacy Dispensing and Inventory Control System. The diagram contains the following five process nodes:

1. **Process 1.0 (Ingest Electronic Prescription):** Receives `Prescription_Payload` from `Clinic_EMR_System` (External Entity). Emits `Validated_Rx` to Data Store `D1: Active_Prescriptions`.
2. **Process 2.0 (Check Medication Interactions):** Receives `Validated_Rx` from `D1: Active_Prescriptions`. Emits `Interaction_Warning` to `Pharmacist_Console`. Has zero other inputs or outputs.
3. **Process 3.0 (Dispensing Actuator Control):** Has zero input flows. Emits `Robotic_Actuator_Pulse` to `Pill_Dispenser_Hardware`.
4. **Process 4.0 (Audit Compliance Logger):** Receives `Dispense_Timestamp` from `Process 3.0` and `Patient_ID` from `Process 1.0`. Has zero outgoing flows.
5. **Data Flow: Data Store `D1: Active_Prescriptions` has a direct arrow connected to Data Store `D2: Historical_Archives`.**

**Architectural Audit Tasks:**
1. Identify all structural anti-patterns and DFD invariant violations across these nodes.
2. Classify each defect (Black Hole, Miracle Source, Illegal Direct Transfer, etc.).
3. Provide the corrected architectural flow connections to make the system mathematically balanced and sound.

<details>
<summary>Click to view Level 1 Solution & Architectural Audit</summary>

##### 1. Identified Violations & Classifications:
- **Process 3.0 is a MIRACLE SOURCE:** It emits `Robotic_Actuator_Pulse` to physical hardware with zero incoming data flows. A robotic dispensing actuator cannot fire without receiving an approved dispensing order command!
- **Process 4.0 is a BLACK HOLE:** It receives `Dispense_Timestamp` and `Patient_ID`, but produces no outgoing data flows and does not write to a Data Store. Data enters the node and vanishes.
- **Direct Store-to-Store Flow ($D_1 \longrightarrow D_2$):** Data Store `D1` connects directly to Data Store `D2`. This violates the fundamental axiom that data stores are passive. An archival process (e.g., `Process 5.0: Archive_Dispensed_Prescriptions`) is required to read expired records from `D1` and append them to `D2`.

##### 2. Corrected Architectural Topology:
1. **Fix Miracle Source on Process 3.0:** Add an incoming data flow `Approved_Dispense_Command` from `Process 2.0` (or `Pharmacist_Console` sign-off) into `Process 3.0`.
2. **Fix Black Hole on Process 4.0:** Direct the output of `Process 4.0` as an append flow `Audit_Record` into Data Store `D3: Regulatory_Audit_Log`.
3. **Fix Illegal Store-to-Store Transfer:** Introduce `Process 5.0 (Archive Historical Records)`. `Process 5.0` reads `Archivable_Rx` from `D1`, marks status as archived, and writes `Archived_Record` into `D2`.

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The DFD Graph & Balancing Linter

A software engineering team built a Python graph validator to verify DFD topologies before publishing system specifications. However, the validator is crashing on recursive multi-level parent-child inspections and fails to detect Grey Holes (processes where output fields do not exist in input schemas).

Examine the flawed script below:

```python
# FLAWED DFD VALIDATOR (PYTHON)
def validate_dfd_graph(processes, data_stores, flows):
    errors = []

    # Check 1: Detect Black Holes and Miracle Sources
    for p_id in processes:
        # BUG: Fails to distinguish between external entity flows, store flows,
        # and inter-process flows!
        in_flows = [f for f in flows if f["target"] == p_id]
        out_flows = [f for f in flows if f["source"] == p_id]

        if len(in_flows) == 0:
            errors.append(f"Miracle Source at Process {p_id}")
        if len(out_flows) == 0:
            errors.append(f"Black Hole at Process {p_id}")

    # Check 2: Detect Illegal Store-to-Store Transfers
    for f in flows:
        # BUG: Crashes with KeyError if source or target is not in data_stores dict!
        if f["source"] in data_stores and f["target"] in data_stores:
            errors.append(f"Illegal Store-to-Store flow: {f['id']}")

    # BUG: Completely misses Grey Holes! Does not compare the data element attributes
    # in incoming flows vs. outgoing flows!
    # BUG: Completely misses DFD Level Balancing (Parent vs. Child net boundary flows)!

    return errors
```

**Debug Assignment:**
1. Identify all runtime exceptions, false alarms, and architectural gaps in this script.
2. Implement schema-aware verification to detect **Grey Holes** by asserting:
   $$\text{Attributes}(\text{OutFlows}) \subseteq \left( \bigcup \text{Attributes}(\text{InFlows}) \cup \text{Attributes}(\text{ReadStores}) \cup \text{DerivedCalculations} \right)$$
3. Implement a formal recursive **Parent-Child Level Balancing Validator**.

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. Identified Flaws in the Original Script:
- **Missing Set Membership Guards:** Checking `f["source"] in data_stores` crashes if `data_stores` is a dictionary or list where types are mismatched.
- **Ignored Entity Validation:** External entities writing directly into data stores were not validated.
- **Omission of Grey Hole Attribute Tracking:** Real DFD validation requires inspecting the actual data payload attributes moving along the flows. If `InFlow` has `{id}` and `OutFlow` has `{id, ssn, salary, blood_type}`, a Grey Hole must be raised unless a data store read supplied the missing attributes.
- **Total Absence of Level Balancing:** The script had no concept of hierarchical nesting (matching Level 1 parent input/output vectors to Level 2 child boundary vectors).

##### 2. Corrected Production Implementation:

```python
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional

@dataclass
class Flow:
    id: str
    source_id: str
    target_id: str
    payload_fields: Set[str]

@dataclass
class ProcessNode:
    id: str
    name: str
    parent_process_id: Optional[str] = None
    derived_fields: Set[str] = field(default_factory=set)

class ProductionDFDValidator:
    def __init__(
        self,
        processes: Dict[str, ProcessNode],
        entities: Set[str],
        data_stores: Set[str],
        flows: List[Flow]
    ):
        self.processes = processes
        self.entities = entities
        self.data_stores = data_stores
        self.flows = flows

    def audit_graph_integrity(self) -> List[str]:
        defects = []

        # 1. Illegal Direct Transfers
        for f in self.flows:
            # Store-to-Store illegal flow
            if f.source_id in self.data_stores and f.target_id in self.data_stores:
                defects.append(f"[ILLEGAL STORE-TO-STORE] Flow '{f.id}' connects Store '{f.source_id}' to Store '{f.target_id}'")
            # Entity-to-Store illegal flow
            if f.source_id in self.entities and f.target_id in self.data_stores:
                defects.append(f"[ILLEGAL ENTITY-TO-STORE] Flow '{f.id}' connects Entity '{f.source_id}' directly to Store '{f.target_id}'")

        # 2. Black Holes, Miracle Sources, and Grey Holes
        for p_id, proc in self.processes.items():
            in_flows = [f for f in self.flows if f.target_id == p_id]
            out_flows = [f for f in self.flows if f.source_id == p_id]

            if len(in_flows) == 0:
                defects.append(f"[MIRACLE SOURCE] Process '{p_id}' ({proc.name}) has zero incoming flows.")
            if len(out_flows) == 0:
                defects.append(f"[BLACK HOLE] Process '{p_id}' ({proc.name}) has zero outgoing flows.")

            # Grey Hole Check: Verify outgoing payload fields exist in incoming flows or local derivations
            available_fields = set(proc.derived_fields)
            for inf in in_flows:
                available_fields.update(inf.payload_fields)

            for outf in out_flows:
                missing_fields = outf.payload_fields - available_fields
                if missing_fields:
                    defects.append(
                        f"[GREY HOLE] Process '{p_id}' emits field(s) {missing_fields} in flow '{outf.id}' "
                        f"that never entered via input flows or algorithmic derivation!"
                    )

        return defects

    def verify_parent_child_balancing(self, parent_id: str, child_process_ids: Set[str]) -> List[str]:
        # Asserts that net input and output flows of parent match boundary flows of children
        balancing_defects = []

        # Parent net boundary flows
        parent_in_flows = {f.id: f.payload_fields for f in self.flows if f.target_id == parent_id}
        parent_out_flows = {f.id: f.payload_fields for f in self.flows if f.source_id == parent_id}

        # Child net boundary flows (flows crossing into/out of child cluster from outside)
        child_in_flows = {}
        child_out_flows = {}

        for f in self.flows:
            if f.target_id in child_process_ids and f.source_id not in child_process_ids:
                child_in_flows[f.id] = f.payload_fields
            if f.source_id in child_process_ids and f.target_id not in child_process_ids:
                child_out_flows[f.id] = f.payload_fields

        # Compare Inputs
        if set(parent_in_flows.keys()) != set(child_in_flows.keys()):
            balancing_defects.append(
                f"[UNBALANCED INPUTS] Parent '{parent_id}' inputs {set(parent_in_flows.keys())} "
                f"do not match Child boundary inputs {set(child_in_flows.keys())}"
            )

        # Compare Outputs
        if set(parent_out_flows.keys()) != set(child_out_flows.keys()):
            balancing_defects.append(
                f"[UNBALANCED OUTPUTS] Parent '{parent_id}' outputs {set(parent_out_flows.keys())} "
                f"do not match Child boundary outputs {set(child_out_flows.keys())}"
            )

        return balancing_defects
```

</details>

---

#### Level 3 — High-Scale System Design: Graph-Based DFD Consistency & Flow Conservation Validator in C++

Design and implement a complete, production-grade C++17 **DFD Graph Integrity & Flow Conservation Engine**. The engine must:
1. Represent a multi-tier DFD architecture as a **Directed Hypergraph** with typed nodes (`ENTITY`, `PROCESS`, `DATA_STORE`) and attribute-tagged vectors (`DATA_FLOW`).
2. Implement automated algorithms to detect:
   - **Black Holes:** In-degree $\ge 1$, Out-degree $= 0$.
   - **Miracle Sources:** In-degree $= 0$, Out-degree $\ge 1$.
   - **Grey Holes:** Set difference:
     $$\text{Fields}(\text{OutFlow}) \setminus \left( \bigcup \text{Fields}(\text{InFlow}) \cup \text{DerivedFields} \right) \neq \emptyset$$
   - **Illegal Direct Flows:** Data Store $\to$ Data Store, or Entity $\to$ Data Store.
3. Implement a **Hierarchical Level Balancing Verifier**:
   - Compare the net boundary flows of a Level 1 parent node against the aggregated boundary flows of its decomposed Level 2 child nodes.
4. Output a comprehensive diagnostic compliance audit report.

<details>
<summary>Click to view complete C++17 DFD Integrity Engine</summary>

```cpp
/**
 * ============================================================================
 * DATA FLOW DIAGRAM (DFD) INTEGRITY & CONSERVATION ENGINE (C++17)
 * ============================================================================
 * Implements:
 * 1. Directed Typed Hypergraph Model for DFD Elements.
 * 2. Conservation of Flow Validation (Black Hole, Miracle Source, Grey Hole).
 * 3. Topological Anti-Pattern Detection (Illegal Direct Transfers).
 * 4. Hierarchical Multi-Level Parent-Child Balancing Verification.
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
// DOMAIN TYPED NODES & FLOW DATA STRUCTURES
// ============================================================================

enum class NodeType {
    EXTERNAL_ENTITY,
    PROCESS_NODE,
    DATA_STORE
};

struct DfdNode {
    std::string id;
    std::string name;
    NodeType type;
    std::string parent_process_id; // For hierarchical decomposition
    std::unordered_set<std::string> derived_fields; // Computational attributes
};

struct DataFlow {
    std::string id;
    std::string name;
    std::string source_id;
    std::string target_id;
    std::unordered_set<std::string> payload_fields;
};

// ============================================================================
// DFD GRAPH ENGINE
// ============================================================================

class DfdGraphEngine {
private:
    std::unordered_map<std::string, DfdNode> nodes;
    std::vector<DataFlow> flows;

public:
    void add_node(const DfdNode& node) {
        nodes[node.id] = node;
    }

    void add_flow(const DataFlow& flow) {
        flows.push_back(flow);
    }

    void audit_graph_integrity() const {
        std::cout << "\n================================================================================\n";
        std::cout << "                 DATA FLOW DIAGRAM (DFD) TOPOLOGY AUDIT REPORT\n";
        std::cout << "================================================================================\n";

        std::vector<std::string> defects;

        // 1. Audit Illegal Direct Flows
        for (const auto& f : flows) {
            auto src_it = nodes.find(f.source_id);
            auto dst_it = nodes.find(f.target_id);

            if (src_it == nodes.end() || dst_it == nodes.end()) {
                defects.push_back("[DANGLING FLOW] Flow '" + f.id + "' references non-existent node ID!");
                continue;
            }

            const auto& src = src_it->second;
            const auto& dst = dst_it->second;

            // Direct Store to Store
            if (src.type == NodeType::DATA_STORE && dst.type == NodeType::DATA_STORE) {
                defects.push_back("[ILLEGAL STORE-TO-STORE] Flow '" + f.id + "': Data Store '" + 
                                  src.id + "' cannot directly flow to Store '" + dst.id + "' without an active Process.");
            }

            // Direct Entity to Store
            if (src.type == NodeType::EXTERNAL_ENTITY && dst.type == NodeType::DATA_STORE) {
                defects.push_back("[ILLEGAL ENTITY-TO-STORE] Flow '" + f.id + "': Entity '" + 
                                  src.id + "' cannot write directly to Store '" + dst.id + "' without validating Process.");
            }
        }

        // 2. Audit Process Nodes (Conservation of Flow)
        for (const auto& [id, node] : nodes) {
            if (node.type != NodeType::PROCESS_NODE) continue;

            std::vector<DataFlow> incoming;
            std::vector<DataFlow> outgoing;

            for (const auto& f : flows) {
                if (f.target_id == id) incoming.push_back(f);
                if (f.source_id == id) outgoing.push_back(f);
            }

            // Miracle Source Detection
            if (incoming.empty() && !outgoing.empty()) {
                defects.push_back("[MIRACLE SOURCE] Process '" + id + "' (" + node.name + 
                                  ") produces output with ZERO incoming data flows!");
            }

            // Black Hole Detection
            if (!incoming.empty() && outgoing.empty()) {
                defects.push_back("[BLACK HOLE] Process '" + id + "' (" + node.name + 
                                  ") absorbs inputs but emits ZERO outgoing data flows!");
            }

            // Grey Hole Attribute Tracking
            std::unordered_set<std::string> available_fields = node.derived_fields;
            for (const auto& inf : incoming) {
                for (const auto& fld : inf.payload_fields) {
                    available_fields.insert(fld);
                }
            }

            for (const auto& outf : outgoing) {
                for (const auto& req_field : outf.payload_fields) {
                    if (available_fields.find(req_field) == available_fields.end()) {
                        defects.push_back("[GREY HOLE] Process '" + id + "' emits field '" + req_field + 
                                          "' in flow '" + outf.id + "' which never entered via inputs!");
                    }
                }
            }
        }

        std::cout << "Total Nodes Analyzed : " << nodes.size() << "\n";
        std::cout << "Total Flows Analyzed : " << flows.size() << "\n";
        std::cout << "Total Violations     : " << defects.size() << "\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        if (defects.empty()) {
            std::cout << ">>> DFD TOPOLOGY STATUS: PASSED (100% CONSERVATION OF FLOW)\n";
        } else {
            std::cout << ">>> DFD TOPOLOGY STATUS: FAILED (STRUCTURAL DEFECTS FOUND):\n";
            for (const auto& d : defects) {
                std::cout << "  * " << d << "\n";
            }
        }
        std::cout << "================================================================================\n";
    }

    void verify_level_balancing(const std::string& parent_process_id, 
                                const std::unordered_set<std::string>& child_node_ids) const {
        std::cout << "\n>>> VERIFYING DFD LEVEL BALANCING: Parent [" << parent_process_id << "] <<<\n";

        std::unordered_set<std::string> parent_inputs;
        std::unordered_set<std::string> parent_outputs;

        for (const auto& f : flows) {
            if (f.target_id == parent_process_id) parent_inputs.insert(f.name);
            if (f.source_id == parent_process_id) parent_outputs.insert(f.name);
        }

        std::unordered_set<std::string> child_boundary_inputs;
        std::unordered_set<std::string> child_boundary_outputs;

        for (const auto& f : flows) {
            bool src_in_child = (child_node_ids.find(f.source_id) != child_node_ids.end());
            bool dst_in_child = (child_node_ids.find(f.target_id) != child_node_ids.end());

            // Enters child cluster from outside
            if (dst_in_child && !src_in_child) child_boundary_inputs.insert(f.name);
            // Exits child cluster to outside
            if (src_in_child && !dst_in_child) child_boundary_outputs.insert(f.name);
        }

        bool in_balanced = (parent_inputs == child_boundary_inputs);
        bool out_balanced = (parent_outputs == child_boundary_outputs);

        std::cout << "Parent Inputs        : " << parent_inputs.size() << " | Child Boundary Inputs : " << child_boundary_inputs.size() << "\n";
        std::cout << "Parent Outputs       : " << parent_outputs.size() << " | Child Boundary Outputs: " << child_boundary_outputs.size() << "\n";
        std::cout << "Balancing Verdict    : " << (in_balanced && out_balanced ? "PASSED (PERFECTLY BALANCED)" : "FAILED (UNBALANCED FLOWS)") << "\n";
    }
};

// ============================================================================
// SIMULATION HARNESS
// ============================================================================

int main() {
    DfdGraphEngine engine;

    // 1. External Entities
    engine.add_node({"ENT-PATIENT", "Hospital Patient", NodeType::EXTERNAL_ENTITY, ""});
    engine.add_node({"ENT-PHARMACY", "Pharmacy Dispenser", NodeType::EXTERNAL_ENTITY, ""});

    // 2. Data Stores
    engine.add_node({"D1-PATIENTS", "Patient Records Table", NodeType::DATA_STORE, ""});
    engine.add_node({"D2-ARCHIVES", "Cold Storage Archives", NodeType::DATA_STORE, ""});

    // 3. Valid Process Node
    engine.add_node({"P-1.0", "Ingest Prescription", NodeType::PROCESS_NODE, "", {"Validation_Timestamp"}});

    // 4. Defective Process Nodes for Testing the Engine
    // Miracle Source (Node P-2.0 has zero inputs)
    engine.add_node({"P-2.0", "Generate Miracle Invoices", NodeType::PROCESS_NODE, "", {}});

    // Black Hole (Node P-3.0 has zero outputs)
    engine.add_node({"P-3.0", "Swallow Audit Logs", NodeType::PROCESS_NODE, "", {}});

    // Grey Hole (Node P-4.0 emits fields that never entered via inputs)
    engine.add_node({"P-4.0", "Compute Credit Score", NodeType::PROCESS_NODE, "", {}});

    // 5. Connect Data Flows
    // Valid flow: Patient -> P-1.0
    engine.add_flow({"F1", "Prescription_Order", "ENT-PATIENT", "P-1.0", {"Patient_ID", "Drug_Code", "Dosage"}});
    // Valid flow: P-1.0 -> D1-PATIENTS
    engine.add_flow({"F2", "Persist_Rx", "P-1.0", "D1-PATIENTS", {"Patient_ID", "Drug_Code", "Validation_Timestamp"}});

    // Defect A: Miracle Source (P-2.0 emits without input)
    engine.add_flow({"F3", "Spontaneous_Invoice", "P-2.0", "ENT-PHARMACY", {"Invoice_ID", "Total_Due"}});

    // Defect B: Black Hole (P-3.0 absorbs input, emits nothing)
    engine.add_flow({"F4", "Audit_Stream", "P-1.0", "P-3.0", {"Validation_Timestamp"}});

    // Defect C: Grey Hole (P-4.0 gets only Patient_ID, but emits SSN and FICO_Score!)
    engine.add_flow({"F5", "Lookup_Req", "P-1.0", "P-4.0", {"Patient_ID"}});
    engine.add_flow({"F6", "Credit_Report", "P-4.0", "ENT-PHARMACY", {"Patient_ID", "SSN", "FICO_Score"}});

    // Defect D: Illegal Direct Store-to-Store transfer!
    engine.add_flow({"F7", "Direct_Archive_Sync", "D1-PATIENTS", "D2-ARCHIVES", {"Patient_ID"}});

    // Run Full Topological Integrity Audit
    engine.audit_graph_integrity();

    // Verify Level Balancing Example
    engine.verify_level_balancing("P-1.0", {"P-1.1", "P-1.2"});

    return 0;
}
```

</details>

---

### 7. Reference Video Lecture

{{ media:dfd-structured-analysis-video }}

In this video by Crash Course Computer Science, foundational software engineering principles, system modularization, and architectural data flow transformations are explored in depth.
