# Unit 5 — Semiconductor Main Memory, Error Correction & Storage Architectures
## Lesson 2 — Hardware Error Detection & Correction: Hamming SEC-DED Architecture

### 1. Memory Fault Classes: Hard Physical Defects vs. Soft Errors

Semiconductor memory arrays operate at the atomic threshold of solid-state physics. A modern 64 GB DRAM module contains over **500 billion individual microscopic storage capacitors**, each holding a mere 20 to 30 femtofarads of electrical charge (equivalent to fewer than $150,000$ individual electrons). Under these nanoscale operating conditions, memory cells are vulnerable to two distinct categories of hardware failure:

| Fault Classification | Physical Origin & Etiology | Permanence & Reproducibility | Typical Physical Causes | Architectural Remedy |
| :--- | :--- | :--- | :--- | :--- |
| **Hard Failure** | Permanent physical damage to the silicon crystal lattice, dielectric oxide, or interconnect metallization. | **Permanent:** The damaged cell reliably produces an incorrect binary value on every subsequent access. | • Gate oxide dielectric breakdown.<br>• Electromigration of aluminum/copper traces.<br>• Manufacturing lithography defects.<br>• Voltage spike / electrostatic discharge (ESD). | Physical module replacement or hardware row/column remapping via laser-blown redundancy fuses. |
| **Soft Error** | Transient, non-destructive charge disturbance that flips the state of one or more bits without causing physical silicon damage. | **Transient:** The physical storage cell is completely undamaged; rewriting new data into the cell restores flawless normal operation! | • **Alpha Particle Emission:** Radioactive decay of trace uranium/thorium in chip packaging epoxy.<br>• **Cosmic Rays:** High-energy atmospheric neutrons colliding with silicon atoms, generating electron-hole pairs.<br>• **Power Supply Noise:** Voltage droop across power distribution networks. | **Error-Correcting Codes (ECC):** Hamming Single Error Correction & Double Error Detection (SEC-DED). |

#### The Terrestrial Cosmic Ray Threat
At sea level, secondary cosmic neutron flux is approximately $10\text{ to }20\text{ neutrons}/(\text{cm}^2 \cdot \text{hour})$. A single neutron collision within a silicon substrate can generate a localized charge ionization plume of $150\text{ fC}$—far exceeding the critical charge ($Q_{\text{crit}}$) required to flip a DRAM capacitor state! In a large datacenter cluster with $100,000$ servers containing terabytes of DRAM, soft errors occur every few minutes. Without on-chip Error Correcting Codes, financial transactions, database indices, and kernel pointers would suffer silent data corruption.

{{ media:coa-hamming-diagram }}

---

### 2. Mathematical Foundation of Error Correction: Code Distance & Check Bit Scaling

In 1950, Richard W. Hamming at Bell Laboratories formulated the mathematical foundations of algebraic error-detecting and error-correcting codes.

#### Hamming Distance ($d_{\text{min}}$)
The **Hamming Distance** between two binary words of equal length is the number of bit positions in which the two words differ:
- Distance between `0010` and `0011` is $d = 1$.
- Distance between `1010` and `0101` is $d = 4$.

For a code to detect and correct errors:
1. To **detect** up to $e$ bit errors, the minimum Hamming distance between any two valid codewords must satisfy:
   $$d_{\text{min}} \ge e + 1$$
   *(Example: Standard parity adds 1 bit, making $d_{\text{min}} = 2$; it can detect $e = 1$ single error, but cannot correct it).*
2. To **correct** up to $t$ bit errors, the minimum Hamming distance must satisfy:
   $$d_{\text{min}} \ge 2t + 1$$
   *(To correct $t = 1$ single bit error, the code must have $d_{\text{min}} \ge 3$).*
3. To achieve **Single Error Correction and Double Error Detection (SEC-DED)**, the code requires:
   $$d_{\text{min}} \ge 4$$

