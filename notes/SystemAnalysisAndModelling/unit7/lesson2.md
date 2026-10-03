# Lesson 2 — State Machine Modeling: Harel Statecharts, Orthogonal Regions & Transition Logic

## Executive Summary & Academic Orientation

In reactive software systems engineering, applications do not merely process static input-output transformations; they continuously respond to internal and external asynchronous events while maintaining internal state memory. While interaction models (such as Sequence Diagrams) capture interactions across multiple disparate components, **State Machine Diagrams** (specifically **Harel Statecharts** standardized within the **UML 2.5 Specification**) model the complete, event-driven lifecycle of a single classifier or subsystem.

Classical automata theory—such as finite state machines (FSMs), Mealy machines, and Moore machines—suffers from combinatorial state explosion when applied to complex systems: adding a single independent binary variable doubles the total number of required states ($2^n$). In 1987, computer scientist David Harel solved this fundamental limitation by introducing **Statecharts**, augmenting classical state machines with three revolutionary mechanisms:
1. **Hierarchy (OR-states)**: Super-states encapsulating shared sub-state behaviors and transitions.
2. **Orthogonality (AND-states)**: Concurrently executing sub-state regions that operate independently without multiplicative state cross-products.
3. **History ($H$ and $H^*$)**: Memory pseudostates that preserve and restore previously active sub-state configurations upon re-entry.

This lesson explores the formal mathematical definitions of statecharts, the exact transition execution semantics (entry/exit/do actions, run-to-completion processing), and provides an industrial-grade C++17 hierarchical state machine simulation engine.

```
+-------------------------------------------------------------------------+
|                  HAREL STATECHART CONCURRENCY & DECOMPOSITION           |
|                                                                         |
|  [ Classical Flat FSM ]:                                                |
|  N states * M states = N * M combinatorial state explosion!             |
|                                                                         |
|  [ Harel Statechart with Orthogonal (AND) Regions ]:                    |
|  +-------------------------------------------------------------------+  |
|  | Composite State: ActiveOperation                                  |  |
|  |                                                                   |  |
|  |  Region 1: Telemetry [AND]          Region 2: MotorControl        |  |
|  |  +------------------------+         +------------------------+    |  |
|  |  | (Idle) ---> (Streaming)|         | (Braking) ---> (Drive) |    |  |
|  |  +------------------------+         +------------------------+    |  |
|  |                                                                   |  |
|  +-------------------------------------------------------------------+  |
|  Total state complexity: N + M (Additive rather than Multiplicative!)   |
+-------------------------------------------------------------------------+
```

---

## 2.1 The Discrete-Event State Machine Paradigm: Mealy/Moore vs. Harel Statecharts

### Formal Automata Foundations

In classical computer science, a deterministic finite automaton (DFA) is defined as a 5-tuple:
$$M = \langle Q, \Sigma, \delta, q_0, F \rangle$$
Where:
- $Q$ is a finite set of states.
- $\Sigma$ is a finite input alphabet (events).
- $\delta : Q \times \Sigma \to Q$ is the state transition function.
- $q_0 \in Q$ is the initial state.
- $F \subseteq Q$ is the set of final/accepting states.

In **Moore Machines**, outputs are tied strictly to states: $\lambda : Q \to \Omega$.
In **Mealy Machines**, outputs are tied to transitions: $\lambda : Q \times \Sigma \to \Omega$.

### The Harel Statechart Mathematical Formalism

A Harel statechart expands this tuple to support hierarchy, concurrency, and broadcast communication:
$$\mathcal{SC} = \langle S, E, T, \mathcal{H}, \mathcal{R}, \sigma_0 \rangle$$
Where:
- $S$ is a tree-structured set of states, partitioned into basic states, OR-composite states, and AND-orthogonal states.
- $\mathcal{H} : S \to \mathcal{P}(S)$ defines the hierarchical parent-child nesting function.
- $\mathcal{R}$ is the set of orthogonal regions executing concurrently.
- $T \subseteq S \times E \times C \times A \times S$ is the transition relation, where each transition specifies $\langle \text{source}, \text{event}, \text{guard}, \text{action}, \text{target} \rangle$.

