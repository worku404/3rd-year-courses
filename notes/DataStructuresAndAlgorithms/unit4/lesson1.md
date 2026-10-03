# Lesson 1 — Stack Abstract Data Type & Storage Architectures (Array vs Linked List)

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the mathematical axioms governing the **Last-In, First-Out (LIFO)** Abstract Data Type (ADT).
> - Architect a production-grade contiguous array-backed stack with dynamic capacity scaling and memory leak prevention (**loitering de-referencing**).
> - Implement a singly linked list stack utilizing the **Head-as-Top** invariant for guaranteed strict $O(1)$ mutation boundaries.
> - Quantify memory layout costs and CPU hardware cache locality trade-offs (L1/L2 prefetching vs. heap node fragmentation).
> - Deconstruct concurrent lock-free stack topologies (**Treiber Stack**) utilizing Atomic Compare-And-Swap (CAS) primitives.

{{media:stack-video}}

{{media:stack-visual}}

## Executive Summary & Architectural Positioning

The **Stack** is a fundamental linear Abstract Data Type (ADT) governed by a strictly constrained access discipline: insertion and deletion are permissible exclusively at a single designated boundary known as the **Top**. This operational constraint enforces **Last-In, First-Out (LIFO)** ordering, establishing the stack as the computational backbone of execution runtimes, syntax parsers, memory evaluators, and state backtracking engines.

While the semantic interface of a stack consists of only a few elementary methods (`push`, `pop`, `peek`, `isEmpty`), the concrete physical storage topology chosen beneath this abstraction fundamentally impacts runtime execution characteristics. Software engineers must navigate critical trade-offs between **contiguous memory buffers (Arrays)**—which maximize CPU cache locality but risk allocation spikes—and **dynamic node graphs (Linked Lists)**—which guarantee zero-latency spikes at the expense of severe reference memory overhead and CPU cache thrashing.

---

## 1. Stack Abstract Data Type (ADT) Formal Specification

Mathematically, a Stack $S$ over an element domain $E$ is an ordered sequence:
$$S = \langle e_1, e_2, \dots, e_k \rangle$$
where $e_1$ denotes the **Bottom** of the stack, and $e_k$ denotes the **Top** of the stack ($k = |S| \ge 0$).

### Formal State Axioms
The stack ADT is formally specified by four fundamental operations mapping state transitions:

1. **`push(e: E) -> Stack`**:
   $$\text{push}(\langle e_1, e_2, \dots, e_k \rangle, e) \mapsto \langle e_1, e_2, \dots, e_k, e \rangle$$
   Increments cardinality $k \leftarrow k + 1$. The newly inserted item becomes the immediate top.

2. **`pop() -> (E, Stack)`**:
   $$\text{pop}(\langle e_1, e_2, \dots, e_k \rangle) \mapsto \begin{cases} \text{Error (Underflow)} & \text{if } k = 0 \\ (e_k, \langle e_1, e_2, \dots, e_{k-1} \rangle) & \text{if } k > 0 \end{cases}$$
   Removes and returns the element at the top. Decrements cardinality $k \leftarrow k - 1$.

3. **`peek() -> E`**:
   $$\text{peek}(\langle e_1, e_2, \dots, e_k \rangle) \mapsto \begin{cases} \text{Error (Underflow)} & \text{if } k = 0 \\ e_k & \text{if } k > 0 \end{cases}$$
   Idempotent inspection of the top element without mutating cardinality.

4. **`isEmpty() -> Boolean`**:
   $$\text{isEmpty}(S) \iff k = 0$$

```
                     PUSH (e)          POP () -> e
                        │                 ▲
                        ▼                 │
                 ┌──────────────┬──────────────┐
                 │          [ TOP ]            │  Index = k - 1
                 ├─────────────────────────────┤
                 │            e_k              │
                 ├─────────────────────────────┤
                 │            e_{k-1}          │
                 ├─────────────────────────────┤
                 │            ...              │
                 ├─────────────────────────────┤
                 │            e_1              │
                 ├─────────────────────────────┤
                 │         [ BOTTOM ]          │  Index = 0
                 └─────────────────────────────┘
```

---

## 2. Contiguous Array-Backed Storage Architecture

In an array-backed stack, elements reside in a contiguous block of memory managed by an integer index cursor `top`.

### 2.1 Index Invariants & State Transitions
- **Empty State**: `top == -1`. Cardinality is $0$.
- **Full State (Fixed Capacity $C$)**: `top == C - 1`. Attempting to push triggers a **Stack Overflow**.
- **Push Step**: `array[++top] = element`.
- **Pop Step**: `element = array[top--]`.

