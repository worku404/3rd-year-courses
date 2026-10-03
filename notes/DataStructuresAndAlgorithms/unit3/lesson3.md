# Lesson 3 — Circular Linked Lists, Ring Buffers & Real-World System Applications

> [!NOTE]
> **Learning Outcomes:**
> - Construct **Circular Linked Lists (CLL)** where the tail wraps back to the head, eliminating null pointers.
> - Exploit the single-pointer optimization: why storing **only the tail pointer** provides $O(1)$ access to both the tail and the head.
> - Formulate and prove **Floyd's Cycle-Finding Algorithm** (Tortoise and Hare) detecting loops in $O(n)$ time and $O(1)$ auxiliary space.
> - Trace the mathematical congruence finding the exact entry node of a cycle.
> - Architect a production **Least Recently Used (LRU) Cache** combining a `HashMap` with a Doubly Linked List for strict $O(1)$ read and write SLAs.

{{media:circular-video}}

{{media:circular-visual}}

## Executive Summary & System Context

In standard linear data structures, lists have distinct beginnings and ends marked by `null` terminators. However, many real-world computing systems operate on continuous cyclic patterns:
1. **Operating System Schedulers**: Time-shared OS kernels allocate CPU time slices to active processes in a continuous Round-Robin loop.
2. **Audio & Video Playback**: Media players loop audio tracks or stream circular ring buffers to maintain jitter-free DAC playback.
3. **Multiplayer Gaming**: Turn-based games cycle player turns in a continuous clockwise ring.

The **Circular Linked List (CLL)** models these cyclic domains natively by connecting the last node's `next` pointer back to the first node of the list, creating an infinite traversable ring.

---

## 1. Circular Linked List (CLL) Topologies

```
TOPOLOGY A: Circular Singly Linked List (CSLL)
         ┌────────────────────────────────────────────────────────┐
         ▼                                                        │
      ┌──────┬──────┐    ┌──────┬──────┐    ┌──────┬──────┐    ┌──────┴──────┐
      │  P1  │ 0x20 ┼───>│  P2  │ 0x30 ┼───>│  P3  │ 0x40 ┼───>│  P4  │ 0x10 │
      └──────┴──────┘    └──────┴──────┘    └──────┴──────┘    └─────────────┘
      Addr: 0x10         Addr: 0x20         Addr: 0x30         Addr: 0x40
      [ Head ]                                                 [ Tail ]

TOPOLOGY B: Circular Doubly Linked List (CDLL)
         ┌────────────────────────────────────────────────────────┐
         │  ┌──────────────────────────────────────────────────┐  │
         ▼  │                                                  ▼  │
      ┌──┴──┴┬──────┐    ┌──────┬──────┐    ┌──────┬──────┐    ┌──┴──┴┬──────┐
 <────┼─ P1  │ 0x20 ┼───>│  P2  │ 0x30 ┼───>│  P3  │ 0x40 ┼───>│  P4  │ 0x10 ┼────>
      └──────┴──────┘    └──────┴──────┘    └──────┴──────┘    └─────────────┘
      [ Head.prev == Tail ]                             [ Tail.next == Head ]
```

### The Single-Pointer Tail Optimization
In a linear Singly Linked List, one must maintain both a `head` and a `tail` pointer to achieve $O(1)$ prepending and appending.

In a **Circular Singly Linked List**, a remarkable architectural optimization exists: **we only need to store a single pointer: `tail`**!
- Accessing the **Tail**: Simply `tail` ($O(1)$).
- Accessing the **Head**: Simply `tail.next` ($O(1)$)!

By holding just one 64-bit reference address, the data structure grants instant access to both ends of the list with zero redundant state!

---

## 2. Circular Traversal Invariants

Because a circular list contains zero `null` pointers, attempting a standard traversal loop:
```java
// BUG: INFINITE LOOP!
while (curr != null) { curr = curr.next; }
```
will loop forever!

### The Proper `do-while` Traversal Idiom:
To traverse a Circular Singly Linked List, start at `head` (`tail.next`) and terminate when the cursor wraps back to `head`:

```java
public void printCircularList(Node<E> tail) {
    if (tail == null) return;

    Node<E> head = tail.next;
    Node<E> curr = head;

    do {
        System.out.print(curr.data + " -> ");
        curr = curr.next;
    } while (curr != head); // Terminates after exactly one complete cycle!

    System.out.println("(wraps back to head)");
}
```

