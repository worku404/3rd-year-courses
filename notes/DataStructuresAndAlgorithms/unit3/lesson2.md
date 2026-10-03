# Lesson 2 — Doubly Linked Lists, Sentinel Nodes & Bidirectional Navigation

> [!NOTE]
> **Learning Outcomes:**
> - Construct the symmetrical forward and backward reference architecture of **Doubly Linked Lists (DLL)**.
> - Implement the **Sentinel (Dummy) Node Pattern** (`dummyHead` and `dummyTail`) to eliminate edge-case conditionals and branch mispredictions.
> - Execute the game-changing **$O(1)$ Known-Node Deletion** mutation that forms the foundation of database buffer pools and LRU caches.
> - Formulate the 64-bit JVM object alignment memory cost equation comparing SLL and DLL nodes.
> - Build a robust bidirectional Deque supporting symmetric insertions and removals at both ends in constant time.

{{media:dll-video}}

{{media:dll-visual}}

## Executive Summary & System Context

While Singly Linked Lists provide $O(1)$ insertions at the head and tail, their unidirectional structure imposes severe limitations on practical systems:
1. **The Inability to Traverse Backwards**: Navigating backwards from a current cursor position is impossible without maintaining a secondary stack.
2. **The Asymmetrical Deletion Penalty**: Deleting a node in an SLL requires holding a reference to its *predecessor*. If an application holds a reference to the target node itself, it must waste $O(n)$ time scanning from the head to find who points to it.

The **Doubly Linked List (DLL)** overcomes these architectural constraints by augmenting every node with a second reference pointer: `prev`. By linking nodes bidirectionally, each element has immediate, constant-time access to both its successor and its predecessor.

---

## 1. Doubly Linked List (DLL) Node Architecture

In a Doubly Linked List, each node maintains two pointer references alongside its data payload:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DOUBLY LINKED HEAP NODE                         │
│                                                                        │
│   ┌────────────────────┬────────────────────┬────────────────────┐     │
│   │  prev (64-Bit Ref) │   data (Payload)   │  next (64-Bit Ref) ┼───> │
│ <─┼── (Predecessor)    │   (Object/Value)   │  (Successor)       │     │
│   └────────────────────┴────────────────────┴────────────────────┘     │
└────────────────────────────────────────────────────────────────────────┘
```

### Java Definition:
```java
package edu.se.dsa.list;

public class DoubleNode<E> {
    public E data;
    public DoubleNode<E> prev; // Reference to predecessor
    public DoubleNode<E> next; // Reference to successor

    public DoubleNode(E data) {
        this(data, null, null);
    }

    public DoubleNode(E data, DoubleNode<E> prev, DoubleNode<E> next) {
        this.data = data;
        this.prev = prev;
        this.next = next;
    }
}
```

### The Symmetrical Invariants:
For any active interior node $N$ in a Doubly Linked List:
$$N.next.prev == N \\quad \\text{and} \\quad N.prev.next == N$$
This symmetry ensures that stepping forward and then backward lands back on the exact same memory address.

---

## 2. The Sentinel (Dummy) Node Architectural Pattern

When implementing a raw linked list, engineers frequently encounter "conditional explosion"—writing numerous fragile `if-else` branches to handle boundary edge cases:
- Inserting into an empty list
- Inserting at the head vs. the tail vs. the middle
- Deleting the only element vs. the head vs. the tail

### The Sentinel Solution:
A **Sentinel Node** (also known as a *Dummy Node*) is a permanent placeholder node containing no payload data. A production Doubly Linked List uses two sentinels: `dummyHead` and `dummyTail`.

```
        ┌─────────────┐                                           ┌─────────────┐
        │  dummyHead  │                                           │  dummyTail  │
        ├─────────────┤                                           ├─────────────┤
null <──┼─ prev       │    ┌───────────┐         ┌───────────┐    │        next ┼──> null
        │        next ┼───>│   Node A  │<───────>│   Node B  │<───┼─ prev       │
        └─────────────┘    └───────────┘         └───────────┘    └─────────────┘
                           [ FIRST ITEM ]        [ LAST ITEM ]
