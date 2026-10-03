# Unit 5 — Semiconductor Main Memory, Error Correction & Storage Architectures
## Lesson 1 — Semiconductor Memory Technologies, DRAM Cell Kinetics & Chip Organization

### 1. Semiconductor Memory Cell Fundamentals: SRAM (6T) vs. DRAM (1T-1C)

At the lowest physical level of digital computing, all semiconductor memory systems are composed of microscopic electrical circuits designated as **Memory Cells**. Every semiconductor memory cell exhibits three essential operational characteristics:
1. It possesses two stable (or semi-stable) electrical states representing binary **1** and binary **0**.
2. It can be written into (at least once) by applying an electrical excitation signal to set its state.
3. It can be sensed (read) to determine its internal electrical state without permanently corrupting the stored value (or with automatic hardware restoration).

The two dominant semiconductor random-access memory technologies are **Static RAM (SRAM)** and **Dynamic RAM (DRAM)**.

```
+-----------------------------------------------------------------------------------------+
|                         SRAM (6T) VS. DRAM (1T-1C) CELL TOPOLOGY                        |
|                                                                                         |
|       [ STATIC RAM (SRAM) - 6T CELL ]             [ DYNAMIC RAM (DRAM) - 1T-1C CELL ]   |
|                                                                                         |
|                  V_DD                                                                   |
|                   |                                                WORD LINE            |
|              +----+----+                                              |                 |
|              |         |                                              v                 |
|           [P-MOS]   [P-MOS]                                      +---------+            |
|              |    X    |                          BIT LINE <==== | PASS-TR | ===+       |
|              +----+----+                                         +---------+    |       |
|              |    |    |                                                        |       |
|           [N-MOS] | [N-MOS]                                                    === C    |
|              |    |    |                                                     (Storage)  |
|             GND  GND  GND                                                       |       |
|              |         |                                                       GND      |
|    BL <---[PASS]     [PASS]---> BL#                                                     |
|              ^         ^                          • Exactly 1 transistor + 1 capacitor  |
|              |         |                          • Sub-micron trench/stack capacitor   |
|              +----+----+                          • Charge leaks in milliseconds!       |
|                   |                               • Destructive Read: Requires writeback|
|               WORD LINE                           • Extreme density: Billions of cells  |
+-----------------------------------------------------------------------------------------+
```

#### 1. Static RAM (SRAM) Microarchitecture
- **Cell Structure:** Consists of **six CMOS transistors (6T)**. Four transistors form a cross-coupled pair of CMOS inverters ($M_1 - M_4$) operating as a bistable multivibrator (flip-flop). Two additional n-channel transistors ($M_5, M_6$) serve as access pass-gates gated by the horizontal **Word Line**.
- **State Retention:** The feedback loop continuously regenerates the electrical voltages ($V_{DD} \approx 1.0\text{ V}$ for high, $0\text{ V}$ for low). As long as DC power is supplied, the stored bit remains rock-solid without degrading.
- **Read Kinetics:** When the Word Line is pulled high, pass-gates $M_5$ and $M_6$ connect the internal nodes to the complementary vertical **Bit Lines** (`BL` and `BL#`). Differential sense amplifiers detect the minute voltage difference ($100\text{ to }200\text{ mV}$) in sub-nanosecond intervals. The read operation is **non-destructive**.
- **Trade-Offs:** Ultra-fast ($0.5\text{ to }2.0\text{ ns}$ access time); however, six transistors require substantial silicon die real estate, resulting in low storage density and exorbitant cost per bit. SRAM is deployed exclusively where access latency is paramount: CPU register files, L1, L2, and L3 caches.

