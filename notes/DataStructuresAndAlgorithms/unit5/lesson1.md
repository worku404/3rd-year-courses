# Lesson 1 — Queue Abstract Data Type & Storage Architectures (Linear vs Circular Array vs Linked List)

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the formal state axioms of the **First-In, First-Out (FIFO)** Queue Abstract Data Type (ADT).
> - Diagnose the **Drifting Boundary Defect ("False Full" failure)** in naive linear array queue implementations.
> - Derive the modular arithmetic equations governing **Circular Ring Buffers** and resolve the Full vs. Empty ambiguity.
> - Prove why a Singly Linked List Queue requires the **Head-as-Front / Tail-as-Rear** topology for strict $O(1)$ operations.
> - Engineer a production-grade resizing circular queue with memory leak elimination (**loitering prevention**).

{{media:queue-video}}

{{media:queue-visual}}

## Executive Summary & System Context

The **Queue** is a foundational linear Abstract Data Type (ADT) governed by the **First-In, First-Out (FIFO)** discipline: elements are inserted exclusively at one boundary (the **Rear** or **Tail**) and extracted exclusively at the opposing boundary (the **Front** or **Head**). This temporal ordering mirrors physical waiting lines and establishes the queue as the core data structure of asynchronous messaging architectures, operating system task dispatchers, network packet buffers, and breadth-first graph traversal algorithms.

While the abstract contract of a queue appears trivial, its physical realization in computer memory presents severe architectural traps. Naive implementations on top of linear arrays inevitably suffer from the **Drifting Boundary Defect**, where the queue rapidly reports that it is full despite most of its memory being empty. Resolving this defect requires mastering **Circular Ring Buffers** via modular arithmetic or deploying **Dual-Pointer Linked Lists** with strict pointer invariants.

---

## 1. Queue Abstract Data Type (ADT) Formal Specification

Mathematically, a Queue $Q$ over an element domain $E$ is an ordered sequence:
$$Q = \langle e_1, e_2, \dots, e_k \rangle$$
where $e_1$ denotes the **Front** of the queue, and $e_k$ denotes the **Rear** of the queue ($k = |Q| \ge 0$).

### Formal State Transition Axioms
1. **`enqueue(e: E) -> Queue`** (also designated `offer`):
   $$\text{enqueue}(\langle e_1, e_2, \dots, e_k \rangle, e) \mapsto \langle e_1, e_2, \dots, e_k, e \rangle$$
   Appends $e$ to the rear of the queue. Cardinality increments $k \leftarrow k + 1$.

2. **`dequeue() -> (E, Queue)`** (also designated `poll`):
   $$\text{dequeue}(\langle e_1, e_2, \dots, e_k \rangle) \mapsto \begin{cases} \text{Error (Underflow)} & \text{if } k = 0 \\ (e_1, \langle e_2, \dots, e_k \rangle) & \text{if } k > 0 \end{cases}$$
   Removes and returns the front element. Cardinality decrements $k \leftarrow k - 1$.

3. **`peek() -> E`**:
   $$\text{peek}(\langle e_1, e_2, \dots, e_k \rangle) \mapsto \begin{cases} \text{Error (Underflow)} & \text{if } k = 0 \\ e_1 & \text{if } k > 0 \end{cases}$$
   Idempotently inspects the front element without state mutation.

```
       DEQUEUE () ◄── [ FRONT ]                                [ REAR ] ◄── ENQUEUE (e)
                         │                                        │
                         ▼                                        ▼
                  ┌──────────────┬──────────────┬───┬──────────────┐
                  │     e_1      │     e_2      │...│     e_k      │
                  └──────────────┴──────────────┴───┴──────────────┘
                    Index: front                      Index: rear
```

---

## 2. Linear Array Storage & The Drifting Boundary Defect

In a naive linear array implementation of size $C$, elements are stored sequentially using two integer pointers: `front` (initialized to $0$) and `rear` (initialized to $-1$).

### 2.1 The "False Full" Catastrophe
Consider a queue initialized with fixed capacity $C = 5$:
1. Perform 5 enqueues: `enqueue(10)`, `20`, `30`, `40`, `50`.
   - `front = 0`, `rear = 4`. The array buffer is full.
