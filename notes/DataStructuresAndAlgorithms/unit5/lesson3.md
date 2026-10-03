# Lesson 3 — Priority Queues, Binary Heaps & Enterprise Scheduling Engines

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the **Priority Queue ADT** contract, distinguishing key-ordered extraction from standard chronological FIFO ordering.
> - Map a **Complete Binary Tree** onto a contiguous flat array using mathematical index relationships without pointer overhead.
> - Derive the algorithmic mechanics and complexity of **Sift-Up (Bubble-Up)** and **Sift-Down (Heapify)** mutations.
> - Contrast repeated insertion ($O(n \log n)$) with **Floyd's Bottom-Up Linear Heap Construction ($O(n)$)**.
> - Engineer an **Indexed Priority Queue (IPQ)** enabling $O(\log n)$ `decreaseKey` operations for Dijkstra's and Prim's graph algorithms.

{{media:priority-video}}

{{media:priority-visual}}

## Executive Summary & Industrial Positioning

While standard queues enforce strict First-In, First-Out (FIFO) processing based purely on the arrival timestamp, real-world distributed architectures, operating systems, and network protocols require processing jobs according to **relative urgency, severity, or quality of service (QoS)**. In a hospital emergency room, a trauma patient must be treated before someone with a minor fracture regardless of who arrived first; similarly, in an operating system kernel, real-time audio threads preempt background disk indexing.

The **Priority Queue** is the Abstract Data Type (ADT) that governs these dynamics. While implementing a priority queue via linked lists or unsorted arrays incurs crippling $O(n)$ penalties for either insertion or extraction, implementing it via a **Binary Heap** delivers guaranteed $O(\log n)$ worst-case bounds for all mutations and $O(1)$ instantaneous inspection of the highest-priority element.

---

## 1. Priority Queue ADT & Queue Merging/Demerging

A Priority Queue stores key-value records where each element $e$ has an associated priority key $p \in K$ governed by a total order relation ($\le$).

### 1.1 Fundamental Operations
- **`insert(e, p)`**: Adds element $e$ with priority $p$.
- **`extractMax()` / `extractMin()`**: Removes and returns the element with the maximum (or minimum) priority.
- **`peek()`**: Returns the element with the highest priority without removal.

### 1.2 Curriculum Case Study: Queue Demerging & Merging (Slides 29–35)
In distributed message routing and curriculum systems, engineers frequently split and combine priority streams:

#### Demerging Queues (Categorical Splitting)
Separates a mixed-priority queue into discrete sub-queues based on categorization attributes (e.g., splitting interactive tasks from batch tasks, or the curriculum example of separating gender queues):
```java
// Demerging Algorithm: O(n) linear segregation
while (!priorityQueue.isEmpty()) {
    Record r = priorityQueue.dequeue();
    if (r.priorityLevel() == HIGH) {
        highPriorityQueue.enqueue(r);
    } else {
        lowPriorityQueue.enqueue(r);
    }
}
```

#### Merging Queues (Priority Reconstitution)
Recombines distinct sub-queues into a unified priority queue by sequentially draining high-priority streams before lower-priority streams:
```java
// Merging Algorithm: Preserves tiered dominance
while (!highPriorityQueue.isEmpty()) {
    unifiedQueue.enqueue(highPriorityQueue.dequeue());
}
while (!lowPriorityQueue.isEmpty()) {
    unifiedQueue.enqueue(lowPriorityQueue.dequeue());
}
```

---

## 2. Storage Topology Trade-Off Matrix

| Underlying Storage Topology | `insert(e, p)` Time | `extractMax()` Time | `peek()` Time | Architectural Bottleneck |
| :--- | :--- | :--- | :--- | :--- |
| **Unsorted Contiguous Array** | $\mathbf{O(1)}$ (Append) | $\mathbf{O(n)}$ (Linear scan) | $O(n)$ | Dequeue forces full array scan |
| **Unsorted Singly Linked List** | $\mathbf{O(1)}$ (Prepend) | $\mathbf{O(n)}$ (Linear scan) | $O(n)$ | Dequeue forces full node traversal |
| **Sorted Contiguous Array** | $\mathbf{O(n)}$ (Insertion shift)| $\mathbf{O(1)}$ (Pop end) | $O(1)$ | Enqueue forces $O(n)$ memory shift |
| **Sorted Singly Linked List** | $\mathbf{O(n)}$ (Insertion traversal)| $\mathbf{O(1)}$ (Pop head)| $O(1)$ | Enqueue forces linear search |
| **Binary Heap (Implicit Array)**| $\mathbf{O(\log n)}$ | $\mathbf{O(\log n)}$ | $\mathbf{O(1)}$ | **Optimal balance of insertion and extraction** |

