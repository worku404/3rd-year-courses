# Unit 1 — Introduction to Computer Organization, Architecture & Top-Level Structure
## Lesson 2 — The Von Neumann Stored-Program Model, Top-Level Structure & Functional Operations

### 1. The Stored-Program Concept & The Von Neumann Architecture

Prior to 1945, the earliest electronic calculating machines—such as the ENIAC (Electronic Numerical Integrator and Computer)—were **fixed-program computers**. While capable of executing arithmetic at electronic speeds, "programming" the ENIAC required teams of engineers to physically re-route hundreds of wire patch cables, throw manual multi-pole rotary switches, and reconstruct hardware circuit paths. Changing a computational program required hours or days of physical labor.

In June 1945, mathematician and physicist **John von Neumann** published the groundbreaking treatise *First Draft of a Report on the EDVAC*. In this document, von Neumann, alongside J. Presper Eckert and John Mauchly, introduced the **Stored-Program Concept**, establishing the architectural blueprint that remains the foundation of virtually every general-purpose computer manufactured today.

```
+-----------------------------------------------------------------------------------+
|                       THE VON NEUMANN ARCHITECTURAL MODEL                         |
|                                                                                   |
|                   +----------------------------------+                            |
|                   |   CENTRAL PROCESSING UNIT (CPU)  |                            |
|                   |  +------------+  +------------+  |                            |
|                   |  |Control Unit|  |    ALU     |  |                            |
|                   |  +------------+  +------------+  |                            |
|                   |  +----------------------------+  |                            |
|                   |  | Internal CPU Registers     |  |                            |
|                   |  +----------------------------+  |                            |
|                   +-----------------+----------------+                            |
|                                     |                                             |
|           ==========================v============================                 |
|           SYSTEM BUS (Control Bus, Address Bus, Data Bus)                         |
|           ==========================+============================                 |
|                                     |                                             |
|                   +-----------------+----------------+                            |
|                   |                                  |                            |
|          +--------v---------+              +---------v--------+                   |
|          |   MAIN MEMORY    |              |   INPUT/OUTPUT   |                   |
|          | (Instructions &  |              |    SUBSYSTEM     |                   |
|          |   Data Unified)  |              | (Peripherals)    |                   |
|          +------------------+              +------------------+                   |
+-----------------------------------------------------------------------------------+
```

{{ media:coa-von-neumann-diagram }}

#### The Three Core Principles of the Von Neumann Architecture
1. **Unified Memory for Code and Data:** Instructions (executable machine code) and data (operands, variables, buffers) are stored simultaneously in the same read-write memory space.
2. **Word-Addressable Memory Abstraction:** Memory consists of a sequence of numbered storage locations (addresses). The hardware makes no intrinsic distinction between an instruction and a data word; the meaning of a bit pattern is determined solely by the context in which the CPU references it.
3. **Sequential Execution Control:** Instructions execute sequentially from low memory addresses to high memory addresses, guided by an internal pointer (the **Program Counter**). Execution sequence deviates from linear ordering only when an explicit control-transfer instruction (jump, branch, call) alters the Program Counter.

#### Von Neumann vs. Harvard Architecture
The primary structural alternative to the Von Neumann model is the **Harvard Architecture**:

| Architectural Dimension | Classical Von Neumann Architecture | Classical Harvard Architecture |
| :--- | :--- | :--- |
| **Physical Memory** | Unified: Instructions and data share the same RAM | Divided: Separate physical instruction RAM & data RAM |
| **Bus Topology** | Single shared bus for instructions and data | Two independent, simultaneous buses |
| **Simultaneous Access** | Impossible: CPU cannot fetch an instruction and read/write data in the same clock cycle | Permitted: Instruction fetch and data read/write occur concurrently |
| **Hardware Complexity**| Low: Simpler memory controller and pin count | High: Twice the memory address/data pins and controllers |
| **Modern Application** | General-purpose microprocessors (x86, ARM, RISC-V) | Digital Signal Processors (DSPs), Microcontrollers (AVR) |