#### 2. Dynamic RAM (DRAM) Microarchitecture
- **Cell Structure:** Engineered around an ultra-minimalist topology consisting of **exactly one access transistor and one microscopic capacitor (1T-1C)**, invented by Robert Dennard at IBM in 1968.
- **State Retention:** A binary **1** is represented by a charged capacitor ($Q = C \cdot V_{DD}$, with capacitance $C \approx 25\text{ to }35\text{ femtofarads}$); a binary **0** is represented by an uncharged capacitor ($Q \approx 0$).
- **Destructive Read Mechanism:** When the Word Line activates the pass transistor, the charge stored on the tiny capacitor discharges onto the vertical Bit Line. Because the capacitance of the Bit Line itself ($C_{\text{bitline}} \approx 1\text{ pF}$) is significantly larger than the cell capacitor, charge sharing alters the Bit Line voltage by only tens of millivolts:
  $$\Delta V = \frac{C_{\text{cell}}}{C_{\text{cell}} + C_{\text{bitline}}} \cdot (V_{\text{cell}} - V_{\text{precharge}})$$
  Sensitive differential **Sense Amplifiers** detect this tiny swing, amplify it to full rail voltage ($0\text{ V}$ or $V_{DD}$), and latch the data word. Crucially, this read process **completely empties the cell capacitor**! The sense amplifier must immediately drive the amplified voltage back into the cell before closing the row (**Precharge & Restore Phase**).
- **Trade-Offs:** Dense, inexpensive, low power per idle bit; however, high access latency ($40\text{ to }80\text{ ns}$) and continuous maintenance overhead due to charge leakage.

{{ media:coa-semiconductor-diagram }}

---

### 2. DRAM Refreshing Kinetics: Distributed vs. Burst Refreshing

Because the dielectric oxide layer insulating the 1T-1C storage capacitor is only a few nanometers thick, charge continuously leaks away through reverse-bias junction leakage and sub-threshold conduction. Within tens of milliseconds, a stored binary **1** will degrade into a binary **0**.

To prevent catastrophic data loss, every dynamic semiconductor memory chip contains automated internal **Refresh Circuitry**. Refreshing is accomplished by executing a dummy read on each row: activating the Word Line causes the Sense Amplifiers to latch the remaining charge, amplify it, and rewrite the original full-rail voltage back into all capacitors along that row.

```
+-----------------------------------------------------------------------------------------+
|                             DRAM REFRESHING MECHANISMS                                  |
|                                                                                         |
|       [ BURST REFRESHING ]                                                              |
|       Normal Operations       All Rows Refreshed Consecutively     Normal Operations    |
|       [ CPU Access ]          [ BUS SUSPENDED / LOCKED FOR REFRESH ] [ CPU Access ]     |
|   ----+---------------------+---------------------------------------+-----------------  |
|       |<--- 63.5 ms ------->|<------------- 0.5 ms ---------------->|                   |
|                                                                                         |
|       [ DISTRIBUTED REFRESHING ] (Standard in Modern Memory Controllers)                |
|       Op   Ref   Op   Ref   Op   Ref   Op   Ref   Op   Ref   Op   Ref   Op   Ref      |
|   ----+----+-----+----+-----+----+-----+----+-----+----+-----+----+-----+----+----+---  |
|       |    |     |    |     |    |     |    |     |    |     |    |     |    |          |
|       |<-- t_REFI (7.8 us)->|                                                           |
+-----------------------------------------------------------------------------------------+
```

#### The Quantitative Refresh Model
- Standard DDR4/DDR5 JEDEC specifications mandate a maximum **Retention Window** of:
  $$t_{\text{ref}} = 64\text{ milliseconds} \quad (\text{or } 32\text{ ms at junction temperatures } > 85^\circ\text{C})$$
- For a DRAM chip containing $R = 8,192\text{ rows}$ ($2^{13}$ rows):
  1. **Burst Refresh:** The memory controller suspends all CPU access, rapidly cycling through all 8,192 rows sequentially. During this interval ($t_{\text{burst}} \approx 8192 \times 50\text{ ns} \approx 410\ \mu\text{s}$), the memory bus is completely blocked, introducing severe latency jitter into real-time operating systems.
  2. **Distributed Refresh:** Refresh cycles are evenly spaced across the 64 ms window. The refresh interval ($t_{\text{REFI}}$) is calculated as:
     $$t_{\text{REFI}} = \frac{t_{\text{ref}}}{R} = \frac{64\text{ ms}}{8,192\text{ rows}} = 7.8125\ \mu\text{s}$$
     Every $7.8\ \mu\text{s}$, the memory controller issues a `REFRESH` (`REF`) command, refreshing one row in approximately $t_{\text{RFC}} = 50\text{ ns}$, leaving $99.3\%$ of the memory bus bandwidth available for user CPU accesses.

