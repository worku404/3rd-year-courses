# Unit 1 — Introduction to System Analysis, Modelling Paradigms & SDLC Methodologies
## Lesson 3 — System Development Methodologies & Process Lifecycles (SDLC)

### 1. The Classical Waterfall Model: Linear Sequencing & The Late-Stage Integration Fallacy

The **Software Development Life Cycle (SDLC)** is a structured, organizational framework that defines the sequential and iterative phases required to conceive, specify, design, construct, verify, deploy, and maintain an enterprise software application.

In 1970, Dr. Winston W. Royce published the first formal description of the linear sequential process, which became colloquially known as the **Waterfall Model**.

```
+-----------------------------------------------------------------------------------------+
|                              THE CLASSICAL WATERFALL MODEL                              |
|                                                                                         |
|       [ REQUIREMENTS ANALYSIS ]                                                         |
|       (Complete, unambiguous SRS signed off)                                            |
|                 |                                                                       |
|                 v                                                                       |
|           [ SYSTEM ARCHITECTURE & DESIGN ]                                              |
|           (Technical specs, database schemas, component APIs)                           |
|                 |                                                                       |
|                 v                                                                       |
|                 [ IMPLEMENTATION & CODING ]                                             |
|                 (Programmers convert specs into source code)                            |
|                       |                                                                 |
|                       v                                                                 |
|                       [ INTEGRATION & TESTING ]                                         |
|                       (First time modules meet physically!)                             |
|                             |                                                           |
|                             v                                                           |
|                             [ DEPLOYMENT & MAINTENANCE ]                                |
|                             (Product installed in production)                           |
+-----------------------------------------------------------------------------------------+
```

#### Operational Mechanics of the Waterfall Model
1. **Strict Phase Gates (Formal Milestones):** Each phase must be $100\%$ completed, rigorously documented, reviewed, and signed off before the subsequent phase is permitted to initiate.
2. **Heavy Document-Driven Governance:** Every stage produces voluminous written specifications: Software Requirements Specification (SRS), Software Design Description (SDD), and Master Test Plans (MTP).
3. **No Overlapping Phases:** Testing cannot begin until coding is completely finished; coding cannot commence until the entire architectural design is frozen.

#### The Late-Stage Integration Fallacy & The Cost of Change Curve
While Waterfall provides clean management visibility and predictable contractual deadlines, it contains a catastrophic structural flaw: **The Late-Stage Integration Fallacy**.
- Working software is not assembled or executed until the very end of the lifecycle (Month 9 of a 12-month contract).
- When disparate subsystems developed by separate teams are integrated for the first time, subtle requirement misinterpretations, concurrency race conditions, and interface mismatches collide simultaneously.
- **Boehm's Cost of Change Curve:** Barry Boehm's empirical studies demonstrate that the economic cost of repairing a software defect escalates exponentially as the system progresses through the SDLC:

$$\text{Relative Cost to Fix Defect} = \begin{cases} 1\times & \text{Requirements Phase} \\ 3\text{ to }5\times & \text{Design Phase} \\ 10\times & \text{Coding Phase} \\ 50\times & \text{System Integration Testing} \\ 100\text{ to }200\times & \text{Post-Release Production!} \end{cases}$$

In a strict Waterfall process, discovering an ambiguous requirement during the late Testing phase forces an excruciating, costly rollback across all preceding phases.

##### When to Use Waterfall:
Waterfall remains the gold standard for projects characterized by **stable, immutable requirements and safety-critical compliance constraints**:
- Aerospace avionics flight control software (DO-178C).
- Medical device firmware (FDA Class III).
- Nuclear power plant reactor monitoring systems.
- Regulated banking clearinghouses where requirements are legally fixed by national statutes.

{{ media:sam-sdlc-models-diagram }}

---

### 2. The V-Model: Early Verification, Validation Traceability & Test-Level Mapping

To overcome the delayed-testing trap of the Waterfall model without sacrificing formal rigor, systems engineers developed the **V-Model (Verification and Validation Model)**.

