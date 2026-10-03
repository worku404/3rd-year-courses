# Lesson 1 — Singly Linked Lists: Node Anatomy, Pointer Invariants & Splice Operations

> [!NOTE]
> **Learning Outcomes:**
> - Deconstruct the memory architecture of **Self-Referential Structures** and pointer dereferencing on modern 64-bit runtimes.
> - Formulate the formal invariants governing the **Head** pointer, **Tail** pointer, and **Null Terminator**.
> - Execute splice mutations: Prepending ($O(1)$), Appending ($O(1)$ with tail), and Middle Splicing ($O(1)$ given predecessor).
> - Analyze the catastrophic **Fatal Pointer Loss Anti-Pattern** that orphan-leaks sub-lists and triggers infinite loops.
> - Evaluate why Tail Deletion remains $O(n)$ in a Singly Linked List even when maintaining an active tail reference pointer.

{{media:sll-video}}

{{media:sll-visual}}

## Executive Summary & System Context

While contiguous dynamic arrays (`ArrayList`) excel at random access indexing via address arithmetic, they suffer from two severe structural drawbacks:
1. **Expensive Mid-Buffer Insertions and Deletions**: Inserting or removing an element at index $0$ forces the CPU to shift all $n$ subsequent elements right or left, incurring a heavy $O(n)$ memory copy penalty.
2. **Buffer Reallocation Latency**: When a dynamic array exhausts its physical capacity, the runtime must allocate a larger contiguous block of memory and copy every existing element over, introducing latency spikes in real-time systems.

The **Linked List** solves these constraints by abandoning physical contiguity entirely. Elements are wrapped inside independent heap nodes that can be allocated anywhere in memory, dynamically linked together via **64-bit reference pointers**.

---

## 1. Self-Referential Data Structures & Node Anatomy

A data structure is defined as **Self-Referential** if one of its member fields is a pointer or reference to an instance of the *same* structure type.

```
┌─────────────────────────────────────────────────────────┐
│                      HEAP NODE                          │
│                                                         │
│   ┌────────────────────────┬────────────────────────┐   │
│   │   data (Object/Value)  │  next (64-Bit Pointer) ┼───┼──> [ Next Node ]
│   │   (e.g., int / String) │  (Memory Address)      │   │
│   └────────────────────────┴────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Java Generic Definition:
```java
package edu.se.dsa.list;

public class Node<E> {
    public E data;        // Payload value
    public Node<E> next;  // Reference to successor node (null if last)

    public Node(E data) {
        this(data, null);
    }

    public Node(E data, Node<E> next) {
        this.data = data;
        this.next = next;
    }
}
```

### Memory Layout on Modern 64-bit Runtimes:
When a new node `new Node<>(val)` is instantiated on the heap:
1. The memory allocator finds any available $24$-to-$32$ byte block of memory.
2. The `next` field stores the **64-bit virtual memory address** of the successor node (e.g., `0x7ffee4b28190`).
3. If a node is the final element in the list, its `next` field contains the primitive literal `null` (address `0x0`).

---

## 2. Singly Linked List Structural Invariants

A valid Singly Linked List (SLL) satisfies the following structural invariants:
1. **Entry Point Invariant**: The external world holds an entry reference called `head`. If `head == null`, the list is strictly empty.
2. **Successor Invariant**: For every node $N_i$ (where $0 \\le i < n - 1$), $N_i.next$ references node $N_{i+1}$.
3. **Termination Invariant**: The last node $N_{n-1}$ satisfies $N_{n-1}.next == null$.
4. **Tail Invariant (Optional Optimization)**: If a `tail` reference is maintained, `tail` points directly to $N_{n-1}$. If the list is empty, both `head` and `tail` are `null`.

```
        head                                                tail
         │                                                   │
         ▼                                                   ▼
      ┌──────┬──────┐    ┌──────┬──────┐    ┌──────┬──────┐ ┌──────┬──────┐
      │  10  │ 0x20 ┼───>│  20  │ 0x55 ┼───>│  30  │ 0x88 ┼─>│  40  │ null │
      └──────┴──────┘    └──────┴──────┘    └──────┴──────┘ └──────┴──────┘
      Addr: 0x10         Addr: 0x20         Addr: 0x55      Addr: 0x88