---

### 3. ROM Taxonomies & Evolution: Mask ROM, PROM, EPROM, EEPROM & Flash Memory

Non-volatile semiconductor memory retains its stored binary data permanently, even when DC electrical power is removed. Non-volatile storage is essential for holding system bootstrap firmware (BIOS/UEFI), microcode control stores, embedded firmware, and persistent storage arrays.

| Memory Type | Erasability Mechanism | Write / Programming Mechanism | Volatility | Typical Latency & Application |
| :--- | :--- | :--- | :--- | :--- |
| **Mask ROM** | Non-erasable (Hardwired). | Photolithographic mask at factory fabrication. | Strictly Non-Volatile | High setup cost; economic only for millions of units (embedded ASICs, toy ROMs). |
| **PROM** (Programmable ROM)| Non-erasable (One-Time Programmable / OTP). | High-voltage electrical pulses blow fusible nichrome/polysilicon links. | Strictly Non-Volatile | Prototyping; programmed once in field with specialized PROM burner. |
| **EPROM** (Erasable PROM) | Optical: Expose chip die to intense **Ultraviolet (UV) Light** via quartz window for 20-30 minutes. | Electrical: Hot-carrier injection traps electrons on Floating Gates. | Strictly Non-Volatile | Slower erase; requires physical removal of chip from board. Historical (1980s-90s). |
| **EEPROM** (Electrically Erasable PROM)| Electrical: Byte-by-byte in-circuit erasure using Fowler-Nordheim quantum tunneling. | Electrical: High internal charge pump voltage pulses. | Strictly Non-Volatile | Read access $\sim 50\text{ ns}$; write latency $\sim 5\text{ ms}$/byte. System configuration NVRAM. |
| **Flash Memory** (NAND / NOR) | Electrical: Erased in entire **Blocks** ($128\text{ KB to }4\text{ MB}$) in milliseconds. | Electrical: Page-level programming ($4\text{ KB to }16\text{ KB}$). | Strictly Non-Volatile | Sits between RAM and secondary storage. Underpins all SSDs, USB drives, and smartphones. |

#### NOR vs. NAND Flash Architectural Divergence
1. **NOR Flash:** Memory cells are connected in parallel to bit lines (resembling a NOR gate). Provides true **byte-level random read access** ($O(1)$ constant time), permitting the CPU to execute code directly from flash without copying to RAM (**Execute-in-Place / XIP**). Used for UEFI BIOS chips.
2. **NAND Flash:** Memory cells are connected in long series strings (resembling a NAND gate). Eliminates individual bit line contacts, reducing cell silicon area by $60\%$. However, reading and writing must occur in multi-kilobyte **Pages**, and erasing requires multi-megabyte **Blocks**. Forms the storage medium of all Solid-State Drives (SSDs).

---

### 4. DRAM Internal Architecture & Address Multiplexing: 16Mb (4M x 4) Case Study

To understand how billions of memory cells are physically addressed on a printed circuit board, consider the canonical architectural organization of a **16 Megabit DRAM chip configured as $4\text{M} \times 4\text{ bits}$** (Stallings textbook / AASTU SE curriculum standard):

