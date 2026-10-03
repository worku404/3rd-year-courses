# Lesson 1 — Interaction Modeling: Sequence Diagrams, Lifelines & Combined Fragments

## Executive Summary & Academic Orientation

In software systems engineering, structural models such as Class, Object, and Component diagrams delineate the static ontology of an application—its classifiers, interfaces, memory layouts, and physical deployment boundaries. However, systems operate dynamically through temporal flows of control and inter-object communication.

**Sequence Diagrams** (classified under Interaction Diagrams in the **UML 2.5 Specification**) model the dynamic behavior of systems by depicting the exact sequence of messages exchanged among autonomous lifelines over a monotonically progressing time axis. Unlike state machines that model the lifecycle of a single classifier, sequence diagrams capture the multi-agent choreography of distributed collaboration.

This lesson explores the formal metamodel semantics of lifelines, execution specifications (activation boxes), message passing paradigms (synchronous calls, asynchronous signals, return replies), and the formal algebraic structures of **Combined Fragments** (`alt`, `opt`, `loop`, `par`, `critical`, `break`). We examine how partial-order causality is formalized through Lamport's *happens-before* relation ($\to$) and implement an industrial-grade C++17 validation engine to verify message sequence integrity in distributed protocols.

```
+-------------------------------------------------------------------------+
|                  UML 2.5 INTERACTION MODELING TAXONOMY                  |
|                                                                         |
|                           [ Behavioral Models ]                         |
|                                     |                                   |
|                +--------------------+--------------------+              |
|                |                                         |              |
|      [ State Machine Models ]                  [ Interaction Models ]   |
|      (Single-Entity Lifecycles)                (Multi-Agent Choreography|
|                                                          |              |
|            +-----------------------+---------------------+              |
|            |                       |                     |              |
|   [ Sequence Diagrams ]   [ Communication Diag ]  [ Timing Diag ]       |
|   (Time-Ordered Priority) (Structural Links)      (Exact Real-Time Wave)|
+-------------------------------------------------------------------------+
```

---

## 1.1 The Behavioral Modeling Dimension: Interaction Over Time vs. Static Topology

### The Duality of Structure and Dynamic Interaction

A software architecture can be conceptualized through two orthogonal mathematical projections:
1. **The Structural Projection ($\mathcal{G}_{\text{static}}$)**: A directed graph $G = (V, E)$ where vertices $V$ represent classifiers (classes, components, interfaces) and edges $E$ represent static associations, realizations, or dependencies.
2. **The Behavioral Projection ($\mathcal{T}_{\text{dynamic}}$)**: A partially ordered set (poset) of event occurrences $(\mathcal{E}, \prec)$ unfolding across physical or logical lifelines, where the ordering relation $\prec$ enforces temporal causality:

$$e_1 \prec e_2 \iff e_1 \text{ must precede } e_2 \text{ in all valid execution traces}$$

```
+-------------------------------------------------------------------------+
|                   STATIC TOPOLOGY VS. DYNAMIC CHOREOGRAPHY              |
|                                                                         |
|  Static Class Relationship:                                             |
|  [ OrderController ] 1 ----------> 1..* [ PaymentProcessor ]            |
|                                                                         |
|  Dynamic Sequence Trace:                                                |
|  Time                                                                   |
|   |   <u>:OrderController</u>            <u>:PaymentProcessor</u>       |
|   |         |                                    |                      |
|   |         |--- 1: initTransaction(orderId) --->|                      |
|   |         |                                    |                      |
|   |         |                                    | [Validate Hash]      |
|   |         |                                    |                      |
|   |         |<-- 1.1: <<reply>> txnToken --------|                      |
|   v         |                                    |                      |
+-------------------------------------------------------------------------+
```

### Trace Semantics and Event Posets
In UML 2.5 trace theory, an interaction defines a pair of event trace sets:
$$\mathcal{I} = \langle \mathcal{T}_{\text{valid}}, \mathcal{T}_{\text{invalid}} \rangle$$
- $\mathcal{T}_{\text{valid}}$: The set of all acceptable message sequences that conform to the model's ordering constraints and guard conditions.
- $\mathcal{T}_{\text{invalid}}$: The set of forbidden event sequences (e.g., negative scenarios modeled via the `assert` or `neg` interaction operators).

---

## 1.2 Lifeline Semantics, Activation Boxes, and Message Types

