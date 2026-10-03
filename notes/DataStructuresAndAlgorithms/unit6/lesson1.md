# Lesson 1 — Tree Hierarchical Topologies & Binary Tree Structural Axioms

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the mathematical graph invariants of **Hierarchical Non-Linear Tree Structures**.
> - Distinguish topological metrics: **Depth** vs. **Height**, **Level**, and **Degree**.
> - Eliminate $N$-ary pointer memory fragmentation using the **Left-Child / Right-Sibling (LCRS)** binary representation.
> - Classify the four fundamental binary tree taxonomies: **Full (Strict)**, **Complete**, **Perfect**, and **Balanced**.
> - Prove the fundamental structural theorem: in any strict binary tree, the leaf count $L$ strictly equals internal nodes $I + 1$.

{{media:tree-video}}

{{media:tree-visual}}

## Executive Summary & Topological Context

Until now, our curriculum has explored **Linear Data Structures**—Arrays, Linked Lists, Stacks, and Queues—where elements maintain a simple, sequential $1$-to-$1$ predecessor/successor relationship. While linear models are intuitive, real-world engineering domains are fundamentally **hierarchical** ($1$-to-$N$):
- **Operating Systems**: Unix/Linux hierarchical file system directories (`/`, `etc`, `var`, `usr`).
- **Web Engines**: Document Object Model (DOM) node trees in browsers and Abstract Syntax Trees (ASTs) in language compilers.
- **Enterprise Databases**: High-fanout B-Trees and Binary Search Trees powering indexed query retrieval.

A **Tree** is a non-linear data structure representing hierarchical relationships between entities. Deconstructing the structural axioms and geometric bounds of binary trees is mandatory before engineering search algorithms, balanced rotation engines, and persistent heaps.

---

## 1. Formal Tree Anatomy & Invariants

Mathematically, a Tree $T = (V, E)$ is an undirected, connected, acyclic graph. In computer science, trees are almost universally rooted and directed:
- Exactly one node is designated as the **Root** (having an in-degree of $0$).
- Every non-root node has an in-degree of exactly $1$ (a unique parent).
- There are no cycles (directed acyclic graph).

```
                        [ Root: 8 ]                 Level 1  (Depth = 0)
                       /           \
               [ Node: 3 ]       [ Node: 10 ]       Level 2  (Depth = 1)
               /         \                  \
        [ Leaf: 1 ]   [ Node: 6 ]        [ Node: 14 ] Level 3  (Depth = 2)
                      /         \             /
               [ Leaf: 4 ]   [ Leaf: 7 ]  [ Leaf: 13] Level 4  (Depth = 3)
```

### 1.1 Structural Metrics & Terminology
1. **Root**: The top-most origin node with no incoming parent edges.
2. **Leaf (External) Node**: A terminal node possessing zero children ($\text{degree} = 0$).
3. **Internal (Interior) Node**: Any non-leaf node possessing at least one child.
4. **Degree of a Node**: The number of children directly attached to that node.
5. **Degree of a Tree**: The maximum degree across all nodes in the tree ($D = \max_{u \in V} \text{deg}(u)$).
6. **Path**: A sequence of directed edges connecting an ancestor node to a descendant.
7. **Depth of a Node $u$**: The length (number of edges) of the path from the root to $u$. $\text{depth}(\text{root}) = 0$.
8. **Height of a Node $u$**: The length of the longest path from $u$ downward to any leaf. $\text{height}(\text{leaf}) = 0$.
9. **Height of a Tree**: The height of the root node, which equals the maximum depth among all nodes in $T$.
10. **Level**: Equal to $\text{depth}(u) + 1$ (1-based metric where root is at Level 1).

---

## 2. Generic $N$-ary Trees & The LCRS Pointer Optimization

In a generic $N$-ary tree, a node can have an arbitrary number of children (e.g., an organizational hierarchy like AASTU: President $\to$ VPs $\to$ Deans $\to$ Department Heads).

### 2.1 The Fixed-Pointer Array Dilemma
A naive implementation allocates a fixed-size pointer array at each node:
```java
// ANTI-PATTERN: MASSIVE MEMORY FRAGMENTATION
class NaryNode<T> {
    T data;
    NaryNode<T>[] children = new NaryNode[10]; // Capacity for 10 children
}
```
If a tree contains $N = 100,000$ nodes, but the average node only has $2$ children:
- $100,000 \times 10 = 1,000,000$ pointer slots are allocated.
- Only $200,000$ slots are used.
- **$800,000$ slots ($80\%$) sit completely wasted as null references!**