The V-Model arranges the development lifecycle as a symmetric **V-shaped trajectory**:
- The **Left Wing (Downward Slope):** Represents the progressive **Decomposition & Specification (Verification)** of requirements into design and code.
- The **Vertex (Base of the V):** Represents physical **Implementation (Coding)**.
- The **Right Wing (Upward Slope):** Represents the progressive **Integration & Assembly (Validation)** of the software into the delivered product.

```
+-----------------------------------------------------------------------------------------+
|                                    THE V-MODEL ARCHITECTURE                             |
|                                                                                         |
|       VERIFICATION PHASES                                      VALIDATION PHASES        |
|       (Building the system right?)                             (Building right system?) |
|                                                                                         |
|       User Requirements (SRS) ==================================> Acceptance Testing    |
|               \                                                   /                     |
|                \                                                 /                      |
|            System Architecture ==========================> System Testing               |
|                    \                                         /                          |
|                     \                                       /                           |
|                  Detailed Design ===================> Integration Testing               |
|                          \                             /                                |
|                           \                           /                                 |
|                            +--- Component Coding ---+                                   |
|                            |     Unit Testing       |                                   |
|                            +------------------------+                                   |
+-----------------------------------------------------------------------------------------+
```

#### Detailed Test-Level Mapping & Traceability Matrix

| Development Stage (Verification) | Corresponding Test Stage (Validation) | Verification Question & Scope | Test Techniques & Artifacts |
| :--- | :--- | :--- | :--- |
| **1. User Requirements (SRS)** | **Acceptance Testing (UAT)** | *"Does the software fulfill the client's business operational goals?"* | Alpha/Beta testing, user scenario walkthroughs, contractual acceptance criteria. |
| **2. System Architecture** | **System Testing** | *"Does the complete integrated system meet end-to-end performance & security SLAs?"* | Load testing, penetration testing, disaster recovery failover, stress testing. |
| **3. Detailed Module Design** | **Integration Testing** | *"Do disparate modules communicate correctly across their shared interface contracts?"* | API contract tests, mock server stubs, database connection pooling tests, middleware verification. |
| **4. Component Implementation**| **Unit Testing** | *"Does an individual function, method, or class compute the correct outputs for given inputs?"* | Automated unit test frameworks (JUnit, GoogleTest), white-box branch coverage, boundary value analysis. |

#### The Fundamental Axiom of the V-Model: Early Test Preparation
In the V-Model, **Test Cases are NOT designed after the code is written!**
- While analysts write the User Requirements, QA architects simultaneously author the **Acceptance Test Suite**.
- While architects draft the System Architecture, the test team authors the **System Integration Test Plans**.
- By designing test cases concurrently with specifications, analysts discover ambiguities, contradictions, and untestable requirements before a single line of code is ever typed!

---

### 3. Evolutionary & Risk-Driven Paradigms: Boehm's Spiral Model

In 1988, Barry Boehm formulated the **Spiral Model**, recognizing that large, unprecedented software systems are dominated by **Uncertainty and Technological Risk**.

The Spiral Model is an evolutionary software process model that couples the iterative nature of prototyping with the controlled, systematic aspects of the linear sequential model.

```
+-----------------------------------------------------------------------------------------+
|                                 BOEHM'S SPIRAL MODEL                                    |
|                                                                                         |
|       QUADRANT 1: DETERMINE OBJECTIVES            QUADRANT 2: IDENTIFY & RESOLVE RISKS  |
|       • Identify alternative solutions            • Risk analysis & technical feasibility|
|       • Define operational constraints            • Rapid software prototyping          |
|       • Establish milestone targets               • Benchmark simulation models         |
|                          \                             /                                |
|                           \       CUMULATIVE          /                                 |
|                            \         COST            /                                  |
|                             \    (Expands Outward)  /                                   |
|                              +---------------------+                                    |
|                              |   START OF SPIRAL   |                                    |
|                              +---------------------+                                    |
|                             /                       \                                   |
|                            /                         \                                  |
|                           /                           \                                 |
|       QUADRANT 4: PLAN NEXT PHASES                QUADRANT 3: ENGINEERING & VERIFY      |
|       • Formal customer review                    • Detailed design & architecture      |
|       • Assess iteration progress                 • Implementation / coding             |
|       • Commit resources for next loop            • Testing, validation & delivery      |
+-----------------------------------------------------------------------------------------+
```