*The Modern Modified Harvard Synthesis:* Modern high-performance processors adopt a **Modified Harvard Architecture**. Externally, main memory (DRAM) is unified (Von Neumann model), presenting a single address space to the operating system. Internally on the processor silicon die, the Level 1 cache is split into a **dedicated L1 Instruction Cache (L1-I)** and a **dedicated L1 Data Cache (L1-D)** (Harvard model), allowing the execution pipeline to fetch new instructions and perform load/store data accesses simultaneously without structural bus hazards.

---

### 2. Top-Level Computer Structure & The System Bus

At the highest structural level, a computer system consists of four major operational components interconnected by the **System Bus**:

#### The Four Structural Pillars
1. **Central Processing Unit (CPU):** The supervisory and arithmetic engine. Interprets instructions, performs mathematical and logical evaluations, controls datapath routing, and synchronizes system timing.
2. **Main Memory (Primary Storage):** High-speed semiconductor storage that holds active programs and runtime datasets. Organized as a linear array of $M$ addressable bytes, where each byte possesses a unique physical address ranging from $0$ to $M - 1$.
3. **Input/Output (I/O) Modules:** Dedicated hardware controllers that bridge the high-speed internal bus with external peripheral devices (NVMe drives, network interfaces, graphics cards, human input devices). I/O modules contain internal data registers, control/status registers, and address decoding logic.
4. **System Interconnection (The System Bus):** A set of parallel physical conductors connecting the CPU, Memory, and I/O modules.

```
+-----------------------------------------------------------------------------------+
|                        SYSTEM BUS FUNCTIONAL ANATOMY                              |
|                                                                                   |
|  [ CPU ]                 [ MEMORY ]                 [ I/O MODULE ]                |
|    |                         |                            |                       |
|    |==== CONTROL LINES ===================================| (Read/Write, Clock)   |
|    |                                                      |                       |
|    |---> ADDRESS LINES ==================================>| (Uni-directional CPU) |
|    |                                                      |                       |
|    |<==> DATA LINES <====================================>| (Bi-directional Data) |
+-----------------------------------------------------------------------------------+
```

#### Detailed Bus Line Taxonomy

##### 1. Control Bus (Signaling & Synchronization)
Transmits command and timing signals that regulate access to the data and address lines:
- **Memory Read (`MEMR`) / Memory Write (`MEMW`):** Signals whether the addressed memory location should drive data onto the bus or latch data from the bus.
- **I/O Read (`IOR`) / I/O Write (`IOW`):** Directs an addressed I/O port to read or write data.
- **Transfer Acknowledge (`READY` / `ACK`):** Indicates that data has been successfully placed on or accepted from the data bus.
- **Bus Request (`BREQ`) / Bus Grant (`BGNT`):** Governs bus mastership arbitration.
- **Interrupt Request (`IRQ`):** Signaled by I/O modules to notify the CPU of pending hardware events.
- **System Clock (`CLK`) & Reset (`RST`):** Synchronizes operations across all bus interface units.

##### 2. Address Bus (Memory Location Targeting)
A unidirectional set of lines driven primarily by the CPU (or a DMA controller). It specifies the source or destination physical memory address or I/O port identifier.
- **Address Space Capacity Formula:** An address bus of width $k$ bits can uniquely address $2^k$ distinct memory locations:
$$\text{Addressable Space} = 2^k \text{ words (or bytes)}$$
- *Engineering Example:* A 32-bit address bus can address $2^{32} = 4,294,967,296 \text{ bytes} = 4 \text{ GiB}$. A 64-bit address bus can theoretically address $2^{64} = 16 \text{ Exabytes} = 18.4 \times 10^{18} \text{ bytes}$.

