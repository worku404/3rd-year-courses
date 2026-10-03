# Unit 4 — Cache Memory Principles, Mapping Functions & Coherency Architectures
## Lesson 2 — Cache Mapping Architectures: Direct, Fully Associative & Set-Associative Mapping

### 1. The Cache Mapping Problem & Address Partitioning

In any computer architecture incorporating high-speed cache memory, a fundamental structural disparity exists: **Main Memory is vast, while Cache Memory is compact**.
- Consider a representative system:
  - Main Memory capacity = $16\text{ MB} = 2^{24}\text{ bytes}$ (requiring a $24\text{-bit}$ physical address).
  - Main Memory block size = $4\text{ bytes} = 2^2\text{ bytes}$ ($w = 2\text{ bits}$).
  - Total number of memory blocks = $\frac{16\text{ MB}}{4\text{ B}} = 4\text{ M blocks} = 2^{22}\text{ blocks}$.
  - Cache Memory capacity = $64\text{ KB} = 2^{16}\text{ bytes}$.
  - Total number of cache lines = $\frac{64\text{ KB}}{4\text{ B}} = 16,384\text{ lines} = 16\text{ K lines} = 2^{14}\text{ lines}$.

Because $2^{22}$ memory blocks must share $2^{14}$ cache lines, **each cache line must be dynamically shared by $2^{22 - 14} = 2^8 = 256$ distinct main memory blocks!**

The **Mapping Function** is the architectural algorithm that governs:
1. Which specific cache slot(s) a given main memory block is permitted to occupy.
2. How the CPU's binary address is decomposed into bit-fields to locate, identify, and verify the requested data within nanoseconds.

There are three classic mapping architectures: **Direct Mapping**, **Fully Associative Mapping**, and **$K$-Way Set-Associative Mapping**.

{{ media:coa-cache-mapping-diagram }}

---

### 2. Direct Mapping Architecture: Modulo Indexing & Address Fields

#### Operational Principle
Direct Mapping is the simplest mapping technique. Each block of main memory maps to **exactly one fixed line** in the cache. The mapping function is defined mathematically by the modulo operation:

$$i = j \pmod m$$

Where:
- $i$ = Assigned Cache Line index ($0 \le i < m$).
- $j$ = Main Memory Block number ($j = \lfloor \text{Address} / \text{Block Size} \rfloor$).
- $m$ = Total number of lines in the cache ($m = 2^r$).

#### Physical Address Bit Partitioning
Under Direct Mapping, the CPU's $n$-bit physical address is partitioned into three contiguous bit-fields:

```
+-----------------------------------------------------------------------------------------+
|                         DIRECT MAPPED PHYSICAL ADDRESS FORMAT                           |
|                                                                                         |
|         <------------------------------ n bits ------------------------------>          |
|        +---------------------------+------------------------+------------------+        |
|        |         TAG FIELD         |    LINE / SLOT FIELD   |    WORD OFFSET   |        |
|        |        (s - r bits)       |        (r bits)        |     (w bits)     |        |
|        +---------------------------+------------------------+------------------+        |
|         <------------------- Block Address s bits --------->                            |
+-----------------------------------------------------------------------------------------+
```

1. **Word Offset Field ($w$ bits):** Identifies the specific byte or word within a $2^w\text{-byte}$ cache line.
2. **Line / Slot Index Field ($r$ bits):** Selects one of the $m = 2^r$ lines in the cache directory.
3. **Tag Field ($s - r$ bits):** Stored alongside the data in the cache directory. Because multiple memory blocks map to the same line, the Tag uniquely identifies *which* of those candidate blocks currently occupies the slot.

##### Concrete Architectural Example (Stallings / AASTU Benchmark):
- Main Memory = $16\text{ MB} \implies n = 24\text{ bits}$.
- Block Size = $4\text{ bytes} \implies w = \log_2(4) = 2\text{ bits}$.
- Cache Size = $64\text{ KB} = 16\text{ K lines} \implies m = 2^{14} \implies r = 14\text{ bits}$.
- Tag Size = $n - r - w = 24 - 14 - 2 = 8\text{ bits}$ ($s - r = 22 - 14 = 8\text{ bits}$).

