# Lesson 3 — Binary Search Trees (BST): Search, Insertion, Deletion Mechanics & AVL Balancing

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the formal ordering axioms of the **Binary Search Tree (BST)** data structure.
> - Implement $O(h)$ **Search** and **Insertion** state machines while preserving the BST ordering invariant.
> - Execute the three canonical **Deletion** cases: Leaf removal, Single-Child splicing, and Two-Child substitution.
> - Contrast **Deletion by Merging** against **Deletion by Copying** (In-Order Predecessor vs. Successor).
> - Analyze pathological tree degeneration ($O(n)$ skew) and derive the four fundamental **AVL Balancing Rotations (LL, RR, LR, RL)**.

{{media:bst-video}}

{{media:bst-visual}}

## Executive Summary & Computational Context

In sorted arrays, searching is fast ($O(\log n)$ via Binary Search), but inserting or deleting an element incurs a devastating $O(n)$ data-shifting penalty. Conversely, in linked lists, inserting or deleting at a known position is instantaneous ($O(1)$), but searching requires an expensive $O(n)$ linear scan.

The **Binary Search Tree (BST)** resolves this fundamental software engineering dilemma by combining the logarithmic search capability of a sorted array with the dynamic pointer-linking flexibility of a linked list. By enforcing a recursive structural order—where all elements in a node's left subtree are strictly smaller, and all elements in its right subtree are strictly greater—a BST theoretically delivers $O(\log n)$ time for Search, Insertion, and Deletion. However, if the tree becomes unbalanced, performance degenerates into a linear linked list ($O(n)$), making **Self-Balancing Trees (AVL Trees)** an indispensable engineering paradigm.

---

## 1. BST Ordering Axioms & Formal Specification

A Binary Search Tree (BST) is a binary tree in which every node $u$ satisfies the **Binary Search Invariant**:
1. For every node $v$ in the **left subtree** of $u$:
   $$\text{key}(v) < \text{key}(u)$$
2. For every node $w$ in the **right subtree** of $u$:
   $$\text{key}(w) > \text{key}(u)$$
3. Both the left and right subtrees are themselves Binary Search Trees.
4. **No duplicate keys** are permitted (or duplicates are maintained via explicit frequency counters).

```
                            [ Node: 10 ]
                           /            \
                     [ Left < 10 ]    [ Right > 10 ]
                     ┌──────────┐      ┌──────────┐
                     │ 2, 5     │      │ 25, 30,45│
                     └──────────┘      └──────────┘
```

> [!IMPORTANT]
> **The Global Subtree Trap:**
> It is NOT sufficient for a node to merely be larger than its immediate left child! **Every single node in the entire left subtree** must be smaller than the ancestor. For instance, if root is $10$, its left child is $5$, and $5$'s right child is $15$, the local check ($5 < 10$ and $5 < 15$) passes, but the BST invariant is violated globally because $15 > 10$.

---

## 2. Search & Insertion Mechanics

### 2.1 Iterative Search Algorithm ($O(h)$)
Searching in a BST is a direct binary partitioning: if the target key is less than the current node, branch left; if greater, branch right; if equal, search terminates successfully.

```java
public BinaryTreeNode<E> find(BinaryTreeNode<E> root, E key) {
    BinaryTreeNode<E> curr = root;
    while (curr != null) {
        int cmp = key.compareTo(curr.data);
        if (cmp < 0) {
            curr = curr.left; // Target resides in left subtree
        } else if (cmp > 0) {
            curr = curr.right; // Target resides in right subtree
        } else {
            return curr; // Key located!
        }
    }
    return null; // Key absent from tree
}
```

### 2.2 Insertion Dynamics ($O(h)$)
Insertion always attaches the new element as a **Leaf Node** at the terminal boundary where a search for that key would have terminated with `null`:

```java
public BinaryTreeNode<E> insert(BinaryTreeNode<E> root, E key) {
    if (root == null) return new BinaryTreeNode<>(key);

    BinaryTreeNode<E> curr = root;
    BinaryTreeNode<E> parent = null;
    int cmp = 0;

    while (curr != null) {
        parent = curr;
        cmp = key.compareTo(curr.data);
        if (cmp < 0) {
            curr = curr.left;
        } else if (cmp > 0) {
            curr = curr.right;
        } else {
            return root; // Duplicate key: ignore or increment frequency counter
        }
    }

    BinaryTreeNode<E> newNode = new BinaryTreeNode<>(key);
    if (cmp < 0) {
        parent.left = newNode;
    } else {
        parent.right = newNode;
    }

    return root;
}
```

