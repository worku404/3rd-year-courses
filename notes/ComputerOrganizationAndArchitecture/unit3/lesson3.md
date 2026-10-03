# Unit 3 — Computer Function, Instruction Cycles, Interrupts & Bus Structures
## Lesson 3 — Bus Interconnection Structures, Multi-Tier Hierarchies & Timing Protocols

### 1. The System Bus Interconnection Triad: Data, Address & Control Signal Topology

In a stored-program digital computer, discrete functional modules—the Central Processing Unit (CPU), Semiconductor Main Memory, and Input/Output (I/O) peripheral interfaces—must continuously exchange binary operands, machine instructions, device addresses, and synchronization signals. The shared physical transmission medium providing this interconnectivity is the **System Bus**.

A bus is a collection of parallel conductive pathways (copper traces on a printed circuit board, backplane wiring pins, or on-chip metal layers) to which multiple functional devices are electrically coupled. Because a bus is a shared broadcast medium, signals transmitted by any single transmitting unit propagate to all other attached units; however, only the uniquely targeted receiver responds to the transmission.

```
+-----------------------------------------------------------------------------------------+
|                                    THE SYSTEM BUS TRIAD                                 |
|                                                                                         |
|        CONTROL BUS   (e.g., MEMR, MEMW, IOR, IOW, TRANSFER_ACK, BUS_REQ, BUS_GRANT)     |
|   <=================================================================================>   |
|                                                                                         |
|        ADDRESS BUS   (e.g., A0 - A31 -> 32-bit Physical Address Space = 4 GB)           |
|   ==================================================================================>   |
|                                                                                         |
|        DATA BUS      (e.g., D0 - D63 -> 64-bit Bi-directional Data Path)                |
|   <=================================================================================>   |
|           ^                               ^                               ^             |
|           |                               |                               |             |
|     +-----------+                   +-----------+                   +-----------+       |
|     |    CPU    |                   |   MAIN    |                   |    I/O    |       |
|     |  MASTER   |                   |  MEMORY   |                   | CONTROLLER|       |
|     +-----------+                   +-----------+                   +-----------+       |
+-----------------------------------------------------------------------------------------+
```

#### The Functional Line Triad
A computer system bus is physically partitioned into three distinct functional signal groups:

1. **The Data Bus ($W_D$ lines):**
   - Transmits binary data words bi-directionally between the CPU, memory subsystem, and I/O modules.
   - The **width** of the data bus ($W_D \in \{8, 16, 32, 64, 128\}\text{ bits}$) dictates the instantaneous word transfer capacity of the architecture. If an architecture features an $8\text{-byte}$ ($64\text{-bit}$) instruction format, a $32\text{-bit}$ data bus requires two sequential bus cycles to fetch a single instruction, whereas a $64\text{-bit}$ bus fetches it in a single cycle.
   - Peak theoretical data throughput is directly proportional to data bus width:
   $$\text{Throughput}_{\text{peak}} = W_D \times f_{\text{bus}} \quad [\text{bits/second}]$$

2. **The Address Bus ($W_A$ lines):**
   - Designates the precise source or destination memory address of data traveling along the data bus, or identifies a specific peripheral device register port.
   - The width of the address bus determines the maximum directly addressable physical memory capacity of the computer system:
   $$\text{Physical Address Space} = 2^{W_A} \times \text{Addressable Unit (Bytes)}$$
   - *Example Calculations:*
     - A 16-bit address bus ($W_A = 16$) yields $2^{16} = 65,536\text{ bytes} = 64\text{ KB}$.
     - A 32-bit address bus ($W_A = 32$) yields $2^{32} = 4,294,967,296\text{ bytes} = 4\text{ GB}$.
     - A 36-bit Physical Address Extension (PAE) bus ($W_A = 36$) addresses $2^{36} = 64\text{ GB}$.
     - Modern 64-bit architectures typically implement 48-bit or 52-bit physical address lines ($W_A = 48 \implies 256\text{ TB}$, $W_A = 52 \implies 4\text{ PB}$).
   - The higher-order bits of the address bus are decoded by address decoding circuitry to select specific memory chips or I/O interface blocks, while lower-order bits select individual words within a bank.

3. **The Control Bus:**
   - Controls and coordinates access to, and the use of, the data and address lines. Because data and address lines are shared by all system components, control signals transmit command opcodes and timing strobe pulses that prevent electrical bus contention.
   - Primary control lines include:
     - **Memory Read (`MEMR`):** Directs the addressed memory location to place its contents onto the data bus.
     - **Memory Write (`MEMW`):** Directs the addressed memory location to store the byte/word currently asserted on the data bus.
     - **I/O Read (`IOR`):** Commands the addressed peripheral port to place input data onto the data bus.
     - **I/O Write (`IOW`):** Commands the addressed peripheral port to latch the output data asserted on the data bus.
     - **Transfer Acknowledge (`ACK` / `READY`):** Indicates that data has been accepted from or placed onto the data bus by the target slave module.
     - **Bus Request (`BREQ`):** Asserted by a bus master requesting exclusive control of the bus.
     - **Bus Grant (`BGRANT`):** Asserted by the bus arbiter indicating that control has been allocated to a requesting master.
     - **Interrupt Request (`IRQ`):** Signals an asynchronous service request to the processor.
     - **Interrupt Acknowledge (`INTA`):** Signals that an asserted interrupt has been recognized by the CPU.
     - **Clock (`CLK`):** Provides the master square-wave clock signal for synchronous bus transitions.
     - **Reset (`RST`):** Initializes all connected hardware modules to a known, stable initial state.

