# Lesson 2 — Graph Traversal Engines: Depth-First (DFS), BFS & Topological Sorting

> [!NOTE]
> **Learning Outcomes:**
> - Implement **Depth-First Search (DFS)** and **Breadth-First Search (BFS)** graph traversal state machines in $O(V + E)$ time.
> - Prove why BFS guarantees the **minimal hop shortest path** in any unweighted network.
> - Reconstruct complete end-to-end paths using explicit parent pointer tracking arrays.
> - Detect cyclic deadlocks in directed graphs using the formal **Three-Coloring (WHITE/GRAY/BLACK)** algorithm.
> - Order task dependency DAGs using **Kahn's Topological Sorting Algorithm** via zero in-degree queues.

{{media:traversal-video}}

{{media:traversal-visual}}

## Executive Summary & Traversal Dynamics

In tree structures, traversals (Pre-order, In-order, Post-order, Level-order) are simplified by two structural guarantees: every node is reachable from a unique root, and there are zero cycles.

In a general **Graph**, however, two major challenges arise:
1. **Disconnected Topologies**: A graph may contain multiple isolated connected components. A traversal starting from vertex $u$ will only explore the component containing $u$.
2. **Arbitrary Cycles**: A graph can contain loops. Without a mechanism to track state, an algorithm will loop infinitely between adjacent nodes.

To traverse a graph systematically, every engine must maintain a **Visited State Set** (or boolean bitset) ensuring that every vertex is processed **exactly once**.

---

## 1. Depth-First Search (DFS): Stack Mechanics & Deep Probing

**Depth-First Search (DFS)** explores as far as possible along each branch before backtracking. It operates under a Last-In, First-Out (LIFO) discipline, implemented via recursion (using the JVM thread call stack) or an explicit `java.util.Deque`.

### 1.1 Recursive DFS Algorithm
```java
public void dfs(Graph graph, int startVertex) {
    boolean[] visited = new boolean[graph.getNumVertices()];
    dfsRecursive(graph, startVertex, visited);
}

private void dfsRecursive(Graph graph, int curr, boolean[] visited) {
    visited[curr] = true;
    processVertex(curr);

    for (Graph.Edge edge : graph.getNeighbors(curr)) {
        if (!visited[edge.to]) {
            dfsRecursive(graph, edge.to, visited);
        }
    }
}
```

### 1.2 Iterative Stack DFS Engine (Curriculum Slides 23–25)
To prevent JVM `StackOverflowError` on deep graphs, production systems use an explicit stack:
```java
public boolean isPathDfs(Graph graph, int start, int target) {
    boolean[] visited = new boolean[graph.getNumVertices()];
    Deque<Integer> stack = new ArrayDeque<>();

    stack.push(start);
    visited[start] = true;

    while (!stack.isEmpty()) {
        int curr = stack.pop();
        if (curr == target) return true; // Destination reached!

        for (Graph.Edge edge : graph.getNeighbors(curr)) {
            if (!visited[edge.to]) {
                visited[edge.to] = true;
                stack.push(edge.to);
            }
        }
    }
    return false; // Target unreachable
}
```

---

## 2. Breadth-First Search (BFS): Concentric Radial Wavefronts

**Breadth-First Search (BFS)** explores all immediate neighbors at distance $1$, then all neighbors at distance $2$, and so forth. It operates under a First-In, First-Out (FIFO) discipline using a `java.util.Queue`.

### 2.1 The Shortest Unweighted Path Guarantee
> **Theorem:** In an unweighted graph (or a graph where all edges have identical weight), BFS is guaranteed to discover the **shortest path (minimum number of edge hops)** from the source vertex to all other reachable vertices.

```java
package edu.se.datastructures.traversal;

import edu.se.datastructures.graphs.Graph;
import java.util.*;

public class BreadthFirstSearch {

    public static List<Integer> findShortestHopPath(Graph graph, int source, int destination) {
        int n = graph.getNumVertices();
        boolean[] visited = new boolean[n];
        int[] parent = new int[n];
        Arrays.fill(parent, -1);

        Queue<Integer> queue = new ArrayDeque<>();
        queue.offer(source);
        visited[source] = true;

        boolean found = false;

        while (!queue.isEmpty()) {
            int curr = queue.poll();
            if (curr == destination) {
                found = true;
                break;
            }

            for (Graph.Edge edge : graph.getNeighbors(curr)) {
                if (!visited[edge.to]) {
                    visited[edge.to] = true;
                    parent[edge.to] = curr; // Record predecessor for path reconstruction
                    queue.offer(edge.to);
                }
            }
        }

        if (!found) return Collections.emptyList();

        // Reconstruct path by walking backward from destination to source
        LinkedList<Integer> path = new LinkedList<>();
        for (int at = destination; at != -1; at = parent[at]) {
            path.addFirst(at);
        }
        return path;
    }
}
```

