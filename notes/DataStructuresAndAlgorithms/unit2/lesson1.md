# Lesson 1 — Fundamental Search Algorithms: Linear vs. Binary Search & Midpoint Overflow

> [!NOTE]
> **Learning Outcomes:**
> - Formulate the formal computational **Search Problem** across contiguous memory buffers.
> - Derive the statistical average-case comparison proof for **Linear Search** ($\\frac{n+1}{2} \\in \\Theta(n)$) and evaluate sentinel optimizations.
> - Solve the recurrence relation for **Binary Search** ($T(n) = T(n/2) + O(1) \\implies O(\\log_2 n)$).
> - Deconstruct the historic **Joshua Bloch Midpoint Overflow Bug** that remained undetected in the standard Java JDK for nine years.
> - Establish an amortized algebraic threshold determining when pre-sorting an unordered dataset for binary search is computationally profitable.

{{media:search-video}}

{{media:search-visual}}

## Executive Summary & System Context

At its computational core, a software system is an information retrieval engine. Whether searching for a user record in a database, querying a routing table in a network switch, or locating a symbol in an AST during compiler synthesis, systems spend a massive proportion of their CPU cycles searching.

The search problem is defined formally as follows:
- Given a collection $A$ containing $n$ elements $\\{ A[0], A[1], \\dots, A[n-1] \\}$ and a query target key $K$.
- Find an index $i$ such that $A[i] == K$, or return a sentinel value (typically $-1$ or an empty optional) if $K \\notin A$.

The efficiency of searching is strictly dictated by the **underlying structure and ordering of the data**. In an unordered collection, the search algorithm has zero prior knowledge; every location is equally likely to contain the target. In an ordered collection, the algorithm can exploit monotonic invariants to prune vast subspaces of memory without inspecting them.

---

## 1. Linear (Sequential) Search Mechanics

Linear search is the simplest search strategy: the algorithm starts at the first element and inspects each successive item until the target key is located or the collection is exhausted.

```java
public static int linearSearch(int[] arr, int target) {
    if (arr == null) return -1;
    for (int i = 0; i < arr.length; i++) {
        if (arr[i] == target) {
            return i; // Target found at index i
        }
    }
    return -1; // Target absent after n comparisons
}
```

### Formal Complexity & Probability Analysis:
1. **Best-Case Scenario**: Target $K$ is at index $0$.
   - Comparisons: Exactly **1**.
   - Asymptotic Bound: **$\\Theta(1)$ Constant Time**.
2. **Worst-Case Scenario**: Target $K$ is at index $n-1$, or is not present in the array.
   - Comparisons: Exactly **$n$**.
   - Asymptotic Bound: **$\\Theta(n)$ Linear Time**.
3. **Average-Case Scenario**:
   - Assume target $K$ is present and equally likely to reside at any index $0 \\le i < n$ with uniform probability $P(i) = \\frac{1}{n}$.
   - The expected number of comparisons $E[C]$ is the probability-weighted sum:
     $$E[C] = \\sum_{i=1}^n i \\cdot P(i) = \\sum_{i=1}^n i \\cdot \\frac{1}{n} = \\frac{1}{n} \\sum_{i=1}^n i$$
   - Applying Gauss's summation $\\sum_{i=1}^n i = \\frac{n(n+1)}{2}$:
     $$E[C] = \\frac{1}{n} \\cdot \\frac{n(n+1)}{2} = \\frac{n+1}{2} \\approx 0.5n$$
   - Conclusion: On average, linear search scans half the array: **$\\Theta(n)$**.

---

### The Sentinel Optimization Technique
In the standard linear search loop, the CPU performs **two comparisons per iteration**:
1. `i < arr.length` (Loop boundary termination check).
2. `arr[i] == target` (Key equality check).

For high-throughput systems, software engineers can eliminate the loop boundary check entirely by placing the target key as a **Sentinel** at the end of the array:

```java
public static int sentinelLinearSearch(int[] arr, int n, int target) {
    int last = arr[n - 1]; // Preserve original last element
    arr[n - 1] = target;   // Install sentinel

    int i = 0;
    while (arr[i] != target) { // ONLY ONE comparison per loop iteration!
        i++;
    }

    arr[n - 1] = last; // Restore original value

    // Verify if match was genuine or hit the sentinel
    if (i < n - 1 || last == target) {
        return i;
    }
    return -1;
}
```
*Performance Gain*: Reduces branching instructions by **$50\\%$**, accelerating linear searches in low-level C and assembly routines.

---