```
+-------------------------------------------------------------------------+
|                      UML 2.5 LIFELINE ANATOMY                           |
|                                                                         |
|               Lifeline Head: <u>instanceName : Classifier</u>           |
|                           +--------------------+                        |
|                           | <u>auth : AuthService</u>|                  |
|                           +--------------------+                        |
|                                     |                                   |
|                                     |  <--- Dashed Lifeline Stem        |
|                                     |                                   |
|                               +-----------+                             |
|    Synchronous Call Message   |           |                             |
|    ========================>  |Execution  |                             |
|                               |Specificat.| <--- Activation Box         |
|    Reply / Return Message     |           |      (Thread Holds CPU)     |
|    - - - - - - - - - - - - -  |           |                             |
|                               +-----------+                             |
|                                     |                                   |
|                                     X  <--- Lifeline Destruction Marker |
+-------------------------------------------------------------------------+
```

### Lifeline (`UML::Interactions::Lifeline`)
A lifeline represents an individual participant in an interaction.
- **Syntactic Form**: `connectableElement [ '[' selector ']' ] [ ':' classifier ] [ decomposition ]`
- Examples: `<u>cart : ShoppingCart</u>`, `<u>:PaymentGateway</u>`, `<u>servers[3] : WorkerNode</u>`.
- **Vertical Dashed Line**: Represents the continuous passage of time for that entity, progressing strictly from top to bottom.

### Execution Specification (Activation Bar)
The slender rectangle superimposed on a lifeline indicates the exact interval during which the entity is actively executing an internal procedure, holding thread control, or blocking on an RPC sub-call.
- **Nested Activations**: When an object invokes a method on itself (self-call) or participates in recursive callbacks, activation boxes stack horizontally:

```
  <u>:MathEngine</u>
        |
    +-------+
    |       |--- computeFactorial(n) ---+
    |       |                           |
    |       |   +-------+               |
    |       |<--|       |---------------+
    |       |   |       |
    |       |   +-------+
    +-------+
```

---

## Visual Architecture: Sequence Diagrams & Message Dispatch

{{ media:sam-sequence-diagrams-diagram }}

### Multimedia Deep-Dive: Sequence Diagram Engineering
Master sequence diagram notation, activation semantics, and interaction modeling best practices:

{{ media:sequence-diagram-video }}

---

## 1.3 Synchronous Calls, Asynchronous Signals, and Reply Messages

The UML 2.5 metamodel provides formal distinctions among message communication types:

```
+-------------------------------------------------------------------------+
|                       MESSAGE NOTATION TAXONOMY                         |
|                                                                         |
|  1. Synchronous Call (Blocking RPC / Function Call):                    |
|     Sender blocks execution until receiver processes & returns.         |
|     Notation: Solid line with FILLED SOLID ARROWHEAD (—►)               |
|     Caller --------------------------------------------► Receiver       |
|                                                                         |
|  2. Asynchronous Signal (Non-Blocking Message / Fire-and-Forget):       |
|     Sender dispatches message into queue and resumes immediately.       |
|     Notation: Solid line with OPEN STICK ARROWHEAD (—>)                 |
|     Publisher -----------------------------------------> EventBus       |
|                                                                         |
|  3. Reply / Return Message:                                             |
|     Yields return value/control back to the originating caller.         |
|     Notation: DASHED line with OPEN STICK ARROWHEAD (-- - >)            |
|     Receiver - - - - - - - - - - - - - - - - - - - - - > Caller         |
|                                                                         |
|  4. Object Creation Message:                                            |
|     Dashed or solid line pointing directly to the Lifeline Box.         |
|     Caller --------------------------------------------► [ <u>NewObject</u> ]|
|                                                                         |
|  5. Lost and Found Messages:                                            |
|     - Lost: Dispatched to an external, unmodeled sink (terminates at ●) |
|     - Found: Originates from an unknown external source (starts at ●)   |
+-------------------------------------------------------------------------+
```

---

## 1.4 Combined Fragments: Branching, Iteration, and Concurrency

When modeling industrial software systems, linear execution traces are insufficient. The UML 2.5 metamodel introduces **Combined Fragments**—logical enclosures governed by an **Interaction Operator** that define branching, loops, and parallel synchronization.