---

## 3. Binary Heap Architecture: Implicit Array Mathematics

A **Binary Heap** is a complete binary tree that satisfies the **Heap Order Property**:
- **Max-Heap**: For every node $i$ other than the root, $\text{key}(\text{parent}(i)) \ge \text{key}(i)$.
- **Min-Heap**: For every node $i$ other than the root, $\text{key}(\text{parent}(i)) \le \text{key}(i)$.

Because a binary heap is guaranteed to be a **Complete Binary Tree** (every level is fully filled except possibly the last level, which is filled sequentially from left to right), it can be mapped into a single contiguous flat array **without storing any pointer references**.

```
                [0] 40                       Array Layout:
               /      \                      Index: [ 0 |  1 |  2 |  3 |  4 |  5 |  6 ]
          [1] 30      [2] 25                 Value: [40 | 30 | 25 | 15 | 18 | 20 | 12 ]
          /    \      /    \
       [3]15  [4]18 [5]20  [6]12
```

### 3.1 Pointer-Free Index Equations (0-Indexed Array)
For any element at index $i$:
$$\text{parent}(i) = \left\lfloor \frac{i - 1}{2} \right\rfloor$$
$$\text{leftChild}(i) = 2i + 1$$
$$\text{rightChild}(i) = 2i + 2$$

---

## 4. Heap Restructuring Dynamics: Sift-Up & Sift-Down

### 4.1 Insertion (`siftUp` / Bubble-Up) — $O(\log n)$
When a new element is added to the heap:
1. Append the element to the end of the array (preserving the complete tree shape).
2. Compare the element with its parent.
3. If the heap invariant is violated, swap the element with its parent.
4. Repeat upward until the heap property is satisfied or the element reaches the root ($i = 0$).

$$\text{Maximum Swaps} = \text{Tree Height} = \lfloor \log_2 n \rfloor \implies \mathbf{O(\log n)}$$

```java
private void siftUp(int index) {
    E target = heap[index];
    while (index > 0) {
        int parentIdx = (index - 1) >>> 1; // Integer division by 2
        E parent = heap[parentIdx];
        if (target.compareTo(parent) <= 0) break; // Invariant satisfied
        heap[index] = parent; // Push parent down
        index = parentIdx;
    }
    heap[index] = target;
}
```

### 4.2 Extraction (`siftDown` / Heapify) — $O(\log n)$
When extracting the root (maximum or minimum):
1. Save the root element to return.
2. Move the **last element** in the array into the root slot ($i = 0$), and decrement the heap size.
3. Compare the new root with its children.
4. Swap the element with its **larger child** (for max-heap) or **smaller child** (for min-heap).
5. Repeat downward until the heap property is satisfied or a leaf position is reached.

```java
private void siftDown(int index) {
    E target = heap[index];
    int half = size >>> 1; // Non-leaf nodes boundary

    while (index < half) {
        int child = (index << 1) + 1; // Left child
        E rightChild = (child + 1 < size) ? heap[child + 1] : null;

        // Choose larger child
        if (rightChild != null && rightChild.compareTo(heap[child]) > 0) {
            child++;
        }

        if (target.compareTo(heap[child]) >= 0) break; // Invariant satisfied
        heap[index] = heap[child]; // Pull child up
        index = child;
    }
    heap[index] = target;
}
```

---

## 5. Floyd's Bottom-Up Linear Heap Construction: $O(n)$

Suppose we are given an unsorted array of $n$ elements. How quickly can we convert it into a valid heap?

### Repeated Insertion vs. Floyd's Algorithm
- **Naive Approach (Repeated Insertion)**: Call `insert()` $n$ times $\implies \sum_{i=1}^n \log i = \mathbf{O(n \log n)}$.
- **Floyd's Algorithm (`buildHeap`)**: Treat the raw array as a complete binary tree. All leaf nodes (from index $\lfloor n/2 \rfloor$ to $n - 1$) already trivially satisfy the heap property! We simply iterate **backward** from the last non-leaf node down to the root, executing `siftDown()` at each node:

```java
public void buildHeap(E[] array) {
    this.heap = array;
    this.size = array.length;
    // Start at last non-leaf parent: (size / 2) - 1
    for (int i = (size >>> 1) - 1; i >= 0; i--) {
        siftDown(i);
    }
}
```

