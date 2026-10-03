# Unit 4 — Cache Memory Principles, Mapping Functions & Coherency Architectures
## Lesson 3 — Cache Replacement Algorithms, Write Policies & Multicore Cache Coherency

### 1. Cache Line Replacement Algorithms: LRU, Tree-PLRU, FIFO, LFU & Random

In a Direct-Mapped cache, line replacement is trivial: because every main memory block maps to exactly one predetermined line, the incoming block unconditionally overwrites the resident block. However, in **Associative** and **$K$-Way Set-Associative** caches, when a cache miss occurs and all $K$ lines within the target set are already occupied with valid data, the cache controller must make an autonomous hardware decision: **Which resident block must be sacrificed and evicted to make room for the newly requested block?**

The objective of an eviction algorithm is to minimize future cache misses by predicting future memory reference patterns based on historical access telemetry.

```
+-----------------------------------------------------------------------------------------+
|                         CACHE LINE REPLACEMENT TAXONOMY                                 |
|                                                                                         |
|       +-------------------------------------------------------------------------+       |
|       | 1. LEAST RECENTLY USED (LRU):                                           |       |
|       | • Evicts the block unreferenced for the longest temporal duration.      |       |
|       | • Exploits Temporal Locality: Infrequently used data is evicted.        |       |
|       | • Implementation: True LRU (Matrix/Stack) vs. Tree-PLRU (Pseudo-LRU).   |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|       +-------------------------------------------------------------------------+       |
|       | 2. FIRST-IN, FIRST-OUT (FIFO):                                          |       |
|       | • Evicts the block resident in the set for the longest time.            |       |
|       | • Circular queue structure; ignores frequency or recency of hits.       |       |
|       | • Vulnerability: Can evict critical, heavily accessed loop constants!  |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|       +-------------------------------------------------------------------------+       |
|       | 3. LEAST FREQUENTLY USED (LFU):                                         |       |
|       | • Evicts the block with the lowest cumulative hit counter.              |       |
|       | • Vulnerability: Old initialization routines gain high counts and stay  |       |
|       |   resident forever ("Cache Pollution"). Requires aging/decay counters. |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|       +-------------------------------------------------------------------------+       |
|       | 4. RANDOM REPLACEMENT:                                                  |       |
|       | • Evicts a randomly selected candidate line among the K ways.           |       |
|       | • Zero state tracking bits; surprisingly effective in large sets (16-way)|      |
|       +-------------------------------------------------------------------------+       |
+-----------------------------------------------------------------------------------------+
```

#### Detailed Examination of True LRU vs. Tree-Pseudo-LRU (PLRU)

##### 1. True LRU Hardware Implementation
- For a 2-way set-associative cache ($K = 2$), LRU tracking requires only **1 bit per set**: a `USE` bit. When Way 0 is referenced, `USE = 1`; when Way 1 is referenced, `USE = 0`. On eviction, the way opposite to the `USE` bit is replaced.
- For $K > 2$ (e.g., 4-way, 8-way, 16-way), True LRU hardware complexity explodes exponentially:
  - An **Age Matrix (Triangular Matrix)** requires $\frac{K(K-1)}{2}$ flip-flops per set.
  - For $K = 4$: $\frac{4 \times 3}{2} = 6\text{ bits per set}$.
  - For $K = 8$: $\frac{8 \times 7}{2} = 28\text{ bits per set}$.
  - For $K = 16$: $\frac{16 \times 15}{2} = 120\text{ bits per set}$! Across a $32,768\text{-set}$ L3 cache, True LRU would consume nearly $500\text{ KB}$ of raw silicon state registers just to track line ages, while gate switching delays would lengthen hit cycle latency.

##### 2. Tree-Based Pseudo-LRU (Tree-PLRU)
To bypass this quadratic scaling, modern microprocessors (e.g., Intel Nehalem through Alder Lake, ARM Cortex-A78) implement **Tree-PLRU**, requiring only **$K - 1$ tracking bits per set** arranged as a binary decision tree:

```
                          SET ACCESSED: WAY 2
                          
                              [ Bit B0: 0 ]        (B0 points to Right subtree)
                                 /      \
                                /        \
                    [ Bit B1: 0 ]        [ Bit B2: 1 ] (B2 toggles to 0!)
                       /      \            /      \
                      /        \          /        \
                    Way 0    Way 1      Way 2    Way 3
```

- Each internal tree node is a single bit indicating which child branch was *less* recently accessed.
- On any access to a Way, the bits along the traversal path are toggled to point away from that Way.
- On eviction, the controller simply follows the arrows down the binary tree to find the pseudo-LRU candidate in $O(\log_2 K)$ gate delays with only 3 bits per set for 4-way, and 7 bits per set for 8-way!

{{ media:coa-cache-mesi-diagram }}

---

### 2. Memory Write Policies: Write-Through vs. Write-Back & Write Allocation

When the CPU datapath issues a **Memory Read**, cache behavior is straightforward: on a hit, read the cache; on a miss, fetch the block from DRAM.
However, when the CPU issues a **Memory Write (Store)**, fundamental architectural complications arise:
1. When data is modified in the cache, the corresponding copy residing in Semiconductor Main Memory (DRAM) becomes stale and out-of-date.
2. If multiple processor cores or Direct Memory Access (DMA) peripheral devices read from DRAM, they will read corrupted, stale data unless strict cache update policies are enforced.

#### 1. Write-Through with Write Buffers
- **Operational Rule:** Every write operation is written **simultaneously to both the Cache line and Main Memory**.
- **Architectural Mechanics:**
  - When the CPU executes a store instruction, the cache controller updates the cache line and immediately asserts a write command on the System Bus to update DRAM.
  - *Advantage:* Main memory is **always clean and 100% synchronized** with the cache. Replacement of an evicted line requires zero write-back cycles; the old line is simply overwritten.
  - *Disadvantage (The Store Bottleneck):* DRAM writes require $60\text{ to }100\text{ ns}$. If the CPU had to stall on every store instruction, performance would degrade catastrophically.
  - *Remedy (The Write Buffer):* Architects place a high-speed FIFO queue (typically 4 to 8 entries) called a **Write Buffer** between the cache and memory bus. The CPU deposits the written word and address into the write buffer in $1\text{ ns}$ and resumes execution immediately. The memory controller drains the write buffer to DRAM asynchronously in the background. If the buffer fills up during a write burst, the CPU must stall until an entry clears.

#### 2. Write-Back (Copy-Back) with Dirty Bits
- **Operational Rule:** Write updates are made **exclusively in the Cache**. Main memory is **NOT** updated at the time of the write.
- **Architectural Mechanics:**
  - Each cache line directory entry is augmented with a 1-bit hardware status flag: the **Dirty Bit (Modified Bit, $D$)**.
  - When a line is first fetched from DRAM, its dirty bit is cleared ($D = 0$).
  - When the CPU performs a write to the line, the data is modified in SRAM, and the hardware sets $D = 1$.
  - When a cache miss forces the eviction of a line:
    - If $D == 0$ (Clean): The block is discarded immediately with zero bus traffic.
    - If $D == 1$ (Dirty): The cache controller issues a burst write to flush the modified 64-byte block back to Main Memory before installing the new block.
  - *Advantage:* Slashes memory bus traffic by **$80\%\text{ to }90\%$**, because variables modified thousands of times inside inner loops generate zero external bus writes until final eviction.
  - *Disadvantage:* High controller complexity; main memory contains stale data; requires complex snooping protocols in multi-core systems.

#### Write Allocation Policies (Handling Write Misses)
What happens if the CPU performs a write to a memory address that is **NOT** currently resident in cache (a **Write Miss**)?

| Policy | Operational Sequence on Write Miss | Typical Pairing |
| :--- | :--- | :--- |
| **Write-Allocate (Fetch-on-Write)** | The target 64-byte block is fetched from Main Memory into the Cache, and the write is subsequently executed into the cached line. Exploits spatial locality (future writes/reads to nearby bytes hit in cache). | Universally paired with **Write-Back** caches. |
| **No-Write-Allocate (Write-Around)** | The cache is completely bypassed. The data word is written directly to Main Memory (or through the write buffer) without loading the surrounding block into cache. | Universally paired with **Write-Through** caches. |