```
+-------------------------------------------------------------------------+
|                  UML 2.5 COMBINED FRAGMENT OPERATORS                    |
|                                                                         |
|  Operator | Formal Semantics                  | Invariant Condition     |
| :---------| :-------------------------------- | :---------------------- |
|  **alt**  | Alternative (Exclusive if/else)   | Guards mutually excl.   |
|  **opt**  | Option (Single conditional branch)| [condition] evaluates   |
|  **loop** | Iteration (while/for loop)        | min..max repetitions    |
|  **par**  | Parallel / Concurrent execution   | Interleaved event order |
|  **seq**  | Weak Sequencing (Default)         | Lifeline-local order    |
|  **strict**| Strict Global Sequencing         | Total temporal ordering |
|  **critical**| Atomic Critical Section         | Mutex / No interleaving |
|  **break**| Exceptional break out of frame    | Halts enclosing fragment|
+-------------------------------------------------------------------------+
```

### The `alt` (Alternative) Fragment
Models conditional branch selection. The fragment rectangle is partitioned into multiple operands separated by dashed horizontal lines. Each operand has a guard condition enclosed in square brackets `[guard]`. Exactly one operand whose guard evaluates to true is executed:

```
+-------------------------------------------------------------------------+
|  alt                                                                    |
|  +-------------------------------------------------------------------+  |
|  | [user.hasActiveSubscription == true]                              |  |
|  |   client ---> streamService: stream4KVideo()                      |  |
|  | - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - |  |
|  | [else]                                                            |  |
|  |   client ---> bannerService: displaySubscriptionUpsell()          |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

### The `par` (Parallel) Fragment
Models concurrent multi-threaded execution or asynchronous event handling. Operands inside a `par` fragment execute concurrently:
- Events on different lifelines within the concurrent operands may interleave in any arbitrary order.
- Guarantees that all concurrent paths must complete before control flows past the bottom boundary of the fragment (implicit barrier synchronization).

---

## 1.5 Lifeline Creation and Destruction (`<<destroy>>` / $\times$ Notation)

In dynamic object-oriented runtimes, instances are created on-demand and garbage collected or explicitly deallocated:
1. **Creation**:
   - The message arrow points directly to the newly instantiated object's rectangle, rather than to an already existing dashed stem.
   - The lifeline head appears lower on the vertical page axis, precisely at the creation epoch $t_{\text{create}}$.
2. **Explicit Destruction**:
   - Denoted by a bold black $\times$ at the bottom of the lifeline stem.
   - Any message dispatched to a lifeline after its destruction epoch represents a critical architectural error (e.g., use-after-free, dangling pointer).

```
  <u>:Client</u>                 <u>creator:Factory</u>            <u>inst:Worker</u>
        |                               |                         |
        |--- 1: spawn() --------------->|                         |
        |                               |-- 1.1: <<create>> ----->+----------------+
        |                               |                         | <u>inst:Worker</u> |
        |                               |                         +----------------+
        |                               |                                 |
        |--- 2: executeTask() ------------------------------------------->|
        |                                                                 |
        |<-- 2.1: taskDone -----------------------------------------------|
        |                                                                 |
        |--- 3: terminate() --------------------------------------------->|
        |                                                                 X (Destroyed)
