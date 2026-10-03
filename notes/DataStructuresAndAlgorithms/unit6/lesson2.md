# Lesson 2 — Tree Traversal Topologies: Depth-First (DFS) & Breadth-First (BFS)

> [!NOTE]
> **Learning Outcomes:**
> - Contrast the topological execution models of **Depth-First Search (DFS)** and **Breadth-First Search (BFS)** tree traversals.
> - Formalize the recursive visiting sequences: **Pre-Order ($N-L-R$)**, **In-Order ($L-N-R$)**, and **Post-Order ($L-R-N$)**.
> - Prove why In-Order traversal on a Binary Search Tree produces a strictly monotonic sorted permutation of keys.
> - Implement iterative tree traversals using explicit heap stacks, eliminating JVM `-Xss` `StackOverflowError` vulnerabilities.
> - Engineer **Morris In-Order Traversal** using threaded pointers to achieve traversal in $O(1)$ auxiliary memory.

{{media:traversal-video}}

{{media:traversal-visual}}

## Executive Summary & Computational Context

In a linear collection, traversing elements is straightforward: an iterator moves monotonically from index $0$ to $n - 1$. In a hierarchical non-linear **Tree Structure**, however, a node has multiple independent descendant paths. A systematic **Traversal Algorithm** is a deterministic procedure that visits every single node in the tree **exactly once**.

Tree traversals fall into two broad computational categories:
1. **Depth-First Search (DFS)**: Recursively penetrates along a single branch to its terminal leaves before backtracking. Divided into **Pre-Order**, **In-Order**, and **Post-Order** depending on when the parent node is processed relative to its subtrees.
2. **Breadth-First Search (BFS)**: Explores nodes layer-by-layer along horizontal geometric levels using a First-In, First-Out (FIFO) queue.

---

## 1. Depth-First Traversal Disciplines

Let $T$ be a binary tree with root node $N$, left subtree $L$, and right subtree $R$.

### 1.1 Pre-Order Traversal ($N - L - R$)
- **Order of Execution**: Visit Root Node $\to$ Traverse Left Subtree $\to$ Traverse Right Subtree.
- **Architectural Utility**: Serialization, cloning trees, generating **Prefix (Polish)** notation, directory structure cloning.
```java
public void preOrder(BinaryTreeNode<E> node) {
    if (node == null) return;
    visit(node.data);
    preOrder(node.left);
    preOrder(node.right);
}
```

### 1.2 In-Order Traversal ($L - N - R$)
- **Order of Execution**: Traverse Left Subtree $\to$ Visit Root Node $\to$ Traverse Right Subtree.
- **Architectural Utility**: In a Binary Search Tree (BST), In-Order traversal visits keys in **strictly ascending sorted order**. Also reconstructs parenthesized **Infix** mathematical expressions.
```java
public void inOrder(BinaryTreeNode<E> node) {
    if (node == null) return;
    inOrder(node.left);
    visit(node.data);
    inOrder(node.right);
}
```

### 1.3 Post-Order Traversal ($L - R - N$)
- **Order of Execution**: Traverse Left Subtree $\to$ Traverse Right Subtree $\to$ Visit Root Node.
- **Architectural Utility**: Essential for bottom-up computational dependencies:
  - Evaluating **Postfix (RPN)** algebraic expression trees.
  - Computing disk space usage of hierarchical directory trees (children must be measured before the parent folder size is known).
  - Memory deallocation in unmanaged languages like C/C++ (child nodes must be deleted before the parent pointer is destroyed).
```java
public void postOrder(BinaryTreeNode<E> node) {
    if (node == null) return;
    postOrder(node.left);
    postOrder(node.right);
    visit(node.data);
}
```

---

## 2. Curriculum Algebraic Expression Tree Trace (Slides 45–49)

Consider the complex university curriculum expression tree from the slide deck:
```
                                 [ + ]
                                /     \
                        [ - ]             [ % ]
                       /     \           /     \
                    [ A ]   [ * ]     [ * ]   [ 4 ]
                           /     \   /     \
                        [ / ]   [2] [ D ] [ 5 ]
                       /     \
                    [ C ]   [ 5 ]
```

### Tracing the Three Orders Across the Tree:
1. **Pre-Order ($N-L-R$)**:
   $$\mathbf{+ \quad - \quad A \quad * \quad / \quad C \quad 5 \quad 2 \quad \% \quad * \quad D \quad 5 \quad 4}$$
   *(Generates Polish Prefix notation; root operator $+$ appears at the very beginning).*

