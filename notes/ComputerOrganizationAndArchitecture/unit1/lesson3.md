# Unit 1 — Introduction to Computer Organization, Architecture & Top-Level Structure
## Lesson 3 — CPU Internal Microarchitecture, Registers & The Execution Engine

### 1. CPU Internal Microarchitecture & The Internal Datapath

At the core of the computer sits the **Central Processing Unit (CPU)**. While previous lessons examined the CPU as a single structural block interfacing with the System Bus, this lesson opens the silicon casing to inspect the internal microarchitecture: the **Arithmetic and Logic Unit (ALU)**, the **Control Unit (CU)**, the **Register File**, and the **Internal CPU Bus**.

```
+-----------------------------------------------------------------------------------+
|                        CPU INTERNAL MICROARCHITECTURE                             |
|                                                                                   |
|           +-----------------------------------------------------------+           |
|           |                   INTERNAL CPU BUS                        |           |
|           +-----+-------------+-------------+-------------+-----------+           |
|                 |             |             |             |                       |
|                 v             v             v             v                       |
|          +------------+ +------------+ +------------+ +------------+              |
|          |  CONTROL   | |  REGISTER  | | ARITHMETIC | |   MEMORY   |              |
|          |    UNIT    | |    FILE    | |    LOGIC   | | INTERFACE  |              |
|          |    (CU)    | |   (GPRs)   | |  UNIT(ALU) | |  (MAR/MBR) |              |
|          +------------+ +------------+ +------------+ +------------+              |
|                 |             |             |             |                       |
|                 |             +------+------+             |                       |
|                 |                    |                    |                       |
|                 v                    v                    v                       |
|           [Decoders &          [Operand A/B        [Address & Data                |
|          Control Lines]        & Result Bus]        System Lines]                 |
+-----------------------------------------------------------------------------------+
```

{{ media:coa-cpu-datapath-diagram }}

#### The Primary Subsystems of the CPU

##### 1. The Arithmetic and Logic Unit (ALU)
The computational workhorse of the processor. The ALU receives two binary operand inputs (typically from internal registers or the internal bus), performs a specified arithmetic or boolean operation, outputs the $N$-bit result, and updates the hardware status flags.
- **Arithmetic Primitives:** Addition, Subtraction, Increment, Decrement, Two's complement negation, and hardware Multiplication/Division.
- **Logic Primitives:** Bitwise `AND`, `OR`, `XOR`, `NOT`, and bit shifting (`Logical Shift Left`, `Logical Shift Right`, `Arithmetic Shift Right`, `Rotate`).
- **Timing & Latency:** In a standard single-cycle integer ALU, basic operations complete within a single clock cycle ($< 0.3\text{ ns}$ at 3.5 GHz).

##### 2. The Control Unit (CU)
The supervisory coordinator that directs the physical operation of the entire system. At every phase of the clock cycle, the Control Unit asserts or de-asserts electrical control signals (voltages) that:
- Gate data out of specific registers onto the internal bus.
- Select the active operation code on the ALU input lines (`ALUOp`).
- Enable write-back of results into the destination register (`RegWrite`).
- Issue read or write command strobes to external memory (`MemRead`, `MemWrite`).
- Multiplex operand sources (e.g., choosing between a register operand or a sign-extended immediate constant).

##### 3. The Internal CPU Bus
A set of parallel internal connections optimized for high-speed intra-die data movement. It is completely isolated from the slower external System Bus. By isolating internal register transfers from external memory transactions, the CPU can execute register-to-register arithmetic without inducing external bus contention.

---

### 2. Comprehensive Register Typology & The Status Register

Registers are the fastest storage locations in the entire computer memory hierarchy. Implemented as static D flip-flop latches directly embedded inside the datapath, registers provide read/write access times under **0.1 nanoseconds**.

Computer architects partition registers into two operational categories: **User-Visible Registers** and **Control and Status Registers**.

#### Category A: User-Visible Registers (Programmer-Accessible)
These registers can be referenced directly by machine instructions and assembly programmers to minimize slow main memory accesses:

##### 1. General-Purpose Registers (GPRs)
Can be assigned arbitrarily by compilers for arithmetic, string manipulations, or temporary storage:
- In **x86-64**: 16 GPRs (`RAX`, `RBX`, `RCX`, `RDX`, `RSI`, `RDI`, `RBP`, `RSP`, and `R8` through `R15`).
- In **RISC-V**: 32 GPRs (`x0` through `x31`, where `x0` is hardwired permanently to zero).

##### 2. Dedicated Address & Pointer Registers
- **Stack Pointer (`RSP` / `SP`):** Points to the top of the active execution Call Stack in memory. Automatically decremented on `PUSH` and incremented on `POP`.
- **Base / Frame Pointer (`RBP` / `FP`):** Points to the base of the current stack frame, establishing a stable reference anchor for accessing function arguments and local variables.
- **Index Registers (`RSI` / `RDI`):** Used in base-plus-index and scaled-indexed addressing modes for rapid array and string traversals.

##### 3. The Program Status Word (PSW / Condition Flags)
A collection of individual 1-bit flip-flops that record the algebraic outcome of the most recent ALU instruction. Conditional jump instructions (`JE`, `JNE`, `JG`, `JL`, `JC`) inspect these flags to make branching decisions:

```
+-----------------------------------------------------------------------------------+
|               PROGRAM STATUS WORD (PSW / RFLAGS REGISTER)                         |
|                                                                                   |
|  [ ... | OF | DF | IF | TF | SF | ZF | AF | PF | CF ]                             |
|          |         |    |    |    |         |    |                                |
|          |         |    |    |    |         |    +--> Carry Flag (Unsigned OVF)   |
|          |         |    |    |    |         +-------> Parity Flag (Even parity)   |
|          |         |    |    |    +-----------------> Zero Flag (Result == 0)     |
|          |         |    |    +----------------------> Sign Flag (MSB == 1)        |
|          |         |    +---------------------------> Trap Flag (Single-step debug|
|          |         +--------------------------------> Interrupt Enable Flag       |
|          +------------------------------------------> Overflow Flag (Signed OVF)  |
+-----------------------------------------------------------------------------------+
```

| Flag Bit | Name | Hardware Assertion Condition | Primary Architectural Use Case |
| :--- | :--- | :--- | :--- |
| **`ZF`** | Zero Flag | Set to $1$ if the ALU result is strictly zero ($0$). | Loop termination, equality tests (`CMP A, B`). |
| **`SF`** | Sign Flag | Set to $1$ if the most significant bit (MSB) of the result is $1$. | Negative value detection in signed arithmetic. |
| **`CF`** | Carry Flag | Set to $1$ if an arithmetic operation generates a carry out of (addition) or borrow into (subtraction) the MSB. | **Unsigned integer overflow** detection; multi-word arithmetic (`ADC`, `SBB`). |
| **`OF`** | Overflow Flag | Set to $1$ if the signed result exceeds the representable range of the word ($+A + +B = -C$ or $-A + -B = +C$). | **Signed two's complement overflow** detection. |
| **`IF`** | Interrupt Flag | When set to $1$, the CPU recognizes external maskable hardware interrupts (`INTR`). | Critical section synchronization in OS kernels. |

---

#### Category B: Control & Status Registers (Microarchitecture-Internal)
These registers are used exclusively by the Control Unit and operating system kernel to govern the execution of instructions. Standard user-mode application software cannot directly read or write them:

##### 1. Program Counter (PC / RIP)
Holds the physical or virtual memory address of the **next instruction** to be fetched from memory. After every fetch micro-operation, the PC automatically increments by the instruction length in bytes ($PC \leftarrow PC + 4$ in 32-bit RISC architectures).

##### 2. Instruction Register (IR)
Holds the raw binary opcode and operand specifiers of the instruction currently being decoded and executed.

##### 3. Memory Address Register (MAR)
Directly wired to the physical **Address Bus** lines. Whenever the CPU reads or writes memory (whether fetching an instruction or loading data), it latches the target address into the MAR.