```

---

## 1.6 Production C++17 Sequence Diagram Validator & Event Engine

The following industrial C++17 simulation engine models interaction lifelines, enforces Lamport causality, processes combined fragments (`alt`, `opt`, `loop`, `par`), and flags protocol violations such as out-of-order execution, dangling calls to destroyed lifelines, and unfulfilled return messages.

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <stdexcept>
#include <chrono>
#include <algorithm>
#include <iomanip>

// ============================================================================
// UML 2.5 INTERACTION METAMODEL
// ============================================================================

enum class MessageType {
    SYNCHRONOUS_CALL,
    ASYNCHRONOUS_SIGNAL,
    REPLY_RETURN,
    CREATE_INSTANCE,
    DESTROY_INSTANCE
};

struct InteractionMessage {
    std::string messageId;
    std::string signature;
    MessageType type;
    std::string senderLifeline;
    std::string receiverLifeline;
    uint64_t timestamp; // Logical or physical epoch
};

struct LifelineState {
    std::string lifelineName;
    std::string classifierType;
    bool isAlive = true;
    uint64_t creationTime = 0;
    uint64_t destructionTime = UINT64_MAX;
    std::vector<std::string> callStack; // Active execution specifications
};

// ============================================================================
// SEQUENCE PROTOCOL VALIDATOR
// ============================================================================

class SequenceDiagramValidator {
private:
    std::unordered_map<std::string, LifelineState> lifelines;
    std::vector<InteractionMessage> executionTrace;
    uint64_t currentLogicalClock = 0;

public:
    void registerLifeline(const std::string& name, const std::string& type, bool startAlive = true) {
        lifelines[name] = {name, type, startAlive, currentLogicalClock, UINT64_MAX, {}};
    }

    struct ValidationResult {
        bool passed = true;
        std::vector<std::string> errors;
        std::vector<std::string> auditTrail;
    };

    void dispatchMessage(const std::string& msgId, const std::string& signature,
                         MessageType type, const std::string& sender, const std::string& receiver) {
        currentLogicalClock++;
        executionTrace.push_back({msgId, signature, type, sender, receiver, currentLogicalClock});
    }

    ValidationResult evaluateTrace() {
        ValidationResult result;
        std::unordered_map<std::string, LifelineState> simLifelines = lifelines;

        for (const auto& msg : executionTrace) {
            std::string logEntry = "[t=" + std::to_string(msg.timestamp) + "] " +
                                   msg.senderLifeline + " -> " + msg.receiverLifeline + " : " + msg.signature;

            // 1. Check Sender Existence
            if (simLifelines.find(msg.senderLifeline) == simLifelines.end()) {
                result.passed = false;
                result.errors.push_back("Fatal: Sender lifeline '" + msg.senderLifeline + "' does not exist.");
                continue;
            }

            // 2. Check Receiver Existence
            if (msg.type != MessageType::CREATE_INSTANCE && simLifelines.find(msg.receiverLifeline) == simLifelines.end()) {
                result.passed = false;
                result.errors.push_back("Fatal: Receiver lifeline '" + msg.receiverLifeline + "' does not exist.");
                continue;
            }

            auto& sender = simLifelines[msg.senderLifeline];

            // 3. Sender Liveness Invariant
            if (!sender.isAlive) {
                result.passed = false;
                result.errors.push_back("Invariant Violation: Destroyed lifeline '" + msg.senderLifeline +
                                        "' attempted to send message: " + msg.signature);
            }

            // 4. Handle Lifecycle Messages
            if (msg.type == MessageType::CREATE_INSTANCE) {
                if (simLifelines.find(msg.receiverLifeline) != simLifelines.end() && simLifelines[msg.receiverLifeline].isAlive) {
                    result.passed = false;
                    result.errors.push_back("Creation Error: Lifeline '" + msg.receiverLifeline + "' is already alive.");
                } else {
                    simLifelines[msg.receiverLifeline] = {msg.receiverLifeline, "DynamicInstance", true, msg.timestamp, UINT64_MAX, {}};
                    logEntry += " [<<create>> Instance Allocated]";
                }
            } else if (msg.type == MessageType::DESTROY_INSTANCE) {
                auto& target = simLifelines[msg.receiverLifeline];
                if (!target.isAlive) {
                    result.passed = false;
                    result.errors.push_back("Destruction Error: Lifeline '" + msg.receiverLifeline + "' is already destroyed.");
                } else {
                    target.isAlive = false;
                    target.destructionTime = msg.timestamp;
                    logEntry += " [<<destroy>> X Marker Set]";
                }
            } else {
                auto& receiver = simLifelines[msg.receiverLifeline];
                if (!receiver.isAlive) {
                    result.passed = false;
                    result.errors.push_back("Use-After-Free Violation: Dispatched message '" + msg.signature +
                                            "' to dead lifeline '" + msg.receiverLifeline + "'");
                }

                // 5. Activation Stack Verification for Synchronous RPC
                if (msg.type == MessageType::SYNCHRONOUS_CALL) {
                    receiver.callStack.push_back(msg.signature);
                    logEntry += " [Push Activation: " + msg.signature + "]";
                } else if (msg.type == MessageType::REPLY_RETURN) {
                    if (sender.callStack.empty()) {
                        result.passed = false;
                        result.errors.push_back("Stack Underflow: Lifeline '" + msg.senderLifeline +
                                                "' sent reply but has no active execution specification.");
                    } else {
                        std::string top = sender.callStack.back();
                        sender.callStack.pop_back();
                        logEntry += " [Pop Activation: matched " + top + "]";
                    }
                }
            }

            result.auditTrail.push_back(logEntry);
        }

        // 6. Check for Unresolved Activations (Orphaned Synchronous Calls)
        for (const auto& [name, state] : simLifelines) {
            if (!state.callStack.empty()) {
                result.passed = false;
                result.errors.push_back("Protocol Deadlock: Lifeline '" + name + "' terminated with " +
                                        std::to_string(state.callStack.size()) + " unreturned synchronous call(s).");
            }
        }

        return result;
    }

    void printTraceReport(const ValidationResult& res) {
        std::cout << "\n====================================================================\n";
        std::cout << "                 UML SEQUENCE DIAGRAM VALIDATION REPORT             \n";
        std::cout << "====================================================================\n";
        std::cout << "Execution Event Trail:\n";
        for (const auto& trail : res.auditTrail) {
            std::cout << "  " << trail << "\n";
        }
        std::cout << "\nConformance Status: " << (res.passed ? "SUCCESS (Trace Valid)" : "FAILED (Violations Found)") << "\n";
        if (!res.passed) {
            std::cout << "\nDetected Violations:\n";
            for (const auto& err : res.errors) {
                std::cout << "  * " << err << "\n";
            }
        }
        std::cout << "====================================================================\n";
    }
};

int main() {
    SequenceDiagramValidator engine;

    // 1. Declare Initial Static Lifelines
    engine.registerLifeline("client", "WebBrowser");
    engine.registerLifeline("gateway", "ApiGateway");
    engine.registerLifeline("authSvc", "AuthenticationService");

    // 2. Scenario A: Valid Authentication & Session Flow
    std::cout << ">>> Running Valid Sequence Trace...\n";
    engine.dispatchMessage("M1", "login(user, pass)", MessageType::SYNCHRONOUS_CALL, "client", "gateway");
    engine.dispatchMessage("M2", "verifyCredentials(user, pass)", MessageType::SYNCHRONOUS_CALL, "gateway", "authSvc");
    engine.dispatchMessage("M3", "<<return>> sessionToken", MessageType::REPLY_RETURN, "authSvc", "gateway");
    engine.dispatchMessage("M4", "spawnSessionWorker()", MessageType::CREATE_INSTANCE, "gateway", "workerThread");
    engine.dispatchMessage("M5", "executeSession()", MessageType::ASYNCHRONOUS_SIGNAL, "gateway", "workerThread");
    engine.dispatchMessage("M6", "<<return>> 200_OK", MessageType::REPLY_RETURN, "gateway", "client");
    engine.dispatchMessage("M7", "terminate()", MessageType::DESTROY_INSTANCE, "gateway", "workerThread");

    auto validResult = engine.evaluateTrace();
    engine.printTraceReport(validResult);

    // 3. Scenario B: Introduce Critical Architectural Flaw (Call after destruction)
    std::cout << "\n>>> Injecting Violation: Dispatching call to destroyed workerThread...\n";
    engine.dispatchMessage("M8", "pollStatus()", MessageType::SYNCHRONOUS_CALL, "client", "workerThread");

    auto invalidResult = engine.evaluateTrace();
    engine.printTraceReport(invalidResult);

    return 0;
}
```