```
+-------------------------------------------------------------------------+
|                  FSM COMPARISON: CLASSICAL VS. HAREL                    |
|                                                                         |
|  Feature            | Classical Flat FSM     | UML Harel Statechart     |
| :------------------ | :--------------------- | :----------------------- |
|  State Hierarchy    | Strictly Flat (1-tier) | Arbitrary Recursive Nest |
|  Concurrency        | Single thread of state | Orthogonal AND-Regions    |
|  State Memory       | None (Forgets on exit) | Shallow/Deep History (H) |
|  Internal Actions   | Non-standardized       | entry, exit, do activity |
|  Execution Model    | Immediate trigger      | Run-to-Completion (RTC)   |
+-------------------------------------------------------------------------+
```

---

## 2.2 State Anatomy: Compartments, Entry, Exit, and Do Activities

In the UML 2.5 metamodel, a `State` is rendered as a rectangle with rounded corners, partitioned into distinct functional compartments:

```
+-------------------------------------------------------------------------+
|                        UML 2.5 STATE ANATOMY                            |
|                                                                         |
|   +-----------------------------------------------------------------+   |
|   |                       CONNECTED_SECURE                          |   |
|   +-----------------------------------------------------------------+   |
|   | entry / sendHandshakeAck(); startHeartbeatTimer()               |   |
|   | exit  / flushOutputBuffer(); releaseSocketHandle()              |   |
|   | do    / monitorInboundTrafficStream()                           |   |
|   | ping  / sendPongResponse()  [Internal Transition]               |   |
|   +-----------------------------------------------------------------+   |
+-------------------------------------------------------------------------+
```

### The Three Primitive Internal Behaviors

1. **`entry / actionList`**:
   - Atomic action executed immediately upon crossing the state boundary into this state.
   - Guaranteed to execute before any internal transitions or `do` activities commence.
   - Non-interruptible.
2. **`exit / actionList`**:
   - Atomic action executed immediately when departing this state, regardless of which outgoing transition was triggered.
   - Ideal for releasing locks, tearing down network sockets, or cleaning memory heaps.
3. **`do / ongoingActivity`**:
   - Long-running, interruptible background work that executes continuously while the state remains active.
   - If an outgoing transition triggers, the `do` activity is preemptively aborted before the `exit` action executes.
4. **Internal Transition (`eventName [guard] / action`)**:
   - Executes an action without exiting and re-entering the state. Neither `exit` nor `entry` actions are triggered.

---

## Visual Architecture: Harel Statecharts & Guarded Transitions

{{ media:sam-state-machine-diagram }}

### Multimedia Deep-Dive: Operating System States & State Machine Concurrency
Explore how operating systems, kernels, and reactive runtimes manage state transitions, process queues, and concurrency:

{{ media:state-machine-video }}

---

## 2.3 Transition Semantics: Trigger Events, Guard Conditions, and Action Effects

The canonical UML 2.5 transition syntax follows a strict structural grammar:

$$\text{TriggerEvent} \quad [\text{GuardCondition}] \quad / \quad \text{ActionEffect}$$

```
+-------------------------------------------------------------------------+
|                     TRANSITION SYNTAX & EXECUTION FLOW                  |
|                                                                         |
|                cardInserted [isChipValid == true] / lockSlot()          |
|  [ WAITING ] -------------------------------------------------> [ AUTH ]|
|                                                                         |
|  1. TriggerEvent: "cardInserted" arrives in event queue.                |
|  2. GuardCondition: "[isChipValid == true]" evaluates to true.          |
|  3. Source State Exit: WAITING.exit() executes.                         |
|  4. ActionEffect: "lockSlot()" executes during transition passage.      |
|  5. Target State Entry: AUTH.entry() executes.                          |
|  6. Target State Do: AUTH.doActivity() spawns.                          |
+-------------------------------------------------------------------------+
```

### The Run-to-Completion (RTC) Processing Model
In UML 2.5 state machines, events are evaluated according to the **Run-to-Completion (RTC)** guarantee:
- The state machine processes one event at a time from its inbound FIFO dispatch queue.
- An event step is only complete when all triggered entry/exit actions, transition effects, and stable state configurations have been established.
- Incoming external events arriving while an RTC step is in progress are queued and never preempt an active transition step.

---

## 2.4 Composite States and Orthogonal (AND) Concurrency Regions