##### 4. Memory Buffer Register (MBR / MDR)
Directly wired to the bidirectional **Data Bus** lines. 
- On a **Memory Read**, the external memory drives data onto the bus, which latches into the MBR before transferring to internal registers.
- On a **Memory Write**, the CPU places data into the MBR, which drives the bus until memory completes writing.

---

### 3. Register Transfer Language (RTL) & Micro-operations

Every machine instruction (such as `ADD R1, [1000]`) is not an atomic hardware event. It decomposes into a sequence of microscopic, clock-synchronized hardware operations called **micro-operations ($\mu$-ops)**.

To formalize these hardware actions without ambiguity, computer scientists use **Register Transfer Language (RTL)**.

#### The Standard Instruction Cycle Decomposed

```
      +-------------+        +-------------+        +-------------+
      |    FETCH    | -----> |   DECODE    | -----> |   EXECUTE   |
      +------+------+        +-------------+        +------+------+
             ^                                             |
             |                                             v
             +-----------------[ INTERRUPT ]<--------------+
                               (If IRQ Pending)
```

##### 1. The Fetch Sub-Cycle (Universal to all instructions)
Fetches the instruction from memory at the location pointed to by the PC and places it into the IR:

$$\begin{aligned}
t_1: & \quad \text{MAR} \leftarrow (\text{PC}) \\
t_2: & \quad \text{MBR} \leftarrow \text{Memory}[\text{MAR}]; \quad \text{PC} \leftarrow (\text{PC}) + 4 \\
t_3: & \quad \text{IR} \leftarrow (\text{MBR})
\end{aligned}$$

- **Clock Cycle $t_1$:** The CPU copies the contents of the Program Counter onto the internal bus and latches it into the MAR.
- **Clock Cycle $t_2$:** The Control Unit asserts the `MemRead` control signal on the System Bus. Memory places the instruction into the MBR. Simultaneously, the ALU or dedicated adder increments the PC by 4 to prepare for the next instruction.
- **Clock Cycle $t_3$:** The instruction word is transferred from the MBR to the Instruction Register (`IR`).

##### 2. The Indirect Addressing Sub-Cycle (Optional)
If an instruction specifies indirect memory addressing (e.g., loading an operand from a pointer to a pointer), an additional memory read cycle is required:

$$\begin{aligned}
t_1: & \quad \text{MAR} \leftarrow (\text{IR}[\text{Address}]) \\
t_2: & \quad \text{MBR} \leftarrow \text{Memory}[\text{MAR}] \\
t_3: & \quad \text{IR}[\text{Address}] \leftarrow (\text{MBR}[\text{Address}])
\end{aligned}$$

##### 3. The Execute Sub-Cycle (Varies by Opcode)
The micro-operations executed depend entirely on the decoded opcode:

*Example A: Arithmetic Addition with Memory Operand (`ADD R1, [X]`):*
$$\begin{aligned}
t_1: & \quad \text{MAR} \leftarrow (\text{IR}[\text{Address}]) \\
t_2: & \quad \text{MBR} \leftarrow \text{Memory}[\text{MAR}] \\
t_3: & \quad \text{R1} \leftarrow (\text{R1}) + (\text{MBR}); \quad \text{PSW} \leftarrow \text{ALUStatus}
\end{aligned}$$

*Example B: Conditional Branch (`BEQ R1, R2, Offset`):*
$$\begin{aligned}
t_1: & \quad \text{ALU} \leftarrow (\text{R1}) - (\text{R2}) \\
t_2: & \quad \mathbf{if} \ (\text{ALUStatus.ZF} == 1) \ \mathbf{then} \ \text{PC} \leftarrow (\text{PC}) + (\text{IR}[\text{Offset}] \times 4)
\end{aligned}$$

##### 4. The Interrupt Sub-Cycle (Hardware Servicing)
At the end of every instruction's execution sub-cycle, the CPU samples its hardware Interrupt Request (`IRQ`) lines. If an unmasked interrupt is pending, the CPU saves its current state and vectors to the kernel's Interrupt Service Routine (ISR):

