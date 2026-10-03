# Unit 5 — Semiconductor Main Memory, Error Correction & Storage Architectures
## Lesson 3 — External Storage Subsystems, Magnetic Disk Timing & RAID Architectures

### 1. Magnetic Disk Physics & Geometric Data Layout: Platters, Tracks & Cylinders

Despite the proliferation of solid-state storage, Magnetic Hard Disk Drives (HDDs) remain the economic bedrock of global cloud datacenters, storing exabytes of cold and warm archival data at a fraction of the cost per terabyte of flash memory.

A magnetic disk is a high-precision electro-mechanical storage subsystem consisting of one or more rigid circular platters fabricated from an aluminum alloy or glass-ceramic substrate, coated on both sides with an ultra-thin ($10\text{ to }20\text{ nm}$) ferromagnetic recording film.

```
+-----------------------------------------------------------------------------------------+
|                              MAGNETIC DISK GEOMETRY                                     |
|                                                                                         |
|                    ACTUATOR ARM & READ/WRITE HEAD                                       |
|                    <======[HEAD]  (Flies < 10 nm above surface!)                        |
|                               |                                                         |
|                       +-------v-------------------------+                               |
|                      /         TRACK k (Outer Ring)      \                              |
|                     /   +-----------------------------+   \                             |
|                    /   /       TRACK 0 (Inner Ring)    \   \                            |
|                   |   |        +---------------+        |   |                           |
|                   |   |       /     SPINDLE     \       |   |                           |
|                   |   |      |   (7,200 - 15,000 |      |   |                           |
|                   |   |       \      RPM)       /       |   |                           |
|                   |   |        +---------------+        |   |                           |
|                    \   \                               /   /                            |
|                     \   +-----------------------------+   /                             |
|                      \         SECTOR (512B / 4KB)       /                              |
|                       +---------------------------------+                               |
|                                                                                         |
|       CYLINDER: The set of identically positioned tracks across ALL platter surfaces!   |
+-----------------------------------------------------------------------------------------+
```

#### Physical Data Formatting
1. **Tracks:** Data is recorded along concentric circular rings called **Tracks**. A modern 3.5-inch enterprise platter contains over $300,000$ tracks per inch (TPI).
2. **Cylinders:** A **Cylinder** is the collection of all vertically aligned tracks across all platter surfaces at a given radial distance from the spindle. The read/write heads for all surfaces are rigidly ganged to a single moving actuator arm; thus, switching between tracks within the same cylinder requires **zero mechanical actuator motion**.
3. **Sectors:** Each track is partitioned into discrete, individually addressable circular arcs called **Sectors**. Historically, sectors stored $512\text{ bytes}$ of payload; modern drives universally utilize **Advanced Format 4 KB ($4,096\text{ bytes}$)** sectors, reducing inter-sector formatting overhead.
4. **Inter-Sector Gaps & Synchronization Fields:** Adjacent sectors are separated by unrecorded physical gaps (`Gap 1`, `Gap 2`, `Gap 3`) to accommodate head motor speed tolerances. Each sector begins with a physical **Preamble / ID Field** containing a synchronization bit pattern, cylinder/head/sector numbers, and a Cyclic Redundancy Check (CRC) or Reed-Solomon / LDPC Error Correcting Code.

#### CAV vs. Multiple Zoned Recording (ZBR)
- **Constant Angular Velocity (CAV):**
  - In early hard drives, every track contained the exact same number of sectors and rotated at a constant angular speed ($r\text{ RPM}$).
  - *Inefficiency:* Because the circumference of an outer track ($2\pi R_{\text{outer}}$) is more than double that of an inner track ($2\pi R_{\text{inner}}$), data bits on outer tracks were spaced wastefully far apart, leaving massive recording density unexploited.