---

## 3. Deletion Mechanics: The Three Canonical Cases

Deleting a node from a BST is significantly more complex because the structural hierarchy and the binary search ordering invariant must both be strictly preserved.

```
       Case 1: LEAF NODE              Case 2: ONE CHILD               Case 3: TWO CHILDREN
           (Parent)                       (Parent)                          (Target)
              │                              │                             /        \
           (Target)                       (Target)                     (Left)      (Right)
                                             │                                        │
           Set parent pointer             (Child)                          Find In-Order Successor
           to null!                       Bypass Target:                   (Smallest in Right Tree)
                                          parent.left = child!             Copy value -> Delete leaf!
```

### Case 1: The Target Node is a Leaf (0 Children)
- **Action**: The parent's pointer to the target node is simply set to `null`, and the node is reclaimed.
- **Complexity**: $O(h)$ search $+ O(1)$ pointer assignment.

### Case 2: The Target Node has Exactly 1 Child
- **Action**: Splicing/Bypassing. The parent's pointer to the target node is updated to point directly to the target's sole child (whether left or right).
- **Complexity**: $O(h)$ search $+ O(1)$ pointer assignment.

### Case 3: The Target Node has Two Children (Complex)
When a node has two active subtrees, removing it leaves a vacant root position that must be filled by a valid substitute key. There are two major algorithmic techniques:

#### Method A: Deletion by Merging (Curriculum Slide 30)
- In a BST, every key in the left subtree is strictly smaller than every key in the right subtree.
- Locate the **largest element in the left subtree** (the in-order predecessor).
- Attach the entire right subtree as the right child of this predecessor node.
- Attach the left subtree to the target node's parent.
- **Architectural Drawback**: Merging repeatedly deepens the tree, severely increasing tree height $h$ and accelerating degradation.

#### Method B: Deletion by Copying (Curriculum Slides 32–38) — *Standard Production Choice*
Instead of merging massive subtrees, we replace the target node's value with an adjacent key that preserves ordering, reducing the structural removal to Case 1 or Case 2:
1. Find the target's **In-Order Successor** $S$ (the smallest element in the right subtree: `node.right` followed by drilling left until `left == null`).
   *(Alternatively, find the In-Order Predecessor: largest in left subtree).*
2. Copy $S$'s key into the target node.
3. Delete node $S$ from the right subtree.
   *(Because $S$ is the minimum of the right subtree, it is mathematically guaranteed to have **at most one child**—specifically, no left child! Thus, deleting $S$ is trivially Case 1 or Case 2).*

---

## 4. Production Java Implementation: Recursive BST Deletion

```java
package edu.se.datastructures.trees;

public class BinarySearchTree<E extends Comparable<E>> {
    private BinaryTreeNode<E> root;

    public void delete(E key) {
        this.root = deleteRec(this.root, key);
    }

    private BinaryTreeNode<E> deleteRec(BinaryTreeNode<E> curr, E key) {
        if (curr == null) return null; // Key absent from tree

        int cmp = key.compareTo(curr.data);
        if (cmp < 0) {
            curr.left = deleteRec(curr.left, key);
        } else if (cmp > 0) {
            curr.right = deleteRec(curr.right, key);
        } else {
            // Target Node Found! Execute Deletion Cases:

            // Case 1: Leaf (both null) OR Case 2: Single child (left null)
            if (curr.left == null) return curr.right;

            // Case 2: Single child (right null)
            if (curr.right == null) return curr.left;

            // Case 3: Two Children! Execute Deletion by Copying
            // Find In-Order Successor (smallest value in right subtree)
            BinaryTreeNode<E> successor = findMin(curr.right);

            // Copy successor value to current node
            curr.data = successor.data;

            // Recursively delete the successor node from the right subtree
            curr.right = deleteRec(curr.right, successor.data);
        }
        return curr;
    }

    private BinaryTreeNode<E> findMin(BinaryTreeNode<E> node) {
        while (node.left != null) {
            node = node.left;
        }
        return node;
    }
}
```