2. Perform 3 dequeues: `dequeue()`, `dequeue()`, `dequeue()`.
   - `front = 3`, `rear = 4`. Elements 10, 20, 30 are removed. Slots `[0]`, `[1]`, and `[2]` are completely vacant!
3. Attempt to enqueue a new element `enqueue(60)`:
   - The queue inspects `rear == C - 1` ($4 == 4$).
   - It raises a **Queue Full / Overflow Error**, refusing the insertion!

```
     Slot:      [ 0 ]      [ 1 ]      [ 2 ]      [ 3 ]      [ 4 ]
     State:    VACANT     VACANT     VACANT       40         50
                                                  ▲          ▲
                                                  │          │
                                                front       rear (End of Array!)
     RESULT: Queue has 3 FREE SLOTS, yet CANNOT ACCEPT any new elements!
```

### 2.2 The Flawed Fix: Data Shifting ($O(n)$ Latency Disaster)
Some naive implementations attempt to fix this by shifting all remaining elements to the left by one position upon every dequeue:
```java
// ANTI-PATTERN: DESTROYS QUEUE PERFORMANCE
public T dequeue() {
    if (isEmpty()) throw new NoSuchElementException();
    T item = elements[0];
    for (int i = 0; i < rear; i++) {
        elements[i] = elements[i + 1]; // O(n) array copy on EVERY removal!
    }
    rear--;
    return item;
}
```
Shifting turns dequeue into an expensive $O(n)$ operation. In high-frequency network drivers or event dispatchers processing 100,000 requests per second, this results in immediate CPU saturation and catastrophic latency spikes.

---

## 3. Circular Ring Buffer Architecture (Modulo Arithmetic)

The mathematically optimal solution to the drifting boundary defect is the **Circular Ring Buffer**. Conceptually, index $C - 1$ connects directly back to index $0$, forming a continuous ring. Vacated front slots are seamlessly reused.

```
                               [ 0 ]
                           ┌───────────┐
                    [ 5 ]  │           │  [ 1 ]
                     ┌─────┴───────────┴─────┐
                     │                       │
                     │    CIRCULAR RING      │
                     │       BUFFER          │
                     │     (Capacity N)      │
                     └─────┬───────────┬─────┘
                    [ 4 ]  │           │  [ 2 ]
                           └───────────┘
                               [ 3 ]
```

### 3.1 Modulo Pointer Wrap Equations
To advance pointers around a circular buffer of capacity $N$:
$$\text{rear} \leftarrow (\text{rear} + 1) \pmod N$$
$$\text{front} \leftarrow (\text{front} + 1) \pmod N$$

### 3.2 Resolving the Full vs. Empty Ambiguity
In a circular buffer, both an empty queue and a completely full queue result in `front == rear`. Systems architects use one of two primary strategies to eliminate this ambiguity:

#### Strategy A: Explicit Cardinality Counter (`count`) — *Recommended*
- Maintain an explicit integer `size` (or `count`).
- **Empty State**: `size == 0`.
- **Full State**: `size == capacity`.
- **Advantage**: Uses $100\%$ of array capacity (zero wasted slots) and makes `size()` an instantaneous $O(1)$ query.

#### Strategy B: Sacrificing One Sentinel Slot
- Do not track size; leave one array slot permanently empty.
- **Empty State**: `front == rear`.
- **Full State**: `(rear + 1) % capacity == front`.
- **Disadvantage**: In a buffer of size $N$, only $N - 1$ elements can ever be stored.

---

## 4. Dual-Pointer Linked List Queue Architecture

A linked queue decomposes storage into heap-allocated nodes, dynamically expanding and contracting without capacity constraints.

### 4.1 The Head-as-Front / Tail-as-Rear Invariant
In a Singly Linked List, we maintain two pointers: `head` and `tail`.
- **`dequeue()` at `head`**:
  - `head = head.next` $\implies \mathbf{O(1)}$ strictly guaranteed.
- **`enqueue()` at `tail`**:
  - `tail.next = newNode; tail = newNode;` $\implies \mathbf{O(1)}$ strictly guaranteed.

> [!IMPORTANT]
> **Why the Inverse Architecture Fails:**
> If an architect maps `enqueue` to `head` and `dequeue` to `tail`, `enqueue` remains $O(1)$, but `dequeue` requires deleting the tail node. In a Singly Linked List, advancing the tail pointer backward requires finding the node *preceding* the tail, which forces a full traversal from `head` taking $\mathbf{O(n)}$ time. Thus, **Front MUST be at Head, and Rear MUST be at Tail**.