- **Multiple Zoned Recording (Zoned Bit Recording / ZBR):**
  - Modern drives partition the platter into 16 to 30 concentric radial **Zones**.
  - Outer zones contain significantly more sectors per track than inner zones.
  - The spindle continues to spin at constant RPM, but the read/write channel clock dynamically accelerates as the head moves outward, delivering **$50\%\text{ to }100\%$ higher data transfer throughput on outer tracks** compared to inner tracks!

{{ media:coa-storage-raid-diagram }}

---

### 2. Disk Access Performance Kinetics: Seek Time, Rotational Latency & Transfer Derivations

The total time required for an electro-mechanical hard drive to service an I/O read or write request ($T_a$) is the sum of three distinct physical latencies:

$$T_a = T_s + T_r + T_t$$

Where:
- $T_s$ = **Seek Time** (Mechanical actuator arm positioning).
- $T_r$ = **Rotational Latency** (Platter angular rotation).
- $T_t$ = **Transfer Time** (Data streaming rate from disk surface).

```
+-----------------------------------------------------------------------------------------+
|                             DISK ACCESS TIME TIMELINE                                   |
|                                                                                         |
|       |<------------------------------- Total Access Time T_a ----------------------->|
|       +-------------------------+-------------------------+---------------------------+
|       |     SEEK TIME (T_s)     | ROTATIONAL LATENCY (T_r)|    TRANSFER TIME (T_t)    |
|       |  Actuator moves arm to  | Platter rotates target  | Bits stream from rotating |
|       |     target cylinder     |  sector under the head  |    medium into buffer     |
|       |       (3 - 8 ms)        |       (2 - 4.17 ms)     |        (< 0.1 ms)         |
|       +-------------------------+-------------------------+---------------------------+
+-----------------------------------------------------------------------------------------+
```

#### Detailed Breakdown of Latency Components

##### 1. Seek Time ($T_s$)
- The time required for the voice-coil actuator to physically accelerate, coast, decelerate, and settle the read/write head assembly over the target cylinder.
- Full-stroke seek (traversing the entire platter width): $\sim 15\text{ to }20\text{ ms}$.
- Average seek time (across randomly distributed cylinders):
  $$T_{s,\text{avg}} \approx 3.0\text{ to }8.5\text{ ms}$$

##### 2. Rotational Latency ($T_r$)
- Once the head arrives on the target cylinder, it must wait for the target sector to rotate underneath it.
- In the best case, the sector arrives immediately ($T_{r,\text{min}} = 0$).
- In the worst case, the head just missed the sector and must wait for an entire $360^\circ$ rotation ($T_{r,\text{max}} = \frac{1}{r}$, where $r$ is rotational speed in revolutions per second).
- On average, the target sector is located halfway around the platter ($180^\circ$ rotation):
  $$T_{r,\text{avg}} = \frac{1}{2 \cdot r}$$

*Quantitative Rotational Latency by Spindle Speed:*
- At $5,400\text{ RPM}$ ($90\text{ rev/s}$): $T_{r,\text{avg}} = \frac{1}{2 \times 90} = 5.56\text{ ms}$.
- At $7,200\text{ RPM}$ ($120\text{ rev/s}$): $T_{r,\text{avg}} = \frac{1}{2 \times 120} = 4.17\text{ ms}$.
- At $10,000\text{ RPM}$ ($166.7\text{ rev/s}$): $T_{r,\text{avg}} = \frac{1}{2 \times 166.7} = 3.00\text{ ms}$.
- At $15,000\text{ RPM}$ ($250\text{ rev/s}$): $T_{r,\text{avg}} = \frac{1}{2 \times 250} = 2.00\text{ ms}$.

##### 3. Transfer Time ($T_t$)
- The time required to stream $b$ bytes of continuous data off the track:
  $$T_t = \frac{b}{r \cdot N}$$
  Where:
  - $b$ = Number of bytes to transfer.
  - $N$ = Total data bytes recorded on a single track.
  - $r$ = Rotational speed in revolutions/second.
  - The quantity $r \cdot N$ represents the instantaneous track streaming rate ($\text{Bytes/second}$).

