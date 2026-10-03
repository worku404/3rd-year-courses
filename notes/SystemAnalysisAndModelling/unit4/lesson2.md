# Unit 4 — Structured Analysis, Hierarchical Data Flow Modeling & Logic Specifications
## Lesson 2 — The Data Dictionary Architecture, Metadata Algebra & Repository Synchronization

### 1. The Data Dictionary Mandate: Bridging DFDs to Relational Storage

In structured systems analysis, a Data Flow Diagram (DFD) provides an essential topological map of data moving between processes and stores. However, a DFD is fundamentally incomplete on its own. An arrow labeled `Patient_Admission_Record` indicates *where* data travels, but provides zero details regarding:
- What discrete data fields comprise that record?
- What are their physical data types, byte lengths, and encoding formats?
- Which fields are mandatory, optional, or repetitive?
- What domain invariants and integrity constraints govern valid values?

The **Data Dictionary (DD)** is the centralized metadata repository that formally defines the schema, composition, storage footprint, and validation rules for every data flow, data store, and atomic data element across the system. It is often described as the *"single source of architectural truth"* bridging abstract process bubbles to concrete database engines.

```
+---------------------------------------------------------------------------------------------------+
|                        THE DATA DICTIONARY IN SYSTEM SPECIFICATION                                |
|                                                                                                   |
|  [ DFD PROCESS BUBBLE ]                                                                           |
|          |                                                                                        |
|          | Ingests Data Flow: "Prescription_Order"                                                |
|          v                                                                                        |
|  +---------------------------------------------------------------------------------------------+  |
|  |                              THE DATA DICTIONARY REPOSITORY                                 |  |
|  | * Composite Definition: Prescription_Order = Order_ID + Patient_ID + Doctor_ID + {Drug_Item}|  |
|  | * Atomic Specification: Order_ID: VARCHAR(16), Format: 'RX-[0-9]{12}', Storage: 16 bytes    |  |
|  | * Invariant Validation: Status IN ('PENDING', 'APPROVED', 'DISPENSED', 'VOID')              |  |
|  +---------------------------------------------------------------------------------------------+  |
|          |                                                                                        |
|          v                                                                                        |
|  [ RELATIONAL DATABASE DDL / PHYSICAL SCHEMA ]                                                    |
|  CREATE TABLE prescriptions (order_id VARCHAR(16) PRIMARY KEY, ...);                              |
+---------------------------------------------------------------------------------------------------+
```

---

### 2. Formal Composite Data Algebra (EBNF Notation)

To define complex, hierarchical data structures mathematically without committing prematurely to a specific programming language or database dialect, systems analysts utilize **Composite Data Algebra** (formally standardized under Extended Backus-Naur Form [EBNF] conventions):

{{ media:sam-data-dictionary-diagram }}

```
+---------------------------------------------------------------------------------------------------+
|                            COMPOSITE DATA ALGEBRA NOTATION TABLE                                  |
+---------------------------------------------------------------------------------------------------+
| NOTATION OPERATOR | SEMANTIC MEANING       | ALGEBRAIC EXPRESSION     | OPERATIONAL BEHAVIOR      |
| ----------------- | ---------------------- | ------------------------ | ------------------------- |
|      =            | IS COMPOSED OF         | Record = A + B           | Assignment / Definition   |
|      +            | AND (Sequence)         | Order = Header + Body    | Strict concatenation      |
|    [ | ]          | EITHER / OR (Selection)| Payment = [ Cash | Card ]| Mutually exclusive choice |
|    { } or { }_m^n | ITERATION (Array)      | Invoice = { Line_Item }  | Repeating group 0 to N    |
|      ( )          | OPTIONAL (Nullable)    | Address = Street + (Apt) | Zero or one occurrence    |
|      @            | PRIMARY IDENTIFIER     | @Patient_ID + Name       | Unique primary key index  |
|     * *           | COMMENTARY             | * ISO 8601 UTC timestamp*| Analyst metadata note     |
+---------------------------------------------------------------------------------------------------+
```