#### The Check Bit Scaling Constraint Inequality
Consider a memory system storing an $M$-bit data word. To protect this word against single-bit errors, the hardware generates and appends $K$ additional **Check Bits (Parity Bits)**, creating an $(M + K)$-bit codeword.

When reading the word back from memory:
- If no error occurred, the check circuitry must report a "Zero / No Error" condition ($1$ unique state).
- If a single bit error occurred, the error could have struck any of the $M$ data bits or any of the $K$ check bits ($M + K$ possible single-error locations).
- The total number of distinct informational states that the $K$ check bits must be capable of uniquely encoding is:
  $$\text{Total States Required} = (M + K) + 1$$

Since $K$ binary bits can represent at most $2^K$ unique states, the fundamental **Hamming Inequality** dictates:

$$2^K - 1 \ge M + K$$

##### Solving for Check Bit Overhead ($K$):
| Data Bits ($M$) | Inequality ($2^K - 1 \ge M + K$) | Minimum Check Bits ($K$) | Total Word Length ($M + K$) | Relative Storage Overhead |
| :---: | :---: | :---: | :---: | :---: |
| **4 bits** | $2^3 - 1 = 7 \ge 4 + 3 = 7$ | **$K = 3$** | 7 bits (Hamming 7,4) | $75.0\%$ |
| **8 bits** | $2^4 - 1 = 15 \ge 8 + 4 = 12$ | **$K = 4$** | 12 bits (Hamming 12,8) | $50.0\%$ |
| **16 bits** | $2^5 - 1 = 31 \ge 16 + 5 = 21$ | **$K = 5$** | 21 bits | $31.25\%$ |
| **32 bits** | $2^6 - 1 = 63 \ge 32 + 6 = 38$ | **$K = 6$** | 38 bits | $18.75\%$ |
| **64 bits** | $2^7 - 1 = 127 \ge 64 + 7 = 71$ | **$K = 7$** | 71 bits | **$10.9\%$** |

*(Notice how check bit overhead drops from $75\%$ for 4-bit nibbles down to only $10.9\%$ for 64-bit words, demonstrating the high efficiency of wide memory words).*

---

### 3. Hamming Code Architecture: Parity Matrices & Syndrome Decoding

#### Richard Hamming's Geometric Bit Placement Scheme
Hamming established an ingenious bit-positioning layout: **Assign the check bits ($P_i$) to bit positions that are integer powers of two ($1, 2, 4, 8, 16, \dots, 2^{K-1}$)**. All other positions are assigned to the actual data bits ($D_1, D_2, \dots, D_M$).

For an 8-bit data word ($M = 8$) protected by 4 check bits ($K = 4$), the 12-bit codeword layout is:

```
Bit Position:     1    2    3    4    5    6    7    8    9   10   11   12
Binary Position: 0001 0010 0011 0100 0101 0110 0111 1000 1001 1010 1011 1100
Assigned Entity:  P1   P2   D1   P4   D2   D3   D4   P8   D5   D6   D7   D8
```

#### Check Bit Coverage Equations (Even Parity / XOR)
Each check bit $P_i$ checks all bit positions whose binary index has a **1** in position $2^i$:
- **$P_1$ (Position $1 = 0001_2$):** Checks all positions with bit 0 set (`1, 3, 5, 7, 9, 11`):
  $$P_1 = D_1 \oplus D_2 \oplus D_4 \oplus D_5 \oplus D_7$$
- **$P_2$ (Position $2 = 0010_2$):** Checks all positions with bit 1 set (`2, 3, 6, 7, 10, 11`):
  $$P_2 = D_1 \oplus D_3 \oplus D_4 \oplus D_6 \oplus D_7$$
- **$P_4$ (Position $4 = 0100_2$):** Checks all positions with bit 2 set (`4, 5, 6, 7, 12`):
  $$P_4 = D_2 \oplus D_3 \oplus D_4 \oplus D_8$$