##### Key Insight:
For small random I/O operations (e.g., reading a $4\text{ KB}$ database page):
- $T_s \approx 5.0\text{ ms}$, $T_r \approx 4.17\text{ ms}$, while $T_t \approx 0.02\text{ ms}$.
- Over **$99.8\%$ of total transaction latency is spent burning mechanical movement!**
$$\text{Random HDD IOPS} = \frac{1}{T_s + T_r} = \frac{1}{9.17\text{ ms}} \approx 109\text{ IOPS}$$
*(Compared to $500,000+$ IOPS on modern NVMe solid-state drives!).*

---

### 3. RAID Architectures: Redundant Array of Independent Disks

In 1988, David Patterson, Garth Gibson, and Randy Katz at UC Berkeley published their seminal paper introducing **RAID (Redundant Array of Inexpensive/Independent Disks)**.
RAID addresses the fundamental reliability and performance bottleneck of storage subsystems by organizing multiple physical disk drives into an aggregated, coherent array presented to the operating system as a single high-capacity logical volume.

```
+-----------------------------------------------------------------------------------------+
|                              CLASSICAL RAID ARCHITECTURES                               |
|                                                                                         |
|       RAID 0 (Striping)           RAID 1 (Mirroring)          RAID 5 (Distributed Parity)|
|   [Disk 0]     [Disk 1]       [Disk 0]     [Disk 1]       [Disk 0]  [Disk 1]  [Disk 2]  |
|   +-------+    +-------+      +-------+    +-------+      +-------+ +-------+ +-------+ |
|   | Strip0|    | Strip1|      | Strip0|    | Strip0|      | Strip0| | Strip1| |Parity0| |
|   +-------+    +-------+      +-------+    +-------+      +-------+ +-------+ +-------+ |
|   | Strip2|    | Strip3|      | Strip1|    | Strip1|      | Strip2| |Parity1| | Strip3| |
|   +-------+    +-------+      +-------+    +-------+      +-------+ +-------+ +-------+ |
|   | Strip4|    | Strip5|      | Strip2|    | Strip2|      |Parity2| | Strip4| | Strip5| |
|   +-------+    +-------+      +-------+    +-------+      +-------+ +-------+ +-------+ |
|   High Bandwidth, 0 Faults    100% Redundancy ($$$)       High Speed + Fault Tolerance  |
+-----------------------------------------------------------------------------------------+
```

#### Systematic Taxonomy of RAID Levels

| RAID Level | Structural Organization | Redundancy Mechanism | Storage Capacity Efficiency | Fault Tolerance | Read / Write Performance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RAID 0** | Block-level striping across $N$ disks. | **None (Zero Redundancy).** | $100\%$ ($N \times \text{Size}$) | **0 drives.** If 1 disk fails, entire volume is lost! | Max Read & Write throughput ($N \times$ single disk). |
| **RAID 1** | Mirroring (Duplicate identical data). | $100\%$ data duplication across pairs. | $50\%$ ($\frac{N}{2} \times \text{Size}$) | 1 drive per mirror pair. | $2\times$ Read speed; Write speed limited to slowest disk. |
| **RAID 2** | Bit-level striping with Hamming SEC-DED ECC disks. | Dedicated Hamming ECC disks ($3$ parity disks for 4 data disks). | Low ($\sim 57\%$) | 1 drive correction; 2 drive detection. | Obsolete; eclipsed by on-disk sector CRC/ECC. |
| **RAID 3** | Byte-level striping with dedicated parity disk. | Dedicated physical parity disk ($P = D_0 \oplus D_1 \oplus D_2$). | $\frac{N-1}{N}$ | 1 drive failure. | High sequential streaming; poor random IOPS. |
| **RAID 4** | Block-level striping with dedicated parity disk. | Dedicated physical parity disk. | $\frac{N-1}{N}$ | 1 drive failure. | Severe bottleneck on dedicated parity disk! |
| **RAID 5** | Block-level striping with **Distributed Parity**. | Parity blocks rotated evenly across ALL $N$ disks. | $\frac{N-1}{N}$ | **1 drive failure.** | High read IOPS; write penalty ($4$ I/O operations). |
| **RAID 6** | Block-level striping with **Dual Distributed Parity ($P+Q$)**. | Two independent parity syndromes (XOR + Reed-Solomon). | $\frac{N-2}{N}$ | **2 simultaneous drive failures!** | Enterprise standard; write penalty ($6$ I/O operations). |
| **RAID 10 (1+0)**| Mirrored sets that are then Striped. | Mirroring + Striping combined. | $50\%$ | Up to 1 drive per mirror sub-array. | Exceptional IOPS & zero write penalty! Database gold standard. |