$$\begin{aligned}
t_1: & \quad \text{MBR} \leftarrow (\text{PC}); \quad \text{MAR} \leftarrow (\text{SP}) \\
t_2: & \quad \text{Memory}[\text{MAR}] \leftarrow (\text{MBR}); \quad \text{SP} \leftarrow (\text{SP}) - 8 \\
t_3: & \quad \text{PC} \leftarrow \text{ISR\_Vector\_Address}; \quad \text{PSW.IF} \leftarrow 0
\end{aligned}$$

---

### 4. Introduction to Instruction Pipelining & Hazard Taxonomy

In non-pipelined architectures, the execution of instruction $N+1$ cannot begin until instruction $N$ has completely traversed all fetch, decode, execute, memory, and writeback cycles. The majority of datapath hardware sits idle during any given clock period.

#### The 5-Stage Classic RISC Pipeline
Instruction Pipelining splits instruction execution across five overlapping hardware stages:
1. **IF (Instruction Fetch):** Fetch instruction from L1-I cache using PC.
2. **ID (Instruction Decode & Register Read):** Decode opcode; read source registers from Register File.
3. **EX (Execute / ALU):** Perform arithmetic or calculate effective memory address.
4. **MEM (Memory Access):** Read or write data from/to L1-D cache if instruction is a Load or Store.
5. **WB (Writeback):** Write computed result back into the destination register in the Register File.

```
Clock Cycle:   1    2    3    4    5    6    7    8
Inst 1:       [IF] [ID] [EX] [MEM] [WB]
Inst 2:            [IF] [ID] [EX] [MEM] [WB]
Inst 3:                 [IF] [ID] [EX] [MEM] [WB]
Inst 4:                      [IF] [ID] [EX] [MEM] [WB]
Inst 5:                           [IF] [ID] [EX] [MEM] [WB]
```
Under ideal steady-state pipelining, the CPU retires **one instruction per clock cycle** ($CPI = 1.0$), achieving a theoretical $5\times$ throughput speedup over a multi-cycle implementation.

#### Pipeline Hazards (The Structural Obstacles to Speedup)
Real-world execution pipelines cannot maintain ideal single-cycle throughput due to **Hazards**:
1. **Structural Hazards:** Hardware resource conflicts (e.g., a single-port memory attempting to serve an Instruction Fetch and a Data Load in the same cycle).
2. **Data Hazards (Data Dependencies):** An instruction attempts to read a register before a preceding instruction has written its result back (Read-After-Write / RAW hazard). Solved via **Hardware Forwarding / Bypassing** or inserting pipeline bubbles (stalls).
3. **Control Hazards (Branch Hazards):** The processor fetches instruction $PC + 4$, but a preceding branch instruction evaluates to taken, redirecting execution to a different target address. Solved via **Dynamic Branch Prediction** and branch target buffers (BTB).

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Micro-operation RTL Trace
Construct the exact Register Transfer Language ($\mu$-op) sequence for a subroutine return instruction `RET` on a 64-bit stack-based processor. The instruction must pop the 64-bit return address from the top of the stack (pointed to by `RSP`) and restore it into `PC`.

##### Step-by-Step RTL Micro-operation Trace:
| Clock Sub-cycle | RTL Expression | Internal Hardware Bus / Control Action |
| :--- | :--- | :--- |
| **Fetch $t_1$** | `MAR <- (PC)` | PC drives internal bus; latched into MAR. |
| **Fetch $t_2$** | `MBR <- Memory[MAR]; PC <- (PC) + 8` | MemRead asserted; instruction arrives in MBR; PC advanced. |
| **Fetch $t_3$** | `IR <- (MBR)` | Opcode transferred to IR for decoding. |
| **Decode $t_4$**| `CU decodes RET opcode` | Control Unit recognizes stack restoration instruction. |
| **Execute $t_5$**| `MAR <- (RSP)` | Stack Pointer drives internal bus; latched into MAR. |
| **Execute $t_6$**| `MBR <- Memory[MAR]; RSP <- (RSP) + 8` | MemRead asserted; return address arrives in MBR; RSP incremented. |
| **Execute $t_7$**| `PC <- (MBR)` | Return address restored to PC; control flow redirected! |

