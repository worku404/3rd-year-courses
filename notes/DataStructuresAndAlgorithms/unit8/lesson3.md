# Lesson 3 — Linear Sorting & the Omega(n log n) Lower Bound Proof

> [!NOTE]
> **Learning Outcomes:**
> - Prove the **$\Omega(n \log n)$ information-theoretic lower bound** for comparison-based sorting via decision trees and Stirling's Approximation.
> - Implement **Counting Sort** ($O(n + k)$ time, $O(n + k)$ space) with the prefix-sum stability guarantee.
> - Implement **Radix Sort LSD** ($O(d(n + k))$) using stable Counting Sort as a sub-routine on each digit.
> - Implement **Bucket Sort** ($O(n)$ average on uniform inputs) using dynamic linked lists per bucket.
> - Identify the fundamental constraint: all linear-time sorts require **non-comparison structural assumptions** about the keys.

{{media:radix-video}}

{{media:linear-visual}}

## Executive Summary

The previous two lessons examined algorithms that all achieve $O(n \log n)$. A natural question arises: **can we do better?** The answer is: **not with comparisons**. This lesson first proves that $\Omega(n \log n)$ is a strict mathematical lower bound for any sort that only uses $<$, $>$, $=$ comparisons. Then it introduces three radically different algorithms — **Counting Sort**, **Radix Sort**, and **Bucket Sort** — that bypass this barrier by exploiting structural knowledge of the key domain (integer bounds, fixed digit lengths, uniform distributions).

---

## 1. The $\Omega(n \log n)$ Lower Bound (Decision Tree Argument)

### 1.1 Decision Tree Model
A **comparison-based sorting algorithm** can be modelled as a binary decision tree where:
- Each **internal node** represents a comparison: $A[i] \le A[j]?$
- Each **leaf** represents one specific output permutation.

### 1.2 The Counting Argument

> **Theorem:** Any comparison-based sorting algorithm requires at least $\Omega(n \log n)$ comparisons in the worst case.

**Proof:**
1. There are $n!$ possible permutations of $n$ elements. For the algorithm to be **correct**, it must produce the unique correct permutation for every input. Therefore the decision tree must have **at least $n!$ leaves**.
2. A binary tree of height $h$ contains at most $2^h$ leaves. Therefore:
$$2^h \ge n! \implies h \ge \log_2(n!)$$
3. By **Stirling's Approximation**: $\log_2(n!) = \sum_{k=1}^n \log_2 k \ge \int_1^n \log_2 x \, dx = n\log_2 n - n/\ln 2 = \Omega(n \log n)$.
4. Therefore: $h \ge \Omega(n \log n)$.

Since $h$ is the minimum number of comparisons in the worst case, **no comparison sort can beat $\Omega(n \log n)$. $\mathbf{Q.E.D.}$**

### 1.3 Algorithms at the Bound
- **Merge Sort**, **Heap Sort**: Achieve $\Theta(n \log n)$ — asymptotically optimal.
- **Quick Sort**: $\Theta(n \log n)$ average, $O(n^2)$ worst — not worst-case optimal.
- To beat the bound, we must **stop using comparisons as the fundamental operation**.

---

## 2. Counting Sort — $O(n + k)$ Stable Integer Sort

### 2.1 Precondition
All keys must be non-negative integers in a known bounded range $[0, k-1]$.

### 2.2 The Three-Phase Algorithm (Curriculum Slide Reference)
```
Phase 1 — COUNT frequencies:
    For each element A[j]: count[A[j]]++

Phase 2 — PREFIX SUM (running total):
    For i = 1 to k-1: count[i] += count[i-1]
    (count[i] now = number of elements <= i = last valid output position + 1)

Phase 3 — BUILD OUTPUT (right-to-left for stability):
    For j = n-1 down to 0:
        out[--count[A[j]]] = A[j]
```

### 2.3 Production Java Implementation
```java
package edu.se.sorting;

public class CountingSort {

    public static int[] sort(int[] arr, int maxKey) {
        int k = maxKey + 1;
        int[] count  = new int[k];
        int[] output = new int[arr.length];

        // Phase 1: Frequency count
        for (int x : arr) count[x]++;

        // Phase 2: Prefix sum — count[i] = number of elements <= i
        for (int i = 1; i < k; i++) count[i] += count[i - 1];

        // Phase 3: Right-to-left placement for stability
        for (int j = arr.length - 1; j >= 0; j--) {
            output[--count[arr[j]]] = arr[j];
        }

        return output;
    }

    /** In-place variant when only ordering is needed (non-stable) */
    public static void sortInPlace(int[] arr, int maxKey) {
        int[] count = new int[maxKey + 1];
        for (int x : arr)    count[x]++;
        int idx = 0;
        for (int v = 0; v <= maxKey; v++)
            while (count[v]-- > 0) arr[idx++] = v;
    }
}
```

