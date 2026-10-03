# Unit 4 — Cache Memory Principles, Mapping Functions & Coherency Architectures
## Lesson 1 — Memory Hierarchy Fundamentals, Locality of Reference & AMAT Analysis

### 1. Key Characteristics of Computer Memory Systems

In modern computer architecture, memory cannot be conceptualized as a single, uniform monolithic storage array. Microprocessor execution rates scale at an exponential pace dictated by pipeline depth and multi-core parallelism, whereas dynamic semiconductor memory access speeds are fundamentally constrained by capacitor charge/discharge physical kinetics and printed circuit board trace routing lengths.

To systematically categorize and design memory subsystems, computer architects classify storage systems across eight fundamental dimensions:

| Dimension / Characteristic | Architectural Description & Scope | Concrete Hardware Manifestations |
| :--- | :--- | :--- |
| **1. Location** | Physical positioning of the storage element relative to the CPU datapath. | • **Internal / CPU:** Register files, control store, L1/L2 caches.<br>• **Internal / System:** Main Semiconductor RAM (DRAM, DDR5).<br>• **External / Secondary:** Peripheral controllers (NVMe SSD, SATA, Optical). |
| **2. Capacity** | Total volume of binary data the memory medium can store. | Expressed in Bytes ($2^0$ to $2^{40+}$) or words (natural machine data width: 32-bit or 64-bit). |
| **3. Unit of Transfer** | Number of bits read into or written out of the memory subsystem simultaneously. | • **Internal:** Governed by the memory bus width (e.g., 64-bit word).<br>• **External:** Transferred in multi-word **blocks** (e.g., 64-byte cache line, 4 KB disk page). |
| **4. Access Method** | The algorithmic and physical mechanism required to locate and address a specific storage unit. | • **Sequential Access:** Linear serial tape pass.<br>• **Direct Access:** Track/sector head positioning (HDD).<br>• **Random Access:** Constant-time electrical row/column addressing (DRAM/SRAM).<br>• **Associative Access:** Content-based parallel comparison. |
| **5. Performance** | Quantitative metrics defining speed and throughput. | • **Access Time ($t_a$):** Latency from address assertion to valid data output.<br>• **Memory Cycle Time ($t_c$):** Minimum duration between consecutive accesses.<br>• **Transfer Rate ($R$):** Bandwidth in bits/second: $R = \text{Data Width} / t_c$. |
| **6. Physical Type** | Semiconductor, magnetic, optical, or magneto-optical physical medium. | Static RAM (bistable flip-flops), Dynamic RAM (MOS capacitor + transistor), Flash NAND, Magnetic disk. |
| **7. Physical Characteristics** | Volatility, erasability, and data retention behavior. | • **Volatile:** Loses contents on power down (SRAM, DRAM).<br>• **Non-Volatile:** Retains magnetic/floating-gate charge (ROM, Flash). |
| **8. Organization** | Physical array layout of storage cells, sense amplifiers, and decoders. | 2D/3D memory cell matrices, bank interleaving, rank/channel hierarchies. |

#### Detailed Examination of Access Methods
The four access methods represent fundamental hardware trade-offs between physical addressing complexity and retrieval latency:

1. **Sequential Access:**
   - Memory is organized into physical records ordered sequentially along a continuous medium.
   - Access is achieved by physically advancing past intervening records; access time is highly variable and depends on the current position of the read/write mechanism relative to the target record ($O(N)$ access time).
   - *Example:* Magnetic tape archives.
2. **Direct Access:**
   - Blocks or records occupy unique, distinct physical positions (tracks, sectors, cylinders).
   - The hardware access mechanism steps directly to the general vicinity of the target region, followed by a localized sequential search ($O(1)$ seek + $O(\text{sector})$ rotational latency).
   - *Example:* Hard Disk Drives (HDD), Floppy Disks.
3. **Random Access:**
   - Every uniquely addressable physical location has dedicated hardwired electrical addressing circuitry (row and column address strobes / decoders).
   - The time to access any arbitrary memory address is **strictly invariant** and completely independent of previous access sequences ($O(1)$ constant-time latency).
   - *Example:* Semiconductor Main Memory (SRAM, DRAM).