#### The Four Quadrants of Every Spiral Cycle
Each traversal around the spiral sweeps through four distinct functional quadrants:

1. **Quadrant 1: Determine Objectives, Alternatives, and Constraints:**
   - Define the specific goals of the current iteration (e.g., verifying database transaction throughput).
   - Identify alternative design approaches (e.g., Relational PostgreSQL vs NoSQL Cassandra).
   - Enumerate operational constraints (budget, latency budgets, hardware availability).
2. **Quadrant 2: Identify and Resolve Risks (The Heart of the Spiral):**
   - Perform comprehensive **Risk Analysis**.
   - What could cause this project to fail in this iteration?
   - Construct rapid throwaway **Prototypes**, simulation models, or algorithmic benchmarks to physically prove or disprove high-risk architectural assumptions.
3. **Quadrant 3: Develop and Verify Next-Level Product:**
   - Execute the actual engineering work dictated by the risk resolution findings.
   - For early cycles, the deliverable may be an architectural proof-of-concept; for later cycles, it is a fully compiled, tested software release.
4. **Quadrant 4: Plan the Next Phase & Review:**
   - The customer and management evaluate the results of the current iteration.
   - If the project's technical risks are resolved and business value is proven, management commits budget and resources for the next outward spiral loop. If the risk is unacceptable, the project is safely terminated before millions of dollars are wasted!

#### Mathematical Risk Exposure ($RE$) Formulation
In Quadrant 2, risks are prioritized using quantitative **Risk Exposure**:

$$RE = P(\text{UO}) \times L(\text{UO})$$

Where:
- $P(\text{UO})$ = Probability of an Unsatisfactory Outcome ($0.0 \le P \le 1.0$).
- $L(\text{UO})$ = Loss incurred if the unsatisfactory outcome occurs (measured in dollars, weeks of delay, or human safety impact).

Engineering teams rank risks by their calculated $RE$, dedicating prototyping and architectural resources strictly to the highest $RE$ threats first.

---

### 4. Agile Scrum, Rapid Application Development (RAD) & Modern Adaptive Frameworks

#### 1. The Agile Paradigm Shift
In February 2001, seventeen software leaders drafted the **Agile Manifesto**, fundamentally challenging the document-heavy, rigid planning orthodoxy of traditional waterfall methodologies:

```
+-----------------------------------------------------------------------------------------+
|                             THE FOUR CORE AGILE VALUES                                  |
|                                                                                         |
|       1. Individuals and Interactions  OVER  Processes and Tools                        |
|       2. Working Software              OVER  Comprehensive Documentation                |
|       3. Customer Collaboration        OVER  Contract Negotiation                       |
|       4. Responding to Change          OVER  Following a Rigid Plan                     |
+-----------------------------------------------------------------------------------------+
```

#### 2. The Scrum Framework Architecture
Scrum is the most widely adopted operational framework for implementing Agile principles:

```
+-----------------------------------------------------------------------------------------+
|                                THE SCRUM LIFECYCLE                                      |
|                                                                                         |
|       +-------------------+                     +-------------------+                   |
|       |  PRODUCT BACKLOG  |                     |   SPRINT BACKLOG  |                   |
|       | (Prioritized User | === Sprint ======>  | (Committed Tasks  |                   |
|       |     Stories)      |    Planning         |  for next 2 weeks)|                   |
|       +-------------------+                     +-------------------+                   |
|                                                           |                             |
|                                                           v                             |
|                                            +-----------------------------+              |
|                                            |    2 - 4 WEEK SPRINT        |              |
|                                            |  • Daily Standup (15 mins)  |              |
|                                            |  • Burndown Chart Tracking  |              |
|                                            +-----------------------------+              |
|                                                           |                             |
|                                                           v                             |
|       +-------------------+                     +-------------------+                   |
|       | SPRINT REVIEW &   | <================== | POTENTIALLY       |                   |
|       | RETROSPECTIVE     |                     | SHIPPABLE PRODUCT |                   |
|       | (Inspect & Adapt) |                     | INCREMENT         |                   |
|       +-------------------+                     +-------------------+                   |
+-----------------------------------------------------------------------------------------+
```

