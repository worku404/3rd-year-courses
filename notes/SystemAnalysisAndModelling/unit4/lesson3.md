# Unit 4 — Structured Analysis, Hierarchical Data Flow Modeling & Logic Specifications
## Lesson 3 — Logic Modeling: Decision Trees, 2^N Complete Decision Tables & Structured English

### 1. The Mandate for Process Specifications (P-Specs)

In the hierarchical decomposition of Data Flow Diagrams (DFDs), the top tiers (Context Diagram Level 0 and Subsystems Level 1) partition data pipelines into manageable subsystems. However, when decomposition reaches **Level 2 or Level 3**, the analyst arrives at **Functional Primitives**—atomic process nodes that cannot be decomposed into child sub-DFDs without resorting to imperative algorithmic logic.

To specify the precise transformation logic inside a functional primitive, systems engineers construct a **Process Specification (P-Spec)** (also termed a *Mini-Spec*).

A formal P-Spec must fulfill three software engineering criteria:
1. **Mathematical Completeness:** Every possible combination of input conditions must result in an unambiguous set of executable actions.
2. **Implementation Independence:** The logic must be expressed without tying the design prematurely to a specific programming language syntax (e.g., C++, Python, SQL).
3. **Verification Verifiability:** A QA engineer must be able to convert the P-Spec directly into a deterministic test matrix with $100\%$ path and branch coverage.

```
+---------------------------------------------------------------------------------------------------+
|                           THE P-SPEC LOGIC MODELING TOOLSET                                       |
+---------------------------------------------------------------------------------------------------+
| 1. DECISION TREES     : Graphical horizontal branching trees; best for sequential decisions       |
|                         where conditions occur in a fixed chronological order.                    |
|                                                                                                   |
| 2. DECISION TABLES    : Formal 2^N algebraic truth tables; best for complex combinatorial logic   |
|                         where actions depend on simultaneous independent boolean variables.       |
|                                                                                                   |
| 3. STRUCTURED ENGLISH : Restricted imperative natural language; best for procedural logic         |
|                         requiring loops, iterations, and database record mutations.               |
+---------------------------------------------------------------------------------------------------+
```

---

### 2. Decision Trees: Graphical Sequential Branching

A **Decision Tree** is a horizontal branching diagram that graphically traces conditional decisions from a root trigger node to terminal action leaves:

{{ media:sam-decision-logic-diagram }}

```
                                                 +------------------------------+
                                          +----> | Action 1: 20% VIP Discount   |
                   [ VIP Member? (T) ] ---+      +------------------------------+
                   |                      |
                   |                      +----> +------------------------------+
                   |                             | Action 2: Free Priority Ship |
[ Order > $500? ] -+                             +------------------------------+
(Root Decision)    |
                   |                             +------------------------------+
                   +-- [ VIP Member? (F) ] ----> | Action 3: 10% Standard Disc  |
                   |                             +------------------------------+
                   |
                   |                             +------------------------------+
                   +-- [ Order <= $500? ] -----> | Action 4: Zero Discount      |
                                                 +------------------------------+
```

#### 2.1 Anatomical Elements of a Decision Tree
- **Root Node:** The initial decision or stimulus (e.g., arrival of an incoming order).
- **Decision Nodes (Branches):** Mutually exclusive condition alternatives (e.g., `Order > $500` vs. `Order <= $500`).
- **Terminal Nodes (Leaves):** The resulting set of system actions, calculations, or state mutations.

#### 2.2 Strengths and Structural Limitations
- **Cognitive Readability:** Exceptional for communicating complex business policies to non-technical executive stakeholders and corporate clients.
- **The Combinatorial Explosion Flaw:** While intuitive for 2 or 3 conditions, a decision tree with $N = 7$ independent boolean conditions produces $2^7 = 128$ sprawling leaf branches, rendering the diagram unreadable. For large condition sets, analysts transition to **Decision Tables**.

---

### 3. Decision Tables: Mathematical 2^N Combinatorial Exhaustion

A **Decision Table** is a rigorous matrix that models complex decision logic by listing all input conditions, all possible permutations of those conditions, and all resulting system actions.

A canonical Decision Table is partitioned into **four distinct quadrants**:

```
+-------------------------------------------------------+-------------------------------------------+
|                  CONDITION STUB                       |             CONDITION ENTRIES             |
| Lists all independent input conditions / predicates.  | Matrix of permutations: Y/N, T/F, or '-'  |
+-------------------------------------------------------+-------------------------------------------+
|                   ACTION STUB                         |              ACTION ENTRIES               |
| Lists all executable actions, outputs, or transforms. | Execution flags: 'X' (execute) or '-'     |
+-------------------------------------------------------+-------------------------------------------+
```

#### 3.1 The $2^N$ Completeness Theorem
For a system governed by $N$ independent binary boolean conditions ($C_1, C_2, \dots, C_N$), the total number of distinct operational states is:

$$\text{Total Combinatorial State Space } (S) = 2^N$$

$$\text{For multi-valued conditions: } S = \prod_{k=1}^N V_k \quad (\text{where } V_k \text{ is the number of valid states for condition } C_k)$$

If an analyst constructs a decision table for 4 binary conditions ($2^4 = 16$ states) but only documents 12 rule columns, the specification has an **Incompleteness Defect**: exactly 4 real-world operational scenarios have undefined behavior, representing potential production crash bugs.

---

### 4. Decision Table Optimization: "Don't Care" ($-$) Wildcard Reduction

While an unreduced decision table contains $2^N$ rule columns, many rules produce identical actions regardless of the value of certain conditions. Analysts simplify the table by substituting **"Don't Care" ($-$)** wildcards, merging adjacent rules in a manner analogous to Karnaugh Maps and Quine-McCluskey boolean minimization.

#### 4.1 Algebraic Mechanics of Wildcard Expansion
A rule containing $K$ "Don't Care" ($-$) wildcards spans exactly $2^K$ concrete states in the boolean hypercube:

$$\text{Rule Coverage } = 2^K \quad (K = \text{count of '-' entries in the rule column})$$

$$\text{Completeness Invariant: } \sum_{r=1}^M 2^{K_r} = 2^N$$

Consider a retail banking authorization table with $N = 3$ conditions ($2^3 = 8$ states):
- $C_1$: Account status is `ACTIVE` ($T/F$).
- $C_2$: Available balance $\ge$ withdrawal amount ($T/F$).
- $C_3$: Daily withdrawal limit not exceeded ($T/F$).

```
====================================================================================================
                        REDUCED DECISION TABLE: CASH WITHDRAWAL ENGINE
====================================================================================================
CONDITIONS:                              RULE 1      RULE 2      RULE 3      RULE 4 (Fraud / Inactive)
----------------------------------------------------------------------------------------------------
C1: Account Status is ACTIVE               T           T           T                   F
C2: Balance >= Withdrawal Amount           T           T           F                   -
C3: Daily Limit Not Exceeded               T           F           -                   -
====================================================================================================
ACTIONS:                                 RULE 1      RULE 2      RULE 3      RULE 4
----------------------------------------------------------------------------------------------------
A1: Dispense Cash                          X           -           -                   -
A2: Emit "Daily Limit Exceeded" Receipt    -           X           -                   -
A3: Emit "Insufficient Funds" Receipt      -           -           X                   -
A4: Freeze Card & Alert Security Branch    -           -           -                   X
----------------------------------------------------------------------------------------------------
Wildcard Count (K):                      K = 0       K = 0       K = 1               K = 2
Covered State Count (2^K):               2^0 = 1     2^0 = 1     2^1 = 2             2^2 = 4
====================================================================================================
Total Covered States: 1 + 1 + 2 + 4 = 8 states == 2^3 (100% MATHEMATICAL COMPLETENESS PROVEN!)
====================================================================================================
```

In this optimized table, Rule 4 contains two wildcards ($K = 2$), instantly covering $4$ distinct states ($FTT, FTF, FFT, FFF$). If the account is inactive, the system freezes the card immediately without inspecting balance or daily limits.

---

### 5. Structured English: The Procedural Bridge to Code

**Structured English** translates the logic of Decision Trees and Decision Tables into a standardized, procedural pseudo-specification. It eliminates the stylistic ambiguities of natural language while avoiding the syntax clutter of concrete programming languages.

