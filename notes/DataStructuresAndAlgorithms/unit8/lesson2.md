# Lesson 2 — Quick Sort Partitioning Architectures & In-Place Heap Sort

> [!NOTE]
> **Learning Outcomes:**
> - Implement and trace the **Lomuto** and **Hoare** partition schemas, understanding their boundary invariants.
> - Explain why Quick Sort degenerates to $O(n^2)$ on pre-sorted inputs and apply **randomised pivot** mitigation.
> - Prove the **BuildHeap linear time** invariant: converting an arbitrary array into a Max-Heap costs $O(n)$ not $O(n \log n)$.
> - Implement production **Heap Sort** and articulate why it guarantees $O(n \log n)$ worst-case with $O(1)$ auxiliary space.
> - Compare Quick Sort, Merge Sort and Heap Sort across stability, cache behaviour, and practical throughput.

{{media:quick-video}}

{{media:heap-video}}

{{media:quick-heap-visual}}

## Executive Summary

This lesson covers the two most important in-place comparison sorts:

1. **Quick Sort** — expected $O(n \log n)$ with small constant factors, making it the fastest comparison sort in practice for random data. Its key weakness is $O(n^2)$ worst-case on adversarial pivot selections, mitigated by randomisation.

2. **Heap Sort** — guaranteed $O(n \log n)$ worst-case with $O(1)$ auxiliary space via in-place heap manipulation. It trades cache performance for the unconditional time guarantee.

Both underpin Java's dual strategy: `Arrays.sort(int[])` uses **Dual-Pivot Quick Sort** for primitives (exploiting no stability requirement and great cache behaviour); `Arrays.sort(Object[])` uses **TimSort** (Merge-based, stable, required for Comparable contract).

---

## 1. Quick Sort — Lomuto Partition Schema (Curriculum Slides 13–17)

Quick Sort uses the **divide-and-conquer** strategy:
1. Choose a **pivot** element $p$.
2. **Partition** the array so all elements $\le p$ go left, and all elements $\ge p$ go right.
3. Recursively sort the two partitions.

### 1.1 Lomuto Partition
The Lomuto schema designates the **last element** as pivot. It maintains a "boundary" index $i$ such that elements in $[lo, i]$ are all $\le$ pivot.

```java
package edu.se.sorting;

public class QuickSort {

    public static void sort(int[] arr) {
        sort(arr, 0, arr.length - 1);
    }

    private static void sort(int[] arr, int lo, int hi) {
        if (lo >= hi) return;
        int pivotIdx = partition(arr, lo, hi);
        sort(arr, lo, pivotIdx - 1);
        sort(arr, pivotIdx + 1, hi);
    }

    /** Lomuto partition: places pivot at its correct sorted position. */
    private static int partition(int[] arr, int lo, int hi) {
        int pivot = arr[hi]; // Choose rightmost as pivot
        int i = lo - 1;      // Index of last element <= pivot

        for (int j = lo; j < hi; j++) {
            if (arr[j] <= pivot) {
                i++;
                swap(arr, i, j);
            }
        }
        swap(arr, i + 1, hi); // Place pivot in correct position
        return i + 1;
    }

    private static void swap(int[] arr, int i, int j) {
        int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    }
}
```

### 1.2 Correctness Invariant
After `partition(arr, lo, hi)` returns index `p`:
- `arr[p] == pivot` is at its **final sorted position**.
- All elements in `arr[lo..p-1]` are $\le$ pivot.
- All elements in `arr[p+1..hi]` are $\ge$ pivot.

### 1.3 Hoare Partition (Original 1962 Schema)
Uses two converging pointers, averages 3x fewer swaps than Lomuto:

```java
/** Hoare partition: pivot not necessarily placed at exact position; returns split index. */
private static int hoarePartition(int[] arr, int lo, int hi) {
    int pivot = arr[lo + (hi - lo) / 2]; // Median position pivot
    int i = lo - 1;
    int j = hi + 1;

    while (true) {
        do { i++; } while (arr[i] < pivot);
        do { j--; } while (arr[j] > pivot);
        if (i >= j) return j;
        swap(arr, i, j);
    }
}
```

> [!WARNING]
> **Hoare Boundary Subtlety:** Hoare returns index `j` such that elements `[lo..j]` are $\le$ pivot and `[j+1..hi]` are $\ge$ pivot, but the pivot itself may NOT be at position `j`. The recursive calls must be `sort(lo, j)` and `sort(j+1, hi)`.

---

## 2. Pivot Selection & Worst-Case Mitigation

### 2.1 The Sorted-Input Disaster
If the input `[1, 2, 3, ..., n]` is already sorted and we pick the last element as pivot:
- Partition produces partitions of size $0$ and $n-1$ (maximally unbalanced).
- Recurrence: $T(n) = T(n-1) + O(n)$ → $T(n) = O(n^2)$.
- Stack depth reaches $O(n)$, risking `StackOverflowError` on $n = 100,000$.

### 2.2 Pivot Mitigation Strategies