- **Sprint (Iteration):** A fixed timebox (typically 2 weeks) during which the cross-functional team converts committed backlog user stories into a **Potentially Shippable Product Increment**.
- **The Core Roles:**
  - **Product Owner (PO):** Owns the Product Backlog, defines user stories, and prioritizes features based on business ROI.
  - **Scrum Master:** Servant leader who coaches the team, eliminates external organizational impediments, and ensures Scrum process discipline.
  - **Development Team:** Self-organizing, cross-functional group of engineers (designers, coders, testers) who collectively own sprint delivery.
- **Ceremonies:** Sprint Planning, Daily Scrum (15-minute standup answering: *What did I do yesterday? What will I do today? What blockers exist?*), Sprint Review (live product demo to stakeholders), and Sprint Retrospective (team self-reflection on process improvement).

#### 3. Rapid Application Development (RAD)
Pioneered by James Martin (1991), RAD emphasizes rapid construction of working prototypes using high-productivity visual tools, automated code generators, and Joint Application Design (JAD) stakeholder workshops:
1. **Requirements Planning:** High-level scoping sessions combining users and analysts.
2. **User Design (Interactive Prototyping):** Users interact directly with working visual UI mockups, refining requirements in real time.
3. **Construction:** Automated code generators, reusable components, and rapid integration.
4. **Cutover:** Final acceptance testing, data migration, and immediate production deployment.

#### Comprehensive Methodology Selection Decision Matrix
| Project Dimension / Constraint | Classical Waterfall | V-Model | Boehm's Spiral | Agile Scrum | RAD |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Requirements Stability** | Completely Frozen | Completely Frozen | Evolutionary / Unclear | Highly Volatile / Fluid | Moderately Volatile |
| **Primary Risk Profile** | Low Technical Risk | Compliance / Safety | High Technical Risk | Market / Value Risk | Schedule / Speed Risk |
| **Customer Involvement** | Beginning & End only | Beginning & End | Regular Milestones | Continuous (Daily/Weekly)| Intensive (JAD Workshops) |
| **Delivery Mechanism** | Single Big-Bang Delivery | Single Big-Bang Delivery | Incremental Milestones | Small Sprints (2 weeks) | Rapid Prototypes (60-90 days)|
| **Documentation Burden** | Heavy / Exhaustive | Heavy / Traceable | Moderate / Risk Reports| Light / User Stories | Minimal / Working Models |

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Quantitative SDLC Selection & Risk Assessment

##### Problem Statement
An autonomous aerospace robotics startup is contracted to engineer two distinct software systems:
- **System Alpha (Sub-Orbital Drone Autopilot):** Flight-critical avionics firmware directly actuating thrusters and control surfaces. A software deadlock or unhandled exception will cause the physical vehicle to crash, risking human lives. Requirements are dictated by FAA aerodynamic physics and telemetry standards ($N = 120$ requirements, volatility rate $< 1\%$ per year).
- **System Beta (Passenger In-Flight Entertainment & Tourism Mobile App):** Passenger mobile app allowing passengers to stream 4K movies, order gourmet snacks, and view live augmented-reality geography maps. Market competition is fierce; marketing executives want to experiment with dynamic discounts, social media integration, and UI themes ($N = 45$ initial features, expected volatility $> 40\%$ every quarter).

As Principal Systems Architect, select and justify the optimal SDLC model for each system using formal quantitative criteria.

##### Quantitative Selection Analysis

##### 1. System Alpha Evaluation:
- **Safety Criticality:** Category A (Catastrophic: Loss of Life / Vehicle).
- **Requirements Volatility Index ($RVI$):**
  $$RVI = \frac{\Delta \text{Requirements}}{\text{Total Baseline}} = \frac{1}{120} \approx 0.008 \quad (< 1\%)$$
- **Regulatory Governance:** Mandates strict bidirectional traceability from high-level system requirements down to object code machine instructions (FAA DO-178C Level A).
- **Optimal SDLC Selection:** **The V-Model (augmented with Formal Methods)**.
- *Justification:* Because requirements are physically bounded by aerodynamics, iterative trial-and-error in production is catastrophic. The V-Model's dual-wing verification and validation guarantees that every unit test and integration harness is formally mapped to flight safety specifications prior to coding.

