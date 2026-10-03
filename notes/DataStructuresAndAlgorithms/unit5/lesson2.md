# Lesson 2 — Double-Ended Queues (Deque) & Monotonic Queue Architectures

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the formal contract of the **Double-Ended Queue (Deque)** supporting bidirectional mutations.
> - Dissect the high-performance memory model of `java.util.ArrayDeque` utilizing power-of-two circular bitwise masking.
> - Implement the **Monotonic Queue** algorithmic paradigm to compute sliding window extrema in strictly amortized $O(n)$ time.
> - Analyze multi-threaded **Work-Stealing Schedulers** (JVM ForkJoinPool, Go runtime, Rust Tokio) utilizing dual-ended operational topologies.
> - Compare why `ArrayDeque` fundamentally outperforms `LinkedList` and legacy `Stack` across modern hardware memory hierarchies.

{{media:deque-video}}

{{media:deque-visual}}

## Executive Summary & Industrial Positioning

A **Double-Ended Queue (Deque)**, pronounced *"deck"*, generalizes both Stacks and Queues by permitting insertions and deletions at both extremities: the **Front (Head)** and the **Rear (Tail)**. This dual-ended capability allows a Deque to function simultaneously as a LIFO Stack, a FIFO Queue, or a bidirectional scroll buffer.

In modern systems engineering, Deques play two pivotal roles:
1. **Algorithmic Optimizations**: The **Monotonic Deque** pattern transforms polynomial $O(n \cdot k)$ sliding window analytics into optimal $O(n)$ linear scans by pruning redundant elements.
2. **High-Concurrency Task Scheduling**: Parallel runtimes—including the Java Virtual Machine's **ForkJoinPool**, the **Go runtime scheduler**, and Rust's **Tokio** runtime—rely on Deques for **Work-Stealing**, where worker threads execute their own tasks from one end (LIFO for cache warmth) while idle workers steal stalled tasks from the opposite end (FIFO for fairness).

---

## 1. Deque Abstract Data Type (ADT) Specification

A Deque provides symmetric operations across both endpoints:

| Operation | Head (Front) Boundary | Tail (Rear) Boundary | Semantic Behavior |
| :--- | :--- | :--- | :--- |
| **Insert** | `addFirst(e)` / `offerFirst(e)` | `addLast(e)` / `offerLast(e)` | Pushes item to specified extremity |
| **Remove** | `removeFirst()` / `pollFirst()` | `removeLast()` / `pollLast()` | Pops and returns item from specified extremity |
| **Examine** | `getFirst()` / `peekFirst()` | `getLast()` / `peekLast()` | Inspects item without modifying state |

```
    addFirst(e) ──► ┌───────────────────────────────────────┐ ◄── addLast(e)
                    │  [ FRONT ]  ...  BUFFER  ...  [ REAR ]│
 removeFirst() ◄── └───────────────────────────────────────┘ ──► removeLast()
```

---

## 2. Concrete Storage Architectures & ArrayDeque Internals

To implement a Deque efficiently, architects choose between a **Doubly Linked List** and a **Circular Resizable Array**.

### 2.1 The Java `ArrayDeque` Power-of-Two Optimization
In standard circular arrays, advancing or decrementing an index requires the integer modulo operator `%`:
$$\text{newHead} = (\text{head} - 1 + N) \pmod N$$
However, integer division and remainder instructions (`idiv` in x86 assembly) consume $10\text{--}20$ CPU clock cycles. To achieve peak throughput, `java.util.ArrayDeque` mandates that the buffer capacity $N$ is always a **strict power of two** ($N = 2^p$). When $N$ is a power of two, modulo arithmetic is replaced with an instantaneous, single-cycle **bitwise AND operation**:
$$X \pmod N \equiv X \ \& \ (N - 1)$$

### 2.2 Decrementing and Incrementing with Bitwise Masking
```java
// Prepend to front:
head = (head - 1) & (elements.length - 1);
elements[head] = item;

// Append to rear:
elements[tail] = item;
tail = (tail + 1) & (elements.length - 1);
```
If `head` is initially $0$ and capacity is $16$ (mask $= 15 = 00001111_2$):
$$(0 - 1) \ \& \ 15 = -1 \ \& \ 15 = 11111111_2 \ \& \ 00001111_2 = 15$$
The pointer wraps seamlessly to the highest index in a single CPU instruction!

---

## 3. Comparative Architecture: `ArrayDeque` vs. `LinkedList` vs. `Stack`

Why does Oracle's Java documentation explicitly mandate: *"ArrayDeque is likely to be faster than Stack when used as a stack, and faster than LinkedList when used as a queue"*?

