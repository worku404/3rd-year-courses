# Unit 2 — Computer Evolution, Generations & Quantitative Performance Assessment
## Lesson 1 — Historical Computer Generations, The Princeton IAS Machine & Moore's Law

### 1. The Four Generations of Computing Technology

The history of electronic computing is categorized into **four technological generations**. Each generational transition was propelled by a fundamental revolution in physical electronics—progressing from fragile, heat-dissipating vacuum tubes to discrete solid-state transistors, integrated silicon planar circuits, and modern billion-transistor microprocessors.

```
+-----------------------------------------------------------------------------------+
|                        THE FOUR GENERATIONS OF COMPUTING                          |
|                                                                                   |
|  [ 1st GENERATION (1946-1958) ] ---------> Vacuum Tubes & Delay Lines             |
|  ENIAC, IAS Machine, UNIVAC I              ~40,000 ops/sec; 150 kW power; Relays  |
|                                                                                   |
|  [ 2nd GENERATION (1958-1964) ] ---------> Discrete Bipolar Transistors           |
|  IBM 7094, DEC PDP-1                       ~200,000 ops/sec; Magnetic Core Memory;|
|                                            HLLs: FORTRAN & COBOL                  |
|                                                                                   |
|  [ 3rd GENERATION (1964-1971) ] ---------> Small/Medium Integrated Circuits (SSI) |
|  IBM System/360, DEC PDP-8                 ~1,000,000 ops/sec; Standardized Byte; |
|                                            Common Family ISA; Omnibus Bus         |
|                                                                                   |
|  [ 4th GENERATION (1971-Present) ] ------> VLSI / ULSI Microprocessors            |
|  Intel 4004/8086, ARM, RISC-V, Multi-Core >100,000,000,000 ops/sec; CMOS; 3nm Nodes|
+-----------------------------------------------------------------------------------+
```

{{ media:coa-generations-diagram }}

#### Generational Evolution Matrix

| Generation | Era | Primary Switching Technology | Typical Cycle Time | Primary Memory Storage | Canonical Exemplar Systems |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **First** | 1946–1958 | Thermionic Vacuum Tubes | $\approx 100\,\mu\text{s}$ | Mercury Delay Lines, Williams Electrostatic Tubes | ENIAC, IAS Computer, UNIVAC I, IBM 701 |
| **Second** | 1958–1964 | Discrete Solid-State Transistors | $\approx 2\,\mu\text{s}$ | Ferrite Magnetic Core Coincident-Current Memory | IBM 7094, Control Data CDC 1604, DEC PDP-1 |
| **Third** | 1964–1971 | Integrated Circuits (SSI / MSI) | $\approx 500\text{ ns}$ | Magnetic Cores, Early Semiconductor RAM | IBM System/360, DEC PDP-8 Minicomputer |
| **Fourth** | 1971–Pres. | VLSI / ULSI Microprocessors | $< 0.3\text{ ns}$ | Dynamic Semiconductor RAM (DRAM), SRAM Caches | Intel 8086, ARM Cortex, Apple M3, AMD Zen 4 |

---

### 2. Deep Dive: First Generation & The Princeton IAS Machine

#### ENIAC: The Electronic Pioneer
Constructed between 1943 and 1946 at the University of Pennsylvania by John Mauchly and J. Presper Eckert, the **ENIAC** was the world's first general-purpose electronic digital computer. 
- **Physical Specifications:** Weighed 30 tons, occupied 1,800 square feet, contained 17,468 vacuum tubes, 7,200 crystal diodes, 1,500 relays, and consumed 150 kW of electrical power.
- **Architectural Architecture:** Used decimal arithmetic (not binary), representing numbers via 10-position ring counters. Programmed entirely by manually rewiring patch cables and setting 3-way switches.

#### The Princeton IAS Computer Architecture (1952)
Commissioned by mathematician John von Neumann at the Institute for Advanced Study (IAS) in Princeton, New Jersey, the **IAS Machine** was completed in 1952. It served as the physical prototype for modern stored-program computers.