## 2. Binary Search Architecture

If an array is strictly sorted in monotonic order ($A[0] \\le A[1] \\le \\dots \\le A[n-1]$), we can eliminate half the search space with a single comparison using **Binary Search**.

```
Search Target: 77
Sorted Array: [ 11,  22,  33,  44,  55,  66,  77,  88,  99 ]
Indices:         0    1    2    3    4    5    6    7    8
               ▲                   ▲                   ▲
              low                 mid                high
                                (val=55)

Step 1: Compare target (77) with mid (55).
        Since 77 > 55, target CANNOT exist in indices 0..4!
        Prune left half! Set low = mid + 1 (index 5).

Sub-array:                          [ 66,  77,  88,  99 ]
Indices:                               5    6    7    8
                                       ▲    ▲         ▲
                                      low  mid       high
                                         (val=77)

Step 2: Compare target (77) with mid (77).
        Match found! Return index 6 in exactly 2 comparisons!
```

### Recurrence Relation & Complexity Derivation:
At each step, binary search performs $1$ comparison and reduces the problem size from $n$ to $n/2$:
$$T(n) = T\\left(\\frac{n}{2}\\right) + O(1)$$

By the Master Theorem (where $a = 1, b = 2, d = 0 \\implies \\log_b a = \\log_2 1 = 0 == d$):
$$T(n) \\in \\mathbf{O(\\log_2 n)} \\quad \\text{(Logarithmic Time)}$$

#### The Power of Logarithmic Scaling:
- $n = 1,000 \\implies \\log_2(1,000) \\approx 10$ comparisons.
- $n = 1,000,000 \\implies \\log_2(1,000,000) \\approx 20$ comparisons.
- $n = 1,000,000,000 \\implies \\log_2(1,000,000,000) \\approx \\mathbf{30}$ comparisons!
Binary search can find an individual person out of the entire global human population in just **33 comparisons**.

---

## 3. The Historic Midpoint Integer Overflow Bug

In 2006, Google research engineer Joshua Bloch published a famous paper revealing a critical software defect present in `java.util.Arrays.binarySearch()` and standard C/C++ libraries since 1997:

### The Flawed Code:
```java
// LETHAL OVERFLOW DEFECT:
int mid = (low + high) / 2;
```

### Why it Failed in Production:
In Java, `int` is a signed 32-bit two's complement integer with a maximum positive value:
$$\\text{Integer.MAX_VALUE} = 2^{31} - 1 = 2,147,483,647$$

When searching large in-memory datasets (common in big data and search engines where arrays contain $1$ to $2$ billion elements):
1. Suppose `low = 1,500,000,000` and `high = 2,000,000,000`.
2. The mathematical sum `low + high` is `3,500,000,000`.
3. In 32-bit signed arithmetic, `3,500,000,000` overflows into the sign bit, wrapping around to **$-794,967,296$**!
4. The division `(-794,967,296) / 2` yields a negative index: **$-397,483,648$**!
5. When the code attempts `arr[mid]`, the JVM crashes with:
   `java.lang.ArrayIndexOutOfBoundsException: -397483648`!

---

### The Two Enterprise Solutions:

#### Solution 1: Difference Formulation (Mathematical Subtraction)
Instead of adding two potentially large numbers, compute the distance between them:
```java
int mid = low + (high - low) / 2;
```
Because $high \\ge low$, the difference $high - low$ is always non-negative and strictly smaller than $high$, making integer overflow physically impossible.

#### Solution 2: Unsigned Bitwise Right Shift (`>>>`)
In Java, the unsigned right-shift operator `>>>` shifts zeros into the most significant bit, treating the 32 bits as an unsigned binary integer:
```java
int mid = (low + high) >>> 1;
```
Even if `low + high` overflows into negative range, `>>> 1` converts the 32-bit bit pattern into the correct positive midpoint value!

---

## 4. Iterative vs. Recursive Binary Search

```java
package edu.se.dsa.search;

public class BinarySearchEngine {

    // 1. Iterative Implementation: O(1) Auxiliary Space (Optimal)
    public static int binarySearchIterative(int[] arr, int key) {
        int low = 0;
        int high = arr.length - 1;

        while (low <= high) {
            int mid = low + (high - low) / 2; // Overflow-safe!

            if (arr[mid] == key) {
                return mid; // Key located
            } else if (arr[mid] < key) {
                low = mid + 1; // Discard left half
            } else {
                high = mid - 1; // Discard right half
            }
        }
        return -1; // Key absent
    }

    // 2. Recursive Implementation: O(log n) Auxiliary Space on Call Stack
    public static int binarySearchRecursive(int[] arr, int low, int high, int key) {
        if (low > high) return -1; // Base case: search space exhausted

        int mid = low + (high - low) / 2;

        if (arr[mid] == key) {
            return mid;
        } else if (arr[mid] < key) {
            return binarySearchRecursive(arr, mid + 1, high, key);
        } else {
            return binarySearchRecursive(arr, low, mid - 1, key);
        }
    }
}
```