### 2.2 The Silent Disaster: Object Loitering (Memory Leaks in Managed Runtimes)
In managed environments like Java, C#, or Go, writing a pop operation as:
```java
// ANTI-PATTERN: CAUSES SEVERE MEMORY LEAKS
public T pop() {
    if (isEmpty()) throw new EmptyStackException();
    return elements[top--]; // BUG: elements[top + 1] retains reference!
}
```
leaves an **obsolete reference** inside the underlying array slot at `top + 1`. Even though the stack logically discarded the object, the garbage collector's root-tracing graph sees an active heap reference from the array buffer, preventing reclamation. In high-throughput enterprise pipelines, this **loitering bug** causes silent, catastrophic heap exhaustion (`OutOfMemoryError`).

**Correct Defensive Dereferencing:**
```java
public T pop() {
    if (isEmpty()) throw new EmptyStackException();
    T item = elements[top];
    elements[top] = null; // Obliterate reference to permit immediate GC
    top--;
    return item;
}
```

### 2.3 Production Dynamic Array Stack (`ResizingArrayStack<T>`)
```java
package edu.se.datastructures.stack;

import java.util.EmptyStackException;
import java.util.Iterator;
import java.util.NoSuchElementException;

public class ResizingArrayStack<T> implements Iterable<T> {
    private T[] elements;
    private int top;
    private static final int DEFAULT_CAPACITY = 8;

    @SuppressWarnings("unchecked")
    public ResizingArrayStack() {
        this.elements = (T[]) new Object[DEFAULT_CAPACITY];
        this.top = -1;
    }

    public int size() {
        return top + 1;
    }

    public boolean isEmpty() {
        return top == -1;
    }

    public void push(T item) {
        if (item == null) throw new IllegalArgumentException("Null values disallowed");
        // Geometric doubling when capacity limit is breached
        if (top == elements.length - 1) {
            resize(elements.length * 2);
        }
        elements[++top] = item;
    }

    public T pop() {
        if (isEmpty()) throw new EmptyStackException();
        T item = elements[top];
        elements[top] = null; // Prevent loitering
        top--;

        // Quarter-capacity hysteresis threshold to eliminate thrashing
        if (top > 0 && top == elements.length / 4) {
            resize(elements.length / 2);
        }
        return item;
    }

    public T peek() {
        if (isEmpty()) throw new EmptyStackException();
        return elements[top];
    }

    @SuppressWarnings("unchecked")
    private void resize(int newCapacity) {
        T[] newBuffer = (T[]) new Object[newCapacity];
        System.arraycopy(elements, 0, newBuffer, 0, top + 1);
        this.elements = newBuffer;
    }

    @Override
    public Iterator<T> iterator() {
        return new Iterator<T>() {
            private int current = top;
            @Override public boolean hasNext() { return current >= 0; }
            @Override public T next() {
                if (!hasNext()) throw new NoSuchElementException();
                return elements[current--];
            }
        };
    }
}
```

---

## 3. Linked-List-Backed Storage Architecture

A linked stack decomposes storage into discrete, dynamically allocated node records connected via unidirectional reference pointers.

### 3.1 The Head-as-Top Invariant
In a singly linked list, an architect faces a design decision: should `top` be mapped to the **Head** or the **Tail**?
- **Head as Top**:
  - `push`: Prepend node before head $\implies O(1)$ strictly.
  - `pop`: Detach head and advance to `head.next` $\implies O(1)$ strictly.
- **Tail as Top**:
  - `push`: Append node after tail $\implies O(1)$ with tail pointer.
  - `pop`: Deleting tail requires retrieving the predecessor node. In a Singly Linked List, finding the penultimate node requires traversing all $n$ nodes from head $\implies O(n)$!
  - **Verdict**: Mapping `top` to `head` is the only mathematically sound architecture for a Singly Linked Stack.

```
       push(X):
         newNode.next = top;
         top = newNode;

       pop():
         item = top.data;
         top = top.next;
         return item;

       [ top ] ──► ┌──────────┬───────┐      ┌──────────┬───────┐
                   │ data: 42 │ next  ├───►  │ data: 19 │ next  ├───► null
                   └──────────┴───────┘      └──────────┴───────┘
```

### 3.2 Production Linked Stack (`LinkedStack<T>`)
```java
package edu.se.datastructures.stack;

import java.util.EmptyStackException;
import java.util.Iterator;
import java.util.NoSuchElementException;

public class LinkedStack<T> implements Iterable<T> {
    private static final class Node<T> {
        final T data;
        final Node<T> next;

        Node(T data, Node<T> next) {
            this.data = data;
            this.next = next;
        }
    }

    private Node<T> top;
    private int size;

    public LinkedStack() {
        this.top = null;
        this.size = 0;
    }

    public int size() {
        return size;
    }

    public boolean isEmpty() {
        return top == null;
    }

    public void push(T item) {
        if (item == null) throw new IllegalArgumentException("Null values disallowed");
        this.top = new Node<>(item, this.top);
        this.size++;
    }

    public T pop() {
        if (isEmpty()) throw new EmptyStackException();
        T value = top.data;
        this.top = top.next; // Dereference previous head for GC
        this.size--;
        return value;
    }

    public T peek() {
        if (isEmpty()) throw new EmptyStackException();
        return top.data;
    }

    @Override
    public Iterator<T> iterator() {
        return new Iterator<T>() {
            private Node<T> current = top;
            @Override public boolean hasNext() { return current != null; }
            @Override public T next() {
                if (!hasNext()) throw new NoSuchElementException();
                T val = current.data;
                current = current.next;
                return val;
            }
        };
    }
}
```

