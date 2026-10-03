# Unit 3 — Computer Function, Instruction Cycles, Interrupts & Bus Structures
## Lesson 1 — The Machine Instruction Cycle & State Transition Mechanics

### 1. The Fundamental Two-Step Instruction Cycle

At the lowest microarchitectural level, the function of a computer is the continuous, repetitive execution of machine instructions. Program execution consists of the processor repeatedly cycling through two fundamental phases: the **Fetch Cycle** and the **Execute Cycle**.

```
+-----------------------------------------------------------------------------------+
|                        BASIC TWO-STEP INSTRUCTION CYCLE                           |
|                                                                                   |
|                  +------------------+                                             |
|                  |   START / RESET  |                                             |
|                  +--------+---------+                                             |
|                           |                                                       |
|                           v                                                       |
|                    +------+-------+                                               |
|           +------> |  FETCH CYCLE | <------+                                      |
|           |        +------+-------+        |                                      |
|           |               |                |                                      |
|           |               v                |                                      |
|           |        +------+-------+        |                                      |
|           +------- | EXECUTE CYCLE| -------+                                      |
|     (Loop Next     +------+-------+   (Branch / Jump Loop)                        |
|    Instruction)           |                                                       |
|                           v                                                       |
|                    +------+-------+                                               |
|                    |     HALT     |                                               |
|                    +--------------+                                               |
+-----------------------------------------------------------------------------------+
```

#### 1. The Fetch Cycle
At the start of each instruction cycle, the processor fetches an instruction word from memory:
1. **The Program Counter (PC):** Holds the physical address of the instruction to be fetched.
2. **Memory Transfer:** The processor passes the address from the `PC` to the Memory Address Register (`MAR`), drives the external Address Bus, and asserts the `MemRead` control signal. Main memory places the instruction word onto the Data Bus, which latches into the Memory Buffer Register (`MBR`).
3. **Instruction Latching:** The instruction word is transferred from the `MBR` to the **Instruction Register (IR)**.
4. **PC Increment:** Unless a branch occurred, the processor increments the `PC` by the instruction length in bytes ($PC \leftarrow PC + I$) so that it points to the subsequent instruction in memory.

#### 2. The Execute Cycle
The processor decodes the raw binary opcode residing in the `IR` and performs the designated hardware micro-operations:
- **Operand Fetching:** If the instruction references data in memory, additional memory read cycles are initiated.
- **ALU Execution:** Operands are routed through the internal datapath into the Arithmetic and Logic Unit.
- **Result Write-Back:** The computed result is written back to an internal register, the condition status flags in the Program Status Word (`PSW`) are updated, or data is committed to memory.

{{ media:coa-inst-cycle-diagram }}

---

### 2. The Expanded Instruction Cycle State Transition Architecture

In modern computer architectures, a single instruction may involve multiple memory references, variable addressing modes, multi-word operands, and condition checking. To capture this complexity, William Stallings formalized the **Expanded Instruction Cycle State Transition Diagram**:

```
+-----------------------------------------------------------------------------------+
|                 EXPANDED INSTRUCTION CYCLE STATE TRANSITION MODEL                 |
|                                                                                   |
|         +-------------------------------------------------------------+           |
|         |                                                             |           |
|         v                                                             |           |
|     +-------+         +-------+         +-------+                     |           |
|     |  IAC  | ------> |  IF   | ------> |  IOD  |                     |           |
|     +-------+         +-------+         +---+---+                     |           |
|                                             |                         |           |
|                       +---------------------+---------------------+   |           |
|                       |                                           |   |           |
|                       v                                           v   |           |
|                   +-------+                                   +-------+           |
|       +---------> |  OAC  |                                   |  OS   |           |
|       |           +---+---+                                   +---+---+           |
|       |               |                                           ^               |
|       |               v                                           |               |
|       |           +-------+         +-------+                     |               |
|       +---------- |  OF   | ------> |  DO   | --------------------+               |
|   (Multiple       +-------+         +-------+                                     |
|    Operands)                                                                      |
+-----------------------------------------------------------------------------------+
```