### Mathematical Proof of $O(n)$ Runtime
In a complete binary tree of height $h \approx \log_2 n$:
- There are $\approx n / 2^{k+1}$ nodes at height $k$.
- A node at height $k$ can sift down at most $k$ levels.
- Total operations:
$$T(n) = \sum_{k=0}^h \frac{n}{2^{k+1}} \cdot k = \frac{n}{2} \sum_{k=0}^\infty \frac{k}{2^k}$$
Using the standard mathematical summation identity $\sum_{k=0}^\infty \frac{k}{2^k} = 2$:
$$T(n) \le \frac{n}{2} \times 2 = \mathbf{O(n)}$$
Floyd's algorithm constructs a heap in **strictly linear time**!

---

## 6. Operating System Task Scheduling & Multilevel Feedback Queues

In operating systems (such as the Linux kernel or FreeBSD), the task scheduler orchestrates CPU access among hundreds of competing threads using priority queues.

```
       [ READY PROCESSES ]
                │
                ▼
       ┌────────────────────────────────────────────────────────┐
       │ Priority Queue Q0: Real-Time / Interactive (Quantum=8ms)│ ◄── Highest Priority
       └────────────────────────┬───────────────────────────────┘
                                │ (Demoted on Quantum Expiry)
                                ▼
       ┌────────────────────────────────────────────────────────┐
       │ Priority Queue Q1: Standard Priority Tasks (Quantum=16ms)│
       └────────────────────────┬───────────────────────────────┘
                                │ (Demoted on Quantum Expiry)
                                ▼
       ┌────────────────────────────────────────────────────────┐
       │ Priority Queue Q2: Batch CPU-Bound Tasks (Quantum=32ms) │ ◄── Lowest Priority
       └────────────────────────────────────────────────────────┘
```

### The Starvation Hazard & Anti-Starvation Aging
If high-priority tasks continuously arrive, batch tasks in lower queues will never execute, suffering from **Starvation (Livelock)**.
- **Remedy: Dynamic Aging**:
  Every $T$ milliseconds, the kernel sweeps waiting threads. Any process that has waited in a lower queue for longer than a threshold has its priority key boosted:
  $$\text{priority} \leftarrow \text{priority} + \Delta p$$
  This guarantees that every thread eventually ascends to the highest queue, ensuring deterministic execution fairness.

---

## 7. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Given the initial Max-Heap array:
`[ 40, 30, 25, 15, 18, 20, 12 ]`
Trace the array contents through:
1. `insert(35)`
2. `extractMax()`

<details>
<summary>View Level 1 Step-by-Step Heap Trace</summary>

**Step 1: `insert(35)`**
1. Append 35 at index 7: `[ 40, 30, 25, 15, 18, 20, 12, 35 ]`.
2. Compare with parent at $\lfloor (7 - 1) / 2 \rfloor = 3$ (value 15). Since $35 > 15$, swap:
   `[ 40, 30, 25, 35, 18, 20, 12, 15 ]`.
3. Compare with parent at $\lfloor (3 - 1) / 2 \rfloor = 1$ (value 30). Since $35 > 30$, swap:
   `[ 40, 35, 25, 30, 18, 20, 12, 15 ]`.
4. Compare with parent at $\lfloor (1 - 1) / 2 \rfloor = 0$ (value 40). Since $35 \le 40$, stop.
   **Result:** `[ 40, 35, 25, 30, 18, 20, 12, 15 ]`.

**Step 2: `extractMax()`**
1. Root 40 is extracted.
2. Move last element (15 at index 7) to root:
   `[ 15, 35, 25, 30, 18, 20, 12 ]` (size = 7).
3. `siftDown(0)`: Children of 15 are index 1 (35) and index 2 (25). Larger child is 35. Swap with index 1:
   `[ 35, 15, 25, 30, 18, 20, 12 ]`.
4. Children of 15 are index 3 (30) and index 4 (18). Larger child is 30. Swap with index 3:
   `[ 35, 30, 25, 15, 18, 20, 12 ]`.
5. Index 3 has no valid children in bounds ($2 \times 3 + 1 = 7 \ge \text{size}$). Stop.
   **Final Array:** `[ 35, 30, 25, 15, 18, 20, 12 ]`.
</details>

---

### Level 2: Scaffolded System Refactoring — Indexed Priority Queue (IPQ)
**Problem Statement:** In Dijkstra's Algorithm and Prim's Minimum Spanning Tree, we frequently need to update the priority of an arbitrary vertex ($O(\log n)$ `decreaseKey`). A standard `PriorityQueue` takes $O(n)$ to locate the item. Implement an **Indexed Priority Queue** that maintains an inverse position map to execute `decreaseKey` in strictly $O(\log n)$ time.