---

### 3. Multi-Core Cache Coherence: The Snooping Bus & The MESI Protocol

In a modern Symmetric Multiprocessing (SMP) multi-core architecture, each execution core possesses its own private L1 and L2 caches, while sharing a common L3 cache and Main Memory via a shared coherent bus fabric:

```
+-----------------------------------------------------------------------------------------+
|                         THE MULTI-CORE COHERENCE DILEMMA                                |
|                                                                                         |
|       +-------------------+                     +-------------------+                   |
|       |    CORE 0 (CPU)   |                     |    CORE 1 (CPU)   |                   |
|       +-------------------+                     +-------------------+                   |
|                 |                                         |                             |
|                 v                                         v                             |
|       +-------------------+                     +-------------------+                   |
|       | L1 CACHE: [X = 42]|                     | L1 CACHE: [X = 42]|                   |
|       +-------------------+                     +-------------------+                   |
|                 |                                         |                             |
|   Core 0 writes: X = 99!                                  |                             |
|   L1 Cache 0: [X = 99] (Dirty)                  Core 1 reads: X ???                     |
|                 |                               Core 1 reads stale X = 42!              |
|                 v                               CATASTROPHIC MEMORY CORRUPTION!         |
|       ===============================================================                   |
|                       SHARED SYSTEM BUS (COHERENCE FABRIC)                              |
|       ===============================================================                   |
|                                       |                                                 |
|                                       v                                                 |
|                             +-------------------+                                       |
|                             | MAIN MEMORY (DRAM)|                                       |
|                             |     [X = 42]      |                                       |
|                             +-------------------+                                       |
+-----------------------------------------------------------------------------------------+
```

To guarantee that any read by any processor returns the most recently written data value (**Cache Coherence**), systems employ **Hardware Bus Snooping**. Every cache controller continuously monitors ("snoops") the broadcast bus lines for address transactions initiated by peer cores.

#### The 4-State MESI (Illinois) Protocol
The most widely implemented snooping protocol is the **MESI Protocol**. Every cache line directory tracks a 2-bit state machine with four discrete states:

```
+-----------------------------------------------------------------------------------------+
|                                  THE 4 MESI STATES                                      |
|                                                                                         |
|   1. [M] MODIFIED (Dirty & Exclusive):                                                  |
|      • The line is present ONLY in this private cache.                                  |
|      • Its contents have been modified and are DIRTY relative to Main Memory.           |
|      • The core has exclusive permission to read and write without generating bus cycles.|
|      • Must write back to memory when evicted or flushed.                               |
|                                                                                         |
|   2. [E] EXCLUSIVE (Clean & Exclusive):                                                 |
|      • The line is present ONLY in this private cache.                                  |
|      • Its contents are CLEAN (identical to Main Memory).                               |
|      • The core can transition silently to [M] on a local write with 0 bus broadcast!   |
|                                                                                         |
|   3. [S] SHARED (Clean & Shared):                                                       |
|      • The line may be present concurrently in multiple cores' private caches.          |
|      • Its contents are CLEAN (identical to Main Memory).                               |
|      • Writing to this line requires broadcasting an Invalidation signal (`BusUpgr`).   |
|                                                                                         |
|   4. [I] INVALID (Stale / Empty):                                                       |
|      • The line does not contain valid data.                                            |
|      • Any read or write by the local core triggers a Cache Miss.                       |
+-----------------------------------------------------------------------------------------+
```

#### Complete MESI State Transition Matrix