#### Detailed State Transition Breakdown
1. **Instruction Address Calculation (IAC):** Determines the effective physical memory address of the next instruction to be executed. In linear execution, this is $PC \leftarrow PC + \text{length}$. In branching or subroutines, it computes target displacements: $PC \leftarrow PC + (\text{Offset} \times 4)$.
2. **Instruction Fetch (IF):** Reads the machine instruction from its calculated memory location into the processor's Instruction Register (`IR`).
3. **Instruction Operation Decoding (IOD):** The Control Unit decodes the opcode bits to determine the operation to be performed, the number of operands required, and their respective addressing modes.
4. **Operand Address Calculation (OAC):** If an operand resides in memory or requires address indirection (e.g., Base-Plus-Index, Displaced, or Indirect addressing), the processor computes the effective physical memory address of the source operand.
5. **Operand Fetch (OF):** Fetches the source operand from memory or reads it directly from the internal General-Purpose Register (GPR) file. For multi-operand instructions (e.g., `ADD R1, R2, R3`), this state repeats sequentially until all inputs are loaded.
6. **Data Operation (DO):** The Arithmetic and Logic Unit (ALU) performs the designated arithmetic transformation, boolean operation, or bitwise shift on the loaded operands.
7. **Operand Store (OS):** Writes the computed result into the destination location (an internal GPR or a physical memory address via the `MAR`/`MBR`). If an operation generates multiple results (such as integer division yielding both a quotient and a remainder), this state repeats.

---

### 3. The Four Machine Instruction Action Categories

Regardless of processor architecture (x86, ARM, RISC-V, MIPS), all machine instructions execute actions that fall into four fundamental functional categories:

| Category | Primary Functional Action | Example Assembly Mnemonics | Typical Hardware Datapath Flow |
| :--- | :--- | :--- | :--- |
| **Processor — Memory** | Transfers data between internal CPU registers and external memory addresses. | `MOV RAX, [RBP-8]`<br>`LDR R0, [R1]`<br>`SW t0, 0(sp)` | $\text{MAR} \leftarrow \text{Addr}$<br>$\text{MBR} \leftarrow \text{Memory}[\text{MAR}]$<br>$\text{Reg} \leftarrow \text{MBR}$ |
| **Processor — I/O** | Transfers data between internal CPU registers and external peripheral interface buffers. | `IN AL, 0x60`<br>`OUT 0x3F8, AL`<br>`MMIO Load/Store` | $\text{MAR} \leftarrow \text{Port}$<br>$\text{I/O Controller} \leftrightarrow \text{ALU/Reg}$ |
| **Data Processing** | Performs computational transformations on binary operands within the ALU. | `ADD R1, R2, R3`<br>`XOR EAX, EAX`<br>`MUL R4, R5` | $\text{ALU} \leftarrow \text{OpA} + \text{OpB}$<br>$\text{Dest} \leftarrow \text{ALU Result}$<br>$\text{PSW} \leftarrow \text{Status Flags}$ |
| **Control / Branch** | Evaluates conditions and alters the sequential flow of program execution. | `JMP 0x00401000`<br>`BEQ t0, t1, label`<br>`CALL printf` | $\text{ALU} \leftarrow \text{Reg}_A - \text{Reg}_B$<br>$\mathbf{if} \ (\text{Condition}) \ PC \leftarrow \text{Target}$ |

---

### 4. Register Transfer Language (RTL) Micro-operations

To illustrate how machine instructions translate into hardware actions, consider a hypothetical **16-bit Accumulator Computer** with:
- **Instruction Format:** 4-bit Opcode (supporting 16 instructions) + 12-bit Memory Address ($2^{12} = 4,096$ words).
- **Internal Registers:** `PC` (12 bits), `IR` (16 bits), `MAR` (12 bits), `MBR` (16 bits), `AC` (16 bits).

#### Canonical Instruction Execution Traces

```
Hypothetical Opcode Set:
0001 (0x1) = LOAD  M(X) -> AC <- Memory[X]
0010 (0x2) = STORE M(X) -> Memory[X] <- AC
0101 (0x5) = ADD   M(X) -> AC <- AC + Memory[X]
```

##### Example Program:
We examine the step-by-step register states for adding the contents of memory location `940` to memory location `941`, and storing the result in `941`:

```
Memory Initial State:
Address 300: 0x1940  (LOAD  M(940))
Address 301: 0x5941  (ADD   M(941))
Address 302: 0x2941  (STORE M(941))
Address 940: 0x0003  (Data value: 3)
Address 941: 0x0002  (Data value: 2)
Initial Registers: PC = 300, AC = 0x0000
```