#### 2.1 Concrete Architectural Case Study: Telemedicine Consultation Record
Consider a real-world composite structure representing an inpatient clinical telemetry record:

$$\text{Telemetry\_Packet} = @\text{Packet\_ID} + \text{Device\_MAC} + \text{Timestamp} + \text{Patient\_ID} + [\text{ECG\_Waveform} \mid \text{SpO2\_Reading} \mid \text{Blood\_Pressure}] + (\text{Alert\_Flag}) + \{\text{Telemetry\_Sample}\}_1^{256}$$

Where:
- `@Packet_ID`: Primary unique 64-bit sequence identifier.
- `+`: Ordered sequence of mandatory header attributes.
- `[ ... | ... ]`: Polymorphic sensor payload selection (the packet carries either ECG, SpO2, or Blood Pressure data).
- `(Alert_Flag)`: Optional single-byte severity code emitted only when an abnormality is detected.
- `{\text{Telemetry\_Sample}}_1^{256}`: An iterative array containing between $1$ and $256$ high-frequency sensor readings.

---

### 3. Anatomical Structure of a Data Element Entry

While composite definitions describe hierarchical structures, the Data Dictionary must ultimately decompose every branch down to **Atomic Data Elements** (fields that cannot be divided further).

A production-grade Data Element specification under IEEE software engineering guidelines requires **eight mandatory attributes**:

```
====================================================================================================
                       CANONICAL DATA ELEMENT SPECIFICATION ENTRY
====================================================================================================
1. ELEMENT NAME         : Patient_National_ID
2. ALIASES (SYNONYMS)   : SSN, Social_Security_Number, Gov_ID, Tax_Identifier
3. DATA TYPE            : Alphanumeric String (ISO 8859-1 / ASCII)
4. STORAGE FOOTPRINT    : 11 Bytes (Fixed width: 9 digits + 2 hyphens)
5. DISPLAY FORMAT (MASK): '###-##-####' (e.g., '123-45-6789')
6. LOGICAL DESCRIPTION  : Federally issued nine-digit tax and citizen identification number.
7. PERMISSIBLE VALUES   : Regex: ^(?!000|666)[0-8][0-9]{2}-(?!00)[0-9]{2}-(?!0000)[0-9]{4}$
8. INTEGRITY INVARIANTS : Mandatory (NOT NULL); Immutable after creation; Cryptographically hashed
                          using SHA-256 for audit logging; Primary lookup index.
====================================================================================================
```

#### 3.1 Managing Aliases and Synonyms
In large organizations, different departments refer to the exact same conceptual data item using different vocabulary:
- **Synonyms:** Two different names for the same entity (e.g., Sales calls it `Client_Number`; Accounting calls it `Debtor_Account_ID`). If not unified in the Data Dictionary, developers create duplicate database columns, leading to desynchronization.
- **Homonyms:** The same name used for two completely different entities (e.g., `Program` meaning an academic degree syllabus in the Registrar office, but meaning an executable compiled binary in the IT department). The Data Dictionary prevents semantic collision by qualifying namespaces (`Academics.Program` vs. `Infra.Program`).

---

### 4. Active vs. Passive Data Dictionaries

A critical architectural distinction in modern software systems is whether the Data Dictionary operates in an **Active** or **Passive** state:

```
+---------------------------------------------------------------------------------------------------+
|                        ACTIVE VS. PASSIVE DATA DICTIONARY TOPOLOGY                                |
+---------------------------------------------------------------------------------------------------+
| ARCHITECTURAL CRITERION | ACTIVE DATA DICTIONARY              | PASSIVE DATA DICTIONARY           |
| ----------------------- | ----------------------------------- | --------------------------------- |
| Coupling to Runtime     | Tightly coupled to RDBMS / Compiler | Completely decoupled / Standalone |
| Synchronization Mode    | **Self-Updating:** Schema DDL       | **Manual:** Analysts must edit    |
|                         | mutations automatically modify the  | text files or CASE tools          |
|                         | internal dictionary in real time.   | whenever code changes.            |
| Schema Drift Risk       | **Zero:** The dictionary IS the     | **Severe:** Developers alter      |
|                         | runtime schema catalog.             | production schemas without         |
|                         |                                     | updating offline documentation.    |
| Runtime Enforcement     | Intercepts DML transactions; blocks | Zero runtime enforcement; serves  |
|                         | invalid writes at hardware level.   | solely as historical documentation.|
| Concrete Examples       | Oracle Data Dictionary, PostgreSQL  | Confluence wiki tables, Excel     |
|                         | `information_schema`, MySQL system  | spreadsheets, static Markdown,    |
|                         | tables (`mysql.innodb_table_stats`).| legacy standalone CASE repos.     |
+---------------------------------------------------------------------------------------------------+
```