4. **Associative Access:**
   - A specialized variant of random-access memory where data is retrieved based on its **data contents** (or a subset of its bits) rather than its numeric physical memory address.
   - Internal comparison logic evaluates every stored word in parallel within a single clock cycle ($O(1)$ parallel lookup).
   - *Example:* Content-Addressable Memory (CAM) utilized in CPU Cache Tag directories and Translation Lookaside Buffers (TLBs).

---

### 2. The Memory Hierarchy Pyramid: Speed vs. Capacity vs. Cost/Bit Trade-Offs

The fundamental economic and physical reality governing digital computing is the **Memory Dilemma**:
1. *Faster access time* requires complex, high-power silicon structures (e.g., 6-transistor SRAM cells), which drastically increases the cost per bit ($\$/\text{bit}$).
2. *Greater storage capacity* requires compact, low-cost physical elements (e.g., 1-transistor 1-capacitor DRAM cells or 3D charge-trap NAND flash), which incur significantly higher latency and complex refresh/erase overheads.
3. *Lower cost per bit* inevitably leads to slower access times.

Computer architects resolve this conflict by arranging disparate memory technologies into a hierarchical pyramid:

```
+-----------------------------------------------------------------------------------------+
|                               THE MEMORY HIERARCHY PYRAMID                              |
|                                                                                         |
|                                         / \                                             |
|                                        /   \                                            |
|                                       / CPU \   < 1 ns Latency                          |
|                                      / REG-  \  512 B - 2 KB Capacity                   |
|                                     /  ISTERS \ $$$$$ Cost/bit                          |
|                                    /-----------\                                        |
|                                   /   LEVEL 1   \   1 - 2 ns Latency                    |
|                                  /  CACHE (SRAM) \  32 - 64 KB Capacity                 |
|                                 /-----------------\                                     |
|                                /      LEVEL 2      \   3 - 8 ns Latency                 |
|                               /     CACHE (SRAM)    \  256 KB - 1 MB Capacity           |
|                              /-----------------------\                                  |
|                             /         LEVEL 3         \   10 - 25 ns Latency            |
|                            /     SHARED CACHE (SRAM)   \  8 - 64 MB Capacity            |
|                           /-----------------------------\                               |
|                          /        SEMICONDUCTOR          \   60 - 100 ns Latency        |
|                         /      MAIN MEMORY (DRAM)         \  16 - 128 GB Capacity       |
|                        /-----------------------------------\                            |
|                       /          SECONDARY STORAGE          \   10 - 100 us Latency     |
|                      /         SOLID STATE DRIVE (SSD)       \  512 GB - 4 TB Capacity  |
|                     /-----------------------------------------\                         |
|                    /              TERTIARY STORAGE             \   1 - 10 ms Latency    |
|                   /         HARD DISK / CLOUD / TAPE ARCHIVE    \  Petabytes            |
|                  +-----------------------------------------------+                      |
+-----------------------------------------------------------------------------------------+
```

#### Quantitative Hardware Comparison Across Levels
| Hierarchy Level | Underlying Silicon Technology | Typical Access Latency | Typical Capacity | Implementation Location | Relative Cost per Byte |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CPU Registers** | Multi-ported D-type Flip-Flops | $\le 0.5\text{ ns}$ (1 clock cycle) | $1\text{ to }2\text{ KB}$ (32-64 regs) | On CPU execution core | Exorbitant ($> \$10,000/\text{GB}$) |
| **L1 Cache (Inst/Data)**| 6T Static RAM (SRAM) | $1.0\text{ to }1.5\text{ ns}$ (4 cycles) | $32\text{ to }64\text{ KB}$ per core | Inside CPU core execution pipeline | Very High ($\sim \$5,000/\text{GB}$) |
| **L2 Cache** | 6T / 8T SRAM | $3.0\text{ to }7.0\text{ ns}$ (12-14 cycles)| $512\text{ KB to }1\text{ MB}$ per core | Dedicated on-die slice | High ($\sim \$1,000/\text{GB}$) |
| **L3 Cache** | High-density 6T SRAM | $10\text{ to }25\text{ ns}$ (40-60 cycles) | $16\text{ to }96\text{ MB}$ shared | On-die central uncore ring | Moderate ($\sim \$200/\text{GB}$) |
| **Main Memory** | 1T-1C Dynamic RAM (DDR4/5)| $60\text{ to }100\text{ ns}$ (200+ cycles)| $16\text{ to }128\text{ GB}$ | Motherboard DIMM modules | Inexpensive ($\sim \$3/\text{GB}$) |
| **NVMe SSD** | 3D TLC/QLC NAND Flash | $10\text{ to }50\ \mu\text{s}$ ($10^5\text{ cycles}$) | $1\text{ to }8\text{ TB}$ | PCIe M.2 expansion slot | Very Cheap ($\sim \$0.08/\text{GB}$) |