```
STEP 1: Fetch and Execute Instruction at 300 (LOAD M(940))
  Fetch:
    t1: MAR <- PC (300)
    t2: MBR <- Memory[300] (0x1940); PC <- PC + 1 (301)
    t3: IR  <- MBR (0x1940)
  Execute:
    t4: MAR <- IR[0:11] (940)
    t5: MBR <- Memory[940] (0x0003)
    t6: AC  <- MBR (0x0003)
  Result: AC = 0x0003, PC = 301

STEP 2: Fetch and Execute Instruction at 301 (ADD M(941))
  Fetch:
    t1: MAR <- PC (301)
    t2: MBR <- Memory[301] (0x5941); PC <- PC + 1 (302)
    t3: IR  <- MBR (0x5941)
  Execute:
    t4: MAR <- IR[0:11] (941)
    t5: MBR <- Memory[941] (0x0002)
    t6: AC  <- AC + MBR (0x0003 + 0x0002 = 0x0005)
  Result: AC = 0x0005, PC = 302

STEP 3: Fetch and Execute Instruction at 302 (STORE M(941))
  Fetch:
    t1: MAR <- PC (302)
    t2: MBR <- Memory[302] (0x2941); PC <- PC + 1 (303)
    t3: IR  <- MBR (0x2941)
  Execute:
    t4: MAR <- IR[0:11] (941)
    t5: MBR <- AC (0x0005)
    t6: Memory[MAR] <- MBR (Memory[941] overwritten with 0x0005)
  Result: Memory[941] = 0x0005, AC = 0x0005, PC = 303
```

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Micro-operation State Trace
Trace the exact micro-operations and register contents for an indirect memory load instruction:
$$\text{LOAD\_INDIR R1, @(100)}$$
Where memory location `100` contains the pointer address `850`, and location `850` contains the actual integer operand `42`.

##### Micro-operation Sequence Table:
| Step / Clock | RTL Micro-operation | Hardware Action & Bus Signaling |
| :--- | :--- | :--- |
| **$t_1$ (Fetch)** | `MAR <- (PC)` | PC drives internal bus; latched into MAR. |
| **$t_2$ (Fetch)** | `MBR <- Memory[MAR]; PC <- (PC) + 4` | MemRead asserted; instruction arrives in MBR; PC advanced. |
| **$t_3$ (Fetch)** | `IR <- (MBR)` | Instruction opcode and address field latched into IR. |
| **$t_4$ (Decode)**| `CU decodes LOAD_INDIR` | Recognizes indirect addressing mode requirement. |
| **$t_5$ (OAC 1)** | `MAR <- (IR[Address: 100])` | Address of pointer latched into MAR. |
| **$t_6$ (OF 1)**  | `MBR <- Memory[MAR]` | MemRead asserted; pointer value `850` arrives in MBR. |
| **$t_7$ (OAC 2)** | `MAR <- (MBR)` | Pointer `850` transferred to MAR as effective operand address! |
| **$t_8$ (OF 2)**  | `MBR <- Memory[MAR]` | MemRead asserted; true operand value `42` arrives in MBR. |
| **$t_9$ (OS)**    | `R1 <- (MBR)` | Operand `42` loaded into destination register R1. |

---

#### Level 2 — Scaffolded Bug-Fix: The Shared Address Register Clashing Hazard
A hardware engineer synthesized an experimental dual-operand ALU execution state machine in Verilog. The instruction `ADD [Addr1], [Addr2]` attempts to read two distinct memory locations and compute their sum.

The hardware implementation below exhibits a critical race condition where the first operand is corrupted before the ALU can execute.

##### The Broken Hardware RTL Sequence:
```
// BROKEN MULTI-OPERAND MICRO-OPERATION STATE MACHINE
// Instruction: ADD [Addr1], [Addr2]
t1: MAR <- IR[Addr1]
t2: MBR <- Memory[MAR]         // MBR now holds Operand 1
t3: MAR <- IR[Addr2]           // Setting up address for Operand 2
t4: MBR <- Memory[MAR]         // BUG! Overwrites MBR with Operand 2 before ALU can read Operand 1!
t5: ALU <- MBR + MBR           // Evaluates Operand 2 + Operand 2! Corrupts calculation!
```

<details>
<summary><strong>View Root Cause Analysis & Hardware Latch Solution</strong></summary>

##### Root Cause Analysis:
The processor microarchitecture features only **one** Memory Buffer Register (`MBR`). In step $t_4$, when memory reads `Operand 2` into the `MBR`, the previous value (`Operand 1` read in step $t_2$) is destructively overwritten and lost forever. The subsequent ALU operation adds `Operand 2` to itself!

