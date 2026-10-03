# Lesson 3 — Activity & Communication Diagrams: Swimlanes, Fork/Join Concurrency & Message Topologies

## Executive Summary & Academic Orientation

In software systems engineering, complex computational logic manifests both as data-transforming algorithmic workflows and as collaborative object networks. While State Machine diagrams model event-driven state transitions of individual components, and Sequence diagrams model time-ordered message passing, software engineers require two specialized behavioral views to complete the dynamic modeling spectrum:

1. **Activity Diagrams**: Flowchart and Petri net extensions within the **UML 2.5 Specification** that model procedural logic, concurrent branching, object transformations, and organizational responsibilities through **Swimlanes (Activity Partitions)**.
2. **Communication Diagrams** (formerly designated as **Collaboration Diagrams** in UML 1.x): Structural-behavioral hybrid models that superimpose sequenced message flows directly onto static object association links, highlighting architectural network topology over chronological progression.

This lesson explores the formal token flow semantics of UML 2.5 activity networks, mathematical Petri net foundations, fork/join concurrency barriers, object flow pin bindings, nested hierarchical sequence numbering (e.g., $1.2.1$), and implements an industrial C++17 workflow engine with Petri net token mechanics.

```
+-------------------------------------------------------------------------+
|                  UML 2.5 BEHAVIORAL MODELING SPECTRUM                   |
|                                                                         |
|  [ Workflow & Token Flow ]              [ Structural Object Flow ]      |
|     Activity Diagrams                      Communication Diagrams       |
|     - Action Nodes (Pills)                 - Object Nodes               |
|     - Control Flows (Arrows)               - Association Links          |
|     - Fork/Join Synchronization            - Nested Sequence Numbers    |
|     - Swimlanes (Domain Boundaries)        - Topological Proximity      |
+-------------------------------------------------------------------------+
```

---

## 3.1 Activity Diagrams as Petri Net Extensions: Token Flow Semantics

### Petri Net Mathematical Foundations

Modern UML 2.5 Activity Diagrams are not simplistic flowcharts; they are formal semantic extensions of **Petri Nets** (specifically Colored Petri Nets with queuing). A Petri net is formally defined as a 5-tuple:

$$PN = \langle P, T, F, W, M_0 \rangle$$

Where:
- $P = \{p_1, p_2, \dots, p_m\}$ is a finite set of places (analogous to buffers/pins in UML).
- $T = \{t_1, t_2, \dots, t_n\}$ is a finite set of transitions (analogous to action nodes in UML).
- $F \subseteq (P \times T) \cup (T \times P)$ is a set of directed flow arcs.
- $W : F \to \mathbb{N}^+$ is the arc weight function.
- $M_0 : P \to \mathbb{N}$ is the initial token marking vector.

### Token Flow Semantics in UML 2.5
In UML 2.5, execution is modeled through the propagation of discrete **Tokens**:
- **Control Tokens**: Represent the thread of control passing along edges.
- **Object Tokens**: Represent physical data payloads or instantiated objects moving through the execution graph.
- **Firing Rule**: An action node begins execution if and only if all incoming control and object edges offer the required tokens. Upon completion, it consumes the input tokens and produces output tokens on all outgoing edges.

---

## 3.2 Control Nodes: Initial, Final, Decision, and Merge Diamonds

```
+-------------------------------------------------------------------------+
|                        CONTROL NODE TAXONOMY                            |
|                                                                         |
|  Symbol | Metamodel Classifier | Operational Execution Semantics        |
| :------ | :------------------- | :------------------------------------- |
|  ●      | **Initial Node**     | Generates the initial control token.   |
|  (●)    | **Activity Final**   | Immediately aborts ENTIRE activity.    |
|  (X)    | **Flow Final**       | Destroys token on THIS branch only.    |
|  <>     | **Decision Diamond** | 1 input, N guarded outputs (alt flow). |
|  <>     | **Merge Diamond**    | N inputs, 1 output (joins alternatives)|
+-------------------------------------------------------------------------+
```

