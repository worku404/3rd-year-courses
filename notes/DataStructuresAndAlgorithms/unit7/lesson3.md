# Lesson 3 — Shortest Path Routing & Minimum Spanning Forests (Dijkstra, Prim & Kruskal)

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the **Single-Source Shortest Path (SSSP)** problem and formalize the **Edge Relaxation Invariant**.
> - Implement **Dijkstra's Greedy Shortest Path Algorithm** using Min-Priority Queues in $O((V + E) \log V)$ time.
> - Explain why negative edge weights cause Dijkstra's greedy invariant to fail catastrophically.
> - Prove the **Cut Property** governing **Minimum Spanning Trees (MST)**.
> - Contrast **Prim's vertex-growing algorithm** against **Kruskal's edge-sorting engine** powered by **Disjoint-Set Union-Find (DSU)** with Path Compression and Union by Rank.

{{media:routing-video}}

{{media:routing-visual}}

## Executive Summary & Network Routing Context

In unweighted networks, Breadth-First Search (BFS) easily finds the shortest path because each edge represents an identical unit cost. However, real-world systems—Internet backbone packet routers (OSPF, BGP), electrical power transmission grids, and GPS navigation systems (Google Maps)—operate over **Weighted Graphs** where edge values quantify physical distance, monetary cost, electrical resistance, or latency.