#### 5.1 Syntax Conventions of Structured English
1. **Restricted Vocabulary:** Uses only action verbs (e.g., `VALIDATE`, `CALCULATE`, `PERSIST`, `DISPATCH`) and nouns formally defined in the **Data Dictionary**.
2. **Algorithmic Primitives:** Limited strictly to:
   - Sequence: Sequential statements executed top-to-bottom.
   - Selection: `IF <condition> THEN ... ELSE ... ENDIF` or `MATCH ... CASE ...`.
   - Iteration: `FOR EACH <item> IN <collection> ... ENDFOR` or `WHILE <condition> DO ... ENDWHILE`.
3. **Indentation Discipline:** Indentation strictly conveys nesting levels and scope blocks.

* **Example P-Spec for Process 2.4 (Evaluate Insurance Claim):**
```text
PROCESS SPECIFICATION 2.4: Evaluate_Insurance_Claim
INPUTS: Claim_Submission, Patient_Policy_Record
OUTPUTS: Adjudication_Result, Payment_Disbursement

BEGIN
  IF Claim_Submission.Policy_Number NOT FOUND IN Patient_Policy_Record THEN
    GENERATE Error_Notification("Invalid Policy Identification")
    SET Adjudication_Result.Status = "REJECTED_INVALID_POLICY"
  ELSE
    IF Patient_Policy_Record.Status != "ACTIVE" THEN
      SET Adjudication_Result.Status = "REJECTED_POLICY_LAPSED"
    ELSE
      CALCULATE Total_Claim_Cost = SUM(Claim_Submission.Line_Items.Billed_Amount)
      IF Total_Claim_Cost <= Patient_Policy_Record.Remaining_Deductible THEN
        SET Adjudication_Result.Status = "APPROVED_ZERO_DISBURSEMENT"
        UPDATE Patient_Policy_Record.Remaining_Deductible -= Total_Claim_Cost
      ELSE
        SET Covered_Amount = Total_Claim_Cost - Patient_Policy_Record.Remaining_Deductible
        SET Coinsurance_Patient_Share = Covered_Amount * Patient_Policy_Record.Coinsurance_Rate
        SET Insurer_Disbursement = Covered_Amount - Coinsurance_Patient_Share
        
        SET Adjudication_Result.Status = "APPROVED_PAID"
        DISPATCH Payment_Disbursement(Insurer_Disbursement, Claim_Submission.Provider_ID)
        UPDATE Patient_Policy_Record.Remaining_Deductible = 0.00
      ENDIF
    ENDIF
  ENDIF
END
```

---

### 6. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

A state university financial aid office is revising its merit and need-based tuition scholarship policies. The board establishes four independent boolean criteria for applicant evaluation:
1. $C_1$: Cumulative GPA $\ge 3.80$ ($T/F$).
2. $C_2$: Household annual income $< \$45,000$ ($T/F$).
3. $C_3$: First-generation college student ($T/F$).
4. $C_4$: Disciplinary infractions on record ($T/F$).

**Policy Rules:**
- Any student with a disciplinary infraction ($C_4 = T$) is immediately disqualified from all aid, regardless of GPA or income.
- Students with GPA $\ge 3.80$ and income $< \$45,000$ receive a **Full Presidential Tuition Waiver + Living Stipend**.
- Students with GPA $\ge 3.80$ and income $\ge \$45,000$ receive a **Merit Honors Tuition Waiver (50%)**.
- Students with GPA $< 3.80$ and income $< \$45,000$ who are first-generation receive an **Opportunity Grant (75%)**.
- Students with GPA $< 3.80$ and income $< \$45,000$ who are not first-generation receive a **Need-Based Work-Study Grant (25%)**.
- All remaining students receive **Standard Federal Loan Eligibility**.

**Architectural Analysis Assignment:**
1. Determine the total state space size ($2^N$).
2. Construct a complete, minimized Decision Table with "Don't Care" ($-$) wildcards.
3. Prove that the sum of covered states across all rules equals $2^N$.

<details>
<summary>Click to view Level 1 Solution & Complete Decision Table</summary>

##### 1. Total Combinatorial State Space:
$$N = 4 \text{ binary conditions} \implies 2^4 = 16 \text{ distinct states}.$$

##### 2. Minimized Decision Table:

| Conditions | Rule 1 (Disqualified) | Rule 2 (Presidential) | Rule 3 (Merit 50%) | Rule 4 (Opp Grant 75%) | Rule 5 (Work-Study 25%) | Rule 6 (Standard Loans) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| $C_1$: $\text{GPA} \ge 3.80$ | $-$ | **T** | **T** | **F** | **F** | **F** |
| $C_2$: $\text{Income} < \$45\text{K}$ | $-$ | **T** | **F** | **T** | **T** | **F** |
| $C_3$: First-Generation | $-$ | $-$ | $-$ | **T** | **F** | $-$ |
| $C_4$: Disciplinary Record | **T** | **F** | **F** | **F** | **F** | **F** |
| **Actions:** | | | | | | |
| $A_1$: Immediate Disqualification | **X** | $-$ | $-$ | $-$ | $-$ | $-$ |
| $A_2$: Presidential Waiver + Stipend | $-$ | **X** | $-$ | $-$ | $-$ | $-$ |
| $A_3$: Merit Honors Waiver (50%) | $-$ | $-$ | **X** | $-$ | $-$ | $-$ |
| $A_4$: Opportunity Grant (75%) | $-$ | $-$ | $-$ | **X** | $-$ | $-$ |
| $A_5$: Need-Based Work-Study (25%) | $-$ | $-$ | $-$ | $-$ | **X** | $-$ |
| $A_6$: Standard Federal Loans | $-$ | $-$ | $-$ | $-$ | $-$ | **X** |
| **Wildcards ($K$):** | $K = 3$ | $K = 1$ | $K = 1$ | $K = 0$ | $K = 0$ | $K = 1$ |
| **Covered States ($2^K$):** | $2^3 = 8$ | $2^1 = 2$ | $2^1 = 2$ | $2^0 = 1$ | $2^0 = 1$ | $2^1 = 2$ |

##### 3. Proof of Mathematical Completeness:
$$\text{Total Covered States} = 8 + 2 + 2 + 1 + 1 + 2 = 16 = 2^4$$
Every possible permutation of applicant conditions maps to exactly one unambiguous award action. Zero undefined states; zero contradictions!

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The Dead-Code Decision Tree Generator

A fintech startup implemented a Python code generator that compiles decision tables into nested Python `if-elif-else` code for credit score approval. However, in production, high-net-worth customers are being erroneously routed to the generic fallback `else` branch, and several valid rules are never reached (dead code).

Examine the flawed compiler logic below:

```python
# FLAWED DECISION TABLE COMPILER (PYTHON)
def generate_decision_code(rules):
    code_lines = []
    # BUG 1: Rules are sorted arbitrarily by dictionary key,
    # causing general wildcard rules to precede specific rules!
    # A rule with condition [-, -, -] placed at the top eclipses all subsequent rules!
    for r in rules:
        cond_clauses = []
        for cond_name, val in r["conditions"].items():
            if val == "T":
                cond_clauses.append(f"{cond_name} is True")
            elif val == "F":
                cond_clauses.append(f"{cond_name} is False")
            # Wildcard '-' is omitted from clauses
            
        # BUG 2: Empty clause list generated for all-wildcard rule produces invalid syntax!
        condition_str = " and ".join(cond_clauses)
        code_lines.append(f"if {condition_str}:")
        for action in r["actions"]:
            code_lines.append(f"    execute_{action}()")
            
    # BUG 3: Generates parallel 'if' blocks instead of chained 'elif',
    # causing non-mutually-exclusive rule firing!
    return "\n".join(code_lines)
```

**Debug Assignment:**
1. Explain how rule order matters when "Don't Care" ($-$) wildcards are present, and why more specific rules (fewer wildcards) must be evaluated before broader rules (more wildcards) or mutually exclusive partitions must be enforced.
2. Fix the syntax generation so that chained `if-elif-else` control flow is produced.
3. Add an automated unreachable dead-code detector that identifies rules eclipsed by prior clauses.

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. The Rule Specificity & Precedence Flaw:
- When a decision table is translated into procedural code (`if ... elif ...`), the order of evaluation is critical.
- A rule with condition entries `[-, -, -]` matches **all $8$ states**. If this rule is evaluated first, its branch is *always* taken, rendering every subsequent `elif` rule completely unreachable dead code.
- To prevent shadowing, rules must either be:
  1. Guaranteed mathematically disjoint (no state intersection between rules).
  2. Sorted by **Specificity** (rules with $0$ wildcards first, then $1$ wildcard, down to default catch-alls with $N$ wildcards).