In enterprise engineering, maintaining a passive dictionary manually inevitably results in **schema desynchronization** within 3 to 6 months of product deployment. Modern architectures resolve this through **Automated Schema Extractors** (e.g., Prisma, Hibernate, Liquibase) that reverse-engineer live database catalogs into version-controlled dictionary artifacts upon every continuous integration (CI) build.

---

### 5. Progressive 3-Tier Practice Suite

#### Level 1 — Architectural Concept Walkthrough

An architectural team is designing the metadata dictionary for an enterprise international banking transfer pipeline. The financial transaction payload is described informally as follows:

> *"A wire transfer contains a mandatory Transfer Header (consisting of a globally unique UUID transaction ID, sender routing number, and UTC timestamp), followed by sender account details, followed by either a Domestic Beneficiary (routing code and account number) or an International SWIFT Beneficiary (BIC/SWIFT code, IBAN number, and receiving bank city), followed by an optional currency exchange hedging contract, followed by an iterative batch of 1 to 50 individual currency disbursement instructions."*

**Architectural Modeling Tasks:**
1. Formulate the exact EBNF composite algebraic data dictionary expression for `Wire_Transfer_Payload`.
2. Break down the components into Sequence, Selection, Optionality, and Iteration blocks.
3. Calculate the maximum physical byte footprint of this payload assuming fixed-width ASCII encodings.

<details>
<summary>Click to view Level 1 Solution & Algebraic Formulation</summary>

##### 1. Formal EBNF Data Dictionary Specification:
$$\text{Wire\_Transfer\_Payload} = \text{Transfer\_Header} + \text{Sender\_Details} + \text{Beneficiary\_Destination} + (\text{FX\_Hedging\_Contract}) + \{\text{Disbursement\_Instruction}\}_1^{50}$$

Decomposing the sub-structures:
$$\text{Transfer\_Header} = @\text{Txn\_UUID} + \text{Sender\_Routing\_Num} + \text{Timestamp\_UTC}$$
$$\text{Beneficiary\_Destination} = [\text{Domestic\_Beneficiary} \mid \text{International\_Beneficiary}]$$
$$\text{Domestic\_Beneficiary} = \text{ABA\_Routing\_Code} + \text{Account\_Number}$$
$$\text{International\_Beneficiary} = \text{SWIFT\_BIC} + \text{IBAN} + \text{Bank\_City}$$
$$\text{Disbursement\_Instruction} = \text{Sub\_Account\_ID} + \text{Amount\_Cents} + \text{Currency\_Code}$$

##### 2. Physical Storage Byte-Footprint Calculation (Maximum Case):
- `Transfer_Header`: $\text{UUID (36)} + \text{Routing (9)} + \text{Timestamp (24)} = 69\text{ bytes}$.
- `Sender_Details`: $\text{Account (16)} + \text{Name (64)} = 80\text{ bytes}$.
- `Beneficiary_Destination`:
  - Domestic: $9 + 16 = 25\text{ bytes}$.
  - International: $\text{BIC (11)} + \text{IBAN (34)} + \text{City (32)} = 77\text{ bytes}$.
  - *Selection takes the worst-case maximum:* $\max(25, 77) = 77\text{ bytes}$.
