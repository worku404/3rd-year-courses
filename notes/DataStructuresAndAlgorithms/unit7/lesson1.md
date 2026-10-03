# Lesson 1 — Graph Topologies, Invariant Axioms & Storage Architectures

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the formal mathematical graph axioms: $G = (V, E)$, **Undirected Graphs** vs. **Directed Digraphs**.
> - Prove **Euler's Handshaking Lemma** ($\sum \text{deg}(v) = 2|E|$) and calculate maximum edge densities for complete topologies.
> - Contrast the memory layouts, spatial footprints, and algorithmic complexities of **Adjacency Matrices** ($O(V^2)$) vs. **Adjacency Lists** ($O(V + E)$).
> - Analyze cache-line locality and memory bandwidth trade-offs in sparse versus dense graph implementations.
> - Engineer a production-grade generic `Graph` system in modern Java.

{{media:graph-video}}

{{media:graph-visual}}

## Executive Summary & Non-Linear Structural Context

In previous units, we examined linear collections (Arrays, Stacks, Queues, Lists) where each element has a single predecessor and successor, followed by **Tree Structures** where elements diverge hierarchically in a strict parent-child relationship with a single root and zero cycles.

However, real-world systems rarely adhere to strict hierarchical topologies. Consider:
- **Global Civil Aviation**: Flight networks between airports (e.g., Ethiopian Airlines hubs connecting Addis Ababa, Nairobi, Dubai, London, and Washington) where routes intersect arbitrarily and cycles are ubiquitous.
- **Internet Infrastructure**: Autonomous Systems (AS) and packet routers interconnected across redundant fiber rings.
- **Microservices & Web Graphs**: Distributed service meshes communicating via asynchronous RPC endpoints.

A **Graph** is the most generic non-linear data structure in computer science. It consists of a set of entities called **Vertices (Nodes)** and a collection of relationships called **Edges (Arcs)** that bridge pairs of vertices without topological restrictions.

---

## 1. Mathematical Graph Foundations & Formal Axioms

A graph $G$ is formally specified as an ordered pair:
$$G = (V, E)$$
Where:
- $V(G)$ is a finite, non-empty set of **Vertices** (or nodes): $V = \{v_1, v_2, \dots, v_n\}$. The cardinality $|V|$ denotes the number of vertices.
- $E(G)$ is a set of **Edges** (or links): $E = \{e_1, e_2, \dots, e_m\}$. Each edge $e \in E$ establishes a relationship between two vertices $u, v \in V$.

### 1.1 Undirected vs. Directed Graphs (Digraphs)

| Topological Attribute | Undirected Graph | Directed Graph (Digraph) |
| :--- | :--- | :--- |
| **Edge Specification** | Unordered pair: $e = \{u, v\} = \{v, u\}$ | Ordered pair: $e = (u, v) \ne (v, u)$ ($u \to v$) |
| **Traversal Direction** | Bidirectional traversal: $u \leftrightarrow v$ | Unidirectional: flow from source $u$ to target $v$ |
| **Degree Metric** | Single degree $\text{deg}(v)$ = connected edges | Split: **In-Degree** $\text{deg}^-(v)$ and **Out-Degree** $\text{deg}^+(v)$ |
| **Real-World Parallel** | Mutual Facebook Friendship, Two-Way Roads | Twitter/X Follower model, Web Page Hyperlinks |

```
    UNDIRECTED GRAPH:                         DIRECTED DIGRAPH:
       (1) ───────── (2)                         (1) ────────► (2)
        │             │                           ▲             │
        │             │                           │             ▼
       (3) ───────── (4)                         (3) ◄──────── (4)
    Edge: {1, 2} == {2, 1}                    Edge: (1, 2) is distinct from (2, 1)
```

### 1.2 Graph Terminology
1. **Adjacency**: Two vertices $u$ and $v$ are **adjacent** if an edge $(u, v) \in E$ directly connects them.
   - In digraphs, $v$ is adjacent *from* $u$, and $u$ is adjacent *to* $v$.
2. **Incident**: An edge is **incident** to the vertices it connects.
3. **Path**: A sequence of vertices $(v_0, v_1, \dots, v_k)$ such that each consecutive pair $(v_i, v_{i+1}) \in E$.
4. **Simple Path**: A path in which all vertices are pairwise distinct.
5. **Cycle**: A path of length $\ge 3$ (or length $\ge 1$ in digraphs) that begins and ends at the identical vertex ($v_0 = v_k$).
6. **Weighted Graph**: A graph where each edge carries a numerical attribute $w(u, v) \in \mathbb{R}$ representing distance, latency, toll cost, or bandwidth capacity.