```

### The Unbreakable Invariants of Sentinels:
1. `dummyHead.prev` is ALWAYS `null`.
2. `dummyTail.next` is ALWAYS `null`.
3. In an **Empty List**: `dummyHead.next == dummyTail` and `dummyTail.prev == dummyHead`.
4. **The List is NEVER Empty**: Sentinels are never removed. Every payload node $N$ is guaranteed to have a non-null `prev` and non-null `next`!

#### Impact on Code Quality:
By introducing two dummy nodes, **100% of special-case `if` branches are eliminated**. The same 4-line mutation method handles insertions and deletions at the head, tail, or middle of the list!

---

## 3. Symmetrical Mutations with Sentinels

### 1. Unified Insertion Before a Successor Node ($O(1)$)
To insert `newNode` immediately before an existing node `succ`:

```java
// Branchless, zero-if statement insertion:
private void addBefore(DoubleNode<E> succ, E item) {
    DoubleNode<E> pred = succ.prev;
    DoubleNode<E> newNode = new DoubleNode<>(item, pred, succ);

    pred.next = newNode;
    succ.prev = newNode;
    size++;
}

// Inserting at Head is simply inserting before dummyHead.next:
public void addFirst(E item) {
    addBefore(dummyHead.next, item);
}

// Inserting at Tail is simply inserting before dummyTail:
public void addLast(E item) {
    addBefore(dummyTail, item);
}
```

---

### 2. The $O(1)$ Known-Node Deletion Advantage
Suppose an enterprise caching system (such as an LRU Cache) holds a direct pointer reference to `node`. How do we delete it?

```java
// Branchless O(1) Deletion of KNOWN node:
public void removeNode(DoubleNode<E> node) {
    // 1. Link predecessor directly to successor
    node.prev.next = node.next;
    // 2. Link successor directly to predecessor
    node.next.prev = node.prev;

    // 3. Clean up node references to prevent memory retention
    node.prev = null;
    node.next = null;
    size--;
}
```

```
Before Deletion:
[ pred ] <═════> [ TARGET NODE ] <═════> [ succ ]