---

## 5. Pathological Degeneration & The Self-Balancing Need

The computational complexity of BST operations depends entirely on tree height $h$:
$$\text{Time Complexity} = \mathbf{O(h)}$$
- In an optimally balanced BST: $h = \lfloor \log_2 n \rfloor \implies \mathbf{O(\log n)}$.
- **The Presorted Input Catastrophe**:
  Suppose elements arrive in ascending sorted order: `10, 20, 30, 40, 50`.
  Every incoming element is larger than the previous, branching exclusively to the right:
  ```
       (10)
          \
          (20)
             \
             (30)
                \
                (40)
                   \
                   (50)
  ```
  The BST degenerates into a **Singly Linked List** of height $h = n - 1$.
  Search time collapses from $O(\log n)$ to a sluggish $\mathbf{O(n)}$!

---

## 6. Self-Balancing Foundations: AVL Tree Rotations

To prevent pathological skewing, Georgy Adelson-Velsky and Evgenii Landis invented the **AVL Tree** in 1962.

### 6.1 The Balance Factor (BF) Invariant
For every node $u$ in an AVL tree, the **Balance Factor** is defined as:
$$\text{BF}(u) = \text{height}(\text{left}) - \text{height}(\text{right})$$
An AVL tree strictly mandates:
$$\text{BF}(u) \in \{-1, 0, +1\}$$
If any insertion or deletion causes $|\text{BF}(u)| \ge 2$, the node is unbalanced, and the tree executes an immediate $O(1)$ **Tree Rotation**.

### 6.2 The Four Canonical Balancing Rotations

| Imbalance Type | Condition | Corrective Rotation | Algebraic Transformation |
| :--- | :--- | :--- | :--- |
| **Left-Left (LL)** | $\text{BF}(\text{Node}) = +2$ and $\text{BF}(\text{LeftChild}) \ge 0$ | **Single Right Rotation** | `rotateRight(Node)` |
| **Right-Right (RR)**| $\text{BF}(\text{Node}) = -2$ and $\text{BF}(\text{RightChild}) \le 0$ | **Single Left Rotation** | `rotateLeft(Node)` |
| **Left-Right (LR)** | $\text{BF}(\text{Node}) = +2$ and $\text{BF}(\text{LeftChild}) < 0$ | **Double Rotation (Left-Right)** | `rotateLeft(LeftChild) -> rotateRight(Node)` |
| **Right-Left (RL)** | $\text{BF}(\text{Node}) = -2$ and $\text{BF}(\text{RightChild}) > 0$ | **Double Rotation (Right-Left)** | `rotateRight(RightChild) -> rotateLeft(Node)` |

```
       RIGHT ROTATION (LL CASE):

              [ Z ] (BF = +2)                         [ Y ] (BF = 0)
             /     \                                 /     \
           [ Y ]    T3        Rotate Right         [ X ]   [ Z ]
          /     \           ────────────────►     /    \   /   \
        [ X ]    T2                              T1    T2 T3   T4
       /     \
      T1     T4
```

---

## 7. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Given the BST below:
```
              [ 10 ]
             /      \
          [ 5 ]    [ 30 ]
          /        /    \
        [ 2 ]   [ 25 ]  [ 45 ]
```
Trace the exact tree mutations when:
1. `delete(25)`
2. `delete(10)` using In-Order Successor copying.

<details>
<summary>View Level 1 Step-by-Step Deletion Trace</summary>

**Step 1: `delete(25)`**
- Search: $25 > 10$ (right), $25 < 30$ (left), found 25.
- Classification: Node 25 is a **Leaf Node (Case 1)**.
- Action: Clear parent pointer `30.left = null`.
- Tree becomes:
```
              [ 10 ]
             /      \
          [ 5 ]    [ 30 ]
          /             \
        [ 2 ]          [ 45 ]
```

**Step 2: `delete(10)` (Root removal with 2 children)**
- Target: Node 10 has two active children (5 and 30) $\implies$ **Case 3**.
- Find In-Order Successor: Smallest in right subtree (`10.right` which is 30; drill left $\implies$ 30 has no left child, so 30 is the minimum!).
- Copy value 30 to root: `root.data = 30`.
- Delete original successor node 30 from right subtree:
  - Node 30 has exactly one right child (45) $\implies$ **Case 2**.
  - Bypass 30: `root.right = 45`.