```
+-----------------------------------------------------------------------------------------+
|                  16 Mb DRAM (4M x 4) INTERNAL CHIP ORGANIZATION                         |
|                                                                                         |
|        ADDRESS BUS: 11 PINS (A0 - A10)                                                  |
|             |                                                                           |
|             v                                                                           |
|     +---------------+                                                                   |
|     | ADDRESS BUFFER| <--- RAS# (Row Address Strobe Latch)                             |
|     |  MULTIPLEXER  | <--- CAS# (Column Address Strobe Latch)                          |
|     +-------+-------+                                                                   |
|             |                                                                           |
|             +-------------------------+                                                 |
|             | 11 bits                 | 11 bits                                         |
|             v                         v                                                 |
|     +---------------+         +---------------+                                         |
|     |  ROW DECODER  |         | COLUMN DECODER|                                         |
|     | (11-to-2048)  |         | (11-to-2048)  |                                         |
|     +-------+-------+         +-------+-------+                                         |
|             | 2,048 Word Lines        | Selects 4 bits                                  |
|             v                         v                                                 |
|     +=========================================+                                         |
|     |   4 MEMORY ARRAYS / PLANES (4 x 4 Mb)   |                                         |
|     |   Each plane = 2,048 Rows x 2,048 Cols  |                                         |
|     |   Array Size: 4,194,304 cells / plane   |                                         |
|     +=========================================+                                         |
|                         |                                                               |
|                         v                                                               |
|             +-----------------------+                                                   |
|             | 2,048 SENSE AMPS /    |                                                   |
|             | ROW BUFFER LATCHES    |                                                   |
|             +-----------+-----------+                                                   |
|                         |                                                               |
|                         v                                                               |
|             +-----------------------+                                                   |
|             | 4-BIT DATA BUFFER (I/O)| <===> DATA BUS PINS: D0, D1, D2, D3             |
|             +-----------------------+                                                   |
+-----------------------------------------------------------------------------------------+
```

#### Why Address Multiplexing is Mandatory
A $4\text{M} \times 4$ DRAM chip contains $4,194,304$ unique 4-bit nibbles.
- Directly addressing $4\text{M}$ words requires:
  $$\text{Address Lines} = \log_2(4,194,304) = 22\text{ address bits}$$
- If the chip had 22 dedicated address pins, plus 4 data pins (`D0-D3`), power (`V_DD`), ground (`V_SS`), and control lines (`RAS#`, `CAS#`, `WE#`, `OE#`), the physical silicon package would require over **36 to 40 pins**.
- In the semiconductor industry, physical package pin count directly dictates package cost, board trace routing complexity, and silicon surface area.
- **The Architectural Solution:** Memory designers split the 22-bit address into two equal 11-bit halves transmitted sequentially across **only 11 physical address pins ($A_0 - A_{10}$)**:

1. **Step 1: Row Address Strobe (`RAS#`):**
   - The memory controller places the upper 11 address bits ($A_{11} - A_{21}$) onto the 11 address pins.
   - The controller pulls `RAS#` LOW.
   - The internal Row Decoder latches the 11 bits and energizes **1 of the 2,048 Word Lines**.
   - An entire row of **$2,048 \times 4\text{ bits} = 8,192\text{ cells}$** dumps its charge into the Sense Amplifiers simultaneously (loading the **Row Buffer**).
2. **Step 2: Column Address Strobe (`CAS#`):**
   - The memory controller switches the same 11 address pins to present the lower 11 address bits ($A_0 - A_{10}$).
   - The controller pulls `CAS#` LOW.
   - The Column Decoder selects the specific 4-bit nibble from the 2,048 latched sense amplifiers and gates it to data output pins `D0 - D3`.

##### Key Result:
The physical address pin count is halved from **22 pins to 11 pins**, allowing the chip to be housed in a compact, inexpensive 26-pin Small Outline J-lead (SOJ) or Thin Small Outline Package (TSOP)!

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Quantitative DRAM Refresh & Timing Trace

##### Problem Statement
An enterprise database server contains a 32 GB DDR4 memory module constructed from 8Gb DRAM chips. Each chip has an array geometry of $65,536\text{ rows}$ ($2^{16}$) per bank.
- Maximum allowable retention window $t_{\text{ref}} = 64\text{ ms}$.
- Time required to service a single refresh command (Row Refresh Cycle Time) is $t_{\text{RFC}} = 260\text{ ns}$.