##### Refactored Hardware Micro-operation Solution:
The datapath must introduce an internal temporary operand latch register (`Y` or `TEMP`) to buffer the first operand before the `MBR` is reused for the second memory transaction:

```
// CORRECTED HARDWARE RTL SEQUENCE
t1: MAR  <- IR[Addr1]
t2: MBR  <- Memory[MAR]        // MBR holds Operand 1
t3: TEMP <- MBR                // Fix: Save Operand 1 into dedicated temporary latch register!
t4: MAR  <- IR[Addr2]          // Setup address for Operand 2
t5: MBR  <- Memory[MAR]        // MBR now holds Operand 2 (TEMP safely holds Operand 1)
t6: ALU  <- TEMP + MBR         // Correct addition of both independent operands!
t7: AC   <- ALU_Result
```
</details>

---

#### Level 3 — Production System Design: Cycle-Accurate Multi-State Microcode Sequencer Engine

##### Architectural Challenge:
Design an architectural simulation engine in C++ that models a **Multi-State Microprogrammed Instruction Sequencer**.

The simulator must:
1. Model the 7 discrete states of the expanded instruction cycle (`IAC`, `IF`, `IOD`, `OAC`, `OF`, `DO`, `OS`).
2. Simulate a microcode ROM containing control words that assert explicit control signals:
   `{ MAR_In, MBR_Out, PC_Inc, Reg_Write, ALU_Op, Mem_Read, Mem_Write }`.
3. Support direct, indirect, and register-based addressing modes.
4. Execute instructions clock-cycle by clock-cycle, maintaining an accurate cycle counter and state audit log.

<details>
<summary><strong>View Production Architectural Implementation</strong></summary>