---

## 2. Structural Invariants & Mathematical Bounds

### 2.1 Euler's Handshaking Lemma
> **Theorem:** In any undirected graph $G = (V, E)$, the sum of degrees of all vertices strictly equals twice the total number of edges:
> $$\sum_{v \in V} \text{deg}(v) = 2 |E|$$

**Proof:** Every undirected edge $e = \{u, v\}$ has two distinct endpoints. When we sum the degrees across all vertices, each edge is counted exactly twice—once at endpoint $u$, and once at endpoint $v$. $\mathbf{Q.E.D.}$

> **Corollary:** In any undirected graph, the number of vertices with an **odd degree** is always **even**.
> *(If the number of odd-degree vertices were odd, the total sum of degrees would be an odd number, contradicting the theorem that the sum equals $2|E|$ which is strictly even).*

### 2.2 Complete Graph Edge Densities
A **Complete Graph** $K_n$ is a topology where every single vertex is directly connected by an edge to every other vertex.
- **Undirected Complete Graph**:
  Each of the $N$ vertices connects to $N - 1$ other vertices. By the Handshaking Lemma:
  $$|E|_{\max} = \frac{N(N - 1)}{2} = \Theta(N^2)$$
- **Directed Complete Digraph**:
  Every vertex possesses directed edges to all other $N - 1$ vertices:
  $$|E|_{\max} = N(N - 1) = \Theta(N^2)$$

### 2.3 Sparse vs. Dense Graphs
- **Sparse Graph**: $|E| \ll |V|^2$. Typically, $|E| \approx O(|V|)$ (e.g., planar road maps, computer communication networks).
- **Dense Graph**: $|E| \approx \Theta(|V|^2)$. The number of edges approaches the maximum complete limit.

---

## 3. Storage Architecture 1: The Adjacency Matrix

An **Adjacency Matrix** represents a graph with $|V| = n$ vertices using an $n \times n$ two-dimensional array $A$:
$$A[i][j] = \begin{cases} 1 \quad (\text{or } w(i, j)), & \text{if } (v_i, v_j) \in E \\ 0 \quad (\text{or } \infty), & \text{otherwise} \end{cases}$$

```
    GRAPH:               ADJACENCY MATRIX (4 x 4):
      (0) ─── (1)             0   1   2   3
       │       │         0 [  0,  1,  1,  0  ]
       │       │         1 [  1,  0,  0,  1  ]
      (2) ─── (3)         2 [  1,  0,  0,  1  ]
                         3 [  0,  1,  1,  0  ]
```

### 3.1 Architectural Properties of the Adjacency Matrix
1. **Symmetry in Undirected Graphs**: The matrix is symmetric along its main diagonal ($A[i][j] == A[j][i]$).
2. **Instantaneous Edge Verification**: Checking whether edge $(u, v)$ exists is an instantaneous $O(1)$ memory lookup: `return matrix[u][v] != 0`.
3. **Space Inefficiency on Sparse Topologies**:
   - The matrix always allocates $V^2$ slots regardless of edge count.
   - For an airline routing system with $|V| = 5,000$ airports and $|E| = 40,000$ flights:
     - Matrix size: $5,000 \times 5,000 = 25,000,000$ integer cells ($100 \text{ MB}$).
     - Only $40,000$ cells ($0.16\%$) contain data! **$99.84\%$ of memory is wasted on zeros.**
4. **Neighbor Enumeration Overhead**: Finding all neighbors of vertex $u$ requires scanning the entire row of length $V$, yielding $O(V)$ time even if $u$ has only 1 neighbor.

---

## 4. Storage Architecture 2: The Adjacency List

An **Adjacency List** represents a graph using an array of dynamic lists or vectors. For each vertex $i \in V$, `adj[i]` stores a list of all vertices $j$ such that $(i, j) \in E$.

```
    GRAPH:               ADJACENCY LIST:
      (0) ─── (1)         [0] ──► [1] ──► [2] ──► null
       │       │          [1] ──► [0] ──► [3] ──► null
       │       │          [2] ──► [0] ──► [3] ──► null
      (2) ─── (3)         [3] ──► [1] ──► [2] ──► null
```