1. Calculate the required distributed refresh interval ($t_{\text{REFI}}$) in microseconds.
2. Calculate the total percentage of memory operational time lost to refresh overhead.
3. If operating in a high-temperature industrial environment ($T > 85^\circ\text{C}$), the retention window drops to $t_{\text{ref}} = 32\text{ ms}$. Re-calculate the refresh overhead percentage.

##### Mathematical Solutions

1. **Distributed Refresh Interval ($t_{\text{REFI}}$):**
   $$t_{\text{REFI}} = \frac{t_{\text{ref}}}{\text{Number of Rows}} = \frac{64\text{ ms}}{65,536\text{ rows}} = \frac{64 \times 10^{-3}\text{ s}}{65,536} \approx 9.7656 \times 10^{-7}\text{ s} = 0.9766\ \mu\text{s}$$
   *(Note: Modern DDR4 standardizes on $t_{\text{REFI}} = 7.8\ \mu\text{s}$ by refreshing banks in parallel groups of 8).*

2. **Refresh Overhead Percentage ($T \le 85^\circ\text{C}$):**
   $$\text{Total Time Spent Refreshing per Window} = 65,536 \times t_{\text{RFC}} = 65,536 \times 260\text{ ns} = 17,039,360\text{ ns} \approx 17.04\text{ ms}$$
   $$\text{Overhead Percentage} = \frac{17.04\text{ ms}}{64.0\text{ ms}} \times 100\% = 26.62\% \quad (\text{if unbanked single-row})$$
   Under JEDEC All-Bank parallel refresh ($t_{\text{RFC}} = 260\text{ ns}$ every $t_{\text{REFI}} = 7.8\ \mu\text{s}$):
   $$\text{JEDEC Refresh Overhead} = \frac{t_{\text{RFC}}}{t_{\text{REFI}}} = \frac{260\text{ ns}}{7,800\text{ ns}} \times 100\% \approx 3.33\%$$

3. **High-Temperature Overhead ($T > 85^\circ\text{C}$, $t_{\text{ref}} = 32\text{ ms}$):**
   $$t_{\text{REFI\_hot}} = \frac{7.8\ \mu\text{s}}{2} = 3.9\ \mu\text{s}$$
   $$\text{Hot Refresh Overhead} = \frac{260\text{ ns}}{3,900\text{ ns}} \times 100\% = 6.67\% \quad (\text{Doubled memory access penalty!})$$

---

#### Level 2 — Scaffolded Bug-Fix: DRAM Row-Buffer Conflict & Timing Violation Fix

##### Defect Scenario
An embedded real-time robotics vision controller interfaces directly with an SDRAM chip using a custom FPGA memory controller. The controller accesses image pixels stored across different rows of DRAM Bank 0:

```c
// DEFECTIVE MEMORY CONTROLLER TIMING SEQUENCE: ROW CONFLICT COLLISION
void read_pixel_pair(uint32_t rowA, uint32_t colA, uint32_t rowB, uint32_t colB) {
    // Access Pixel 1 in Row A
    assert_RAS(rowA);
    delay_cycles(t_RCD); // Wait RAS-to-CAS delay (e.g., 14 ns)
    assert_CAS(colA);
    uint32_t p1 = read_data_bus();

    // Immediately attempt to access Pixel 2 in Row B (DIFFERENT ROW IN SAME BANK!)
    assert_RAS(rowB); // FATAL HARDWARE TIMING VIOLATION!
    delay_cycles(t_RCD);
    assert_CAS(colB);
    uint32_t p2 = read_data_bus(); // Reads corrupt garbage / electrical bus contention!
}
```

##### Microarchitectural Diagnosis
- In dynamic RAM, the **Row Buffer** acts as an internal cache holding exactly one open row at a time.
- When `assert_RAS(rowA)` is issued, Row A is activated and copied into the Sense Amplifiers.
- To access a *different* row (Row B) in the same bank, the controller **MUST FIRST DEACTIVATE AND PRECHARGE ROW A**:
  1. It must issue a **Precharge (`PRE`)** command to close Row A, restoring capacitor charges and resetting Bit Lines to $V_{DD}/2$.
  2. It must wait for the **Row Precharge Latency ($t_{RP}$)** before issuing a new `RAS` command for Row B!