```
+-------------------------------------------------------------------------+
|                  ORTHOGONAL REGIONS IN COMPOSITE STATES                 |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  | OPERATIONAL_MODE                                                  |  |
|  |                                                                   |  |
|  |  Region A (Navigation Engine)                                     |  |
|  |  ● ---> [ GPS_ACQUIRING ] ---> (fixLocked) ---> [ WAYPOINT_NAV ]  |  |
|  |                                                                   |  |
|  |  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  |  |
|  |                                                                   |  |
|  |  Region B (Payload Management)                                    |  |
|  |  ● ---> [ SENSORS_CALIBRATING ] ---> (ready) ---> [ RECORDING ]   |  |
|  +-------------------------------------------------------------------+  |
|         |                                                               |
|         | emergencyLandSignal / abortAllRegions()                       |
|         v                                                               |
|    [ EMERGENCY_LANDING ]                                                |
+-------------------------------------------------------------------------+
```

### Orthogonal Region Invariants
1. **Simultaneous Sub-state Residence**: When composite state `OPERATIONAL_MODE` is active, the system resides in exactly one sub-state of Region A AND exactly one sub-state of Region B concurrently.
2. **High-Level Preemption (Group Transitions)**: An outgoing transition originating on the boundary of `OPERATIONAL_MODE` (e.g., `emergencyLandSignal`) immediately terminates all active sub-states across all internal regions simultaneously, executing their respective exit actions in innermost-to-outermost order.

---

## 2.5 Pseudostates: Choice, Junction, History ($H$ vs. $H^*$), and Final States

```
+-------------------------------------------------------------------------+
|                        UML 2.5 PSEUDOSTATE TAXONOMY                     |
|                                                                         |
|  Symbol | Name              | Formal Operational Semantics              |
| :------ | :---------------- | :---------------------------------------- |
|  ●      | **Initial**       | Default start point within a region.       |
|  (●)    | **Final State**   | Indicates completion of enclosing region.  |
|  <>     | **Junction**      | Static merge/split; all guards pre-checked.|
|  /\     | **Choice**        | Dynamic branching evaluated at arrival.    |
|  (H)    | **Shallow History**| Restores most recent 1st-level sub-state. |
|  (H*)   | **Deep History**  | Recursively restores full nested sub-tree. |
|  (X)    | **Terminate**     | Destroys the state machine context.        |
+-------------------------------------------------------------------------+
```

### Shallow History ($H$) vs. Deep History ($H^*$)
Suppose composite state $C$ contains sub-states $S_1$ and $S_2$, where $S_2$ is itself a composite state containing $SubA$ and $SubB$.
- If the system is currently in $SubB$ and is interrupted by an external transition out of $C$:
  - Re-entering via **Shallow History ($H$)** restores state $S_2$, which then drops into its default initial sub-state ($SubA$).
  - Re-entering via **Deep History ($H^*$)** restores $S_2$ and restores the nested sub-state $SubB$.

---

## 2.6 Production Modern C++17 Hierarchical State Machine Engine

The following industrial C++17 simulation engine implements a robust Hierarchical State Machine (HSM) with entry/exit action chains, guard predicates, and run-to-completion event processing.

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <functional>
#include <queue>
#include <cassert>

// ============================================================================
// HAREL STATE MACHINE METAMODEL (C++17)
// ============================================================================

struct State;

struct Transition {
    std::string eventName;
    std::function<bool()> guard;
    std::function<void()> action;
    std::string targetStateName;
};

struct State {
    std::string name;
    std::string parentStateName = ""; // Empty string denotes top-level state
    std::function<void()> entryAction = nullptr;
    std::function<void()> exitAction = nullptr;
    std::function<void()> doActivity = nullptr;
    std::vector<Transition> outgoingTransitions;
    std::string defaultSubState = "";
};

class HierarchicalStateMachine {
private:
    std::unordered_map<std::string, State> states;
    std::string currentStateName;
    std::string deepHistoryState = "";
    std::queue<std::string> eventQueue;
    bool isProcessing = false;

    // Computes path from current state up to root
    std::vector<std::string> getStatePathToRoot(const std::string& stateName) const {
        std::vector<std::string> path;
        std::string curr = stateName;
        while (!curr.empty()) {
            path.push_back(curr);
            curr = states.at(curr).parentStateName;
        }
        return path;
    }