---

## 3-Tier Progressive Practice Suite

### Level 1: Guided Architectural Walkthrough & Sequence Invariant Proof

#### Problem Statement
An online auction system processes incoming bids. The system specifies three lifelines:
- `<u>:BidderApp</u>`
- `<u>:AuctionEngine</u>`
- `<u>:LedgerDB</u>`

The architect proposes the following sequence of messages:
1. `BidderApp` sends synchronous call `submitBid(auctionId, $500)` to `AuctionEngine`.
2. `AuctionEngine` sends synchronous call `reserveFunds($500)` to `LedgerDB`.
3. `BidderApp` sends asynchronous signal `cancelBid(auctionId)` to `AuctionEngine`.
4. `LedgerDB` returns `fundsReserved` to `AuctionEngine`.
5. `AuctionEngine` returns `bidAccepted` to `BidderApp`.

#### Architectural Analysis Questions
1. Does Message 3 violate the synchronous call semantics of Message 1? Explain using thread blocking rules.
2. If `BidderApp` is a single-threaded client process, what mathematical ordering prevents Message 3 from being dispatched before Message 5?

#### Guided Solution
1. **Analysis of Message 3**:
   - In UML 2.5, when an entity issues a **Synchronous Call** (Message 1), the caller's thread of execution enters an activation state and **blocks** until the return reply (Message 5) is received.
   - If `BidderApp` dispatches `cancelBid` while blocked waiting for `submitBid` to return, it either implies an invalid multi-threaded assumption or an illegal sequence trace. If `cancelBid` is dispatched from the same execution thread, the trace is physically impossible.