---

## 3. Floyd's Cycle-Finding Algorithm: Tortoise and Hare

In software engineering, malformed pointer assignments (or malicious graph corruptions) can cause an intended linear list to accidentally form a closed loop.
- **The Problem**: How do you detect if a linked list contains an internal cycle **without modifying nodes** and **without allocating an $O(n)$ hash set of visited memory addresses**?

### The Algorithm:
Robert W. Floyd formulated the **Two-Pointer (Tortoise and Hare)** algorithm:
1. Initialize two pointers at `head`: `slow` and `fast`.
2. Advance `slow` by **1 step**: `slow = slow.next`.
3. Advance `fast` by **2 steps**: `fast = fast.next.next`.
4. If `fast` encounters `null`, the list is **acyclic** ($100\\%$ loop-free).
5. If `slow == fast` at any point, a **cycle is mathematically proven to exist**!

```
          [ m steps ]                    [ Cycle of length C ]
head ───> ... ─────────> [ Cycle Entrance ] ───> ... ───> [ Collision Point ]
                                ▲                                 │
                                └─────────────────────────────────┘
```

---

### The Mathematical Proof of Detection & Entry Location:

#### Phase 1: Proof of Inevitable Collision
- Let the cycle have length $C$.
- Once both pointers enter the cycle, let $d$ be the distance from `slow` to `fast` moving forward along the cycle ($0 \\le d < C$).
- In each iteration, `slow` moves forward by $1$ and `fast` moves forward by $2$.
- The relative gap between `fast` and `slow` increases by $2 - 1 = 1$ step per iteration (or equivalently, the distance behind shrinks by $1$).
- Therefore, within at most $C$ iterations after entering the loop, the distance must reach $0$: **`slow == fast` is guaranteed to occur!**

---

#### Phase 2: Locating the Exact Start Node of the Cycle
Let:
- $m$ = distance from `head` to the **Cycle Entrance**.
- $k$ = distance from the **Cycle Entrance** to the **Collision Point**.
- $C$ = total perimeter of the cycle.

When they collide:
- Total distance traveled by `slow`: $D_{\\text{slow}} = m + p \\cdot C + k$ (for some integer $p$).
- Total distance traveled by `fast`: $D_{\\text{fast}} = m + q \\cdot C + k$ (for some integer $q$).

Because `fast` runs at exactly twice the speed of `slow`:
$$D_{\\text{fast}} = 2 \\cdot D_{\\text{slow}}$$
$$m + q \\cdot C + k = 2(m + p \\cdot C + k)$$
$$m + k = (q - 2p) \\cdot C$$

> [!IMPORTANT]
> **The Key Mathematical Insight**: The distance $m + k$ is an **exact integer multiple of cycle length $C$**!
> Therefore:
> $$m = (q - 2p) \\cdot C - k$$

#### The Detection Algorithm:
1. Leave `fast` at the **Collision Point**.
2. Reset `slow` back to `head`.
3. Now, advance **BOTH `slow` and `fast` at the EXACT SAME SPEED (1 step per iteration)**!
4. By the time `slow` travels $m$ steps to reach the Cycle Entrance, `fast` has traveled $(q - 2p)C - k$ steps from the collision point—landing **AT THE EXACT SAME CYCLE ENTRANCE NODE**!

---

## 4. Enterprise Architecture: The Production LRU Cache

A **Least Recently Used (LRU) Cache** is the standard eviction algorithm in distributed databases (e.g., Redis, MySQL InnoDB Buffer Pool, operating system virtual memory page replacement).

### Problem Statement:
- Fixed capacity $C$.
- `get(key)`: Retrieve value and mark as **Most Recently Used**. Must run in **$O(1)$ Time**.
- `put(key, value)`: Insert/update value. If capacity exceeded, evict the **Least Recently Used** item. Must run in **$O(1)$ Time**.

### The Hybrid Solution: `HashMap` + Doubly Linked List
Neither a `HashMap` nor a `LinkedList` alone can satisfy both requirements:
- A `HashMap` provides $O(1)$ lookups, but cannot maintain ordering.
- A `LinkedList` maintains ordering, but takes $O(n)$ to search for a key.

By combining them:
1. A **Sentinel Doubly Linked List** maintains access recency:
   - `dummyHead.next` = **Most Recently Used (MRU)** item.
   - `dummyTail.prev` = **Least Recently Used (LRU)** item.