```
       DEQUEUE()                                             ENQUEUE(item)
          ▲                                                        │
          │                                                        ▼
       [ head ] ──► ┌────────┬──────┐      ┌────────┬──────┐ ◄── [ tail ]
                    │ val: A │ next ├───►  │ val: B │ next ├───► null
                    └────────┴──────┘      └────────┴──────┘
```

---

## 5. Production Java Implementation: Resizing Circular Queue

Below is a production-grade, generic circular array queue featuring dynamic geometric capacity doubling, hysteresis shrinking, and defensive reference clearing to eliminate **memory loitering**.

```java
package edu.se.datastructures.queue;

import java.util.Iterator;
import java.util.NoSuchElementException;

public class ResizingCircularQueue<E> implements Iterable<E> {
    private E[] data;
    private int front;
    private int rear;
    private int size;
    private static final int DEFAULT_CAPACITY = 8;

    @SuppressWarnings("unchecked")
    public ResizingCircularQueue() {
        this.data = (E[]) new Object[DEFAULT_CAPACITY];
        this.front = 0;
        this.rear = 0;
        this.size = 0;
    }

    public int size() {
        return size;
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public void enqueue(E item) {
        if (item == null) throw new IllegalArgumentException("Null elements disallowed");

        // Geometric doubling when buffer is completely filled
        if (size == data.length) {
            resize(data.length * 2);
        }

        data[rear] = item;
        rear = (rear + 1) % data.length;
        size++;
    }

    public E dequeue() {
        if (isEmpty()) throw new NoSuchElementException("Queue underflow");

        E item = data[front];
        data[front] = null; // Prevent object loitering memory leak
        front = (front + 1) % data.length;
        size--;

        // Hysteresis threshold: halve capacity when quarter-full
        if (size > 0 && size == data.length / 4 && data.length / 2 >= DEFAULT_CAPACITY) {
            resize(data.length / 2);
        }

        return item;
    }

    public E peek() {
        if (isEmpty()) throw new NoSuchElementException("Queue underflow");
        return data[front];
    }

    @SuppressWarnings("unchecked")
    private void resize(int newCapacity) {
        E[] newBuffer = (E[]) new Object[newCapacity];
        // Linearize wrapped circular elements into flat contiguous layout
        for (int i = 0; i < size; i++) {
            newBuffer[i] = data[(front + i) % data.length];
        }
        this.data = newBuffer;
        this.front = 0;
        this.rear = size;
    }

    @Override
    public Iterator<E> iterator() {
        return new Iterator<E>() {
            private int index = 0;
            @Override public boolean hasNext() { return index < size; }
            @Override public E next() {
                if (!hasNext()) throw new NoSuchElementException();
                E val = data[(front + index) % data.length];
                index++;
                return val;
            }
        };
    }
}
```

---

## 6. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Trace the state of a Circular Array Queue of capacity $4$ through the following operations:
1. `enqueue(A)`
2. `enqueue(B)`
3. `enqueue(C)`
4. `dequeue()` -> returns A
5. `dequeue()` -> returns B
6. `enqueue(D)`
7. `enqueue(E)`
8. `enqueue(F)`

Record the values of `front`, `rear`, `size`, and the array buffer slots after each step.

<details>
<summary>View Level 1 Solution & State Table</summary>

| Step | Operation | `front` | `rear` | `size` | Array Buffer `[0, 1, 2, 3]` | Architectural Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Initial | - | 0 | 0 | 0 | `[null, null, null, null]` | Empty buffer |
| 1 | `enqueue(A)` | 0 | 1 | 1 | `[A, null, null, null]` | Placed at [0] |
| 2 | `enqueue(B)` | 0 | 2 | 2 | `[A, B, null, null]` | Placed at [1] |
| 3 | `enqueue(C)` | 0 | 3 | 3 | `[A, B, C, null]` | Placed at [2] |
| 4 | `dequeue()` | 1 | 3 | 2 | `[null, B, C, null]` | Front advances to 1; [0] nulled |
| 5 | `dequeue()` | 2 | 3 | 1 | `[null, null, C, null]` | Front advances to 2; [1] nulled |
| 6 | `enqueue(D)` | 2 | 0 | 2 | `[null, null, C, D]` | **Wrap!** $(3+1)\%4 = 0$; placed at [3] |
| 7 | `enqueue(E)` | 2 | 1 | 3 | `[E, null, C, D]` | Reuses vacated slot [0] |
| 8 | `enqueue(F)` | 2 | 2 | 4 | `[E, F, C, D]` | Reuses vacated slot [1]; **Queue Full!** |
</details>