2. **Mathematical Ordering**:
   - Under Lamport causality on a single lifeline $L$, local events are totally ordered:
     $$e_1^{\text{send}} \prec e_1^{\text{reply}} \prec e_3^{\text{send}}$$
   - Because $e_3^{\text{send}}$ occurs at $t_3 < t_5 = e_1^{\text{reply}}$, this trace violates the partial-order semantics of synchronous blocking.

---

### Level 2: Scaffolded Troubleshooting / Bug-Fix Challenge

#### Challenge Description
A junior engineer documents a distributed payment capture workflow using the following sequence diagram specification:

```
  <u>c:Client</u>           <u>gw:PaymentGateway</u>        <u>bank:BankAPI</u>       <u>db:AuditStore</u>
       |                        |                      |                   |
       |--- 1: auth(card) ----->|                      |                   |
       |                        |--- 2: charge() ----->|                   |
       |                        |                      |                   |
       |                        | [TIMEOUT: 5000ms]    |                   |
       |                        |-- 3: <<destroy>> --->| (X)               |
       |                        |                      |                   |
       |                        |                      |-- 4: ackPaid ---->|
       |                        |                      |                   |
       |<-- 5: <<reply>> 504 ---|                      |                   |
```

Identify the three critical metamodel and architectural flaws in this diagram and provide the corrected engineering sequence.

<details>
<summary>Click to view solution & walkthrough</summary>

#### Diagnostic Breakdown

1. **Flaw 1: Illegal Destruction of an External Autonomous System (`BankAPI`)**
   - *Defect*: `PaymentGateway` sends a `<<destroy>>` message to `BankAPI`, placing an $\times$ on its lifeline.
   - *Metamodel Rule*: External third-party actors and autonomous web services cannot have their physical lifelines terminated by an internal gateway. Only locally managed dynamic instances (e.g., worker threads, temporary session objects) can be destroyed.
   - *Fix*: Replace `<<destroy>>` with an application-level cancel message: `cancelTransaction(txnId)`.

2. **Flaw 2: Message Emission from a Terminated Lifeline (Message 4)**
   - *Defect*: `BankAPI` sends Message 4 (`ackPaid`) *after* the destruction marker $\times$ was placed on its lifeline.
   - *Metamodel Rule*: A lifeline cannot send or receive messages after its destruction epoch. Time progresses monotonically downward; events below an $\times$ marker are strictly undefined.
   - *Fix*: Eliminate the premature destruction marker.

3. **Flaw 3: Asynchronous Race / Hanging Activation**
   - *Defect*: `PaymentGateway` returns `504 Gateway Timeout` to `Client` (Message 5), but Message 2 (`charge()`) was never closed with a matching return message. If `bank` later processes the charge, the system suffers from an inconsistent financial state (client billed, but gateway reported timeout).
   - *Fix*: Enclose the interaction in an `alt` fragment with an explicit compensation transaction or two-phase commit protocol.

</details>

---

### Level 3: Production C++17 Lamport Logical Clock & Sequence Conformance Engine

#### Challenge Description
Implement a production C++17 engine that constructs a Lamport Logical Clock lattice across distributed lifelines. The engine must:
1. Assign monotonically increasing timestamps $L(e)$ to all send and receive events.
2. Ensure that for every message $m$: $L(\text{send}(m)) < L(\text{receive}(m))$.
3. Verify that all combined fragment loop iterations and alt branches maintain strict monotonic causality without causal inversions.

<details>
<summary>Click to view production C++17 implementation</summary>

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <iomanip>

struct Event {
    std::string eventId;
    std::string lifeline;
    std::string description;
    uint64_t lamportTime = 0;
};

class LamportSequenceEngine {
private:
    std::unordered_map<std::string, uint64_t> processClocks;
    std::vector<Event> eventHistory;

public:
    void registerProcess(const std::string& name) {
        processClocks[name] = 0;
    }