*Architectural Verdict*: In production, **always prefer the iterative implementation**. The recursive approach pushes $\\approx \\log_2 n$ stack frames onto the execution thread, incurring call overhead and wasting memory.

---

## 5. Amortized Cost Analysis: When Should You Sort to Search?

A junior engineer might suggest: *"Since Binary Search is $O(\\log n)$ and Linear Search is $O(n)$, why don't we always sort our arrays first?"*

### The Mathematical Cost Analysis:
Let $n$ be the number of elements, and $k$ be the number of search queries to be performed.

- **Option A (Unsorted Linear Search)**:
  $$\\text{Cost}_A = k \\cdot O(n)$$
- **Option B (Sort First, Then Binary Search)**:
  $$\\text{Cost}_B = \\text{Cost}(\\text{Sort}) + k \\cdot \\text{Cost}(\\text{Binary Search}) = O(n \\log n) + k \\cdot O(\\log n)$$

For Option B to be computationally profitable:
$$\\text{Cost}_B < \\text{Cost}_A \\implies n \\log n + k \\log n < k \\cdot n$$
$$n \\log n < k(n - \\log n) \\implies k > \\frac{n \\log n}{n - \\log n} \\approx \\mathbf{\\log_2 n}$$

### Strategic Takeaways:
1. **Single One-Off Search ($k = 1$)**:
   - Linear Search takes $n$ operations.
   - Sorting + Binary Search takes $n \\log n + \\log n$ operations.
   - **Linear search is drastically faster! Never sort an array for a single search!**
2. **Repeated Batch Searches ($k \\gg \\log n$)**:
   - If a system will execute hundreds or thousands of queries against a static dataset, the $O(n \\log n)$ sorting investment is amortized over all future queries, delivering immense performance gains.

---

## 6. Comprehensive Trade-Off Matrix

| Metric / Dimension | Linear Search | Iterative Binary Search | Recursive Binary Search |
| :--- | :--- | :--- | :--- |
| **Data Precondition** | None (Unsorted data) | **Strictly Sorted** | **Strictly Sorted** |
| **Data Structure Requirement** | Array or Linked List | **Contiguous Array** (Random access) | **Contiguous Array** (Random access) |
| **Best-Case Time** | $\\mathbf{O(1)}$ (First item) | $\\mathbf{O(1)}$ (Midpoint) | $\\mathbf{O(1)}$ (Midpoint) |
| **Worst-Case Time** | $O(n)$ Linear | $\\mathbf{O(\\log n)}$ Logarithmic | $\\mathbf{O(\\log n)}$ Logarithmic |
| **Average-Case Time** | $\\approx 0.5n$ comparisons | $\\approx \\log_2 n$ comparisons | $\\approx \\log_2 n$ comparisons |
| **Auxiliary Memory Space** | $\\mathbf{O(1)}$ In-place | $\\mathbf{O(1)}$ In-place | $O(\\log n)$ Stack frames |
| **Algorithmic Paradigm** | Brute Force Iteration | Divide and Conquer | Divide and Conquer |

---

## 7. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Manual State Space Tracing
**Objective**: Trace the execution of iterative binary search on the following sorted 10-element array for target key $K = 42$.
`arr = [ 5, 12, 18, 25, 33, 42, 57, 68, 81, 95 ]`

Document the exact values of `low`, `high`, `mid`, and `arr[mid]` for every iteration.

<details>
<summary>View Level 1 State Space Execution Trace</summary>

#### Step-by-Step Trace Table:
Target $K = 42$. Array length $n = 10$. Initial bounds: `low = 0`, `high = 9`.

| Iteration | `low` | `high` | `mid = low + (high - low) / 2` | `arr[mid]` | Comparison Result | New Range Action |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | $0$ | $9$ | $0 + (9 - 0) / 2 = \\mathbf{4}$ | `arr[4] = 33` | $42 > 33$ (Target > Mid) | `low = mid + 1 = 5` |
| **2** | $5$ | $9$ | $5 + (9 - 5) / 2 = \\mathbf{7}$ | `arr[7] = 68` | $42 < 68$ (Target < Mid) | `high = mid - 1 = 6` |
| **3** | $5$ | $6$ | $5 + (6 - 5) / 2 = \\mathbf{5}$ | `arr[5] = 42` | $42 == 42$ (Target == Mid) | **MATCH! Return index 5.** |