#### Physical Characteristics and Transmission Line Effects
At high frequencies, physical bus traces behave as transmission lines rather than idealized zero-resistance conductors. Key physical constraints include:
- **Propagation Delay ($\tau$):** An electrical signal propagates across standard FR4 printed circuit boards at approximately $15\text{ to }20\text{ cm/ns}$ ($\approx 6\text{ inches/ns}$, or half the speed of light in vacuum):
  $$\tau = \frac{d}{v_p} = \frac{d \cdot \sqrt{\epsilon_r}}{c}$$
- **Capacitive Loading:** Every device attached to a bus introduces parasitic input capacitance ($C_{\text{pin}} \approx 5\text{ to }10\text{ pF}$). As the number of connected devices $N$ increases, total capacitance $C_{\text{total}} = \sum_{i=1}^N C_i$ increases significantly, increasing the $RC$ charging time constant and severely attenuating high-frequency signal rise times ($t_r \approx 2.2 \cdot R \cdot C$).
- **Bus Reflections & Ringing:** Impedance mismatches at open trace terminations cause electromagnetic waves to reflect back along the bus, inducing voltage undershoot, overshoot, and false digital switching thresholds. High-speed buses require active termination resistor networks matched to trace characteristic impedance ($Z_0 \approx 50\text{ to }75\ \Omega$).

{{ media:coa-bus-hierarchy-diagram }}

---

### 2. Propagation Bottlenecks & Multi-Tier Bus Hierarchies (Traditional vs. Mezzanine / PCIe)

#### The Failure of the Single Shared Bus
In early personal computing architectures (such as the original IBM PC 8-bit ISA bus), a single shared system bus interconnected the CPU, memory subsystem, and all peripheral expansion slots. As microprocessor clock speeds accelerated from $4.77\text{ MHz}$ to hundreds of megahertz and gigahertz, the single-bus topology collapsed under three severe physical constraints:

1. **Bus Contention / Traffic Congestion:** High-throughput devices (video graphics accelerators, disk array controllers, high-speed network interfaces) saturate the shared bus bandwidth, starving the CPU of instruction fetch and operand read cycles.
2. **Capacitive Degradation:** The physical trace length required to span multiple expansion slots on a motherboard, combined with dozens of device load pins, creates massive capacitance, forcing the bus clock down to archaic speeds ($8.33\text{ MHz}$ for ISA) to allow signals to settle.
3. **Impedance and Propagation Delays:** At a $1\text{ GHz}$ clock frequency, one clock period is only $1\text{ ns}$. In that single cycle, an electrical signal travels at most $15\text{ cm}$. A shared bus physically spanning $30\text{ cm}$ across a motherboard cannot complete even a single-cycle round-trip transaction at modern CPU clock rates!

#### The Evolution of Multi-Tier Bus Hierarchies
To resolve this bottleneck, computer architects transitioned from a single monolithic bus to hierarchical, multi-tiered architectures where high-speed local buses operate in close physical proximity to the CPU, while slower expansion buses are isolated behind bidirectional bridge interfaces.

```
+-----------------------------------------------------------------------------------------+
|                  TRADITIONAL DUAL-BUS HIERARCHY ARCHITECTURE                            |
|                                                                                         |
|       +--------------+                    +---------------------+                       |
|       |     CPU      | <================> | L2 / L3 CACHE MEMORY|                       |
|       +--------------+   LOCAL CPU BUS    +---------------------+                       |
|              ^                                       ^                                  |
|              |                                       |                                  |
|              +===================+===================+                                  |
|                                  |                                                      |
|                         +-----------------+                                             |
|                         | SYSTEM CONTROLLER|                                            |
|                         | (NORTHBRIDGE /  |                                             |
|                         | MEMORY CONTROL) | <=================> MAIN DRAM MEMORY        |
|                         +-----------------+    SYSTEM BUS                               |
|                                  |                                                      |
|                         +-----------------+                                             |
|                         | EXPANSION BUS   |                                             |
|                         |    INTERFACE    |                                             |
|                         | (SOUTHBRIDGE)   |                                             |
|                         +-----------------+                                             |
|                                  |                                                      |
|                ==================+===================                                   |
|                          EXPANSION BUS (e.g., ISA / PCI)                                |
|                        |                  |                                             |
|                   +---------+        +---------+                                        |
|                   | SERIAL/ |        | NETWORK |                                        |
|                   | PARALLEL|        |   NIC   |                                        |
|                   +---------+        +---------+                                        |
+-----------------------------------------------------------------------------------------+
```

#### Traditional vs. High-Performance Mezzanine Topologies

##### 1. Traditional Multi-Bus Topology
- **Local CPU Bus:** Connects the processor core directly to internal registers, L1 cache, and L2 cache. Operates at full core clock frequency over microscopic on-die or module distances ($< 2\text{ cm}$).
- **System Bus:** Couples the processor/cache unit to the main DRAM memory subsystem through a Memory Controller (Northbridge).
- **Expansion Bus:** A slow, standardized legacy bus (such as 16-bit ISA) connected through an Expansion Bus Interface / Southbridge. Peripherals on the expansion bus cannot interrupt or delay memory transfers on the system bus.