```
Bit Positions:  [ 23 . . . 16 ]  [ 15 . . . 2 ]  [ 1 . . 0 ]
Field:              TAG            LINE INDEX      WORD OFFSET
Width:             8 Bits           14 Bits          2 Bits
```

#### Hardware Lookup Logic
1. The CPU generates a 24-bit physical address.
2. The $14\text{-bit}$ Line Index bits ($A_{15} - A_2$) are fed directly into an address decoder to index row $i$ of the cache SRAM array.
3. The cache line's stored Tag ($8\text{ bits}$) and **Valid Bit ($V$)** are read out.
4. A single $8\text{-bit}$ hardware comparator checks:
   $$\text{Hit Condition} = (V == 1) \land (\text{Stored Tag} == \text{Address}[23:16])$$
5. If true, a **Cache Hit** signal is asserted, and the $2\text{-bit}$ Word Offset ($A_1 - A_0$) gates the requested word through a multiplexer to the CPU pipeline.

#### Architectural Evaluation
- **Advantages:**
  - Extremely simple and inexpensive hardware implementation.
  - Requires only **one tag comparator** per cache access.
  - Constant-time $O(1)$ indexed lookup with zero search delay.
- **Disadvantages:**
  - **Severe Conflict Misses (Thrashing):** Because each block has exactly one possible location, if a program repeatedly accesses two distinct memory blocks that happen to share the same line index ($j_1 \equiv j_2 \pmod m$), the two blocks will continuously evict each other on every iteration, driving the hit rate to $0\%$!

---

### 3. Fully Associative Mapping: Parallel Tag Matching & CAM Architecture

#### Operational Principle
To eliminate conflict misses entirely, **Fully Associative Mapping** permits a main memory block to be loaded into **any arbitrary line** within the cache.

Because a block has no predetermined slot, the cache line index field disappears from the address. The physical address is partitioned into only two fields:

```
+-----------------------------------------------------------------------------------------+
|                     FULLY ASSOCIATIVE PHYSICAL ADDRESS FORMAT                           |
|                                                                                         |
|         <------------------------------ n bits ------------------------------>          |
|        +----------------------------------------------------+------------------+        |
|        |                     TAG FIELD                      |    WORD OFFSET   |        |
|        |                   (s = n - w bits)                 |     (w bits)     |        |
|        +----------------------------------------------------+------------------+        |
+-----------------------------------------------------------------------------------------+
```

##### Concrete Architectural Example:
- Address = $24\text{ bits}$.
- Block Size = $4\text{ bytes} \implies w = 2\text{ bits}$.
- Tag Size = $24 - 2 = 22\text{ bits}$ ($s = 22\text{ bits}$).

```
Bit Positions:  [ 23 . . . . . . . . . . 2 ]  [ 1 . . 0 ]
Field:                     TAG                 WORD OFFSET
Width:                   22 Bits                 2 Bits
```

#### Hardware Lookup Logic: Content-Addressable Memory (CAM)
Because any block can reside in any line, the cache controller cannot index a single line. Instead, it must examine the tag of **every single line in the cache simultaneously**:

```
CPU Tag (22 bits) ------------------------------------+
                                                      |
    +--------------+    +--------------+              |
    | Cache Line 0 |    | Line 0 Tag   | ===[==]======+---> Match 0?
    +--------------+    +--------------+   Comparator |
    | Cache Line 1 |    | Line 1 Tag   | ===[==]======+---> Match 1?
    +--------------+    +--------------+   Comparator |
           :                   :                      |
    +--------------+    +--------------+              |
    | Line 16,383  |    | Line 16,383  | ===[==]======+---> Match 16383?
    +--------------+    +--------------+   Comparator
                                                      |
                                                      v
                                        +----------------------------+
                                        | Priority Encoder / HIT MUX | ===> DATA OUT
                                        +----------------------------+
```

1. For a cache with $m = 16,384$ lines, the cache hardware requires **$16,384$ parallel 22-bit comparators**!
2. All 16,384 comparisons occur concurrently within a single clock phase.
3. If any comparator signals a match and its valid bit is set, a priority encoder drives the data multiplexer to output the target block.