2. A **`HashMap<K, DoubleNode<K, V>>`** maps each key directly to its corresponding heap node pointer in the Doubly Linked List!

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ENTERPRISE LRU CACHE                            │
│                                                                        │
│   HASH MAP:                                                            │
│   "user:101" ───> [ Pointer to Node A ]                                │
│   "user:204" ───> [ Pointer to Node B ]                                │
│                                                                        │
│   DOUBLY LINKED LIST (Recency Ordering):                               │
│                  MRU                                     LRU           │
│   [ dummyHead ] <===> [ Node A ] <===> [ Node B ] <===> [ dummyTail ]  │
│                             ▲                                          │
│                             │ (O(1) Direct Pointer Access)             │
│                             └──────────────────────────────────────────┘
```

---

## 5. Comprehensive Trade-Off Matrix

| List Variation | Access Topology | Memory / Node (64-bit) | Deletion of Known Node | Primary System Application |
| :--- | :--- | :--- | :--- | :--- |
| **Singly Linked (SLL)** | Linear Unidirectional | $\\approx 32$ bytes | $O(n)$ (Predecessor scan) | Fast stacks, lock-free queues |
| **Doubly Linked (DLL)** | Linear Bidirectional | $\\approx 40-48$ bytes | $\\mathbf{O(1)}$ Constant | Deques, text editors, LRU list |
| **Circular Singly (CSLL)** | Cyclic Ring | $\\approx 32$ bytes | $O(n)$ | OS Round-Robin process schedulers |
| **Circular Doubly (CDLL)** | Cyclic Bidirectional | $\\approx 40-48$ bytes | $\\mathbf{O(1)}$ Constant | Linux kernel `list_head`, audio loops |
| **HashMap + DLL (LRU)** | Hybrid Associative | $\\approx 120$ bytes | $\\mathbf{O(1)}$ Constant | High-throughput in-memory caching |

---

## 6. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Floyd's Cycle Mathematics
**Objective**: A linked list has 4 linear nodes outside the cycle ($m = 4$), followed by a closed cycle of 6 nodes ($C = 6$).
Nodes are labeled $0, 1, 2, 3$ (outside) and $4, 5, 6, 7, 8, 9$ (cycle, where $9.next = 4$).
1. At what exact step does `slow` collide with `fast`?
2. At which node does the collision occur?
3. Verify that resetting `slow` to `head` and stepping both by 1 reaches the cycle entrance ($4$).

<details>
<summary>View Level 1 Mathematical Walkthrough & Verification</summary>

#### Step-by-Step Simulation:
- Slow advances 1 step: $S(t)$
- Fast advances 2 steps: $F(t)$

| Time Step $t$ | `slow` Position | `fast` Position | Notes |
| :---: | :---: | :---: | :--- |
| **0** | Node 0 | Node 0 | Start at head |
| **1** | Node 1 | Node 2 | |
| **2** | Node 2 | Node 4 | Fast enters cycle |
| **3** | Node 3 | Node 6 | |
| **4** | Node 4 | Node 8 | Slow enters cycle! (Entrance = 4) |
| **5** | Node 5 | Node 4 | Fast wraps around: $(8+2 - 4) \\% 6 + 4 = 4$ |
| **6** | Node 6 | Node 6 | **COLLISION! `slow == fast` at Node 6!** |

1. **Collision Step**: Exactly at **$t = 6$**.
2. **Collision Node**: **Node 6**.
3. **Phase 2 Verification**:
   - Reset `slow` to Node 0. Leave `fast` at Node 6.
   - Step 1: `slow` -> 1, `fast` -> 7.
   - Step 2: `slow` -> 2, `fast` -> 8.
   - Step 3: `slow` -> 3, `fast` -> 9.
   - Step 4: `slow` -> 4, `fast` -> 4 ($9.next == 4$).
   - **Both meet at Node 4: The exact Cycle Entrance! $\\blacksquare$**
</details>

---

### Level 2: Scaffolded System Refactoring — Floyd's Loop Detector & Start Finder
**Objective**: Implement a production method `detectCycleStart(Node head)` that:
- Returns `null` if the list is acyclic.
- Returns the exact `Node` where the cycle begins in $O(n)$ time and $O(1)$ space.

<details>
<summary>View Level 2 Complete Production Java Implementation</summary>

```java
package edu.se.dsa.cycle;

public class CycleDetector {