```java
/** Randomised pivot — expected O(n log n) regardless of input distribution */
private static int randomisedPartition(int[] arr, int lo, int hi) {
    int randIdx = lo + (int)(Math.random() * (hi - lo + 1));
    swap(arr, randIdx, hi); // Move random element to last position
    return partition(arr, lo, hi);
}

/** Median-of-Three pivot */
private static int medianOfThreePivot(int[] arr, int lo, int hi) {
    int mid = lo + (hi - lo) / 2;
    // Sort lo, mid, hi so that arr[mid] is the median
    if (arr[lo] > arr[mid]) swap(arr, lo, mid);
    if (arr[lo] > arr[hi])  swap(arr, lo, hi);
    if (arr[mid] > arr[hi]) swap(arr, mid, hi);
    swap(arr, mid, hi - 1); // Place median just before last
    return arr[hi - 1];
}
```

---

## 3. Heap Sort — O(n) BuildHeap + O(n log n) Extraction

### 3.1 Max-Heap Array Representation
A Max-Heap stored in array $A$ obeys: $A[\text{parent}(i)] \ge A[i]$ for all $i$, where:
$$\text{parent}(i) = \lfloor (i-1)/2 \rfloor, \quad \text{leftChild}(i) = 2i+1, \quad \text{rightChild}(i) = 2i+2$$

### 3.2 Heapify (Sift-Down) — $O(\log n)$
Restores the heap property at index $i$ assuming both subtrees are valid heaps:

```java
package edu.se.sorting;

public class HeapSort {

    private static void heapify(int[] arr, int n, int i) {
        int largest = i;
        int left  = 2 * i + 1;
        int right = 2 * i + 2;

        if (left  < n && arr[left]  > arr[largest]) largest = left;
        if (right < n && arr[right] > arr[largest]) largest = right;

        if (largest != i) {
            int tmp = arr[i]; arr[i] = arr[largest]; arr[largest] = tmp;
            heapify(arr, n, largest); // Recurse down the displaced element
        }
    }
```

### 3.3 BuildHeap — $O(n)$ Linear Time (NOT $O(n \log n)$!)
```java
    private static void buildMaxHeap(int[] arr) {
        int n = arr.length;
        // Start from last non-leaf node and sift down each
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(arr, n, i);
        }
    }
```

> [!IMPORTANT]
> **BuildHeap Linear-Time Proof:**
> Heapify at height $h$ costs $O(h)$. At height $h$, there are $\le \lceil n/2^{h+1} \rceil$ nodes.
> Total cost $= \sum_{h=0}^{\lfloor \log n \rfloor} \lceil n/2^{h+1} \rceil \cdot O(h) = O\!\left(n \sum_{h=0}^{\infty} h/2^h\right) = O(n \cdot 2) = \mathbf{O(n)}$.

### 3.4 Sort Phase
```java
    public static void sort(int[] arr) {
        buildMaxHeap(arr);

        for (int i = arr.length - 1; i > 0; i--) {
            // Root (maximum) goes to final position
            int tmp = arr[0]; arr[0] = arr[i]; arr[i] = tmp;
            // Shrink heap and restore
            heapify(arr, i, 0);
        }
    }
}
```

---

## 4. Comparative Analysis: Quick Sort vs Merge Sort vs Heap Sort

| Property | Quick Sort | Merge Sort | Heap Sort |
| :--- | :--- | :--- | :--- |
| **Best Time** | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ |
| **Average Time** | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ |
| **Worst Time** | $O(n^2)$ ⚠️ | $O(n \log n)$ ✅ | $O(n \log n)$ ✅ |
| **Auxiliary Space** | $O(\log n)$ stack | $O(n)$ buffer | $O(1)$ ✅ |
| **Stable?** | No | Yes | No |
| **Cache Efficiency** | Excellent | Good | Poor |
| **Practical Speed** | **Fastest in practice** | Medium | Slower than QS |
| **Java Usage** | `Arrays.sort(int[])` (Dual-Pivot) | `Arrays.sort(Object[])` (TimSort) | `PriorityQueue` internals |

---

## 5. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Trace the Lomuto partition on `[3, 6, 8, 10, 1, 2, 1]` with pivot = last element ($1$). Show the array state and the values of $i$, $j$, and pivot after each iteration of the `j` loop.

<details>
<summary>View Level 1 Trace Table</summary>

**pivot = arr[6] = 1, i = -1**

| j | arr[j] | arr[j] <= pivot? | i | Array state |
|---|--------|------------------|---|-------------|
| 0 | 3 | No | -1 | `[3,6,8,10,1,2,1]` |
| 1 | 6 | No | -1 | `[3,6,8,10,1,2,1]` |
| 2 | 8 | No | -1 | `[3,6,8,10,1,2,1]` |
| 3 | 10 | No | -1 | `[3,6,8,10,1,2,1]` |
| 4 | 1 | **Yes** | 0 | `[1,6,8,10,3,2,1]` ← swap(0,4) |
| 5 | 2 | No | 0 | `[1,6,8,10,3,2,1]` |