- **$P_8$ (Position $8 = 1000_2$):** Checks all positions with bit 3 set (`8, 9, 10, 11, 12`):
  $$P_8 = D_5 \oplus D_6 \oplus D_7 \oplus D_8$$

#### The Syndrome Word ($S$) & Hardware Error Correction
When the 12-bit word is read from memory, the check bits are recalculated from the retrieved data bits ($C_{\text{calc}} = \{C_8, C_4, C_2, C_1\}$).
The hardware then computes the **Syndrome Word ($S$)** via bitwise XOR with the stored check bits ($C_{\text{stored}} = \{P_8, P_4, P_2, P_1\}$):

$$S = C_{\text{calc}} \oplus C_{\text{stored}} = (S_8, S_4, S_2, S_1)$$

Where:
$$S_1 = P_1 \oplus D_1 \oplus D_2 \oplus D_4 \oplus D_5 \oplus D_7$$
$$S_2 = P_2 \oplus D_1 \oplus D_3 \oplus D_4 \oplus D_6 \oplus D_7$$
$$S_4 = P_4 \oplus D_2 \oplus D_3 \oplus D_4 \oplus D_8$$
$$S_8 = P_8 \oplus D_5 \oplus D_6 \oplus D_7 \oplus D_8$$

##### The Beauty of Hamming's Mapping:
- If $S = 0000_2 \implies$ **Zero errors!**
- If $S \ne 0000_2 \implies$ **The binary value of the syndrome word $S$ is the EXACT bit position of the corrupted bit!**
  - If $S = 0110_2 = 6_{10} \implies$ Bit 6 ($D_3$) is corrupted!
  - If $S = 1000_2 = 8_{10} \implies$ Bit 8 ($P_8$) is corrupted!
- **Automatic Correction:** A 4-to-16 line decoder decodes the integer value of $S$ and energizes an XOR gate attached to bit position $S$, inverting the corrupted bit back to its true value in sub-nanosecond hardware time!

---

### 4. Single Error Correction, Double Error Detection (SEC-DED) Architecture

A standard Hamming code has a minimum Hamming distance of $d_{\text{min}} = 3$. While it flawlessly corrects any single bit error ($t = 1$), it has a dangerous architectural blind spot: **Double Bit Errors**.
If two bits flip simultaneously (e.g., bits 3 and 5), the syndrome calculation will produce a non-zero integer (e.g., $3 \oplus 5 = 6$), causing the hardware to "correct" bit 6! The result is **Triple Bit Data Corruption** with zero notification to the CPU.

#### The SEC-DED Global Parity Extension
To prevent silent corruption from double errors, computer architects append one additional global parity bit: the **Overall Parity Bit ($P_{\text{global}}$)**:

```
+-----------------------------------------------------------------------------------------+
|                               SEC-DED CODEWORD STRUCTURE                                |
|                                                                                         |
|       +-------------------------------------------------------------+-----------------+ |
|       |               HAMMING CODEWORD (M + K BITS)                 |  GLOBAL PARITY  | |
|       |                                                             |    P_global     | |
|       +-------------------------------------------------------------+-----------------+ |
|       <-------------------------- d_min = 4 ------------------------------------------> |
+-----------------------------------------------------------------------------------------+
```

$P_{\text{global}}$ covers the entire $(M + K)$-bit codeword using even parity:
$$P_{\text{global}} = \bigoplus_{i=1}^{M+K} \text{Bit}_i$$

#### SEC-DED Hardware Decision Matrix
When reading a codeword from memory:

| Syndrome Value ($S$) | Overall Global Parity ($P_{\text{global}}$) | Hardware Diagnostic & Action Taken |
| :---: | :---: | :--- |
| **$S == 0$** | **Even (0)** | **No Error:** Data is completely valid and clean. |
| **$S \ne 0$** | **Odd (1)** | **Single Bit Error:** Exactly one bit flipped. The syndrome $S$ indicates its precise location. Invert Bit[$S$] (Corrected). Log correctable error. |
| **$S \ne 0$** | **Even (0)** | **Double Bit Error Detected (DED)!** Two bits flipped simultaneously. Data cannot be reconstructed. Memory controller asserts a **Non-Maskable Interrupt (NMI) / Machine Check Exception (MCE)**, halting the system to prevent database corruption! |
| **$S == 0$** | **Odd (1)** | **Global Parity Bit Error:** Only $P_{\text{global}}$ itself flipped. Data bits are completely valid. |

*(Standard enterprise server ECC memory universally implements 64-bit data + 8-bit SEC-DED check bits = 72-bit DIMM modules).*

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Step-by-Step Hamming(12,8) Generation & Correction Trace

##### Problem Statement
An 8-bit microprocessor writes the data byte:
$$\text{Data Word} = \text{0x4B} = 0100\_1011_2$$
Where $D_8 = 0, D_7 = 1, D_6 = 0, D_5 = 0, D_4 = 1, D_3 = 0, D_2 = 1, D_1 = 1$.

1. Calculate the 4 check bits ($P_1, P_2, P_4, P_8$) and assemble the full 12-bit transmitted codeword.
2. During DRAM retention, an atmospheric cosmic ray strikes **Bit 7 ($D_4$)**, flipping it from **1 to 0**.
3. Trace the recalculation of check bits ($C_1, C_2, C_4, C_8$), the generation of the syndrome word $S$, and demonstrate how hardware isolates and inverts the corrupted bit.

##### Step-by-Step Execution Trace

1. **Check Bit Generation:**
   - $P_1 = D_1 \oplus D_2 \oplus D_4 \oplus D_5 \oplus D_7 = 1 \oplus 1 \oplus 1 \oplus 0 \oplus 1 = 0$
   - $P_2 = D_1 \oplus D_3 \oplus D_4 \oplus D_6 \oplus D_7 = 1 \oplus 0 \oplus 1 \oplus 0 \oplus 1 = 1$
   - $P_4 = D_2 \oplus D_3 \oplus D_4 \oplus D_8 = 1 \oplus 0 \oplus 1 \oplus 0 = 0$
   - $P_8 = D_5 \oplus D_6 \oplus D_7 \oplus D_8 = 0 \oplus 0 \oplus 1 \oplus 0 = 1$

   Assembled 12-bit stored codeword:
   $$\begin{matrix}
   \text{Bit Position:} & 1 & 2 & 3 & 4 & 5 & 6 & 7 & 8 & 9 & 10 & 11 & 12 \\
   \text{Entity:} & P_1 & P_2 & D_1 & P_4 & D_2 & D_3 & D_4 & P_8 & D_5 & D_6 & D_7 & D_8 \\
   \text{Stored Value:} & \mathbf{0} & \mathbf{1} & 1 & \mathbf{0} & 1 & 0 & \mathbf{1} & \mathbf{1} & 0 & 0 & 1 & 0
   \end{matrix}$$

2. **Cosmic Ray Strike on Bit 7 ($D_4$ flips $1 \to 0$):**
   Retrieved Codeword from DRAM:
   $$\text{Bit 7 is now } \mathbf{0} \quad (\text{Word: } 0110\_10\mathbf{0}1\_0010)$$

3. **Syndrome Decoding:**
   - $C_1 = 1 \oplus 1 \oplus \mathbf{0} \oplus 0 \oplus 1 = 1 \implies S_1 = C_1 \oplus P_1 = 1 \oplus 0 = \mathbf{1}$
   - $C_2 = 1 \oplus 0 \oplus \mathbf{0} \oplus 0 \oplus 1 = 0 \implies S_2 = C_2 \oplus P_2 = 0 \oplus 1 = \mathbf{1}$
   - $C_4 = 1 \oplus 0 \oplus \mathbf{0} \oplus 0 = 1 \implies S_4 = C_4 \oplus P_4 = 1 \oplus 0 = \mathbf{1}$
   - $C_8 = 0 \oplus 0 \oplus 1 \oplus 0 = 1 \implies S_8 = C_8 \oplus P_8 = 1 \oplus 1 = \mathbf{0}$

   Assemble Syndrome Word:
   $$S = (S_8, S_4, S_2, S_1) = (0, 1, 1, 1)_2 = 7_{10}!$$
   **Hardware Conclusion:** The syndrome explicitly isolates **Bit 7** as the corrupted bit!
   Hardware inverts Bit 7: $0 \to 1$, restoring the original authenticated data byte `0x4B` with zero pipeline stall!