After Deletion:
[ pred ] ───────────────────────────────> [ succ ]
[ pred ] <─────────────────────────────── [ succ ]
```

*Architectural Superpower*: In a Singly Linked List, deleting a known node requires scanning linearly from the head ($O(n)$). In a Doubly Linked List, because `node.prev` is directly accessible, deletion executes in **strictly $O(1)$ Constant Time**!

---

## 4. Memory Footprint Equation: SLL vs. DLL on 64-bit JVM

Every architectural feature comes at a hardware cost. What is the exact physical RAM overhead of maintaining the backward pointer?

### 64-bit HotSpot JVM Object Memory Model:
- **Object Header**: $12$ bytes (Mark Word $8$ bytes + Klass Pointer $4$ bytes under Compressed OOPs) $\\to$ rounded to $16$ bytes aligned.
- **Reference Pointers**: $4$ bytes (with Compressed OOPs) or $8$ bytes (without Compressed OOPs).
- **Object Padding**: Objects in the JVM must align to $8$-byte boundaries.

#### Singly Linked List Node Footprint (`data`, `next`):
- Header: $16$ bytes
- Field `data` reference: $8$ bytes
- Field `next` reference: $8$ bytes
- **Total per Node**: **$32$ bytes**

#### Doubly Linked List Node Footprint (`data`, `next`, `prev`):
- Header: $16$ bytes
- Field `data` reference: $8$ bytes
- Field `next` reference: $8$ bytes
- Field `prev` reference: $8$ bytes
- **Total per Node**: **$40$ bytes** (or $48$ bytes with padding)

#### Quantitative Impact: Storing 10,000,000 Elements
- `ArrayList<Integer>` (Contiguous buffer of references): $\\approx 40$ MB
- `SinglyLinkedList<Integer>` ($10M \\times 32$ B): $\\approx \\mathbf{320\\text{ MB}}$
- `DoublyLinkedList<Integer>` ($10M \\times 40$ B): $\\approx \\mathbf{400\\text{ MB}}$

*Verdict*: A Doubly Linked List consumes **$10\\times$ more memory** than a contiguous array and **$25\\%$ more memory** than a Singly Linked List. Use DLLs only when bidirectional traversal or $O(1)$ arbitrary deletions are strict algorithmic requirements!

---

## 5. Comprehensive Trade-Off Matrix

| Operation / Metric | Singly Linked List (with Tail) | Doubly Linked List (with Sentinels) |
| :--- | :--- | :--- |
| **Insert First (`addFirst`)** | $\\mathbf{O(1)}$ Constant | $\\mathbf{O(1)}$ Constant |
| **Insert Last (`addLast`)** | $\\mathbf{O(1)}$ Constant | $\\mathbf{O(1)}$ Constant |
| **Delete First (`removeFirst`)** | $\\mathbf{O(1)}$ Constant | $\\mathbf{O(1)}$ Constant |
| **Delete Last (`removeLast`)** | $O(n)$ Linear (Predecessor scan) | $\\mathbf{O(1)}$ **Constant (Instant via `dummyTail.prev`)** |
| **Delete Known Node** | $O(n)$ Linear | $\\mathbf{O(1)}$ **Constant** |
| **Reverse Traversal** | Impossible ($O(n)$ auxiliary stack) | $\\mathbf{O(1)}$ **Native (Traverse `prev` links)** |
| **Pointer Updates on Insert** | $2$ pointer writes | $4$ pointer writes |
| **Memory per Node (64-bit)** | $\\approx 32$ bytes | $\\approx 40$ to $48$ bytes |
| **Primary Domain** | Forward-only queues, memory-tight lists | Deques, LRU caches, text-editor undo stacks |

---

## 6. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Sentinel Mutation Trace
**Objective**: Trace the pointers of `dummyHead`, `dummyTail`, and payload nodes when inserting elements `10` and `20` into an initially empty sentinel-bounded Doubly Linked List.

<details>
<summary>View Level 1 Step-by-Step Pointer Trace</summary>

#### Initial Empty State:
- `dummyHead.next = dummyTail`
- `dummyTail.prev = dummyHead`

#### 1. Execute `addFirst(10)`:
Target: Insert `Node(10)` before `dummyHead.next` (`dummyTail`):
1. `Node(10).prev = dummyHead`
2. `Node(10).next = dummyTail`
3. `dummyHead.next = Node(10)`
4. `dummyTail.prev = Node(10)`
- *State*: `dummyHead <===> Node(10) <===> dummyTail`

#### 2. Execute `addLast(20)`:
Target: Insert `Node(20)` before `dummyTail`:
1. Predecessor is `dummyTail.prev` (`Node(10)`).
2. `Node(20).prev = Node(10)`
3. `Node(20).next = dummyTail`
4. `Node(10).next = Node(20)`
5. `dummyTail.prev = Node(20)`
- *Final State*: `dummyHead <===> Node(10) <===> Node(20) <===> dummyTail`
</details>

---

### Level 2: Scaffolded System Refactoring — Complete Sentinel DLL Container
**Objective**: Implement a complete generic `DoublyLinkedList<E>` using the Sentinel Pattern. It must provide:
- `addFirst(E item)`, `addLast(E item)` ($O(1)$)
- `removeFirst()`, `removeLast()` ($O(1)$)
- `remove(DoubleNode<E> node)` ($O(1)$)
- `toString()` and `toReverseString()`

<details>
<summary>View Level 2 Complete Production Java Implementation</summary>

```java
package edu.se.dsa.list;

import java.util.NoSuchElementException;

public class DoublyLinkedList<E> {
    private final DoubleNode<E> dummyHead;
    private final DoubleNode<E> dummyTail;
    private int size = 0;