##### 2. High-Performance Mezzanine Topology
- To accommodate high-bandwidth peripherals (such as 3D graphics cards, Gigabit Ethernet, and SCSI/SATA host adapters) without degrading local memory bandwidth, architects introduced an intermediate **Mezzanine Bus** (such as PCI / Peripheral Component Interconnect):
- The Mezzanine bus sits between the high-speed local bus and the slow expansion bus.
- High-speed I/O controllers attach directly to the Mezzanine bus through localized bridge circuitry, providing high bandwidth ($133\text{ MB/s}$ to $533\text{ MB/s}$ for PCI) while electrically isolating the CPU-memory bus.

```
+-----------------------------------------------------------------------------------------+
|                    HIGH-PERFORMANCE MEZZANINE (PCI) TOPOLOGY                            |
|                                                                                         |
|     +-----------+                  +-------------+                                      |
|     |    CPU    | <==============> |  L2 CACHE   |                                      |
|     +-----------+    LOCAL BUS     +-------------+                                      |
|           ^                               ^                                             |
|           +===============+===============+                                             |
|                           |                                                             |
|                 +-------------------+                                                   |
|                 |  HOST/PCI BRIDGE  | <=====================> MAIN MEMORY               |
|                 |   (NORTHBRIDGE)   |        MEMORY BUS                                 |
|                 +-------------------+                                                   |
|                           |                                                             |
|       ====================+=======================================                      |
|                      MEZZANINE BUS (PCI @ 33 / 66 MHz)                                  |
|            |                              |                      |                      |
|     +--------------+              +---------------+      +---------------+              |
|     | HIGH-SPEED   |              |  GIGABIT NIC  |      | PCI-EXPANSION |              |
|     | GRAPHICS GPU |              |  CONTROLLER   |      |    BRIDGE     |              |
|     +--------------+              +---------------+      +---------------+              |
|                                                                  |                      |
|                                                      ============+============          |
|                                                            LEGACY EXPANSION BUS         |
|                                                            (e.g., ISA / LPC / COM)      |
+-----------------------------------------------------------------------------------------+
```

#### The Paradigm Shift: Parallel Shared Buses to Point-to-Point Serial Fabrics (PCIe)
Despite the success of PCI and PCI-X, parallel buses encountered an insurmountable physical barrier: **Clock Skew**.
- On a 64-bit parallel bus, all 64 data signals, 32 address signals, and control signals must arrive at the destination receiver within an infinitesimal fraction of a single clock cycle.
- Microscopic differences in trace length, board dielectric thickness, and pin capacitance cause different bits to arrive at slightly different times (**trace skew**).
- At frequencies beyond $133\text{ MHz}$, clock skew exceeds the setup/hold time window, causing bit errors.

Modern systems abandon wide parallel broadcast buses in favor of **Point-to-Point Serial Interconnects (PCI Express / PCIe, Intel Ultra Path Interconnect - UPI, AMD Infinity Fabric)**:
- **Dedicated Switched Fabric:** Devices do not share a common electrical trace. Instead, a central Root Complex and Switch dynamically route serialized packet buffers between point-to-point links.
- **Differential Signaling:** Each transmission path consists of two complementary wires carrying opposite polarity voltages ($+V$ and $-V$). External electromagnetic interference affects both wires equally, allowing the receiver's differential operational amplifier to subtract noise completely ($V_{\text{out}} = V^+ - V^-$), enabling ultra-low voltages ($800\text{ mV}$) and extreme frequencies ($16\text{ to }32\text{ GHz}$).
- **Embedded Clocking:** Instead of a separate clock line prone to skew, the clock is encoded directly into the bitstream using $8\text{b}/10\text{b}$ or $128\text{b}/130\text{b}$ encoding, guaranteeing zero clock-data skew regardless of physical cable length.

##### Historical Interconnect Comparison Matrix
| Standard / Specification | Architecture Type | Bus Width (Bits) | Clock Frequency | Aggregate Peak Bandwidth | Dominant Bottleneck / Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ISA (Industry Standard Arch)** | Monolithic Shared Parallel | 8 / 16 bits | 8.33 MHz | 8.33 MB/s (16-bit) | High capacitive loading; slow CPU stalls. |
| **PCI (32-bit / 33 MHz)** | Shared Mezzanine Parallel | 32 bits | 33.33 MHz | 133.33 MB/s | Bus arbitration contention; shared bandwidth. |
| **PCI-X 2.0 (DDR)** | Parallel Point-to-Point/Shared | 64 bits | 266 MHz (DDR) | 4.26 GB/s | Severe trace-to-trace clock skew across 64 bits. |
| **PCIe Gen 3 (x16 Link)** | Switched Serial Differential | 16 Lanes (1 bit/lane) | 8.0 GT/s | 15.75 GB/s ($128\text{b}/130\text{b}$) | Controller silicon area and thermal dissipation. |
| **PCIe Gen 5 (x16 Link)** | Switched Serial Differential | 16 Lanes (1 bit/lane) | 32.0 GT/s | 63.0 GB/s ($128\text{b}/130\text{b}$) | High-frequency trace attenuation (PAM4 in Gen 6). |

---

### 3. Bus Arbitration Mechanics: Centralized vs. Distributed Priority Election

Because multiple functional modules (the CPU, Direct Memory Access / DMA controllers, high-speed NICs, GPU coprocessors) can act as **Bus Masters** (devices capable of initiating read/write transactions), an arbitration scheme is required to resolve conflicting simultaneous access requests. At any given instant, exactly **one** master must be granted write access to prevent conflicting electrical drivers from destroying the bus.