### Activity Final vs. Flow Final Semantics
- **Activity Final Node (`(●)`)**: When any token reaches an Activity Final node, the entire activity terminates immediately. All active concurrent threads, pending tokens, and background actions across all swimlanes are halted.
- **Flow Final Node (`(X)`)**: When a token arrives at a Flow Final node, that individual token is destroyed, terminating only that specific parallel path. Other concurrent branches continue executing unhindered.

### Decision vs. Merge Diamonds
- **Decision**: Evaluates boolean guards `[predicate]` on outgoing edges. Exactly one guard must be true.
- **Merge**: Receives multiple alternate incoming flows and multiplexes them into a single downstream edge *without synchronization*. Tokens do not wait for each other.

---

## Visual Architecture: Activity Diagrams, Swimlanes & Concurrency

{{ media:sam-activity-swimlanes-diagram }}

### Multimedia Deep-Dive: Workflow Systems & Process Engineering
Examine how enterprise software architectures model business process workflows, organizational pipelines, and lifecycle phases:

{{ media:activity-workflow-video }}

---

## 3.3 Fork and Join Synchronization Bars: Parallelism & Concurrency Barriers

```
+-------------------------------------------------------------------------+
|                  FORK AND JOIN SYNCHRONIZATION BARS                     |
|                                                                         |
|                            [ Incoming Flow ]                            |
|                                    |                                    |
|                                    v                                    |
|  =====================================================================  |
|                         FORK BAR (1 input -> N outputs)                 |
|  =====================================================================  |
|            |                                              |             |
|    Token cloned to branch A                       Token cloned to branch B
|            v                                              v             |
|  +--------------------+                         +--------------------+  |
|  |  Action 1 (Thread) |                         |  Action 2 (Thread) |  |
|  +--------------------+                         +--------------------+  |
|            |                                              |             |
|            v                                              v             |
|  =====================================================================  |
|                         JOIN BAR (N inputs -> 1 output)                 |
|  =====================================================================  |
|                                    |                                    |
|               Emits 1 token ONLY when ALL inputs have arrived           |
|                                    v                                    |
|                            [ Downstream Flow ]                          |
+-------------------------------------------------------------------------+
```

### Mathematical Invariants of Synchronization Bars
1. **Fork Semantics**:
   - Takes 1 incoming flow and splits it into $k \ge 2$ concurrent outgoing flows.
   - For every incoming token, a replica token is offered to all $k$ outgoing edges concurrently.
2. **Join Semantics (Barrier Synchronization)**:
   - Takes $k \ge 2$ incoming flows and produces 1 outgoing flow.
   - A token is released downstream if and only if:
     $$\forall i \in \{1, \dots, k\}: \text{TokensAt}(\text{Input}_i) \ge 1$$
   - Consumes exactly 1 token from each input edge atomically. If one branch fails to arrive, the downstream flow suffers from **Join Starvation (Deadlock)**.

---

## 3.4 Object Nodes, Object Flows, and Pin Parameters

In addition to control flow, activity diagrams model data flow via **Object Nodes** and **Action Pins**:
- **Object Node**: A rectangle representing data instances available in the workflow (e.g., `OrderRecord [Status = Authorized]`).
- **Pins**: Small square boxes attached to action boundaries representing explicit input and output parameters.
- **Object Flow**: A dashed or solid directed arrow carrying typed object instances between pins.

```
  +------------------+                    +------------------+
  | ValidateOrder    |                    | ChargeCustomer   |
  |                  |[orderId] ----> [id]|                  |
  +------------------+ (Output Pin)  (Input Pin)+------------+
```

---

## 3.5 Swimlanes (Activity Partitions): Cross-Functional Boundaries

Swimlanes partition an activity diagram into vertical or horizontal columns representing organizational units, system components, or physical nodes:

```
+-------------------------------------------------------------------------+
|                        SWIMLANE DOMAIN PARTITIONS                       |
|                                                                         |
|  Customer Domain      | Payment Gateway         | Logistics Warehouse   |
|  -------------------  | ----------------------- | --------------------- |
|  ● Start              |                         |                       |
|    |                  |                         |                       |
|  [Submit Cart] ------>| [Authorize Card]        |                       |
|                       |   | (Fork Bar)          |                       |
|                       |   +-------------------->| [Pick Stock Items]    |
|  [Receive Receipt]<---|   |                     |   |                   |
|                       |   +====================>| [Pack & Ship]         |
|                       |                         |   v                   |
|                       |                         | (●) Final             |
+-------------------------------------------------------------------------+
```

---

## 3.6 Communication Diagrams: Object Roles, Links, and Sequence Numbers

### Definition and Metamodel Role
A **Communication Diagram** (UML 2.5) models an interaction by emphasizing the structural topology of participating instances rather than the temporal time-axis.
- **Nodes**: Object instances or roles (`<u>orderMgr : OrderManager</u>`).
- **Edges**: Solid lines representing association links between instances.
- **Messages**: Directed arrows parallel to the link labeled with sequence expressions.

```
+-------------------------------------------------------------------------+
|                  UML 2.5 COMMUNICATION DIAGRAM NOTATION                 |
|                                                                         |
|                  1: submitOrder()                                       |
|  +------------+ =====================> +--------------------+           |
|  | <u>:Client</u> |                        | <u>:OrderService</u>   |           |
|  +------------+ < - - - - - - - - - -  +--------------------+           |
|                    1.3: orderConfirmed            |                     |
|                                                   | 1.1: verifyStock()  |
|                                                   v                     |
|                                        +--------------------+           |
|                                        | <u>:InventoryRepo</u>  |           |
|                                        +--------------------+           |
|                                                   |                     |
|                                                   | 1.2: captureFunds() |
|                                                   v                     |
|                                        +--------------------+           |
|                                        | <u>:PaymentService</u> |           |
|                                        +--------------------+           |
+-------------------------------------------------------------------------+
```

### Nested Sequence Numbering Syntax
Communication diagrams express hierarchical nested calls through dot notation:
- `1`: Top-level message initiated by client.
- `1.1`: First sub-call dispatched by receiver during handling of message 1.
- `1.1.1`: Sub-call inside message 1.1.
- `1.2`: Second sub-call dispatched by receiver during handling of message 1.
- `2`: Next independent top-level message.
- `* [i = 1..n]`: Iteration quantifier.
- `[guard]`: Conditional execution predicate.

### Sequence vs. Communication Diagrams Comparison

| Dimension | Sequence Diagram | Communication Diagram |
| :--- | :--- | :--- |
| **Primary Focus** | Exact chronological time progression | Structural topology and network proximity |
| **Space Consumption** | Grows horizontally with lifelines, vertically with time | Compact graph layout in 2D space |
| **Control Logic** | Visual frames (`alt`, `opt`, `loop`, `par`) | Nested numbers and textual qualifiers (`1.1[g]: msg`) |
| **Best Used For** | Complex real-time protocols, timing, branching | Architectural review of interface couplings |

---

## 3.7 Production C++17 Concurrent Workflow & Petri Net Engine

The following industrial C++17 simulation engine implements a formal token-flow workflow engine supporting action nodes, decision diamonds, fork bars, and join synchronization barriers.

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>
#include <memory>
#include <functional>

// ============================================================================
// ACTIVITY DIAGRAM TOKEN-FLOW METAMODEL (C++17)
// ============================================================================

enum class NodeType {
    INITIAL_NODE,
    ACTION_NODE,
    DECISION_NODE,
    MERGE_NODE,
    FORK_NODE,
    JOIN_NODE,
    FLOW_FINAL_NODE,
    ACTIVITY_FINAL_NODE
};