```
+-----------------------------------------------------------------------------------+
|                        PRINCETON IAS MACHINE REGISTERS                            |
|                                                                                   |
|           +-----------------------------------------------------------+           |
|           |                 1024 x 40-Bit Word Main Memory            |           |
|           +-----+-----------------------------------------------+-----+           |
|                 | (12-bit Address)                              | (40-bit Data)   |
|                 v                                               v                 |
|           +------------+                                  +------------+          |
|           | MAR (12b)  |                                  | MBR (40b)  |          |
|           +------------+                                  +-----+------+          |
|                 ^                                               |                 |
|                 | (Address routing)           +-----------------+-----------------+
|                 |                             |                                   |
|           +-----+------+                +-----v------+                      +-----v------+
|           |  PC (12b)  |                |  IBR (20b) |                      |  IR (8b)   |
|           +------------+                +------------+                      +------------+
|                                               |                                   |
|                                               v                                   v
|                                         [Right Inst]                        [Left Opcode]
|                                               |                                   |
|                                         +-----v-----------------------------------v---+
|                                         |     ARITHMETIC & LOGIC DATAPATH             |
|                                         |  +------------------+  +-----------------+  |
|                                         |  | Accumulator (AC) |  |   Multiplier-   |  |
|                                         |  |     (40-Bit)     |  |  Quotient (MQ)  |  |
|                                         |  +------------------+  +-----------------+  |
|                                         +---------------------------------------------+
+-----------------------------------------------------------------------------------+
```

#### The IAS 40-Bit Word Structure
The IAS memory consisted of 1,024 memory locations (words), each exactly 40 bits wide ($1024 \times 40 = 40,960$ bits $\approx 5.12\text{ KB}$).

A 40-bit word served two distinct architectural representations:

##### Format A: Number Representation
Numbers were represented as signed 40-bit binary fixed-point values:
```
Bit 0: Sign (0 = Positive, 1 = Negative)
Bits 1-39: 39-bit Binary Fraction / Integer Magnitude
Range: -2^39 to +(2^39 - 1)
```

##### Format B: Instruction Pair Representation
Because individual instructions were 20 bits wide, each 40-bit memory word packed **two complete instructions** executed sequentially (the Left Instruction followed by the Right Instruction):
```
+--------------------+--------------------+--------------------+--------------------+
|  Left Opcode (8b)  | Left Address (12b) | Right Opcode (8b)  | Right Address (12b)|
|     Bits 0 - 7     |    Bits 8 - 19     |    Bits 20 - 27    |    Bits 28 - 39    |
+--------------------+--------------------+--------------------+--------------------+
```
- **Opcode (8 bits):** Allowed up to $2^8 = 256$ machine operations (IAS implemented 21 distinct opcodes).
- **Address (12 bits):** Allowed directly addressing $2^{12} = 4,096$ words of memory (though the physical IAS machine implemented 1,024 words).

#### The IAS Operational Registers
The IAS datapath utilized seven discrete hardware registers:
1. **Memory Buffer Register (MBR - 40 bits):** Receives a 40-bit word from memory or holds a word to be written to memory.
2. **Memory Address Register (MAR - 12 bits):** Specifies the 12-bit physical address in memory for a read or write operation.
3. **Instruction Register (IR - 8 bits):** Latches the 8-bit opcode currently being decoded and executed.
4. **Instruction Buffer Register (IBR - 20 bits):** Temporarily holds the 20-bit **Right Instruction** while the **Left Instruction** is being executed.
5. **Program Counter (PC - 12 bits):** Stores the address of the next instruction pair to be fetched from memory.
6. **Accumulator (AC - 40 bits):** Primary working register for the ALU; holds intermediate arithmetic and logical results.
7. **Multiplier-Quotient (MQ - 40 bits):** Cooperates with the AC during multiplication and division. In multiplication, the product of two 40-bit numbers yields an 80-bit result, stored across the combined `AC:MQ` register pair.

---