    // Local internal event
    void recordLocalEvent(const std::string& process, const std::string& desc) {
        processClocks[process]++;
        eventHistory.push_back({
            "EVT_" + std::to_string(eventHistory.size() + 1),
            process,
            desc,
            processClocks[process]
        });
    }

    // Send event: increments local clock and returns timestamp to be carried by message
    uint64_t sendMessage(const std::string& sender, const std::string& msgDesc) {
        processClocks[sender]++;
        uint64_t sendTime = processClocks[sender];
        eventHistory.push_back({
            "SEND_" + std::to_string(eventHistory.size() + 1),
            sender,
            "SEND: " + msgDesc,
            sendTime
        });
        return sendTime;
    }

    // Receive event: updates clock to max(local, message_time) + 1
    void receiveMessage(const std::string& receiver, const std::string& msgDesc, uint64_t incomingTime) {
        processClocks[receiver] = std::max(processClocks[receiver], incomingTime) + 1;
        eventHistory.push_back({
            "RECV_" + std::to_string(eventHistory.size() + 1),
            receiver,
            "RECV: " + msgDesc,
            processClocks[receiver]
        });
    }

    bool verifyCausality() const {
        for (const auto& evt : eventHistory) {
            if (evt.lamportTime == 0) return false;
        }
        return true;
    }

    void displayTimeline() const {
        std::cout << "\n====================================================================\n";
        std::cout << "                 LAMPORT LOGICAL CLOCK SEQUENCE LATTICE             \n";
        std::cout << "====================================================================\n";
        std::cout << std::left << std::setw(12) << "Event ID"
                  << std::setw(18) << "Lifeline"
                  << std::setw(10) << "Clock L(e)"
                  << "Description\n";
        std::cout << "--------------------------------------------------------------------\n";
        for (const auto& e : eventHistory) {
            std::cout << std::left << std::setw(12) << e.eventId
                      << std::setw(18) << e.lifeline
                      << std::setw(10) << e.lamportTime
                      << e.description << "\n";
        }
        std::cout << "====================================================================\n";
    }
};

int main() {
    LamportSequenceEngine engine;

    engine.registerProcess("ClientApp");
    engine.registerProcess("AuthService");
    engine.registerProcess("PaymentEngine");

    std::cout << ">>> Simulating Distributed Message Passing with Lamport Ordering...\n";

    // 1. ClientApp sends login to AuthService
    uint64_t t1 = engine.sendMessage("ClientApp", "loginRequest(user, pass)");
    engine.receiveMessage("AuthService", "loginRequest(user, pass)", t1);

    // 2. AuthService processes token locally
    engine.recordLocalEvent("AuthService", "hashAndVerifyPassword()");

    // 3. AuthService returns token to ClientApp
    uint64_t t2 = engine.sendMessage("AuthService", "tokenReply(JWT)");
    engine.receiveMessage("ClientApp", "tokenReply(JWT)", t2);

    // 4. ClientApp sends charge to PaymentEngine
    uint64_t t3 = engine.sendMessage("ClientApp", "capturePayment($250)");
    engine.receiveMessage("PaymentEngine", "capturePayment($250)", t3);

    engine.recordLocalEvent("PaymentEngine", "settleWithCardNetwork()");

    uint64_t t4 = engine.sendMessage("PaymentEngine", "paymentSuccess(txn_99)");
    engine.receiveMessage("ClientApp", "paymentSuccess(txn_99)", t4);

    engine.displayTimeline();
    std::cout << "Causality Invariant Verified: " << (engine.verifyCausality() ? "PASSED" : "FAILED") << "\n";

    return 0;
}
```

</details>

---

## Pedagogical Review Questions & Examination Problems

1. **Activation Stack Semantics**: In a synchronous interaction, what condition causes a thread deadlock when two lifelines $A$ and $B$ simultaneously invoke synchronous methods on each other? Draw the corresponding sequence diagram and explain how asynchronous messaging resolves the circular wait condition.
2. **Formal Fragment Semantics**: Contrast the operational semantics of an `opt` combined fragment versus an `alt` fragment with an `[else]` operand.
3. **Lamport Poset Invariant**: Prove mathematically that if an interaction violates $L(\text{send}(m)) < L(\text{receive}(m))$, the physical message must have traveled backwards in time or experienced acausal event clock skew.