| Current State | Local Processor Event | Action Generated on Shared Bus | Next State | Detailed Coherence Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Invalid [I]** | Processor Read (`PrRd`) | Broadcasts `BusRd` | **[E]** or **[S]** | If other caches assert Shared line (`SHARED`), transition to **[S]**; if no peer holds block, transition to **[E]**. |
| **Invalid [I]** | Processor Write (`PrWr`) | Broadcasts `BusRdX` (Read with Intent to Modify) | **[M]** | Block fetched; peer caches invalidate their copies; local word written. |
| **Shared [S]** | Processor Read (`PrRd`) | *None (Silent)* | **[S]** | Local cache hit; zero bus traffic. |
| **Shared [S]** | Processor Write (`PrWr`) | Broadcasts `BusUpgr` (Invalidation Strobe) | **[M]** | Invalidates all peer copies without data transfer; local state becomes Modified. |
| **Exclusive [E]**| Processor Read (`PrRd`) | *None (Silent)* | **[E]** | Local cache hit; zero bus traffic. |
| **Exclusive [E]**| Processor Write (`PrWr`)| *None (Silent)* | **[M]** | **Crucial Optimization:** Transitions to Modified with zero bus traffic because line was exclusive! |
| **Modified [M]** | Processor Read/Write | *None (Silent)* | **[M]** | Local hit; data updated in SRAM; remains Modified. |
| **Any (Snoop)** | Peers assert `BusRd` on [M] | Core intervenes: Flushes data to bus | **[S]** | Snooping core supplies dirty data to requesting peer and memory; transitions to Shared. |
| **Any (Snoop)** | Peers assert `BusRdX` on [M]| Core flushes data to bus | **[I]** | Snooping core flushes block to memory and invalidates its own copy. |
| **Any (Snoop)** | Peers assert `BusRdX` or `BusUpgr` on [S] | *None* | **[I]** | Snooping core invalidates its local copy. |

---

### 4. Modern High-Throughput Cache Microarchitectures

To keep pace with superscalar out-of-order execution engines (capable of executing 4 to 8 instructions per clock cycle), modern cache controllers implement sophisticated latency-hiding mechanisms:

#### 1. Non-Blocking (Lockup-Free) Caches & MSHRs
In early microprocessors, a cache miss stalled the entire memory hierarchy until the block returned from DRAM (**Blocking Cache**).
Modern processors employ **Non-Blocking Caches** capable of servicing subsequent cache hits while an earlier miss is in-flight (**Hit-Under-Miss**), or even managing multiple simultaneous outstanding misses to different DRAM banks (**Miss-Under-Miss**).
- This is achieved via a dedicated hardware tracking structure: **Miss Status Holding Registers (MSHRs)**.
- Each MSHR entry records the missing physical block address, the requesting instruction tag/register, and target word offsets. When the DRAM burst arrives, the MSHR matches the incoming block and routes the operand directly to the awaiting reservation station.

#### 2. Hardware Stream & Stride Prefetchers
Rather than waiting reactively for the CPU to suffer a cache miss, on-chip **Hardware Prefetchers** monitor the sequence of memory addresses issued by the execution pipeline:
- **Stream Prefetcher:** Detects consecutive sequential cache line references ($L, L+1, L+2$) and proactively issues DRAM burst reads for lines $L+3$ and $L+4$ before the CPU even reaches those instructions.
- **Stride Prefetcher:** Detects constant address stride jumps (e.g., $A, A+128, A+256$) produced by struct array traversals, pre-loading target lines into the L2/L3 cache, completely eliminating compulsory misses!

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: MESI Multi-Core Trace Analysis

##### Problem Statement
Consider a dual-core processor (Core 0 and Core 1) sharing a coherent memory bus. Both cores possess private L1 caches implementing the MESI snooping protocol with Write-Back / Write-Allocate policies.
Initially, variable `X` (stored in memory block `B_X`) resides in Main Memory, and both cores' L1 caches have block `B_X` in the **[I] Invalid** state.

Trace the exact sequence of states, bus signals, and data transfers for the following chronological operations:
1. $t_1$: Core 0 reads `X` (`PrRd`).
2. $t_2$: Core 1 reads `X` (`PrRd`).
3. $t_3$: Core 0 writes `X = 99` (`PrWr`).
4. $t_4$: Core 1 reads `X` (`PrRd`).

##### Chronological Trace Table:

| Time | Core & Action | Bus Transaction Generated | Snooping Response by Peer | Core 0 State | Core 1 State | Memory State | Data Source |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Initial**| — | None | None | **[I]** | **[I]** | Clean ($X=0$) | — |
| **$t_1$** | **Core 0: Read X** | Core 0 broadcasts `BusRd(B_X)`. | Core 1 snoops `BusRd`, detects block is [I], asserts `SHARED = 0`. | **[E]** | **[I]** | Clean ($X=0$) | Main Memory supplies block. Core 0 enters **[E]** because peer does not have it. |
| **$t_2$** | **Core 1: Read X** | Core 1 broadcasts `BusRd(B_X)`. | Core 0 snoops `BusRd`, detects hit in [E], asserts `SHARED = 1`. | **[S]** | **[S]** | Clean ($X=0$) | Core 0 or Memory supplies block. Both cores transition to **[S]**. |
| **$t_3$** | **Core 0: Write X** | Core 0 broadcasts `BusUpgr(B_X)`. | Core 1 snoops `BusUpgr`, immediately invalidates its copy (**[S] $\to$ [I]**). | **[M]** | **[I]** | Stale ($X=0$) | Zero data transferred on bus! Core 0 updates local SRAM ($X=99$), sets dirty bit. |
| **$t_4$** | **Core 1: Read X** | Core 1 broadcasts `BusRd(B_X)` (Miss!). | Core 0 snoops `BusRd`, detects it holds block in **[M]**. Core 0 aborts DRAM read, flushes $X=99$ to bus, asserts `SHARED=1`. | **[S]** | **[S]** | Clean ($X=99$) | Core 0 intervenes and supplies dirty block to both Core 1 and Main Memory! |

---

#### Level 2 — Scaffolded Bug-Fix: Multi-Threaded False Sharing Catastrophe

##### Defect Scenario
A distributed server application tracks network metrics using a multi-threaded C++ program. Four worker threads running on four dedicated CPU cores continuously increment independent statistical packet counters:

```cpp
// DEFECTIVE IMPLEMENTATION: CATASTROPHIC FALSE SHARING
struct ThreadStats {
    uint64_t core0_packets; // 8 bytes
    uint64_t core1_packets; // 8 bytes
    uint64_t core2_packets; // 8 bytes
    uint64_t core3_packets; // 8 bytes
};

ThreadStats global_metrics; // Total size = 32 bytes (FITS IN A SINGLE 64B CACHE LINE!)

void worker_thread(int thread_id) {
    for (uint64_t i = 0; i < 100000000; i++) {
        if (thread_id == 0) global_metrics.core0_packets++;
        else if (thread_id == 1) global_metrics.core1_packets++;
        else if (thread_id == 2) global_metrics.core2_packets++;
        else if (thread_id == 3) global_metrics.core3_packets++;
    }
}
```

When tested on a 4-core processor, running 4 threads in parallel is **six times slower** than running a single thread on one core!

##### Microarchitectural Diagnosis
- In this architecture, Cache Lines are $64\text{ bytes}$ wide.
- All four variables (`core0_packets`, `core1_packets`, `core2_packets`, `core3_packets`) occupy a contiguous $32\text{-byte}$ block residing within the **exact same 64-byte physical cache line**.
- Even though the four threads never access each other's variables:
  - When Core 0 writes to `core0_packets`, its private L1 cache broadcasts an invalidation signal (`BusUpgr` / `BusRdX`).
  - This immediately forces the L1 caches of Core 1, Core 2, and Core 3 to **invalidate their entire copy of that 64-byte line**!
  - When Core 1 attempts to increment `core1_packets`, it suffers an immediate L1 cache miss, stalls its pipeline, and forces Core 0 to flush the line across the bus.
- This pathological thrashing is known as **False Sharing**: Cores battle for ownership of a shared cache line containing unrelated variables, turning a high-speed parallel computation into a serialized bus-bottlenecked ping-pong match.

<details>
<summary><b>View Architectural Solution & Hardware Cache-Line Alignment Fix</b></summary>