- **Final Resulting Tree:**
```
              [ 30 ]
             /      \
          [ 5 ]    [ 45 ]
          /
        [ 2 ]
```
</details>

---

### Level 2: Scaffolded System Refactoring — BST Validator with Range Invariants
**Problem Statement:** Write an algorithm that validates whether an arbitrary binary tree is a strictly valid Binary Search Tree in $O(n)$ time. Guard against the "Local Subtree Trap" using recursive lower and upper bounds.

<details>
<summary>View Complete Java BST Validator Implementation</summary>

```java
package edu.se.datastructures.trees;

public class BstValidator {

    public static boolean isValidBst(BinaryTreeNode<Integer> root) {
        return validate(root, null, null);
    }

    private static boolean validate(BinaryTreeNode<Integer> node, Integer minBound, Integer maxBound) {
        if (node == null) return true;

        // Current node MUST strictly satisfy range: minBound < node.data < maxBound
        if (minBound != null && node.data <= minBound) return false;
        if (maxBound != null && node.data >= maxBound) return false;

        // Left subtree must be < node.data; Right subtree must be > node.data
        return validate(node.left, minBound, node.data) &&
               validate(node.right, node.data, maxBound);
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Production AVL Node Auto-Balancer
**Problem Statement:** Implement the rotation and rebalancing routines for an AVL Tree in Java. Upon inserting a key, update node heights and restore the Balance Factor within $\{-1, 0, +1\}$ using single and double rotations.

<details>
<summary>View Complete Java AVL Balancing Engine</summary>

```java
package edu.se.datastructures.trees;

public class AvlTree<E extends Comparable<E>> {

    public static class AvlNode<E> {
        public E data;
        public int height;
        public AvlNode<E> left;
        public AvlNode<E> right;

        public AvlNode(E data) {
            this.data = data;
            this.height = 0;
        }
    }

    private AvlNode<E> root;

    private int height(AvlNode<E> n) {
        return (n == null) ? -1 : n.height;
    }

    private int getBalance(AvlNode<E> n) {
        return (n == null) ? 0 : height(n.left) - height(n.right);
    }

    private void updateHeight(AvlNode<E> n) {
        n.height = 1 + Math.max(height(n.left), height(n.right));
    }

    private AvlNode<E> rotateRight(AvlNode<E> y) {
        AvlNode<E> x = y.left;
        AvlNode<E> t2 = x.right;

        // Execute rotation
        x.right = y;
        y.left = t2;

        // Update heights
        updateHeight(y);
        updateHeight(x);

        return x; // New root of rotated subtree
    }

    private AvlNode<E> rotateLeft(AvlNode<E> x) {
        AvlNode<E> y = x.right;
        AvlNode<E> t2 = y.left;

        // Execute rotation
        y.left = x;
        x.right = t2;

        // Update heights
        updateHeight(x);
        updateHeight(y);

        return y; // New root of rotated subtree
    }

    public void insert(E key) {
        this.root = insertRec(this.root, key);
    }

    private AvlNode<E> insertRec(AvlNode<E> node, E key) {
        if (node == null) return new AvlNode<>(key);

        int cmp = key.compareTo(node.data);
        if (cmp < 0) {
            node.left = insertRec(node.left, key);
        } else if (cmp > 0) {
            node.right = insertRec(node.right, key);
        } else {
            return node; // Duplicate keys not permitted
        }

        updateHeight(node);
        int balance = getBalance(node);

        // LL Case -> Single Right Rotate
        if (balance > 1 && key.compareTo(node.left.data) < 0) {
            return rotateRight(node);
        }

        // RR Case -> Single Left Rotate
        if (balance < -1 && key.compareTo(node.right.data) > 0) {
            return rotateLeft(node);
        }

        // LR Case -> Double Rotate (Left then Right)
        if (balance > 1 && key.compareTo(node.left.data) > 0) {
            node.left = rotateLeft(node.left);
            return rotateRight(node);
        }

        // RL Case -> Double Rotate (Right then Left)
        if (balance < -1 && key.compareTo(node.right.data) < 0) {
            node.right = rotateRight(node.right);
            return rotateLeft(node);
        }

        return node;
    }
}
```
</details>