---

#### Level 2 — Scaffolded Bug-Fix: Silent Data Corruption in Pure SEC & SEC-DED Remedy

##### Defect Scenario
A medical imaging workstation runs software on an unbuffered non-ECC memory controller that was recently modified with a standard Hamming(7,4) Single Error Correction chip without global parity.
During a surgical imaging procedure, a double-bit memory fault occurs on codeword `1010011` (bits 1 and 2 flip). The pure SEC hardware decodes the syndrome, misinterprets the double fault as a single fault at bit 3, and flips bit 3!
The patient scan coordinates are silently corrupted, resulting in invalid robotic arm positioning!

##### Microarchitectural Diagnosis
A pure SEC code lacks the minimum Hamming distance ($d_{\text{min}} = 3$) required to distinguish between a single-bit error and a double-bit error. When two bits flip, their combined error vector aliases to a valid single-error syndrome, triggering false correction and creating **Triple Bit Corruption**.

<details>
<summary><b>View Architectural Solution & SEC-DED Global Parity Verifier</b></summary>

```c
// ============================================================================
// HARDWARE SIMULATION: SEC-DED ERROR DETECTION & CORRECTION UNIT
// ============================================================================
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

typedef enum {
    ECC_CLEAN,
    ECC_SINGLE_CORRECTED,
    ECC_DOUBLE_ERROR_DETECTED, // Uncorrectable!
    ECC_PARITY_ERROR
} ECCStatus;

typedef struct {
    uint8_t data;
    ECCStatus status;
} ECCResult;

// Evaluates 8-bit Data + 4-bit Hamming + 1-bit Global Parity (13-bit SEC-DED)
ECCResult decode_sec_ded_word(uint16_t codeword_13bit) {
    ECCResult result;
    
    // Extract bit entities
    uint8_t p1 = (codeword_13bit >> 0) & 1;
    uint8_t p2 = (codeword_13bit >> 1) & 1;
    uint8_t d1 = (codeword_13bit >> 2) & 1;
    uint8_t p4 = (codeword_13bit >> 3) & 1;
    uint8_t d2 = (codeword_13bit >> 4) & 1;
    uint8_t d3 = (codeword_13bit >> 5) & 1;
    uint8_t d4 = (codeword_13bit >> 6) & 1;
    uint8_t p8 = (codeword_13bit >> 7) & 1;
    uint8_t d5 = (codeword_13bit >> 8) & 1;
    uint8_t d6 = (codeword_13bit >> 9) & 1;
    uint8_t d7 = (codeword_13bit >> 10) & 1;
    uint8_t d8 = (codeword_13bit >> 11) & 1;
    uint8_t p_global = (codeword_13bit >> 12) & 1;

    // 1. Calculate Syndrome
    uint8_t s1 = p1 ^ d1 ^ d2 ^ d4 ^ d5 ^ d7;
    uint8_t s2 = p2 ^ d1 ^ d3 ^ d4 ^ d6 ^ d7;
    uint8_t s4 = p4 ^ d2 ^ d3 ^ d4 ^ d8;
    uint8_t s8 = p8 ^ d5 ^ d6 ^ d7 ^ d8;
    uint8_t syndrome = (s8 << 3) | (s4 << 2) | (s2 << 1) | s1;

    // 2. Calculate Total Overall Parity of entire 13-bit word
    uint8_t total_parity = 0;
    for (int i = 0; i < 13; i++) {
        total_parity ^= ((codeword_13bit >> i) & 1);
    }

    // 3. SEC-DED Decision Matrix
    if (syndrome == 0 && total_parity == 0) {
        result.status = ECC_CLEAN;
    } else if (syndrome != 0 && total_parity == 1) {
        // SINGLE BIT ERROR: Invert target bit
        printf("[ECC HARDWARE] Single-bit error detected at position %d! Auto-correcting.\n", syndrome);
        codeword_13bit ^= (1 << (syndrome - 1));
        result.status = ECC_SINGLE_CORRECTED;
    } else if (syndrome != 0 && total_parity == 0) {
        // DOUBLE BIT ERROR DETECTED!
        printf(">>> FATAL MACHINE CHECK EXCEPTION: DOUBLE-BIT ERROR DETECTED! <<<\n");
        printf(">>> Halting memory writeback to prevent patient data corruption! <<<\n");
        result.status = ECC_DOUBLE_ERROR_DETECTED;
    } else {
        result.status = ECC_PARITY_ERROR;
    }

    // Reconstruct 8-bit data byte
    result.data = ((codeword_13bit >> 2) & 1) |
                  (((codeword_13bit >> 4) & 1) << 1) |
                  (((codeword_13bit >> 5) & 1) << 2) |
                  (((codeword_13bit >> 6) & 1) << 3) |
                  (((codeword_13bit >> 8) & 1) << 4) |
                  (((codeword_13bit >> 9) & 1) << 5) |
                  (((codeword_13bit >> 10) & 1) << 6) |
                  (((codeword_13bit >> 11) & 1) << 7);

    return result;
}
```