### 2.2 The Left-Child / Right-Sibling (LCRS) Representation
To achieve zero memory waste, computer scientists represent any arbitrary $N$-ary tree as a binary structure where each node stores only **two pointers**:
1. `firstChild`: Points to the node's first (left-most) child.
2. `nextSibling`: Points to the immediate right sibling sharing the identical parent.

```
       Generic N-ary Tree:                  Binary LCRS Equivalent:

              (A)                                      (A)
           /   |   \                                  /
         (B)  (C)  (D)                              (B) ──► (C) ──► (D)
             /   \                                         /
           (E)   (F)                                     (E) ──► (F)
```

With LCRS, every single node uses exactly two pointer references regardless of whether it has $0$, $5$, or $100$ children!

---

## 3. Binary Tree Structural Taxonomies

A **Binary Tree** is a tree in which every node has at most two children, strictly distinguished as the **Left Child** and the **Right Child**.

### 3.1 The Four Fundamental Taxonomies

| Binary Tree Classification | Formal Invariant Definition | Crucial Architectural Characteristic |
| :--- | :--- | :--- |
| **1. Full / Strict Binary Tree** | Every node has **strictly 0 or 2 children**. Never 1 child. | Leaf Count $L = \text{Internal Nodes } I + 1$ |
| **2. Complete Binary Tree** | All levels $0 \dots h-1$ are fully filled; level $h$ is filled **sequentially from left to right**. | Enables pointer-free array mapping (Binary Heaps) |
| **3. Perfect Binary Tree** | All internal nodes have 2 children, and **all leaves sit at identical depth**. | Exactly $2^{h+1} - 1$ total nodes; $2^h$ leaves |
| **4. Height-Balanced (AVL)**| For every node, $|\text{height}(\text{left}) - \text{height}(\text{right})| \le 1$. | Guarantees $O(\log n)$ worst-case search boundaries |

```
    FULL / STRICT:           COMPLETE:              PERFECT:             DEGENERATE / SKEWED:
         (O)                    (O)                   (O)                       (O)
        /   \                  /   \                 /   \                        \
      (O)   (O)              (O)   (O)             (O)   (O)                      (O)
           /   \            /   \  /              / \   / \                         \
         (O)   (O)        (O)  (O)(O)           (O) (O)(O) (O)                      (O)
```

---

## 4. Mathematical Bounds & Structural Theorems

Understanding tree geometry allows engineers to calculate memory footprints and algorithmic time complexities accurately.

### Theorem 1: Leaf-to-Internal Invariant in Strict Binary Trees
> **Theorem:** In any non-empty full (strict) binary tree with $L$ leaves and $I$ internal nodes:
> $$L = I + 1$$
> Consequently, the total number of nodes is $n = 2I + 1 = 2L - 1$.

**Proof by Induction on Internal Nodes $I$:**
- **Base Case ($I = 0$)**: The tree consists of only the root node. The root has no children, so it is a leaf. $L = 1$, $I = 0 \implies 1 = 0 + 1$. Holds.
- **Inductive Step**: Assume the property holds for all strict trees with $k$ internal nodes ($L_k = k + 1$).
  To construct a tree with $k + 1$ internal nodes, choose any existing leaf $u$ and convert it into an internal node by attaching two new leaf children.
  - Internal nodes increment: $I_{k+1} = k + 1$.
  - Old leaf $u$ is no longer a leaf ($-1$), but two new leaves are added ($+2$): $L_{k+1} = L_k - 1 + 2 = L_k + 1$.
  - By inductive hypothesis, $L_k = k + 1 \implies L_{k+1} = (k + 1) + 1 = I_{k+1} + 1$.
  - $\mathbf{Q.E.D.}$

### Theorem 2: Node Bounds in Binary Trees of Height $h$
- **Minimum Nodes for Height $h$**:
  $$n_{\min} = h + 1 \quad \text{(Degenerate path-like tree)}$$
- **Maximum Nodes for Height $h$**:
  $$n_{\max} = \sum_{i=0}^h 2^i = 2^{h+1} - 1 \quad \text{(Perfect binary tree)}$$
- **Height Bounds for $n$ Nodes**:
  $$\lfloor \log_2 n \rfloor \le h \le n - 1$$

---

## 5. Production Java Implementation: Node Architectures

```java
package edu.se.datastructures.trees;

public class BinaryTreeNode<E> {
    public E data;
    public BinaryTreeNode<E> left;
    public BinaryTreeNode<E> right;

    public BinaryTreeNode(E data) {
        this.data = data;
        this.left = null;
        this.right = null;
    }

    public boolean isLeaf() {
        return left == null && right == null;
    }

    public int height() {
        int leftH = (left == null) ? -1 : left.height();
        int rightH = (right == null) ? -1 : right.height();
        return 1 + Math.max(leftH, rightH);
    }
}
```