```cpp
// ============================================================================
// CORRECTED IMPLEMENTATION: HARDWARE CACHE-LINE PADDING & ALIGNMENT
// ============================================================================
#include <cstdint>
#include <thread>
#include <vector>

// Force each independent counter to reside on its own dedicated 64-byte cache line
// using the C++11 / C++17 alignas specifier:
struct alignas(64) CoherentCounter {
    uint64_t packet_count;
    // Explicit padding guarantees no other variable shares this 64-byte block
    uint8_t padding[64 - sizeof(uint64_t)];
};

struct OptimizedThreadStats {
    CoherentCounter counters[4];
};

OptimizedThreadStats global_metrics_optimized;

void worker_thread_optimized(int thread_id) {
    for (uint64_t i = 0; i < 100000000; i++) {
        // Each core writes exclusively to its own private 64-byte cache line!
        // State remains in [M] (Modified) with ZERO bus invalidations!
        global_metrics_optimized.counters[thread_id].packet_count++;
    }
}

int main() {
    std::vector<std::thread> workers;
    for (int i = 0; i < 4; i++) {
        workers.emplace_back(worker_thread_optimized, i);
    }
    for (auto& w : workers) {
        w.join();
    }
    return 0;
}
```

##### Performance Impact:
- **Defective Structure:** $\approx 420\text{ ms}$ execution time, billions of interconnect coherence flushes.
- **Optimized Structure:** $\approx 18\text{ ms}$ execution time (**$23.3\times$ speedup**; near-linear multi-core parallel scaling)!

</details>

---

#### Level 3 — High-Scale System Design: Cycle-Accurate MESI Cache Coherence Simulator in C++

Design a complete discrete-event multi-core cache coherence simulator modeling:
1. A multi-core Symmetric Multiprocessing (SMP) system with 2 independent cores.
2. Private L1 data caches implementing the complete 4-state MESI state machine.
3. A shared broadcast Snoop Bus that intercepts read/write transactions, handles remote invalidations, and models dirty line intervention flushes.

<details>
<summary><b>View Complete C++ MESI Protocol Simulator Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: MULTI-CORE MESI CACHE COHERENCE SIMULATOR
// Compile: g++ -std=c++17 -O3 mesi_sim.cpp -o mesi_sim
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cstdint>

enum class MESIState { MODIFIED, EXCLUSIVE, SHARED, INVALID };

std::string state_to_string(MESIState s) {
    switch (s) {
        case MESIState::MODIFIED:  return "MODIFIED [M]";
        case MESIState::EXCLUSIVE: return "EXCLUSIVE [E]";
        case MESIState::SHARED:    return "SHARED [S]";
        case MESIState::INVALID:   return "INVALID [I]";
    }
    return "UNKNOWN";
}

enum class BusCommand { NONE, BUS_RD, BUS_RDX, BUS_UPGR };

struct BusEvent {
    BusCommand cmd;
    uint32_t initiating_core;
    uint64_t block_address;
    bool shared_asserted = false;
    bool data_supplied_by_cache = false;
};

class CoherentCache {
public:
    uint32_t core_id;
    MESIState state = MESIState::INVALID;
    uint64_t cached_block = 0;
    uint32_t data_value = 0;

    CoherentCache(uint32_t id) : core_id(id) {}

    // Processor Core initiates Read
    void cpu_read(uint64_t block_addr, class CoherenceBus& bus);

    // Processor Core initiates Write
    void cpu_write(uint64_t block_addr, uint32_t new_val, class CoherenceBus& bus);

    // Snooping logic responding to bus broadcasts
    void snoop(BusEvent& event);
};

class CoherenceBus {
public:
    std::vector<CoherentCache*> caches;

    void broadcast(BusEvent& event) {
        // Peer caches snoop the broadcast
        for (auto* c : caches) {
            if (c->core_id != event.initiating_core) {
                c->snoop(event);
            }
        }
    }
};