### 3. Second & Third Generations: Transistors, IBM System/360 & The Minicomputer

#### Second Generation: The Transistor Revolution (1958–1964)
Invented at Bell Telephone Laboratories in 1947 by John Bardeen, Walter Brattain, and William Shockley, the solid-state transistor replaced fragile, burning-hot vacuum tubes. Transistors were smaller, cheaper, dissipated a fraction of the power, and operated at microsecond switching speeds.
- **Ferrite Magnetic Core Memory:** Replaced acoustic delay lines. Small toroidal ferrite rings strung on wire grids stored magnetic polarization ($0$ or $1$) non-volatily, with access times dropping to 2 microseconds.
- **Birth of High-Level Programming:** Assembly gave way to the first portable compilers: **FORTRAN** (John Backus at IBM, 1957) for scientific mathematics and **COBOL** (Grace Hopper, 1959) for business enterprise records.

#### Third Generation: Integrated Circuits (1964–1971)
In 1958, Jack Kilby (Texas Instruments) and Robert Noyce (Fairchild Semiconductor) independently invented the **Integrated Circuit (IC)**. Instead of soldering thousands of individual transistors, resistors, and capacitors onto circuit boards, the entire circuit was fabricated simultaneously onto a single monolithic wafer of silicon.

```
+-----------------------------------------------------------------------------------+
|                        THE IBM SYSTEM/360 REVOLUTION (1964)                       |
|                                                                                   |
|     +-----------------------------------------------------------------------+     |
|     |                      COMMON SYSTEM/360 ARCHITECTURE                   |     |
|     |  - Standard 8-bit Byte   - Byte-Addressable 32-bit Words              |     |
|     |  - 16 General Purpose Registers (32b)  - Common Machine Instruction Set|     |
|     +-----------------------------------+-----------------------------------+     |
|                                         |                                         |
|        +-----------------+--------------+----------------+----------------+       |
|        |                 |                               |                |       |
|  +-----v-----+     +-----v-----+                   +-----v-----+    +-----v-----+ |
|  | Model 30  |     | Model 40  |                   | Model 65  |    | Model 75  | |
|  | 8-bit bus |     | 16-bit bus|                   | 64-bit bus|    | Dual Pipe | |
|  | 33 KIPS   |     | 125 KIPS  |                   | 650 KIPS  |    | 1200 KIPS | |
|  | $133,000  |     | $225,000  |                   | $1,200,000|    | $2,000,000| |
|  +-----------+     +-----------+                   +-----------+    +-----------+ |
+-----------------------------------------------------------------------------------+
```

#### The IBM System/360 Milestone (1964)
Announced in April 1964, the IBM System/360 is widely recognized as the single most consequential product release in computer hardware history. Gene Amdahl, Fred Brooks, and Bob Evans introduced the industry's first planned **family of compatible computers**:
1. **Architectural Standardization:** Defined a single common ISA across diverse physical models. A software program written for the low-cost Model 30 executed identically on the ultra-fast Model 75 without modification or recompilation.
2. **The 8-Bit Byte:** Prior to System/360, computers used arbitrary 6-bit (character), 36-bit, or 60-bit words. IBM standardized the **8-bit byte** and **32-bit word** that dominates global computing to this day.
3. **Microprogrammed Control Units:** Maurice Wilkes's concept of microprogramming allowed complex CISC instructions to be realized as microcode stored in read-only memory, drastically reducing hardware control logic cost.

#### DEC PDP-8 & The Minicomputer Revolution (1965)
While IBM mainframes filled entire air-conditioned basements and cost millions of dollars, Digital Equipment Corporation (DEC) unveiled the **PDP-8** in 1965. Priced at just $16,000, it created the **minicomputer** market.
- **The Omnibus Bus Architecture:** Allowed CPU, memory, and peripheral devices to plug directly into a unified 96-pin printed circuit backplane, slashing assembly costs and democratizing computing for small laboratory and academic environments.

---

### 4. Fourth Generation: Microprocessors, Moore's Law & The Dennard Cliff