#### The RAID 5 "Small Write Penalty" Formulation
When updating a single data block in a RAID 5 array, the controller cannot simply write the new data block. Because parity is shared:
$$P_{\text{new}} = D_{\text{old}} \oplus D_{\text{new}} \oplus P_{\text{old}}$$
To update a single block, the RAID controller must perform **4 physical I/O operations**:
1. **Read** the old data block ($D_{\text{old}}$).
2. **Read** the old parity block ($P_{\text{old}}$).
3. Compute the new parity: $P_{\text{new}} = D_{\text{old}} \oplus D_{\text{new}} \oplus P_{\text{old}}$.
4. **Write** the new data block ($D_{\text{new}}$).
5. **Write** the new parity block ($P_{\text{new}}$).

To mitigate this write penalty, enterprise hardware RAID controllers incorporate battery-backed or flash-backed Non-Volatile RAM (NVRAM) write caches.

---

### 4. Optical & Solid-State Evolution: CD/DVD/Blu-ray & Flash Translation Layer (FTL)

#### 1. Optical Storage Mechanics (CD-ROM, DVD & Blu-ray)
Optical storage utilizes focused semiconductor lasers to read physical microscopic indentations pressed into a reflective polycarbonate substrate:
- **Pits and Lands:** Data is stored as microscopic depressions (**Pits**) and flat surfaces (**Lands**) along a single continuous spiral track spanning $5.6\text{ km}$ on a compact disc.
- **Interference Sensing:** The laser reflects off the reflective aluminum layer. When the laser transitions from a pit to a land or from a land to a pit, the step height difference ($\lambda / 4$) induces destructive phase interference ($180^\circ$), dropping the reflected light intensity. A photodiode detects this transition, interpreting each edge transition as a binary **1** and absence of transition as a binary **0** (NRZI encoding).
- **Constant Linear Velocity (CLV):** Unlike magnetic CAV disks, optical CD-ROM drives vary their spindle rotational speed dynamically (spinning faster near the center, slower near the rim) to keep the linear track speed underneath the laser head strictly constant ($1.2\text{ to }1.4\text{ m/s}$).

##### Optical Density Evolution Across Generations
| Optical Format | Laser Wavelength ($\lambda$) | Numerical Aperture (NA) | Minimum Pit Length | Track Pitch | Storage Capacity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CD-ROM** | $780\text{ nm}$ (Infrared) | $0.45$ | $0.83\ \mu\text{m}$ | $1.6\ \mu\text{m}$ | $650\text{ to }700\text{ MB}$ |
| **DVD** | $650\text{ nm}$ (Red) | $0.60$ | $0.40\ \mu\text{m}$ | $0.74\ \mu\text{m}$ | $4.7\text{ GB}$ (Single layer) |
| **Blu-ray (BD)** | $405\text{ nm}$ (Blue-Violet) | $0.85$ | $0.15\ \mu\text{m}$ | $0.32\ \mu\text{m}$ | $25\text{ GB}$ (Single layer) |