    public DoublyLinkedList() {
        dummyHead = new DoubleNode<>(null);
        dummyTail = new DoubleNode<>(null);
        dummyHead.next = dummyTail;
        dummyTail.prev = dummyHead;
    }

    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }

    public void addFirst(E item) {
        addBefore(dummyHead.next, item);
    }

    public void addLast(E item) {
        addBefore(dummyTail, item);
    }

    public E removeFirst() {
        if (isEmpty()) throw new NoSuchElementException("List is empty");
        return removeNode(dummyHead.next);
    }

    public E removeLast() {
        if (isEmpty()) throw new NoSuchElementException("List is empty");
        return removeNode(dummyTail.prev);
    }

    private void addBefore(DoubleNode<E> succ, E item) {
        DoubleNode<E> pred = succ.prev;
        DoubleNode<E> newNode = new DoubleNode<>(item, pred, succ);
        pred.next = newNode;
        succ.prev = newNode;
        size++;
    }

    public E removeNode(DoubleNode<E> node) {
        if (node == dummyHead || node == dummyTail) {
            throw new IllegalArgumentException("Cannot remove sentinel nodes");
        }
        node.prev.next = node.next;
        node.next.prev = node.prev;
        E item = node.data;
        node.prev = null;
        node.next = null;
        size--;
        return item;
    }

    public String toReverseString() {
        StringBuilder sb = new StringBuilder("[");
        DoubleNode<E> curr = dummyTail.prev;
        while (curr != dummyHead) {
            sb.append(curr.data);
            if (curr.prev != dummyHead) sb.append(", ");
            curr = curr.prev; // Traverse backwards natively!
        }
        return sb.append("]").toString();
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — High-Throughput Bidirectional Deque
**Objective**: A **Double-Ended Queue (Deque)** allows $O(1)$ push and pop operations at both the front and the back.
- Architect an enterprise `LinkedDeque<E>` implementing FIFO queue, LIFO stack, and scrolling buffer interfaces.
- Guarantee that all operations (`offerFirst`, `offerLast`, `pollFirst`, `pollLast`, `peekFirst`, `peekLast`) run in strict **$O(1)$ worst-case time**.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.dsa.deque;

import java.util.NoSuchElementException;

/**
 * Enterprise Double-Ended Queue (Deque) backed by Sentinel DLL.
 * Guarantees O(1) operations for all front/rear push, pop, and peek mutations.
 */
public class LinkedDeque<E> {
    private final DoubleNode<E> head;
    private final DoubleNode<E> tail;
    private int size = 0;

    private static class DoubleNode<T> {
        T data;
        DoubleNode<T> prev;
        DoubleNode<T> next;
        DoubleNode(T data, DoubleNode<T> p, DoubleNode<T> n) {
            this.data = data; this.prev = p; this.next = n;
        }
    }

    public LinkedDeque() {
        head = new DoubleNode<>(null, null, null);
        tail = new DoubleNode<>(null, head, null);
        head.next = tail;
    }

    public void offerFirst(E item) {
        DoubleNode<E> first = head.next;
        DoubleNode<E> newNode = new DoubleNode<>(item, head, first);
        head.next = newNode;
        first.prev = newNode;
        size++;
    }

    public void offerLast(E item) {
        DoubleNode<E> last = tail.prev;
        DoubleNode<E> newNode = new DoubleNode<>(item, last, tail);
        last.next = newNode;
        tail.prev = newNode;
        size++;
    }

    public E pollFirst() {
        if (isEmpty()) return null;
        DoubleNode<E> target = head.next;
        head.next = target.next;
        target.next.prev = head;
        size--;
        return target.data;
    }

    public E pollLast() {
        if (isEmpty()) return null;
        DoubleNode<E> target = tail.prev;
        tail.prev = target.prev;
        target.prev.next = tail;
        size--;
        return target.data;
    }

    public E peekFirst() {
        return isEmpty() ? null : head.next.data;
    }

    public E peekLast() {
        return isEmpty() ? null : tail.prev.data;
    }

    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }
}
```

#### Architectural Key Insight:
Because the sentinel nodes maintain non-null references even when the Deque is completely drained of data, concurrent thread wrappers can lock only `head` or `tail` independently, enabling lock-striped bidirectional concurrent queues!
</details>