    // Finds Lowest Common Ancestor (LCA) between source and target state
    std::string findLCA(const std::string& src, const std::string& tgt) const {
        auto srcPath = getStatePathToRoot(src);
        auto tgtPath = getStatePathToRoot(tgt);
        for (const auto& s : srcPath) {
            for (const auto& t : tgtPath) {
                if (s == t) return s;
            }
        }
        return "";
    }

public:
    void addState(const State& state) {
        states[state.name] = state;
    }

    void initialize(const std::string& initialStateName) {
        currentStateName = initialStateName;
        std::cout << "[INIT] Bootstrapping State Machine at: " << currentStateName << "\n";
        auto path = getStatePathToRoot(currentStateName);
        // Execute entry actions from top-down
        for (auto it = path.rbegin(); it != path.rend(); ++it) {
            if (states[*it].entryAction) {
                std::cout << "  -> Entry: " << *it << "\n";
                states[*it].entryAction();
            }
        }
    }

    void postEvent(const std::string& eventName) {
        eventQueue.push(eventName);
        if (!isProcessing) {
            processEventQueue();
        }
    }

    void processEventQueue() {
        isProcessing = true;
        while (!eventQueue.empty()) {
            std::string evt = eventQueue.front();
            eventQueue.pop();
            executeRunToCompletionStep(evt);
        }
        isProcessing = false;
    }

    void executeRunToCompletionStep(const std::string& eventName) {
        std::cout << "\n[EVENT DISPATCH] Processing Event: '" << eventName 
                  << "' (Current State: " << currentStateName << ")\n";

        // Search for matching transition starting from current state up the hierarchy
        std::string inspectState = currentStateName;
        const Transition* matchedTransition = nullptr;

        while (!inspectState.empty()) {
            const auto& stateObj = states.at(inspectState);
            for (const auto& trans : stateObj.outgoingTransitions) {
                if (trans.eventName == eventName) {
                    if (!trans.guard || trans.guard()) {
                        matchedTransition = &trans;
                        break;
                    }
                }
            }
            if (matchedTransition) break;
            inspectState = stateObj.parentStateName;
        }

        if (!matchedTransition) {
            std::cout << "  [NO-OP] Event '" << eventName << "' ignored in state: " << currentStateName << "\n";
            return;
        }

        // Execute Transition Passage
        std::string targetState = matchedTransition->targetStateName;
        std::string lca = findLCA(currentStateName, targetState);

        // 1. Exit active states from current up to (but not including) LCA
        std::string exitCursor = currentStateName;
        while (exitCursor != lca && !exitCursor.empty()) {
            if (states[exitCursor].exitAction) {
                std::cout << "  <- Exit: " << exitCursor << "\n";
                states[exitCursor].exitAction();
            }
            exitCursor = states[exitCursor].parentStateName;
        }

        // 2. Execute Transition Action Effect
        if (matchedTransition->action) {
            std::cout << "  == Action Effect Executed ==\n";
            matchedTransition->action();
        }

        // 3. Enter states from below LCA down to target
        auto targetPath = getStatePathToRoot(targetState);
        std::vector<std::string> toEnter;
        for (const auto& s : targetPath) {
            if (s == lca) break;
            toEnter.push_back(s);
        }

        for (auto it = toEnter.rbegin(); it != toEnter.rend(); ++it) {
            if (states[*it].entryAction) {
                std::cout << "  -> Entry: " << *it << "\n";
                states[*it].entryAction();
            }
        }

        // Handle composite state default sub-states
        std::string finalLanding = targetState;
        while (!states[finalLanding].defaultSubState.empty()) {
            finalLanding = states[finalLanding].defaultSubState;
            std::cout << "  -> Auto-drilldown into Default Sub-State: " << finalLanding << "\n";
            if (states[finalLanding].entryAction) {
                states[finalLanding].entryAction();
            }
        }

        currentStateName = finalLanding;
        std::cout << "[TRANSITION COMPLETE] New Active State: " << currentStateName << "\n";
    }

    std::string getCurrentState() const { return currentStateName; }
};