##### 3. Data Bus (Information Transfer)
A bidirectional set of lines that transports the actual operands, machine instructions, and status values between modules.
- **Data Bus Width & Bandwidth:** The width of the data bus (typically 32, 64, or 128 bits in modern architectures) dictates the number of bits the system can transfer in a single bus cycle.
$$\text{Theoretical Bus Bandwidth} = \text{Bus Width (bytes)} \times \text{Bus Clock Frequency (Hz)}$$
- *Engineering Example:* A 64-bit (8-byte) DDR4 memory channel operating at a transfer rate of 3,200 MT/s provides a peak throughput of:
$$\text{Throughput} = 8 \text{ bytes} \times 3,200 \times 10^6 \text{ transfers/sec} = 25.6 \text{ GB/s}$$

---

### 3. The Four Fundamental Computer Functions

Regardless of whether a machine is an embedded automotive microcontroller or a multi-rack supercomputer, all computing activities decompose into four primary functions:

```
                      +-----------------------------+
                      |       DATA PROCESSING       |
                      |       (ALU Operations)      |
                      +--------------+--------------+
                                     ^
                                     |
               +---------------------+---------------------+
               |                                           |
               v                                           v
+--------------+--------------+             +--------------+--------------+
|         DATA STORAGE        |             |        DATA MOVEMENT        |
|    (RAM, Disks, Registers)  |             |      (I/O, Network Comm)    |
+--------------+--------------+             +--------------+--------------+
               ^                                           ^
               |                                           |
               +---------------------+---------------------+
                                     |
                      +--------------+--------------+
                      |           CONTROL           |
                      |    (Sequencing & Timing)    |
                      +-----------------------------+
```

#### The Four Functional Operational Pathways
1. **Data Movement (Storage to I/O):** Transferring data between internal memory and the external world without transformation. *Example:* An NVMe SSD reading a file into RAM, or a network interface controller (NIC) transmitting a buffered packet over Ethernet.
2. **Data Storage & Processing (Internal Transformation):** Loading data from storage into CPU registers, executing an arithmetic/logical transformation, and storing the result back to storage. *Example:* Incrementing a counter in an in-memory database record.
3. **Data Movement with Processing to Storage:** Receiving raw external data from an I/O device, transforming or parsing it, and committing the structured output to storage. *Example:* An optical sensor streaming raw camera frames to the CPU, which performs JPEG compression and saves the image to an SSD.
4. **Data Movement with Processing to Movement:** Streaming data from an external input, transforming it in real time, and immediately dispatching it to an external output without persistent storage. *Example:* A real-time digital audio processor sampling sound from a microphone, applying noise-cancellation filters, and driving the speaker output.

---

### 4. The Von Neumann Bottleneck: Physics, Impact & Modern Remedies

#### The Physical Nature of the Bottleneck
In a pure Von Neumann architecture, CPU throughput is fundamentally constrained by the **Von Neumann Bottleneck**: because instructions and data must traverse the identical physical bus infrastructure, the CPU cannot read an instruction and read/write data simultaneously.

Over the past four decades, semiconductor technological progress exhibited a severe divergence known as the **Processor-Memory Performance Gap (The Memory Wall)**:
- **CPU Speed:** Scaled historically at approximately **50% per year** due to pipelining, superscalar execution, and frequency scaling.
- **DRAM Access Latency:** Improved at merely **7% per year**, governed by the analog RC time constants required to charge microscopic capacitive bitcells across silicon arrays.

```
Relative Performance (Log Scale)
10000 |                                              /-- Processor Performance (~50%/yr)
 1000 |                                         /---/
  100 |                                    /---/
   10 |                               /---/
    1 |--------------------------/---------------------- DRAM Speed (~7%/yr)
      +-------------------------------------------------> Time (1980 to Present)
                          ^
                          | THE GROWING MEMORY WALL GAP
```