- By asserting `RAS(rowB)` while Row A was still actively driving the sense amplifiers, the internal word lines short-circuited, corrupting the stored charge across all capacitors in Row A!

<details>
<summary><b>View Architectural Solution & Corrected State Machine</b></summary>

```c
// ============================================================================
// CORRECTED MEMORY CONTROLLER: ROW BUFFER MANAGEMENT WITH PRECHARGE TIMING
// ============================================================================
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t active_row;
    bool is_open;
} DRAMBankState;

DRAMBankState bank0 = {.active_row = 0, .is_open = false};

// JEDEC Timing Parameters (in clock cycles)
#define T_RCD 5  // RAS-to-CAS delay (Row activation time)
#define T_CAS 5  // Column Access Strobe latency (read data ready)
#define T_RP  5  // Row Precharge time (closing active row)
#define T_RAS 14 // Minimum Row Active time (time row must stay open)

void dram_access_word(uint32_t target_row, uint32_t target_col, uint32_t* out_data) {
    if (bank0.is_open && bank0.active_row == target_row) {
        // CASE 1: ROW HIT (Page Hit): Row is ALREADY OPEN in sense amps!
        // No RAS or PRE needed! Zero row activation penalty!
        assert_CAS(target_col);
        delay_cycles(T_CAS);
        *out_data = read_data_bus();
    } else {
        // CASE 2: ROW MISS / CONFLICT: Must close existing row first!
        if (bank0.is_open) {
            // Step 1: Precharge and close currently open row
            issue_PRECHARGE_command();
            delay_cycles(T_RP); // Mandatory t_RP wait for bitline restoration!
            bank0.is_open = false;
        }

        // Step 2: Activate new row (RAS)
        assert_RAS(target_row);
        delay_cycles(T_RCD); // Wait t_RCD for sense amplifiers to stabilize
        bank0.active_row = target_row;
        bank0.is_open = true;

        // Step 3: Column read (CAS)
        assert_CAS(target_col);
        delay_cycles(T_CAS);
        *out_data = read_data_bus();
    }
}
```

</details>

---

#### Level 3 — High-Scale System Design: Cycle-Accurate DRAM Controller Simulator in C++

Design a complete, cycle-accurate discrete-event C++17 simulation modeling:
1. **DRAM Bank Architecture** with a single shared Row Buffer.
2. Standard JEDEC DDR4 timing constraints: $t_{RCD}$ (RAS-to-CAS), $t_{RP}$ (Row Precharge), $t_{CAS}$ (Column Latency), and $t_{RAS}$ (Row Active Time).
3. **Open-Page vs. Closed-Page Policy Comparison:** Demonstrates how locality converts 50 ns memory misses into 14 ns row-buffer hits.

<details>
<summary><b>View Complete C++ DRAM Memory Controller Simulator Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: CYCLE-ACCURATE DRAM CONTROLLER & ROW BUFFER SIMULATOR
// Compile: g++ -std=c++17 -O3 dram_sim.cpp -o dram_sim
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cstdint>

enum class BankState { CLOSED, ACTIVE, PRECHARGING };

struct DRAMRequest {
    uint32_t request_id;
    uint32_t row;
    uint32_t column;
    uint64_t arrival_cycle;
};

class DRAMController {
private:
    // JEDEC Timing Parameters (in clock cycles)
    const uint64_t t_RCD = 14; // RAS-to-CAS delay (Row activation)
    const uint64_t t_CAS = 14; // Column read latency
    const uint64_t t_RP  = 14; // Row Precharge delay
    const uint64_t t_RAS = 32; // Minimum Row Active time

    BankState state = BankState::CLOSED;
    uint32_t active_row = 0;
    uint64_t current_cycle = 0;
    uint64_t row_opened_at_cycle = 0;