---

## 3. Curriculum Case Study: Austin to Washington Pathfinding (Slides 26–33)

Consider the curriculum airline flight graph connecting American cities:
```
           [ Dallas ] ─────────► [ Chicago ] ─────────► [ Washington ]
          ▲          \                                 ▲
         /            \                               /
   [ Austin ]          └───► [ Atlanta ] ────────────┘
         \
          └───► [ Denver ] ────► [ Atlanta ]
```

### Tracing Path Search:
- **DFS Trace from Austin to Washington**:
  1. Start at `Austin`. Push `Dallas`, `Denver`.
  2. Pop `Dallas`. Push `Chicago`, `Atlanta`.
  3. Pop `Chicago`. Push `Washington`.
  4. Pop `Washington` $\implies$ **Target Found!**
  - Path found by DFS: `[Austin ──► Dallas ──► Chicago ──► Washington]` (Length: 3 hops).

- **BFS Trace from Austin to Washington**:
  1. Queue: `[Austin]`.
  2. Level 1: Dequeue `Austin`, enqueue neighbors `[Dallas, Denver]`.
  3. Level 2: Dequeue `Dallas`, enqueue `Chicago, Atlanta`. Dequeue `Denver`, enqueue `Atlanta` (already visited).
  4. Level 3: Dequeue `Chicago`, enqueue `Washington`! Target reached!
  - Both reach Washington, but BFS guarantees that no 2-hop or 1-hop path exists before exploring 3-hop candidates.

---

## 4. Cycle Detection in Directed Graphs (The Three-Color Algorithm)

In an undirected graph, a cycle exists if DFS encounters an already-visited vertex that is **not the immediate parent** of the current node.

In a **Directed Graph (Digraph)**, however, encountering a visited node does NOT necessarily indicate a cycle! Consider $A \to B$ and $A \to C \to B$ (a diamond topology). Vertex $B$ is reached twice from $A$, yet the graph is completely acyclic.

### 4.1 The Three-Color Invariant
To detect cycles in digraphs with mathematical precision, we color vertices into three states:
- **WHITE (0)**: Unvisited.
- **GRAY (1)**: **Active in current recursion stack**. The algorithm is currently exploring descendants along this branch.
- **BLACK (2)**: **Finished and backtracked**. All descendants have been completely processed.

> **Theorem:** A directed graph contains a cycle if and only if DFS encounters a directed edge $(u, v)$ where vertex $v$ is currently colored **GRAY** (a **Back-Edge**).

```java
package edu.se.datastructures.traversal;

import edu.se.datastructures.graphs.Graph;

public class DirectedCycleDetector {
    private static final int WHITE = 0;
    private static final int GRAY = 1;
    private static final int BLACK = 2;

    public static boolean hasCycle(Graph graph) {
        int n = graph.getNumVertices();
        int[] color = new int[n];

        for (int i = 0; i < n; i++) {
            if (color[i] == WHITE) {
                if (dfsCheck(graph, i, color)) return true;
            }
        }
        return false;
    }

    private static boolean dfsCheck(Graph graph, int curr, int[] color) {
        color[curr] = GRAY; // Mark as active in recursion stack

        for (Graph.Edge edge : graph.getNeighbors(curr)) {
            if (color[edge.to] == GRAY) {
                return true; // BACK-EDGE DETECTED: CYCLE CONFIRMED!
            }
            if (color[edge.to] == WHITE) {
                if (dfsCheck(graph, edge.to, color)) return true;
            }
        }

        color[curr] = BLACK; // Mark as completely finished
        return false;
    }
}
```

---

## 5. Topological Sorting & Kahn's Algorithm