#### Architectural Consequences
While a modern CPU arithmetic unit can execute an integer `ADD` instruction in **0.25 nanoseconds** (1 clock cycle at 4 GHz), reading a cache-missed operand from external DDR5 main memory takes **60 to 80 nanoseconds** (250 to 320 clock cycles). Without architectural remedies, the CPU would spend over 99% of its operational lifetime stalled, burning idle power while waiting for memory bus transactions.

#### Modern Architectural Remedies
Computer architects have developed sophisticated techniques to mitigate the Von Neumann bottleneck:
1. **Hierarchical Multi-Level SRAM Caches:** Placing small, ultra-fast static RAM (SRAM) memories directly on the processor die. A modern L1 cache responds in 1 nanosecond (4 cycles), L2 in 3–4 nanoseconds (12–14 cycles), and L3 in 10–12 nanoseconds (40 cycles), satisfying over 95% of all memory requests without accessing DRAM.
2. **Hardware Data Prefetchers:** Silicon state machines that monitor memory access streams. If the CPU iterates through a sequential array, the prefetcher predicts future memory lines and pulls them from DRAM into L2/L1 cache before the CPU explicitly requests them.
3. **Out-of-Order (OoO) Speculative Execution:** When an instruction stalls on a memory read, the CPU's reservation stations locate subsequent independent instructions in the instruction window and execute them out of order, hiding memory latency behind useful computation.
4. **Wide Vector Units (SIMD):** Intel AVX-512 and ARM SVE process 512 bits of data simultaneously with a single instruction, amortizing the instruction-fetch bus overhead across 16 parallel 32-bit arithmetic operations.

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Bus Capacity & Bandwidth Calculations
A 3rd-year computer engineering team is designing an industrial embedded processor with a 24-bit physical address bus and a 32-bit bidirectional data bus operating at a synchronous bus clock frequency of 133 MHz. Each standard memory read cycle requires 2 bus clock periods.

##### Architectural Calculations:
1. **Maximum Directly Addressable Physical Memory:**
   $$\text{Addressable Locations} = 2^{24} = 16,777,216 \text{ addresses}$$
   Assuming byte-addressable memory:
   $$\text{Max Capacity} = 16 \text{ Megabytes (MiB)}$$
2. **Maximum Data Transferred per Bus Cycle:**
   $$\text{Width} = 32 \text{ bits} = 4 \text{ bytes per transaction}$$
3. **Peak Theoretical Bus Bandwidth (Continuous Burst):**
   $$\text{Bandwidth}_{\text{peak}} = \text{Bus Width} \times \text{Frequency} = 4 \text{ bytes} \times 133.33 \times 10^6 \text{ Hz} = 533.33 \text{ MB/s}$$
4. **Actual Sustained Memory Bandwidth (2 clocks per 4-byte transfer):**
   $$\text{Cycle Time} = \frac{2}{133.33 \times 10^6} = 15 \text{ nanoseconds}$$
   $$\text{Sustained Throughput} = \frac{4 \text{ bytes}}{15 \times 10^{-9} \text{ sec}} = 266.67 \text{ MB/s}$$

---

#### Level 2 — Scaffolded Bug-Fix: Memory-Mapped I/O (MMIO) Caching Hazard
In a high-reliability aerospace controller, a software driver polls an external radar telemetry receiver using **Memory-Mapped I/O (MMIO)** at physical address `0xFFFF_0100`. The hardware receiver writes new target coordinates into this register when data arrives and sets bit 0 of the status byte.

The driver loop below hangs in an infinite loop, freezing the control system.

##### The Broken Code:
```c
// BROKEN DRIVER: Polling Memory-Mapped I/O Status Register
#include <stdint.h>
#include <stdbool.h>

#define RADAR_STATUS_REG  ((uint32_t*)0xFFFF0100)
#define RADAR_DATA_REG    ((uint32_t*)0xFFFF0104)

uint32_t awaitRadarTelemetry(void) {
    // BUG 1: Compiler Optimization Hazard! The compiler detects that RADAR_STATUS_REG
    // is never written to inside the loop. Under -O2 or -O3 optimization, the compiler
    // loads *RADAR_STATUS_REG ONCE into a CPU register and loops infinitely on that register!
    // BUG 2: Cache Hazard! The CPU's L1 Data Cache caches address 0xFFFF0100,
    // blinding the core to external peripheral hardware bus updates!
    while ((*RADAR_STATUS_REG & 0x01) == 0) {
        // Busy-wait polling
    }
    
    return *RADAR_DATA_REG;
}
```