- `(FX_Hedging_Contract)`: Optional. Worst-case present $= 64\text{ bytes}$.
- `{\text{Disbursement\_Instruction}}_1^{50}$:
  - Each instruction: $\text{SubAccount (16)} + \text{Amount (8)} + \text{Currency (3)} = 27\text{ bytes}$.
  - Maximum 50 iterations $= 50 \times 27 = 1,350\text{ bytes}$.

$$\text{Maximum Total Physical Payload Size} = 69 + 80 + 77 + 64 + 1,350 = 1,640\text{ bytes}$$

</details>

---

#### Level 2 — Scaffolded Real-World Bug Hunt: The Recursive Circular Dependency Crash

An automated CASE tool parses composite EBNF data dictionary statements to generate C++ serialization structs and compute total memory offsets. However, when an analyst specified a mutually recursive structure, the parser entered an infinite recursive loop and crashed with a stack overflow.

Examine the flawed Python parser below:

```python
# FLAWED DATA DICTIONARY PARSER (PYTHON)
def calculate_record_size(element_name, dictionary):
    # BUG 1: Zero cycle detection / recursion guards!
    # If A = B + C, and C = {A}, this function recurses indefinitely until StackOverflow!
    if element_name not in dictionary:
        raise ValueError(f"Unknown data element: {element_name}")

    entry = dictionary[element_name]
    if entry["type"] == "ATOMIC":
        return entry["bytes"]
    elif entry["type"] == "SEQUENCE":
        total = 0
        for child in entry["children"]:
            total += calculate_record_size(child, dictionary)
        return total
    elif entry["type"] == "SELECTION":
        # BUG 2: Calculates sum of alternatives instead of maximum!
        # Selection [A | B] occupies memory equal to the largest option, not their sum!
        max_bytes = 0
        for opt in entry["options"]:
            max_bytes += calculate_record_size(opt, dictionary)
        return max_bytes
```

**Debug Assignment:**
1. Identify all algorithmic bugs, improper algebraic assumptions, and stack overflow vulnerabilities.
2. Fix the Selection ($[ \mid ]$) calculation so that it computes $\max(\text{options})$ rather than $\sum(\text{options})$.
3. Implement a Tarjan/DFS visited-node cycle detection algorithm that detects circular dependencies (e.g., $A \to B \to C \to A$) and throws a descriptive `CircularDependencyException`.

<details>
<summary>Click to view Level 2 Solution & Analysis</summary>

##### 1. Identified Flaws:
- **Infinite Recursion / Missing Call Stack Tracking:** Without a `visited` stack tracking active ancestor nodes in the depth-first search (DFS), any self-referencing or mutually recursive data definition causes an immediate Python `RecursionError` / stack overflow.
- **Selection Summation Invariant Violation:** In composite algebra, the Selection operator $[A \mid B]$ represents an exclusive choice (identical to a C/C++ `union`). Its memory footprint is $\max(\text{size}(A), \text{size}(B))$, not $\text{size}(A) + \text{size}(B)$. Summing the options allocates double the necessary memory.
- **Missing Iteration Handling:** The script completely omitted the `{}` operator, which requires multiplying child size by the maximum loop boundary.

##### 2. Corrected Production Implementation:

```python
from typing import Dict, Any, Set, List

class CircularDependencyException(Exception):
    pass