<details>
<summary>View Complete Java Indexed Priority Queue Implementation</summary>

```java
package edu.se.datastructures.priority;

import java.util.NoSuchElementException;

public class IndexMinPQ<Key extends Comparable<Key>> {
    private int maxN;        // Maximum number of elements
    private int n;           // Number of elements in PQ
    private int[] pq;        // Binary heap using 1-based indexing (stores keys' IDs)
    private int[] qp;        // Inverse of pq: qp[i] gives index of ID i in pq[] (-1 if absent)
    private Key[] keys;      // keys[i] = priority of ID i

    @SuppressWarnings("unchecked")
    public IndexMinPQ(int maxN) {
        this.maxN = maxN;
        this.n = 0;
        this.keys = (Key[]) new Comparable[maxN + 1];
        this.pq = new int[maxN + 1];
        this.qp = new int[maxN + 1];
        for (int i = 0; i <= maxN; i++) qp[i] = -1;
    }

    public boolean contains(int i) {
        return qp[i] != -1;
    }

    public void insert(int i, Key key) {
        if (contains(i)) throw new IllegalArgumentException("Index already in PQ");
        n++;
        qp[i] = n;
        pq[n] = i;
        keys[i] = key;
        swim(n);
    }

    public int delMin() {
        if (n == 0) throw new NoSuchElementException("PQ underflow");
        int minId = pq[1];
        exch(1, n--);
        sink(1);
        qp[minId] = -1;
        keys[minId] = null;
        return minId;
    }

    public void decreaseKey(int i, Key key) {
        if (!contains(i)) throw new NoSuchElementException();
        if (keys[i].compareTo(key) <= 0) throw new IllegalArgumentException("New key must be strictly smaller");
        keys[i] = key;
        swim(qp[i]); // Sift-up in O(log n) using inverse map pointer!
    }

    private void swim(int k) {
        while (k > 1 && greater(k / 2, k)) {
            exch(k, k / 2);
            k = k / 2;
        }
    }

    private void sink(int k) {
        while (2 * k <= n) {
            int j = 2 * k;
            if (j < n && greater(j, j + 1)) j++;
            if (!greater(k, j)) break;
            exch(k, j);
            k = j;
        }
    }

    private boolean greater(int i, int j) {
        return keys[pq[i]].compareTo(keys[pq[j]]) > 0;
    }

    private void exch(int i, int j) {
        int swap = pq[i];
        pq[i] = pq[j];
        pq[j] = swap;
        qp[pq[i]] = i;
        qp[pq[j]] = j;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Multi-Tenant Task Scheduler with Aging
**Problem Statement:** Design a multi-tenant task scheduler queue where jobs possess base priorities (1 to 10). To prevent starvation of low-priority batch jobs during traffic bursts, implement an internal aging clock where effective priority increases dynamically with wait time:
$$\text{effectivePriority} = \text{basePriority} + (\text{currentTimestamp} - \text{enqueueTimestamp}) \times \alpha$$

<details>
<summary>View Multi-Tenant Aging Scheduler Implementation</summary>

```java
package edu.se.datastructures.scheduling;

import java.util.PriorityQueue;

public class StarvationFreeTaskScheduler {
    public static class Task implements Comparable<Task> {
        final String taskId;
        final int basePriority;
        final long enqueueTime;
        final double alpha; // Aging coefficient

        public Task(String taskId, int basePriority, double alpha) {
            this.taskId = taskId;
            this.basePriority = basePriority;
            this.enqueueTime = System.currentTimeMillis();
            this.alpha = alpha;
        }

        public double getEffectivePriority(long now) {
            long waitTime = now - enqueueTime;
            return basePriority + (waitTime * alpha);
        }

        @Override
        public int compareTo(Task other) {
            long now = System.currentTimeMillis();
            // Higher effective priority executed first (Max-Heap order)
            return Double.compare(other.getEffectivePriority(now), this.getEffectivePriority(now));
        }
    }

    private final PriorityQueue<Task> taskQueue = new PriorityQueue<>();

    public synchronized void submitTask(Task task) {
        taskQueue.offer(task);
    }

    public synchronized Task pollNextTask() {
        return taskQueue.poll();
    }

    public synchronized int pendingTasks() {
        return taskQueue.size();
    }
}
```
</details>