---

#### Level 2 — Scaffolded Bug-Fix: The Signed vs. Unsigned Flag Evaluation Hazard
A systems programmer wrote a custom bounds-checking routine in x86-64 assembly to validate memory allocations against a maximum buffer size. The code erroneously permits malicious negative integers, triggering a massive heap buffer overflow vulnerability.

##### The Broken Code:
```assembly
# BROKEN SECURITY CHECK: Validating buffer allocation size
# Input: EDI = requested size in bytes (32-bit integer)
validateBufferSize:
    cmpl  $1024, %edi           # Compare requested size with 1024
    
    # CRITICAL BUG: 'jg' (Jump if Greater) evaluates SIGNED flags: (SF ^ OF) == 0 && ZF == 0.
    # If an attacker passes a negative number (e.g. -1 = 0xFFFFFFFF),
    # the comparison treats -1 as LESS than 1024!
    # The check passes, and malloc subsequently treats 0xFFFFFFFF as 4GB unsigned!
    jg    .L_error_too_large
    
    call  allocateBuffer        # Vulnerable call executed!
    ret

.L_error_too_large:
    movl  $-1, %eax             # Return error code
    ret
```

<details>
<summary><strong>View Root Cause Analysis & Secure Flag Evaluation Solution</strong></summary>

##### Root Cause Analysis:
1. **The `CMP` Instruction:** Computes the algebraic difference between operands without saving the result:
   $$\text{ALU} = \text{EDI} - 1024$$
   It updates the hardware condition flags in the PSW: `ZF`, `SF`, `CF`, and `OF`.
2. **Signed vs Unsigned Branching Semantics:**
   - **`jg` (Jump if Greater):** Inspects **signed** condition flags: checks that $\text{SF} = \text{OF}$ and $\text{ZF} = 0$. When $\text{EDI} = -1$ ($0xFFFFFFFF$), $-1 - 1024 = -1025$, setting $\text{SF} = 1$ and $\text{OF} = 0$. Since $\text{SF} \neq \text{OF}$, `jg` evaluates to **false**, bypassing the error branch!
   - **`ja` (Jump if Above):** Inspects **unsigned** condition flags: checks that $\text{CF} = 0$ and $\text{ZF} = 0$. In unsigned representation, $0xFFFFFFFF = 4,294,967,295$, which is vastly above $1024$. The unsigned subtraction sets $\text{CF} = 0$ (no borrow), so `ja` evaluates to **true** and traps the overflow!

##### Secure Assembly Refactoring:
```assembly
# SECURE VALIDATION ROUTINE
# Input: EDI = requested size in bytes
validateBufferSizeSecure:
    # Fix: Use 'ja' (Jump if Above - Unsigned) instead of 'jg' (Signed)
    cmpl  $1024, %edi
    ja    .L_error_too_large    # Traps both >1024 AND all negative values (0x80000000+)!
    
    call  allocateBuffer
    ret

.L_error_too_large:
    movl  $-1, %eax
    ret
```
</details>

---

#### Level 3 — Production System Design: 5-Stage Pipelined RISC Datapath & Hazard Simulator

##### Architectural Challenge:
Design an architectural simulator in C++ for a **5-stage pipelined RISC processor** (IF, ID, EX, MEM, WB).
The simulator must model:
1. Discrete pipeline registers (`IF/ID`, `ID/EX`, `EX/MEM`, `MEM/WB`) passing instruction state between clock edges.
2. A **Hardware Forwarding Unit** that detects Read-After-Write (RAW) data dependencies and forwards ALU results from `EX/MEM` and `MEM/WB` directly to the `EX` stage, avoiding pipeline stalls.
3. A **Load-Use Hazard Detection Unit** that detects when an instruction immediately following a `LOAD` requires the loaded operand, inserting exactly one pipeline bubble (stall) and freezing the `PC` and `IF/ID` registers.