</details>

---

#### Level 3 — High-Scale System Design: Full 64-bit SEC-DED ECC Memory Subsystem in C++

Design a complete, production-grade C++17 simulation of a 64-bit enterprise server ECC memory subsystem:
1. Generates 8 check bits ($K = 8$) for each 64-bit data word ($M = 64$), forming a 72-bit SEC-DED codeword.
2. Implements a hardware fault injection harness simulating single-bit cosmic ray flips and double-bit capacitor shorts.
3. Automatically corrects single-bit flips and safely triggers an architectural kernel panic on double-bit corruptions.

<details>
<summary><b>View Complete C++ 64-bit SEC-DED ECC Subsystem Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: 64-BIT SEC-DED ECC HARDWARE CONTROLLER
// Compile: g++ -std=c++17 -O3 ecc_subsystem.cpp -o ecc_subsystem
// ============================================================================

#include <iostream>
#include <vector>
#include <bitset>
#include <iomanip>
#include <cstdint>
#include <cassert>

class ECCController64 {
public:
    struct Codeword72 {
        uint64_t data_payload;
        uint8_t ecc_parity; // 7 Hamming check bits + 1 global parity bit
    };

    // Parity Generator Matrix: Generates 7 Hamming check bits + 1 global parity
    static Codeword72 encode(uint64_t data) {
        uint8_t c = 0;
        // Compute 7 check bits based on powers-of-two coverage
        for (int i = 0; i < 7; i++) {
            uint64_t mask = get_check_mask(i);
            uint64_t parity_bit = __builtin_parityll(data & mask);
            c |= (parity_bit << i);
        }

        // 8th bit is Global Parity across all 64 data bits + 7 check bits
        uint64_t all_data_parity = __builtin_parityll(data);
        uint64_t check_parity = __builtin_parity(c & 0x7F);
        uint8_t global_p = (all_data_parity ^ check_parity) & 1;
        c |= (global_p << 7);

        return Codeword72{data, c};
    }