Bus arbitration schemes are fundamentally divided into **Centralized** and **Distributed** architectures.

#### 1. Centralized Arbitration Schemes
In centralized arbitration, a single hardware module—designated the **Bus Arbiter**—receives all access requests and determines which master receives the bus.

##### A. Daisy Chaining (Serial Grant Allocation)
In a daisy-chained arbitration circuit, all bus masters assert a shared wired-OR Bus Request line (`BREQ`). When the Arbiter receives `BREQ`, it asserts a **Bus Grant** signal (`BGRANT_0`) that passes serially through each master in physical priority order:

```
+-----------------------------------------------------------------------------------------+
|                              DAISY-CHAINED BUS ARBITRATION                              |
|                                                                                         |
|                    +---------------------------------------------+                      |
|                    |             BUS BUSY (BBUSY)                |                      |
|                    +---------------------------------------------+                      |
|                         ^                   ^                   ^                       |
|                         |                   |                   |                       |
|                    +---------------------------------------------+                      |
|                    |            BUS REQUEST (BREQ)               |                      |
|                    +---------------------------------------------+                      |
|                      |  ^                 |  ^                |  ^                      |
|                      |  |                 |  |                |  |                      |
|     +-----------+    |  |  +-----------+  |  |  +-----------+ |  |  +-----------+       |
|     |           | BGRANT_0 |           |BGRANT_1|           |BGRANT_2           |       |
|     |  CENTRAL  |=========>| MASTER 1  |=======>| MASTER 2  |======>| MASTER 3  |       |
|     |  ARBITER  |          | (HIGHEST) |        | (MEDIUM)  |       | (LOWEST)  |       |
|     +-----------+          +-----------+        +-----------+       +-----------+       |
+-----------------------------------------------------------------------------------------+
```

- **Protocol Sequence:**
  1. Masters requiring the bus pull down the open-collector `BREQ` line.
  2. The Arbiter detects `BREQ` low and drives `BGRANT_0` high.
  3. Master 1 inspects `BGRANT_0`:
     - If Master 1 requested the bus, it absorbs the grant, asserts `BBUSY` (Bus Busy) low to signal ownership, and leaves `BGRANT_1` low.
     - If Master 1 did not request the bus, it propagates the grant to Master 2 via `BGRANT_1`.
  4. The process repeats until a requesting master absorbs the grant.
- **Architectural Trade-Offs:**
  - *Advantages:* Extremely low pin count (only 3 control lines: `BREQ`, `BGRANT`, `BBUSY`), independent of the number of attached devices.
  - *Disadvantages:*
    1. **Priority Starvation:** Devices situated physically far downstream from the arbiter experience starvation if upstream devices generate frequent traffic.
    2. **Slow Arbitration Speed:** Grant propagation delay scales linearly with device count:
       $$t_{\text{grant\_total}} = N \cdot t_{\text{prop\_gate}}$$
    3. **Single Point of Physical Failure:** If a device is unplugged or its internal bypass logic fails, the grant daisy chain is broken, permanently locking all downstream devices out of the bus!

##### B. Independent Request / Grant (Parallel Arbitration)
To eliminate daisy-chain propagation delays and starvation, independent parallel arbitration assigns dedicated `BREQ_i` and `BGRANT_i` lines to every individual master module:

```
+-----------------------------------------------------------------------------------------+
|                   CENTRALIZED INDEPENDENT PARALLEL ARBITRATION                          |
|                                                                                         |
|                             +--------------------+                                      |
|                             |  CENTRAL ARBITER   |                                      |
|                             +--------------------+                                      |
|                               ^  |   ^  |   ^  |                                        |
|                       BREQ_1  |  |   |  |   |  |  BREQ_3                                |
|                      +--------+  |   |  |   |  +--------+                               |
|                      |  +--------+   |  |   +--------+  |                               |
|             BGRANT_1 |  |    BGRANT_2|  |BREQ_2      |  | BGRANT_3                      |
|                      v  v            v  v            v  v                               |
|                  +----------+    +----------+    +----------+                           |
|                  | MASTER 1 |    | MASTER 2 |    | MASTER 3 |                           |
|                  +----------+    +----------+    +----------+                           |
+-----------------------------------------------------------------------------------------+
```

- **Arbitration Logic:**
  Because the central arbiter has direct, parallel visibility into all active requests simultaneously, it can execute sophisticated arbitration algorithms in programmable silicon:
  - **Fixed Priority:** Master 1 > Master 2 > Master 3.
  - **Rotating Round-Robin:** After Master $k$ finishes its burst, priority rotates such that Master $(k+1) \pmod N$ receives highest priority in the subsequent arbitration cycle, guaranteeing starvation-free execution.
  - **Least Recently Used (LRU):** The master that has not accessed the bus for the longest time window is granted priority.
  - **Dynamic Time-Slice:** Masters are assigned bandwidth quotas based on Quality of Service (QoS) guarantees.
- *Trade-Offs:* Rapid arbitration ($O(1)$ clock cycle), dynamic reconfigurability; however, pin overhead scales linearly with $2N$ dedicated control lines.

#### 2. Distributed Arbitration Schemes
In distributed (decentralized) arbitration, there is no central arbiter chip. Each bus master contains on-chip arbitration logic, and all masters collaborate over shared arbitration control lines to elect the bus owner.