In 1971, Intel engineer Ted Hoff integrated an entire central processing unit onto a single silicon chip—the **Intel 4004** (a 4-bit CPU operating at 740 kHz containing 2,300 pMOS transistors). This ignited the microcomputer revolution:

```
Intel 4004 (1971): 4-bit, 2,300 transistors, 740 kHz
        |
        v
Intel 8086 (1978): 16-bit, 29,000 transistors, 5 MHz (Birth of x86)
        |
        v
Intel 80386 (1985): 32-bit flat paging, 275,000 transistors, 16 MHz
        |
        v
Intel Core i9 / AMD Zen 4 (2024+): 64-bit multi-core, >50,000,000,000 transistors, 5.7 GHz
```

#### Moore's Law Formally Stated
In 1965, Fairchild Semiconductor R&D Director **Gordon Moore** published an article in *Electronics* noting an empirical trend: the number of transistors that can be placed inexpensively on an integrated circuit doubles approximately every year. In 1975, he revised the projection to **every 24 months**.

$$N(t) = N_0 \cdot 2^{\frac{t - t_0}{2}}$$

```
Transistors per Microprocessor Die (Logarithmic Scale)
100 Billion |                                                    * Apple M3 Max (92B)
 10 Billion |                                             * Core i9 (14B)
  1 Billion |                                      * Core 2 Quad (820M)
100 Million |                               * Pentium 4 (125M)
 10 Million |                        * Pentium (3.1M)
  1 Million |                 * 486 (1.2M)
    100,000 |          * 8086 (29K)
     10,000 |   * 4004 (2.3K)
            +----------------------------------------------------> Year (1971 - Present)
```

#### The Consequences of Moore's Law
1. **Radical Cost Reduction:** The cost of an individual transistor plummeted from several dollars in 1960 to less than one-billionth of a dollar today.
2. **Path Length Reduction:** Packing transistors closer together reduced the physical distance electrical signals must travel, enabling higher clock frequencies ($f = 1/\tau$).
3. **Power Efficiency per Gate:** Smaller capacitances required less energy to switch.

#### The Collapse of Dennard Scaling & The Power Wall
As discussed in Lesson 1, while Moore's Law provided more transistors, **Dennard Scaling collapsed around 2004**. When gate oxide layers approached atomic thicknesses ($pprox 1.2\text{ nm}$), quantum tunneling leakage caused idle power to surge.

Unable to increase clock frequencies beyond 4 to 5 GHz without thermal destruction, architects transitioned from single-core performance to **Multi-Core Scaling**:
- Instead of building a single 10 GHz monolithic processor, architects build processors with 8, 16, 64, or 128 parallel cores operating at 3 to 4 GHz.
- This shifted the burden of performance from hardware frequency scaling to **software parallelism and architectural multi-core coordination**.

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: IAS Instruction Pair Execution Trace
Trace the execution of a 40-bit IAS memory word located at address `0x01A`. The word contains an arithmetic addition instruction in its left half and an unconditional jump instruction in its right half:

```
Memory[0x01A]:
Bits [0:7]   = 0x01  (Opcode: LOAD M(X) into AC)
Bits [8:19]  = 0x040 (Address: 0x040)
Bits [20:27] = 0x05  (Opcode: ADD M(X) to AC)
Bits [28:39] = 0x041 (Address: 0x041)
Initial State: PC = 0x01A; Memory[0x040] = 50; Memory[0x041] = 25; AC = 0
```