2. **In-Order ($L-N-R$)**:
   $$\mathbf{A \quad - \quad C \quad / \quad 5 \quad * \quad 2 \quad + \quad D \quad * \quad 5 \quad \% \quad 4}$$
   *(Generates Infix notation; operations appear between operands).*

3. **Post-Order ($L-R-N$)**:
   $$\mathbf{A \quad C \quad 5 \quad / \quad 2 \quad * \quad - \quad D \quad 5 \quad * \quad 4 \quad \% \quad +}$$
   *(Generates Reverse Polish Notation; root operator $+$ evaluated last).*

---

## 3. Breadth-First Search (BFS) / Level-Order Traversal

While DFS uses a LIFO call stack to drill vertically, BFS uses a **FIFO Queue** to visit nodes horizontally level by level (Level 1, Level 2, Level 3, etc.).

```java
package edu.se.datastructures.traversal;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;

public class LevelOrderTraversal {

    public static <E> List<List<E>> levelOrder(BinaryTreeNode<E> root) {
        List<List<E>> result = new ArrayList<>();
        if (root == null) return result;

        Queue<BinaryTreeNode<E>> queue = new ArrayDeque<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            List<E> currentLevel = new ArrayList<>(levelSize);

            for (int i = 0; i < levelSize; i++) {
                BinaryTreeNode<E> curr = queue.poll();
                currentLevel.add(curr.data);

                if (curr.left != null) queue.offer(curr.left);
                if (curr.right != null) queue.offer(curr.right);
            }
            result.add(currentLevel);
        }

        return result;
    }
}
```

### 3.1 Memory Model: DFS ($O(h)$) vs. BFS ($O(w)$)
- **DFS Auxiliary Memory**: Proportional to the **height** of the tree $h$. In a balanced tree, $h = \log_2 n$. Memory footprint is tiny: for $1,000,000$ nodes, stack depth is only $\approx 20$ frames.
- **BFS Auxiliary Memory**: Proportional to the maximum **width** (broadest level) of the tree $w$. In a balanced tree, the bottom level contains $w = 2^{\log_2 n} = \lceil n / 2 \rceil$ nodes! For $1,000,000$ nodes, the queue must simultaneously buffer $\mathbf{500,000}$ node references.

---

## 4. Production Iterative Traversal Engines (Eliminating Recursion)

In high-reliability enterprise software, deep trees (such as ASTs generated from massive source files) can exceed the JVM thread stack limit (default 1MB `-Xss`), triggering a fatal `java.lang.StackOverflowError`. Production search engines (e.g. Apache Lucene) convert recursive traversals into **Iterative Stack Loops** that allocate frames on the multi-gigabyte Java Heap.

### 4.1 Production Iterative In-Order Traversal
```java
package edu.se.datastructures.traversal;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class IterativeInOrder {

    public static <E> List<E> inOrder(BinaryTreeNode<E> root) {
        List<E> result = new ArrayList<>();
        Deque<BinaryTreeNode<E>> stack = new ArrayDeque<>();
        BinaryTreeNode<E> curr = root;

        while (curr != null || !stack.isEmpty()) {
            // Drill down to the left-most leaf of the current subtree
            while (curr != null) {
                stack.push(curr);
                curr = curr.left;
            }

            // Pop the root of the smallest pending subtree
            curr = stack.pop();
            result.add(curr.data); // Visit node

            // Shift to right subtree
            curr = curr.right;
        }

        return result;
    }
}
```

---

## 5. Morris In-Order Traversal ($O(1)$ Auxiliary Space)

In 1979, J. Henry Morris published an algorithm capable of traversing a binary tree in strictly **$O(1)$ auxiliary memory** without using recursion, stacks, or queues.

### 5.1 The Threaded Pointer Mechanism
Morris traversal exploits unused `null` right child pointers of leaf nodes to create temporary return links ("threads") back to the in-order successor parent:
1. Initialize `curr = root`.
2. While `curr != null`:
   - If `curr.left == null`:
     - Visit `curr.data`.
     - `curr = curr.right`.
   - Else:
     - Find the **In-Order Predecessor** of `curr` (right-most node in left subtree).
     - If `predecessor.right == null`:
       - Create thread: `predecessor.right = curr`.
       - `curr = curr.left`.
     - Else (thread already exists!):
       - Remove thread: `predecessor.right = null`.
       - Visit `curr.data`.
       - `curr = curr.right`.