##### 2. System Beta Evaluation:
- **Safety Criticality:** Category E (Inconsequential: Entertainment convenience).
- **Requirements Volatility Index ($RVI$):**
  $$RVI = \frac{18}{45} = 0.40 \quad (40\%\text{ requirement churn per quarter!})$$
- **Market Window:** Must release a Minimum Viable Product (MVP) within 60 days to capture tourism market share.
- **Optimal SDLC Selection:** **Agile Scrum (2-Week Sprints)**.
- *Justification:* Waterfall or V-Model would fail catastrophically: by the time comprehensive specifications were signed off in Month 6, market trends would have shifted, rendering the app obsolete. Agile Scrum allows the Product Owner to pivot features every 14 days based on actual passenger usage analytics.

---

#### Level 2 — Scaffolded Bug-Fix: The "Agile Without Automated Verification" Anti-Pattern

##### Defect Scenario
A fintech banking startup transitioned from Waterfall to "Agile Scrum". To accelerate sprint velocity, the engineering manager mandated that developers write zero automated unit tests, skip code reviews, and eliminate continuous integration gates:
*"We are Agile! Working code is our only metric. We don't have time for documentation or automated testing!"*

By Sprint 8:
- Every new user story committed broke two previously working features (**Catastrophic Regression**).
- Sprint Velocity collapsed from $45\text{ story points}$ in Sprint 1 to $6\text{ story points}$ in Sprint 8.
- Developers spent $90\%$ of every sprint doing manual firefighting and hotfixing production outages.

##### Systems Engineering Diagnosis
The team fell into the notorious **"Flaccid Scrum" / Pseudo-Agile Anti-Pattern**. Agile is not an excuse to abandon engineering discipline; in fact, Agile requires **substantially HIGHER technical discipline** (Automated Testing, Test-Driven Development / TDD, Continuous Integration / CI, and Strict Definitions of Done) than Waterfall, because code is modified and refactored every single day! Without automated regression safety nets, technical debt compounds exponentially.

<details>
<summary><b>View Architectural Solution & Strict Definition of Done (DoD) CI/CD Pipeline</b></summary>

```yaml
# ============================================================================
# ARCHITECTURAL REMEDY: AUTOMATED QUALITY GATE PIPELINE (CI/CD SPECIFICATION)
# Enforces strict "Definition of Done" before any pull request can merge!
# ============================================================================
name: Automated Agile Quality Gate Pipeline

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  verify_code_quality:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v3

      # GATE 1: STATIC CODE ANALYSIS & LINTING
      - name: Static Analysis & Security Scanning
        run: |
          echo ">>> Running SonarQube / Clang-Tidy Static Analysis..."
          # Blocks merge if cyclomatic complexity > 15 or security smells detected
          clang-tidy src/*.cpp -- -Iinclude/

      # GATE 2: AUTOMATED UNIT TESTING & BRANCH COVERAGE
      - name: Compile & Execute Automated Unit Tests
        run: |
          echo ">>> Compiling and Executing GoogleTest Suite..."
          mkdir build && cd build
          cmake .. -DENABLE_COVERAGE=ON
          make -j4
          ctest --output-on-failure
          
      # GATE 3: STRICT CODE COVERAGE ENFORCEMENT
      - name: Verify Code Coverage Threshold
        run: |
          echo ">>> Verifying Code Coverage..."
          # Definition of Done Mandate: PR fails if coverage < 85%!
          lcov --directory build/ --capture --output-file coverage.info
          COVERAGE=$(lcov --summary coverage.info | grep lines | awk '{print $4}' | cut -d'%' -f1)
          echo "Measured Line Coverage: $COVERAGE%"
          if (( $(echo "$COVERAGE < 85.0" | bc -l) )); then
            echo "FAILED: Code coverage ($COVERAGE%) is below mandatory 85% threshold!"
            exit 1
          fi

      # GATE 4: AUTOMATED INTEGRATION & CONTRACT VERIFICATION
      - name: API Contract Tests against Mock Gateway
        run: |
          echo ">>> Running Pact / WireMock API Contract Tests..."
          ./build/integration_tests
```