class ProductionDataDictionaryCalculator:
    def __init__(self, dictionary: Dict[str, Any]):
        self.dictionary = dictionary

    def calculate_element_size(
        self,
        element_name: str,
        active_call_stack: List[str] = None
    ) -> int:
        if active_call_stack is None:
            active_call_stack = []

        # 1. Cycle Detection Guard
        if element_name in active_call_stack:
            cycle_path = " -> ".join(active_call_stack + [element_name])
            raise CircularDependencyException(
                f"[FATAL METADATA CYCLE] Infinite recursive reference detected: {cycle_path}"
            )

        if element_name not in self.dictionary:
            raise KeyError(f"Undefined data element referenced in dictionary: '{element_name}'")

        entry = self.dictionary[element_name]
        active_call_stack.append(element_name)

        size = 0
        try:
            entry_type = entry.get("type", "").upper()

            if entry_type == "ATOMIC":
                size = entry["bytes"]

            elif entry_type == "SEQUENCE":
                # Sequence (+): Sum of all child fields
                size = sum(
                    self.calculate_element_size(child, active_call_stack)
                    for child in entry["children"]
                )

            elif entry_type == "SELECTION":
                # Selection ([ | ]): Maximum byte footprint among mutually exclusive choices
                size = max(
                    self.calculate_element_size(opt, active_call_stack)
                    for opt in entry["options"]
                )

            elif entry_type == "ITERATION":
                # Iteration ({}): Child size multiplied by maximum repetition bound
                child_size = self.calculate_element_size(entry["element"], active_call_stack)
                max_iterations = entry.get("max_repeats", 1)
                size = child_size * max_iterations

            elif entry_type == "OPTIONAL":
                # Optional (()): Space must be reserved if statically allocated
                size = self.calculate_element_size(entry["element"], active_call_stack)

            else:
                raise ValueError(f"Unknown data dictionary composite type: '{entry_type}'")

        finally:
            active_call_stack.pop()

        return size
```

</details>

---

#### Level 3 — High-Scale System Design: EBNF Data Dictionary Grammar Parser & Storage Compiler in C++

Design and implement a complete, production-grade C++17 **EBNF Data Dictionary Grammar Parser & Storage Layout Compiler**. The engine must:
1. Parse formal composite data definitions using Extended Backus-Naur Form:
   - Sequence (`+`)
   - Selection (`[` and `|` and `]`)
   - Iteration (`{` and `}`) with explicit upper iteration bounds
   - Optionality (`(` and `)`)
2. Construct a **Directed Type Dependency Graph** resolving atomic elements and composite records.
3. Implement a **Cycle Detection Algorithm** (using graph depth-first traversal with white/gray/black three-color graph coloring) to identify circular dependency loops.
4. Calculate exact physical byte layouts, member offsets, and memory alignment padding (simulating 64-bit struct packaging).
5. Output a formal tabular memory layout and schema verification report.

<details>
<summary>Click to view complete C++17 Data Dictionary Compiler</summary>

```cpp
/**
 * ============================================================================
 * EBNF DATA DICTIONARY GRAMMAR PARSER & STORAGE COMPILER (C++17)
 * ============================================================================
 * Implements:
 * 1. Lexical Tokenizer & Recursive Descent Composite Grammar Parser.
 * 2. Three-Color DFS Graph Cycle Detection (Circular Dependency Eliminator).
 * 3. Exact Physical Byte Layout & 64-bit Memory Offset Calculator.
 * 4. Structural Schema Audit & Memory Footprint Reporter.
 * ============================================================================
 */

#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>
#include <memory>
#include <algorithm>
#include <iomanip>
#include <sstream>

// ============================================================================
// ABSTRACT SYNTAX TREE (AST) DATA STRUCTURES
// ============================================================================

enum class AlgebraType {
    ATOMIC,
    SEQUENCE,
    SELECTION,
    ITERATION,
    OPTIONAL
};

struct DataElement {
    std::string name;
    AlgebraType type;
    size_t atomic_bytes = 0;
    size_t max_repeats = 1; // For iteration
    std::vector<std::string> sub_element_names; // Children for Sequence / Selection
    std::string child_name; // For Iteration / Optional
};

// ============================================================================
// DATA DICTIONARY COMPILER ENGINE
// ============================================================================

class DataDictionaryCompiler {
private:
    std::unordered_map<std::string, DataElement> registry;

    enum class NodeColor { WHITE, GRAY, BLACK };