int main() {
    HierarchicalStateMachine hsm;

    // Construct ATM Controller State Machine
    // Root States: IDLE, IN_TRANSACTION (Composite), MAINTENANCE
    // IN_TRANSACTION contains sub-states: AUTHENTICATING, SELECTING_ACTION, DISPENSING

    bool cardValid = true;
    double accountBalance = 500.0;
    double withdrawAmount = 100.0;

    // 1. IDLE State
    hsm.addState({
        "IDLE", "",
        []() { std::cout << "      [IDLE] Displaying 'Insert Card' greeting screen.\n"; },
        []() { std::cout << "      [IDLE] Card reader motor energized.\n"; },
        nullptr,
        {
            {"insertCard", [&]() { return cardValid; }, []() { std::cout << "      [ACTION] Card chip recognized.\n"; }, "IN_TRANSACTION"}
        },
        ""
    });

    // 2. IN_TRANSACTION (Composite Super-State)
    hsm.addState({
        "IN_TRANSACTION", "",
        []() { std::cout << "      [IN_TXN] Session lock acquired. Encryption keys loaded.\n"; },
        []() { std::cout << "      [IN_TXN] Session destroyed. Card ejected. Receipt printed.\n"; },
        nullptr,
        {
            {"cancelButton", nullptr, []() { std::cout << "      [ACTION] User pressed cancel.\n"; }, "IDLE"},
            {"timeout", nullptr, []() { std::cout << "      [ACTION] Inactivity timeout triggered.\n"; }, "IDLE"}
        },
        "AUTHENTICATING" // Default sub-state
    });

    // 3. Sub-State: AUTHENTICATING
    hsm.addState({
        "AUTHENTICATING", "IN_TRANSACTION",
        []() { std::cout << "      [AUTH] Prompting for PIN entry.\n"; },
        []() { std::cout << "      [AUTH] Clearing PIN buffer from volatile RAM.\n"; },
        nullptr,
        {
            {"pinEntered", nullptr, []() { std::cout << "      [ACTION] PIN verified by banking switch.\n"; }, "SELECTING_ACTION"}
        },
        ""
    });

    // 4. Sub-State: SELECTING_ACTION
    hsm.addState({
        "SELECTING_ACTION", "IN_TRANSACTION",
        []() { std::cout << "      [SELECT] Displaying main account operations menu.\n"; },
        nullptr,
        nullptr,
        {
            {"selectWithdraw", [&]() { return accountBalance >= withdrawAmount; },
             []() { std::cout << "      [ACTION] Funds reserved on core ledger.\n"; }, "DISPENSING"}
        },
        ""
    });

    // 5. Sub-State: DISPENSING
    hsm.addState({
        "DISPENSING", "IN_TRANSACTION",
        []() { std::cout << "      [DISPENSE] Currency dispenser motor active.\n"; },
        []() { std::cout << "      [DISPENSE] Shutter closed.\n"; },
        nullptr,
        {
            {"cashTaken", nullptr, []() { std::cout << "      [ACTION] Cash sensor confirmed removal.\n"; }, "IDLE"}
        },
        ""
    });

    // Run Simulation Trace
    hsm.initialize("IDLE");

    std::cout << "\n=======================================================\n";
    hsm.postEvent("insertCard");
    hsm.postEvent("pinEntered");
    hsm.postEvent("selectWithdraw");
    hsm.postEvent("cashTaken");
    std::cout << "=======================================================\n";

    return 0;
}
```

---

## 3-Tier Progressive Practice Suite

### Level 1: Guided Architectural Walkthrough & State Transition Table Derivation

#### Problem Statement
An autonomous warehouse robotics platform operates under four distinct states:
1. `DOCK_CHARGING`
2. `TRANSIT_TO_SHELF`
3. `LIFTING_PAYLOAD`
4. `OBSTACLE_AVOIDANCE`

Derive the formal **State Transition Table** for the following event specifications:
- In `DOCK_CHARGING`: Receiving `batteryFull` transitions to `TRANSIT_TO_SHELF`.
- In `TRANSIT_TO_SHELF`: Receiving `lidarHazardDetected [distance < 1.0m]` transitions to `OBSTACLE_AVOIDANCE`. Receiving `waypointReached` transitions to `LIFTING_PAYLOAD`.
- In `OBSTACLE_AVOIDANCE`: Receiving `pathClear` transitions back to `TRANSIT_TO_SHELF`. Receiving `stuckTimeout` transitions to `DOCK_CHARGING`.
- In `LIFTING_PAYLOAD`: Receiving `payloadSecured` transitions to `TRANSIT_TO_SHELF`.

#### Guided Solution: State Transition Table

| Current State ($s_t$) | Trigger Event ($e$) | Guard Condition ($[g]$) | Target State ($s_{t+1}$) | Action Effect ($/a$) |
| :--- | :--- | :--- | :--- | :--- |
| `DOCK_CHARGING` | `batteryFull` | `[true]` | `TRANSIT_TO_SHELF` | `disengageChargingDock()` |
| `TRANSIT_TO_SHELF` | `lidarHazardDetected` | `[distance < 1.0m]` | `OBSTACLE_AVOIDANCE` | `applyEmergencyBrakes()` |
| `TRANSIT_TO_SHELF` | `waypointReached` | `[shelfAligned]` | `LIFTING_PAYLOAD` | `engageHydraulicLift()` |
| `OBSTACLE_AVOIDANCE` | `pathClear` | `[true]` | `TRANSIT_TO_SHELF` | `resumePathPlanning()` |
| `OBSTACLE_AVOIDANCE` | `stuckTimeout` | `[after 60s]` | `DOCK_CHARGING` | `emitRescueBeacon(); rth()` |
| `LIFTING_PAYLOAD` | `payloadSecured` | `[weightOK]` | `TRANSIT_TO_SHELF` | `lockCargoBay()` |

---

### Level 2: Scaffolded Troubleshooting / Bug-Fix Challenge

#### Challenge Description
A medical infusion pump controller firmware exhibits an intermittent deadlock. The state machine model is defined with two orthogonal regions inside composite state `ACTIVE_INFUSION`:
- **Region 1 (Motor Dosage)**: `● ---> [RUNNING] ---> (flowRateExceeded) ---> [SHUTDOWN]`
- **Region 2 (Pressure Sensor)**: `● ---> [NORMAL] ---> (overpressureDetected) ---> [SHUTDOWN]`

In testing, when both `flowRateExceeded` and `overpressureDetected` occur within 2 milliseconds of each other, the firmware hangs and watchdog timer resets the microcontroller.

Identify the two metamodel and concurrency flaws causing this critical medical defect.

<details>
<summary>Click to view solution & walkthrough</summary>

#### Diagnostic Breakdown

1. **Defect 1: State Cross-Region Scope Ambiguity (Local vs. Global Shutdown)**
   - *Symptom*: Transitions inside Region 1 and Region 2 both target a state labeled `SHUTDOWN`.
   - *Metamodel Rule*: An orthogonal region cannot arbitrarily terminate another parallel region by transitioning into a local sub-state. If `SHUTDOWN` is local to Region 1, Region 2 continues pumping medicine despite the motor error!
   - *Hazard*: Patient overdose or equipment destruction.

2. **Defect 2: Race Condition and Event Queue Contention under RTC**
   - *Symptom*: Two simultaneous fatal error events compete in the event queue without an explicit high-level composite exit.
   - *Architectural Fix*:
     - Lift `SHUTDOWN` out of the orthogonal sub-regions to become a peer top-level state alongside `ACTIVE_INFUSION`.
     - Replace internal local transitions with a single high-level group transition originating from the perimeter of `ACTIVE_INFUSION`:
       `[ACTIVE_INFUSION] -------------------> [GLOBAL_ALARM_SHUTDOWN]`
       `trigger: hardwareAlert [isCriticalFault == true]`
     - Because group transitions exit the entire composite state, all orthogonal regions are guaranteed to abort cleanly in a deterministic, single-step RTC cycle.

</details>

---

### Level 3: Production C++17 Orthogonal Concurrency Statechart Engine

#### Challenge Description
Implement a production C++17 multi-region statechart engine that supports:
1. Composite states containing two orthogonal (AND) regions running simultaneously.
2. Synchronized joint transitions where both regions must reach a synchronization barrier before triggering an outer composite transition.
3. Clean thread-safe event queue processing.

<details>
<summary>Click to view production C++17 implementation</summary>

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <atomic>
#include <mutex>
#include <condition_variable>

class OrthogonalStatechartSimulator {
public:
    struct RegionState {
        std::string regionName;
        std::string activeSubState;
        bool isCompleted = false;
    };

private:
    std::mutex mtx;
    std::string compositeStateName = "FLIGHT_SYSTEM_RUNNING";
    std::unordered_map<std::string, RegionState> regions;

public:
    OrthogonalStatechartSimulator() {
        regions["AvionicsRegion"] = {"AvionicsRegion", "STANDBY", false};
        regions["PropulsionRegion"] = {"PropulsionRegion", "IDLE_CHAMBER", false};
    }

    void dispatchEvent(const std::string& targetRegion, const std::string& eventName) {
        std::lock_guard<std::mutex> lock(mtx);
        std::cout << "[EVENT] Region: " << targetRegion << " received '" << eventName << "'\n";

        if (regions.find(targetRegion) == regions.end()) return;

        auto& r = regions[targetRegion];

        if (targetRegion == "AvionicsRegion") {
            if (r.activeSubState == "STANDBY" && eventName == "lockSensors") {
                r.activeSubState = "NAV_ACTIVE";
                std::cout << "  -> Avionics transitioned to NAV_ACTIVE\n";
            } else if (r.activeSubState == "NAV_ACTIVE" && eventName == "routeComplete") {
                r.activeSubState = "AVIONICS_DONE";
                r.isCompleted = true;
                std::cout << "  -> Avionics reached Join Synchronization Point\n";
            }
        } else if (targetRegion == "PropulsionRegion") {
            if (r.activeSubState == "IDLE_CHAMBER" && eventName == "igniteThruster") {
                r.activeSubState = "BURN_ACTIVE";
                std::cout << "  -> Propulsion transitioned to BURN_ACTIVE\n";
            } else if (r.activeSubState == "BURN_ACTIVE" && eventName == "burnExhausted") {
                r.activeSubState = "PROPULSION_DONE";
                r.isCompleted = true;
                std::cout << "  -> Propulsion reached Join Synchronization Point\n";
            }
        }

        // Check Joint Join Synchronization Condition
        checkJointTransition();
    }

    void checkJointTransition() {
        bool allCompleted = true;
        for (const auto& [name, reg] : regions) {
            if (!reg.isCompleted) {
                allCompleted = false;
                break;
            }
        }

        if (allCompleted) {
            std::cout << "\n=======================================================\n";
            std::cout << "  [JOINT TRANSITION TRIGGERED]: Both Orthogonal Regions\n";
            std::cout << "  Completed! Exiting " << compositeStateName << "\n";
            std::cout << "  ===> New State: LANDING_TOUCHDOWN_SAFE <===\n";
            std::cout << "=======================================================\n";
            compositeStateName = "LANDING_TOUCHDOWN_SAFE";
        }
    }

    void printStateConfiguration() {
        std::lock_guard<std::mutex> lock(mtx);
        std::cout << "\n--- Current Statechart Configuration ---\n";
        std::cout << "Composite State: " << compositeStateName << "\n";
        for (const auto& [name, reg] : regions) {
            std::cout << "  * " << name << " -> Active State: [" << reg.activeSubState 
                      << "] (Completed: " << (reg.isCompleted ? "YES" : "NO") << ")\n";
        }
        std::cout << "----------------------------------------\n\n";
    }
};

int main() {
    OrthogonalStatechartSimulator sim;

    sim.printStateConfiguration();

    // Fire events in interleaved concurrent order
    sim.dispatchEvent("AvionicsRegion", "lockSensors");
    sim.dispatchEvent("PropulsionRegion", "igniteThruster");

    sim.printStateConfiguration();

    // Advance Propulsion to completion first
    sim.dispatchEvent("PropulsionRegion", "burnExhausted");
    sim.printStateConfiguration();

    // Now advance Avionics to completion (triggers Join Barrier)
    sim.dispatchEvent("AvionicsRegion", "routeComplete");
    sim.printStateConfiguration();

    return 0;
}
```

</details>

---

## Pedagogical Review Questions & Examination Problems

1. **State Explosion Proof**: Mathematically prove why a classical flat FSM modeling a mobile device with 4 network states (WiFi, LTE, 5G, Airplane), 3 battery states (Full, Low, Critical), and 2 lock states (Locked, Unlocked) requires 24 discrete states, whereas an orthogonal Harel statechart requires only 9.
2. **History Pseudostate Recovery**: An audio player is in state `PLAYING` within sub-state `TRACK_07` when an incoming phone call interrupts it into state `VOICE_CALL`. When the call ends, the user expects playback to resume at `TRACK_07`. Explain whether a Shallow History ($H$) or Deep History ($H^*$) pseudostate is required if the track list is nested inside a playlist container.
3. **Run-to-Completion Invariants**: Why does UML 2.5 forbid preemption of an active run-to-completion step by external events? How does this guarantee transactional integrity in state machines?