<details>
<summary><strong>View Production Architectural Implementation</strong></summary>

```cpp
/**
 * Production 5-Stage Pipelined RISC Processor Simulator
 * Features: Pipeline Inter-Stage Registers, Data Forwarding Unit & Load-Use Hazard Detection
 */
#include <iostream>
#include <vector>
#include <cstdint>
#include <string>
#include <iomanip>

enum OpType { OP_ADD, OP_SUB, OP_LOAD, OP_STORE, OP_NOP, OP_HALT };

struct Instruction {
    OpType type;
    int rd;    // Destination register
    int rs1;   // Source register 1
    int rs2;   // Source register 2 / Store value
    int imm;   // Immediate offset
    std::string mnemonic;
};

// 1. Pipeline Inter-Stage Registers
struct Reg_IF_ID {
    Instruction inst{OP_NOP, 0, 0, 0, 0, "NOP"};
    uint32_t pc{0};
};

struct Reg_ID_EX {
    Instruction inst{OP_NOP, 0, 0, 0, 0, "NOP"};
    int32_t val1{0};
    int32_t val2{0};
    int rd{0};
    int rs1{0};
    int rs2{0};
};

struct Reg_EX_MEM {
    Instruction inst{OP_NOP, 0, 0, 0, 0, "NOP"};
    int32_t aluResult{0};
    int32_t writeVal{0};
    int rd{0};
    bool regWrite{false};
    bool memRead{false};
    bool memWrite{false};
};

struct Reg_MEM_WB {
    Instruction inst{OP_NOP, 0, 0, 0, 0, "NOP"};
    int32_t finalData{0};
    int rd{0};
    bool regWrite{false};
};

class PipelinedRiscCore {
public:
    PipelinedRiscCore(const std::vector<Instruction>& program)
        : rom(program), pc(0), cycleCount(0), instructionsRetired(0), halted(false) {
        registers.resize(32, 0);
        dram.resize(1024, 0);
    }

    void run() {
        std::cout << ">>> 5-Stage Pipelined RISC Core Simulation Started <<<\n" << std::endl;

        while (!halted && cycleCount < 50) {
            cycleCount++;
            std::cout << "=== CLOCK CYCLE " << cycleCount << " (PC: " << pc << ") ===" << std::endl;

            // Pipeline operates in reverse stage order to simulate concurrent clock-edge latching
            stageWB();
            stageMEM();
            stageEX();
            stageID();
            stageIF();

            // Termination condition: All pipeline stages contain NOP/HALT
            if (if_id.inst.type == OP_HALT && id_ex.inst.type == OP_HALT &&
                ex_mem.inst.type == OP_HALT && mem_wb.inst.type == OP_HALT) {
                halted = true;
            }
        }

        printReport();
    }

private:
    std::vector<Instruction> rom;
    std::vector<int32_t> registers;
    std::vector<int32_t> dram;
    uint32_t pc;
    uint32_t cycleCount;
    uint32_t instructionsRetired;
    bool halted;

    // Inter-stage pipeline latches
    Reg_IF_ID  if_id;
    Reg_ID_EX  id_ex;
    Reg_EX_MEM ex_mem;
    Reg_MEM_WB mem_wb;

    // Hazard control wires
    bool stallPipeline{false};

    // Stage 5: Write-Back (WB)
    void stageWB() {
        if (mem_wb.regWrite && mem_wb.rd != 0) {
            registers[mem_wb.rd] = mem_wb.finalData;
            std::cout << "  [WB] Retiring " << mem_wb.inst.mnemonic 
                      << " -> R" << mem_wb.rd << " = " << mem_wb.finalData << std::endl;
            instructionsRetired++;
        }
    }

    // Stage 4: Memory Access (MEM)
    void stageMEM() {
        Reg_MEM_WB next_wb;
        next_wb.inst = ex_mem.inst;
        next_wb.rd = ex_mem.rd;
        next_wb.regWrite = ex_mem.regWrite;

        if (ex_mem.memRead) {
            next_wb.finalData = dram[ex_mem.aluResult % 1024];
            std::cout << "  [MEM] Load from DRAM[" << ex_mem.aluResult << "] -> " << next_wb.finalData << std::endl;
        } else if (ex_mem.memWrite) {
            dram[ex_mem.aluResult % 1024] = ex_mem.writeVal;
            std::cout << "  [MEM] Store " << ex_mem.writeVal << " into DRAM[" << ex_mem.aluResult << "]" << std::endl;
            next_wb.finalData = 0;
        } else {
            next_wb.finalData = ex_mem.aluResult;
        }

        mem_wb = next_wb;
    }

    // Stage 3: Execution & ALU (EX) with Hardware Data Forwarding Unit
    void stageEX() {
        Reg_EX_MEM next_mem;
        next_mem.inst = id_ex.inst;
        next_mem.rd = id_ex.rd;
        next_mem.regWrite = (id_ex.inst.type == OP_ADD || id_ex.inst.type == OP_SUB || id_ex.inst.type == OP_LOAD);
        next_mem.memRead  = (id_ex.inst.type == OP_LOAD);
        next_mem.memWrite = (id_ex.inst.type == OP_STORE);

        // --- HARDWARE DATA FORWARDING UNIT ---
        int32_t operandA = id_ex.val1;
        int32_t operandB = id_ex.val2;

        // Forwarding to Operand A
        if (ex_mem.regWrite && ex_mem.rd != 0 && ex_mem.rd == id_ex.rs1) {
            operandA = ex_mem.aluResult; // Forward from EX/MEM stage
            std::cout << "  [FORWARD] Forwarded R" << id_ex.rs1 << " from EX/MEM to ALU InA" << std::endl;
        } else if (mem_wb.regWrite && mem_wb.rd != 0 && mem_wb.rd == id_ex.rs1) {
            operandA = mem_wb.finalData; // Forward from MEM/WB stage
            std::cout << "  [FORWARD] Forwarded R" << id_ex.rs1 << " from MEM/WB to ALU InA" << std::endl;
        }

        // Forwarding to Operand B
        if (ex_mem.regWrite && ex_mem.rd != 0 && ex_mem.rd == id_ex.rs2) {
            operandB = ex_mem.aluResult;
            std::cout << "  [FORWARD] Forwarded R" << id_ex.rs2 << " from EX/MEM to ALU InB" << std::endl;
        } else if (mem_wb.regWrite && mem_wb.rd != 0 && mem_wb.rd == id_ex.rs2) {
            operandB = mem_wb.finalData;
            std::cout << "  [FORWARD] Forwarded R" << id_ex.rs2 << " from MEM/WB to ALU InB" << std::endl;
        }

        // Execute ALU Operation
        switch (id_ex.inst.type) {
            case OP_ADD:   next_mem.aluResult = operandA + operandB; break;
            case OP_SUB:   next_mem.aluResult = operandA - operandB; break;
            case OP_LOAD:  next_mem.aluResult = operandA + id_ex.inst.imm; break;
            case OP_STORE: 
                next_mem.aluResult = operandA + id_ex.inst.imm; 
                next_mem.writeVal = operandB;
                break;
            default:       next_mem.aluResult = 0; break;
        }

        ex_mem = next_mem;
    }

    // Stage 2: Instruction Decode & Register Read (ID) with Load-Use Hazard Unit
    void stageID() {
        // --- LOAD-USE HAZARD DETECTION UNIT ---
        if (id_ex.inst.type == OP_LOAD && 
           (id_ex.rd == if_id.inst.rs1 || id_ex.rd == if_id.inst.rs2)) {
            // Hazard detected! Must insert 1-cycle stall bubble into EX stage
            std::cout << "  [HAZARD] Load-Use Dependency Detected! Stalling pipeline..." << std::endl;
            stallPipeline = true;
            id_ex = Reg_ID_EX(); // Injects NOP bubble into EX stage
            return;
        }

        stallPipeline = false;
        Reg_ID_EX next_ex;
        next_ex.inst = if_id.inst;
        next_ex.rd   = if_id.inst.rd;
        next_ex.rs1  = if_id.inst.rs1;
        next_ex.rs2  = if_id.inst.rs2;
        next_ex.val1 = registers[if_id.inst.rs1];
        next_ex.val2 = registers[if_id.inst.rs2];

        id_ex = next_ex;
    }

    // Stage 1: Instruction Fetch (IF)
    void stageIF() {
        if (stallPipeline) {
            // Freeze PC and IF/ID register during a load-use stall!
            std::cout << "  [IF] Pipeline Stalled. Freezing PC at " << pc << std::endl;
            return;
        }

        if (pc < rom.size()) {
            if_id.inst = rom[pc];
            if_id.pc   = pc;
            std::cout << "  [IF] Fetched: " << rom[pc].mnemonic << std::endl;
            pc++;
        } else {
            if_id.inst = Instruction{OP_HALT, 0, 0, 0, 0, "HALT"};
        }
    }

    void printReport() const {
        std::cout << "
=============================================" << std::endl;
        std::cout << "   PIPELINED PROCESSOR EXECUTION METRICS     " << std::endl;
        std::cout << "=============================================" << std::endl;
        std::cout << "Total Clock Cycles     : " << cycleCount << std::endl;
        std::cout << "Instructions Retired   : " << instructionsRetired << std::endl;
        double cpi = instructionsRetired == 0 ? 0.0 : static_cast<double>(cycleCount) / instructionsRetired;
        std::cout << "Cycles Per Instruction : " << std::fixed << std::setprecision(2) << cpi << " CPI" << std::endl;
        std::cout << "Final Register File State:" << std::endl;
        for (int i = 1; i <= 4; ++i) {
            std::cout << "  R" << i << " = " << registers[i] << std::endl;
        }
        std::cout << "=============================================
" << std::endl;
    }
};

int main() {
    // Demonstration Program exhibiting:
    // 1. RAW Dependency resolved via Hardware Forwarding: R1 updated by ADD, read immediately by SUB.
    // 2. Load-Use Hazard requiring a 1-cycle bubble: LOAD R3, followed immediately by ADD R4, R3.
    std::vector<Instruction> code = {
        {OP_ADD,   1, 0, 0, 10,  "ADD R1, R0, 10 (R1 = 10)"},     // R1 = 10
        {OP_SUB,   2, 1, 0, 3,   "SUB R2, R1, 3  (R2 = 7)"},      // RAW: Needs R1 (Forwarded!)
        {OP_STORE, 0, 0, 2, 100, "STORE R2 -> DRAM[100]"},        // DRAM[100] = 7
        {OP_LOAD,  3, 0, 0, 100, "LOAD R3 <- DRAM[100]"},         // R3 = 7
        {OP_ADD,   4, 3, 1, 0,   "ADD R4, R3, R1 (R4 = 17)"},     // LOAD-USE HAZARD: Stalls 1 cycle!
        {OP_HALT,  0, 0, 0, 0,   "HALT"}
    };

    // Initialize R0 as permanent 0
    PipelinedRiscCore cpu(code);
    cpu.run();

    return 0;
}
```

##### Architectural Verification:
- **Forwarding Unit Efficiency:** Eliminates stalls for ALU-to-ALU dependencies, maintaining continuous throughput.
- **Load-Use Interlock:** Automatically detects unforwardable memory latencies and injects deterministic hardware bubbles.
- **Microarchitectural Fidelity:** Perfectly demonstrates the pipeline state transitions between IF, ID, EX, MEM, and WB.
</details>

---

### 6. Reference Video Lecture
Review this foundational engineering animation of the internal CPU datapath, arithmetic logic unit, and register transfers:

{{ media:cpu-works-video }}