##### Distributed Self-Selection via Open-Collector Priority Lines
1. Each master is assigned a unique $k$-bit binary priority identification number (e.g., a 4-bit ID from `0000` to `1111`).
2. A shared $k$-bit arbitration bus (`ARB0` to `ARB3`) is wired using open-collector (wired-OR) logic, where any device driving a `0` pulls the line down, dominating a passive `1`.
3. When arbitration begins, every requesting master drives its ID onto the arbitration lines.
4. Each master reads back the resulting bus state bit-by-bit from MSB to LSB. If a master drives a `1` but detects that the line has been pulled down to `0` by a higher-priority competitor, it immediately recognizes that it has lost arbitration and disables its remaining output drivers!
5. At the end of the arbitration resolution interval, exactly one master remains driving the bus—the master with the highest priority ID.
- *Examples:* CAN (Controller Area Network) automotive bus (arbitration on message identifiers), SCSI (Small Computer System Interface), and IEEE Futurebus+.

---

### 4. Bus Timing Protocols: Synchronous Clock-Edge Latching vs. Asynchronous Handshaking Protocols

The timing protocol of a bus governs the temporal coordination between master and slave modules during address broadcasting, command assertion, and data latching.

#### 1. Synchronous Timing Protocols
In a **Synchronous Bus**, all address, data, and control events are strictly locked to the discrete edges of a single, centralized square-wave **Bus Clock** signal distributed across the motherboard.

```
       CYCLE 1             CYCLE 2             CYCLE 3             CYCLE 4
   +-----+     +-----+     +-----+     +-----+     +-----+     +-----+     +-----+
CLK|     |_____|     |_____|     |_____|     |_____|     |_____|     |_____|     |
   +-----------------------------------------------------------------------------+
ADDR     VALID ADDRESS ASSERTED
   ===============<=================================================>============
CTRL     READ/WRITE STROBE ASSERTED
   _______________+=================================================+____________
READY (WAIT)
   ________________________________________________+================+____________
                                                     (Slave Ready)
DATA                                               +----------------+
                                                   | VALID DATA OUT |
   ================================================<================>============
                                                    ^
                                                    LATCHED HERE!
```

- **Operational Mechanism:**
  1. **Clock Edge 1 (T1):** The Master asserts the physical address on the Address Bus and drives the control line (e.g., `MEMR` high).
  2. **Propagation Window:** The address and command signals propagate across the PCB traces and are decoded by the slave interface.
  3. **Clock Edge 2 (T2):** The targeted slave device accesses its internal registers or DRAM cells to retrieve the requested data word.
  4. **Clock Edge 3 (T3):** If the slave requires additional time (e.g., DRAM refresh or slow ROM access), it pulls the `READY` / `WAIT` line low, forcing the CPU to insert idle clock cycles (**Wait States**).
  5. **Clock Edge 4 (T4):** Once `READY` goes high, the slave places the data onto the Data Bus, and the master latches the data lines on the rising clock edge.
- **Architectural Trade-Offs:**
  - *Advantages:* Hardware implementation is simple; state transitions are governed by standard edge-triggered flip-flops without complex handshaking control logic.
  - *Disadvantages:*
    - **Rigid Clock Lockstep:** All transactions occur in discrete integer multiples of clock periods. If a fast device finishes an operation in $1.1$ clock periods, it must wait until clock period 2 to transfer data, wasting $0.9$ clock cycles.
    - **Clock Skew Constraints:** As bus trace lengths increase, the clock edge arrives at different chips at different nanosecond offsets, limiting the maximum scalable clock speed of synchronous buses.

#### 2. Asynchronous Timing Protocols (Fully Interlocked Handshaking)
In an **Asynchronous Bus**, there is **no centralized bus clock**. Synchronization is achieved entirely through an event-driven, closed-loop handshaking exchange between two control lines: **Master Synchronization (`MSYN` / Address Strobe)** and **Slave Synchronization (`SSYN` / Data Acknowledge)**.

```
        EVENT 1               EVENT 2             EVENT 3            EVENT 4
           +---------------------+                   +------------------+
Master     | Master asserts ADDR |                   | Master latches   |
Action     | and drives MSYN HIGH|                   | DATA, drops MSYN |
           +---------------------+                   +------------------+
                      |                                       |
                      v                                       v
MSYN   _______________+=======================================+__________________
                              |                                       |
                              v                                       v
SSYN   _______________________+=======================================+__________
                                      ^                                       ^
           +--------------------------+           +---------------------------+
Slave      | Slave decodes ADDR, puts |           | Slave detects MSYN LOW,   |
Action     | DATA on bus, drives SSYN |           | removes DATA, drops SSYN  |
           +--------------------------+           +---------------------------+
```

##### The Classical 4-Phase Fully Interlocked Handshake Protocol
The 4-phase asynchronous read transaction proceeds as follows:

1. **Phase 1: Master Assertion (`MSYN` $\uparrow$)**
   - The Master drives the target memory address onto the Address Bus and asserts the `READ` control line.
   - The master waits for a predetermined deskew delay ($t_{\text{deskew}} \approx 10\text{ to }20\text{ ns}$) to allow address signals to settle and stabilize on the bus traces.
   - The Master drives `MSYN` (Master Synchronization) HIGH, informing all devices that a stable address is present.
2. **Phase 2: Slave Response (`SSYN` $\uparrow$)**
   - The targeted Slave decodes the address, retrieves the requested byte/word from its internal memory storage, and places the data onto the Data Bus.
   - The Slave drives `SSYN` (Slave Synchronization / Transfer Complete) HIGH.