#### Architectural Evaluation
- **Advantages:**
  - **Zero Conflict Misses:** A block is only evicted when the *entire* cache is $100\%$ full.
  - Maximum flexibility and optimal utilization of every available cache line.
- **Disadvantages:**
  - **Prohibitive Hardware Cost & Power Dissipation:** Fabricating tens of thousands of parallel comparators consumes immense silicon area and generates severe thermal dissipation.
  - **Replacement Complexity:** Requires an active hardware replacement algorithm (e.g., LRU) across all lines.
  - *Practical Usage:* Fully associative caches are physically restricted to small specialized buffers, such as Translation Lookaside Buffers (TLBs with 32 to 128 entries) and Victim Caches.

---

### 4. K-Way Set-Associative Mapping: The Modern Compromise

#### Operational Principle
To achieve the high hit rates of associative mapping without the catastrophic hardware cost of thousands of comparators, modern microprocessors (Intel Core, AMD Zen, ARM Cortex, Apple Silicon) universally implement **$K$-Way Set-Associative Mapping**.

The cache is physically partitioned into $v$ distinct **Sets**. Each set contains exactly $K$ cache lines (referred to as a "$K$-Way" associative cache):

$$m = v \times K$$

Where:
- $m$ = Total number of cache lines.
- $K$ = Associativity degree (typically $K \in \{2, 4, 8, 16\}$).
- $v$ = Total number of sets ($v = 2^d$).

#### The Mapping Function
A main memory block maps to **exactly one specific set**, but can occupy **any of the $K$ lines (ways) within that set**:

$$\text{Set Index} = j \pmod v$$

Where $j$ is the main memory block number.

#### Physical Address Bit Partitioning
Under $K$-way set associativity, the $n$-bit physical address is partitioned into:

```
+-----------------------------------------------------------------------------------------+
|                    K-WAY SET-ASSOCIATIVE PHYSICAL ADDRESS FORMAT                        |
|                                                                                         |
|         <------------------------------ n bits ------------------------------>          |
|        +---------------------------+------------------------+------------------+        |
|        |         TAG FIELD         |        SET FIELD       |    WORD OFFSET   |        |
|        |        (s - d bits)       |        (d bits)        |     (w bits)     |        |
|        +---------------------------+------------------------+------------------+        |
|         <------------------- Block Address s bits --------->                            |
+-----------------------------------------------------------------------------------------+
```

1. **Word Offset ($w$ bits):** Selects byte/word within block ($2^w\text{ bytes}$).
2. **Set Index ($d$ bits):** Selects one of the $v = 2^d$ sets ($d = \log_2(v)$).
3. **Tag Field ($s - d$ bits):** Compared against the $K$ tags stored in the selected set.

##### Concrete Architectural Example (2-Way Set Associative):
- Main Memory = $16\text{ MB} \implies n = 24\text{ bits}$.
- Block Size = $4\text{ bytes} \implies w = 2\text{ bits}$.
- Cache Size = $64\text{ KB} = 16,384\text{ lines}$.
- Degree of Associativity $K = 2$ lines/set.
- Number of Sets $v = \frac{16,384}{2} = 8,192\text{ sets} = 2^{13} \implies d = 13\text{ bits}$.
- Tag Field = $24 - 13 - 2 = 9\text{ bits}$.

```
Bit Positions:  [ 23 . . . 15 ]  [ 14 . . . 2 ]  [ 1 . . 0 ]
Field:              TAG             SET INDEX      WORD OFFSET
Width:             9 Bits            13 Bits         2 Bits
```

#### Hardware Lookup Datapath (2-Way Set Associative)
```
                  CPU Address: [ TAG: 9b | SET: 13b | OFFSET: 2b ]
                                             |
                                             v
                           +------------------------------------+
                           | Set Decoder: Selects Set #k (0-8191)|
                           +-----------------+------------------+
                                             |
                     +-----------------------+-----------------------+
                     |                                               |
                     v (Way 0)                                       v (Way 1)
           +--------------------+                          +--------------------+
           | Valid0 | Tag0 | Data|                          | Valid1 | Tag1 | Data|
           +---+----+---+----+---+                          +---+----+---+----+---+
               |        |                                       |        |
               |        v                                       |        v
               |     +====+                                     |     +====+
  CPU Tag =====+====>| == | Tag Comparator 0       CPU Tag =====+====>| == | Tag Comparator 1
  (9 bits)     |     +====+                        (9 bits)     |     +====+
               |        |                                       |        |
               v        v                                       v        v
             [ & ]  (Hit0?)                                   [ & ]  (Hit1?)
               |                                                |
               +-----------------------+------------------------+
                                       |
                                       v
                              [ OR Gate: HIT? ] --------------------------> CPU CACHE HIT
                                       |
                                       v
                            [ 2-to-1 DATA MULTIPLEXER ]
                                       |
                                       v
                           Target Word to CPU Pipeline
```