---

## 4. Hardware Memory Model & Comparative Architectural Trade-Offs

When choosing between `ResizingArrayStack` and `LinkedStack` in mission-critical software, raw Big-$O$ notation is insufficient. We must analyze CPU cache line prefetching and byte-level memory overhead.

### 4.1 Memory Footprint Deconstruction (64-bit JVM with Compressed OOPs)
Assume a stack holding $N = 1,000,000$ 32-bit `Integer` objects:

1. **`LinkedStack<Integer>`**:
   - Each entry requires an allocated `Node` instance on the Heap:
     - 12 bytes Mark/Klass word header + 4-byte padding = **16 bytes**
     - 4 bytes reference to `data` (`Integer`)
     - 4 bytes reference to `next` (`Node`)
     - Total per node = **24 bytes**
   - Total overhead for 1M nodes: $24 \times 1,000,000 \approx \mathbf{24 \text{ MB}}$ (excluding Integer objects).

2. **`ResizingArrayStack<Integer>`**:
   - Uses a single contiguous reference array:
     - Array header = 16 bytes.
     - Array slots: $4 \text{ bytes} \times \text{capacity}$. At an average load factor of $70\%$, capacity $\approx 1.43 \times 10^6$.
     - Total overhead: $4 \times 1.43 \times 10^6 \approx \mathbf{5.72 \text{ MB}}$.
   - **Footprint Advantage**: Array stack consumes $\approx 76\%$ less auxiliary memory.

### 4.2 Hardware Cache Locality (L1/L2 Cache Lines)
- **Contiguous Array**: Because elements sit side-by-side in RAM, a CPU accessing `elements[top]` triggers the hardware prefetcher to load the entire 64-byte cache line (containing the next 16 pointers). Subsequent pops execute directly out of the ultra-fast L1 cache ($1\text{--}2 \text{ ns}$).
- **Linked Node Graph**: Nodes are allocated across non-contiguous heap addresses. Dereferencing `top.next` frequently causes a CPU cache miss, forcing an expensive main memory bus cycle ($50\text{--}100 \text{ ns}$).

| Architectural Dimension | Array-Backed Stack (`ResizingArrayStack`) | Linked-List Stack (`LinkedStack`) |
| :--- | :--- | :--- |
| **Push Time Complexity** | $O(1)$ amortized; $O(n)$ worst-case during resize | $O(1)$ strictly guaranteed always |
| **Pop Time Complexity** | $O(1)$ amortized; $O(n)$ during compaction | $O(1)$ strictly guaranteed always |
| **Memory Auxiliary Overhead** | Low ($pprox 4\text{--}8$ bytes per slot) | High ($\ge 24$ bytes per element node) |
| **CPU L1/L2 Cache Spatial Locality** | **Exceptional** (sequential contiguous stride) | **Poor** (pointer chasing across heap) |
| **Latency Jitter / Predictability** | High jitter on reallocation boundary | **Ultra-low jitter** (ideal for Hard Real-Time) |
| **Recommended Production Choice** | General high-throughput backend services | Real-time audio/telecom embedded controllers |

---

## 5. Industrial Systems: Concurrent Lock-Free Stack (Treiber Algorithm)

In multi-threaded architectures, wrapping stack operations in `synchronized` blocks creates catastrophic lock contention under high core counts. In 1986, R. Kent Treiber designed an ultra-high performance lock-free stack using hardware **Compare-And-Swap (CAS)** instructions.

```
       Thread 1: push(X)                   Thread 2: push(Y)
          ┌────────┐                          ┌────────┐
          │ Node X ├──┐                       │ Node Y ├──┐
          └────────┘  │                       └────────┘  │
                      ▼                                   ▼
                   [ TOP ] ──► ┌──────────┐ ──► ┌──────────┐
                               │  Head A  │     │  Head B  │
                               └──────────┘     └──────────┘
             CAS(TOP, Head A, Node X) wins!
             Thread 2 fails CAS, re-reads TOP, retries atomically.
```