---

### Level 2: Scaffolded System Refactoring — Lock-Free SPSC Ring Buffer
**Problem Statement:** In high-throughput messaging architectures (like the LMAX Disruptor), locks introduce severe operating system kernel context-switch penalties. Implement a lock-free Single-Producer Single-Consumer (SPSC) circular queue using volatile memory barriers and power-of-two bitwise masking.

<details>
<summary>View Complete Java SPSC Lock-Free Implementation</summary>

```java
package edu.se.datastructures.concurrency;

/**
 * Lock-Free Single-Producer Single-Consumer (SPSC) Ring Buffer.
 * Exploits bitwise masking (mask = capacity - 1) and volatile memory fences.
 */
public final class SpscArrayQueue<E> {
    private final E[] buffer;
    private final int mask;

    // Separate cache lines to eliminate false sharing (CPU cache ping-pong)
    private volatile long head = 0; // Read by consumer
    private volatile long tail = 0; // Written by producer

    @SuppressWarnings("unchecked")
    public SpscArrayQueue(int capacityPowerOfTwo) {
        if (Integer.bitCount(capacityPowerOfTwo) != 1) {
            throw new IllegalArgumentException("Capacity must be an exact power of two");
        }
        this.buffer = (E[]) new Object[capacityPowerOfTwo];
        this.mask = capacityPowerOfTwo - 1;
    }

    public boolean offer(E item) {
        if (item == null) throw new NullPointerException();
        long currentTail = tail;
        long currentHead = head;

        if (currentTail - currentHead >= buffer.length) {
            return false; // Queue buffer full
        }

        buffer[(int) (currentTail & mask)] = item;
        tail = currentTail + 1; // Volatile release barrier
        return true;
    }

    public E poll() {
        long currentHead = head;
        if (currentHead >= tail) {
            return null; // Queue buffer empty
        }

        int index = (int) (currentHead & mask);
        E item = buffer[index];
        buffer[index] = null; // Prevent loitering
        head = currentHead + 1; // Volatile release barrier
        return item;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Telemetry Batcher with Backpressure
**Problem Statement:** Build an industrial telemetry batch collector. Worker threads push metrics into a bounded queue. A background dispatch thread pulls batches when either: (a) batch size reaches $K$ items, or (b) a maximum timeout $T$ milliseconds elapses. If the queue is full, apply a Drop-Oldest backpressure policy.

<details>
<summary>View Bounded Batcher Architecture Implementation</summary>

```java
package edu.se.datastructures.telemetry;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;

public class TelemetryBatcher<T> {
    private final BlockingQueue<T> queue;
    private final int batchSize;
    private final long maxWaitMs;

    public TelemetryBatcher(int queueCapacity, int batchSize, long maxWaitMs) {
        this.queue = new ArrayBlockingQueue<>(queueCapacity);
        this.batchSize = batchSize;
        this.maxWaitMs = maxWaitMs;
    }

    public synchronized void publish(T metric) {
        while (!queue.offer(metric)) {
            // Drop-Oldest Backpressure Policy: Drop front to make room for newest
            queue.poll();
        }
    }

    public List<T> drainBatch() throws InterruptedException {
        List<T> batch = new ArrayList<>(batchSize);
        long deadline = System.currentTimeMillis() + maxWaitMs;

        while (batch.size() < batchSize) {
            long remaining = deadline - System.currentTimeMillis();
            if (remaining <= 0 && !batch.isEmpty()) break;

            T item = queue.poll(Math.max(1, remaining), TimeUnit.MILLISECONDS);
            if (item != null) {
                batch.add(item);
            } else if (System.currentTimeMillis() >= deadline) {
                break;
            }
        }
        return batch;
    }
}
```
</details>