##### Process Governance Transformation:
1. **Redefined Definition of Done (DoD):** A user story is **NOT DONE** until:
   - Code is peer-reviewed by at least 2 senior engineers.
   - Automated unit tests achieve $\ge 85\%$ branch coverage.
   - Integration tests pass against automated CI containers.
   - Zero critical static security warnings exist.
2. **Velocity Stabilization:** Sprint velocity rebounded to a predictable, sustainable 38 points per sprint with zero production rollbacks!

</details>

---

#### Level 3 — High-Scale System Design: Discrete-Event SDLC Process & Defect Leakage Simulator in C++

Design a complete, mathematically rigorous C++17 discrete-event simulation modeling:
1. **The Three Core SDLC Methodologies:** Classical Waterfall, V-Model, and Agile Scrum.
2. **Defect Injection and Discovery Kinetics:** Injects synthetic requirements, design, and coding defects, tracking the exact phase where defects are discovered.
3. **Boehm's Cost Escalation Model:** Computes cumulative development hours, total rework penalty costs, and final software reliability metrics across all three lifecycles.

<details>
<summary><b>View Complete C++ SDLC Defect Leakage Simulation Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: DISCRETE-EVENT SDLC DEFECT LEAKAGE & COST SIMULATOR
// Compile: g++ -std=c++17 -O3 sdlc_simulator.cpp -o sdlc_simulator
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <random>
#include <cstdint>

enum class SDLCPhase { REQUIREMENTS, DESIGN, CODING, TESTING, PRODUCTION };

struct SoftwareDefect {
    uint32_t id;
    SDLCPhase injected_phase;
    SDLCPhase discovered_phase;
    double fix_cost_usd;
};

class SDLCSimulationModel {
public:
    std::string model_name;
    double base_development_cost;
    double total_rework_cost = 0.0;
    std::vector<SoftwareDefect> defects;

    SDLCSimulationModel(const std::string& name, double base_cost)
        : model_name(name), base_development_cost(base_cost) {}

    // Boehm's Empirical Cost Escalation Multiplier
    double calculate_fix_cost(SDLCPhase injected, SDLCPhase discovered) {
        const double base_cost_per_bug = 200.0; // $200 to fix in requirements

        int delta = static_cast<int>(discovered) - static_cast<int>(injected);
        if (delta <= 0) return base_cost_per_bug;

        // Exponential escalation: 1x -> 4x -> 15x -> 50x -> 150x
        switch (delta) {
            case 1: return base_cost_per_bug * 4.0;   // Caught in next phase ($800)
            case 2: return base_cost_per_bug * 15.0;  // Caught 2 phases later ($3,000)
            case 3: return base_cost_per_bug * 50.0;  // Caught in Testing ($10,000)
            case 4: return base_cost_per_bug * 150.0; // Leaked to Production ($30,000!)
            default: return base_cost_per_bug * 200.0;
        }
    }

    virtual void run_simulation(int num_synthetic_defects) = 0;

    void print_financial_report() const {
        double total_project_cost = base_development_cost + total_rework_cost;
        int leaked_to_production = 0;
        for (const auto& d : defects) {
            if (d.discovered_phase == SDLCPhase::PRODUCTION) leaked_to_production++;
        }

        std::cout << "\n=======================================================\n";
        std::cout << "        SDLC FINANCIAL & QUALITY REPORT: " << model_name << "\n";
        std::cout << "=======================================================\n";
        std::cout << "Base Engineering Cost : $" << std::fixed << std::setprecision(2) << base_development_cost << "\n";
        std::cout << "Total Defect Fix Cost : $" << total_rework_cost << "\n";
        std::cout << "TOTAL PROJECT COST    : $" << total_project_cost << "\n";
        std::cout << "Defects Injected      : " << defects.size() << "\n";
        std::cout << "Production Escapes    : " << leaked_to_production 
                  << " (" << (100.0 * leaked_to_production / defects.size()) << "% Escape Rate!)\n";
        std::cout << "=======================================================\n";
    }
};