```java
package edu.se.datastructures.stack;

import java.util.concurrent.atomic.AtomicReference;

public class TreiberStack<E> {
    private static final class Node<E> {
        final E item;
        Node<E> next;
        Node(E item) { this.item = item; }
    }

    private final AtomicReference<Node<E>> top = new AtomicReference<>(null);

    public void push(E item) {
        if (item == null) throw new IllegalArgumentException();
        Node<E> newHead = new Node<>(item);
        Node<E> oldHead;
        do {
            oldHead = top.get();
            newHead.next = oldHead;
            // Atomic CAS: If top is still oldHead, swing pointer to newHead
        } while (!top.compareAndSet(oldHead, newHead));
    }

    public E pop() {
        Node<E> oldHead;
        Node<E> newHead;
        do {
            oldHead = top.get();
            if (oldHead == null) {
                return null; // Stack is empty
            }
            newHead = oldHead.next;
        } while (!top.compareAndSet(oldHead, newHead));
        return oldHead.item;
    }
}
```

---

## 6. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Trace the execution of the following operations on an array stack of initial capacity $2$:
`push(10)`, `push(20)`, `push(30)`, `pop()`, `pop()`.
Specify the array length, `top` value, and whether a resize occurs at each step.

<details>
<summary>View Architectural Walkthrough Solution</summary>

| Step | Operation | Array Capacity | `top` Index | Array Contents | Action Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Initial State | 2 | -1 | `[null, null]` | Empty stack initialized |
| 2 | `push(10)` | 2 | 0 | `[10, null]` | Stored at index 0 |
| 3 | `push(20)` | 2 | 1 | `[10, 20]` | Buffer full; `top == capacity - 1` |
| 4 | `push(30)` | **4** | 2 | `[10, 20, 30, null]` | **Resize triggered!** Capacity doubled to 4; 30 stored at index 2 |
| 5 | `pop()` -> 30 | 4 | 1 | `[10, 20, null, null]` | Top decremented; index 2 nulled out |
| 6 | `pop()` -> 20 | **2** | 0 | `[10, null]` | `top == capacity / 4`; **Shrink triggered!** Capacity halved to 2 |
</details>

---

### Level 2: Scaffolded System Refactoring — $O(1)$ Min-Stack
**Problem Statement:** Design a stack that supports `push`, `pop`, `peek`, and retrieving the minimum element (`getMin()`) in strictly guaranteed $O(1)$ time complexity without degrading $O(1)$ auxiliary overhead.

<details>
<summary>View Complete Java Implementation & Invariant Proof</summary>

```java
package edu.se.datastructures.stack;

import java.util.EmptyStackException;

/**
 * MinStack maintaining minimum state using differential encoding.
 * Eliminates auxiliary stack by storing offsets against running minimum.
 */
public class MinStack {
    private static final class Node {
        final long val; // Stores actual value or encoded offset
        final Node next;
        Node(long val, Node next) {
            this.val = val;
            this.next = next;
        }
    }

    private Node head;
    private long min;

    public MinStack() {
        this.head = null;
    }

    public void push(int x) {
        if (head == null) {
            head = new Node(0L, null);
            min = x;
        } else {
            // Push difference between new value and current minimum
            long diff = (long) x - min;
            head = new Node(diff, head);
            if (diff < 0) {
                min = x; // Update running minimum
            }
        }
    }

    public int pop() {
        if (head == null) throw new EmptyStackException();
        long diff = head.val;
        head = head.next;

        if (diff < 0) {
            long actual = min;
            min = min - diff; // Restore previous minimum
            return (int) actual;
        } else {
            return (int) (min + diff);
        }
    }

    public int getMin() {
        if (head == null) throw new EmptyStackException();
        return (int) min;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Bounded High-Throughput Ring Buffer Stack
**Problem Statement:** Build a bounded `LIFO` stack without any dynamic allocations or locks, using a fixed-size ring buffer with circular bitwise masking for high-frequency trading (HFT) ingestion.

<details>
<summary>View High-Throughput Implementation</summary>

```java
package edu.se.datastructures.stack;

public final class RingBufferStack<T> {
    private final Object[] ring;
    private final int mask;
    private int head = 0;
    private int size = 0;

    @SuppressWarnings("unchecked")
    public RingBufferStack(int capacityPowerOfTwo) {
        if (Integer.bitCount(capacityPowerOfTwo) != 1) {
            throw new IllegalArgumentException("Capacity must be an exact power of two");
        }
        this.ring = new Object[capacityPowerOfTwo];
        this.mask = capacityPowerOfTwo - 1;
    }

    public boolean push(T item) {
        if (size == ring.length) {
            return false; // Bounded overflow refusal
        }
        ring[head] = item;
        head = (head + 1) & mask;
        size++;
        return true;
    }

    @SuppressWarnings("unchecked")
    public T pop() {
        if (size == 0) {
            return null; // Underflow
        }
        head = (head - 1) & mask;
        T item = (T) ring[head];
        ring[head] = null; // Prevent loitering
        size--;
        return item;
    }
}
```
</details>