3. **Phase 3: Master Latch & Deassertion (`MSYN` $\downarrow$)**
   - The Master detects the rising edge of `SSYN`.
   - The Master latches the data from the Data Bus into its internal CPU pipeline buffer.
   - Having captured the data, the Master drops `MSYN` to LOW.
4. **Phase 4: Slave Termination (`SSYN` $\downarrow$)**
   - The Slave detects that `MSYN` has gone LOW.
   - The Slave removes its data drivers from the Data Bus (returning data lines to a high-impedance `Hi-Z` float state).
   - The Slave drops `SSYN` to LOW.
   - The bus is now completely idle, and a new transaction can initiate immediately.

##### Comparison: Synchronous vs. Asynchronous Timing
| Architectural Metric | Synchronous Bus Protocol | Asynchronous Handshake Protocol |
| :--- | :--- | :--- |
| **Clock Requirement** | Requires a high-stability centralized global clock generator. | No clock line required; completely event-driven. |
| **Latency Characteristics** | Constrained to discrete clock cycles; wasted fraction of clock cycles. | Latency equals exact physical device access time + trace delay ($\tau$). |
| **Heterogeneous Devices** | Requires dynamic wait-state generator logic for slow devices. | Inherently adapts to arbitrary mixed-speed devices (5 ns SRAM vs 500 ns I/O). |
| **Clock Skew Vulnerability** | Highly vulnerable; requires matched trace lengths across all pins. | Immune to clock skew; deskew delays guaranteed by handshake sequencing. |
| **Hardware Complexity** | Simple synchronous register transfer logic. | Complex asynchronous finite state machines; susceptible to metastability. |

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Asynchronous Handshake Timing Trace
A 64-bit microprocessor connects to an asynchronous memory bus. The processor initiates a Read transaction to an external DRAM controller with an access latency of $t_{\text{access}} = 45\text{ ns}$.
- Trace propagation delay between Master and Slave is $t_{\text{prop}} = 5\text{ ns}$.
- Master address-to-strobe deskew delay is $t_{\text{deskew}} = 10\text{ ns}$.
- Master data latching hold time is $t_{\text{hold}} = 5\text{ ns}$.
- Slave bus release time after `MSYN` drops is $t_{\text{release}} = 8\text{ ns}$.

Trace the exact timeline of signal edges and calculate total transaction cycle time.

##### Timing Breakdown Table:
| Absolute Timestamp ($t$) | Signal Transition / Bus Event | Responsible Module | Architectural State Description |
| :--- | :--- | :--- | :--- |
| $t = 0.0\text{ ns}$ | `ADDR = 0x7FFF_0040`, `READ = 1` | CPU Master | Address placed on address lines; deskew timer started. |
| $t = 10.0\text{ ns}$ | `MSYN` driven HIGH | CPU Master | Deskew delay elapsed; address guaranteed stable at all receivers. |
| $t = 15.0\text{ ns}$ | `MSYN` arrives at Slave | Physical Bus | Signal propagates across PCB traces ($t_{\text{prop}} = 5\text{ ns}$). |
| $t = 15.0\text{ ns} \to 60.0\text{ ns}$ | Internal DRAM access | DRAM Slave | Slave accesses memory cells ($t_{\text{access}} = 45\text{ ns}$). |
| $t = 60.0\text{ ns}$ | `DATA = 0xCAFEBABE`, `SSYN` HIGH | DRAM Slave | Data asserted on bus; Slave drives acknowledge signal. |
| $t = 65.0\text{ ns}$ | `SSYN` arrives at Master | Physical Bus | Acknowledge propagates back to Master ($t_{\text{prop}} = 5\text{ ns}$). |
| $t = 70.0\text{ ns}$ | Data latched; `MSYN` driven LOW | CPU Master | Master captures data word; drops strobe ($t_{\text{hold}} = 5\text{ ns}$). |
| $t = 75.0\text{ ns}$ | `MSYN` low arrives at Slave | Physical Bus | Falling edge propagates across traces ($t_{\text{prop}} = 5\text{ ns}$). |
| $t = 83.0\text{ ns}$ | Data floated; `SSYN` driven LOW | DRAM Slave | Slave releases data bus ($t_{\text{release}} = 8\text{ ns}$) and drops ack. |
| $t = 88.0\text{ ns}$ | `SSYN` low arrives at Master | Physical Bus | Final transition returns to Master; **Bus Cycle Complete!** |

$$\text{Total Bus Transaction Latency} = 88.0\text{ nanoseconds}$$
$$\text{Max Throughput} = \frac{8\text{ Bytes}}{88.0\text{ ns}} \approx 90.91\text{ MB/s}$$

---

#### Level 2 — Scaffolded Bug-Fix: Daisy-Chain Priority Starvation & Broken Chain Bypass

##### Architectural Defect Scenario
An industrial telemetry system utilizes a 4-channel Daisy-Chained arbitration circuit where:
- Channel 0: High-bandwidth Video Streaming Coprocessor
- Channel 1: High-Speed Ethernet Controller
- Channel 2: Real-Time Motor Position Sensor (Critical safety watchdog)
- Channel 3: Diagnostic Flash Logger