// ----------------------------------------------------------------------------
// WATERFALL SIMULATION: HIGH DEFECT LEAKAGE TO TESTING & PRODUCTION
// ----------------------------------------------------------------------------
class WaterfallSimulation : public SDLCSimulationModel {
public:
    WaterfallSimulation() : SDLCSimulationModel("CLASSICAL WATERFALL", 200000.0) {}

    void run_simulation(int num_defects) override {
        // In Waterfall, testing only occurs at the very end!
        // 60% of bugs discovered in late Testing, 25% leak to Production, 15% caught early
        for (int i = 0; i < num_defects; i++) {
            SDLCPhase injected = static_cast<SDLCPhase>(i % 3); // Injected in Req, Design, or Code
            SDLCPhase discovered;

            if (i % 100 < 15) discovered = static_cast<SDLCPhase>(static_cast<int>(injected) + 1);
            else if (i % 100 < 75) discovered = SDLCPhase::TESTING; // Caught late in testing!
            else discovered = SDLCPhase::PRODUCTION;                // Leaked to live users!

            double cost = calculate_fix_cost(injected, discovered);
            total_rework_cost += cost;
            defects.push_back({static_cast<uint32_t>(i), injected, discovered, cost});
        }
    }
};

// ----------------------------------------------------------------------------
// V-MODEL SIMULATION: HIGH VERIFICATION DISCOVERY IN INTERMEDIATE PHASES
// ----------------------------------------------------------------------------
class VModelSimulation : public SDLCSimulationModel {
public:
    VModelSimulation() : SDLCSimulationModel("VERIFICATION & VALIDATION (V-MODEL)", 240000.0) {}

    void run_simulation(int num_defects) override {
        // V-Model catches requirements/design bugs during early test planning!
        for (int i = 0; i < num_defects; i++) {
            SDLCPhase injected = static_cast<SDLCPhase>(i % 3);
            SDLCPhase discovered;

            if (i % 100 < 55) discovered = static_cast<SDLCPhase>(static_cast<int>(injected) + 1); // Caught immediately!
            else if (i % 100 < 92) discovered = SDLCPhase::TESTING;
            else discovered = SDLCPhase::PRODUCTION; // Only 8% escapes!

            double cost = calculate_fix_cost(injected, discovered);
            total_rework_cost += cost;
            defects.push_back({static_cast<uint32_t>(i), injected, discovered, cost});
        }
    }
};

// ----------------------------------------------------------------------------
// AGILE SCRUM SIMULATION: SPRINT-LEVEL CONTINUOUS VERIFICATION
// ----------------------------------------------------------------------------
class AgileScrumSimulation : public SDLCSimulationModel {
public:
    AgileScrumSimulation() : SDLCSimulationModel("AGILE SCRUM (WITH CI/TDD)", 220000.0) {}

    void run_simulation(int num_defects) override {
        // Agile Sprints discover and repair defects within the same 2-week iteration!
        for (int i = 0; i < num_defects; i++) {
            SDLCPhase injected = static_cast<SDLCPhase>(i % 3);
            SDLCPhase discovered;

            if (i % 100 < 80) discovered = injected; // Caught in same sprint via TDD! ($200)
            else if (i % 100 < 96) discovered = static_cast<SDLCPhase>(static_cast<int>(injected) + 1);
            else discovered = SDLCPhase::PRODUCTION; // Only 4% escape!

            double cost = calculate_fix_cost(injected, discovered);
            total_rework_cost += cost;
            defects.push_back({static_cast<uint32_t>(i), injected, discovered, cost});
        }
    }
};

int main() {
    const int total_bugs = 200;

    WaterfallSimulation waterfall;
    waterfall.run_simulation(total_bugs);
    waterfall.print_financial_report();

    VModelSimulation vmodel;
    vmodel.run_simulation(total_bugs);
    vmodel.print_financial_report();

    AgileScrumSimulation agile;
    agile.run_simulation(total_bugs);
    agile.print_financial_report();

    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:sdlc-overview-video }}

In this video by Simplilearn, the foundational phases of the Software Development Life Cycle (SDLC) are explained, highlighting the critical transitions from requirements gathering through testing, deployment, and ongoing maintenance.
