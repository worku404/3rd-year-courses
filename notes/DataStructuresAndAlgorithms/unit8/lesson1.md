# Lesson 1 — Shell Sort Gap Mathematics & Merge Sort Stable Divide-and-Conquer

> [!NOTE]
> **Learning Outcomes:**
> - Formalise the **Shell Sort** algorithm as a generalised Insertion Sort over diminishing gap sequences.
> - Analyse the asymptotic impact of different gap sequences: **Shell ($O(n^2)$)**, **Knuth ($O(n^{1.5})$)**, **Sedgewick ($O(n^{4/3})$)**, and **Ciura (empirical best)**.
> - Prove **Merge Sort's** time recurrence $T(n) = 2T(n/2) + O(n) = O(n \log n)$ via the Master Theorem.
> - Implement the stable, cache-conscious merge routine with $O(n)$ auxiliary buffer.
> - Explain external sorting (multi-way merge on disk/tape) and the **TimSort** hybrid used in Java's `Arrays.sort`.

{{media:merge-video}}

{{media:merge-visual}}

## Executive Summary

The AASTU curriculum introduces **Shell Sort** and **Merge Sort** as foundational advanced-sorting paradigms that motivate the critical performance boundary between the simple $O(n^2)$ algorithms (Bubble, Insertion, Selection) and the theoretically optimal $O(n \log n)$ algorithms. Shell Sort approaches this boundary by repeatedly reducing the number of inversions via coarser-then-finer gap passes; Merge Sort achieves it by exploiting the recursive halving structure of the problem.

---

## 1. Shell Sort — Diminishing Increment Algorithm

Invented by Donald L. Shell in 1959, Shell Sort generalises Insertion Sort by performing $g$-sorted passes: instead of comparing adjacent elements (gap $g = 1$), it compares elements separated by a gap $g$, reducing $g$ in stages until $g = 1$.

### 1.1 Formal Algorithm
```
function shellSort(A, n):
    for each gap g in decreasing gap sequence:
        for i = g to n-1:
            temp = A[i]
            j = i
            while j >= g and A[j-g] > temp:
                A[j] = A[j-g]
                j -= g
            A[j] = temp
```

### 1.2 Worked Example from Curriculum (Slides 5–12)
Input: `[8, 3, 1, 5, 2, 7, 4, 6]`  $n = 8$

- **$g = 4$**: Compare pairs $(0,4), (1,5), (2,6), (3,7)$ — 4-sort each interleaved subsequence.
  - $(8,2) \to 2, 8$ swapped; $(3,7) \to 3, 7$ OK; $(1,4) \to 1, 4$ OK; $(5,6) \to 5, 6$ OK.
  - After g=4: `[2, 3, 1, 5, 8, 7, 4, 6]`
- **$g = 2$**: Insertion sort on odd-index list $[3,5,7,6]$ and even-index list $[2,1,8,4]$.
  - After g=2: `[1, 3, 2, 5, 4, 7, 8, 6]`
- **$g = 1$**: Standard Insertion Sort on a nearly-sorted list — very few swaps needed!
  - After g=1: `[1, 2, 3, 4, 5, 6, 7, 8]` ✅

### 1.3 Gap Sequence Complexity Comparison

| Gap Sequence | Formula | Worst-Case Complexity |
| :--- | :--- | :--- |
| **Shell (1959)** | $\lfloor n/2 \rfloor, \lfloor n/4 \rfloor, \dots, 1$ | $O(n^2)$ |
| **Knuth (1973)** | $1, 4, 13, 40, 121, \dots$ where $g_k = 3g_{k-1}+1$ | $O(n^{1.5})$ |
| **Sedgewick (1982)** | $1, 5, 19, 41, 109, \dots$ | $O(n^{4/3})$ |
| **Ciura (2001)** | $1, 4, 10, 23, 57, 132, 301, 701$ | Best empirical |