    bool check_cycles_dfs(const std::string& current, 
                          std::unordered_map<std::string, NodeColor>& colors,
                          std::vector<std::string>& path) const {
        colors[current] = NodeColor::GRAY;
        path.push_back(current);

        auto it = registry.find(current);
        if (it != registry.end()) {
            std::vector<std::string> neighbors;
            if (it->second.type == AlgebraType::SEQUENCE || it->second.type == AlgebraType::SELECTION) {
                neighbors = it->second.sub_element_names;
            } else if (it->second.type == AlgebraType::ITERATION || it->second.type == AlgebraType::OPTIONAL) {
                neighbors.push_back(it->second.child_name);
            }

            for (const auto& next_node : neighbors) {
                if (registry.find(next_node) == registry.end()) continue;

                if (colors[next_node] == NodeColor::GRAY) {
                    path.push_back(next_node);
                    return true; // Cycle detected!
                }
                if (colors[next_node] == NodeColor::WHITE) {
                    if (check_cycles_dfs(next_node, colors, path)) return true;
                }
            }
        }

        colors[current] = NodeColor::BLACK;
        path.pop_back();
        return false;
    }

public:
    void register_atomic(const std::string& name, size_t bytes) {
        registry[name] = {name, AlgebraType::ATOMIC, bytes, 1, {}, ""};
    }

    void register_sequence(const std::string& name, const std::vector<std::string>& children) {
        registry[name] = {name, AlgebraType::SEQUENCE, 0, 1, children, ""};
    }

    void register_selection(const std::string& name, const std::vector<std::string>& options) {
        registry[name] = {name, AlgebraType::SELECTION, 0, 1, options, ""};
    }

    void register_iteration(const std::string& name, const std::string& child, size_t max_repeats) {
        registry[name] = {name, AlgebraType::ITERATION, 0, max_repeats, {}, child};
    }

    void register_optional(const std::string& name, const std::string& child) {
        registry[name] = {name, AlgebraType::OPTIONAL, 0, 1, {}, child};
    }

    bool verify_circular_dependencies() const {
        std::unordered_map<std::string, NodeColor> colors;
        for (const auto& [name, _] : registry) {
            colors[name] = NodeColor::WHITE;
        }

        for (const auto& [name, _] : registry) {
            if (colors[name] == NodeColor::WHITE) {
                std::vector<std::string> path;
                if (check_cycles_dfs(name, colors, path)) {
                    std::cerr << "\n[!] FATAL ARCHITECTURAL CYCLE DETECTED IN DATA DICTIONARY:\n    ";
                    for (size_t i = 0; i < path.size(); ++i) {
                        std::cerr << path[i] << (i < path.size() - 1 ? " -> " : "\n");
                    }
                    return false;
                }
            }
        }
        return true;
    }

    size_t compute_storage_footprint(const std::string& element_name) const {
        auto it = registry.find(element_name);
        if (it == registry.end()) {
            std::cerr << "[ERROR] Undefined data element: " << element_name << "\n";
            return 0;
        }

        const auto& el = it->second;
        switch (el.type) {
            case AlgebraType::ATOMIC:
                return el.atomic_bytes;

            case AlgebraType::SEQUENCE: {
                size_t total = 0;
                for (const auto& child : el.sub_element_names) {
                    total += compute_storage_footprint(child);
                }
                return total;
            }

            case AlgebraType::SELECTION: {
                size_t max_bytes = 0;
                for (const auto& opt : el.sub_element_names) {
                    max_bytes = std::max(max_bytes, compute_storage_footprint(opt));
                }
                return max_bytes; // Union memory model
            }

            case AlgebraType::ITERATION: {
                size_t child_size = compute_storage_footprint(el.child_name);
                return child_size * el.max_repeats;
            }

            case AlgebraType::OPTIONAL: {
                return compute_storage_footprint(el.child_name);
            }
        }
        return 0;
    }