- Notice the dramatic hardware simplification: Instead of $16,384$ comparators, **only $K = 2$ comparators** are required!
- For an 8-way set associative cache, only 8 comparators are needed, regardless of whether the cache has 1,000 sets or 100,000 sets!

---

### 5. The 3 C's Miss Classification Framework

To systematically optimize cache microarchitectures, Mark Hill and David Patterson formulated the **3 C's Model**, categorizing all cache misses into three distinct physical causes:

```
+-----------------------------------------------------------------------------------------+
|                                THE 3 C'S CACHE MISS MODEL                               |
|                                                                                         |
|       +-------------------------------------------------------------------------+       |
|       | 1. COMPULSORY (COLD) MISSES:                                            |       |
|       | • Occur on the first reference to a memory block.                       |       |
|       | • Inevitable: The block has never been in cache before.                 |       |
|       | • Solution: Larger cache lines (spatial locality) & hardware prefetch.  |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|                                           v                                             |
|       +-------------------------------------------------------------------------+       |
|       | 2. CAPACITY MISSES:                                                     |       |
|       | • Occur when the cache cannot contain all blocks needed during execution.|       |
|       | • Occurs even in an idealized Fully Associative cache of that size.     |       |
|       | • Solution: Increase total physical cache capacity.                     |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|                                           v                                             |
|       +-------------------------------------------------------------------------+       |
|       | 3. CONFLICT (COLLISION) MISSES:                                         |       |
|       | • Occur when multiple blocks compete for the same line/set.             |       |
|       | • Would NOT occur in a fully associative cache of the same capacity.   |       |
|       | • Solution: Increase degree of associativity K (Direct -> 4-Way -> 8-Way)|      |
|       +-------------------------------------------------------------------------+       |
+-----------------------------------------------------------------------------------------+
```

*(Note: In multi-core shared memory systems, a **4th C** is added: **Coherence Misses**, caused by external bus invalidations when another processor writes to a shared line).*

---

### 6. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Comparative Trace Across Mapping Schemes

##### System Parameters
Consider a tiny, educational 8-word cache with 1-word blocks ($w = 0$ bits, 1 word per line). Total cache lines $m = 8$.
A sequence of memory block references is generated by the CPU:
$$\text{Reference Sequence:} \quad 0, \ 4, \ 8, \ 0, \ 4, \ 8, \ 1, \ 2$$

Trace the contents and Hit/Miss state of:
1. **Direct Mapped Cache** ($m = 8$ lines, Line $= j \pmod 8$).
2. **2-Way Set Associative Cache** ($v = 4$ sets, Set $= j \pmod 4$, LRU replacement).
3. **Fully Associative Cache** ($m = 8$ lines, LRU replacement).

##### Step-by-Step Execution Trace Table:

| Ref ($j$) | Direct Mapped (Line = $j \pmod 8$) | 2-Way Set Associative (Set = $j \pmod 4$) | Fully Associative (LRU Replacement) |
| :---: | :--- | :--- | :--- |
| **0** | **MISS:** Line 0 $\leftarrow [0]$ | **MISS:** Set 0, Way 0 $\leftarrow [0]$ | **MISS:** Line 0 $\leftarrow [0]$ |
| **4** | **MISS:** Line 4 $\leftarrow [4]$ | **MISS:** Set 0, Way 1 $\leftarrow [4]$ | **MISS:** Line 1 $\leftarrow [4]$ |
| **8** | **MISS (Conflict):** Line 0 $\leftarrow [8]$ (evicts 0) | **MISS (Conflict):** Set 0 full! Evicts LRU [0] $\leftarrow [8]$ | **MISS:** Line 2 $\leftarrow [8]$ |
| **0** | **MISS (Conflict):** Line 0 $\leftarrow [0]$ (evicts 8) | **MISS (Conflict):** Set 0 full! Evicts LRU [4] $\leftarrow [0]$ | **HIT!** (Block 0 present in Line 0) |
| **4** | **HIT!** (Block 4 is still in Line 4) | **MISS (Conflict):** Set 0 full! Evicts LRU [8] $\leftarrow [4]$ | **HIT!** (Block 4 present in Line 1) |
| **8** | **MISS (Conflict):** Line 0 $\leftarrow [8]$ (evicts 0) | **MISS (Conflict):** Set 0 full! Evicts LRU [0] $\leftarrow [8]$ | **HIT!** (Block 8 present in Line 2) |
| **1** | **MISS:** Line 1 $\leftarrow [1]$ | **MISS:** Set 1, Way 0 $\leftarrow [1]$ | **MISS:** Line 3 $\leftarrow [1]$ |
| **2** | **MISS:** Line 2 $\leftarrow [2]$ | **MISS:** Set 2, Way 0 $\leftarrow [2]$ | **MISS:** Line 4 $\leftarrow [2]$ |

##### Quantitative Summary:
- **Direct Mapped:** $7\text{ Misses}, 1\text{ Hit} \implies \text{Hit Rate} = 12.5\%$. (Severely thrashed on Line 0 by blocks 0 and 8).
- **2-Way Set Associative:** $7\text{ Misses}, 1\text{ Hit} \implies \text{Hit Rate} = 12.5\%$. (Set 0 thrashed because 3 blocks {0, 4, 8} competed for 2 ways).
- **Fully Associative:** $5\text{ Misses}, 3\text{ Hits} \implies \text{Hit Rate} = 37.5\%$. (Zero conflict misses; all 3 repeated references {0, 4, 8} hit cleanly!).

---

#### Level 2 — Scaffolded Bug-Fix: Power-of-Two Stride Conflict Thrashing & Prime Hash Inversion

##### Defect Scenario
A scientific image processing filter operates on an array of structs representing pixels. The program allocates a hash map with $N = 2048$ buckets ($2^{11}$).
The target machine possesses an L1 data cache of $32\text{ KB}$ with $64\text{-byte}$ lines, organized as **4-Way Set Associative** ($128\text{ sets}$, $d = 7\text{ bits}$).
A software developer writes an image downsampling routine:

```c
// DEFECTIVE IMPLEMENTATION: POWER-OF-TWO STRIDE CONFLICT THRASHING
#define STRIDE 2048 // Exactly 2^11 elements!

void process_vertical_downsample(float* image_buffer, int rows, int cols) {
    float sum = 0.0f;
    for (int r = 0; r < rows; r++) {
        // Every iteration accesses address offset: r * STRIDE * sizeof(float)
        // Stride in bytes = 2048 * 4 bytes = 8192 bytes = 8 KB!
        sum += image_buffer[r * STRIDE];
    }
}
```

Despite the entire data set accessed in the loop totaling only $16\text{ KB}$ (which should easily fit inside the $32\text{ KB}$ L1 cache), profiling with `perf stat` reveals an L1 Data Cache Miss Rate of **$99.2\%$**!

##### Microarchitectural Diagnosis
1. Stride in Bytes = $8192\text{ bytes} = 2^{13}\text{ bytes}$.
2. Address bits for Set Index in the $32\text{ KB}$ 4-way cache ($128\text{ sets}$, $64\text{ B}$ lines):
   - Offset: Bits $A_5 - A_0$ ($6\text{ bits}$).
   - Set Index: Bits $A_{12} - A_6$ ($7\text{ bits}$).
3. Since every consecutive element's address jumps by $8192\text{ bytes} = 2^{13}$:
   $$\text{Address}_r = \text{Base} + r \cdot 2^{13}$$
   The lower 13 bits of the address ($A_{12} - A_0$) are **identical for every single access!**