    public static class Node {
        public int val;
        public Node next;
        public Node(int val) { this.val = val; }
    }

    /**
     * Floyd's Cycle-Finding Algorithm.
     * Detects cycle and returns the cycle entrance node.
     * Time Complexity: O(n). Auxiliary Space: O(1).
     */
    public static Node detectCycleStart(Node head) {
        if (head == null || head.next == null) return null;

        Node slow = head;
        Node fast = head;

        // Phase 1: Detect presence of cycle via collision
        boolean hasCycle = false;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;

            if (slow == fast) {
                hasCycle = true;
                break; // Collision detected!
            }
        }

        if (!hasCycle) return null; // Acyclic list

        // Phase 2: Find cycle entrance node
        slow = head; // Reset slow to head; fast remains at collision point
        while (slow != fast) {
            slow = slow.next; // Advance 1 step
            fast = fast.next; // Advance 1 step
        }

        return slow; // Both pointers intersect at cycle entrance!
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — Production-Grade Generic LRU Cache
**Objective**: Build a complete, thread-safe production `LRUCache<K, V>` implementing the hybrid **HashMap + Sentinel Doubly Linked List** pattern.
- Must support generic keys and values (`K`, `V`).
- Must guarantee strictly **$O(1)$ Time Complexity** for both `get(K key)` and `put(K key, V value)`.
- Evict the least recently used item whenever capacity is exceeded.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.dsa.cache;

import java.util.HashMap;
import java.util.Map;

/**
 * Enterprise Production LRU (Least Recently Used) Cache.
 * Backed by HashMap for O(1) key indexing and Sentinel DLL for O(1) recency eviction.
 */
public class LRUCache<K, V> {

    private static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev;
        Node<K, V> next;

        Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    private final int capacity;
    private final Map<K, Node<K, V>> map;
    private final Node<K, V> dummyHead;
    private final Node<K, V> dummyTail;

    public LRUCache(int capacity) {
        if (capacity < 1) throw new IllegalArgumentException("Capacity must be >= 1");
        this.capacity = capacity;
        this.map = new HashMap<>(capacity);

        // Initialize Sentinel Nodes
        dummyHead = new Node<>(null, null);
        dummyTail = new Node<>(null, null);
        dummyHead.next = dummyTail;
        dummyTail.prev = dummyHead;
    }

    public synchronized V get(K key) {
        Node<K, V> node = map.get(key);
        if (node == null) {
            return null; // Cache Miss
        }
        // Cache Hit: Move node to MRU position (immediately after dummyHead)
        moveToHead(node);
        return node.value;
    }

    public synchronized void put(K key, V value) {
        Node<K, V> existing = map.get(key);

        if (existing != null) {
            // Update existing value and promote to MRU
            existing.value = value;
            moveToHead(existing);
        } else {
            // Check capacity before inserting new node
            if (map.size() >= capacity) {
                // Evict LRU node (immediately before dummyTail)
                Node<K, V> lru = dummyTail.prev;
                removeNode(lru);
                map.remove(lru.key);
            }

            Node<K, V> newNode = new Node<>(key, value);
            addFirst(newNode);
            map.put(key, newNode);
        }
    }

    private void addFirst(Node<K, V> node) {
        node.prev = dummyHead;
        node.next = dummyHead.next;
        dummyHead.next.prev = node;
        dummyHead.next = node;
    }

    private void removeNode(Node<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private void moveToHead(Node<K, V> node) {
        removeNode(node);
        addFirst(node);
    }

    public synchronized int size() {
        return map.size();
    }

    public static void main(String[] args) {
        LRUCache<String, Integer> cache = new LRUCache<>(2);

        cache.put("A", 100);
        cache.put("B", 200);
        System.out.println("Get A: " + cache.get("A")); // 100 (A becomes MRU)

        cache.put("C", 300); // Capacity full! Evicts B (LRU)!
        System.out.println("Get B (Evicted): " + cache.get("B")); // null
        System.out.println("Get C: " + cache.get("C")); // 300
    }
}
```

#### Architectural Key Insight:
1. `map.get(key)` locates the target `Node` in $O(1)$ time.
2. `removeNode(node)` unlinks the node in $O(1)$ using its own `prev` and `next` pointers.
3. `addFirst(node)` splices it back in as MRU in $O(1)$.
Every single user operation executes with zero loops: **Strictly $O(1)$ SLA Guaranteed**!
</details>