#### 2. Solid-State Drives (SSDs) & The Flash Translation Layer (FTL)
While hard drives and optical discs rely on macroscopic moving parts, Solid-State Drives (SSDs) eliminate mechanics entirely, employing 3D TLC/QLC NAND Flash memory chips coordinated by a high-performance multi-core SSD Controller running a specialized operating system layer: the **Flash Translation Layer (FTL)**.
- **The Out-of-Place Write Rule:** In NAND flash, bits can be read and programmed in **Pages ($4\text{ to }16\text{ KB}$)**, but can only be erased in **Blocks ($2\text{ to }8\text{ MB}$)** containing hundreds of pages! An occupied page cannot be overwritten in-place.
- **FTL Responsibilities:**
  1. **Logical-to-Physical Address Translation:** Remaps OS logical block addresses (LBAs) to dynamically shifting physical flash pages.
  2. **Garbage Collection:** Consolidates valid pages from fragmented blocks into fresh blocks and executes block erases in the background.
  3. **Wear Leveling:** Distributes write/erase cycles uniformly across all physical blocks to prevent premature flash endurance burnout ($1,000\text{ to }3,000\text{ P/E cycles}$).

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Quantitative Disk Performance & Throughput Derivations

##### Problem Statement
An enterprise storage array features high-performance 3.5-inch SAS magnetic disks with the following specifications:
- Spindle Speed: $r = 15,000\text{ RPM}$ ($250\text{ rev/sec}$).
- Average Seek Time: $T_s = 3.5\text{ ms}$.
- Platter Geometry: 512 sectors per track, 4 KB Advanced Format sectors ($N = 512 \times 4,096\text{ bytes} = 2,097,152\text{ bytes} = 2\text{ MB}$ per track).

1. Calculate the average rotational latency ($T_r$).
2. Calculate the total time to access and transfer a single isolated random $4\text{ KB}$ sector ($T_a$), and compute the maximum random IOPS.
3. Calculate the time to read a contiguous sequential $10\text{ MB}$ video file spanning 5 consecutive tracks on the same cylinder.

##### Analytical Derivations

1. **Average Rotational Latency ($T_r$):**
   $$T_r = \frac{1}{2 \cdot r} = \frac{1}{2 \times 250\text{ rev/s}} = \frac{1}{500}\text{ s} = 0.002\text{ s} = 2.0\text{ ms}$$

2. **Single Random 4 KB Access:**
   - Transfer Time for $4\text{ KB}$ ($b = 4,096\text{ B}$):
     $$T_t = \frac{b}{r \cdot N} = \frac{4,096\text{ B}}{250 \times 2,097,152\text{ B/s}} = \frac{4,096}{524,288,000} \approx 7.81\ \mu\text{s} = 0.00781\text{ ms}$$
   - Total Access Latency:
     $$T_a = T_s + T_r + T_t = 3.5\text{ ms} + 2.0\text{ ms} + 0.0078\text{ ms} \approx 5.508\text{ ms}$$
   - Random 4 KB IOPS:
     $$\text{IOPS} = \frac{1}{T_a} = \frac{1}{0.005508\text{ s}} \approx 181.5\text{ IOPS}$$

3. **Sequential 10 MB File Read (5 Tracks on Same Cylinder):**
   - Head performs 1 initial seek to the cylinder: $T_s = 3.5\text{ ms}$.
   - Head waits for initial sector rotational alignment: $T_r = 2.0\text{ ms}$.
   - The head streams all 5 tracks sequentially. Since all tracks reside on the same cylinder, switching heads between platter surfaces requires **zero actuator seek motion** (only electronic head switch delay $t_{\text{head\_switch}} \approx 0.5\text{ ms}$).
   - Time to stream 5 complete rotations:
     $$T_{\text{stream}} = 5 \times \frac{1}{r} = 5 \times \frac{1}{250} = 5 \times 4.0\text{ ms} = 20.0\text{ ms}$$
   - Total Sequential Read Time:
     $$T_{\text{seq}} = T_s + T_r + T_{\text{stream}} = 3.5\text{ ms} + 2.0\text{ ms} + 20.0\text{ ms} = 25.5\text{ ms}$$
   - Effective Sequential Throughput:
     $$\text{Sequential Throughput} = \frac{10\text{ MB}}{0.0255\text{ s}} \approx 392.15\text{ MB/s!}$$