During field deployment, two critical hardware failures occur:
1. **Priority Starvation:** The Video Coprocessor (Channel 0) continuously generates burst requests, monopolizing the `BREQ` line and starving the Motor Position Sensor (Channel 2), causing the motor controller to miss its real-time control deadlines.
2. **Broken Daisy Chain:** When the Ethernet Controller (Channel 1) experiences a transient hardware lockup or is hot-unplugged for maintenance, the `BGRANT` signal cannot pass through Channel 1, permanently freezing Channels 2 and 3!

```
[ARBITER] ---BGRANT_0---> [CH 0: VIDEO] ---BGRANT_1---> [CH 1: LOCKUP/OPEN] ---X (BROKEN)
                                                                                  |
                                                                           [CH 2: MOTOR SENSOR]
                                                                                  |
                                                                           [CH 3: DIAGNOSTICS]
```

##### Defect Analysis & Architectural Remedy
- The standard daisy chain lacks an **Arbiter Fairness Timer (Bus Tenure Limit)** to enforce maximum continuous bus acquisition windows.
- The grant propagation line passes serially through internal active logic gates on each plug-in board. Hot-unplugging a card or losing chip power breaks the physical conductor.
- **Architectural Solution:**
  1. Implement a **Hardware Bus Watchdog Timer** inside the Arbiter that deasserts the grant line if any master holds `BBUSY` for longer than a programmable tenure limit ($t_{\text{tenure}} = 20\ \mu\text{s}$).
  2. Implement an **Active Multiplexed Bypass Gate** on the backplane motherboard, using mechanical or solid-state presence-detection pins (`PRESENT_L`), such that if Channel 1 is unseated or unpowered, hardware multiplexers automatically route `BGRANT_1` directly to Channel 2.

<details>
<summary><b>View Architectural Solution & Corrected Circuit Logic</b></summary>

```c
// ============================================================================
// HARDWARE SIMULATION: BUS TENURE WATCHDOG & DAISY-CHAIN BYPASS CONTROLLER
// ============================================================================
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

#define MAX_MASTERS 4
#define TENURE_LIMIT_CYCLES 200 // Max cycles a master can hold BBUSY

typedef struct {
    bool breq;          // Device asserts request
    bool bgrant_in;     // Grant input pin
    bool bgrant_out;    // Grant pass-through pin
    bool bbusy;         // Bus busy asserted by master
    bool card_present;  // Hardware pin grounded when card is physically seated
} BusMasterChannel;

typedef struct {
    bool master_breq;   // Wired-OR Bus Request line
    bool master_bbusy;  // Shared Bus Busy line
    uint32_t tenure_counter;
    int current_owner;
} CentralArbiter;

void evaluate_daisy_chain_bypass(BusMasterChannel channels[MAX_MASTERS], bool arbiter_grant) {
    bool current_grant = arbiter_grant;

    for (int i = 0; i < MAX_MASTERS; i++) {
        if (!channels[i].card_present) {
            // HARDWARE BYPASS: Card missing or dead; multiplex grant directly downstream
            channels[i].bgrant_in = false;
            channels[i].bgrant_out = current_grant;
            printf("[Motherboard Backplane] Channel %d ABSENT -> Grant Bypassed downstream.\\n", i);
        } else {
            channels[i].bgrant_in = current_grant;
            if (channels[i].breq && current_grant) {
                // Device captures grant; asserts bus busy; blocks downstream pass-through
                channels[i].bbusy = true;
                channels[i].bgrant_out = false;
                current_grant = false; // Grant absorbed!
            } else {
                // Device does not need bus; passes grant downstream
                channels[i].bbusy = false;
                channels[i].bgrant_out = current_grant;
            }
        }
        current_grant = channels[i].bgrant_out;
    }
}

void tick_arbiter_watchdog(CentralArbiter *arb, BusMasterChannel channels[MAX_MASTERS]) {
    if (arb->master_bbusy) {
        arb->tenure_counter++;
        if (arb->tenure_counter >= TENURE_LIMIT_CYCLES) {
            // TENURE EXPIRATION: Revoke grant from greedy master!
            printf(">>> ARBITER WATCHDOG EXPIRED: Force-clearing grant to prevent starvation! <<<\\n");
            for (int i = 0; i < MAX_MASTERS; i++) {
                channels[i].bbusy = false;
            }
            arb->master_bbusy = false;
            arb->tenure_counter = 0;
        }
    } else {
        arb->tenure_counter = 0;
    }
}
```

</details>

---

#### Level 3 — High-Scale System Design: Cycle-Accurate Asynchronous Bus Arbiter & Slave Simulator in C++

Design a complete, cycle-accurate discrete-event C++17 simulation modeling:
1. **Centralized Arbiter** supporting **Round-Robin Priority Allocation** to eliminate starvation.
2. **Asynchronous Handshake Protocol (4-Phase: `MSYN` / `SSYN`)** with programmable physical propagation delays and slave access latencies.
3. Multiple competing masters (CPU Cache Refill, DMA Controller, GPU Display Engine) performing read/write transfers.

<details>
<summary><b>View Complete C++ Cycle-Accurate Simulator Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: CYCLE-ACCURATE ASYNCHRONOUS BUS & ARBITER SIMULATOR
// Compile: g++ -std=c++17 -O3 bus_simulator.cpp -o bus_simulator
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <iomanip>
#include <cstdint>

enum class HandshakePhase { IDLE, MSYN_ASSERTED, SSYN_ASSERTED, MSYN_DEASSERTED, COMPLETE };

struct BusTransaction {
    uint32_t master_id;
    uint32_t address;
    uint32_t data;
    bool is_write;
    uint64_t start_time_ns;
};