4. Every single access maps to the **exact same Set Index** (Set $\lfloor \text{Base} / 64 \rfloor \pmod{128}$).
5. Because the cache is only 4-way set associative, that single set can only hold 4 lines. On iteration 5, it evicts iteration 1; on iteration 6, it evicts iteration 2!
6. The other 127 sets in the cache sit completely empty ($0\%$ utilized), while set $k$ suffers $100\%$ thrashing!

<details>
<summary><b>View Architectural Solution & Corrected Padding / Hash Transformation</b></summary>

```c
// ============================================================================
// CORRECTED IMPLEMENTATION: CACHE SET CONFLICT ELIMINATION
// ============================================================================
#include <stdio.h>
#include <stdlib.h>

// SOLUTION 1: PITCH PADDING (Break Power-of-Two Stride Alignment)
// By adding a small prime pad to the row allocation pitch, consecutive rows
// land in rotating, uniformly distributed cache sets!
#define PADDED_STRIDE (2048 + 3) // 2051 floats = 8204 bytes

void process_vertical_downsample_padded(float* image_buffer_padded, int rows) {
    float sum = 0.0f;
    for (int r = 0; r < rows; r++) {
        // Stride is now co-prime to the cache set modulus (128)!
        // Every consecutive access visits Set: (Set_prev + (8204 / 64)) % 128
        // 8204 / 64 = 128.1875 -> Rotates set index by 1 on every step!
        sum += image_buffer_padded[r * PADDED_STRIDE];
    }
}

// SOLUTION 2: HARDWARE-LEVEL XOR HASHING (Used in Modern CPU Uncore / L3 Slices)
// Many modern architectures (e.g., AMD Zen / Intel Skylake) XOR higher-order tag bits
// with lower-order index bits to randomize set mapping for power-of-two strides:
static inline uint32_t compute_xor_cache_set(uint64_t physical_address) {
    uint32_t line_addr = (uint32_t)(physical_address >> 6); // Discard 64B offset
    uint32_t lower_index = line_addr & 0x7F;                 // Standard 7-bit set index
    uint32_t higher_bits  = (line_addr >> 7) & 0x7F;        // Lower 7 bits of Tag
    return (lower_index ^ higher_bits) % 128;               // Permuted Set Index!
}
```

</details>

---

#### Level 3 — High-Scale System Design: Cycle-Accurate K-Way Set-Associative Cache Simulator in C++

Design a complete, modular, and configurable C++17 cache simulator modeling:
1. Arbitrary cache capacity, block size, and degree of associativity ($K$-Way).
2. Bit-level address field decoding (Tag, Set Index, Word Offset).
3. Tag matching, Valid bit verification, and true **Least Recently Used (LRU)** line replacement tracking.
4. Comprehensive statistical instrumentation (Compulsory vs Conflict Misses, Hit Rate, AMAT).

<details>
<summary><b>View Complete C++ K-Way Set-Associative Cache Simulator Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: CONFIGURABLE K-WAY SET-ASSOCIATIVE CACHE SIMULATOR
// Compile: g++ -std=c++17 -O3 cache_sim.cpp -o cache_sim
// ============================================================================

#include <iostream>
#include <vector>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <string>

struct CacheLine {
    bool valid = false;
    bool dirty = false;
    uint64_t tag = 0;
    uint64_t last_access_timestamp = 0; // For LRU replacement
};

class SetAssociativeCache {
private:
    size_t cache_size_bytes;
    size_t block_size_bytes;
    size_t ways;
    size_t num_sets;

    uint32_t offset_bits;
    uint32_t set_bits;
    uint32_t tag_bits;

    uint64_t global_timer = 0;
    std::vector<std::vector<CacheLine>> sets;

    // Statistics
    uint64_t total_accesses = 0;
    uint64_t hits = 0;
    uint64_t compulsory_misses = 0;
    uint64_t conflict_misses = 0;

public:
    SetAssociativeCache(size_t cache_bytes, size_t block_bytes, size_t k_ways)
        : cache_size_bytes(cache_bytes), block_size_bytes(block_bytes), ways(k_ways) {
        
        size_t total_lines = cache_size_bytes / block_size_bytes;
        num_sets = total_lines / ways;

        offset_bits = static_cast<uint32_t>(std::log2(block_size_bytes));
        set_bits    = static_cast<uint32_t>(std::log2(num_sets));
        tag_bits    = 64 - offset_bits - set_bits;

        sets.resize(num_sets, std::vector<CacheLine>(ways));
    }