A **Directed Acyclic Graph (DAG)** is a directed graph containing no directed cycles.
A **Topological Sort** of a DAG is a linear ordering of its vertices such that for every directed edge $(u, v)$, vertex $u$ appears before vertex $v$ in the ordering.

### 5.1 Real-World Architectural Applications
- **Software Build Systems**: Resolving compilation order of Java packages in Gradle, Maven, and Bazel.
- **Academic Curricula**: Scheduling university courses based on prerequisite constraints (e.g., Data Structures must precede Algorithms).
- **Database Transaction Schedulers**: Determining serializable transaction commit sequences.

### 5.2 Kahn's Algorithm (In-Degree Queue Processing)
Kahn's algorithm operates on the topological axiom that **any DAG must possess at least one vertex with an in-degree of zero** (a source with no prerequisite dependencies):
1. Compute the in-degree $\text{deg}^-(v)$ for every vertex $v \in V$.
2. Initialize a queue with all vertices having $\text{deg}^-(v) == 0$.
3. While the queue is not empty:
   - Poll vertex $u$ and append it to the topological order list.
   - For each outgoing neighbor $v$ of $u$:
     - Decrement in-degree: $\text{deg}^-(v) \gets \text{deg}^-(v) - 1$.
     - If $\text{deg}^-(v) == 0$, enqueue $v$.
4. **Validation Check**: If the resulting list contains fewer than $|V|$ vertices, the graph contains a **Cycle**, making a topological ordering mathematically impossible!

```java
package edu.se.datastructures.traversal;

import edu.se.datastructures.graphs.Graph;
import java.util.*;

public class TopologicalSorter {

    public static List<Integer> sort(Graph graph) {
        int n = graph.getNumVertices();
        int[] inDegree = new int[n];

        // 1. Compute in-degrees
        for (int u = 0; u < n; u++) {
            for (Graph.Edge edge : graph.getNeighbors(u)) {
                inDegree[edge.to]++;
            }
        }

        // 2. Queue all zero in-degree vertices
        Queue<Integer> queue = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            if (inDegree[i] == 0) {
                queue.offer(i);
            }
        }

        List<Integer> order = new ArrayList<>(n);

        // 3. Process frontier
        while (!queue.isEmpty()) {
            int u = queue.poll();
            order.add(u);

            for (Graph.Edge edge : graph.getNeighbors(u)) {
                inDegree[edge.to]--;
                if (inDegree[edge.to] == 0) {
                    queue.offer(edge.to);
                }
            }
        }

        // 4. Circular dependency verification
        if (order.size() != n) {
            throw new IllegalStateException("Cyclic dependency detected! Graph is not a DAG.");
        }

        return order;
    }
}
```

---

## 6. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Consider a software build system with 5 modules: `Core (0)`, `Utils (1)`, `Database (2)`, `Auth (3)`, `API (4)`.
Dependencies (Directed Edges $u \to v$ means $u$ must be built before $v$):
- `0 -> 1`, `0 -> 2`, `1 -> 3`, `2 -> 3`, `3 -> 4`.
1. Compute the initial in-degree of all 5 modules.
2. Trace the step-by-step state of Kahn's algorithm queue and output list.
3. Is the resulting topological order unique? Explain why or why not.

<details>
<summary>View Level 1 Trace & Uniqueness Analysis</summary>

1. **Initial In-Degrees**:
   - `Core (0)`: $0$ (No incoming edges)
   - `Utils (1)`: $1$ (From 0)
   - `Database (2)`: $1$ (From 0)
   - `Auth (3)`: $2$ (From 1 and 2)
   - `API (4)`: $1$ (From 3)

2. **Step-by-Step Kahn Execution**:
   - **Init**: Queue = `[0]`, Order = `[]`.
   - **Step 1**: Poll `0`. Order = `[0]`. Decrement neighbors `1` (in-degree $\to 0$) and `2` (in-degree $\to 0$).
     Queue = `[1, 2]`.
   - **Step 2**: Poll `1`. Order = `[0, 1]`. Decrement neighbor `3` (in-degree $2 \to 1$).
     Queue = `[2]`.
   - **Step 3**: Poll `2`. Order = `[0, 1, 2]`. Decrement neighbor `3` (in-degree $1 \to 0 \implies$ Enqueue 3).
     Queue = `[3]`.
   - **Step 4**: Poll `3`. Order = `[0, 1, 2, 3]`. Decrement neighbor `4` (in-degree $1 \to 0 \implies$ Enqueue 4).
     Queue = `[4]`.
   - **Step 5**: Poll `4`. Order = `[0, 1, 2, 3, 4]`.
   - **Final Topological Order**: `[0, 1, 2, 3, 4]`.

