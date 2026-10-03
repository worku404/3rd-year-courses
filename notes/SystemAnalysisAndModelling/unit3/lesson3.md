# Unit 3 — System Requirements Engineering, Elicitation Techniques & Analysis Paradigms
## Lesson 3 — Fact-Finding Elicitation Techniques (JAD, Interviews, Observation) & Structured vs. Object-Oriented Analysis

### 1. The Fact-Finding & Requirements Elicitation Spectrum

Requirements do not exist waiting to be "collected" like stones on a beach. Stakeholders often have vague notions of their problems, confuse symptoms with root causes, omit tacit domain knowledge, and disagree with colleagues across departmental silos. Therefore, software engineers practice **active elicitation**—systematic fact-finding techniques designed to uncover, clarify, and synthesize genuine system requirements.

{{ media:sam-elicitation-paradigms-diagram }}

```
+---------------------------------------------------------------------------------------------------+
|                        THE SPECTRUM OF FACT-FINDING ELICITATION TECHNIQUES                        |
|                                                                                                   |
|  TECHNIQUE:            QUALITATIVE DEPTH:    QUANTITATIVE REACH:   COST & EFFORT:  CHIEF RISK:    |
|  * Personal Interviews High / Exploratory    Low (Small sample)    Very High       Analyst Bias   |
|  * Questionnaires      Low / Fixed Options   Very High (Mass scale)Low             Shallow Data   |
|  * JAD Workshops       High / Consensus      Medium (Key leaders)  High (3-5 days) Dominant Voices|
|  * Observation         High (Ground truth)   Low (Specific desks)  Medium          Hawthorne Eff. |
|  * Document Review     Medium (Historical)   High (Existing specs) Low             Stale Rules    |
+---------------------------------------------------------------------------------------------------+
```

---

### 2. Deep Dive: Personal Interviews (Structured vs. Unstructured)

Interviewing remains the single most common and versatile fact-finding technique in system analysis. It provides the analyst with facial expressions, hesitations, vocal inflections, and immediate follow-up capabilities.

#### 2.1 Unstructured (Exploratory) Interviews
- **Characteristics:** The analyst conducts a fluid, open-ended conversation without a rigid script.
- **Appropriate Phase:** Early project inception when the problem boundary is unknown.
- **Key Advantage:** Discovers unforeseen issues, organizational politics, and hidden operational bottlenecks that would never appear on a questionnaire.
- **Limitation:** High variance; subjective; difficult to compare responses mathematically across different respondents; consumes excessive analyst time.

#### 2.2 Structured (Formal) Interviews
- **Characteristics:** The analyst prepares an exact list of standardized, predetermined questions presented in uniform order to every interviewee.
- **Appropriate Phase:** Mid-analysis when testing specific functional hypotheses, data structures, or transaction frequencies.
- **Question Types:**
  - *Closed-Ended:* *"How many loan applications does your department approve per hour? [A: < 10, B: 10-50, C: > 50]"* (Quantifiable, fast).
  - *Open-Ended:* *"What specific manual workarounds do you perform when the central database times out?"* (Reveals error handling procedures).

---

### 3. Survey Questionnaires & Statistical Sampling

When system users are geographically dispersed, numbering in the hundreds or thousands, personal interviews are economically and logistically impossible. Analysts deploy **Questionnaires**.

#### 3.1 Design Principles for Requirements Questionnaires
1. **Likert Scales for Nuanced Feedback:** Measuring user satisfaction and feature criticality along standard 5-point or 7-point scales:
   $$\text{[ 1: Strongly Disagree ]} \longleftrightarrow \text{[ 3: Neutral ]} \longleftrightarrow \text{[ 5: Strongly Agree ]}$$
2. **Preventing Leading Questions:**
   - *Biased:* *"Do you agree that our current clunky legacy portal should be replaced by a modern web app?"*
   - *Objective:* *"Rate your efficiency when executing monthly inventory audits using the current legacy portal."*
3. **Statistical Sample Sizing (Yamane Formulation):**
   To determine the required sample size $n$ from a total user population $N$ with a margin of error $e$ (typically $e = 0.05$ for $95\%$ confidence):
   $$n = \frac{N}{1 + N(e)^2}$$
   *For an enterprise organization with $N = 5,000$ employees and $e = 0.05$:*
   $$n = \frac{5000}{1 + 5000(0.0025)} = \frac{5000}{13.5} \approx 370.4 \implies \text{Minimum } 371 \text{ completed surveys}.$$