#### The Von Neumann "Memory Wall"
Between 1980 and 2005, CPU clock frequencies scaled at roughly $55\%$ per year (following Moore's Law and Dennard scaling). In contrast, DRAM access latency improved by only $7\%$ per year. This divergence created the infamous **Memory Wall**:
- In 1980, a CPU read from DRAM took approximately $1$ clock cycle.
- Today, a CPU operating at $4.0\text{ GHz}$ ($0.25\text{ ns}$ clock period) waiting for a $100\text{ ns}$ DRAM access stalls for:
$$\text{Stall Cycles} = \frac{100\text{ ns}}{0.25\text{ ns}} = 400\text{ clock cycles!}$$
Unless almost all memory references are intercepted by high-speed SRAM caches, the CPU spends $99\%$ of its operational lifespan idle, waiting for the memory controller.

{{ media:coa-cache-hierarchy-diagram }}

---

### 3. The Principle of Locality: Temporal vs. Spatial Locality in Modern Datapaths

Why do small caches (e.g., a $64\text{ KB}$ L1 cache) successfully service $95\%\text{ to }98\%$ of all memory accesses generated by programs spanning hundreds of gigabytes?

The foundational theorem that makes hierarchical caching physically viable is the **Principle of Locality of Reference**, first formalized by Peter J. Denning (1968). Programs do not access their address space uniformly or randomly; instead, empirical measurements demonstrate that execution clustering follows two distinct dimensions:

```
+-----------------------------------------------------------------------------------------+
|                               PRINCIPLE OF LOCALITY                                     |
|                                                                                         |
|       [ TEMPORAL LOCALITY ]                             [ SPATIAL LOCALITY ]            |
|   "If address X is accessed at time t,             "If address X is accessed, nearby    |
|   it is highly probable that address X             addresses (X+1, X+2, ...) will be    |
|   will be accessed again at time t + dt."          accessed in the near future."        |
|                                                                                         |
|   +---------------------------------------+        +----------------------------------+ |
|   | int sum = 0;                          |        | int arr[1024];                   | |
|   | for (int i = 0; i < 10000; i++) {     |        | for (int i = 0; i < 1024; i++) { | |
|   |     sum += i;  // 'sum' and 'i' hit   |        |     sum += arr[i]; // Sequential | |
|   | }              // in registers/cache! |        | }                  // line burst | |
|   +---------------------------------------+        +----------------------------------+ |
+-----------------------------------------------------------------------------------------+
```

#### 1. Temporal Locality (Locality in Time)
- **Definition:** An item that is referenced at time $t$ will tend to be referenced again in the immediate future ($t + \Delta t$).
- **Software Structures Exhibiting Temporal Locality:**
  - Loop counters and iteration variables (`for (int i = 0; ...)`).
  - Accumulators and running totals (`sum += value`).
  - Frequently invoked function subroutines (leaf functions called inside inner loops).
  - The top of the runtime execution call stack (stack pointer `RSP`, local frame variables).
- **Hardware Exploitation:** When an item is accessed on a cache miss, it is fetched from slow memory and retained in the fastest cache levels (L1/L2), evicting items that have remained idle longest (Least Recently Used policy).

#### 2. Spatial Locality (Locality in Space)
- **Definition:** If a memory address $X$ is referenced at time $t$, addresses physically contiguous or adjacent to $X$ (e.g., $X+1, X+2, X+k$) are highly likely to be referenced in the near future.
- **Software Structures Exhibiting Spatial Locality:**
  - Sequential instruction execution: Unless a branch, call, or return instruction occurs, the Program Counter advances monotonically ($PC \leftarrow PC + 4$).
  - Arrays, matrices, and contiguous struct buffers traversed with unit stride ($i++$).
  - Sequential parsing of strings, file buffers, and network packet headers.
- **Hardware Exploitation:** When a memory read misses in cache, the memory subsystem **never fetches a solitary 4-byte or 8-byte word**. Instead, the cache controller fetches an entire **Block / Cache Line** (typically $64\text{ bytes} = 16$ contiguous 32-bit words) in a high-speed DRAM burst.
  - The first access (`arr[0]`) incurs a cache miss (Cold Miss).
  - The subsequent 15 accesses (`arr[1]` through `arr[15]`) hit instantaneously in L1 cache with zero DRAM latency!

---

### 4. Cache Read Operation Flowchart & Average Memory Access Time (AMAT) Formulations

#### The Cache Read Cycle Operational State Flow
When the CPU datapath issues an address to load an operand:

```
                          +------------------------+
                          |   CPU Issues Address   |
                          | (e.g., 0x0040_20A4)    |
                          +-----------+------------+
                                      |
                                      v
                          +------------------------+
                          | Decompose Address:     |
                          | Tag | Set/Line | Offset|
                          +-----------+------------+
                                      |
                                      v
                        /----------------------------\
                       /   Lookup Cache Directory:    \
                      <    Is Tag present AND          >
                       \   Valid Bit == 1 ?           /
                        \----------------------------/
                               /              \
                        YES   /                \   NO
                             v                  v
                    +-----------------+   +-------------------------+
                    |    CACHE HIT    |   |       CACHE MISS        |
                    +-----------------+   +-------------------------+
                             |                         |
                             v                         v
                    +-----------------+   +-------------------------+
                    | Extract word    |   | Stall CPU datapath      |
                    | using Offset    |   | Issue Burst Read to DRAM|
                    | bits (1-2 ns)   |   | for 64-Byte Block       |
                    +-----------------+   +-------------------------+
                             |                         |
                             v                         v
                    +-----------------+   +-------------------------+
                    | Return Word to  |   | Overwrite Cache Line    |
                    | CPU Register    |   | (run eviction if dirty) |
                    | Pipeline        |   | Update Tag & Set Valid=1|
                    +-----------------+   +-------------------------+
                                                       |
                                                       v
                                          +-------------------------+
                                          | Forward target word to  |
                                          | CPU (Early Restart /    |
                                          | Critical Word First)    |
                                          +-------------------------+
```

#### Mathematical Formulation of Average Memory Access Time (AMAT)
The overall speed of a computer memory subsystem cannot be measured by cache speed alone or main memory speed alone. The true operational figure of merit is the **Average Memory Access Time (AMAT)**.

##### 1. Single-Level Cache Model
For a system with a single cache level:
$$\text{AMAT} = T_{\text{hit}} + (\text{Miss Rate} \times \text{Miss Penalty})$$
Where:
- $T_{\text{hit}} = T_c$ (Time required to inspect the tag directory and deliver the word on a hit).
- $\text{Hit Rate} = H$ (Probability that the requested word is present in cache, $0 \le H \le 1$).
- $\text{Miss Rate} = M = (1 - H)$ (Probability that the access misses).
- $\text{Miss Penalty} = T_m$ (Total latency required to service the miss, including bus arbitration, DRAM row activation, burst transfer, and cache line installation).

Alternatively expressed:
$$\text{AMAT} = H \cdot T_c + (1 - H) \cdot (T_c + T_m) = T_c + (1 - H) \cdot T_m$$

##### 2. Multi-Level Cache Model (L1, L2, L3 & DRAM)
In modern processors featuring a three-level hierarchy, a miss in L1 accesses L2; a miss in L2 accesses L3; and only an L3 miss propagates to DRAM:

$$\text{AMAT} = T_{L1} + M_{L1} \times \left( T_{L2} + M_{L2} \times \left( T_{L3} + M_{L3} \times T_{\text{DRAM}} \right) \right)$$

Where:
- $T_{L1}, T_{L2}, T_{L3}$ are the local hit times of L1, L2, and L3 caches.
- $M_{L1}, M_{L2}, M_{L3}$ are the **local miss rates** of each respective cache level.
- The **Global Miss Rate** is the fraction of all CPU memory references that miss all the way to DRAM:
$$\text{Global Miss Rate} = M_{L1} \times M_{L2} \times M_{L3}$$

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Quantitative AMAT & Pipeline Stall Analysis

##### Problem Statement
A high-performance server processor runs at a core clock frequency of $f = 4.0\text{ GHz}$ (Clock cycle period $\tau = 0.25\text{ ns}$).
The CPU executes a benchmark workload where $30\%$ of all instructions are Memory Data Instructions (Loads/Stores). The base CPI (Cycles Per Instruction) assuming a 100% ideal cache hit rate is $\text{CPI}_{\text{base}} = 1.20$.

The cache hierarchy has the following measured parameters:
- **L1 Data Cache:** Local Hit Time $T_{L1} = 4\text{ clock cycles}$ ($1.0\text{ ns}$), Local Miss Rate $M_{L1} = 6.0\%$.
- **L2 Cache:** Local Hit Time $T_{L2} = 12\text{ clock cycles}$ ($3.0\text{ ns}$), Local Miss Rate $M_{L2} = 15.0\%$.
- **L3 Cache:** Local Hit Time $T_{L3} = 40\text{ clock cycles}$ ($10.0\text{ ns}$), Local Miss Rate $M_{L3} = 20.0\%$.
- **Main Memory (DRAM):** Access Latency $T_{\text{DRAM}} = 300\text{ clock cycles}$ ($75.0\text{ ns}$).

##### Analytical Derivations

1. **Calculate the Global Miss Rate to Main Memory:**
   $$\text{Global Miss Rate} = M_{L1} \times M_{L2} \times M_{L3} = 0.06 \times 0.15 \times 0.20 = 0.0018 = 0.18\%$$
   *Only 18 out of every 10,000 memory references reach DRAM!*

2. **Calculate the Average Memory Access Time (AMAT) in Clock Cycles:**
   $$\text{AMAT} = T_{L1} + M_{L1} \times \left[ T_{L2} + M_{L2} \times \left( T_{L3} + M_{L3} \times T_{\text{DRAM}} \right) \right]$$
   - *L3 Miss Cost to DRAM:* $T_{L3} + (0.20 \times 300) = 40 + 60 = 100\text{ cycles}$.
   - *L2 Penalty:* $T_{L2} + (0.15 \times 100) = 12 + 15 = 27\text{ cycles}$.
   - *Total AMAT:*
   $$\text{AMAT} = 4 + 0.06 \times 27 = 4 + 1.62 = 5.62\text{ clock cycles } (1.405\text{ ns})$$

3. **Calculate the Real CPI including Memory Stall Cycles:**
   $$\text{CPI}_{\text{real}} = \text{CPI}_{\text{base}} + (\text{Memory Instructions / Instruction}) \times \text{Memory Stall Cycles}$$
   Where $\text{Memory Stall Cycles} = \text{AMAT} - T_{L1} = 5.62 - 4.0 = 1.62\text{ cycles}$.
   $$\text{CPI}_{\text{real}} = 1.20 + (0.30 \times 1.62) = 1.20 + 0.486 = 1.686$$

4. **Quantify the Performance Degradation from Memory Stalls:**
   $$\text{Slowdown} = \frac{\text{CPI}_{\text{real}}}{\text{CPI}_{\text{base}}} = \frac{1.686}{1.20} = 1.405 \quad (40.5\%\text{ execution time spent waiting on cache/memory})$$

---

#### Level 2 — Scaffolded Bug-Fix: Matrix Traversal Cache Thrashing & Stride Optimization

##### Defect Scenario
A quantitative finance analytics engine performs mathematical operations on a large 2D matrix of double-precision floating-point numbers ($N \times N$, where $N = 4096$). Each `double` occupies $8\text{ bytes}$.
The target CPU features:
- L1 Data Cache: $32\text{ KB}$, 8-way set associative, with standard $64\text{-Byte}$ cache lines.
- Memory row size: $4096 \times 8\text{ bytes} = 32,768\text{ bytes} = 32\text{ KB}$ per row.

A junior software engineer writes the following matrix summation algorithm:

```c
// DEFECTIVE IMPLEMENTATION: CATASTROPHIC CACHE THRASHING
double compute_matrix_sum(double matrix[4096][4096]) {
    double total = 0.0;
    // Outer loop traverses COLUMNS, Inner loop traverses ROWS!
    for (int col = 0; col < 4096; col++) {
        for (int row = 0; row < 4096; row++) {
            total += matrix[row][col]; // Stride = 4096 elements = 32 KB jump!
        }
    }
    return total;
}
```

When profiled in production, the code runs **18 times slower** than theoretical memory bandwidth limits!

##### Microarchitectural Diagnosis
- In C/C++, multi-dimensional arrays are stored in **Row-Major Order** (row elements are stored contiguously in memory: `matrix[0][0]`, `matrix[0][1]`, `matrix[0][2]`, ...).
- Each $64\text{-Byte}$ cache line contains $\frac{64\text{ bytes}}{8\text{ bytes/double}} = 8$ contiguous doubles.
- In the defective code, the inner loop increments `row`, accessing `matrix[row][col]`. Consecutive memory references jump by:
  $$\text{Stride} = 4096 \times 8\text{ bytes} = 32,768\text{ bytes} = 32\text{ KB}$$
- Because every access jumps $32\text{ KB}$, each access lands in a completely different cache line. None of the other 7 doubles fetched into the $64\text{-byte}$ cache line are ever reused before being evicted!
- **Spatial Locality Utilization = $0\%$!** Cache Miss Rate $\approx 100\%$ on every single matrix element!

<details>
<summary><b>View Architectural Solution & Corrected Loop Transformation</b></summary>

```c
// ============================================================================
// CORRECTED IMPLEMENTATION: OPTIMAL SPATIAL LOCALITY (UNIT STRIDE)
// ============================================================================
#include <stdio.h>
#include <stdlib.h>
#include <immintrin.h>

#define N 4096

// Loop Interchange Transformation: Outer loop traverses ROWS, Inner traverses COLS
double compute_matrix_sum_optimized(double matrix[N][N]) {
    double total = 0.0;
    
    // By interchanging loops, memory is accessed strictly sequentially (Unit Stride = 8 Bytes)
    for (int row = 0; row < N; row++) {
        for (int col = 0; col < N; col++) {
            total += matrix[row][col]; // Cache Hit Rate jumps to 7/8 = 87.5% in L1!
        }
    }
    return total;
}

// Advanced Cache Blocking (Tiling) for Matrix Multiplication / Transposition
// Divides NxN matrix into BxB sub-blocks that fit entirely within L1 Cache
#define BLOCK_SIZE 64 // 64 * 8 bytes = 512 bytes per tile row (fits in L1)

void blocked_matrix_process(double A[N][N], double B[N][N], double C[N][N]) {
    for (int sj = 0; sj < N; sj += BLOCK_SIZE) {
        for (int si = 0; si < N; si += BLOCK_SIZE) {
            for (int sk = 0; sk < N; sk += BLOCK_SIZE) {
                // Micro-kernels operate exclusively inside L1 cache working set
                for (int i = si; i < si + BLOCK_SIZE; i++) {
                    for (int k = sk; k < sk + BLOCK_SIZE; k++) {
                        for (int j = sj; j < sj + BLOCK_SIZE; j++) {
                            C[i][j] += A[i][k] * B[k][j];
                        }
                    }
                }
            }
        }
    }
}
```

##### Quantitative Profiling Comparison:
- **Defective (Column-Major):** $16,777,216$ accesses $\times 100\text{ ns DRAM access} \approx 1.68\text{ seconds}$ memory stall time.
- **Optimized (Row-Major):** Only $1$ miss every $8$ accesses. $2,097,152$ DRAM misses $\implies 0.21\text{ seconds}$ stall time (**$8.0\times$ faster memory bandwidth**)!

</details>

---

#### Level 3 — High-Scale System Design: Cache Working Set Benchmarking Harness in C++

Design a complete, high-precision C++17 benchmarking program that empirically measures:
1. The physical transition cliffs between L1 ($32\text{ KB}$), L2 ($512\text{ KB}$), L3 ($16\text{ MB}$), and Main Memory DRAM by sweeping array working sets from $4\text{ KB}$ to $64\text{ MB}$.
2. Utilizes pointer chasing to defeat hardware stream prefetchers, isolating true random-access memory latency.

<details>
<summary><b>View Complete C++ Cache Hierarchy Benchmark Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: POINTER-CHASING MEMORY LATENCY BENCHMARK
// Compile: g++ -std=c++17 -O3 cache_benchmark.cpp -o cache_benchmark
// ============================================================================

#include <iostream>
#include <vector>
#include <numeric>
#include <random>
#include <chrono>
#include <iomanip>
#include <cstdint>

// Pointer chasing node structure (matches 64-byte cache line size)
struct alignas(64) CacheNode {
    CacheNode* next;
    uint8_t padding[64 - sizeof(CacheNode*)]; // Pad to exactly one 64B cache line
};

void run_pointer_chase_experiment(size_t size_bytes) {
    size_t num_nodes = size_bytes / sizeof(CacheNode);
    if (num_nodes < 2) return;

    std::vector<CacheNode> buffer(num_nodes);
    std::vector<size_t> indices(num_nodes);
    std::iota(indices.begin(), indices.end(), 0);

    // Randomize access order to completely defeat hardware branch/stream prefetchers
    std::mt19937_64 rng(1337);
    std::shuffle(indices.begin(), indices.end(), rng);

    // Construct circular singly-linked list
    for (size_t i = 0; i < num_nodes - 1; i++) {
        buffer[indices[i]].next = &buffer[indices[i + 1]];
    }
    buffer[indices[num_nodes - 1]].next = &buffer[indices[0]];

    // Warm up cache working set
    CacheNode* curr = &buffer[indices[0]];
    for (size_t i = 0; i < num_nodes * 2; i++) {
        curr = curr->next;
    }

    // Benchmark loop: 5,000,000 pointer chases
    const uint64_t iterations = 5000000;
    auto t_start = std::chrono::high_resolution_clock::now();

    for (uint64_t i = 0; i < iterations; i++) {
        curr = curr->next;
    }

    auto t_end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::nano> elapsed_ns = t_end - t_start;
    double latency_per_access = elapsed_ns.count() / iterations;

    std::string zone = "L1 Cache";
    if (size_bytes > 64 * 1024 && size_bytes <= 1024 * 1024) zone = "L2 Cache";
    else if (size_bytes > 1024 * 1024 && size_bytes <= 32 * 1024 * 1024) zone = "L3 Cache";
    else if (size_bytes > 32 * 1024 * 1024) zone = "Main Memory (DRAM)";

    std::cout << "Working Set: " << std::setw(6) << (size_bytes / 1024) << " KB | "
              << "Latency: " << std::fixed << std::setprecision(2) << std::setw(6) << latency_per_access << " ns | "
              << "Hierarchy Zone: " << zone << "\n";
}

int main() {
    std::cout << "======================================================================\n";
    std::cout << "      CPU CACHE MEMORY HIERARCHY LATENCY CHARACTERIZATION BENCHMARK   \n";
    std::cout << "======================================================================\n";

    // Sweep working sets from 4 KB to 64 MB
    std::vector<size_t> test_sizes_kb = {
        4, 8, 16, 32, 48, 64,          // L1 Data Cache range (< 64 KB)
        128, 256, 512, 1024,           // L2 Cache range (< 1 MB)
        2048, 4096, 8192, 16384, 24576, // L3 Shared Cache range (< 32 MB)
        49152, 65536                   // DRAM range (> 32 MB)
    };

    for (size_t kb : test_sizes_kb) {
        run_pointer_chase_experiment(kb * 1024);
    }

    std::cout << "======================================================================\n";
    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:cache-explained-video }}

This video provides a photorealistic 3D visualization of CPU cache microarchitecture, illustrating how nanometer-scale SRAM cells, cache lines, and multi-level hierarchies bridge the latency gulf between the CPU core and external DRAM chips.