*(Demonstrating why sequential streaming is over $2,000\times$ faster than random disk IOPS!).*

---

#### Level 2 — Scaffolded Bug-Fix: The RAID 5 "Write Hole" & Battery-Backed NVRAM Fix

##### Defect Scenario
A financial stock exchange transaction engine writes financial ledgers to a software RAID 5 array composed of 4 disks.
During a heavy trading day, the server experiences a sudden catastrophic total power outage while servicing a write to Strip 2.
At the moment power died:
- The updated data block $D_{\text{new}}$ had completed writing to Disk 2.
- However, the updated parity block $P_{\text{new}}$ had **NOT yet written** to Disk 3!

When power is restored and the server boots up:
- The filesystem appears normal.
- Weeks later, Disk 1 suffers a physical drive head crash. The RAID controller attempts to reconstruct Disk 1's lost data using the equation:
  $$D_1 = D_0 \oplus D_2 \oplus P$$
- Because the parity block $P$ on Disk 3 was never updated with the new value of $D_2$, the reconstructed data on Disk 1 is mathematically corrupted, bankrupting customer ledger balances!

##### Microarchitectural Diagnosis
This vulnerability is the classical **RAID 5 / RAID 6 Write Hole**. Updating data and parity across separate physical disks is a multi-step, non-atomic transaction. If an asynchronous power loss or kernel panic strikes between the data write and parity write, the parity stripe becomes inconsistent with the data stripe. A subsequent drive failure results in silent, unrecoverable data reconstruction corruption.

<details>
<summary><b>View Architectural Solution & Journaling / NVRAM Commit Protocol</b></summary>

```c
// ============================================================================
// HARDWARE SIMULATION: ATOMIC RAID 5 WRITE-AHEAD INTENT JOURNAL
// ============================================================================
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define SECTOR_SIZE 4096

typedef struct {
    uint64_t stripe_id;
    uint32_t data_disk_idx;
    uint32_t parity_disk_idx;
    uint8_t  old_data_xor_new[SECTOR_SIZE];
    bool     committed_to_nvram;
} RAIDWriteJournalEntry;

// Non-Volatile Battery-Backed / Supercapacitor SRAM Journal
RAIDWriteJournalEntry nvram_journal;

void execute_atomic_raid5_write(uint64_t stripe, int disk_idx, int parity_idx, 
                                uint8_t* old_data, uint8_t* new_data, uint8_t* old_parity) {
    
    // STEP 1: Compute Parity Delta in Controller RAM
    uint8_t new_parity[SECTOR_SIZE];
    for (int i = 0; i < SECTOR_SIZE; i++) {
        uint8_t delta = old_data[i] ^ new_data[i];
        new_parity[i] = old_parity[i] ^ delta;
        nvram_journal.old_data_xor_new[i] = delta;
    }

    // STEP 2: ATOMIC WRITE-AHEAD JOURNAL COMMIT TO NON-VOLATILE RAM
    nvram_journal.stripe_id = stripe;
    nvram_journal.data_disk_idx = disk_idx;
    nvram_journal.parity_disk_idx = parity_idx;
    nvram_journal.committed_to_nvram = true;
    flush_to_nvram_hardware(); // Hardware barrier: guaranteed persistent!

    // STEP 3: Issue Physical Disk Writes
    write_physical_disk(disk_idx, new_data);
    write_physical_disk(parity_idx, new_parity);

    // STEP 4: Clear Journal Entry
    nvram_journal.committed_to_nvram = false;
}

// Crash Recovery Routine (Executed during Server Reboot after Power Failure)
void recover_raid_write_hole_on_boot() {
    if (nvram_journal.committed_to_nvram) {
        printf(">>> WARNING: Incomplete RAID 5 Write detected after power crash! <<<\n");
        printf(">>> Replaying Journal for Stripe %llu to eliminate Write Hole! <<<\n", nvram_journal.stripe_id);
        
        // Re-read current parity and re-apply delta to restore absolute consistency
        uint8_t parity[SECTOR_SIZE];
        read_physical_disk(nvram_journal.parity_disk_idx, parity);
        for (int i = 0; i < SECTOR_SIZE; i++) {
            parity[i] ^= nvram_journal.old_data_xor_new[i];
        }
        write_physical_disk(nvram_journal.parity_disk_idx, parity);
        nvram_journal.committed_to_nvram = false;
        printf(">>> Parity Stripe Re-synchronized Flawlessly! Zero data loss! <<<\n");
    }
}
```