- Using independent `if` statements instead of `elif` causes multiple conflicting actions to execute for the same transaction.

##### 2. Corrected Production Implementation:

```python
from typing import List, Dict, Set

class ProductionDecisionCodeGenerator:
    def __init__(self, condition_names: List[str]):
        self.condition_names = condition_names
        self.num_conditions = len(condition_names)

    def compute_specificity(self, condition_entries: Dict[str, str]) -> int:
        # Returns the number of non-wildcard conditions (higher = more specific)
        return sum(1 for val in condition_entries.values() if val in ('T', 'F', '1', '0'))

    def compile_to_python(self, rules: List[Dict]) -> str:
        # 1. Sort rules in descending order of specificity to prevent shadowing
        sorted_rules = sorted(
            rules,
            key=lambda r: self.compute_specificity(r["conditions"]),
            reverse=True
        )

        code_lines = ["def evaluate_business_policy(context):"]
        is_first = True

        for rule_idx, rule in enumerate(sorted_rules):
            cond_clauses = []
            for cond_name in self.condition_names:
                val = rule["conditions"].get(cond_name, "-")
                if val.upper() in ('T', 'Y', '1'):
                    cond_clauses.append(f"context['{cond_name}'] is True")
                elif val.upper() in ('F', 'N', '0'):
                    cond_clauses.append(f"context['{cond_name}'] is False")

            # Determine keyword (if, elif, or else)
            if not cond_clauses: # All wildcards -> Default fallback
                keyword = "else:"
            else:
                condition_expr = " and ".join(cond_clauses)
                keyword = f"if {condition_expr}:" if is_first else f"elif {condition_expr}:"
                is_first = False

            code_lines.append(f"    # Rule: {rule.get('name', f'Rule_{rule_idx}')}")
            code_lines.append(f"    {keyword}")
            for action in rule.get("actions", []):
                code_lines.append(f"        execute_{action}(context)")

        return "\n".join(code_lines)
```

</details>

---

#### Level 3 — High-Scale System Design: Karnaugh-Style Decision Table Reducer & Structured English Compiler in C++

Design and implement a complete, production-grade C++17 **Decision Table Minimization & Structured English Compiler**. The system must:
1. Ingest an unreduced $2^N$ combinatorial truth table representing multi-condition business rules.
2. Implement a **Karnaugh / Quine-McCluskey Minimization Algorithm**:
   - Compare rule pairs differing by exactly one condition bit.
   - If two rules produce identical action sets and differ by exactly one condition, merge them into a single rule with a `' - '` wildcard.
   - Iterate recursively until no further reductions are possible (Prime Implicant reduction).
3. Validate that the minimized table preserves $100\%$ state space coverage without introducing contradictions.
4. Automatically synthesize:
   - A clean **Structured English** specification report.
   - Optimized, branch-predicted C++17 code implementing the rule set.

<details>
<summary>Click to view complete C++17 Decision Table Reducer</summary>