struct ActivityNode {
    std::string nodeId;
    std::string name;
    NodeType type;
    std::string swimlane;
    std::function<void()> actionPayload = nullptr;
    std::function<bool()> guardPredicate = nullptr; // For decision branches
    std::vector<std::string> outgoingEdges;
    std::vector<std::string> incomingEdges;
};

class WorkflowPetriNetEngine {
private:
    std::unordered_map<std::string, ActivityNode> nodes;
    std::unordered_map<std::string, size_t> edgeTokens; // EdgeId -> Token Count
    std::string initialNodeId;
    bool activityTerminated = false;

public:
    void registerNode(const ActivityNode& node) {
        nodes[node.nodeId] = node;
        if (node.type == NodeType::INITIAL_NODE) {
            initialNodeId = node.nodeId;
        }
    }

    void connect(const std::string& fromNode, const std::string& toNode, const std::string& edgeId) {
        nodes[fromNode].outgoingEdges.push_back(edgeId);
        nodes[toNode].incomingEdges.push_back(edgeId);
        edgeTokens[edgeId] = 0;
    }

    void executeWorkflow() {
        std::cout << "\n====================================================================\n";
        std::cout << "                 UML ACTIVITY TOKEN-FLOW SIMULATION                  \n";
        std::cout << "====================================================================\n";

        if (initialNodeId.empty()) {
            std::cerr << "Error: No initial node declared.\n";
            return;
        }

        // 1. Fire Initial Node: Generate Token on Outgoing Edge
        const auto& startNode = nodes[initialNodeId];
        std::cout << "[START] Firing Initial Node in Swimlane: [" << startNode.swimlane << "]\n";
        for (const auto& outEdge : startNode.outgoingEdges) {
            edgeTokens[outEdge] = 1;
        }

        // 2. Continuous Event Execution Loop
        bool progressMade = true;
        size_t step = 0;

        while (progressMade && !activityTerminated) {
            progressMade = false;
            step++;

            for (auto& [id, node] : nodes) {
                if (activityTerminated) break;

                // Check Firing Rule according to Node Type
                if (node.type == NodeType::ACTION_NODE) {
                    // Requires 1 token on at least one incoming edge
                    for (const auto& inEdge : node.incomingEdges) {
                        if (edgeTokens[inEdge] > 0) {
                            edgeTokens[inEdge]--; // Consume Token
                            std::cout << "[STEP " << step << "] Action: [" << node.name 
                                      << "] executed in Swimlane: " << node.swimlane << "\n";
                            if (node.actionPayload) node.actionPayload();

                            // Produce token on outgoing edges
                            for (const auto& outEdge : node.outgoingEdges) {
                                edgeTokens[outEdge]++;
                            }
                            progressMade = true;
                            break;
                        }
                    }
                } else if (node.type == NodeType::FORK_NODE) {
                    for (const auto& inEdge : node.incomingEdges) {
                        if (edgeTokens[inEdge] > 0) {
                            edgeTokens[inEdge]--;
                            std::cout << "[STEP " << step << "] FORK BAR Fired! Cloning token across " 
                                      << node.outgoingEdges.size() << " parallel branches.\n";
                            for (const auto& outEdge : node.outgoingEdges) {
                                edgeTokens[outEdge]++;
                            }
                            progressMade = true;
                            break;
                        }
                    }
                } else if (node.type == NodeType::JOIN_NODE) {
                    // Requires 1 token on ALL incoming edges (Barrier Synchronization)
                    bool allSatisfied = true;
                    for (const auto& inEdge : node.incomingEdges) {
                        if (edgeTokens[inEdge] == 0) {
                            allSatisfied = false;
                            break;
                        }
                    }

                    if (allSatisfied) {
                        for (const auto& inEdge : node.incomingEdges) {
                            edgeTokens[inEdge]--; // Atomically consume all tokens
                        }
                        std::cout << "[STEP " << step << "] JOIN BAR Synchronized! All parallel flows joined.\n";
                        for (const auto& outEdge : node.outgoingEdges) {
                            edgeTokens[outEdge]++;
                        }
                        progressMade = true;
                    }
                } else if (node.type == NodeType::DECISION_NODE) {
                    for (const auto& inEdge : node.incomingEdges) {
                        if (edgeTokens[inEdge] > 0) {
                            edgeTokens[inEdge]--;
                            std::cout << "[STEP " << step << "] DECISION Diamond evaluated: ";
                            // For simulation: fire first branch if guard is null or true
                            bool routed = false;
                            for (const auto& outEdge : node.outgoingEdges) {
                                edgeTokens[outEdge]++;
                                std::cout << "Routed token down edge " << outEdge << "\n";
                                routed = true;
                                break;
                            }
                            progressMade = routed;
                        }
                    }
                } else if (node.type == NodeType::ACTIVITY_FINAL_NODE) {
                    for (const auto& inEdge : node.incomingEdges) {
                        if (edgeTokens[inEdge] > 0) {
                            edgeTokens[inEdge]--;
                            std::cout << "[TERMINATION] Token reached Activity Final Node! Halting system.\n";
                            activityTerminated = true;
                            progressMade = true;
                            break;
                        }
                    }
                }
            }
        }

        std::cout << "====================================================================\n";
        std::cout << "Simulation Completed: " << (activityTerminated ? "NORMAL EXIT" : "DEADLOCK/STARVATION") << "\n";
    }
};