```cpp
/**
 * Cycle-Accurate Multi-State Microcode Instruction Sequencer
 * Implements the 7-State Expanded Instruction Cycle State Machine
 */
#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>
#include <string>

enum class CycleState {
    IAC, // Instruction Address Calculation
    IF,  // Instruction Fetch
    IOD, // Instruction Operation Decoding
    OAC, // Operand Address Calculation
    OF,  // Operand Fetch
    DO,  // Data Operation (ALU)
    OS,  // Operand Store
    HALT
};

struct ControlSignals {
    bool marIn{false};
    bool mbrOut{false};
    bool pcInc{false};
    bool regWrite{false};
    bool memRead{false};
    bool memWrite{false};
    uint8_t aluOp{0}; // 1 = ADD, 2 = SUB, 3 = AND
};

class MicrocodeProcessor {
public:
    MicrocodeProcessor() : pc(0), mar(0), mbr(0), ir(0), ac(0),
                           state(CycleState::IAC), cycleCount(0), isIndirect(false) {
        memory.resize(4096, 0);
    }

    void loadMemory(uint16_t addr, uint16_t val) {
        if (addr < memory.size()) memory[addr] = val;
    }

    void setPC(uint16_t startAddr) {
        pc = startAddr;
    }

    void step() {
        cycleCount++;
        std::cout << "[Cycle " << std::setw(3) << cycleCount << "] State: " 
                  << stateToString(state) << " | PC: 0x" << std::hex << pc 
                  << " AC: 0x" << ac << std::dec << std::endl;

        switch (state) {
            case CycleState::IAC:
                // Calculate next instruction address (linear or branch)
                mar = pc;
                state = CycleState::IF;
                break;

            case CycleState::IF:
                // Read instruction from memory into MBR, advance PC, latch IR
                mbr = memory[mar];
                pc++;
                ir = mbr;
                state = CycleState::IOD;
                break;

            case CycleState::IOD: {
                // Decode Opcode (High 4 bits) and Addressing Flag (Bit 11)
                uint8_t opcode = (ir >> 12) & 0x0F;
                isIndirect = (ir & 0x0800) != 0; // Bit 11 is indirect bit
                uint16_t operandAddr = ir & 0x07FF;

                std::cout << "  -> Decoded Opcode: 0x" << std::hex << (int)opcode 
                          << " (Indirect: " << (isIndirect ? "YES" : "NO") 
                          << ") Addr: 0x" << operandAddr << std::dec << std::endl;

                if (opcode == 0x0) {
                    state = CycleState::HALT;
                } else if (opcode == 0x1 || opcode == 0x2 || opcode == 0x5) {
                    // Memory-referencing instructions proceed to OAC
                    mar = operandAddr;
                    state = CycleState::OAC;
                } else {
                    state = CycleState::DO;
                }
                break;
            }

            case CycleState::OAC:
                if (isIndirect) {
                    // First memory hop: Resolve pointer
                    mbr = memory[mar];
                    mar = mbr & 0x07FF; // Effective address
                    isIndirect = false; // Resolved
                    state = CycleState::OF;
                } else {
                    state = CycleState::OF;
                }
                break;

            case CycleState::OF: {
                uint8_t opcode = (ir >> 12) & 0x0F;
                if (opcode == 0x1 || opcode == 0x5) {
                    // LOAD or ADD fetches operand from memory
                    mbr = memory[mar];
                    state = CycleState::DO;
                } else if (opcode == 0x2) {
                    // STORE skips fetch, proceeds straight to OS
                    state = CycleState::OS;
                }
                break;
            }

            case CycleState::DO: {
                uint8_t opcode = (ir >> 12) & 0x0F;
                if (opcode == 0x1) {
                    // LOAD
                    ac = mbr;
                } else if (opcode == 0x5) {
                    // ADD
                    ac = ac + mbr;
                }
                state = CycleState::IAC; // Finished instruction
                break;
            }

            case CycleState::OS: {
                uint8_t opcode = (ir >> 12) & 0x0F;
                if (opcode == 0x2) {
                    // STORE
                    mbr = ac;
                    memory[mar] = mbr;
                }
                state = CycleState::IAC; // Finished instruction
                break;
            }

            case CycleState::HALT:
                break;
        }
    }

    void run() {
        while (state != CycleState::HALT && cycleCount < 100) {
            step();
        }
        std::cout << "
>>> Program Halted in " << cycleCount << " clock cycles. Final AC = " << ac << std::endl;
    }

private:
    std::vector<uint16_t> memory;
    uint16_t pc;
    uint16_t mar;
    uint16_t mbr;
    uint16_t ir;
    uint16_t ac;
    CycleState state;
    uint32_t cycleCount;
    bool isIndirect;

    static std::string stateToString(CycleState s) {
        switch (s) {
            case CycleState::IAC: return "IAC (Address Calc)";
            case CycleState::IF:  return "IF  (Fetch)";
            case CycleState::IOD: return "IOD (Decode)";
            case CycleState::OAC: return "OAC (Operand Addr)";
            case CycleState::OF:  return "OF  (Operand Fetch)";
            case CycleState::DO:  return "DO  (Data Operation)";
            case CycleState::OS:  return "OS  (Operand Store)";
            case CycleState::HALT:return "HALT";
            default: return "UNKNOWN";
        }
    }
};

int main() {
    MicrocodeProcessor cpu;

    // Load Program into memory at 0x100:
    // Opcode 0x1 = LOAD, Opcode 0x5 = ADD, Opcode 0x2 = STORE, Opcode 0x0 = HALT
    // Bit 11 = Indirect Addressing (0x0800)

    // Data Locations:
    cpu.loadMemory(0x200, 15);   // Direct Operand = 15
    cpu.loadMemory(0x201, 0x250);// Pointer to 0x250
    cpu.loadMemory(0x250, 35);   // Indirect Operand = 35

    // Instructions:
    // 0x1200: LOAD [0x200]             (Direct: AC = 15)
    // 0x5A01: ADD @[0x201] (0x5000 | 0x0800 | 0x201) (Indirect: AC = 15 + 35 = 50)
    // 0x2202: STORE [0x202]            (Direct: Memory[0x202] = 50)
    // 0x0000: HALT
    cpu.loadMemory(0x100, 0x1200);
    cpu.loadMemory(0x101, 0x5A01);
    cpu.loadMemory(0x102, 0x2202);
    cpu.loadMemory(0x103, 0x0000);

    cpu.setPC(0x100);
    cpu.run();

    return 0;
}
```

##### Architectural Verification:
- **State Transition Fidelity:** Validates the exact 7-state progression from Instruction Address Calculation (`IAC`) through Operand Store (`OS`).
- **Indirect Addressing Multi-Cycle Resolution:** Accurately models the extra memory traversal hop required for indirect pointer resolution.
</details>

---

### 6. Reference Video Lecture
Review this masterclass lecture on machine instructions, program flow, and the hardware fetch-decode-execute cycle:

{{ media:instructions-video }}