### 2.4 Worked Example
Input: `[4, 2, 2, 8, 3, 3, 1]`, $k = 9$

| Phase | count array |
|:------|:-----------|
| After frequency count | `[0, 1, 2, 2, 1, 0, 0, 0, 1]` |
| After prefix sum | `[0, 1, 3, 5, 6, 6, 6, 6, 7]` |
| Output (right-to-left placement) | `[1, 2, 2, 3, 3, 4, 8]` ✅ |

**Stability verification:** The two `2`s retain their original left-to-right order in the output — proven by the right-to-left scan.

---

## 3. Radix Sort LSD — $O(d(n + k))$

Radix Sort extends Counting Sort to sort integers with multiple digits. **LSD (Least Significant Digit)** processes digits right-to-left, using a **stable** sort (Counting Sort) on each individual digit position.

### 3.1 LSD Correctness Argument
After sorting on digit $d$: any two elements equal in digits $[d, d_{max}]$ are ordered correctly by prior digits $[0, d-1]$ because we use a **stable** sub-sort. By induction, after processing all $d_{max}$ digits, the array is sorted.

### 3.2 Production Java Implementation
```java
package edu.se.sorting;

public class RadixSort {

    public static void lsdSort(int[] arr) {
        int max = findMax(arr);

        // Process each digit position: units, tens, hundreds, ...
        for (int exp = 1; max / exp > 0; exp *= 10) {
            countingByDigit(arr, exp);
        }
    }

    private static void countingByDigit(int[] arr, int exp) {
        int n = arr.length;
        int[] output = new int[n];
        int[] count  = new int[10]; // Radix k=10

        // Count occurrences of each digit
        for (int x : arr) count[(x / exp) % 10]++;

        // Prefix sum
        for (int i = 1; i < 10; i++) count[i] += count[i - 1];

        // Build output right-to-left (MUST be stable)
        for (int j = n - 1; j >= 0; j--) {
            int digit = (arr[j] / exp) % 10;
            output[--count[digit]] = arr[j];
        }

        System.arraycopy(output, 0, arr, 0, n);
    }

    private static int findMax(int[] arr) {
        int max = arr[0];
        for (int x : arr) if (x > max) max = x;
        return max;
    }
}
```

### 3.3 Worked Example (from Curriculum Slide 51 Reading Assignment)
Input: `[170, 45, 75, 90, 802, 24, 2, 66]`
- **Pass 1 (units digit):** `[170, 90, 802, 2, 24, 45, 75, 66]`
- **Pass 2 (tens digit):** `[802, 2, 24, 45, 66, 170, 75, 90]`
- **Pass 3 (hundreds digit):** `[2, 24, 45, 66, 75, 90, 170, 802]` ✅

---

## 4. Bucket Sort — $O(n)$ Average on Uniform Distributions

**Bucket Sort** works when input values are uniformly distributed over a known range $[a, b)$:

1. Create $k$ empty buckets, each representing a sub-range of $[a, b)$.
2. Distribute elements into buckets: `bucket[floor(k * (x - a) / (b - a))].add(x)`.
3. Sort each bucket individually (Insertion Sort for small buckets).
4. Concatenate all buckets.

```java
package edu.se.sorting;

import java.util.*;

public class BucketSort {

    public static void sort(double[] arr) {
        int n = arr.length;
        if (n <= 1) return;

        List<Double>[] buckets = new ArrayList[n];
        for (int i = 0; i < n; i++) buckets[i] = new ArrayList<>();

        // Distribute into n buckets (assumes values in [0.0, 1.0))
        for (double x : arr) {
            int bucketIdx = (int)(n * x);
            if (bucketIdx == n) bucketIdx = n - 1; // Handle x == 1.0
            buckets[bucketIdx].add(x);
        }

        // Sort each bucket and concatenate
        int idx = 0;
        for (List<Double> bucket : buckets) {
            Collections.sort(bucket);
            for (double x : bucket) arr[idx++] = x;
        }
    }
}
```

**Average-Case Analysis:** With $n$ elements uniformly distributed into $n$ buckets, each bucket contains $O(1)$ elements on average. Sorting each bucket with Insertion Sort is $O(1)$ per bucket → total $O(n)$ average.

---

## 5. Complete Sorting Algorithm Decision Framework

| Situation | Recommended Algorithm |
| :--- | :--- |
| General purpose, primitives, high performance | **Dual-Pivot Quick Sort** (Java `Arrays.sort(int[])`) |
| General purpose, objects, stability required | **TimSort** (Java `Arrays.sort(Object[])`) |
| Guaranteed worst-case, $O(1)$ space | **Heap Sort** |
| Nearly sorted / many natural runs | **TimSort / Merge Sort** |
| Integers with small range $k \ll n$ | **Counting Sort** $O(n + k)$ |
| Fixed-width integer or string keys | **Radix Sort LSD** $O(d(n+k))$ |
| Floating-point in $[0, 1)$, uniform distribution | **Bucket Sort** $O(n)$ avg |