// ----------------------------------------------------------------------------
// ARBITER: ROUND-ROBIN STARVATION-FREE CENTRALIZED ARBITER
// ----------------------------------------------------------------------------
class RoundRobinArbiter {
private:
    size_t num_masters;
    size_t last_granted_master;

public:
    RoundRobinArbiter(size_t masters) : num_masters(masters), last_granted_master(0) {}

    int arbitrate(const std::vector<bool>& requests) {
        for (size_t i = 1; i <= num_masters; i++) {
            size_t candidate = (last_granted_master + i) % num_masters;
            if (requests[candidate]) {
                last_granted_master = candidate;
                return static_cast<int>(candidate);
            }
        }
        return -1; // No active requests
    }
};

// ----------------------------------------------------------------------------
// ASYNCHRONOUS SLAVE: SIMULATES MEMORY ACCESS LATENCY & 4-PHASE HANDSHAKING
// ----------------------------------------------------------------------------
class AsynchronousMemorySlave {
private:
    uint64_t access_latency_ns;
    uint64_t release_time_ns;
    std::vector<uint32_t> memory_array;

public:
    AsynchronousMemorySlave(uint64_t latency_ns, uint64_t release_ns, size_t size_words)
        : access_latency_ns(latency_ns), release_time_ns(release_ns), memory_array(size_words, 0xAA55AA55) {}

    uint64_t get_access_latency() const { return access_latency_ns; }
    uint64_t get_release_time() const { return release_time_ns; }

    uint32_t read(uint32_t address) {
        size_t index = (address / 4) % memory_array.size();
        return memory_array[index];
    }

    void write(uint32_t address, uint32_t value) {
        size_t index = (address / 4) % memory_array.size();
        memory_array[index] = value;
    }
};

// ----------------------------------------------------------------------------
// BUS SIMULATION ENGINE
// ----------------------------------------------------------------------------
class SystemBusSimulation {
private:
    uint64_t current_time_ns;
    const uint64_t propagation_delay_ns = 5;
    const uint64_t deskew_delay_ns = 10;
    RoundRobinArbiter arbiter;
    AsynchronousMemorySlave memory_slave;

public:
    SystemBusSimulation(size_t num_masters, uint64_t mem_latency_ns)
        : current_time_ns(0), arbiter(num_masters), memory_slave(mem_latency_ns, 6, 1024) {}

    void execute_transaction(BusTransaction& tx) {
        std::cout << "\\n=======================================================\\n";
        std::cout << "[T = " << std::setw(5) << current_time_ns << " ns] ARBITER GRANTED BUS TO MASTER #" << tx.master_id << "\\n";
        std::cout << "=======================================================\\n";

        // Phase 1: Master asserts Address and Read/Write lines, waits deskew
        uint64_t t_addr = current_time_ns;
        current_time_ns += deskew_delay_ns;
        std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Phase 1: Master #" << tx.master_id 
                  << " asserts ADDR=0x" << std::hex << tx.address << " & drives MSYN=1\\n";

        // Signal propagates across bus to slave
        current_time_ns += propagation_delay_ns;
        std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Slave receives MSYN=1. Initiating memory access...\\n";

        // Phase 2: Slave processes read/write access
        current_time_ns += memory_slave.get_access_latency();
        if (tx.is_write) {
            memory_slave.write(tx.address, tx.data);
            std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Phase 2: Slave writes 0x" 
                      << std::hex << tx.data << " & drives SSYN=1\\n";
        } else {
            tx.data = memory_slave.read(tx.address);
            std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Phase 2: Slave reads 0x" 
                      << std::hex << tx.data << " to Data Bus & drives SSYN=1\\n";
        }

        // Slave SSYN propagates back to Master
        current_time_ns += propagation_delay_ns;
        std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Master receives SSYN=1. Latching data word...\\n";

        // Phase 3: Master latches data and deasserts MSYN
        current_time_ns += 4; // Master latching delay
        std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Phase 3: Master #" << tx.master_id 
                  << " latches 0x" << std::hex << tx.data << " & deasserts MSYN=0\\n";

        // MSYN falling edge propagates to slave
        current_time_ns += propagation_delay_ns;
        std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Slave detects MSYN=0. Releasing bus...\\n";

        // Phase 4: Slave removes data, drops SSYN
        current_time_ns += memory_slave.get_release_time();
        std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Phase 4: Slave tri-states Data Bus & deasserts SSYN=0\\n";

        // Final SSYN falling edge propagates back to Master
        current_time_ns += propagation_delay_ns;
        std::cout << "  [T = " << std::setw(5) << current_time_ns << " ns] Transaction complete. Total Bus Hold Time: " 
                  << std::dec << (current_time_ns - t_addr) << " ns.\\n";
    }
};

int main() {
    SystemBusSimulation sim(3, 40); // 3 Masters, 40 ns Memory Latency

    std::vector<BusTransaction> workload = {
        {0, 0x1000, 0xDEADBEEF, true, 0},   // Master 0 Write
        {1, 0x1000, 0x00000000, false, 0},  // Master 1 Read
        {2, 0x2040, 0xCAFEBABE, true, 0}    // Master 2 Write
    };

    for (auto& tx : workload) {
        sim.execute_transaction(tx);
    }
    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:registers-ram-video }}

This video provides an intuitive physical visualization of registers, RAM, address lines, and tri-state bus buffering that form the foundational hardware layer of modern computer buses.