int main() {
    WorkflowPetriNetEngine engine;

    // Define Order Fulfillment Workflow with Swimlanes
    engine.registerNode({"init", "InitialNode", NodeType::INITIAL_NODE, "CustomerLane"});
    engine.registerNode({"act1", "SubmitOrder", NodeType::ACTION_NODE, "CustomerLane", []() {
        std::cout << "    -> Customer placed order via web portal.\n";
    }});
    engine.registerNode({"fork1", "ParallelFork", NodeType::FORK_NODE, "SystemLane"});
    
    // Concurrent Branch A: Payment
    engine.registerNode({"act2", "ProcessPayment", NodeType::ACTION_NODE, "PaymentLane", []() {
        std::cout << "    -> Credit card settled via Stripe gateway.\n";
    }});

    // Concurrent Branch B: Warehouse
    engine.registerNode({"act3", "PickWarehouseStock", NodeType::ACTION_NODE, "WarehouseLane", []() {
        std::cout << "    -> Warehouse robot picked items from inventory shelf.\n";
    }});

    // Join Barrier
    engine.registerNode({"join1", "BarrierJoin", NodeType::JOIN_NODE, "SystemLane"});
    engine.registerNode({"act4", "DispatchShipment", NodeType::ACTION_NODE, "WarehouseLane", []() {
        std::cout << "    -> Courier shipping label printed and pasted.\n";
    }});
    engine.registerNode({"final", "ActivityFinal", NodeType::ACTIVITY_FINAL_NODE, "CustomerLane"});

    // Connect Graph
    engine.connect("init", "act1", "e1");
    engine.connect("act1", "fork1", "e2");
    engine.connect("fork1", "act2", "e3_pay");
    engine.connect("fork1", "act3", "e4_stock");
    engine.connect("act2", "join1", "e5_pay_done");
    engine.connect("act3", "join1", "e6_stock_done");
    engine.connect("join1", "act4", "e7");
    engine.connect("act4", "final", "e8");

    // Execute Petri Net
    engine.executeWorkflow();

    return 0;
}
```

---

## 3-Tier Progressive Practice Suite

### Level 1: Guided Architectural Walkthrough & Sequence to Communication Diagram Transformation

#### Problem Statement
Consider an ATM cash withdrawal sequence diagram with the following trace:
1. `Client` sends `insertCard()` to `ATMController`.
2. `ATMController` sends `verifyPin()` to `BankNetwork`.
3. `BankNetwork` sends `queryLedger()` to `DatabaseShard`.
4. `BankNetwork` returns `pinOK` to `ATMController`.
5. `ATMController` sends `ejectCash()` to `CashDispenser`.

Convert this trace into a UML 2.5 Communication Diagram, specifying:
1. All participating object instances.
2. Direct association links between instances.
3. Formally numbered message arrows with correct dot-notation nesting.

#### Guided Solution
1. **Object Instances**:
   - `<u>c : Client</u>`
   - `<u>atm : ATMController</u>`
   - `<u>net : BankNetwork</u>`
   - `<u>db : DatabaseShard</u>`
   - `<u>disp : CashDispenser</u>`
2. **Structural Association Links**:
   - Link 1: `(c) ---------------- (atm)`
   - Link 2: `(atm) -------------- (net)`
   - Link 3: `(net) -------------- (db)`
   - Link 4: `(atm) -------------- (disp)`
3. **Sequenced Message Arrows**:
   - On Link 1: `1: insertCard() —►` (from `c` to `atm`)
   - On Link 2: `1.1: verifyPin() —►` (from `atm` to `net`)
   - On Link 3: `1.1.1: queryLedger() —►` (from `net` to `db`)
   - On Link 2: `1.1.2: pinOK —►` (from `net` to `atm`)
   - On Link 4: `1.2: ejectCash() —►` (from `atm` to `disp`)

---

### Level 2: Scaffolded Troubleshooting / Bug-Fix Challenge

#### Challenge Description
An e-procurement enterprise workflow stalls permanently during month-end vendor invoice settlement. The architect reviews the following activity diagram specification:

```
                      [ Fork Bar ]
                       /        \
                      /          \
                     v            v
            [ Pay Vendor ]    [ Decision ]
                               /        \
               [amount < 10k] /          \ [amount >= 10k]
                             v            v
                      (Flow Final)   [ Executive Sign-off ]
                                          |
                                          |
                                          v
                      [ Join Bar ] <------+
