# Lesson 1 — Linear, Binary, Interpolation & Fibonacci Search Algorithms

> [!NOTE]
> **Learning Outcomes:**
> - Implement and analyse **Linear Search** ($O(n)$) including the sentinel optimisation.
> - Prove the correctness of **Binary Search** using the loop invariant and analyse its $O(\log n)$ recurrence.
> - Derive the **Interpolation Search** formula and explain when it achieves $O(\log \log n)$ and when it degenerates to $O(n)$.
> - Describe **Fibonacci Search** and explain its advantage on hardware without division instructions.
> - Select the appropriate searching algorithm based on data characteristics and access patterns.

{{media:search-video}}

{{media:search-visual}}

## Executive Summary

Searching is the most fundamental operation in computing. The AASTU Unit 9 curriculum covers four searching strategies that span the complexity hierarchy from $O(n)$ to $O(\log \log n)$, before transitioning to hash-based $O(1)$ search. Understanding when and why each algorithm is appropriate is a core competency for 3rd-year software engineers.

---

## 1. Linear (Sequential) Search — $O(n)$

### 1.1 Standard Implementation
```java
package edu.se.searching;

public class LinearSearch {

    /** Returns index of target in arr, or -1 if not found. O(n). */
    public static int search(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) return i;
        }
        return -1;
    }

    /**
     * Sentinel optimisation: avoids bounds check on each iteration.
     * Reduces comparisons by ~50% at the cost of one array write.
     */
    public static int searchSentinel(int[] arr, int n, int target) {
        int last = arr[n - 1];
        arr[n - 1] = target; // Place sentinel

        int i = 0;
        while (arr[i] != target) i++;

        arr[n - 1] = last; // Restore
        return (i < n - 1 || last == target) ? i : -1;
    }
}
```

### 1.2 When to Use
- **Unsorted data** — no alternative exists without preprocessing.
- **Very small $n$** ($n < 32$) — simpler code, no branch misprediction vs Binary Search.
- **Linked lists** — sequential access is the only option; binary search not applicable.

---

## 2. Binary Search — $O(\log n)$

### 2.1 Formal Loop Invariant Proof
**Invariant:** Before each iteration, if the target exists in `arr`, it is in `arr[lo..hi]`.

- **Initialisation:** `lo = 0, hi = n-1` — target is somewhere in `arr[0..n-1]`. ✅
- **Maintenance:** If `arr[mid] < target`, target cannot be in `[lo..mid]`, so set `lo = mid+1`. Invariant preserved. Similarly for `arr[mid] > target`, set `hi = mid-1`. ✅
- **Termination:** When `lo > hi`, the range is empty. If invariant holds and range is empty, target is absent. ✅

### 2.2 Production Java Implementation (Safe Mid-Point)
```java
package edu.se.searching;

public class BinarySearch {

    public static int search(int[] sortedArr, int target) {
        int lo = 0, hi = sortedArr.length - 1;

        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2; // Safe: prevents integer overflow vs (lo+hi)/2

            if      (sortedArr[mid] == target) return mid;
            else if (sortedArr[mid] <  target) lo = mid + 1;
            else                               hi = mid - 1;
        }
        return -1; // Not found
    }

    /** Leftmost insertion point (lower bound) — for sorted arrays with duplicates. */
    public static int lowerBound(int[] sortedArr, int target) {
        int lo = 0, hi = sortedArr.length;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (sortedArr[mid] < target) lo = mid + 1;
            else                          hi = mid;
        }
        return lo; // Index of first element >= target
    }

    /** Rightmost position (upper bound). */
    public static int upperBound(int[] sortedArr, int target) {
        int lo = 0, hi = sortedArr.length;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (sortedArr[mid] <= target) lo = mid + 1;
            else                           hi = mid;
        }
        return lo - 1; // Index of last element <= target
    }
}
```

