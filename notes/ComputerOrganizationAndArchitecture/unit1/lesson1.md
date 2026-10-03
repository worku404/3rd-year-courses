# Unit 1 — Introduction to Computer Organization, Architecture & Top-Level Structure
## Lesson 1 — Computer Architecture vs. Computer Organization & The Hardware/Software Abstraction Hierarchy

### 1. The Fundamental Duality: Architecture vs. Organization

In computer engineering, the distinction between **Computer Architecture** and **Computer Organization** represents one of the most critical conceptual boundaries. Although colloquially conflated, they refer to fundamentally distinct domains of system design, governed by different abstraction contracts, optimization constraints, and lifecycles.

```
+-----------------------------------------------------------------------------------+
|                        THE COMPUTER DESIGN SPECTRUM                               |
|                                                                                   |
|  [ COMPUTER ARCHITECTURE ]                    [ COMPUTER ORGANIZATION ]           |
|  "The Programmer's Visible Model"             "The Physical Implementation"       |
|  - What the machine computes                  - How the machine executes          |
|  - Stable across processor generations        - Rapidly evolves with silicon node |
|  - Instruction Set Architecture (ISA)         - Datapath & Pipeline Depth         |
|  - Register Sets & Data Formats               - Cache Sizing & Memory Hierarchy   |
|  - Memory Addressing Modes                    - Control Unit Logic (Hardwired/uCode)|
|  - Interrupt & Exception Semantics            - Clock Frequencies & Bus Topologies|
+-----------------------------------------------------------------------------------+
```

{{ media:coa-arch-vs-org-diagram }}

#### Formal Definitions (Stallings / Patterson & Hennessy)

##### 1. Computer Architecture
Computer Architecture refers to those operational attributes of a computing system that are **directly visible to the programmer**—or more precisely, to the compiler writer and assembly language engineer. It constitutes the functional specifications and behavioral contract of the processor.