<details>
<summary><strong>View Root Cause Analysis & Production MMIO Driver Solution</strong></summary>

##### Root Cause Analysis:
1. **Compiler Optimization Assumption:** Compilers assume standard C variables reside in ordinary memory where values change *only* via explicit program writes. Because `RADAR_STATUS_REG` is not written within the loop, the optimizing compiler hoists the memory read outside the loop:
   ```assembly
   movl 0xFFFF0100, %eax
   .L_poll:
   testl $1, %eax
   jz .L_poll      # Infinite loop on cached CPU register!
   ```
2. **CPU Cache Hazard:** Standard memory reads are routed through the CPU's L1/L2 cache. When external hardware updates the physical device bus at `0xFFFF0100`, the cache remains stale unless the memory page is mapped as **Uncacheable (Device MMIO)** in the Page Table / MPU.

##### Production Aerospace Driver Implementation:
```c
#include <stdint.h>
#include <stdbool.h>

// Fix 1: Qualify pointer as 'volatile'.
// 'volatile' forces the compiler to emit a physical bus READ instruction on EVERY iteration!
#define RADAR_STATUS_REG  ((volatile uint32_t*)0xFFFF0100)
#define RADAR_DATA_REG    ((volatile uint32_t*)0xFFFF0104)

// Architectural Memory Barrier (Ensures all preceding memory transactions complete)
#define MEMORY_BARRIER()  __asm__ __volatile__("dmb sy" ::: "memory") // ARM Data Memory Barrier

uint32_t awaitRadarTelemetryRobust(uint32_t timeoutCycles) {
    uint32_t attempts = 0;
    
    // Explicit read on every iteration
    while ((*RADAR_STATUS_REG & 0x01) == 0) {
        if (++attempts >= timeoutCycles) {
            return 0xFFFFFFFF; // Error: Hardware Watchdog Timeout
        }
        // Hint to CPU pipeline that this is a spin-loop (prevents pipeline starvation)
        #if defined(__x86_64__) || defined(_M_X64)
            __asm__ __volatile__("pause");
        #elif defined(__aarch64__)
            __asm__ __volatile__("yield");
        #endif
    }
    
    MEMORY_BARRIER(); // Enforce ordering before data payload read
    uint32_t telemetry = *RADAR_DATA_REG;
    return telemetry;
}
```
</details>

---

#### Level 3 — Production System Design: Scatter-Gather DMA Controller Architecture

##### Architectural Challenge:
Direct Memory Access (DMA) controllers alleviate the CPU from the burden of byte-by-byte data movement over the System Bus. Design an enterprise-grade **Scatter-Gather DMA Controller Driver & Descriptor Engine** in C++.

The DMA engine must:
1. Support linked-list **Scatter-Gather Descriptors** enabling non-contiguous physical memory transfers.
2. Arbitrate bus mastership, drive Address/Data buses, and count transferred 64-bit words.
3. Manage bus ownership cycles and assert an Interrupt Request (`IRQ`) upon buffer exhaustion or bus fault.
4. Calculate effective bus utilization and memory throughput.

<details>
<summary><strong>View Production Architectural Implementation</strong></summary>