```

---

## 3. Splice Mutation Invariants: Insertions

### 1. Prepending at the Head ($O(1)$ Constant Time)
To insert a new node at the beginning of the list:
```java
public void addFirst(E item) {
    Node<E> newNode = new Node<>(item, head); // 1. Point newNode.next to current head
    head = newNode;                           // 2. Reassign head to newNode
    if (tail == null) {
        tail = head; // If list was empty, tail also points to newNode
    }
    size++;
}
```
*Time Complexity*: Exactly 2 pointer assignments $\\implies$ **$O(1)$ Constant Time**.

---

### 2. Appending at the Tail ($O(1)$ vs $O(n)$)
- **Without Tail Pointer**: The algorithm must scan linearly from `head` through all $n$ nodes until reaching the node where `curr.next == null`, then set `curr.next = newNode` $\\implies$ **$O(n)$ Linear Time**.
- **With Tail Pointer**: Instantaneous link update:
```java
public void addLast(E item) {
    Node<E> newNode = new Node<>(item, null);
    if (isEmpty()) {
        head = tail = newNode;
    } else {
        tail.next = newNode; // 1. Link current tail to newNode
        tail = newNode;      // 2. Advance tail reference
    }
    size++;
}
```
*Time Complexity*: **$O(1)$ Constant Time**.

---

### 3. Inserting After a Given Predecessor Node (`prev`)
Suppose we hold a reference to node `prev` and wish to splice `newNode` immediately after it:

```java
// CORRECT ORDER OF POINTER ASSIGNMENTS:
newNode.next = prev.next; // Step 1: Connect newNode to the downstream chain FIRST!
prev.next = newNode;      // Step 2: Reroute prev to point to newNode
```

---

## 4. The Fatal Pointer Loss Anti-Pattern (Disaster Analysis)

The most destructive mistake in linked list programming occurs when an engineer reverses the order of the two splice statements:

```java
// FATAL ANTI-PATTERN (NEVER DO THIS):
prev.next = newNode;      // MISTAKE: Overwrote prev's link to the rest of the list!
newNode.next = prev.next; // DISASTER: Sets newNode.next to newNode itself!
```

```
Before Mutation:
[ prev ] ───────────────> [ successor ] ───> [ rest of list ... ]

After Fatal Mistake:
[ prev ] ───> [ newNode ] ───┐
                  ▲          │ (Self-Loop!)
                  └──────────┘