This lesson examines the two most important optimization problems in graph theory:
1. **Single-Source Shortest Paths (SSSP)**: Finding the path with the minimum cumulative edge weight from a source vertex to every other node in the network (**Dijkstra's Algorithm**).
2. **Minimum Spanning Tree (MST)**: Connecting all vertices together with the absolute minimum total edge weight without introducing cycles (**Prim's & Kruskal's Algorithms**).

---

## 1. Single-Source Shortest Paths & Edge Relaxation

Let $G = (V, E, w)$ be a weighted directed graph where each edge $e = (u, v)$ has a non-negative weight $w(u, v) \ge 0$. The weight of a path $P = (v_0, v_1, \dots, v_k)$ is the sum of its constituent edge weights:
$$w(P) = \sum_{i=1}^k w(v_{i-1}, v_i)$$
The shortest path distance $\delta(s, v)$ is the minimum weight over all valid paths from source $s$ to target $v$.

### 1.1 The Edge Relaxation Invariant
Shortest path algorithms maintain an array `dist[]` of provisional upper-bound estimates:
$$\text{dist}[v] \ge \delta(s, v)$$
The fundamental atomic operation is **Edge Relaxation**: testing whether passing through vertex $u$ improves the current shortest path to neighbor $v$:

```java
if (dist[u] + weight(u, v) < dist[v]) {
    dist[v] = dist[u] + weight(u, v); // Relax upper bound
    parent[v] = u;                     // Update shortest-path tree predecessor
    priorityQueue.decreaseKey(v, dist[v]);
}
```

---

## 2. Dijkstra's Algorithm: Greedy Min-Priority Queue Engine

In 1959, Edsger W. Dijkstra published the greedy algorithm for SSSP.

### 2.1 The Greedy Choice Property
Dijkstra maintains two sets of vertices:
1. **Settled Set $S$**: Vertices whose exact shortest-path distance from the source is finalized.
2. **Unsettled Frontier $Q$**: Vertices whose shortest path is still provisional, managed via a **Min-Priority Queue**.

At each iteration, Dijkstra extracts the vertex $u \in Q$ possessing the **smallest provisional distance** $\text{dist}[u]$. Because all edge weights are non-negative ($w \ge 0$), no future path passing through other unsettled vertices can ever improve $\text{dist}[u]$! Thus, $u$ is permanently settled, and all its outgoing edges are relaxed.

```
       Dijkstra Execution State:
       ┌────────────────────────┐      Relax edges (u -> v)
       │  Settled Set S         │    ────────────────────────►  [ Unsettled Frontier Q ]
       │  dist[u] is FINALIZED  │                                (Min-Priority Queue)
       └────────────────────────┘                                Extracts min dist[u]!
```

### 2.2 Production Java Implementation: Dijkstra's Algorithm
```java
package edu.se.datastructures.routing;

import edu.se.datastructures.graphs.Graph;
import java.util.*;

public class DijkstraRouter {

    public static class PathResult {
        public final double[] distances;
        public final int[] predecessors;

        public PathResult(double[] distances, int[] predecessors) {
            this.distances = distances;
            this.predecessors = predecessors;
        }

        public List<Integer> reconstructPath(int target) {
            if (distances[target] == Double.POSITIVE_INFINITY) {
                return Collections.emptyList();
            }
            LinkedList<Integer> path = new LinkedList<>();
            for (int at = target; at != -1; at = predecessors[at]) {
                path.addFirst(at);
            }
            return path;
        }
    }

    private static class NodeRecord implements Comparable<NodeRecord> {
        final int vertex;
        final double dist;

        NodeRecord(int vertex, double dist) {
            this.vertex = vertex;
            this.dist = dist;
        }

        @Override
        public int compareTo(NodeRecord other) {
            return Double.compare(this.dist, other.dist);
        }
    }

    public static PathResult computeShortestPaths(Graph graph, int source) {
        int n = graph.getNumVertices();
        double[] dist = new double[n];
        int[] parent = new int[n];
        Arrays.fill(dist, Double.POSITIVE_INFINITY);
        Arrays.fill(parent, -1);

        PriorityQueue<NodeRecord> pq = new PriorityQueue<>();

        dist[source] = 0.0;
        pq.offer(new NodeRecord(source, 0.0));

        while (!pq.isEmpty()) {
            NodeRecord curr = pq.poll();
            int u = curr.vertex;

            // Stale entry guard: skip if we've already found a shorter path to u
            if (curr.dist > dist[u]) continue;

            for (Graph.Edge edge : graph.getNeighbors(u)) {
                int v = edge.to;
                double newDist = dist[u] + edge.weight;

                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    parent[v] = u;
                    pq.offer(new NodeRecord(v, newDist)); // Offer relaxed candidate
                }
            }
        }

        return new PathResult(dist, parent);
    }
}
```

### 2.3 Computational Complexity Analysis
- Each vertex is extracted from the Priority Queue once: $V \times O(\log V)$.
- Each edge is relaxed at most once: $E \times O(\log V)$ (inserting relaxed keys).
- **Total Time Complexity**: $\mathbf{O((V + E) \log V)}$ with standard Binary Min-Heap.
- *(Theoretical optimum: $O(E + V \log V)$ using a Fibonacci Heap with $O(1)$ amortized `decreaseKey`).*

---

## 3. The Fatal Negative Edge Weight Constraint

> [!WARNING]
> **Dijkstra Fails on Graphs with Negative Edge Weights!**
> Dijkstra's greedy invariant relies on the assumption that adding an edge to a path **can only increase (or maintain) its total length**. If an edge $(u, v)$ has weight $-10$, a path passing through $u$ could become shorter than an already settled node!
> Furthermore, if a graph contains a **Negative Weight Cycle**, traversing the cycle repeatedly decreases the path cost to $-\infty$, rendering the shortest path undefined.

```
       (S) ─── 2 ───► (A) ─── (-5) ───► (B)
        │                                 ▲
        └─────────────── 4 ───────────────┘
```
1. Dijkstra settles $A$ at distance $2$ and $B$ at distance $4$.
2. It greedily declares distance to $B$ is $4$.
3. But passing through $A \to B$ yields cost $2 + (-5) = -3 < 4$! Dijkstra misses this because $B$ was already settled!
*(For graphs with negative weights, engineers must use the **Bellman-Ford Algorithm** running in $O(V \cdot E)$ time).*

---

## 4. Minimum Spanning Trees (MST) & The Cut Property

Given a connected, undirected graph $G = (V, E)$ with edge weights, a **Spanning Tree** is a subgraph $T = (V, E_T)$ that connects all $|V|$ vertices with no cycles (meaning $|E_T| = |V| - 1$).
A **Minimum Spanning Tree (MST)** is a spanning tree whose cumulative edge weight is minimal:
$$\text{Cost}(T) = \sum_{e \in E_T} w(e) \quad \text{is minimized.}$$

### 4.1 The Fundamental Cut Property
> **The Cut Property Theorem:** Let $(S, V \setminus S)$ be any partition (cut) of the vertices of $G$. If an edge $e = (u, v)$ is the **strictly lightest edge crossing the cut** (with $u \in S$ and $v \in V \setminus S$), then $e$ **must belong to every Minimum Spanning Tree** of $G$.

Both Prim's and Kruskal's algorithms are greedy realizations of the Cut Property:
- **Prim's Algorithm**: Grows a single tree cut $S$ vertex-by-vertex.
- **Kruskal's Algorithm**: Maintains a forest of components, repeatedly adding the globally lightest edge that does not form a cycle.

---

## 5. Prim's Algorithm vs. Kruskal's Algorithm

| Algorithmic Dimension | Prim's Algorithm | Kruskal's Algorithm |
| :--- | :--- | :--- |
| **Strategy** | Vertex-centric growing cut | Global edge-centric greedy selection |
| **Data Structure** | Min-Priority Queue / Min-Heap | Disjoint-Set Union-Find (DSU) + Edge Sorting |
| **Intermediate State** | Always maintains a single connected tree | Maintains a disconnected forest until final edge |
| **Time Complexity** | $O(E \log V)$ with Binary Heap | $O(E \log E) = O(E \log V)$ (dominated by edge sort) |
| **Optimal Use Case** | **Dense Graphs** ($E \approx V^2$) | **Sparse Graphs** ($E \ll V^2$) |

---

## 6. Kruskal's Algorithm & The Disjoint-Set Union-Find (DSU)

Kruskal's algorithm requires a lightning-fast mechanism to determine whether adding an edge $(u, v)$ would introduce a cycle. This is solved by the **Disjoint-Set Union-Find (DSU)** data structure.

### 6.1 The Two DSU Optimizations
1. **Path Compression**: During `find(u)`, every traversed node connects directly to the root of the component tree, flattening the tree depth to $\approx 1$.
2. **Union by Rank**: During `union(u, v)`, the shallower tree is attached beneath the root of the deeper tree, preventing pathological path lengthening.

> **Ackermann Theorem:** With Path Compression and Union by Rank, any sequence of $m$ DSU operations on $n$ elements executes in strictly $\mathbf{O(m \cdot \alpha(n))}$ time, where $\alpha$ is the Inverse Ackermann function ($\alpha(n) \le 4$ for all $n < 10^{80}$, effectively **$O(1)$ constant time**).

```java
package edu.se.datastructures.routing;

import java.util.*;

public class KruskalMstEngine {

    public static class DisjointSet {
        private final int[] parent;
        private final int[] rank;

        public DisjointSet(int size) {
            parent = new int[size];
            rank = new int[size];
            for (int i = 0; i < size; i++) parent[i] = i;
        }

        // Find with Path Compression
        public int find(int i) {
            if (parent[i] != i) {
                parent[i] = find(parent[i]); // Path compression
            }
            return parent[i];
        }

        // Union by Rank
        public boolean union(int i, int j) {
            int rootI = find(i);
            int rootJ = find(j);
            if (rootI == rootJ) return false; // Cycle detected!

            if (rank[rootI] < rank[rootJ]) {
                parent[rootI] = rootJ;
            } else if (rank[rootI] > rank[rootJ]) {
                parent[rootJ] = rootI;
            } else {
                parent[rootJ] = rootI;
                rank[rootI]++;
            }
            return true;
        }
    }

    public static class EdgeRecord implements Comparable<EdgeRecord> {
        public final int u, v;
        public final double weight;

        public EdgeRecord(int u, int v, double weight) {
            this.u = u;
            this.v = v;
            this.weight = weight;
        }

        @Override
        public int compareTo(EdgeRecord other) {
            return Double.compare(this.weight, other.weight);
        }
    }

    public static List<EdgeRecord> computeMst(int numVertices, List<EdgeRecord> edges) {
        // 1. Sort all edges in ascending order of weight: O(E log E)
        Collections.sort(edges);

        DisjointSet dsu = new DisjointSet(numVertices);
        List<EdgeRecord> mst = new ArrayList<>(numVertices - 1);

        // 2. Greedily pick lightest non-cyclic edges
        for (EdgeRecord edge : edges) {
            if (dsu.union(edge.u, edge.v)) {
                mst.add(edge);
                if (mst.size() == numVertices - 1) break; // MST complete!
            }
        }

        return mst;
    }
}
```

---

## 7. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Consider a regional fiber-optic network connecting 4 data centers: `A (0)`, `B (1)`, `C (2)`, `D (3)`.
Weighted edges:
- `(0, 1): 1`, `(0, 2): 4`, `(1, 2): 2`, `(1, 3): 5`, `(2, 3): 3`.
1. Trace Dijkstra's algorithm starting from source `A (0)`. Show the distance array and settled order.
2. Trace Kruskal's algorithm to construct the Minimum Spanning Tree. List each edge accepted or rejected.
3. Compare the total shortest path cost from `A` to `D` versus the total weight of the MST.

<details>
<summary>View Level 1 Trace & Comparison Table</summary>

1. **Dijkstra Trace from Source 0 (A)**:
   - Init: `dist = [0, inf, inf, inf]`. Settle `0`.
   - Relax from 0: `dist[1] = 1`, `dist[2] = 4`.
   - Smallest unsettled: Settle `1` (dist=1).
   - Relax from 1:
     - `1 -> 2`: $1 + 2 = 3 < 4 \implies dist[2] = 3$.
     - `1 -> 3`: $1 + 5 = 6 < \inf \implies dist[3] = 6$.
   - Smallest unsettled: Settle `2` (dist=3).
   - Relax from 2:
     - `2 -> 3`: $3 + 3 = 6$ (tie, dist remains 6).
   - Settle `3` (dist=6).
   - **Shortest Paths from A**: `A->A: 0`, `A->B: 1`, `A->C: 3`, `A->D: 6`.
   - **Path to D**: `[0 ──► 1 ──► 2 ──► 3]` (Cost = 6).

2. **Kruskal MST Trace**:
   - Sorted Edges:
     1. `(0, 1)` wt 1: `find(0) != find(1)` $\implies$ **ACCEPT (0, 1)**
     2. `(1, 2)` wt 2: `find(1) != find(2)` $\implies$ **ACCEPT (1, 2)**
     3. `(2, 3)` wt 3: `find(2) != find(3)` $\implies$ **ACCEPT (2, 3)**
     - $V - 1 = 3$ edges accepted! Algorithm terminates.
   - MST Edges: `{(0, 1), (1, 2), (2, 3)}`.
   - **Total MST Weight**: $1 + 2 + 3 = \mathbf{6}$.

3. **Comparison**:
   In this network, the shortest path from `A` to `D` coincides with the MST backbone path, both yielding a cost of 6.
</details>

---

### Level 2: Scaffolded System Refactoring — Multi-Criteria Network Router
**Problem Statement:** In an enterprise VoIP network, paths must optimize for latency, but links with packet loss exceeding $2.0\%$ are unacceptable. Extend Dijkstra's algorithm to compute the shortest latency path while filtering out lossy links.

<details>
<summary>View Complete Java Constrained Dijkstra Implementation</summary>

```java
package edu.se.datastructures.routing;

import java.util.*;

public class ConstrainedVoipRouter {

    public static class VoipEdge {
        public final int to;
        public final double latencyMs;
        public final double packetLossPct;

        public VoipEdge(int to, double latencyMs, double packetLossPct) {
            this.to = to;
            this.latencyMs = latencyMs;
            this.packetLossPct = packetLossPct;
        }
    }

    public static double[] findShortestSafeLatency(List<VoipEdge>[] graph, int source, double maxLossThreshold) {
        int n = graph.length;
        double[] dist = new double[n];
        Arrays.fill(dist, Double.POSITIVE_INFINITY);

        PriorityQueue<double[]> pq = new PriorityQueue<>(Comparator.comparingDouble(a -> a[1]));
        dist[source] = 0.0;
        pq.offer(new double[]{source, 0.0});

        while (!pq.isEmpty()) {
            double[] top = pq.poll();
            int u = (int) top[0];
            double d = top[1];

            if (d > dist[u]) continue;

            for (VoipEdge edge : graph[u]) {
                // Constrained filter: reject lossy links
                if (edge.packetLossPct > maxLossThreshold) continue;

                double nextLatency = dist[u] + edge.latencyMs;
                if (nextLatency < dist[edge.to]) {
                    dist[edge.to] = nextLatency;
                    pq.offer(new double[]{edge.to, nextLatency});
                }
            }
        }

        return dist;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Distributed Electrical Grid Spanning Engine
**Problem Statement:** Design a resilient electrical power grid spanning engine that computes a Minimum Spanning Tree across $N$ electrical substations. If any single transmission line in the MST fails, implement an online routine to identify the lightest replacement edge crossing the severed cut in $O(E)$ time without re-running Kruskal from scratch.

<details>
<summary>View Resilient MST Edge Replacement Engine</summary>

```java
package edu.se.datastructures.routing;

import java.util.*;

public class ResilientGridSpanningEngine {

    public static KruskalMstEngine.EdgeRecord findReplacementEdge(
            int numVertices,
            List<KruskalMstEngine.EdgeRecord> originalMst,
            List<KruskalMstEngine.EdgeRecord> allGridEdges,
            KruskalMstEngine.EdgeRecord severedEdge) {

        // 1. Rebuild the graph of the MST excluding the severed edge
        List<Integer>[] mstAdj = new ArrayList[numVertices];
        for (int i = 0; i < numVertices; i++) mstAdj[i] = new ArrayList<>();

        for (KruskalMstEngine.EdgeRecord e : originalMst) {
            if (e.equals(severedEdge)) continue; // Sever edge
            mstAdj[e.u].add(e.v);
            mstAdj[e.v].add(e.u);
        }

        // 2. Identify the cut: find all vertices in severedEdge.u's partition via BFS
        boolean[] inPartitionS = new boolean[numVertices];
        Queue<Integer> q = new ArrayDeque<>();
        q.offer(severedEdge.u);
        inPartitionS[severedEdge.u] = true;

        while (!q.isEmpty()) {
            int curr = q.poll();
            for (int neighbor : mstAdj[curr]) {
                if (!inPartitionS[neighbor]) {
                    inPartitionS[neighbor] = true;
                    q.offer(neighbor);
                }
            }
        }

        // 3. Scan all candidate grid edges crossing the cut: u in S and v not in S
        KruskalMstEngine.EdgeRecord bestReplacement = null;

        for (KruskalMstEngine.EdgeRecord e : allGridEdges) {
            if (e.equals(severedEdge)) continue;

            boolean uInS = inPartitionS[e.u];
            boolean vInS = inPartitionS[e.v];

            // Edge crosses the cut!
            if (uInS != vInS) {
                if (bestReplacement == null || e.weight < bestReplacement.weight) {
                    bestReplacement = e;
                }
            }
        }

        return bestReplacement; // Lightest replacement edge restoring network connectivity!
    }
}
```
</details>