### 1.4 Production Java (Knuth Gap Sequence)
```java
package edu.se.sorting;

public class ShellSort {
    public static void sort(int[] arr) {
        int n = arr.length;

        // Compute largest Knuth gap: 1, 4, 13, 40, 121, ...
        int gap = 1;
        while (gap < n / 3) gap = gap * 3 + 1;

        while (gap >= 1) {
            // Insertion sort with current gap
            for (int i = gap; i < n; i++) {
                int temp = arr[i];
                int j = i;
                while (j >= gap && arr[j - gap] > temp) {
                    arr[j] = arr[j - gap];
                    j -= gap;
                }
                arr[j] = temp;
            }
            gap /= 3;
        }
    }
}
```

---

## 2. Merge Sort — Stable O(n log n) Divide-and-Conquer

### 2.1 The Master Theorem Proof
Merge Sort divides the array into two halves and merges them. The recurrence is:
$$T(n) = 2T\!\left(\tfrac{n}{2}\right) + \Theta(n)$$
By the Master Theorem (Case 2, $a=2, b=2, f(n)=\Theta(n), n^{\log_b a} = n^1 = f(n)$):
$$T(n) = \Theta(n \log n)$$

### 2.2 The Stable Merge Routine
```java
package edu.se.sorting;

public class MergeSort {

    public static void sort(int[] arr) {
        if (arr.length <= 1) return;
        int[] aux = new int[arr.length]; // Allocate once to avoid GC churn
        mergeSort(arr, aux, 0, arr.length - 1);
    }

    private static void mergeSort(int[] arr, int[] aux, int lo, int hi) {
        if (lo >= hi) return;
        int mid = lo + (hi - lo) / 2; // Safe midpoint (prevents integer overflow)
        mergeSort(arr, aux, lo, mid);
        mergeSort(arr, aux, mid + 1, hi);

        // Optimisation: skip merge if already in order
        if (arr[mid] <= arr[mid + 1]) return;
        merge(arr, aux, lo, mid, hi);
    }

    private static void merge(int[] arr, int[] aux, int lo, int mid, int hi) {
        // Copy to auxiliary buffer
        System.arraycopy(arr, lo, aux, lo, hi - lo + 1);

        int i = lo;       // Pointer into left half
        int j = mid + 1;  // Pointer into right half

        for (int k = lo; k <= hi; k++) {
            if      (i > mid)           arr[k] = aux[j++]; // Left exhausted
            else if (j > hi)            arr[k] = aux[i++]; // Right exhausted
            else if (aux[j] < aux[i])   arr[k] = aux[j++]; // Right element smaller
            else                        arr[k] = aux[i++]; // Left element smaller or equal (STABLE!)
        }
    }
}
```

> [!IMPORTANT]
> **The Stability Invariant**: Note the `aux[j] < aux[i]` test (strict less-than). When equal, we always take from the left half first. This ensures equal elements **preserve their original relative order** — making Merge Sort a **stable** sorting algorithm.

### 2.3 Bottom-Up (Iterative) Merge Sort
Eliminates recursion overhead for production systems:
```java
public static void sortBottomUp(int[] arr) {
    int n = arr.length;
    int[] aux = new int[n];
    // Merge sub-arrays of increasing size: 1, 2, 4, 8, ...
    for (int size = 1; size < n; size *= 2) {
        for (int lo = 0; lo < n - size; lo += 2 * size) {
            int mid = lo + size - 1;
            int hi  = Math.min(lo + 2 * size - 1, n - 1);
            merge(arr, aux, lo, mid, hi);
        }
    }
}
```

---

## 3. External Sorting & TimSort

### 3.1 External Sorting (Large Data on Disk)
When data is too large to fit in RAM, Merge Sort becomes **External Sort**:
1. **Run generation**: Load chunks into RAM, sort internally, write sorted "runs" to disk.
2. **K-way merge**: Simultaneously merge $K$ sorted runs using a Min-Heap of $K$ pointers.