</details>

---

#### Level 3 — High-Scale System Design: Cycle-Accurate RAID Controller Simulator in C++

Design a complete C++17 Software RAID Subsystem modeling:
1. **RAID 0 (Striping), RAID 1 (Mirroring), and RAID 5 (Distributed Parity)**.
2. Bitwise XOR parity generation and stripe rotation across 4 virtual disk drives.
3. **Degraded Mode Simulation & Reconstruction:** Disables Disk 2, executes read transactions in degraded mode via on-the-fly XOR reconstruction, installs a virtual hot-spare disk, and rebuilds the entire volume.

<details>
<summary><b>View Complete C++ RAID Subsystem Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: MULTI-LEVEL SOFTWARE RAID CONTROLLER SIMULATOR
// Compile: g++ -std=c++17 -O3 raid_simulator.cpp -o raid_simulator
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cstdint>
#include <cassert>

class VirtualDisk {
public:
    uint32_t disk_id;
    bool is_online = true;
    std::vector<uint32_t> storage;

    VirtualDisk(uint32_t id, size_t capacity_words)
        : disk_id(id), storage(capacity_words, 0) {}

    bool write(size_t block_idx, uint32_t word) {
        if (!is_online) return false;
        if (block_idx < storage.size()) {
            storage[block_idx] = word;
            return true;
        }
        return false;
    }

    bool read(size_t block_idx, uint32_t& out_word) const {
        if (!is_online) return false;
        if (block_idx < storage.size()) {
            out_word = storage[block_idx];
            return true;
        }
        return false;
    }
};

class RAID5Controller {
private:
    std::vector<VirtualDisk> disks;
    size_t num_disks;
    size_t disk_capacity;

public:
    RAID5Controller(size_t n_disks, size_t capacity)
        : num_disks(n_disks), disk_capacity(capacity) {
        assert(n_disks >= 3);
        for (size_t i = 0; i < n_disks; i++) {
            disks.emplace_back(static_cast<uint32_t>(i), capacity);
        }
    }

    void write_stripe(size_t stripe_idx, const std::vector<uint32_t>& data_blocks) {
        assert(data_blocks.size() == num_disks - 1);

        // Rotating distributed parity disk index: Parity Disk = (num_disks - 1) - (stripe_idx % num_disks)
        size_t parity_disk = (num_disks - 1 - (stripe_idx % num_disks));

        uint32_t parity_word = 0;
        size_t data_cursor = 0;

        for (size_t d = 0; d < num_disks; d++) {
            if (d == parity_disk) continue;
            uint32_t val = data_blocks[data_cursor++];
            disks[d].write(stripe_idx, val);
            parity_word ^= val;
        }

        // Write calculated parity
        disks[parity_disk].write(stripe_idx, parity_word);
    }