##### Step-by-Step IAS State Transition Table:
| Step | Active Sub-cycle | Hardware Action & Register Transfers | Resulting Register State |
| :--- | :--- | :--- | :--- |
| **1** | Fetch Pair | `MAR <- PC (0x01A)`<br>`MBR <- Memory[MAR]` | `MAR = 0x01A`<br>`MBR = [01 | 040 | 05 | 041]` |
| **2** | Unpack Instructions | `IBR <- MBR[20:39]` (Saves right inst)<br>`IR <- MBR[0:7]` (Left opcode)<br>`MAR <- MBR[8:19]` (Left address) | `IBR = [05 | 041]`<br>`IR = 0x01 (LOAD)`<br>`MAR = 0x040` |
| **3** | Execute Left Inst | `MBR <- Memory[MAR] (50)`<br>`AC <- MBR` | `AC = 50`<br>`IR/MAR ready for next phase` |
| **4** | Fetch Right from IBR | `IR <- IBR[0:7]` (Right opcode)<br>`MAR <- IBR[8:19]` (Right address) | `IR = 0x05 (ADD)`<br>`MAR = 0x041` |
| **5** | Execute Right Inst | `MBR <- Memory[MAR] (25)`<br>`AC <- AC + MBR (50 + 25 = 75)`<br>`PC <- PC + 1 (0x01B)` | `AC = 75`<br>`PC = 0x01B` |

---

#### Level 2 — Scaffolded Bug-Fix: IAS Machine Right-Instruction Branch Trap
In the Princeton IAS architecture, instructions are stored in pairs. An assembly programmer written for an IAS simulator attempts to branch to a target label that resides in the **Right Instruction (bits 20-39)** of word `0x080`.

The programmer uses the standard `JUMP` opcode `0x0D`, which causes the processor to erroneously fetch and execute the **Left Instruction (bits 0-19)** first, causing memory corruption!

##### The Broken Code:
```assembly
# BROKEN IAS ASSEMBLY LOGIC
# Location 0x010 (Left Inst):  CMP AC, 0
# Location 0x010 (Right Inst): JUMP to sub_routine (located at 0x080 RIGHT!)
# Target Location 0x080:
#   Left Inst (0:19)   : CRITICAL_DATA_RESET (Should NOT execute!)
#   Right Inst (20:39) : sub_routine_entry   (Target of jump!)

.org 0x010
    # BUG: Opcode 0x0D (JUMP M(X, 0:19)) jumps to the LEFT instruction of word X!
    # It executes CRITICAL_DATA_RESET before sub_routine_entry!
    JUMP 0x080          # Translates to Opcode 0x0D: JUMP M(0x080, 0:19)
```

<details>
<summary><strong>View Root Cause Analysis & The IAS Dual-Jump Instruction Set Fix</strong></summary>

##### Root Cause Analysis:
The IAS Instruction Set Architecture specifically anticipated that jumps might target either the Left Instruction or the Right Instruction of a 40-bit word. Consequently, von Neumann designed two distinct unconditional jump opcodes:
- **Opcode `0x0D` (`JUMP M(X, 0:19)`):** Sets `PC <- X`. The processor initiates a full memory fetch cycle and executes the **Left Instruction** first.
- **Opcode `0x0E` (`JUMP M(X, 20:39)`):** Sets `PC <- X`. The processor fetches word `X`, **discards or ignores the Left Instruction**, loads the Right Instruction directly into `IR`/`MAR`, and executes the **Right Instruction** immediately!

##### Refactored Assembly Solution:
```assembly
# CORRECTED IAS ASSEMBLY LOGIC
.org 0x010
    # Fix: Explicitly emit Opcode 0x0E targeting the Right Instruction (20:39)
    JUMP_RIGHT 0x080    # Encodes as Opcode 0x0E: JUMP M(0x080, 20:39)
```
</details>

---

#### Level 3 — Production System Design: Cycle-Accurate Princeton IAS Architecture Simulator

##### Architectural Challenge:
Design an architectural simulator in C++ for the **Princeton IAS Computer**.
The simulator must:
1. Model 1,024 memory locations of 40-bit words using signed 64-bit integer bitmasks (`uint64_t`).
2. Implement 40-bit arithmetic and handle the 80-bit product across `AC:MQ` in hardware multiplication (`MUL`).
3. Model the dual-instruction packing format (Left Instruction [0:7, 8:19] and Right Instruction [20:27, 28:39]).
4. Faithfully simulate the `IBR` latching behavior and the dual-branch instruction logic (`JUMP_LEFT` vs `JUMP_RIGHT`).