3. **Uniqueness Analysis**:
   The order is **NOT unique**! At Step 1, both module 1 and module 2 reached an in-degree of 0 simultaneously. Processing module 2 before module 1 yields another equally valid topological ordering: `[0, 2, 1, 3, 4]`.
</details>

---

### Level 2: Scaffolded System Refactoring — Bipartite Graph Validator
**Problem Statement:** In a distributed cluster, tasks must be divided into two independent sets such that no two tasks in the same set communicate with each other (a **Bipartite Graph**). Implement an $O(V + E)$ BFS coloring algorithm that determines whether a given graph is bipartite (2-colorable).

<details>
<summary>View Complete Java Bipartite Validator Implementation</summary>

```java
package edu.se.datastructures.traversal;

import edu.se.datastructures.graphs.Graph;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Queue;

public class BipartiteValidator {

    public static boolean isBipartite(Graph graph) {
        int n = graph.getNumVertices();
        int[] colors = new int[n];
        Arrays.fill(colors, -1); // -1: uncolored, 0: Color A, 1: Color B

        for (int i = 0; i < n; i++) {
            if (colors[i] == -1) {
                if (!bfsColor(graph, i, colors)) return false;
            }
        }
        return true;
    }

    private static boolean bfsColor(Graph graph, int start, int[] colors) {
        Queue<Integer> queue = new ArrayDeque<>();
        queue.offer(start);
        colors[start] = 0;

        while (!queue.isEmpty()) {
            int curr = queue.poll();

            for (Graph.Edge edge : graph.getNeighbors(curr)) {
                if (colors[edge.to] == -1) {
                    // Assign alternate color (0 -> 1 or 1 -> 0)
                    colors[edge.to] = 1 - colors[curr];
                    queue.offer(edge.to);
                } else if (colors[edge.to] == colors[curr]) {
                    // Neighbor shares identical color: ODD CYCLE DETECTED!
                    return false;
                }
            }
        }
        return true;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Asynchronous Dependency DAG Executor
**Problem Statement:** Design a concurrent execution engine for a directed acyclic graph of tasks. Multiple tasks whose dependencies have been satisfied must execute concurrently on a `java.util.concurrent.ExecutorService`. Once a task completes, it decrements the dependency counters of its downstream dependents and triggers their immediate parallel execution.

<details>
<summary>View Complete Java Concurrent DAG Task Engine</summary>

```java
package edu.se.datastructures.traversal;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ConcurrentDagExecutor {
    private final ExecutorService threadPool;

    public ConcurrentDagExecutor(int threads) {
        this.threadPool = Executors.newFixedThreadPool(threads);
    }

    public static class Task {
        public final int id;
        public final Runnable action;
        public final List<Task> dependents = new ArrayList<>();
        public final AtomicInteger pendingPrerequisites = new AtomicInteger(0);

        public Task(int id, Runnable action) {
            this.id = id;
            this.action = action;
        }

        public void addDependent(Task dependent) {
            dependents.add(dependent);
            dependent.pendingPrerequisites.incrementAndGet();
        }
    }

    public void executeDag(List<Task> allTasks, Runnable onComplete) {
        AtomicInteger remainingTasks = new AtomicInteger(allTasks.size());

        for (Task task : allTasks) {
            if (task.pendingPrerequisites.get() == 0) {
                dispatch(task, remainingTasks, onComplete);
            }
        }
    }

    private void dispatch(Task task, AtomicInteger remainingTasks, Runnable onComplete) {
        threadPool.submit(() -> {
            try {
                task.action.run(); // Execute task logic
            } finally {
                for (Task dep : task.dependents) {
                    if (dep.pendingPrerequisites.decrementAndGet() == 0) {
                        dispatch(dep, remainingTasks, onComplete);
                    }
                }
                if (remainingTasks.decrementAndGet() == 0) {
                    onComplete.run();
                }
            }
        });
    }
}
```
</details>