### 3.2 TimSort — Production Hybrid (Java, Python, Android)
`java.util.Arrays.sort()` on objects uses **TimSort**:
- **Phase 1**: Scan array for existing natural "runs" (monotone subsequences), extending short ones with Insertion Sort.
- **Phase 2**: Merge adjacent runs using a stack-based merge policy (merge run of size $A$ with run $B$ only if $A \le B$, maintaining a balanced merge tree).
- **Result**: $O(n)$ on already-sorted or nearly-sorted data, $O(n \log n)$ worst case — stable!

---

## 4. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Trace Shell Sort with **Ciura gaps** $[701, 301, 132, 57, 23, 10, 4, 1]$ on the input `[9, 7, 5, 3, 1, 8, 6, 4, 2, 0]` ($n = 10$).
Show the array state after each gap pass that is relevant (i.e., gaps $\le n$).

<details>
<summary>View Level 1 Trace</summary>

Relevant gaps for $n=10$: $\{10 > 10 \to$ skip$\}$, $4$, $1$.

- **g=4**: Each element compared 4 positions back via insertion.
  - Result: `[1, 7, 2, 0, 9, 8, 5, 3, 6, 4]` (approx — near 4-sorted)
- **g=1** (Insertion Sort on near-sorted):
  - Result: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` ✅
</details>

---

### Level 2: Scaffolded System Refactoring — K-way External Merge
**Problem**: Given $K$ pre-sorted integer arrays on "disk", merge them into a single sorted stream in $O(N \log K)$ time using a Min-Heap.

<details>
<summary>View K-way Merge Implementation</summary>

```java
package edu.se.sorting;

import java.util.PriorityQueue;

public class KWayMerge {

    public static int[] merge(int[][] sortedArrays) {
        int k = sortedArrays.length;
        int totalSize = 0;
        for (int[] a : sortedArrays) totalSize += a.length;

        // Min-heap entry: [value, arrayIndex, positionInArray]
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> a[0] - b[0]);

        // Initialise with the first element of each run
        for (int i = 0; i < k; i++) {
            if (sortedArrays[i].length > 0) {
                heap.offer(new int[]{sortedArrays[i][0], i, 0});
            }
        }

        int[] result = new int[totalSize];
        int idx = 0;

        while (!heap.isEmpty()) {
            int[] top = heap.poll();
            result[idx++] = top[0];

            int arrayIdx = top[1];
            int posIdx   = top[2] + 1;

            if (posIdx < sortedArrays[arrayIdx].length) {
                heap.offer(new int[]{sortedArrays[arrayIdx][posIdx], arrayIdx, posIdx});
            }
        }
        return result;
    }
}
```
</details>

---

### Level 3: Senior Engineering Challenge — In-Place Merge Sort
Standard Merge Sort requires $O(n)$ auxiliary space. Implement an **in-place block merge** achieving $O(1)$ auxiliary space (excluding the recursion stack of $O(\log n)$).

<details>
<summary>View In-Place Merge Strategy</summary>

```java
package edu.se.sorting;

public class InPlaceMergeSort {

    private static void inPlaceMerge(int[] arr, int lo, int mid, int hi) {
        int left  = lo;
        int right = mid + 1;

        if (arr[mid] <= arr[right]) return; // Already merged

        while (left <= mid && right <= hi) {
            if (arr[left] <= arr[right]) {
                left++;
            } else {
                // Rotate right element into position (block shift)
                int value = arr[right];
                int idx = right;
                while (idx != left) {
                    arr[idx] = arr[idx - 1];
                    idx--;
                }
                arr[left] = value;
                left++;
                mid++;
                right++;
            }
        }
    }

    public static void sort(int[] arr, int lo, int hi) {
        if (lo >= hi) return;
        int mid = lo + (hi - lo) / 2;
        sort(arr, lo, mid);
        sort(arr, mid + 1, hi);
        inPlaceMerge(arr, lo, mid, hi);
    }
    // Note: Each rotation is O(n) -> overall O(n^2 log n) worst case.
    // True O(n log n) in-place merge requires Kronrod / Huang-Langston algorithms.
}
```
</details>