### 5.1 Generic LCRS Node Implementation
```java
package edu.se.datastructures.trees;

public class LcrsNode<E> {
    public E data;
    public LcrsNode<E> firstChild;
    public LcrsNode<E> nextSibling;

    public LcrsNode(E data) {
        this.data = data;
    }

    public void addChild(LcrsNode<E> child) {
        if (this.firstChild == null) {
            this.firstChild = child;
        } else {
            LcrsNode<E> sibling = this.firstChild;
            while (sibling.nextSibling != null) {
                sibling = sibling.nextSibling;
            }
            sibling.nextSibling = child;
        }
    }
}
```

---

## 6. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
A strict (full) binary tree contains $n = 1,023$ total nodes.
1. How many internal nodes $I$ does it contain?
2. How many leaf nodes $L$ does it contain?
3. What is the minimum possible height $h_{\min}$ of this tree?
4. What is the maximum possible height $h_{\max}$ of this tree?

<details>
<summary>View Level 1 Calculations & Proofs</summary>

1. **Internal Nodes $I$**:
   Since $n = 2I + 1 \implies 1023 = 2I + 1 \implies I = \mathbf{511}$.
2. **Leaf Nodes $L$**:
   $L = I + 1 \implies L = 511 + 1 = \mathbf{512}$ (or $n = 2L - 1 \implies 1023 = 2L - 1 \implies L = 512$).
3. **Minimum Height $h_{\min}$**:
   Minimum height occurs when the tree is a **Perfect Binary Tree**:
   $n = 2^{h+1} - 1 \implies 1023 = 2^{h+1} - 1 \implies 2^{h+1} = 1024 = 2^{10} \implies h_{\min} = \mathbf{9}$.
4. **Maximum Height $h_{\max}$**:
   In a strict binary tree, each internal node adds 1 to the height while having 2 children:
   $h_{\max} = I = \mathbf{511}$.
</details>

---

### Level 2: Scaffolded System Refactoring — Complete Binary Tree Validation
**Problem Statement:** Given the root of a binary tree, implement an algorithm that verifies whether the tree is a **Complete Binary Tree** in $O(n)$ time using Breadth-First Search (BFS).

<details>
<summary>View Complete Java CBT Validator Implementation</summary>

```java
package edu.se.datastructures.trees;

import java.util.ArrayDeque;
import java.util.Queue;

public class CompleteBinaryTreeValidator {

    public static <E> boolean isComplete(BinaryTreeNode<E> root) {
        if (root == null) return true;

        Queue<BinaryTreeNode<E>> queue = new ArrayDeque<>();
        queue.offer(root);
        boolean seenNull = false;

        while (!queue.isEmpty()) {
            BinaryTreeNode<E> curr = queue.poll();

            if (curr == null) {
                // Once a null child is observed in BFS order, NO MORE NON-NULL NODES are permitted!
                seenNull = true;
            } else {
                if (seenNull) {
                    return false; // Found a non-null node after a null node!
                }
                queue.offer(curr.left);
                queue.offer(curr.right);
            }
        }

        return true;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — LCRS Multi-Tenant Hierarchy Serializer
**Problem Statement:** Architect a high-throughput binary serialization engine for an enterprise organizational hierarchy using the LCRS representation. The serializer must write the tree to a compact byte buffer without recursion and reconstruct the identical multi-child tree upon deserialization.

<details>
<summary>View High-Throughput LCRS Serializer Implementation</summary>

```java
package edu.se.datastructures.trees;

import java.io.*;
import java.util.ArrayDeque;
import java.util.Deque;

public class LcrsTreeSerializer {

    public static void serialize(LcrsNode<String> root, DataOutputStream out) throws IOException {
        if (root == null) {
            out.writeUTF("#");
            return;
        }

        // Iterative pre-order traversal buffer
        Deque<LcrsNode<String>> stack = new ArrayDeque<>();
        stack.push(root);

        while (!stack.isEmpty()) {
            LcrsNode<String> node = stack.pop();
            if (node == null) {
                out.writeUTF("#");
            } else {
                out.writeUTF(node.data);
                // Push nextSibling and firstChild
                stack.push(node.nextSibling);
                stack.push(node.firstChild);
            }
        }
    }

    public static LcrsNode<String> deserialize(DataInputStream in) throws IOException {
        String token = in.readUTF();
        if (token.equals("#")) return null;

        LcrsNode<String> root = new LcrsNode<>(token);
        root.firstChild = deserialize(in);
        root.nextSibling = deserialize(in);
        return root;
    }
}
```
</details>