Final swap: swap(i+1=1, hi=6) → `[1,1,8,10,3,2,6]`. Return 1.

Pivot `1` is now at index 1 (its correct final position). Left partition `[1]`, right `[8,10,3,2,6]`.
</details>

---

### Level 2: Scaffolded Refactoring — 3-Way Quick Sort (Dutch National Flag)
**Problem**: Standard Quick Sort handles many equal elements poorly. Implement **3-way partition** (Dijkstra's Dutch National Flag) that partitions into $[< pivot, = pivot, > pivot]$ in $O(n)$.

<details>
<summary>View 3-Way Quick Sort Implementation</summary>

```java
package edu.se.sorting;

public class ThreeWayQuickSort {

    public static void sort(int[] arr, int lo, int hi) {
        if (lo >= hi) return;

        int lt = lo, gt = hi;
        int pivot = arr[lo];
        int i = lo + 1;

        // Dutch National Flag partition
        while (i <= gt) {
            if      (arr[i] < pivot) swap(arr, lt++, i++);
            else if (arr[i] > pivot) swap(arr, i, gt--);
            else                     i++;
        }
        // Now arr[lo..lt-1] < pivot, arr[lt..gt] == pivot, arr[gt+1..hi] > pivot
        sort(arr, lo, lt - 1);
        sort(arr, gt + 1, hi);
    }

    private static void swap(int[] arr, int i, int j) {
        int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
}
```
</details>

---

### Level 3: Senior Engineering Challenge — Introspective Sort (IntroSort)
**Problem**: Implement **IntroSort** — the hybrid algorithm used by `std::sort` in C++ STL. IntroSort starts as Quick Sort but switches to Heap Sort when recursion depth exceeds $2 \lfloor \log_2 n \rfloor$ (preventing $O(n^2)$ on adversarial inputs), and switches to Insertion Sort for small sub-arrays ($n < 16$).

<details>
<summary>View IntroSort Implementation</summary>

```java
package edu.se.sorting;

public class IntroSort {
    private static final int INSERTION_SORT_THRESHOLD = 16;

    public static void sort(int[] arr) {
        int maxDepth = 2 * (int)(Math.log(arr.length) / Math.log(2));
        introSort(arr, 0, arr.length - 1, maxDepth);
    }

    private static void introSort(int[] arr, int lo, int hi, int depthLimit) {
        int size = hi - lo + 1;

        if (size <= INSERTION_SORT_THRESHOLD) {
            insertionSort(arr, lo, hi);
            return;
        }

        if (depthLimit == 0) {
            // Degrade to Heap Sort to guarantee O(n log n)
            partialHeapSort(arr, lo, hi);
            return;
        }

        int pivotIdx = medianOfThree(arr, lo, lo + size / 2, hi);
        swap(arr, pivotIdx, hi);
        int p = lomutoPartition(arr, lo, hi);
        introSort(arr, lo, p - 1, depthLimit - 1);
        introSort(arr, p + 1, hi, depthLimit - 1);
    }

    private static void insertionSort(int[] arr, int lo, int hi) {
        for (int i = lo + 1; i <= hi; i++) {
            int key = arr[i];
            int j = i - 1;
            while (j >= lo && arr[j] > key) { arr[j+1] = arr[j]; j--; }
            arr[j+1] = key;
        }
    }

    private static void partialHeapSort(int[] arr, int lo, int hi) {
        int n = hi - lo + 1;
        for (int i = n/2 - 1; i >= 0; i--) siftDown(arr, lo, i, n);
        for (int i = n - 1; i > 0; i--) {
            int t = arr[lo]; arr[lo] = arr[lo+i]; arr[lo+i] = t;
            siftDown(arr, lo, 0, i);
        }
    }

    private static void siftDown(int[] arr, int base, int i, int n) {
        while (true) {
            int largest = i, l = 2*i+1, r = 2*i+2;
            if (l < n && arr[base+l] > arr[base+largest]) largest = l;
            if (r < n && arr[base+r] > arr[base+largest]) largest = r;
            if (largest == i) break;
            int t = arr[base+i]; arr[base+i] = arr[base+largest]; arr[base+largest] = t;
            i = largest;
        }
    }

    private static int medianOfThree(int[] arr, int a, int b, int c) {
        if (arr[a] < arr[b]) {
            if (arr[b] < arr[c]) return b;
            return arr[a] < arr[c] ? c : a;
        }
        if (arr[a] < arr[c]) return a;
        return arr[b] < arr[c] ? c : b;
    }

    private static int lomutoPartition(int[] arr, int lo, int hi) {
        int pivot = arr[hi], i = lo - 1;
        for (int j = lo; j < hi; j++)
            if (arr[j] <= pivot) swap(arr, ++i, j);
        swap(arr, i+1, hi);
        return i + 1;
    }

    private static void swap(int[] arr, int i, int j) {
        int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
}
```
</details>