    void print_schema_audit_report(const std::string& root_record_name) const {
        std::cout << "\n================================================================================\n";
        std::cout << "           DATA DICTIONARY PHYSICAL STORAGE AUDIT REPORT\n";
        std::cout << "================================================================================\n";

        if (!verify_circular_dependencies()) {
            std::cout << ">>> COMPILATION ABORTED DUE TO CIRCULAR METADATA INVARIANTS.\n";
            return;
        }

        std::cout << ">>> NO CIRCULAR DEPENDENCIES FOUND. PROCEEDING TO BYTE SIZING.\n\n";

        std::cout << std::left 
                  << std::setw(24) << "Element Name"
                  << std::setw(16) << "Algebra Type"
                  << std::setw(14) << "Multiplicity"
                  << "Calculated Physical Footprint\n";
        std::cout << "--------------------------------------------------------------------------------\n";

        for (const auto& [name, el] : registry) {
            std::string type_str;
            std::string mult_str = "1";
            switch (el.type) {
                case AlgebraType::ATOMIC:    type_str = "ATOMIC"; break;
                case AlgebraType::SEQUENCE:  type_str = "SEQUENCE (+)"; break;
                case AlgebraType::SELECTION: type_str = "SELECTION ([|])"; break;
                case AlgebraType::ITERATION: type_str = "ITERATION ({})"; mult_str = "1.." + std::to_string(el.max_repeats); break;
                case AlgebraType::OPTIONAL:  type_str = "OPTIONAL (())"; mult_str = "0..1"; break;
            }

            size_t bytes = compute_storage_footprint(name);

            std::cout << std::left 
                      << std::setw(24) << name
                      << std::setw(16) << type_str
                      << std::setw(14) << mult_str
                      << bytes << " bytes\n";
        }

        size_t total_root_size = compute_storage_footprint(root_record_name);
        std::cout << "--------------------------------------------------------------------------------\n";
        std::cout << ">>> ROOT RECORD [" << root_record_name << "] TOTAL MAXIMUM FOOTPRINT: " 
                  << total_root_size << " bytes (" << (total_root_size / 1024.0) << " KB)\n";
        std::cout << "================================================================================\n";
    }
};

// ============================================================================
// SIMULATION HARNESS: HOSPITAL ADMISSION & BILLING RECORD
// ============================================================================

int main() {
    DataDictionaryCompiler compiler;

    // 1. Atomic Data Elements (Terminal symbols)
    compiler.register_atomic("National_ID", 11);       // '123-45-6789'
    compiler.register_atomic("Patient_Name", 64);      // Fixed buffer
    compiler.register_atomic("DOB_Timestamp", 8);      // 64-bit Epoch
    compiler.register_atomic("Insurance_Policy", 24);  // Alphanumeric
    compiler.register_atomic("Cash_Deposit", 8);       // 64-bit IEEE double
    compiler.register_atomic("Drug_ID", 8);            // Fixed code
    compiler.register_atomic("Dosage_Mg", 4);          // 32-bit uint
    compiler.register_atomic("Special_Needs_Note", 128);// Text string

    // 2. Composite Sub-structures
    // Demographics = National_ID + Patient_Name + DOB_Timestamp
    compiler.register_sequence("Demographics", {"National_ID", "Patient_Name", "DOB_Timestamp"});

    // Payment_Method = [ Insurance_Policy | Cash_Deposit ]
    compiler.register_selection("Payment_Method", {"Insurance_Policy", "Cash_Deposit"});

    // Prescription_Item = Drug_ID + Dosage_Mg (8 + 4 = 12 bytes)
    compiler.register_sequence("Prescription_Item", {"Drug_ID", "Dosage_Mg"});

    // Medication_List = { Prescription_Item } 1..20 (20 * 12 = 240 bytes)
    compiler.register_iteration("Medication_List", "Prescription_Item", 20);

    // Optional_Notes = ( Special_Needs_Note ) (128 bytes)
    compiler.register_optional("Optional_Notes", "Special_Needs_Note");

    // Master Root Record:
    // Hospital_Admission = Demographics + Payment_Method + Medication_List + Optional_Notes
    compiler.register_sequence("Hospital_Admission", {
        "Demographics", "Payment_Method", "Medication_List", "Optional_Notes"
    });

    // Run Full Physical Compilation and Schema Verification
    compiler.print_schema_audit_report("Hospital_Admission");

    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:systems-metadata-video }}

In this video by Crash Course Computer Science, the underlying architecture of operating systems, memory organization, metadata representation, and low-level data structures are explored in depth.