```cpp
/**
 * Production Scatter-Gather DMA Controller Architecture
 * Simulates Top-Level Bus Mastership, Descriptor Traversal & Interrupt Signaling
 */
#include <iostream>
#include <vector>
#include <cstdint>
#include <iomanip>
#include <cstring>

// Hardware Scatter-Gather Descriptor (Must align to 64-bit boundaries)
struct alignas(8) DmaDescriptor {
    uint64_t sourceAddress;       // Physical source address on System Bus
    uint64_t destinationAddress;  // Physical destination address
    uint32_t transferLengthBytes; // Number of bytes to transfer
    uint32_t controlFlags;        // Bit 0: Interrupt Enable, Bit 1: End-Of-Chain (EOC)
    uint64_t nextDescriptorAddr;  // Physical address of next linked descriptor
};

// Control Flag Bitmasks
constexpr uint32_t DMA_FLAG_IRQ_ENABLE = 0x00000001;
constexpr uint32_t DMA_FLAG_EOC        = 0x00000002;

class SystemBusDmaController {
public:
    enum Status : uint32_t {
        STATUS_IDLE       = 0x0,
        STATUS_BUS_MASTER = 0x1,
        STATUS_BUSY       = 0x2,
        STATUS_COMPLETED  = 0x4,
        STATUS_ERROR      = 0x8
    };

    SystemBusDmaController(std::vector<uint8_t>& sharedSystemMemory)
        : memory(sharedSystemMemory), currentStatus(STATUS_IDLE),
          totalBytesTransferred(0), totalBusCycles(0) {}

    void initiateChain(uint64_t headDescriptorAddress) {
        currentStatus = STATUS_BUS_MASTER;
        uint64_t currentDescAddr = headDescriptorAddress;
        
        std::cout << ">>> [DMA] Acquired System Bus Mastership. Parsing Chain at 0x" 
                  << std::hex << currentDescAddr << std::dec << std::endl;

        while (currentStatus != STATUS_ERROR) {
            if (currentDescAddr + sizeof(DmaDescriptor) > memory.size()) {
                std::cerr << ">>> [DMA FAULT] Descriptor address out of physical bounds!" << std::endl;
                currentStatus = STATUS_ERROR;
                break;
            }

            // 1. Fetch Descriptor from memory over System Bus
            DmaDescriptor desc;
            std::memcpy(&desc, &memory[currentDescAddr], sizeof(DmaDescriptor));
            totalBusCycles += 4; // 4 bus cycles to read 32-byte descriptor

            std::cout << "  -> Processing Node: Src=0x" << std::hex << desc.sourceAddress
                      << " Dst=0x" << desc.destinationAddress
                      << " Len=" << std::dec << desc.transferLengthBytes << "B" << std::endl;

            // 2. Validate memory transfer boundaries
            if (desc.sourceAddress + desc.transferLengthBytes > memory.size() ||
                desc.destinationAddress + desc.transferLengthBytes > memory.size()) {
                std::cerr << ">>> [DMA FAULT] Memory transfer range violates physical boundary!" << std::endl;
                currentStatus = STATUS_ERROR;
                break;
            }

            // 3. Execute 64-bit Burst Word Transfers over System Bus
            uint32_t wordsToTransfer = desc.transferLengthBytes / 8;
            for (uint32_t w = 0; w < wordsToTransfer; ++w) {
                uint64_t src = desc.sourceAddress + (w * 8);
                uint64_t dst = desc.destinationAddress + (w * 8);
                
                // Read 64-bit word from source, write to destination
                uint64_t dataWord;
                std::memcpy(&dataWord, &memory[src], 8);
                std::memcpy(&memory[dst], &dataWord, 8);
                
                totalBusCycles += 2; // 1 read cycle + 1 write cycle per word
                totalBytesTransferred += 8;
            }

            // 4. Handle End-Of-Chain or Trigger Interrupt
            if (desc.controlFlags & DMA_FLAG_IRQ_ENABLE) {
                triggerHardwareInterrupt(currentDescAddr);
            }

            if (desc.controlFlags & DMA_FLAG_EOC) {
                std::cout << ">>> [DMA] End-of-Chain bit encountered. Releasing Bus." << std::endl;
                currentStatus = STATUS_COMPLETED;
                break;
            }

            currentDescAddr = desc.nextDescriptorAddr;
        }

        releaseSystemBus();
    }

    void printMetrics() const {
        std::cout << "
========================================" << std::endl;
        std::cout << "   SYSTEM BUS DMA PERFORMANCE REPORT    " << std::endl;
        std::cout << "========================================" << std::endl;
        std::cout << "Total Bytes Moved  : " << totalBytesTransferred << " bytes" << std::endl;
        std::cout << "Total Bus Cycles   : " << totalBusCycles << " cycles" << std::endl;
        double throughput = totalBusCycles == 0 ? 0.0 : 
            static_cast<double>(totalBytesTransferred) / (totalBusCycles * 10e-9); // 100MHz bus (10ns)
        std::cout << "Effective Bandwidth: " << std::fixed << std::setprecision(2) 
                  << (throughput / (1024 * 1024)) << " MB/s (at 100 MHz bus clock)" << std::endl;
        std::cout << "========================================
" << std::endl;
    }

private:
    std::vector<uint8_t>& memory;
    Status currentStatus;
    uint64_t totalBytesTransferred;
    uint64_t totalBusCycles;

    void triggerHardwareInterrupt(uint64_t descAddr) {
        std::cout << "  [IRQ ASSERTED] CPU notified of buffer completion at 0x" 
                  << std::hex << descAddr << std::dec << std::endl;
    }

    void releaseSystemBus() {
        std::cout << ">>> [DMA] Bus Grant de-asserted. CPU resumes bus control." << std::endl;
    }
};

int main() {
    // Simulate 1 MB physical unified memory space
    std::vector<uint8_t> ram(1024 * 1024, 0);

    // Initialize source test payload at 0x20000
    const char* samplePayload = "TOP-LEVEL COMPUTER ARCHITECTURE SYSTEM BUS DMA STREAM";
    std::memcpy(&ram[0x20000], samplePayload, std::strlen(samplePayload));

    // Construct Scatter-Gather Descriptor 1 (at 0x1000)
    DmaDescriptor d1{
        .sourceAddress = 0x20000,
        .destinationAddress = 0x50000,
        .transferLengthBytes = 64, // 8 words
        .controlFlags = DMA_FLAG_IRQ_ENABLE,
        .nextDescriptorAddr = 0x1040 // Points to Descriptor 2
    };

    // Construct Scatter-Gather Descriptor 2 (at 0x1040 - End of Chain)
    DmaDescriptor d2{
        .sourceAddress = 0x20000,
        .destinationAddress = 0x60000,
        .transferLengthBytes = 64,
        .controlFlags = DMA_FLAG_IRQ_ENABLE | DMA_FLAG_EOC,
        .nextDescriptorAddr = 0x0000
    };

    std::memcpy(&ram[0x1000], &d1, sizeof(DmaDescriptor));
    std::memcpy(&ram[0x1040], &d2, sizeof(DmaDescriptor));

    SystemBusDmaController dma(ram);
    dma.initiateChain(0x1000);
    dma.printMetrics();

    // Verify memory destination
    std::cout << "Destination 0x50000 Verification: " << reinterpret_cast<char*>(&ram[0x50000]) << std::endl;
    std::cout << "Destination 0x60000 Verification: " << reinterpret_cast<char*>(&ram[0x60000]) << std::endl;

    return 0;
}
```

##### Architectural Verification:
- **System Bus Offloading:** CPU is completely bypassed during block transfers, freeing the core to compute in L1 cache while the DMA controller saturates the external bus.
- **Scatter-Gather Hardware Mapping:** Models true PCI Express DMA scatter-gather engines used in modern enterprise NVMe and 100GbE network interfaces.
</details>

---

### 6. Reference Video Lecture
Review this engineering demonstration of the stored-program fetch-decode-execute cycle and the physical interactions along the system bus:

{{ media:fetch-execute-video }}