[ successor ] ───> [ rest of list ... ]  <── ORPHANED & PERMANENTLY LOST IN RAM!
```

### Engineering Catastrophe:
1. **Permanent Memory Leak**: The entire downstream list (`successor` and all nodes following it) is severed from the reachable object graph. In C/C++, this memory is permanently leaked.
2. **Infinite Traversal Loop**: `newNode.next` now points back to `newNode`. Any subsequent search or print loop (`while (curr != null) curr = curr.next;`) will enter an **infinite loop**, freezing the thread and exhausting CPU cores at $100\\%$ utilization!

---

## 5. Deletion Mechanics & The Tail Deletion Asymmetry

### 1. Removing the Head Node ($O(1)$ Constant Time)
```java
public E removeFirst() {
    if (isEmpty()) throw new NoSuchElementException();
    E val = head.data;
    head = head.next; // Advance head to second node
    size--;
    if (head == null) {
        tail = null; // List is now empty
    }
    return val;
}
```

---

### 2. The Tail Deletion Asymmetry ($O(n)$ Linear Time)
> [!WARNING]
> **The Great Asymmetry**: Appending with a tail pointer is $O(1)$, but **deleting the tail node in a Singly Linked List is ALWAYS $O(n)$**, even if you have a direct `tail` pointer!

#### Why Can't We Delete the Tail in $O(1)$?
1. To delete `tail`, we must set the **second-to-last node's** `next` pointer to `null`.
2. In a Singly Linked List, pointers are strictly **unidirectional** ($A \\to B \\to C$). There is no backward link from `tail` to its predecessor!
3. Therefore, to find the second-to-last node, the CPU must start at `head` and traverse all $n - 2$ nodes sequentially:
   ```java
   Node<E> curr = head;
   while (curr.next != tail) {
       curr = curr.next; // O(n) Traversal required!
   }
   curr.next = null;
   tail = curr;
   ```
4. *Conclusion*: Deleting the tail of an SLL requires **$\\Theta(n)$ Linear Time**. (To achieve $O(1)$ tail deletion, one must upgrade to a **Doubly Linked List**).

---

## 6. Comprehensive Trade-Off Matrix: ArrayList vs. Singly Linked List

| Operation / Feature | Contiguous Dynamic Array (`ArrayList`) | Singly Linked List (`SLL` with Tail) |
| :--- | :--- | :--- |
| **Random Indexing (`get(i)`)** | $\\mathbf{O(1)}$ Instantaneous Address Math | $O(n)$ Linear Pointer Chasing |
| **Prepend (`addFirst`)** | $O(n)$ (Shifts all $n$ elements right) | $\\mathbf{O(1)}$ (Update head pointer) |
| **Append (`addLast`)** | $O(1)$ Amortized ($O(n)$ on buffer resize) | $\\mathbf{O(1)}$ (Strict guarantee, no resizes) |
| **Delete Head (`removeFirst`)** | $O(n)$ (Shifts all elements left) | $\\mathbf{O(1)}$ (Advance head pointer) |
| **Delete Tail (`removeLast`)** | $\\mathbf{O(1)}$ (Decrement size counter) | $O(n)$ (Linear scan to predecessor) |
| **Insert at Known Node (`insertAfter`)** | $O(n)$ (Shift elements) | $\\mathbf{O(1)}$ (Two pointer updates) |
| **Hardware Cache Locality** | **Exceptional** (Sequential L1 lines) | **Terrible** (Scattered heap cache misses) |
| **Memory Overhead** | Buffer capacity slack ($10\\%-30\\%$) | High ($8$ bytes pointer per node on 64-bit) |

---

## 7. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Manual State Space Tracing
**Objective**: Trace the pointer states of `head`, `tail`, and individual node `next` references through the following sequence of operations on an initially empty Singly Linked List:
1. `addFirst(30)`
2. `addFirst(20)`
3. `addLast(40)`
4. `removeFirst()`

<details>
<summary>View Level 1 Pointer State Walkthrough</summary>

| Step | Operation | `head` Address | `tail` Address | Node Chain Topology | `size` |
| :---: | :--- | :---: | :---: | :--- | :---: |
| **0** | Initial State | `null` | `null` | Empty | $0$ |
| **1** | `addFirst(30)` | `Node(30)` | `Node(30)` | `[ 30 | null ]` | $1$ |
| **2** | `addFirst(20)` | `Node(20)` | `Node(30)` | `[ 20 ] ──> [ 30 | null ]` | $2$ |
| **3** | `addLast(40)` | `Node(20)` | `Node(40)` | `[ 20 ] ──> [ 30 ] ──> [ 40 | null ]` | $3$ |
| **4** | `removeFirst()` | `Node(30)` | `Node(40)` | `[ 30 ] ──> [ 40 | null ]` | $2$ |

*Result*: Head now references `Node(30)`; Tail references `Node(40)`. The old `Node(20)` is unreachable and collected by garbage collection.
</details>

---

### Level 2: Scaffolded System Refactoring — Complete Singly Linked List Container
**Objective**: Implement a complete generic `SinglyLinkedList<E>` container implementing:
- `addFirst(E val)` ($O(1)$)
- `addLast(E val)` ($O(1)$ with tail)
- `removeFirst()` ($O(1)$)
- `removeLast()` ($O(n)$)
- `contains(E val)` ($O(n)$)

<details>
<summary>View Level 2 Complete Production Java Implementation</summary>

```java
package edu.se.dsa.list;