---

### 4. Joint Application Development (JAD)

Developed by Chuck Morris and Tony Crawford at IBM in the late 1970s, **Joint Application Development (JAD)** is a structured, intensive workshop methodology that compresses months of serial interviews and conflicting email threads into a 3-to-5-day collaborative engineering summit.

```
+---------------------------------------------------------------------------------------------------+
|                            THE JAD WORKSHOP ORGANIZATIONAL TOPOLOGY                               |
|                                                                                                   |
|                         +-----------------------------------+                                     |
|                         |       EXECUTIVE SPONSOR           |                                     |
|                         | (Authorizes Budget & Scope Bounds)|                                     |
|                         +-----------------------------------+                                     |
|                                          |                                                        |
|                                          v                                                        |
|  +--------------------+         +------------------+         +--------------------+               |
|  | BUSINESS USERS &   | <=====> | JAD FACILITATOR  | <=====> | SOFTWARE ARCHITECTS|               |
|  | OPERATIONS REPS    |         | (Neutral Driver) |         | & SYSTEM ANALYSTS  |               |
|  +--------------------+         +------------------+         +--------------------+               |
|            |                             |                             |                          |
|            +-----------------------------+-----------------------------+                          |
|                                          |                                                        |
|                                          v                                                        |
|                         +-----------------------------------+                                     |
|                         |             SCRIBE                |                                     |
|                         | (Documents Consensus in Live SRS) |                                     |
|                         +-----------------------------------+                                     |
+---------------------------------------------------------------------------------------------------+
```

#### 4.1 Key JAD Roles & Responsibilities
1. **The JAD Facilitator (Leader):** A specially trained, neutral moderator who does not contribute technical opinions or business rules. The facilitator enforces ground rules, resolves interpersonal conflicts, keeps discussion on agenda, and ensures all participants speak.
2. **Executive Sponsor:** Senior corporate officer who kicks off the workshop, defines the strategic constraints, signs off on major financial trade-offs, and delegates decision authority.
3. **Business Users & Subject Matter Experts (SMEs):** The ground-truth operational staff who describe daily workflows, data anomalies, and operational pain points.
4. **System Analysts & Software Architects:** Technical professionals who listen to business needs, evaluate technical feasibility, estimate architectural costs, and suggest computational abstractions.
5. **The Scribe (Recorder):** Dedicated recorder who captures all agreed definitions, decision tables, UI wireframes, and open issues into the CASE tool / requirements repository in real-time.

---

### 5. Field Observation & The Hawthorne Effect

**Direct Observation** involves the systems analyst physically or digitally embedding themselves in the user's operational workplace to observe real-world behaviors, transaction volumes, and manual workarounds.

* **Passive Observation:** The analyst sits quietly, recording time-and-motion data without interrupting.
* **Active (Participant) Observation:** The analyst periodically stops the worker to ask why a specific branch was taken or what an error message meant.

#### 5.1 The Hawthorne Effect (Observer Invariant)
First identified during studies at Western Electric's Hawthorne Works (1924–1932), the **Hawthorne Effect** states:
> *Human subjects involuntarily alter their behavior, working faster, making fewer errors, and adhering strictly to official rules simply because they are aware of being actively observed.*

To mitigate the Hawthorne Effect, modern analysts employ **Automated Telemetry & Process Mining**:
- Analyzing passive system audit logs (Event log mining via algorithms like Alpha Miner / Inductive Miner).
- Calculating actual user dwell time and error rates without human presence distorting operational reality.

---

### 6. Analysis Paradigms: Structured Analysis vs. Object-Oriented Analysis

Once requirements are elicited, systems analysts organize them into formal conceptual models. In computer science history, two distinct modeling paradigms have emerged: **Structured Analysis** and **Object-Oriented Analysis (OOA)**.