### 4.1 Architectural Properties of the Adjacency List
1. **Optimal Memory Footprint**:
   - Total space is strictly $\mathbf{O(|V| + |E|)}$:
     - Undirected: $V$ list heads $+ 2|E|$ node elements.
     - Directed: $V$ list heads $+ |E|$ node elements.
   - For our $5,000$ airport and $40,000$ flight network:
     - Storage requires only $5,000 + 80,000 = 85,000$ pointers ($\approx 680 \text{ KB}$), achieving a **$>99\%$ memory reduction** compared to the matrix!
2. **Optimal Neighbor Enumeration**:
   - Iterating over all neighbors of vertex $u$ takes strictly $\mathbf{O(\text{deg}(u))}$ time.
3. **Edge Verification Trade-Off**:
   - Checking whether edge $(u, v)$ exists requires traversing `adj[u]`, taking $O(\text{deg}(u))$ time (reduced to $O(1)$ expected if `adj[u]` is implemented as a `HashSet<Integer>`).

---

## 5. Comparative Architectural Decision Matrix

| Metric / Operation | Adjacency Matrix | Adjacency List | Adjacency Hash Table |
| :--- | :--- | :--- | :--- |
| **Auxiliary Memory** | $O(V^2)$ [Massive waste if sparse] | $O(V + E)$ [Optimal for sparse] | $O(V + E)$ [Slight pointer overhead] |
| **Add Vertex** | $O(V^2)$ [Requires 2D reallocation] | $O(1)$ amortized [Append to array] | $O(1)$ amortized |
| **Add Edge $(u, v)$** | $O(1)$ | $O(1)$ [Push to front/back] | $O(1)$ expected |
| **Remove Edge $(u, v)$** | $O(1)$ | $O(\text{deg}(u))$ list search | $O(1)$ expected |
| **Query Edge $(u, v)$** | $O(1)$ [Direct index access] | $O(\text{deg}(u))$ list search | $O(1)$ expected |
| **Find All Neighbors** | $O(V)$ [Scan entire row] | $O(\text{deg}(u))$ [Strictly optimal] | $O(\text{deg}(u))$ |
| **Cache Locality** | High (contiguous row buffer) | Moderate (pointer dereferences) | Low (scattered hash nodes) |

---

## 6. High-Throughput Production Java Implementation

```java
package edu.se.datastructures.graphs;

import java.util.*;

public interface Graph {
    int getNumVertices();
    int getNumEdges();
    void addEdge(int u, int v, double weight);
    boolean hasEdge(int u, int v);
    List<Edge> getNeighbors(int u);

    class Edge {
        public final int to;
        public final double weight;

        public Edge(int to, double weight) {
            this.to = to;
            this.weight = weight;
        }
    }
}
```

### 6.1 Adjacency List Graph Engine
```java
package edu.se.datastructures.graphs;

import java.util.*;

public class AdjacencyListGraph implements Graph {
    private final int numVertices;
    private int numEdges;
    private final List<Edge>[] adj;

    @SuppressWarnings("unchecked")
    public AdjacencyListGraph(int numVertices) {
        this.numVertices = numVertices;
        this.numEdges = 0;
        this.adj = new ArrayList[numVertices];
        for (int i = 0; i < numVertices; i++) {
            this.adj[i] = new ArrayList<>();
        }
    }

    @Override
    public int getNumVertices() { return numVertices; }

    @Override
    public int getNumEdges() { return numEdges; }

    @Override
    public void addEdge(int u, int v, double weight) {
        adj[u].add(new Edge(v, weight));
        numEdges++;
    }

    @Override
    public boolean hasEdge(int u, int v) {
        for (Edge e : adj[u]) {
            if (e.to == v) return true;
        }
        return false;
    }

    @Override
    public List<Edge> getNeighbors(int u) {
        return Collections.unmodifiableList(adj[u]);
    }
}
```

---

## 7. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
An enterprise telecommunications network models fiber-optic connections across $N = 10,000$ regional routing towers. The network is sparse, containing exactly $|E| = 50,000$ bidirectional links.
1. What is the sum of degrees across all towers in the network?
2. How many bytes of RAM are consumed by an Adjacency Matrix representation (assuming 4-byte integers for weights)?
3. How many bytes of RAM are consumed by an Adjacency List representation (assuming an 8-byte pointer per list head and 16 bytes per edge object: 4-byte target, 8-byte double weight, 4-byte padding)?
4. What is the exact percentage memory savings achieved by the Adjacency List?