```java
package edu.se.datastructures.traversal;

import java.util.ArrayList;
import java.util.List;

public class MorrisTraversal {

    public static <E> List<E> inOrder(BinaryTreeNode<E> root) {
        List<E> result = new ArrayList<>();
        BinaryTreeNode<E> curr = root;

        while (curr != null) {
            if (curr.left == null) {
                result.add(curr.data);
                curr = curr.right;
            } else {
                // Find in-order predecessor
                BinaryTreeNode<E> pred = curr.left;
                while (pred.right != null && pred.right != curr) {
                    pred = pred.right;
                }

                if (pred.right == null) {
                    pred.right = curr; // Establish temporary backward thread
                    curr = curr.left;
                } else {
                    pred.right = null; // Sever temporary thread
                    result.add(curr.data);
                    curr = curr.right;
                }
            }
        }

        return result;
    }
}
```

---

## 6. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Trace the execution of Iterative In-Order traversal on the binary tree:
```
       [ 10 ]
       /    \
     [ 5 ]  [ 20 ]
     /
   [ 2 ]
```
Show the exact contents of the `stack`, the variable `curr`, and the `output` list after each iteration of the outer loop.

<details>
<summary>View Level 1 Trace Table</summary>

| Step | Inner Loop Action | Stack State | Popped / Visited | `curr` Next Pointer | Output Buffer |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Push 10, Push 5, Push 2 (`curr` -> null) | `[10, 5, 2]` | Pop 2 | `2.right` (null) | `[ 2 ]` |
| 2 | Stack not empty; pop top | `[10, 5]` | Pop 5 | `5.right` (null) | `[ 2, 5 ]` |
| 3 | Stack not empty; pop top | `[10]` | Pop 10 | `10.right` (Node 20) | `[ 2, 5, 10 ]` |
| 4 | `curr != null`; push 20 (`curr` -> null) | `[20]` | Pop 20 | `20.right` (null) | `[ 2, 5, 10, 20 ]` |
| 5 | `curr == null` and stack empty | `[]` | - | - | **Terminated** |
</details>

---

### Level 2: Scaffolded System Refactoring — Reconstruct Tree from Preorder & Inorder
**Problem Statement:** Given two integer arrays representing the `preorder` and `inorder` traversals of a unique binary tree, reconstruct the exact original binary tree in $O(n)$ time using a hash map lookup.

<details>
<summary>View Complete Java Reconstruction Implementation</summary>

```java
package edu.se.datastructures.traversal;

import java.util.HashMap;
import java.util.Map;

public class TreeReconstructor {

    public static BinaryTreeNode<Integer> buildTree(int[] preorder, int[] inorder) {
        Map<Integer, Integer> inMap = new HashMap<>();
        for (int i = 0; i < inorder.length; i++) {
            inMap.put(inorder[i], i);
        }
        return build(preorder, 0, preorder.length - 1, 0, inorder.length - 1, inMap);
    }

    private static BinaryTreeNode<Integer> build(
            int[] preorder, int preStart, int preEnd,
            int inStart, int inEnd, Map<Integer, Integer> inMap) {

        if (preStart > preEnd || inStart > inEnd) return null;

        int rootVal = preorder[preStart];
        BinaryTreeNode<Integer> root = new BinaryTreeNode<>(rootVal);

        int inRootIdx = inMap.get(rootVal);
        int numsLeft = inRootIdx - inStart;

        root.left = build(preorder, preStart + 1, preStart + numsLeft, inStart, inRootIdx - 1, inMap);
        root.right = build(preorder, preStart + numsLeft + 1, preEnd, inRootIdx + 1, inEnd, inMap);

        return root;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Non-Blocking Iterator with Resource Cleanup
**Problem Statement:** Design a custom `java.util.Iterator<E>` that traverses a binary tree in-order on-demand without buffering all elements into a list upfront. If the caller abandons the iteration early (e.g. `break` in loop), ensure zero resource leaks.

<details>
<summary>View Streaming In-Order Iterator Implementation</summary>

```java
package edu.se.datastructures.traversal;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Iterator;
import java.util.NoSuchElementException;

public class LazyTreeIterator<E> implements Iterator<E> {
    private final Deque<BinaryTreeNode<E>> stack = new ArrayDeque<>();

    public LazyTreeIterator(BinaryTreeNode<E> root) {
        pushLeftPath(root);
    }

    private void pushLeftPath(BinaryTreeNode<E> node) {
        while (node != null) {
            stack.push(node);
            node = node.left;
        }
    }

    @Override
    public boolean hasNext() {
        return !stack.isEmpty();
    }

    @Override
    public E next() {
        if (!hasNext()) throw new NoSuchElementException();
        BinaryTreeNode<E> curr = stack.pop();
        E val = curr.data;
        if (curr.right != null) {
            pushLeftPath(curr.right);
        }
        return val;
    }
}
```
</details>