```
+---------------------------------------------------------------------------------------------------+
|                        STRUCTURED ANALYSIS VS. OBJECT-ORIENTED ANALYSIS                           |
+---------------------------------------------------------------------------------------------------+
| DIMENSION:              STRUCTURED ANALYSIS (PROCESS-CENTRIC)  OBJECT-ORIENTED ANALYSIS (UML)     |
| * Fundamental Unit      Function / Process                     Object (Data + Behavior Encapsulated|
| * Primary Relationship  Data Flow Transformation (Input->Out)  Message Passing & Collaboration    |
| * Core Artifacts        DFDs (Level 0, 1, 2), Data Dictionary, Use Cases, Class Diagrams, Sequence|
|                         Decision Tables, Structured English    State Machine Diagrams (UML 2.5)   |
| * Data-Logic Separation Strict separation: Processes act on    Unified: Data attributes and logic |
|                         passive Data Stores.                   methods co-exist inside Class.     |
| * Reusability           Low (Subroutines tightly coupled)      High (Polymorphism, Inheritance)   |
| * System Fit            ETL pipelines, batch processing,       Enterprise distributed systems,    |
|                         relational data accounting.            event-driven microservices.        |
+---------------------------------------------------------------------------------------------------+
```

#### 6.1 Structured Analysis Artifacts
1. **Data Flow Diagrams (DFD):** Visual representations of data moving through processes, stores, and external entities (Gane & Sarson or DeMarco & Yourdon notations).
2. **Data Dictionary:** A centralized metadata repository defining the atomic data types, lengths, ranges, and compositions for every data flow (e.g., `Patient_Record = National_ID + Full_Name + DOB + {Prescription_History}`).
3. **Structured English:** A restricted subset of natural English using indentation, standard algorithmic primitives (`IF-THEN-ELSE`, `DO-WHILE`), and formal data dictionary terms without programming language syntax clutter.
4. **Decision Tables & Decision Trees:** Tabular tools to disambiguate complex multi-condition business rules.

#### 6.2 The Anatomy of a Formal Decision Table
A Decision Table mathematically verifies that every possible permutation of boolean operational conditions has an unambiguous, corresponding set of system actions. It consists of four quadrants:

```
+------------------------------------+------------------------------------+
|          CONDITION STUB            |          CONDITION ENTRIES         |
| (List of boolean input variables)  | (Permutations: Y/N/True/False/-)   |
+------------------------------------+------------------------------------+
|           ACTION STUB              |           ACTION ENTRIES           |
| (List of executable system actions)| (Execution flags: X / -)           |
+------------------------------------+------------------------------------+
```

For $N$ independent binary conditions, a mathematically complete decision table must evaluate exactly $2^N$ rule columns. Any table with fewer than $2^N$ rules is either:
- **Incomplete:** Omitting edge cases where system behavior is undefined.
- **Redundant:** Containing duplicate rules that can be logically simplified with "Don't Care" ($-$) conditions.
- **Contradictory:** Specifying conflicting actions for the same condition state.

---

### 7. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

A multi-state regional health network is planning a total digital transformation, migrating 12 hospitals and 4,000 clinicians from disparate legacy paper/client-server records to an unified Cloud Electronic Health Record (EHR).

The project executive committee is debating which elicitation and analysis techniques to deploy:
- Option A: Conduct individual structured interviews with all 4,000 clinicians.
- Option B: Distribute an open-ended survey questionnaire via email to all hospital staff.
- Option C: Organize a multi-phase elicitation strategy combining Document Auditing, a 370-person Likert Survey, a 5-day JAD Workshop with key department chiefs, and an Object-Oriented Domain Model.

**Architectural Audit Tasks:**
1. Evaluate why Option A is economically and logistically impossible, calculating the analyst person-hours required.
2. Critique Option B, explaining why open-ended mass surveys fail to yield actionable software specifications.
3. Defend Option C, presenting a chronological workflow demonstrating how JAD and OOA resolve inter-hospital workflow discrepancies.

<details>
<summary>Click to view Level 1 Solution & Architectural Defense</summary>

##### 1. Mathematical Breakdown of Option A:
- Conducting 4,000 individual interviews: Assuming a conservative $1.0\text{ hour}$ interview + $1.5\text{ hours}$ for transcription, coding, and synthesis $= 2.5\text{ analyst-hours per person}$.
$$\text{Total Effort} = 4,000 \times 2.5\text{ hours} = 10,000\text{ analyst-hours}$$
- With a team of 5 full-time senior analysts ($40\text{ hrs/week}$ each $= 200\text{ hrs/week}$ total), completing Option A would require:
$$\text{Duration} = \frac{10,000}{200} = 50\text{ working weeks} \approx 1.0\text{ full calendar year!}$$
- By the time the final clinician is interviewed, clinical workflows, hospital regulations, and project budgets will have drifted completely. Option A is commercially unviable.