    bool access(uint64_t address, bool is_write) {
        total_accesses++;
        global_timer++;

        // Address Field Extraction
        uint64_t offset_mask = (1ULL << offset_bits) - 1;
        uint64_t set_mask    = (1ULL << set_bits) - 1;

        uint64_t offset    = address & offset_mask;
        uint64_t set_index = (address >> offset_bits) & set_mask;
        uint64_t tag       = (address >> (offset_bits + set_bits));

        auto& current_set = sets[set_index];

        // 1. Tag Comparison (Parallel Search across K Ways)
        for (size_t w = 0; w < ways; w++) {
            if (current_set[w].valid && current_set[w].tag == tag) {
                // HIT!
                hits++;
                current_set[w].last_access_timestamp = global_timer;
                if (is_write) current_set[w].dirty = true;
                return true;
            }
        }

        // 2. MISS: Find empty way or evict LRU line
        int empty_way_idx = -1;
        size_t lru_way_idx = 0;
        uint64_t oldest_time = UINT64_MAX;

        for (size_t w = 0; w < ways; w++) {
            if (!current_set[w].valid) {
                empty_way_idx = static_cast<int>(w);
                break;
            }
            if (current_set[w].last_access_timestamp < oldest_time) {
                oldest_time = current_set[w].last_access_timestamp;
                lru_way_idx = w;
            }
        }

        if (empty_way_idx != -1) {
            // Cold / Compulsory Miss
            compulsory_misses++;
            current_set[empty_way_idx].valid = true;
            current_set[empty_way_idx].dirty = is_write;
            current_set[empty_way_idx].tag = tag;
            current_set[empty_way_idx].last_access_timestamp = global_timer;
        } else {
            // Conflict / Capacity Miss: Evict LRU line
            conflict_misses++;
            current_set[lru_way_idx].valid = true;
            current_set[lru_way_idx].dirty = is_write;
            current_set[lru_way_idx].tag = tag;
            current_set[lru_way_idx].last_access_timestamp = global_timer;
        }

        return false;
    }

    void print_telemetry() const {
        double hit_rate = (total_accesses > 0) ? (static_cast<double>(hits) / total_accesses) * 100.0 : 0.0;
        std::cout << "\n=======================================================\n";
        std::cout << "          CACHE SIMULATOR TELEMETRY REPORT             \n";
        std::cout << "=======================================================\n";
        std::cout << "Configuration: " << (cache_size_bytes / 1024) << " KB Cache, "
                  << block_size_bytes << " B Line, " << ways << "-Way Associative\n";
        std::cout << "Sets: " << num_sets << " | Tag Bits: " << tag_bits 
                  << " | Set Bits: " << set_bits << " | Offset Bits: " << offset_bits << "\n";
        std::cout << "-------------------------------------------------------\n";
        std::cout << "Total Memory Accesses : " << total_accesses << "\n";
        std::cout << "Total Cache Hits      : " << hits << " (" << std::fixed << std::setprecision(2) << hit_rate << "%)\n";
        std::cout << "Compulsory (Cold) Miss: " << compulsory_misses << "\n";
        std::cout << "Conflict/Capacity Miss: " << conflict_misses << "\n";
        std::cout << "=======================================================\n";
    }
};

int main() {
    // Simulate 32 KB 4-Way Set Associative Cache with 64-byte lines
    SetAssociativeCache cache(32 * 1024, 64, 4);

    // Sequential burst workload
    for (uint64_t addr = 0x1000; addr < 0x1000 + 4096; addr += 4) {
        cache.access(addr, false); // Read 4-byte words
    }

    // Re-access same range (Expect near 100% hits)
    for (uint64_t addr = 0x1000; addr < 0x1000 + 4096; addr += 4) {
        cache.access(addr, false);
    }

    cache.print_telemetry();
    return 0;
}
```

</details>

---

### 7. Reference Video Lecture

{{ media:why-cpu-cache-video }}

In this video, Professor Steve Furber (co-architect of the ARM processor) explains the physical engineering challenges of CPU caches, the memory wall, cache mapping, tag directories, and multi-level cache hierarchies.