Total comparisons performed: **3** (compared to 6 comparisons required by linear search).
</details>

---

### Level 2: Scaffolded System Refactoring — Exact Insertion-Point Binary Search
**Objective**: Refactor standard binary search to emulate `java.util.Arrays.binarySearch()`. When a target key is not present, standard binary search returns `-1`, discarding valuable spatial information. Refactor the algorithm to return:
- The exact zero-based index if found.
- If not found, return `-(insertionPoint + 1)`, where `insertionPoint` is the exact index where the key should be inserted to preserve sorted order.

<details>
<summary>View Level 2 Refactored Production Solution</summary>

```java
package edu.se.dsa.search;

public class InsertionPointBinarySearch {

    /**
     * Enhanced Binary Search returning insertion point encoding.
     * If key is found: returns index >= 0.
     * If key is not found: returns -(insertionPoint + 1) < 0.
     */
    public static int searchWithInsertionPoint(int[] arr, int key) {
        int low = 0;
        int high = arr.length - 1;

        while (low <= high) {
            int mid = low + (high - low) / 2;

            if (arr[mid] == key) {
                return mid; // Key found!
            } else if (arr[mid] < key) {
                low = mid + 1;
            } else {
                high = mid - 1;
            }
        }

        // When loop terminates, 'low' holds the EXACT index where 'key' belongs!
        // We encode it as -(low + 1) to distinguish an absent key at index 0 from a found key at index 0.
        return -(low + 1);
    }

    public static void main(String[] args) {
        int[] sortedData = {10, 20, 30, 40, 50};

        int idxFound = searchWithInsertionPoint(sortedData, 30);
        System.out.println("Search 30: index = " + idxFound); // 2

        int idxMissing = searchWithInsertionPoint(sortedData, 25);
        System.out.println("Search 25: code = " + idxMissing); // -3
        int insertionPoint = -idxMissing - 1;
        System.out.println("25 should be inserted at index: " + insertionPoint); // 2
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — Search in a Rotated Sorted Array ($O(\\log n)$)
**Objective**: An array of distinct integers sorted in ascending order was rotated at an unknown pivot index (e.g., `[ 0, 1, 2, 4, 5, 6, 7 ]` might become `[ 4, 5, 6, 7, 0, 1, 2 ]`).
- Design and implement an algorithm to find a target value in **$O(\\log n)$ time**.
- You must not un-rotate the array or perform an $O(n)$ search.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.dsa.search;

public class RotatedSortedArraySearch {

    /**
     * Searches for target in a rotated sorted array in O(log n) time.
     * Core Invariant: At least ONE half of the sub-array (left or right) is ALWAYS sorted!
     */
    public static int searchRotated(int[] nums, int target) {
        if (nums == null || nums.length == 0) return -1;

        int low = 0;
        int high = nums.length - 1;

        while (low <= high) {
            int mid = low + (high - low) / 2;

            if (nums[mid] == target) {
                return mid;
            }

            // Determine which half is normally sorted:
            if (nums[low] <= nums[mid]) {
                // LEFT HALF IS SORTED: [low .. mid]
                if (target >= nums[low] && target < nums[mid]) {
                    high = mid - 1; // Target lies within sorted left half
                } else {
                    low = mid + 1;  // Target must be in right half
                }
            } else {
                // RIGHT HALF IS SORTED: [mid .. high]
                if (target > nums[mid] && target <= nums[high]) {
                    low = mid + 1;  // Target lies within sorted right half
                } else {
                    high = mid - 1; // Target must be in left half
                }
            }
        }

        return -1; // Target not found
    }

    public static void main(String[] args) {
        int[] rotated = {4, 5, 6, 7, 0, 1, 2};
        System.out.println("Find 0: Index = " + searchRotated(rotated, 0)); // 4
        System.out.println("Find 3: Index = " + searchRotated(rotated, 3)); // -1
    }
}
```

#### Architectural Key Insight:
Even after rotation, the array retains structural order: for any arbitrary midpoint, **one half is guaranteed to be strictly sorted**. By verifying whether the target falls within the sorted half's boundaries, the algorithm safely discards the other half, maintaining the $O(\\log n)$ divide-and-conquer envelope!
</details>