    uint32_t read_logical_block(size_t stripe_idx, size_t data_offset_in_stripe) {
        size_t parity_disk = (num_disks - 1 - (stripe_idx % num_disks));

        // Locate physical disk corresponding to this data block
        size_t target_disk = 0;
        size_t cursor = 0;
        for (size_t d = 0; d < num_disks; d++) {
            if (d == parity_disk) continue;
            if (cursor == data_offset_in_stripe) {
                target_disk = d;
                break;
            }
            cursor++;
        }

        uint32_t result = 0;
        if (disks[target_disk].read(stripe_idx, result)) {
            // Normal Read Hit
            return result;
        }

        // DEGRADED MODE RECONSTRUCTION: Target disk is DEAD!
        std::cout << "  [DEGRADED MODE] Disk " << target_disk << " is OFFLINE! Reconstructing via XOR parity...\n";
        uint32_t reconstructed = 0;
        for (size_t d = 0; d < num_disks; d++) {
            if (d == target_disk) continue;
            uint32_t peer_word = 0;
            bool ok = disks[d].read(stripe_idx, peer_word);
            assert(ok && "Double disk failure! Array unrecoverable!");
            reconstructed ^= peer_word;
        }
        return reconstructed;
    }

    void simulate_disk_crash(size_t disk_id) {
        std::cout << "\n>>> SIMULATING HARDWARE CRASH ON DISK " << disk_id << "! <<<\n";
        disks[disk_id].is_online = false;
    }

    void rebuild_hot_spare(size_t failed_disk_id) {
        std::cout << "\n>>> HOT-SPARE INSERTED. REBUILDING DISK " << failed_disk_id << "... <<<\n";
        disks[failed_disk_id].is_online = true;

        for (size_t stripe = 0; stripe < disk_capacity; stripe++) {
            uint32_t xor_sum = 0;
            for (size_t d = 0; d < num_disks; d++) {
                if (d == failed_disk_id) continue;
                uint32_t val = 0;
                disks[d].read(stripe, val);
                xor_sum ^= val;
            }
            disks[failed_disk_id].write(stripe, xor_sum);
        }
        std::cout << ">>> REBUILD 100% COMPLETE! ARRAY IS HEALTHY AND REDUNDANT! <<<\n";
    }
};

int main() {
    std::cout << "=======================================================\n";
    std::cout << "        RAID 5 DISTRIBUTED PARITY SIMULATOR            \n";
    std::cout << "=======================================================\n";

    RAID5Controller raid(4, 1024); // 4 Disks (3 Data + 1 Parity per stripe)

    // Stripe 0: Data = [0x1111, 0x2222, 0x3333]
    std::vector<uint32_t> payload = {0x1111, 0x2222, 0x3333};
    raid.write_stripe(0, payload);

    std::cout << "Read Data Block 1 (Stripe 0, Offset 1): 0x" 
              << std::hex << raid.read_logical_block(0, 1) << " (Healthy)\n";

    // Simulate Drive 1 catastrophic head crash
    raid.simulate_disk_crash(1);

    // Read Data Block 1 in Degraded Mode (On-the-fly parity reconstruction)
    uint32_t recovered = raid.read_logical_block(0, 1);
    std::cout << "Recovered Data Word: 0x" << std::hex << recovered 
              << (recovered == 0x2222 ? " (SUCCESSFUL DEGRADED RECONSTRUCTION)" : " (CORRUPT)") << "\n";

    // Rebuild array onto replacement spare drive
    raid.rebuild_hot_spare(1);

    std::cout << "Post-Rebuild Read: 0x" << std::hex << raid.read_logical_block(0, 1) << " (Flawless)\n";
    std::cout << "=======================================================\n";
    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:raid-storage-video }}

In this video by Linus Tech Tips, the core trade-offs between striping (RAID 0), mirroring (RAID 1), parity arrays (RAID 5/6), and nested arrays (RAID 10) are demonstrated in hardware.