<details>
<summary>View Level 1 Memory Calculation Trace</summary>

1. **Sum of Degrees**:
   By Euler's Handshaking Lemma:
   $$\sum \text{deg}(v) = 2 |E| = 2 \times 50,000 = \mathbf{100,000}$$

2. **Adjacency Matrix RAM Consumption**:
   $V \times V = 10,000 \times 10,000 = 100,000,000$ cells.
   $100,000,000 \times 4 \text{ bytes} = 400,000,000 \text{ bytes} \approx \mathbf{381.47 \text{ MB}}$.

3. **Adjacency List RAM Consumption**:
   - List heads array: $10,000 \times 8 \text{ bytes} = 80,000 \text{ bytes}$.
   - Edge objects (bidirectional $\implies 2 |E| = 100,000$ directed edge records):
     $100,000 \times 16 \text{ bytes} = 1,600,000 \text{ bytes}$.
   - Total memory: $80,000 + 1,600,000 = 1,680,000 \text{ bytes} \approx \mathbf{1.60 \text{ MB}}$.

4. **Percentage Memory Savings**:
   $$\text{Savings} = \left(1 - \frac{1.68 \text{ MB}}{400 \text{ MB}}\right) \times 100\% = \mathbf{99.58\% \text{ reduction!}}$$
</details>

---

### Level 2: Scaffolded System Refactoring — Dense Matrix to Sparse List Converter
**Problem Statement:** Write an algorithm that ingests an arbitrary dense adjacency matrix and transforms it into an optimized adjacency list graph while validating the Handshaking Lemma in $O(V^2)$ time.

<details>
<summary>View Complete Java Matrix-to-List Converter Implementation</summary>

```java
package edu.se.datastructures.graphs;

public class GraphRepresentationConverter {

    public static AdjacencyListGraph convert(int[][] matrix, boolean isDirected) {
        int v = matrix.length;
        AdjacencyListGraph listGraph = new AdjacencyListGraph(v);
        int totalDegreeSum = 0;

        for (int i = 0; i < v; i++) {
            for (int j = 0; j < v; j++) {
                if (matrix[i][j] != 0) {
                    listGraph.addEdge(i, j, matrix[i][j]);
                    totalDegreeSum++;
                }
            }
        }

        if (!isDirected) {
            // Validate Euler's Handshaking Lemma
            int edges = listGraph.getNumEdges() / 2;
            if (totalDegreeSum != 2 * edges) {
                throw new IllegalStateException("Handshaking Lemma violated in input matrix!");
            }
        }

        return listGraph;
    }
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — Compressed Sparse Row (CSR) Storage
**Problem Statement:** Design a zero-overhead, cache-aligned **Compressed Sparse Row (CSR)** graph storage engine in Java. CSR represents a graph of $|V|$ vertices and $|E|$ edges using only two contiguous flat primitive arrays: `offsets` of size $|V| + 1$ and `edges` of size $|E|$. Ensure zero object allocations during edge iteration.

<details>
<summary>View Production-Grade CSR Graph Implementation</summary>

```java
package edu.se.datastructures.graphs;

public class CompressedSparseRowGraph {
    private final int numVertices;
    private final int numEdges;
    private final int[] rowOffsets; // Size V + 1
    private final int[] columnIndices; // Size E
    private final double[] weights; // Size E

    public CompressedSparseRowGraph(int numVertices, int numEdges, int[] rowOffsets, int[] columnIndices, double[] weights) {
        this.numVertices = numVertices;
        this.numEdges = numEdges;
        this.rowOffsets = rowOffsets;
        this.columnIndices = columnIndices;
        this.weights = weights;
    }

    public int getDegree(int u) {
        return rowOffsets[u + 1] - rowOffsets[u];
    }

    public void forEachNeighbor(int u, EdgeConsumer consumer) {
        int start = rowOffsets[u];
        int end = rowOffsets[u + 1];
        for (int i = start; i < end; i++) {
            consumer.accept(columnIndices[i], weights[i]);
        }
    }

    @FunctionalInterface
    public interface EdgeConsumer {
        void accept(int neighbor, double weight);
    }
}
```
</details>