void CoherentCache::snoop(BusEvent& event) {
    if (state == MESIState::INVALID || cached_block != event.block_address) {
        return; // Address does not match or line is invalid
    }

    switch (event.cmd) {
        case BusCommand::BUS_RD:
            event.shared_asserted = true; // Signal to initiator that another cache has block
            if (state == MESIState::MODIFIED) {
                std::cout << "    [SNOOP Core " << core_id << "] Holds block in MODIFIED! Intervening & flushing data to bus.\n";
                event.data_supplied_by_cache = true;
                state = MESIState::SHARED;
            } else if (state == MESIState::EXCLUSIVE) {
                state = MESIState::SHARED;
            }
            break;

        case BusCommand::BUS_RDX:
            if (state == MESIState::MODIFIED) {
                std::cout << "    [SNOOP Core " << core_id << "] Flushing modified data to bus before INVALIDATING.\n";
                event.data_supplied_by_cache = true;
            }
            std::cout << "    [SNOOP Core " << core_id << "] Invalidated by peer BusRdX!\n";
            state = MESIState::INVALID;
            break;

        case BusCommand::BUS_UPGR:
            std::cout << "    [SNOOP Core " << core_id << "] Invalidation received (BusUpgr). Transitioning SHARED -> INVALID.\n";
            state = MESIState::INVALID;
            break;

        default:
            break;
    }
}

void CoherentCache::cpu_read(uint64_t block_addr, CoherenceBus& bus) {
    std::cout << "\n>>> CORE " << core_id << " INITIATES CPU READ (Block 0x" << std::hex << block_addr << ")\n";

    if (state != MESIState::INVALID && cached_block == block_addr) {
        std::cout << "    -> CACHE HIT! State remains: " << state_to_string(state) << " | Val = " << std::dec << data_value << "\n";
        return;
    }

    // CACHE MISS: Broadcast BusRd
    BusEvent ev{BusCommand::BUS_RD, core_id, block_addr};
    bus.broadcast(ev);

    cached_block = block_addr;
    data_value = 100; // Simulated memory or flushed value

    if (ev.shared_asserted) {
        state = MESIState::SHARED;
    } else {
        state = MESIState::EXCLUSIVE;
    }
    std::cout << "    -> MISS SERVICED. New State: " << state_to_string(state) << "\n";
}

void CoherentCache::cpu_write(uint64_t block_addr, uint32_t new_val, CoherenceBus& bus) {
    std::cout << "\n>>> CORE " << core_id << " INITIATES CPU WRITE (Block 0x" << std::hex << block_addr 
              << ", NewVal=" << std::dec << new_val << ")\n";

    if (state == MESIState::MODIFIED && cached_block == block_addr) {
        data_value = new_val;
        std::cout << "    -> SILENT WRITE HIT (Already Modified). Zero bus traffic!\n";
        return;
    }

    if (state == MESIState::EXCLUSIVE && cached_block == block_addr) {
        data_value = new_val;
        state = MESIState::MODIFIED;
        std::cout << "    -> SILENT UPGRADE [E] -> [M]. Zero bus traffic required!\n";
        return;
    }

    if (state == MESIState::SHARED && cached_block == block_addr) {
        // Upgrade without data transfer
        BusEvent ev{BusCommand::BUS_UPGR, core_id, block_addr};
        bus.broadcast(ev);
        data_value = new_val;
        state = MESIState::MODIFIED;
        std::cout << "    -> BROADCAST BusUpgr. Transitioned [S] -> [M].\n";
        return;
    }

    // WRITE MISS: Issue BusRdX
    BusEvent ev{BusCommand::BUS_RDX, core_id, block_addr};
    bus.broadcast(ev);
    cached_block = block_addr;
    data_value = new_val;
    state = MESIState::MODIFIED;
    std::cout << "    -> WRITE MISS SERVICED. Transitioned -> [M].\n";
}

int main() {
    CoherenceBus bus;
    CoherentCache core0(0);
    CoherentCache core1(1);

    bus.caches.push_back(&core0);
    bus.caches.push_back(&core1);

    uint64_t shared_block = 0x7FFF0040;

    // Execute standard coherence sequence
    core0.cpu_read(shared_block, bus);       // Core 0 reads -> Exclusive [E]
    core1.cpu_read(shared_block, bus);       // Core 1 reads -> Both Shared [S]
    core0.cpu_write(shared_block, 99, bus);  // Core 0 writes -> Core 0 [M], Core 1 [I]
    core1.cpu_read(shared_block, bus);       // Core 1 reads -> Core 0 flushes, both [S]

    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:memory-storage-video }}

This video reviews the fundamental physical distinctions between semiconductor cache memory, dynamic RAM, and secondary storage, highlighting how storage controllers manage memory bandwidth and write buffering.