| Dimension | `java.util.ArrayDeque` | `java.util.LinkedList` | `java.util.Stack` |
| :--- | :--- | :--- | :--- |
| **Physical Topology** | Contiguous circular array buffer | Non-contiguous doubly linked nodes | Contiguous array (extends `Vector`) |
| **Thread Safety** | Non-synchronized (Ultra-fast) | Non-synchronized | **Synchronized on every call** (Heavy lock overhead) |
| **Node Allocation** | **Zero per push** (amortized array resize) | **1 Node object per push** (GC thrashing) | Zero per push |
| **Memory Overhead** | 4–8 bytes per slot | **24–32 bytes per node** | 4–8 bytes per slot |
| **CPU Cache Locality** | **High** (contiguous sequential stride) | **Extremely Poor** (pointer chasing) | High |
| **Null Storage** | Disallowed (`NullPointerException`) | Allowed | Allowed |

---

## 4. The Monotonic Queue Algorithmic Pattern

In streaming analytics and time-series monitoring, a frequent requirement is computing the running maximum or minimum across a moving window of size $k$ over a stream of $n$ numbers (**Sliding Window Maximum**).

### 4.1 The Naive vs. Optimal Complexity
- **Naive Window Scan**: For every window position, scan all $k$ elements to find the maximum $\implies \mathbf{O(n \cdot k)}$. If $k = 50,000$ and $n = 10,000,000$, this approach is completely unfeasible.
- **Priority Queue (Heap)**: Insert incoming element, remove outgoing element $\implies \mathbf{O(n \log k)}$.
- **Monotonic Deque**: Maintains indices in strictly descending order of their values. Achieves strictly guaranteed $\mathbf{O(n)}$ total runtime ($\mathbf{O(1)}$ amortized per element)!

### 4.2 Invariant Enforcement Rules
For each new element $x$ at index $i$:
1. **Evict Out-of-Bounds Indices (Front)**:
   If `deque.peekFirst() <= i - k`, the current window has moved past this index; pop it from the front.
2. **Maintain Strict Monotonicity (Rear)**:
   While `!deque.isEmpty() && array[deque.peekLast()] <= x`:
   Pop from the rear! Any element smaller than $x$ that appeared *before* $x$ can **never** be the maximum of this or any future window because $x$ is both larger and younger.
3. **Push New Element**:
   `deque.addLast(i)`.
4. **Extract Window Max**:
   The maximum of the current window is always unconditionally at the **Front** of the Deque: `array[deque.peekFirst()]`.

```
      Array: [ 1,  3, -1, -3,  5,  3,  6,  7 ],  k = 3

      Window [1, 3, -1] -> 3 dominates 1 (evicts 1 from rear) -> Deque: [3, -1] -> Max = 3
      Window [3, -1, -3]-> -3 enters                          -> Deque: [3, -1, -3] -> Max = 3
      Window [-1, -3, 5]-> 5 enters! Dominates 3, -1, -3      -> Deque: [5]        -> Max = 5
```

---

## 5. Multiprocessor Work-Stealing Scheduling Architecture

In modern concurrent runtime systems, idle CPU cores must not sit dormant while busy cores drown in tasks. **Work-Stealing** balances load across $P$ processor threads using double-ended queues.

```
       Worker Thread A (Busy):                    Worker Thread B (Idle):
         ┌──────────────────────────────┐           ┌──────────────────────────────┐
         │ Local Deque A                │           │ Local Deque B (EMPTY)        │
         │                              │           │                              │
  POP ◄──┤ [ TOP ] Task 1 (Local Worker)│           │                              │
 PUSH ──►│         Task 2 (LIFO)        │           │                              │
         │         Task 3               │           │                              │
         │ [ BOTTOM ] Task 4            │           │                              │
         └──────────────┬───────────────┘           └──────────────────────────────┘
                        │                                          ▲
                        └──────────── STEAL TASK (FIFO) ───────────┘
```

1. **Local Execution (LIFO at Top)**:
   - Each worker pushes newly spawned tasks to the **Top** of its private Deque and pops from the **Top**.
   - Operating in LIFO order ensures that the most recently created sub-tasks are executed first, maximizing CPU L1/L2 cache data warmth.
2. **Stealing from Peers (FIFO at Bottom)**:
   - When a worker empties its private queue, it becomes a "thief" and steals a task from the **Bottom** of a victim peer's Deque.
   - Stealing from the bottom accesses the oldest, coarsest-grained parent task, reducing subsequent steal attempts.
   - Accessing opposite ends of the Deque dramatically minimizes lock and cache-line contention between the owner and the thief!

---

## 6. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Given the circular array Deque of initial capacity $8$ (with bitwise mask $7$):
Trace the values of `head`, `tail`, and array contents when the following operations execute on an empty deque (`head = 0`, `tail = 0`):
1. `addLast(10)`
2. `addFirst(20)`
3. `addFirst(30)`
4. `addLast(40)`
5. `removeFirst()`
6. `removeLast()`

<details>
<summary>View Level 1 Trace & Bitwise Calculations</summary>