##### 2. Critique of Option B (Open-Ended Mass Survey):
- Open-ended surveys distributed to thousands of non-technical workers suffer from an abysmal response rate (typically $< 8\%$).
- Qualitative text analysis of thousands of freeform paragraphs generates immense ambiguity, semantic drift, and subjective complaints rather than testable functional requirements.
- Lacks any collaborative mechanism to resolve contradictory clinical requests (e.g., pediatricians demanding different intake workflows than trauma surgeons).

##### 3. Defense of Option C (The Recommended Engineering Strategy):
1. **Phase 1: Archival Document & Form Review (Weeks 1-2):** Reverse-engineer all existing physical intake sheets, billing charge masters, and HL7 interface feeds to establish the baseline data dictionary.
2. **Phase 2: Statistically Rigorous Closed Questionnaire (Week 3):** Using Yamane's formula ($n = 371$), sample nurses and clinicians using 5-point Likert scales to establish operational pain points and feature prioritization.
3. **Phase 3: 5-Day JAD Summit (Week 4):** Assemble 15 key department heads (Chief Medical Officer, Head of Pharmacy, Billing Director, Lead Architect, neutral Facilitator, and Scribes). Settle workflow discrepancies, establish the clinical use cases, and achieve signed consensus in 5 days.
4. **Phase 4: Object-Oriented Domain Modeling (Weeks 5-6):** Model patient records, orders, and diagnostic results as encapsulated classes with strict behavioral contracts and state machines, enabling scalable microservice implementation.

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The Defective Decision Table Validator

A software engineering team wrote a Python script to validate business rule decision tables before generating code. The script is supposed to verify that a decision table is mathematically complete ($2^N$ rules) and has no contradictory actions. However, the script is allowing contradictory rules to slip through and is crashing when "Don't Care" ($-$) wildcards are introduced.

Examine the flawed script below:

```python
# FLAWED DECISION TABLE VALIDATOR (PYTHON)
def validate_decision_table(conditions, rules):
    num_conditions = len(conditions)
    # BUG 1: Assumes every rule column represents exactly 1 state,
    # completely failing when rules contain '-' (Don't Care) wildcards!
    expected_combinations = 2 ** num_conditions
    if len(rules) != expected_combinations:
        print(f"Warning: Table has {len(rules)} rules, expected {expected_combinations}")

    # BUG 2: Contradiction detection only checks adjacent rules!
    for i in range(len(rules) - 1):
        rule_a = rules[i]
        rule_b = rules[i + 1]
        if rule_a["conditions"] == rule_b["conditions"]:
            if rule_a["actions"] != rule_b["actions"]:
                print(f"Contradiction found between Rule {i} and Rule {i+1}!")
                
    # BUG 3: Does not expand '-' into concrete boolean permutations,
    # causing false "completeness" claims or unhandled runtime conditions!
```

**Debug Assignment:**
1. Explain how a single "Don't Care" ($-$) entry in a condition row represents two distinct states ($0$ and $1$), and how $K$ "Don't Care" entries expand to $2^K$ concrete states.
2. Implement a complete boolean expansion algorithm that maps all rules to a bitmask universe of $[0, 2^N - 1]$.
3. Implement an exact detector that flags:
   - Missing condition combinations (Incompleteness).
   - Ambiguous/Contradictory condition overlap (Multiple rules claiming the same state with different actions).

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. Mathematical Mechanics of "Don't Care" Wildcards:
If a decision table has $N = 3$ binary conditions ($C_1, C_2, C_3$), the total state space is $2^3 = 8$ states ($\{000, 001, \dots, 111\}$).
If a rule has condition entry `[True, False, -]`, the wildcard `'-'` means the action applies regardless of whether $C_3$ is `True` or `False`. This single rule covers $2^1 = 2$ states:
$$\text{State 1: } (T, F, F) \implies 100_2 = 4$$
$$\text{State 2: } (T, F, T) \implies 101_2 = 5$$
If a table specifies $M$ rules with wildcards, the sum of covered states must equal exactly $2^N$. Checking `len(rules) == 2**N` without expansion is mathematically wrong.

##### 2. Corrected Production Implementation:

```python
from typing import List, Dict, Set

class ProductionDecisionTableValidator:
    def __init__(self, condition_names: List[str]):
        self.conditions = condition_names
        self.num_conditions = len(condition_names)
        self.total_state_space = 2 ** self.num_conditions

    def expand_rule_states(self, cond_values: List[str]) -> List[int]:
        # Expands a list of 'T', 'F', '-' into a list of integer bitmask states
        states = [0]
        for idx, val in enumerate(cond_values):
            bit_val = 1 << (self.num_conditions - 1 - idx)
            new_states = []
            for s in states:
                if val.upper() in ('T', 'Y', '1'):
                    new_states.append(s | bit_val)
                elif val.upper() in ('F', 'N', '0'):
                    new_states.append(s)
                elif val == '-': # Wildcard: covers both 0 and 1
                    new_states.append(s)
                    new_states.append(s | bit_val)
                else:
                    raise ValueError(f"Invalid condition entry: {val}")
            states = new_states
        return states

    def audit_table(self, rules: List[Dict]) -> Dict:
        state_to_action_map: Dict[int, Dict] = {}
        contradictions = []
        covered_states: Set[int] = set()

        for rule_idx, rule in enumerate(rules):
            covered = self.expand_rule_states(rule["conditions"])
            action_signature = tuple(sorted(rule["actions"].items()))

            for state in covered:
                if state in state_to_action_map:
                    prior_rule_idx, prior_actions = state_to_action_map[state]
                    if prior_actions != action_signature:
                        contradictions.append({
                            "state_bitmask": bin(state),
                            "rule_a": prior_rule_idx,
                            "rule_b": rule_idx,
                            "actions_a": dict(prior_actions),
                            "actions_b": rule["actions"]
                        })
                else:
                    state_to_action_map[state] = (rule_idx, action_signature)
                    covered_states.add(state)

        # Missing combinations check
        all_possible_states = set(range(self.total_state_space))
        missing_states = all_possible_states - covered_states

        return {
            "is_complete": len(missing_states) == 0,
            "total_possible_states": self.total_state_space,
            "covered_states_count": len(covered_states),
            "missing_states": [bin(s) for s in sorted(missing_states)],
            "contradictions": contradictions
        }
```

</details>

---

#### Level 3 — High-Scale System Design: Interactive Decision Table Engine & Structured English Generator in C++

Design and implement a complete, production-grade C++17 **Decision Table Evaluation Engine & Structured English Generator**. The system must:
1. Model complex business rules using formal Decision Table components (Condition Stubs, Action Stubs, and Rule Columns with `'T'`, `'F'`, and `'-'` wildcards).
2. Perform exhaustive boolean state expansion across the $2^N$ state universe.
3. Automatically audit the decision table for:
   - **Completeness:** Ensure all $2^N$ condition permutations are mapped to valid actions.
   - **Contradictions:** Detect rules that map the exact same condition state to conflicting actions.
   - **Redundancies:** Identify sub-optimal rules that can be simplified.
4. Execute real-time runtime evaluation of incoming customer domain transactions against the decision table.
5. Automatically synthesize an optimized, human-readable **Structured English** pseudo-code specification.

<details>
<summary>Click to view complete C++17 Decision Table Engine</summary>