import java.util.NoSuchElementException;

public class SinglyLinkedList<E> {
    private Node<E> head = null;
    private Node<E> tail = null;
    private int size = 0;

    public int size() { return size; }
    public boolean isEmpty() { return size == 0; }

    public void addFirst(E item) {
        Node<E> newNode = new Node<>(item, head);
        head = newNode;
        if (tail == null) {
            tail = head;
        }
        size++;
    }

    public void addLast(E item) {
        Node<E> newNode = new Node<>(item, null);
        if (isEmpty()) {
            head = tail = newNode;
        } else {
            tail.next = newNode;
            tail = newNode;
        }
        size++;
    }

    public E removeFirst() {
        if (isEmpty()) throw new NoSuchElementException("List is empty");
        E item = head.data;
        head = head.next;
        size--;
        if (head == null) {
            tail = null;
        }
        return item;
    }

    public E removeLast() {
        if (isEmpty()) throw new NoSuchElementException("List is empty");
        if (head == tail) {
            E item = head.data;
            head = tail = null;
            size = 0;
            return item;
        }

        // Scan to locate second-to-last node
        Node<E> curr = head;
        while (curr.next != tail) {
            curr = curr.next;
        }

        E item = tail.data;
        curr.next = null;
        tail = curr;
        size--;
        return item;
    }

    public boolean contains(E target) {
        Node<E> curr = head;
        while (curr != null) {
            if (target == null ? curr.data == null : target.equals(curr.data)) {
                return true;
            }
            curr = curr.next;
        }
        return false;
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — In-Place Singly Linked List Reversal
**Objective**: Reverse a Singly Linked List in **strictly $O(n)$ Time and $O(1)$ Auxiliary Space** without creating any new nodes or allocating secondary arrays.
- Implement the classic **Three-Pointer Reversal Algorithm** (`prev`, `curr`, `next`).

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.dsa.list;

public class ListReversalEngine {

    /**
     * Reverses a Singly Linked List in-place.
     * Time Complexity: O(n) single linear pass.
     * Space Complexity: O(1) auxiliary variables.
     */
    public static <E> Node<E> reverseList(Node<E> head) {
        Node<E> prev = null;
        Node<E> curr = head;

        while (curr != null) {
            Node<E> nextTemp = curr.next; // 1. Save reference to successor
            curr.next = prev;             // 2. Reverse direction of current pointer!
            prev = curr;                  // 3. Advance prev pointer
            curr = nextTemp;              // 4. Advance curr pointer
        }

        // When curr reaches null, 'prev' is the NEW HEAD of the reversed list!
        return prev;
    }

    public static void main(String[] args) {
        // Build 1 -> 2 -> 3 -> null
        Node<Integer> head = new Node<>(1, new Node<>(2, new Node<>(3, null)));

        System.out.print("Original: ");
        printList(head);

        Node<Integer> reversedHead = reverseList(head);

        System.out.print("Reversed: ");
        printList(reversedHead);
    }

    private static <E> void printList(Node<E> head) {
        Node<E> c = head;
        while (c != null) {
            System.out.print(c.data + " -> ");
            c = c.next;
        }
        System.out.println("null");
    }
}
```

#### Step-by-Step Pointer Animation:
For each node, saving `curr.next` into `nextTemp` prevents the fatal pointer loss error. Rerouting `curr.next = prev` points the link backward. Advancing both pointers preserves continuous progress through the chain until the list is completely inverted.
</details>