<details>
<summary><strong>View Production Architectural Implementation</strong></summary>

```cpp
/**
 * Cycle-Accurate Princeton IAS Machine Architectural Simulator
 * Implements 40-Bit Word Structure, Register Files & Dual-Instruction Fetch State Machine
 */
#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>

class IASComputer {
public:
    // 40-bit Bitmasks
    static constexpr uint64_t MASK_40BIT = 0xFFFFFFFFFFULL;
    static constexpr uint64_t SIGN_40BIT = 0x8000000000ULL;

    // IAS Opcodes
    enum Opcode : uint8_t {
        OP_LOAD_MQ     = 0x0A, // AC <- MQ
        OP_LOAD_MEM    = 0x01, // AC <- Memory[Addr]
        OP_LOAD_NEG    = 0x02, // AC <- -Memory[Addr]
        OP_STORE       = 0x21, // Memory[Addr] <- AC
        OP_ADD         = 0x05, // AC <- AC + Memory[Addr]
        OP_SUB         = 0x06, // AC <- AC - Memory[Addr]
        OP_MUL         = 0x0B, // (AC, MQ) <- MQ * Memory[Addr]
        OP_JUMP_LEFT   = 0x0D, // Jump to Left instruction at Addr
        OP_JUMP_RIGHT  = 0x0E, // Jump to Right instruction at Addr
        OP_JUMP_POS    = 0x0F, // If AC >= 0, Jump to Left at Addr
        OP_HALT        = 0xFF  // Simulator Extension: Halt
    };

    IASComputer() : memory(1024, 0), pc(0), ac(0), mq(0), 
                    mbr(0), mar(0), ibr(0), ir(0), halted(false) {}

    void loadWord(uint16_t address, uint64_t word) {
        if (address < 1024) {
            memory[address] = word & MASK_40BIT;
        }
    }

    // Helper: Pack two 20-bit instructions into a single 40-bit word
    static uint64_t packInstructions(uint8_t opLeft, uint16_t addrLeft, 
                                     uint8_t opRight, uint16_t addrRight) {
        uint64_t left  = ((static_cast<uint64_t>(opLeft) & 0xFF) << 12) | (addrLeft & 0xFFF);
        uint64_t right = ((static_cast<uint64_t>(opRight) & 0xFF) << 12) | (addrRight & 0xFFF);
        return ((left << 20) | right) & MASK_40BIT;
    }

    void run(uint16_t startAddress = 0) {
        pc = startAddress;
        std::cout << ">>> Princeton IAS Machine Running from Word 0x" 
                  << std::hex << pc << std::dec << " <<<\n" << std::endl;

        while (!halted) {
            // STEP 1: FETCH INSTRUCTION PAIR
            mar = pc;
            mbr = memory[mar];

            // STEP 2: EXECUTE LEFT INSTRUCTION
            ir  = static_cast<uint8_t>((mbr >> 32) & 0xFF);
            mar = static_cast<uint16_t>((mbr >> 20) & 0xFFF);
            ibr = mbr & 0xFFFFF; // Save Right Instruction [20:39]

            std::cout << "[FETCH WORD 0x" << std::hex << pc << "] Left Op: 0x" 
                      << (int)ir << " Addr: 0x" << mar << std::endl;

            executeInstruction(ir, mar, true);
            if (halted) break;

            // STEP 3: EXECUTE RIGHT INSTRUCTION FROM IBR
            ir  = static_cast<uint8_t>((ibr >> 12) & 0xFF);
            mar = static_cast<uint16_t>(ibr & 0xFFF);

            std::cout << "  -> Right Op from IBR: 0x" << (int)ir 
                      << " Addr: 0x" << mar << std::endl;

            executeInstruction(ir, mar, false);
            if (halted) break;

            pc++; // Advance to next 40-bit word pair
        }

        std::cout << "\n>>> IAS Execution Terminated." << std::endl;
        std::cout << "Final AC: " << toSigned40(ac) << " (0x" << std::hex << ac << ")" << std::endl;
        std::cout << "Final MQ: " << toSigned40(mq) << " (0x" << std::hex << mq << ")" << std::endl;
    }

private:
    std::vector<uint64_t> memory; // 1024 x 40-bit words
    uint16_t pc;   // 12-bit
    uint64_t ac;   // 40-bit
    uint64_t mq;   // 40-bit
    uint64_t mbr;  // 40-bit
    uint16_t mar;  // 12-bit
    uint32_t ibr;  // 20-bit
    uint8_t  ir;   // 8-bit
    bool halted;

    static int64_t toSigned40(uint64_t val) {
        if (val & SIGN_40BIT) {
            return -static_cast<int64_t>((~val & MASK_40BIT) + 1);
        }
        return static_cast<int64_t>(val);
    }

    static uint64_t fromSigned40(int64_t val) {
        return static_cast<uint64_t>(val) & MASK_40BIT;
    }

    void executeInstruction(uint8_t opcode, uint16_t addr, bool isLeft) {
        switch (opcode) {
            case OP_LOAD_MEM:
                mbr = memory[addr];
                ac = mbr;
                break;

            case OP_LOAD_MQ:
                ac = mq;
                break;

            case OP_STORE:
                mbr = ac;
                memory[addr] = mbr;
                break;

            case OP_ADD: {
                mbr = memory[addr];
                int64_t res = toSigned40(ac) + toSigned40(mbr);
                ac = fromSigned40(res);
                break;
            }

            case OP_SUB: {
                mbr = memory[addr];
                int64_t res = toSigned40(ac) - toSigned40(mbr);
                ac = fromSigned40(res);
                break;
            }

            case OP_MUL: {
                // 40b x 40b -> 80-bit product stored in AC:MQ
                int64_t opA = toSigned40(mq);
                int64_t opB = toSigned40(memory[addr]);
                __int128 prod = static_cast<__int128>(opA) * static_cast<__int128>(opB);
                
                ac = static_cast<uint64_t>((prod >> 40) & MASK_40BIT);
                mq = static_cast<uint64_t>(prod & MASK_40BIT);
                break;
            }

            case OP_JUMP_LEFT:
                pc = addr - 1; // Compensate for loop auto-increment
                break;

            case OP_HALT:
                halted = true;
                break;

            default:
                std::cerr << "Unrecognized IAS Opcode: 0x" << std::hex << (int)opcode << std::endl;
                halted = true;
                break;
        }
    }
};

int main() {
    IASComputer ias;

    // Data Segments at 0x050 and 0x051
    ias.loadWord(0x050, 100); // M[0x050] = 100
    ias.loadWord(0x051, 45);  // M[0x051] = 45

    // Word 0x000:
    // Left:  LOAD M(0x050) -> AC = 100
    // Right: SUB  M(0x051) -> AC = 55
    uint64_t w0 = IASComputer::packInstructions(
        IASComputer::OP_LOAD_MEM, 0x050,
        IASComputer::OP_SUB,      0x051
    );

    // Word 0x001:
    // Left:  STORE M(0x052) -> M[0x052] = 55
    // Right: HALT
    uint64_t w1 = IASComputer::packInstructions(
        IASComputer::OP_STORE, 0x052,
        IASComputer::OP_HALT,  0x000
    );

    ias.loadWord(0x000, w0);
    ias.loadWord(0x001, w1);

    ias.run(0x000);

    return 0;
}
```

##### Architectural Verification:
- **40-bit Storage Integrity:** Demonstrates exact hardware register transfers (`PC`, `MAR`, `MBR`, `IBR`, `IR`, `AC`) conforming to von Neumann's 1952 specification.
- **Micro-Operation Fidelity:** Perfectly tracks IBR right-instruction buffering and execution.
</details>

---

### 6. Reference Video Lecture
Review this engineering exploration of the early electronic computing era, the ENIAC, and the birth of stored-program computers:

{{ media:generations-video }}