```cpp
/**
 * ============================================================================
 * DECISION TABLE EVALUATION & STRUCTURED ENGLISH ENGINE (C++17)
 * ============================================================================
 * Implements:
 * 1. Condition Stub & Action Stub Formal Modeling.
 * 2. 2^N Boolean State-Space Expansion & Completeness Auditing.
 * 3. Contradiction and Ambiguity Conflict Detection.
 * 4. Real-time Transaction Rule Engine Execution.
 * 5. Automated Structured English Specification Synthesis.
 * ============================================================================
 */

#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <iomanip>
#include <sstream>
#include <bitset>
#include <algorithm>

// ============================================================================
// DATA STRUCTURES
// ============================================================================

struct RuleColumn {
    std::string rule_name;
    std::vector<char> condition_entries; // 'T', 'F', or '-' (Don't care)
    std::vector<bool> action_entries;    // true if action executes
};

class DecisionTable {
private:
    std::vector<std::string> condition_stubs;
    std::vector<std::string> action_stubs;
    std::vector<RuleColumn> rules;

    std::vector<uint32_t> expand_rule_to_bitmasks(const std::vector<char>& entries) const {
        std::vector<uint32_t> states = {0};
        size_t n = entries.size();

        for (size_t i = 0; i < n; ++i) {
            uint32_t bit = 1 << (n - 1 - i);
            char val = entries[i];
            std::vector<uint32_t> next_states;

            for (uint32_t s : states) {
                if (val == 'T' || val == 't' || val == '1') {
                    next_states.push_back(s | bit);
                } else if (val == 'F' || val == 'f' || val == '0') {
                    next_states.push_back(s);
                } else if (val == '-') { // Don't Care: spans both 0 and 1
                    next_states.push_back(s);
                    next_states.push_back(s | bit);
                }
            }
            states = next_states;
        }
        return states;
    }

public:
    void add_condition(const std::string& description) {
        condition_stubs.push_back(description);
    }

    void add_action(const std::string& description) {
        action_stubs.push_back(description);
    }

    void add_rule(const std::string& name, const std::vector<char>& conds, const std::vector<bool>& acts) {
        rules.push_back({name, conds, acts});
    }

    bool audit_specification() const {
        std::cout << "\n================================================================================\n";
        std::cout << "                 DECISION TABLE MATHEMATICAL AUDIT REPORT\n";
        std::cout << "================================================================================\n";

        size_t n = condition_stubs.size();
        uint32_t total_space = 1 << n;
        std::cout << "Condition Count (N)            : " << n << "\n";
        std::cout << "Theoretical State Universe (2^N): " << total_space << " distinct states\n";

        std::unordered_map<uint32_t, size_t> state_to_rule_map;
        std::vector<std::string> contradictions;
        std::unordered_set<uint32_t> covered_states;

        for (size_t r = 0; r < rules.size(); ++r) {
            auto states = expand_rule_to_bitmasks(rules[r].condition_entries);
            for (uint32_t st : states) {
                if (state_to_rule_map.find(st) != state_to_rule_map.end()) {
                    size_t prev_r = state_to_rule_map[st];
                    // Compare action equality
                    if (rules[prev_r].action_entries != rules[r].action_entries) {
                        std::stringstream ss;
                        ss << "State [" << std::bitset<8>(st).to_string().substr(8 - n) 
                           << "] triggers conflicting actions in " << rules[prev_r].rule_name 
                           << " and " << rules[r].rule_name;
                        contradictions.push_back(ss.str());
                    }
                } else {
                    state_to_rule_map[st] = r;
                    covered_states.insert(st);
                }
            }
        }

        std::cout << "Total States Covered by Rules  : " << covered_states.size() << " / " << total_space << "\n";

        bool is_complete = (covered_states.size() == total_space);
        std::cout << "Completeness Status            : " 
                  << (is_complete ? "PASSED (100% COVERAGE)" : "FAILED (INCOMPLETE - MISSING COMBINATIONS)") << "\n";

        if (!is_complete) {
            std::cout << "\n[!] UNHANDLED SPECIFICATION STATES:\n";
            for (uint32_t st = 0; st < total_space; ++st) {
                if (covered_states.find(st) == covered_states.end()) {
                    std::cout << "  * Unhandled State: [" 
                              << std::bitset<8>(st).to_string().substr(8 - n) << "]\n";
                }
            }
        }

        if (!contradictions.empty()) {
            std::cout << "\n[!] CONTRADICTIONS DETECTED:\n";
            for (const auto& c : contradictions) {
                std::cout << "  * " << c << "\n";
            }
        }

        return is_complete && contradictions.empty();
    }

    std::vector<std::string> evaluate_transaction(const std::vector<bool>& inputs) const {
        size_t n = condition_stubs.size();
        uint32_t current_state = 0;
        for (size_t i = 0; i < n; ++i) {
            if (inputs[i]) {
                current_state |= (1 << (n - 1 - i));
            }
        }

        for (const auto& r : rules) {
            auto states = expand_rule_to_bitmasks(r.condition_entries);
            if (std::find(states.begin(), states.end(), current_state) != states.end()) {
                std::vector<std::string> triggered_actions;
                for (size_t a = 0; a < action_stubs.size(); ++a) {
                    if (r.action_entries[a]) {
                        triggered_actions.push_back(action_stubs[a]);
                    }
                }
                return triggered_actions;
            }
        }
        return {"[ERROR: Unhandled Condition State - No Rule Matched]"};
    }

    void print_structured_english() const {
        std::cout << "\n================================================================================\n";
        std::cout << "              SYNTHESIZED STRUCTURED ENGLISH SPECIFICATION\n";
        std::cout << "================================================================================\n";

        for (size_t r = 0; r < rules.size(); ++r) {
            const auto& rule = rules[r];
            std::cout << "RULE " << rule.rule_name << ":\n";
            std::cout << "  IF ";

            bool first_cond = true;
            for (size_t c = 0; c < condition_stubs.size(); ++c) {
                char val = rule.condition_entries[c];
                if (val == '-') continue; // Skip wildcards

                if (!first_cond) std::cout << " AND\n     ";
                std::cout << condition_stubs[c] << " IS " << (val == 'T' ? "TRUE" : "FALSE");
                first_cond = false;
            }

            std::cout << "\n  THEN\n";
            for (size_t a = 0; a < action_stubs.size(); ++a) {
                if (rule.action_entries[a]) {
                    std::cout << "     EXECUTE: " << action_stubs[a] << ";\n";
                }
            }
            std::cout << "\n";
        }
        std::cout << "================================================================================\n";
    }
};

// ============================================================================
// SIMULATION HARNESS: E-COMMERCE FRAUD & DISCOUNT ENGINE
// ============================================================================

int main() {
    DecisionTable table;

    // Condition Stubs (N = 3 -> 2^3 = 8 possible states)
    table.add_condition("Customer is Premium VIP Member");
    table.add_condition("Order Value Exceeds $500.00");
    table.add_condition("Risk Score Flags High Fraud Probability");

    // Action Stubs
    table.add_action("Apply 20% VIP Loyalty Discount");
    table.add_action("Apply 10% High-Value Order Discount");
    table.add_action("Approve Order for Instant Fulfillment");
    table.add_action("Hold Order for Manual Fraud Security Review");

    // Rule 1: High Fraud Risk -> Always Hold regardless of VIP or Order Value
    table.add_rule("R1_FraudHold", {'-', '-', 'T'}, {false, false, false, true});

    // Rule 2: Low Risk, VIP, High Value -> Both 20% discount and Instant Approval
    table.add_rule("R2_VipLargeOrder", {'T', 'T', 'F'}, {true, false, true, false});

    // Rule 3: Low Risk, VIP, Regular Value -> 20% discount and Instant Approval
    table.add_rule("R3_VipRegularOrder", {'T', 'F', 'F'}, {true, false, true, false});

    // Rule 4: Low Risk, Non-VIP, High Value -> 10% discount and Instant Approval
    table.add_rule("R4_StandardLargeOrder", {'F', 'T', 'F'}, {false, true, true, false});

    // Rule 5: Low Risk, Non-VIP, Regular Value -> Zero discount and Instant Approval
    table.add_rule("R5_StandardRegularOrder", {'F', 'F', 'F'}, {false, false, true, false});

    // Run Mathematical Completeness and Contradiction Audit
    bool valid = table.audit_specification();

    // Synthesize Structured English Algorithm
    table.print_structured_english();

    // Evaluate Real-World Incoming Transactions
    std::cout << ">>> RUNTIME TRANSACTION EVALUATIONS <<<\n";

    // Transaction 1: Non-VIP ($F$), High Value ($T$), Low Risk ($F$)
    std::vector<bool> txn1 = {false, true, false};
    std::cout << "Txn 1 [Non-VIP, >$500, Low Risk] Actions:\n";
    for (const auto& act : table.evaluate_transaction(txn1)) {
        std::cout << "  -> " << act << "\n";
    }

    // Transaction 2: VIP ($T$), High Value ($T$), High Risk ($T$)
    std::vector<bool> txn2 = {true, true, true};
    std::cout << "\nTxn 2 [VIP, >$500, High Fraud Risk] Actions:\n";
    for (const auto& act : table.evaluate_transaction(txn2)) {
        std::cout << "  -> " << act << "\n";
    }

    return 0;
}
```

</details>

---

### 8. Reference Video Lecture

{{ media:scrum-elicitation-video }}

In this video by Simplilearn, collaborative requirements elicitation dynamics, cross-functional stakeholder workshops, and structured requirement refinement sessions are examined in detail.