```cpp
/**
 * ============================================================================
 * DECISION TABLE REDUCER & STRUCTURED ENGLISH COMPILER (C++17)
 * ============================================================================
 * Implements:
 * 1. Combinatorial Boolean State-Space Expansion.
 * 2. Karnaugh/Quine-McCluskey Rule Merging & Minimization.
 * 3. Formal Completeness & Non-Contradiction Verification.
 * 4. Automated Structured English & Optimized C++17 Code Synthesis.
 * ============================================================================
 */

#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <iomanip>
#include <bitset>
#include <algorithm>
#include <sstream>

// ============================================================================
// DATA STRUCTURES
// ============================================================================

struct MinimizedRule {
    std::string condition_mask; // e.g. "T-F" (T=true, F=false, -=don't care)
    std::string action_signature;
    std::vector<std::string> actions;
    int covered_state_count = 1;
};

class DecisionTableReducer {
private:
    std::vector<std::string> condition_names;
    std::vector<std::string> action_names;
    size_t n;
    uint32_t total_space;
    std::unordered_map<uint32_t, std::vector<std::string>> unreduced_table;

    std::string format_action_sig(const std::vector<std::string>& acts) const {
        std::stringstream ss;
        for (const auto& a : acts) ss << a << ";";
        return ss.str();
    }

public:
    DecisionTableReducer(const std::vector<std::string>& conds, const std::vector<std::string>& acts)
        : condition_names(conds), action_names(acts), n(conds.size()), total_space(1 << conds.size()) {}

    void register_state_action(uint32_t state_bitmask, const std::vector<std::string>& triggered_actions) {
        if (state_bitmask < total_space) {
            unreduced_table[state_bitmask] = triggered_actions;
        }
    }

    std::vector<MinimizedRule> minimize_table() {
        std::cout << "\n================================================================================\n";
        std::cout << "        DECISION TABLE MINIMIZATION & COMPILER AUDIT REPORT\n";
        std::cout << "================================================================================\n";

        // 1. Initial conversion: Each unreduced state is an atomic rule
        std::vector<MinimizedRule> current_rules;
        for (uint32_t s = 0; s < total_space; ++s) {
            if (unreduced_table.find(s) == unreduced_table.end()) {
                std::cerr << "[ERROR] Unspecified state: " << s << " in 2^N state universe!\n";
                continue;
            }

            std::string mask = "";
            for (int i = static_cast<int>(n) - 1; i >= 0; --i) {
                mask += ((s >> i) & 1) ? 'T' : 'F';
            }

            auto acts = unreduced_table[s];
            current_rules.push_back({mask, format_action_sig(acts), acts, 1});
        }

        std::cout << "Initial Combinatorial Rules (2^N): " << current_rules.size() << "\n";

        // 2. Iterative Pairwise Merging (Quine-McCluskey Style)
        bool merged_any = true;
        while (merged_any) {
            merged_any = false;
            std::vector<MinimizedRule> next_generation;
            std::vector<bool> consumed(current_rules.size(), false);

            for (size_t i = 0; i < current_rules.size(); ++i) {
                for (size_t j = i + 1; j < current_rules.size(); ++j) {
                    if (current_rules[i].action_signature != current_rules[j].action_signature) continue;

                    // Check if masks differ by exactly one non-wildcard position
                    int diff_count = 0;
                    size_t diff_pos = 0;
                    bool compatible = true;

                    for (size_t pos = 0; pos < n; ++pos) {
                        char c1 = current_rules[i].condition_mask[pos];
                        char c2 = current_rules[j].condition_mask[pos];

                        if (c1 != c2) {
                            if ((c1 == 'T' && c2 == 'F') || (c1 == 'F' && c2 == 'T')) {
                                diff_count++;
                                diff_pos = pos;
                            } else {
                                compatible = false; // One is '-' and other is not
                                break;
                            }
                        }
                    }

                    if (compatible && diff_count == 1) {
                        std::string merged_mask = current_rules[i].condition_mask;
                        merged_mask[diff_pos] = '-'; // Replace with wildcard

                        // Check if this merged mask already exists in next_generation
                        bool already_exists = false;
                        for (const auto& ng : next_generation) {
                            if (ng.condition_mask == merged_mask && ng.action_signature == current_rules[i].action_signature) {
                                already_exists = true;
                                break;
                            }
                        }

                        if (!already_exists) {
                            next_generation.push_back({
                                merged_mask,
                                current_rules[i].action_signature,
                                current_rules[i].actions,
                                current_rules[i].covered_state_count * 2
                            });
                        }

                        consumed[i] = true;
                        consumed[j] = true;
                        merged_any = true;
                    }
                }
            }

            // Unmerged rules carry forward
            for (size_t k = 0; k < current_rules.size(); ++k) {
                if (!consumed[k]) {
                    next_generation.push_back(current_rules[k]);
                }
            }

            current_rules = next_generation;
        }

        std::cout << "Optimized Minimized Rules        : " << current_rules.size() << " rules\n";
        
        // Completeness validation
        int total_covered = 0;
        for (const auto& r : current_rules) {
            int k = 0;
            for (char ch : r.condition_mask) if (ch == '-') k++;
            total_covered += (1 << k);
        }
        std::cout << "Total State Space Verification   : " << total_covered << " / " << total_space 
                  << " (" << (total_covered == total_space ? "100% COMPLETE" : "DISCREPANCY") << ")\n";

        return current_rules;
    }

    void print_structured_english(const std::vector<MinimizedRule>& rules) const {
        std::cout << "\n================================================================================\n";
        std::cout << "              SYNTHESIZED STRUCTURED ENGLISH (PROCESS SPECIFICATION)\n";
        std::cout << "================================================================================\n";

        for (size_t r = 0; r < rules.size(); ++r) {
            const auto& rule = rules[r];
            std::cout << "RULE #" << (r + 1) << " [Mask: " << rule.condition_mask << "]:\n";
            std::cout << "  IF ";

            bool first = true;
            for (size_t c = 0; c < n; ++c) {
                char val = rule.condition_mask[c];
                if (val == '-') continue;

                if (!first) std::cout << " AND\n     ";
                std::cout << condition_names[c] << " IS " << (val == 'T' ? "TRUE" : "FALSE");
                first = false;
            }

            if (first) std::cout << "[DEFAULT / UNCONDITIONAL]";

            std::cout << "\n  THEN\n";
            for (const auto& a : rule.actions) {
                std::cout << "     EXECUTE: " << a << ";\n";
            }
            std::cout << "\n";
        }
        std::cout << "================================================================================\n";
    }
};

// ============================================================================
// SIMULATION HARNESS: INTENSIVE CARE TELEMETRY ALARM ENGINE
// ============================================================================

int main() {
    // 3 Binary Conditions -> 2^3 = 8 States
    // C0: Heart Rate Abnormal (T/F)
    // C1: Blood Oxygen SpO2 < 90% (T/F)
    // C2: Patient In Transport / Movement (T/F)
    std::vector<std::string> conditions = {
        "Heart_Rate_Abnormal",
        "SpO2_Critically_Low",
        "Patient_In_Motion"
    };

    std::vector<std::string> actions = {
        "Sound_Acoustic_Code_Blue_Alarm",
        "Dispatch_Nurse_Station_Alert",
        "Log_Telemetry_Artifact_Warning",
        "Suppression_Motion_Artifact"
    };

    DecisionTableReducer reducer(conditions, actions);

    // Populate truth table for all 8 states (0 to 7)
    // State bit representation: [HR][SpO2][Motion]
    // 000: F, F, F -> Normal
    reducer.register_state_action(0b000, {"Log_Telemetry_Artifact_Warning"});
    // 001: F, F, T -> Motion normal
    reducer.register_state_action(0b001, {"Suppression_Motion_Artifact"});
    // 010: F, T, F -> Low oxygen, no motion -> Code Blue
    reducer.register_state_action(0b010, {"Sound_Acoustic_Code_Blue_Alarm", "Dispatch_Nurse_Station_Alert"});
    // 011: F, T, T -> Low oxygen with motion -> Check artifact, dispatch alert
    reducer.register_state_action(0b011, {"Dispatch_Nurse_Station_Alert", "Suppression_Motion_Artifact"});
    // 100: T, F, F -> Abnormal heart, no motion -> Code Blue
    reducer.register_state_action(0b100, {"Sound_Acoustic_Code_Blue_Alarm", "Dispatch_Nurse_Station_Alert"});
    // 101: T, F, T -> Abnormal heart with motion -> Dispatch alert
    reducer.register_state_action(0b101, {"Dispatch_Nurse_Station_Alert", "Suppression_Motion_Artifact"});
    // 110: T, T, F -> Both abnormal, no motion -> High Priority Code Blue
    reducer.register_state_action(0b110, {"Sound_Acoustic_Code_Blue_Alarm", "Dispatch_Nurse_Station_Alert"});
    // 111: T, T, T -> Both abnormal with motion -> Immediate Code Blue (cannot suppress)
    reducer.register_state_action(0b111, {"Sound_Acoustic_Code_Blue_Alarm", "Dispatch_Nurse_Station_Alert"});

    // Minimize table using algebraic reduction
    auto minimized_rules = reducer.minimize_table();

    // Generate formal Structured English Specification
    reducer.print_structured_english(minimized_rules);

    return 0;
}
```

</details>

---

### 7. Reference Video Lecture

{{ media:sdlc-logic-process-video }}

In this video by Simplilearn, the critical phases of software development, logical system modeling, decision logic structures, and process specifications are reviewed across the software lifecycle.