    static bool decode_and_correct(Codeword72& cw, uint64_t& out_data) {
        uint8_t syndrome = 0;
        for (int i = 0; i < 7; i++) {
            uint64_t mask = get_check_mask(i);
            uint8_t calc_p = __builtin_parityll(cw.data_payload & mask);
            uint8_t stored_p = (cw.ecc_parity >> i) & 1;
            syndrome |= ((calc_p ^ stored_p) << i);
        }

        // Global parity check
        uint8_t total_parity = __builtin_parityll(cw.data_payload) ^ __builtin_parity(cw.ecc_parity);

        if (syndrome == 0 && total_parity == 0) {
            // Clean
            out_data = cw.data_payload;
            return true;
        } else if (syndrome != 0 && total_parity != 0) {
            // Single bit error in data
            std::cout << "  [ECC Controller] Single bit error detected! Syndrome = 0x" 
                      << std::hex << (int)syndrome << ". Correcting...\n";
            int bit_pos = get_data_bit_from_syndrome(syndrome);
            if (bit_pos >= 0 && bit_pos < 64) {
                cw.data_payload ^= (1ULL << bit_pos);
            }
            out_data = cw.data_payload;
            return true;
        } else if (syndrome != 0 && total_parity == 0) {
            // DOUBLE BIT ERROR: Uncorrectable!
            std::cerr << "  >>> [FATAL MCE] Uncorrectable Double-Bit Error Detected! "
                      << "Halting processor to prevent silent data corruption! <<<\n";
            return false;
        }

        out_data = cw.data_payload;
        return true;
    }

private:
    static uint64_t get_check_mask(int bit_idx) {
        // High-performance precomputed pseudo-random bit masks for 64-bit word
        static const uint64_t masks[7] = {
            0x5555555555555555ULL,
            0x6666666666666666ULL,
            0x7878787878787878ULL,
            0x7F807F807F807F80ULL,
            0x7FFF80007FFF8000ULL,
            0x7FFFFFFF80000000ULL,
            0x8000000000000000ULL
        };
        return masks[bit_idx];
    }

    static int get_data_bit_from_syndrome(uint8_t syndrome) {
        // Maps syndrome value to specific data bit (0-63)
        return (syndrome > 0 && syndrome <= 64) ? (syndrome - 1) : 0;
    }
};

int main() {
    std::cout << "=======================================================\n";
    std::cout << "     64-BIT SEC-DED ECC MEMORY CONTROLLER BENCHMARK    \n";
    std::cout << "=======================================================\n";

    uint64_t original_data = 0xDEADBEEFCAFEBABEULL;
    auto codeword = ECCController64::encode(original_data);

    std::cout << "Original Data : 0x" << std::hex << original_data << "\n";
    std::cout << "Generated ECC : 0x" << std::hex << (int)codeword.ecc_parity << "\n\n";

    // Test 1: Single bit error injection (Cosmic ray strike on Bit 12)
    std::cout << "Test 1: Injecting Single-Bit Fault on Data Bit 12...\n";
    codeword.data_payload ^= (1ULL << 12);
    uint64_t recovered_data = 0;
    bool ok = ECCController64::decode_and_correct(codeword, recovered_data);
    std::cout << "Recovered Data: 0x" << std::hex << recovered_data 
              << (recovered_data == original_data ? " (SUCCESS! MATCHES ORIGINAL)" : " (FAILED)") << "\n\n";

    // Test 2: Double bit error injection (Severe capacitor short)
    std::cout << "Test 2: Injecting Double-Bit Fault on Bits 4 and 25...\n";
    codeword.data_payload ^= (1ULL << 4);
    codeword.data_payload ^= (1ULL << 25);
    ok = ECCController64::decode_and_correct(codeword, recovered_data);
    std::cout << "Double-Bit Fault Handled Gracefully: " << (!ok ? "YES (MCE Triggered)" : "NO") << "\n";

    std::cout << "=======================================================\n";
    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:hamming-codes-video }}

In this video by Grant Sanderson (3Blue1Brown), the geometric intuition and linear algebraic structure of Hamming error-correcting codes are animated with unparalleled visual clarity.