> [!IMPORTANT]
> **Integer Overflow Bug**: `mid = (lo + hi) / 2` will overflow when `lo + hi > Integer.MAX_VALUE` (i.e., for arrays with $> 2^{30}$ elements). Always use `mid = lo + (hi - lo) / 2`. This is a famous bug that existed in the JDK for 9 years (Java bug #5045582).

### 2.3 Recursive Version (Educational)
```java
public static int searchRecursive(int[] arr, int lo, int hi, int target) {
    if (lo > hi) return -1;
    int mid = lo + (hi - lo) / 2;
    if      (arr[mid] == target) return mid;
    else if (arr[mid] <  target) return searchRecursive(arr, mid + 1, hi, target);
    else                         return searchRecursive(arr, lo, mid - 1, target);
}
// Space: O(log n) call stack. Prefer iterative for production.
```

---

## 3. Interpolation Search — $O(\log \log n)$ Average

### 3.1 The Position Formula
Instead of always halving at mid, Interpolation Search estimates where the target would be:

$$\text{mid} = \text{lo} + \left\lfloor(\text{hi} - \text{lo}) \times \frac{\text{key} - A[\text{lo}]}{A[\text{hi}] - A[\text{lo}]}\right\rfloor$$

This is derived from a linear interpolation between $A[\text{lo}]$ and $A[\text{hi}]$.

### 3.2 Implementation
```java
package edu.se.searching;

public class InterpolationSearch {

    public static int search(int[] sortedArr, int target) {
        int lo = 0, hi = sortedArr.length - 1;

        while (lo <= hi
               && target >= sortedArr[lo]
               && target <= sortedArr[hi]) {

            if (lo == hi) {
                return sortedArr[lo] == target ? lo : -1;
            }

            // Interpolated probe position
            int mid = lo + (int)((long)(hi - lo)
                     * (target - sortedArr[lo])
                     / (sortedArr[hi] - sortedArr[lo]));

            if      (sortedArr[mid] == target) return mid;
            else if (sortedArr[mid] <  target) lo = mid + 1;
            else                               hi = mid - 1;
        }
        return -1;
    }
}
```

### 3.3 Complexity Analysis
- **Uniform distribution**: Each probe eliminates a fraction proportional to the range. Analysis yields $O(\log \log n)$ average.
- **Worst case**: If data is extremely skewed (e.g., exponential gaps), the probe position degenerates to near `lo`, making it $O(n)$ — same as Linear Search.
- **Practice guideline**: Only use Interpolation Search when the data distribution is **known to be nearly uniform** (e.g., IP addresses, uniformly-spread timestamp indices).

---

## 4. Fibonacci Search — $O(\log n)$

### 4.1 Motivation
On older CPUs and embedded systems lacking a hardware divide instruction, binary search's `mid = (lo+hi)/2` is costly. Fibonacci Search uses only **subtraction** and **addition**.

### 4.2 Algorithm Description
1. Find the smallest Fibonacci number $F_k \ge n$.
2. Pad the array to size $F_k$ if needed.
3. Probe at position $lo + F_{k-2}$:
   - If equal: found.
   - If target > probe: shift to right sub-problem of size $F_{k-1} - F_{k-2} = F_{k-3}$.
   - If target < probe: shift to left sub-problem of size $F_{k-2}$.

```java
package edu.se.searching;

public class FibonacciSearch {

    public static int search(int[] arr, int target) {
        int n = arr.length;
        int fibM2 = 0, fibM1 = 1, fib = 1; // F(0), F(1), F(2)

        while (fib < n) { fibM2 = fibM1; fibM1 = fib; fib = fibM1 + fibM2; }

        int offset = -1;

        while (fib > 1) {
            int i = Math.min(offset + fibM2, n - 1);

            if      (arr[i] < target) { fib = fibM1; fibM1 = fibM2; fibM2 = fib - fibM1; offset = i; }
            else if (arr[i] > target) { fib = fibM2; fibM1 -= fibM2; fibM2 = fib - fibM1; }
            else                      return i; // Found
        }

        return (fibM1 == 1 && arr[offset + 1] == target) ? offset + 1 : -1;
    }
}
```

---

## 5. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Using Binary Search, trace the search for `key=34` in: `[2, 25, 35, 39, 40, 47, 50]`. Also trace the Interpolation Search formula at each step. Compare the number of probes.

<details>
<summary>View Level 1 Answer</summary>

**Binary Search trace (n=7):**
- Iter 1: lo=0, hi=6, mid=3 → A[3]=39 > 34 → hi=2
- Iter 2: lo=0, hi=2, mid=1 → A[1]=25 < 34 → lo=2
- Iter 3: lo=2, hi=2, mid=2 → A[2]=35 > 34 → hi=1
- lo=2 > hi=1 → NOT FOUND (34 is not in array). 3 probes.

**Interpolation Search trace:**
- Iter 1: mid = 0 + 6*(34-2)/(50-2) = 6*(32/48) = 4 → A[4]=40 > 34 → hi=3
- Iter 2: mid = 0 + 3*(34-2)/(39-2) = 3*(32/37) = 2 → A[2]=35 > 34 → hi=1
- Iter 3: lo=0, hi=1: mid=0*(34-2)/(25-2)=1 → A[1]=25 < 34 → lo=2
- lo=2 > hi=1 → NOT FOUND. Also 3 probes here (array is small).
</details>

---

### Level 2: Scaffolded Refactoring — Binary Search on Answer Technique
**Problem:** Find the **minimum capacity** needed for a conveyor belt to ship `weights = [1,2,3,4,5,6,7,8,9,10]` within `D = 5` days. (LeetCode 1011 — canonical "Binary Search on Answer" problem.)

<details>
<summary>View Binary Search on Answer Solution</summary>

```java
public class CapacityToShipPackages {

    public static int shipWithinDays(int[] weights, int days) {
        // Search space: [max single weight, sum of all weights]
        int lo = 0, hi = 0;
        for (int w : weights) { lo = Math.max(lo, w); hi += w; }

        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (canShipInDays(weights, days, mid)) hi = mid;
            else                                    lo = mid + 1;
        }
        return lo;
    }

    private static boolean canShipInDays(int[] weights, int days, int capacity) {
        int daysNeeded = 1, currentLoad = 0;
        for (int w : weights) {
            if (currentLoad + w > capacity) { daysNeeded++; currentLoad = 0; }
            currentLoad += w;
        }
        return daysNeeded <= days;
    }
}
```
Answer: `15`. This technique applies binary search to monotone feasibility functions.
</details>

---

### Level 3: Senior Engineering Challenge — Exponential Search (Unbounded Input)
**Problem:** Search a **sorted array of unknown length** (unbounded) for target `T`. Standard binary search requires knowing `n`. Implement **Exponential Search** which finds bounds in $O(\log n)$ then delegates to Binary Search.

<details>
<summary>View Exponential Search Implementation</summary>

```java
package edu.se.searching;

public class ExponentialSearch {
    /**
     * Search sorted unbounded array; access beyond actual bounds returns Integer.MAX_VALUE.
     * Phase 1: Double bound until arr[bound] > target -> O(log n)
     * Phase 2: Binary search in [bound/2, bound]      -> O(log n)
     * Total:   O(log n)
     */
    public static int search(int[] arr, int target) {
        if (arr[0] == target) return 0;

        int bound = 1;
        while (bound < arr.length && arr[bound] <= target) {
            bound *= 2;
        }

        int lo = bound / 2;
        int hi = Math.min(bound, arr.length - 1);
        return BinarySearch.search(arr, lo, hi, target);
    }
}
```
</details>