Key architectural attributes include:
- **The Instruction Set Architecture (ISA):** The complete vocabulary of machine operations (e.g., x86-64, ARMv9, RISC-V, MIPS).
- **Data Word Width & Formats:** Bit lengths used to represent primitive numeric entities (e.g., 32-bit signed two's complement integers, 64-bit IEEE 754 floating-point numbers).
- **Programmer-Visible Registers:** The quantity, bit-width, and architectural classification of registers (e.g., 16 General Purpose Registers in x86-64 vs 32 integer registers in RISC-V).
- **Memory Addressing Modes:** The mathematical mechanisms by which an instruction specifies the effective address of an operand in memory (e.g., Immediate, Direct, Register Indirect, Base-Plus-Index).
- **Interrupt & Exception Handling:** The architectural mechanism by which the CPU transitions from user-space execution to privileged kernel handlers upon encountering external hardware signals or software traps.

##### 2. Computer Organization
Computer Organization refers to the **underlying hardware units and their physical interconnections** that realize the architectural specification. Organizational decisions are entirely transparent to software programmers; executing the same compiled binary on different organizational implementations yields identical computational results, differing only in execution time, energy dissipation, and silicon cost.

Key organizational attributes include:
- **Control Unit Design:** Whether control signals are synthesized via combinational hardwired state machines (common in RISC) or microprogrammed control stores (common in CISC).
- **Memory Hierarchy Structure:** The number of cache levels (L1, L2, L3), cache line sizes, associativity (direct-mapped vs 8-way set-associative), and replacement algorithms.
- **ALU Circuit Realization:** Whether an integer adder is implemented as a low-cost Ripple-Carry Adder ($O(N)$ delay) or a high-performance Carry-Lookahead Adder ($O(\log N)$ delay).
- **Interconnection Infrastructure:** Whether components communicate over a shared parallel bus, an on-chip crossbar switch, or point-to-point packet-switched interconnects (e.g., PCIe, Intel Ultra Path Interconnect).
- **Clock Frequency & Pipelining Depth:** Whether an instruction executes in a single long cycle, a 5-stage classic RISC pipeline, or a 19-stage deep speculative superscalar out-of-order execution engine.

#### The Architectural Invariance Principle
A well-designed architecture can survive for decades across radically diverse organizational realizations. 

*The Canonical Industry Example:* The **Intel x86 architecture** originated in 1978 with the 16-bit 8086 microprocessor (29,000 transistors, 5 MHz clock, no cache, unpipelined). Over four decades, Intel and AMD implemented the identical x86 ISA across vastly different organizations—the 80386 (first 32-bit flat memory model), the Pentium (first superscalar dual-pipeline), the Pentium Pro (first out-of-order speculative execution engine), and modern multi-core Core i9 / AMD Zen 4 processors (billions of transistors, 5.7 GHz, 3-level cache hierarchies, 512-bit AVX-512 vector units). A legacy MS-DOS x86 binary compiled in 1982 executes correctly on a 2026 Core i9 without recompilation.

---

### 2. The Multi-Tier Computing Abstraction Hierarchy

Modern computing systems represent the most sophisticated engineering artifacts in human history, containing billions of microscopic switches operating at sub-nanosecond intervals. Managing this overwhelming complexity requires strict **hierarchical abstraction layers**. Each layer presents a clean, simplified interface to the layer above while encapsulating the messy physical reality of the layer below.

```
Level 5: High-Level Language (HLL)        C, C++, Rust, Python, Java
                   |  (Compiler / Interpreter)
                   v
Level 4: Assembly Language                x86-64 ASM, RISC-V ASM (Mnemonics, Labels)
                   |  (Assembler / Linker)
                   v
Level 3: Instruction Set Architecture    Binary Machine Code (0s & 1s, Opcodes)
       ========================================================= [HW / SW BOUNDARY]
Level 2: Microarchitecture               Pipelines, Branch Predictors, Caches, ALUs
                   |  (Register-Transfer Synthesis)
                   v
Level 1: Digital Logic                   Logic Gates (NAND, NOR, XOR), Flip-Flops
                   |  (Electronic Circuit Design)
                   v
Level 0: Physical Electronics            CMOS FET Transistors, Quantum Bandgaps
```

#### Detailed Layer Breakdown

##### Level 5: High-Level Language (HLL)
Programmers formulate algorithms using high-level paradigms (structured control flow, strong static typing, object-oriented or functional models). Machine specifics (registers, memory addresses, flags) are completely hidden.
```c
// Level 5: Pure Algorithmic Intent
uint64_t computeSum(const uint64_t* array, size_t length) {
    uint64_t sum = 0;
    for (size_t i = 0; i < length; ++i) {
        sum += array[i];
    }
    return sum;
}
```

##### Level 4: Assembly Language
The compiler translates Level 5 code into symbolic assembly mnemonics. Each instruction corresponds to a single machine-level operation, exposing processor registers, stack frames, and explicit memory indirection.
```assembly
# Level 4: x86-64 Assembly (System V AMD64 ABI)
# Arguments: RDI = array pointer, RSI = length
# Return: RAX = sum
computeSum:
    xor   %rax, %rax            # sum = 0
    xor   %rcx, %rcx            # i = 0
.L_loop:
    cmp   %rsi, %rcx            # compare i with length
    jge   .L_done               # if i >= length, exit loop
    add   (%rdi,%rcx,8), %rax   # sum += array[i] (Base-Index-Scale Addressing)
    inc   %rcx                  # i++
    jmp   .L_loop               # unconditional branch
.L_done:
    ret                         # return to caller with result in RAX
```

##### Level 3: The Instruction Set Architecture (ISA) — The HW/SW Nexus
The Assembler encodes the symbolic mnemonics into raw binary machine code. This layer constitutes the rigid contractual boundary between software and hardware.
```
Instruction: add (%rdi,%rcx,8), %rax
Machine Code (Hex): 48 03 04 CF
Binary Encoding:    01001000 00000011 00000100 11001111
  [REX.W Prefix: 64-bit operand] [Opcode: ADD r64, r/m64] [ModR/M] [SIB Byte]
```

##### Level 2: Microarchitecture
The hardware implementation of the ISA. The microarchitect designs the physical datapath: instruction fetch units, decoders that split complex CISC instructions into internal micro-operations ($\mu$-ops), reservation stations, reorder buffers (ROB), execution pipelines, and Level 1 instruction/data caches.

##### Level 1: Digital Logic & Register-Transfer Level (RTL)
The microarchitecture is synthesized into combinational and sequential digital logic primitives using Hardware Description Languages (Verilog or VHDL). Logic gates (AND, OR, NOT, NAND), multiplexers, arithmetic adders, and edge-triggered D flip-flops clocked by global clock distribution trees.

##### Level 0: Physical Electronics & Semiconductor Physics
The ultimate physical foundation. Digital logic gates are constructed from Complementary Metal-Oxide-Semiconductor (CMOS) field-effect transistors (nMOS and pMOS pairs) fabricated on silicon wafers via extreme ultraviolet (EUV) photolithography.

---

### 3. The Instruction Set Architecture (ISA) Paradigms: RISC vs. CISC

The historical evolution of computer architecture produced two competing design philosophies:

| Architectural Metric | CISC (Complex Instruction Set Computer) | RISC (Reduced Instruction Set Computer) |
| :--- | :--- | :--- |
| **Design Philosophy** | Heavy hardware complexity; rich instructions | Lean hardware simplicity; compiler optimization |
| **Instruction Length** | Variable (e.g., 1 to 15 bytes in x86-64) | Fixed (strictly 32 bits in standard RISC-V/ARM) |
| **Memory Operations** | Arithmetic instructions can directly access memory (`ADD [mem], EAX`) | **Load/Store Architecture:** Only `LOAD` and `STORE` access memory |
| **Addressing Modes** | Numerous and complex (Direct, Indexed, Scaled) | Minimal, orthogonal (typically Base + Immediate offset) |
| **Register Set** | Small, specialized register files (historical) | Large, orthogonal General Purpose Register file (32+ GPRs) |
| **Instruction Decoding** | Complex; requires multi-byte decoders or microcode | Trivial, hardwired; fixed opcode fields |
| **Cycles Per Instruction** | Highly variable (from 1 to 50+ clock cycles) | Single-cycle goal for basic operations ($CPI \approx 1$) |
| **Modern Exemplars** | Intel Core i7/i9, AMD Ryzen, IBM z/Architecture | ARM Cortex/Neoverse, RISC-V, Apple M-Series |

```
CISC Approach (x86):
  ADD [RDI], RAX        ; Fetches memory at [RDI], adds RAX, writes back to [RDI]
                        ; (1 single complex instruction, multiple memory cycles)

RISC Approach (RISC-V):
  LD   t0, 0(a0)        ; 1. Explicitly load from memory into temporary register t0
  ADD  t0, t0, a1       ; 2. Execute arithmetic strictly between registers
  SD   t0, 0(a0)        ; 3. Explicitly store computed result back to memory
                        ; (3 simple, single-cycle, easily pipelined instructions)
```

*The Modern Convergence:* Contemporary x86 processors (Intel, AMD) are internally hybrid. Externally, they present a CISC x86 interface for software compatibility. Internally, high-speed hardware decoders translate CISC instructions on the fly into RISC-like **micro-operations ($\mu$-ops)**, which execute on an ultra-fast out-of-order superscalar RISC core.

---

### 4. Silicon Realization & The Role of the Computer Architect

The computer architect does not merely design abstract instruction sets; they balance a multi-variable optimization matrix constrained by physics, thermodynamics, and manufacturing economics:

$$\text{The Architect's PPA Triangle:} \quad \text{Performance} \longleftrightarrow \text{Power (Watts)} \longleftrightarrow \text{Area (Cost } \text{mm}^2\text{)}$$

#### Historical Scaling Laws and Their Limits

##### 1. Moore's Law (Gordon Moore, 1965)
The empirical observation that the number of transistors packed onto a dense integrated circuit doubles approximately every 18 to 24 months at minimum component cost. This exponential growth drove computing performance for 50 years.

##### 2. Dennard Scaling (Robert Dennard, 1974)
Dennard observed that as transistor dimensions shrink, their power density remains constant:
$$\text{Power} = C \cdot V^2 \cdot f$$
Where $C$ is capacitance, $V$ is supply voltage, and $f$ is clock frequency. As transistors got smaller, voltage could scale downward proportionally, allowing clock frequencies to increase dramatically (from 5 MHz in 1980 to 3.8 GHz in 2004) without melting the silicon chip.

##### 3. The Power Wall & The Multi-Core Era (2004 - Present)
Around 2004, Dennard scaling collapsed. As transistor gate oxide thicknesses dropped below 1.2 nanometers, quantum mechanical tunneling caused catastrophic **subthreshold static leakage current**. Voltages could no longer be reduced safely without inducing noise errors. 

Because power dissipates as heat, single-thread clock frequencies stalled around 4 to 5 GHz (The "Power Wall"). To continue increasing performance, computer architects were forced to abandon single-thread frequency scaling and transition to **parallel architectures: multi-core processors, heterogeneous computing (big.LITTLE), and domain-specific hardware accelerators (GPUs, TPUs, NPUs)**.

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Abstraction Trace of an Arithmetic Accumulator
Trace the expression $Z = X + Y$ through all 6 levels of the computing abstraction hierarchy. Fill out the operational characteristics table.

```c
// Given High-Level Assignment:
uint32_t x = 42;
uint32_t y = 58;
uint32_t z = x + y;
```

##### Multi-Tier Abstraction State Table:
| Abstraction Level | Concrete Artifact / Representation | Controlling Entity | Key Operational Mechanism |
| :--- | :--- | :--- | :--- |
| **Level 5: HLL** | `uint32_t z = x + y;` | Programmer / IDE | Strongly typed 32-bit unsigned arithmetic expression. |
| **Level 4: Assembly** | `movl $42, %eax`<br>`movl $58, %ebx`<br>`addl %ebx, %eax` | Compiler (GCC/Clang) | Maps variable identifiers to registers `EAX` and `EBX`; emits symbolic mnemonics. |
| **Level 3: ISA** | `01 D8` (Hex) $\to$<br>`00000001 11011000` (Binary) | Assembler / Linker | Opcode `01` specifies `ADD r/m32, r32`. ModR/M byte `D8` binds source `EBX` to destination `EAX`. |
| **Level 2: Microarch** | Datapath multiplexer routes `EAX` and `EBX` to ALU input ports. | Microarchitect | Register file reads operands on positive clock edge; ALU asserts 32-bit result bus. |
| **Level 1: Digital Logic**| 32-bit Carry-Lookahead Adder Circuit | Logic Synthesis Tool | Computes Generate ($G_i = A_i \cdot B_i$) and Propagate ($P_i = A_i \oplus B_i$) logic trees. |
| **Level 0: Transistors** | Silicon CMOS Inverter & Transmission Gates | Foundry (TSMC / Intel) | nMOS channels conduct electrons when gate is high; pMOS pull up output to $V_{DD}$. |

---

#### Level 2 — Scaffolded Bug-Fix: The Endianness & Memory Alignment Fault
A software engineer ported a high-performance network packet parser from an x86-64 server to an embedded 32-bit RISC-V industrial gateway. The code immediately crashes with a `SIGBUS: Unaligned Access Trap` and extracts corrupted integer values.

##### The Broken Code:
```c
// BROKEN: Parsing a binary network telemetry packet
#include <stdint.h>
#include <stdio.h>

void parseTelemetry(const uint8_t* rawBuffer) {
    // Packet Header:
    // Byte 0: Packet Type (8-bit)
    // Bytes 1-4: Sequence Number (32-bit integer)
    
    uint8_t packetType = rawBuffer[0];
    
    // BUG 1: Alignment Fault! rawBuffer + 1 is an ODD memory address.
    // Strict RISC architectures trap on 32-bit reads from unaligned addresses!
    // BUG 2: Endianness Mismatch! Network wire format is Big-Endian (RFC 1700),
    // but the host hardware is Little-Endian!
    uint32_t* seqPtr = (uint32_t*)(rawBuffer + 1);
    uint32_t sequenceNumber = *seqPtr;
    
    printf("Type: %u, Seq: %u\n", packetType, sequenceNumber);
}
```

<details>
<summary><strong>View Root Cause Analysis & Portable Architecture-Aware Solution</strong></summary>

##### Root Cause Analysis:
1. **Memory Alignment Trap:** Modern high-performance RISC architectures (e.g., standard RISC-V, ARMv7, SPARC) require that an $N$-byte data access occur at a memory address that is an exact multiple of $N$ ($	ext{Address} \pmod N == 0$). Dereferencing `rawBuffer + 1` as a 32-bit (`uint32_t*`) pointer forces a 4-byte read from an odd byte address ($	ext{Address} \pmod 4 \neq 0$), triggering a hardware alignment fault exception.
2. **Endianness Conflict:** Network protocol headers standardize on **Big-Endian** (Most Significant Byte stored at lowest memory address). Most modern client/server microprocessors (x86-64, ARM, RISC-V) are **Little-Endian** (Least Significant Byte at lowest address). Direct memory casts invert the byte significance, turning `0x00000001` into `0x01000000` ($16,777,216$).

##### Portable, Robust Enterprise Solution:
```c
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Portable architecture-agnostic Big-Endian to Host conversion
static inline uint32_t readBigEndianUint32(const uint8_t* src) {
    // Shift bytes explicitly: Immune to hardware endianness and memory alignment traps!
    return ((uint32_t)src[0] << 24) |
           ((uint32_t)src[1] << 16) |
           ((uint32_t)src[2] << 8)  |
           ((uint32_t)src[3]);
}

void parseTelemetryRobust(const uint8_t* rawBuffer) {
    uint8_t packetType = rawBuffer[0];
    
    // Safely extract 32-bit integer without unaligned pointer casts
    uint32_t sequenceNumber = readBigEndianUint32(rawBuffer + 1);
    
    printf("Type: %u, Seq: %u\n", packetType, sequenceNumber);
}
```
</details>

---

#### Level 3 — Production System Design: 16-Bit Educational Virtual CPU Emulator

##### Architectural Challenge:
Design an architectural software emulator in C++ for an educational **16-bit Accumulator-Based Microcontroller (EduCPU-16)**.
The ISA specification defines:
- **Registers:** 16-bit Program Counter (`PC`), 16-bit Accumulator (`AC`), 8-bit Condition Flags (`FLAGS: Z, N, C`).
- **Memory:** 64 Kilobytes of byte-addressable unified RAM ($65,536$ bytes).
- **Instruction Format (Fixed 16-bit words):**
  - High 4 bits: `Opcode` (Supports 16 distinct instructions: `HALT`, `LOAD`, `STORE`, `ADD`, `SUB`, `JMP`, `JZ`, `AND`).
  - Low 12 bits: `Address / Immediate Operand` (Direct memory addressing up to 4096 words).
- The emulator must implement a clean Fetch-Decode-Execute cycle loop, handle arithmetic overflow and zero flags, and gracefully halt.

<details>
<summary><strong>View Production Architectural Implementation</strong></summary>

```cpp
/**
 * EduCPU-16 Architectural Emulator
 * Implements an Accumulator-based 16-bit Stored-Program Computer
 */
#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>

class EduCPU16 {
public:
    // Opcode Enumeration (4-bit field: 0x0 to 0xF)
    enum Opcode : uint16_t {
        OP_HALT  = 0x0,
        OP_LOAD  = 0x1, // AC <- Memory[Addr]
        OP_STORE = 0x2, // Memory[Addr] <- AC
        OP_ADD   = 0x3, // AC <- AC + Memory[Addr]
        OP_SUB   = 0x4, // AC <- AC - Memory[Addr]
        OP_AND   = 0x5, // AC <- AC & Memory[Addr]
        OP_JMP   = 0x6, // PC <- Addr
        OP_JZ    = 0x7, // If Z == 1, PC <- Addr
        OP_LDI   = 0x8  // AC <- Immediate (Sign-extended 12-bit)
    };

    // Processor Status Flags
    struct Flags {
        bool Z{false}; // Zero Flag
        bool N{false}; // Negative Flag
        bool C{false}; // Carry Flag
    };

    EduCPU16() : memory(65536, 0), pc(0), ac(0), halted(false) {}

    void loadProgram(const std::vector<uint16_t>& binary, uint16_t startAddress = 0x0000) {
        for (size_t i = 0; i < binary.size(); ++i) {
            uint16_t addr = startAddress + (i * 2);
            // Big-Endian storage in byte memory
            memory[addr]     = static_cast<uint8_t>((binary[i] >> 8) & 0xFF);
            memory[addr + 1] = static_cast<uint8_t>(binary[i] & 0xFF);
        }
        pc = startAddress;
    }

    void run() {
        std::cout << ">>> EduCPU-16 Execution Engine Started at PC: 0x" 
                  << std::hex << std::setw(4) << std::setfill('0') << pc << std::endl;
        
        while (!halted) {
            step();
        }

        std::cout << ">>> Processor Halted. Final AC: 0x" << std::hex << ac 
                  << " (Dec: " << std::dec << static_cast<int16_t>(ac) << ")" << std::endl;
    }

    void step() {
        if (halted) return;

        // 1. FETCH PHASE
        uint16_t instruction = readWord(pc);
        uint16_t currentPc = pc;
        pc += 2; // Advance PC to next instruction word

        // 2. DECODE PHASE
        uint16_t opcodeRaw = (instruction >> 12) & 0x0F;
        uint16_t operand   = instruction & 0x0FFF;

        // 3. EXECUTE PHASE
        switch (opcodeRaw) {
            case OP_HALT:
                halted = true;
                break;

            case OP_LOAD: {
                ac = readWord(operand * 2);
                updateFlags(ac);
                break;
            }

            case OP_STORE: {
                writeWord(operand * 2, ac);
                break;
            }

            case OP_ADD: {
                uint16_t val = readWord(operand * 2);
                uint32_t result = static_cast<uint32_t>(ac) + static_cast<uint32_t>(val);
                flags.C = (result > 0xFFFF);
                ac = static_cast<uint16_t>(result & 0xFFFF);
                updateFlags(ac);
                break;
            }

            case OP_SUB: {
                uint16_t val = readWord(operand * 2);
                uint32_t result = static_cast<uint32_t>(ac) - static_cast<uint32_t>(val);
                flags.C = (ac >= val);
                ac = static_cast<uint16_t>(result & 0xFFFF);
                updateFlags(ac);
                break;
            }

            case OP_AND: {
                ac &= readWord(operand * 2);
                updateFlags(ac);
                break;
            }

            case OP_JMP:
                pc = operand * 2;
                break;

            case OP_JZ:
                if (flags.Z) {
                    pc = operand * 2;
                }
                break;

            case OP_LDI: {
                // Sign-extend 12-bit immediate to 16-bit
                if (operand & 0x0800) {
                    ac = operand | 0xF000;
                } else {
                    ac = operand;
                }
                updateFlags(ac);
                break;
            }

            default:
                std::cerr << "Illegal Opcode Trapped: 0x" << std::hex << opcodeRaw << std::endl;
                halted = true;
                break;
        }
    }

private:
    std::vector<uint8_t> memory;
    uint16_t pc;
    uint16_t ac;
    Flags flags;
    bool halted;

    uint16_t readWord(uint16_t addr) const {
        return (static_cast<uint16_t>(memory[addr]) << 8) | memory[addr + 1];
    }

    void writeWord(uint16_t addr, uint16_t val) {
        memory[addr]     = static_cast<uint8_t>((val >> 8) & 0xFF);
        memory[addr + 1] = static_cast<uint8_t>(val & 0xFF);
    }

    void updateFlags(uint16_t val) {
        flags.Z = (val == 0);
        flags.N = ((val & 0x8000) != 0);
    }
};

int main() {
    EduCPU16 cpu;

    // Sample Binary: Computes 10 + 25 - 5 = 30
    // Assembly:
    //   LDI 10        (0x800A)
    //   STORE [0x050] (0x2050)
    //   LDI 25        (0x8019)
    //   ADD [0x050]   (0x3050) -> AC = 35
    //   STORE [0x050] (0x2050)
    //   LDI 5         (0x8005)
    //   STORE [0x051] (0x2051)
    //   LOAD [0x050]  (0x1050) -> AC = 35
    //   SUB [0x051]   (0x4051) -> AC = 30
    //   HALT          (0x0000)
    std::vector<uint16_t> program = {
        0x800A, 0x2050, 0x8019, 0x3050, 0x2050,
        0x8005, 0x2051, 0x1050, 0x4051, 0x0000
    };

    cpu.loadProgram(program);
    cpu.run();

    return 0;
}
```

##### Architectural Verification:
- **Instruction Execution Fidelity:** Accurately mimics standard two-byte instruction fetching, Big-Endian memory serialization, opcode masking, and ALU flag generation ($Z, N, C$).
- **Software/Hardware Boundary:** Exposes the fundamental mechanism by which high-level arithmetic translates to hardware datapath micro-operations.
</details>

---

### 6. Reference Video Lecture
Review this university lecture exploring the foundations of computer architecture, the hardware-software abstraction boundary, and processor design principles:

{{ media:coa-intro-video }}