---

## 6. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Given the input `[329, 457, 657, 839, 436, 720, 355]`, perform a complete **LSD Radix Sort** trace. Show the array after each of the three digit-position passes (units, tens, hundreds).

<details>
<summary>View Level 1 Trace</summary>

**Pass 1 (units digit: 9,7,7,9,6,0,5):**
Buckets: `0:[720]`, `5:[355]`, `6:[436]`, `7:[457,657]`, `9:[329,839]`
Output: `[720, 355, 436, 457, 657, 329, 839]`

**Pass 2 (tens digit: 2,5,3,5,5,2,3):**
Buckets: `2:[720,329]`, `3:[436,839]`, `5:[355,457,657]`
Output: `[720, 329, 436, 839, 355, 457, 657]`

**Pass 3 (hundreds digit: 7,3,4,8,3,4,6):**
Buckets: `3:[329,355]`, `4:[436,457]`, `6:[657]`, `7:[720]`, `8:[839]`
Output: `[329, 355, 436, 457, 657, 720, 839]` ✅
</details>

---

### Level 2: Scaffolded Refactoring — Negative Integer Radix Sort
**Problem:** Standard Radix Sort handles only non-negative integers. Extend it to handle negative integers by splitting the array, sorting both halves separately, then concatenating (negatives in reverse order, then positives).

<details>
<summary>View Negative Integer Radix Sort</summary>

```java
package edu.se.sorting;

public class RadixSortWithNegatives {

    public static void sort(int[] arr) {
        // Separate negatives and positives
        int negCount = 0;
        for (int x : arr) if (x < 0) negCount++;

        int[] neg = new int[negCount];
        int[] pos = new int[arr.length - negCount];
        int ni = 0, pi = 0;

        for (int x : arr) {
            if (x < 0) neg[ni++] = -x; // Negate for sorting
            else        pos[pi++] = x;
        }

        // Sort both halves
        RadixSort.lsdSort(pos);
        RadixSort.lsdSort(neg); // neg is sorted as positives

        // Merge: negatives reversed (largest negative = smallest absolute value)
        int idx = 0;
        for (int i = neg.length - 1; i >= 0; i--) arr[idx++] = -neg[i];
        for (int x : pos) arr[idx++] = x;
    }
}
```
</details>

---

### Level 3: Senior Engineering Challenge — Parallel Counting Sort on Multi-Core
**Problem:** Implement a **parallel Counting Sort** using Java's `java.util.concurrent.ForkJoinPool`. Split the frequency-counting phase across processor cores, then merge thread-local count arrays before the prefix-sum and output phases.

<details>
<summary>View Parallel Counting Sort Implementation</summary>

```java
package edu.se.sorting;

import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;

public class ParallelCountingSort {
    private static final int PARALLEL_THRESHOLD = 50_000;

    private static class CountAction extends RecursiveAction {
        final int[] arr, localCount;
        final int lo, hi;

        CountAction(int[] arr, int[] localCount, int lo, int hi) {
            this.arr = arr; this.localCount = localCount;
            this.lo = lo; this.hi = hi;
        }

        @Override
        protected void compute() {
            if (hi - lo <= PARALLEL_THRESHOLD) {
                for (int i = lo; i < hi; i++) localCount[arr[i]]++;
                return;
            }
            int mid = (lo + hi) >>> 1;
            int[] leftCount  = new int[localCount.length];
            int[] rightCount = new int[localCount.length];
            CountAction left  = new CountAction(arr, leftCount, lo, mid);
            CountAction right = new CountAction(arr, rightCount, mid, hi);
            invokeAll(left, right);
            // Merge counts
            for (int i = 0; i < localCount.length; i++)
                localCount[i] = leftCount[i] + rightCount[i];
        }
    }

    public static int[] sort(int[] arr, int maxKey) {
        int k = maxKey + 1;
        int[] count  = new int[k];
        int[] output = new int[arr.length];

        // Parallel counting phase
        ForkJoinPool pool = ForkJoinPool.commonPool();
        pool.invoke(new CountAction(arr, count, 0, arr.length));

        // Sequential prefix sum (inherently serial — O(k))
        for (int i = 1; i < k; i++) count[i] += count[i - 1];

        // Sequential output phase (right-to-left for stability)
        for (int j = arr.length - 1; j >= 0; j--)
            output[--count[arr[j]]] = arr[j];

        return output;
    }
}
```
</details>