| Step | Operation | Pointer Math | `head` | `tail` | Buffer `[0, 1, 2, 3, 4, 5, 6, 7]` | Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Init | - | - | 0 | 0 | `[_, _, _, _, _, _, _, _]` | Empty Deque |
| 1 | `addLast(10)` | `tail = (0 + 1) & 7 = 1` | 0 | 1 | `[10, _, _, _, _, _, _, _]` | Placed at [0] |
| 2 | `addFirst(20)` | `head = (0 - 1) & 7 = 7` | 7 | 1 | `[10, _, _, _, _, _, _, 20]` | Placed at [7] |
| 3 | `addFirst(30)` | `head = (7 - 1) & 7 = 6` | 6 | 1 | `[10, _, _, _, _, _, 30, 20]` | Placed at [6] |
| 4 | `addLast(40)` | `tail = (1 + 1) & 7 = 2` | 6 | 2 | `[10, 40, _, _, _, _, 30, 20]` | Placed at [1] |
| 5 | `removeFirst()` | returns 30; `head = (6 + 1) & 7 = 7` | 7 | 2 | `[10, 40, _, _, _, _, _, 20]` | [6] cleared |
| 6 | `removeLast()` | `tail = (2 - 1) & 7 = 1`; returns 40 | 7 | 1 | `[10, _, _, _, _, _, _, 20]` | [1] cleared |
</details>

---

### Level 2: Scaffolded System Refactoring — Monotonic Sliding Window Max
**Problem Statement:** Implement the complete, production-ready `maxSlidingWindow(int[] nums, int k)` algorithm in Java using `ArrayDeque`. Handle edge conditions where $k \ge n$ and empty input arrays.

<details>
<summary>View Complete Java Monotonic Deque Implementation</summary>

```java
package edu.se.datastructures.slidingwindow;

import java.util.ArrayDeque;
import java.util.Deque;

public class SlidingWindowMaxFinder {

    public static int[] maxSlidingWindow(int[] nums, int k) {
        if (nums == null || nums.length == 0 || k <= 0) return new int[0];
        if (k == 1) return nums;

        int n = nums.length;
        int[] result = new int[n - k + 1];
        int resultIdx = 0;

        // Stores INDICES of elements in strictly decreasing order of value
        Deque<Integer> deque = new ArrayDeque<>();

        for (int i = 0; i < n; i++) {
            // 1. Remove elements outside current sliding window boundary
            if (!deque.isEmpty() && deque.peekFirst() <= i - k) {
                deque.pollFirst();
            }

            // 2. Monotonic invariant: evict from rear any element <= current element
            while (!deque.isEmpty() && nums[deque.peekLast()] <= nums[i]) {
                deque.pollLast();
            }

            // 3. Add current element index to rear
            deque.offerLast(i);

            // 4. Record current window maximum once first window of size k is formed
            if (i >= k - 1) {
                result[resultIdx++] = nums[deque.peekFirst()];
            }
        }

        return result;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Lock-Free Work-Stealing Deque
**Problem Statement:** Design a concurrent work-stealing Deque based on the Chase-Lev algorithm. The local worker thread must perform `pushBottom` and `popBottom` with minimal synchronization, while concurrent thief threads invoke `stealTop` using Atomic Compare-And-Swap (CAS).

<details>
<summary>View Chase-Lev Work-Stealing Deque Implementation</summary>

```java
package edu.se.datastructures.concurrent;

import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReferenceArray;

public class WorkStealingDeque<E> {
    private static final int INITIAL_CAPACITY = 1024;
    private final AtomicReferenceArray<E> buffer = new AtomicReferenceArray<>(INITIAL_CAPACITY);
    private final int mask = INITIAL_CAPACITY - 1;

    private final AtomicLong top = new AtomicLong(0);    // Modified by thieves (CAS)
    private volatile long bottom = 0;                    // Modified exclusively by owner

    // Owner Thread: Push to bottom (LIFO)
    public void pushBottom(E item) {
        long b = bottom;
        buffer.set((int) (b & mask), item);
        bottom = b + 1; // Volatile release
    }

    // Owner Thread: Pop from bottom (LIFO)
    public E popBottom() {
        long b = bottom - 1;
        bottom = b;
        long t = top.get();

        if (b < t) {
            bottom = t; // Queue was already empty
            return null;
        }

        E item = buffer.get((int) (b & mask));
        if (b > t) {
            buffer.set((int) (b & mask), null);
            return item;
        }

        // Single element remaining: race against concurrent thief!
        if (!top.compareAndSet(t, t + 1)) {
            item = null; // Thief won the race and stole the item
        }
        bottom = t + 1;
        return item;
    }

    // Thief Thread: Steal from top (FIFO)
    public E stealTop() {
        while (true) {
            long t = top.get();
            long b = bottom;
            if (t >= b) return null; // Deque empty

            E item = buffer.get((int) (t & mask));
            if (top.compareAndSet(t, t + 1)) {
                return item; // Successfully stolen!
            }
        }
    }
}
```
</details>