    // Telemetry
    uint64_t total_requests = 0;
    uint64_t row_hits = 0;
    uint64_t row_conflicts = 0;
    uint64_t total_latency_cycles = 0;

public:
    void service_request(const DRAMRequest& req) {
        total_requests++;
        if (current_cycle < req.arrival_cycle) {
            current_cycle = req.arrival_cycle;
        }

        uint64_t start_time = current_cycle;
        std::cout << "\n[Cycle " << std::setw(5) << current_cycle << "] REQ #" << req.request_id 
                  << " (Row: " << req.row << ", Col: " << req.column << ")\n";

        if (state == BankState::ACTIVE && active_row == req.row) {
            // ROW BUFFER HIT!
            row_hits++;
            current_cycle += t_CAS;
            std::cout << "  -> ROW BUFFER HIT! Col Read issued. Data ready at cycle " << current_cycle 
                      << " (Latency: " << (current_cycle - start_time) << " cycles)\n";
        } else if (state == BankState::ACTIVE && active_row != req.row) {
            // ROW BUFFER CONFLICT!
            row_conflicts++;
            std::cout << "  -> ROW CONFLICT! Closing Row " << active_row << "...\n";

            // Enforce minimum t_RAS before precharging
            uint64_t active_time = current_cycle - row_opened_at_cycle;
            if (active_time < t_RAS) {
                current_cycle += (t_RAS - active_time);
            }

            // Issue Precharge (t_RP)
            current_cycle += t_RP;
            std::cout << "     Precharge complete at cycle " << current_cycle << ". Opening Row " << req.row << "...\n";

            // Issue Activate (t_RCD)
            current_cycle += t_RCD;
            active_row = req.row;
            row_opened_at_cycle = current_cycle;

            // Issue Read (t_CAS)
            current_cycle += t_CAS;
            std::cout << "     Data ready at cycle " << current_cycle 
                      << " (Total Latency: " << (current_cycle - start_time) << " cycles)\n";
        } else {
            // BANK WAS CLOSED (Row Miss)
            std::cout << "  -> ROW MISS (Bank Closed). Activating Row " << req.row << "...\n";
            current_cycle += t_RCD;
            active_row = req.row;
            state = BankState::ACTIVE;
            row_opened_at_cycle = current_cycle;

            current_cycle += t_CAS;
            std::cout << "     Data ready at cycle " << current_cycle 
                      << " (Total Latency: " << (current_cycle - start_time) << " cycles)\n";
        }

        total_latency_cycles += (current_cycle - start_time);
    }

    void print_statistics() const {
        std::cout << "\n=======================================================\n";
        std::cout << "       DRAM CONTROLLER PERFORMANCE TELEMETRY           \n";
        std::cout << "=======================================================\n";
        std::cout << "Total Memory Requests : " << total_requests << "\n";
        std::cout << "Row Buffer Hits       : " << row_hits << " (" 
                  << std::fixed << std::setprecision(1) << (100.0 * row_hits / total_requests) << "%)\n";
        std::cout << "Row Buffer Conflicts  : " << row_conflicts << "\n";
        std::cout << "Average Latency       : " << std::fixed << std::setprecision(2) 
                  << (static_cast<double>(total_latency_cycles) / total_requests) << " cycles\n";
        std::cout << "=======================================================\n";
    }
};

int main() {
    DRAMController controller;

    // Workload demonstrating locality: Streaming through Row 100, then switching to Row 200
    std::vector<DRAMRequest> workload = {
        {1, 100, 0,  0},   // Row 100 Miss (Cold activate)
        {2, 100, 4,  20},  // Row 100 HIT! (Fast)
        {3, 100, 8,  40},  // Row 100 HIT! (Fast)
        {4, 100, 12, 60},  // Row 100 HIT! (Fast)
        {5, 200, 0,  80},  // Row 200 CONFLICT! (Precharge + Activate + Read)
        {6, 200, 4,  140}  // Row 200 HIT!
    };

    for (const auto& req : workload) {
        controller.service_request(req);
    }

    controller.print_statistics();
    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:semiconductor-memory-video }}

This video reviews the hardware mechanics of semiconductor memory, comparing SRAM latches to DRAM dynamic storage cells and explaining how memory controllers handle bus multiplexing.