```

Identify why this workflow causes a system deadlock when `amount < 10k` and provide the correct architectural redesign.

<details>
<summary>Click to view solution & walkthrough</summary>

#### Diagnostic Breakdown

1. **Defect: Join Bar Starvation (Deadlock)**
   - *Symptom*: When `amount < 10k`, the control token on the right branch passes into a `(Flow Final)` node and is destroyed.
   - *Petri Net Rule*: A **Join Bar** requires at least one token on **every incoming edge** before it can fire.
   - *Consequence*: The left branch (`Pay Vendor`) produces a token at the Join Bar, but the Join Bar waits indefinitely for the token from the right branch. The system deadlocks, holding open transactions and unreleased database locks forever.

2. **Architectural Redesign**:
   - Replace the `(Flow Final)` node with an empty bypass edge routed directly into a **Merge Diamond** placed immediately before the Join Bar.
   - Alternatively, merge the bypass edge directly into the Join Bar as an optional token path:
     `[Decision] --- [amount < 10k] ---> [Merge Diamond] ---> [Join Bar]`
   - This guarantees that exactly one token always reaches the Join Bar from the right branch regardless of which decision predicate evaluates to true.

</details>

---

### Level 3: Production C++17 Token-Flow Petri Net Engine with Object Flow Pins

#### Challenge Description
Implement a production C++17 Petri net simulator that models both Control Tokens and Typed Object Tokens moving across Pins. The engine must:
1. Verify that action nodes receive valid object payloads before executing.
2. Prevent join deadlock by verifying path completeness.
3. Measure token transit times across execution nodes.

<details>
<summary>Click to view production C++17 implementation</summary>

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <any>
#include <cassert>

struct ObjectToken {
    std::string typeName;
    std::any payload;
};

class PetriNetPinEngine {
public:
    struct Pin {
        std::string pinName;
        std::vector<ObjectToken> tokenBuffer;
    };

    struct ActionNode {
        std::string name;
        std::vector<std::string> inputPins;
        std::vector<std::string> outputPins;
        std::function<void(const std::unordered_map<std::string, ObjectToken>&,
                           std::unordered_map<std::string, ObjectToken>&)> logic;
    };

private:
    std::unordered_map<std::string, Pin> pins;
    std::unordered_map<std::string, ActionNode> actions;

public:
    void addPin(const std::string& pinName) {
        pins[pinName] = {pinName, {}};
    }

    void addAction(const ActionNode& node) {
        actions[node.name] = node;
    }

    void depositToken(const std::string& pinName, const ObjectToken& token) {
        pins[pinName].tokenBuffer.push_back(token);
    }

    bool stepAction(const std::string& actionName) {
        auto& node = actions.at(actionName);

        // Check if all input pins have tokens
        for (const auto& pName : node.inputPins) {
            if (pins[pName].tokenBuffer.empty()) return false;
        }

        // Consume tokens
        std::unordered_map<std::string, ObjectToken> inTokens;
        for (const auto& pName : node.inputPins) {
            inTokens[pName] = pins[pName].tokenBuffer.front();
            pins[pName].tokenBuffer.erase(pins[pName].tokenBuffer.begin());
        }

        // Execute logic
        std::unordered_map<std::string, ObjectToken> outTokens;
        node.logic(inTokens, outTokens);

        // Emit tokens to output pins
        for (const auto& [pName, tok] : outTokens) {
            pins[pName].tokenBuffer.push_back(tok);
        }

        return true;
    }

    size_t getPinTokenCount(const std::string& pinName) const {
        return pins.at(pinName).tokenBuffer.size();
    }
};

int main() {
    PetriNetPinEngine engine;

    engine.addPin("pRawOrderIn");
    engine.addPin("pValidatedOrder");
    engine.addPin("pPaymentReceiptOut");

    engine.addAction({
        "ValidateOrderAction",
        {"pRawOrderIn"},
        {"pValidatedOrder"},
        [](const auto& in, auto& out) {
            int orderId = std::any_cast<int>(in.at("pRawOrderIn").payload);
            std::cout << "  [ACTION] Validated Order #" << orderId << "\n";
            out["pValidatedOrder"] = {"ValidatedOrder", orderId * 10};
        }
    });

    engine.addAction({
        "SettlePaymentAction",
        {"pValidatedOrder"},
        {"pPaymentReceiptOut"},
        [](const auto& in, auto& out) {
            int validatedId = std::any_cast<int>(in.at("pValidatedOrder").payload);
            std::cout << "  [ACTION] Settle Payment for Order Token " << validatedId << "\n";
            out["pPaymentReceiptOut"] = {"Receipt", std::string("REC_PAID_" + std::to_string(validatedId))};
        }
    });

    std::cout << ">>> Injecting Raw Order Token into Workflow...\n";
    engine.depositToken("pRawOrderIn", {"Order", 42});

    std::cout << "Stepping ValidateOrderAction: " << (engine.stepAction("ValidateOrderAction") ? "OK" : "FAILED") << "\n";
    std::cout << "Stepping SettlePaymentAction: " << (engine.stepAction("SettlePaymentAction") ? "OK" : "FAILED") << "\n";

    std::cout << "Final Receipt Tokens Available: " << engine.getPinTokenCount("pPaymentReceiptOut") << "\n";

    return 0;
}
```

</details>

---

## Pedagogical Review Questions & Examination Problems

1. **Formal Petri Net Liveness**: In an Activity Diagram containing a Fork Bar followed by two branches of unequal execution duration, how do token flow semantics prevent race conditions before reaching the Join Bar?
2. **Flow Final vs. Activity Final**: Explain why using an Activity Final Node inside a nested sub-process can be catastrophic for an enterprise distributed workflow compared to a Flow Final Node.
3. **Communication Diagram Numbering**: Given a communication diagram where message `2: computeBill()` triggers two sequential helper operations and one conditional validation, write the exact UML 2.5 sequence numbering labels for all three sub-operations.
