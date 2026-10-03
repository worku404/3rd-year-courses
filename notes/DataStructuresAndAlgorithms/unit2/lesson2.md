# Lesson 2 — Simple Exchange & Selection Sorts: Bubble Sort, Stability & Selection Sort

> [!NOTE]
> **Learning Outcomes:**
> - Classify sorting algorithms across the complete structural taxonomy: Internal vs. External, In-Place, and **Algorithmic Stability**.
> - Implement **Bubble Sort** with inner pass reductions and early-exit adaptive flags to achieve $O(n)$ best-case detection.
> - Formulate the **Write Minimization Invariant** of **Selection Sort** ($\\le n-1$ total memory swaps).
> - Deconstruct why standard Selection Sort inherently violates algorithmic stability using duplicate key traces.
> - Identify specialized hardware domains (embedded Flash/EEPROM microcontrollers) where Selection Sort is engineered for physical durability.

{{media:bubble-video}}

{{media:bubble-visual}}

## Executive Summary & System Context

Sorting is among the most heavily studied problems in computer science. In enterprise applications, data is rarely processed in random order:
- Search engines present results ranked by relevance score.
- Financial ledgers display transactions sorted chronologically.
- Database query planners sort datasets before executing hash joins and merge aggregates.

Formally, given a sequence of $n$ records $\\langle a_0, a_1, \\dots, a_{n-1} \\rangle$, a sorting algorithm produces a permutation $\\langle a'_0, a'_1, \\dots, a'_{n-1} \\rangle$ such that:
$$key(a'_0) \\le key(a'_1) \\le \\dots \\le key(a'_{n-1})$$

Before examining complex divide-and-conquer algorithms, software engineers must master the fundamental quadratic ($O(n^2)$) elementary sorts. These algorithms establish core principles of data movement, in-place memory constraints, and stability guarantees.

---

## 1. The Architectural Taxonomy of Sorting

Every sorting algorithm is classified along four fundamental dimensions:

```
                                  SORTING ALGORITHM TAXONOMY
                                               │
          ┌────────────────────┬───────────────┴───────────────┬────────────────────┐
          ▼                    ▼                               ▼                    ▼
   [ Space Location ]    [ Memory Mode ]             [ Key Comparison ]      [ Stability ]
   ├── Internal          ├── In-Place (O(1) aux)     ├── Comparison-based    ├── Stable
   │   (Fits in RAM)     │   (Modifies array)        │   (Lower: Ω(n log n)) │   (Preserves order)
   └── External          └── Out-of-Place            └── Non-comparison      └── Unstable
       (Disk / Paging)       (Allocates O(n) buffer)     (O(n) Radix/Counting)   (Reorders ties)
```

### The Principle of Algorithmic Stability
> [!IMPORTANT]
> **Definition of Stability**: A sorting algorithm is **Stable** if elements with identical keys retain their original relative ordering after sorting.
> 
> Formally, if $key(A[i]) == key(A[j])$ and $i < j$, then in the sorted array, $A[i]$ must appear before $A[j]$.

#### Why Stability is Critical in Enterprise Software:
Consider an enterprise employee table sorted alphabetically by **Last Name**:
1. `Abera, Kassa   (Sales)`
2. `Bethlehem, Abebe (Engineering)`
3. `Chala, Abebe     (Marketing)`

If an HR manager now sorts this list by **Department**:
- A **Stable Sort** guarantees that within the `Engineering` department, employees remain sorted alphabetically by last name.
- An **Unstable Sort** arbitrary scrambles the ties, destroying the previous sort!

---

## 2. Bubble Sort: Adjacent Exchange Mechanics

Bubble Sort is the archetypal exchange algorithm: it scans the array repeatedly, comparing adjacent pairs of elements and swapping them if they are out of order.

```
Initial Array: [ 5,  1,  4,  2,  8 ]

Pass 1:
[ 5, 1, 4, 2, 8 ] -> 5 > 1? Swap! -> [ 1, 5, 4, 2, 8 ]
[ 1, 5, 4, 2, 8 ] -> 5 > 4? Swap! -> [ 1, 4, 5, 2, 8 ]
[ 1, 4, 5, 2, 8 ] -> 5 > 2? Swap! -> [ 1, 4, 2, 5, 8 ]
[ 1, 4, 2, 5, 8 ] -> 5 > 8? No!   -> [ 1, 4, 2, 5, 8 ]
Result of Pass 1: 8 has "bubbled" to index 4 (its final sorted position)!

Pass 2:
[ 1, 4, 2, 5 | 8 ] -> 1 > 4? No
[ 1, 4, 2, 5 | 8 ] -> 4 > 2? Swap! -> [ 1, 2, 4, 5 | 8 ]
[ 1, 2, 4, 5 | 8 ] -> 4 > 5? No
Result of Pass 2: 5 has "bubbled" to index 3!
```

### Invariant & Pass Reductions:
- At the end of outer pass $i$ (where $i$ ranges from $0$ to $n-2$), the $i$-th largest element is guaranteed to reside in its final sorted position at index $n - 1 - i$.
- Consequently, inner loop comparisons do not need to check already-sorted suffixes: the inner loop boundary shrinks each pass to $n - 1 - i$.

---

### The Adaptive Early-Exit Optimization
In its naive form, Bubble Sort always executes $\\frac{n(n-1)}{2}$ comparisons even if the array is already sorted.
By introducing an adaptive `boolean swapped` flag, the algorithm detects whether any elements were moved during a pass. If zero swaps occurred, the array is already sorted, terminating execution immediately:

```java
package edu.se.dsa.sorting;

public class BubbleSortEngine {

    public static void bubbleSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        int n = arr.length;

        for (int i = 0; i < n - 1; i++) {
            boolean swapped = false; // Reset flag for each pass

            // Inner loop boundary shrinks by i each pass
            for (int j = 0; j < n - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    // Swap adjacent elements
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }

            // ADAPTIVE TERMINATION: Array is fully sorted!
            if (!swapped) {
                break;
            }
        }
    }
}
```

#### Complexity Analysis:
- **Best Case (Already Sorted)**: Inner loop runs once, makes $n-1$ comparisons, detects `swapped == false`, and exits: **$\\Theta(n)$ Linear Time**.
- **Worst Case (Reverse Sorted)**: Performs $\\frac{n(n-1)}{2}$ comparisons and $\\frac{n(n-1)}{2}$ swaps: **$\\Theta(n^2)$ Quadratic Time**.
- **Average Case**: $\\approx \\frac{n^2}{2}$ comparisons and $\\frac{n^2}{4}$ swaps: **$\\Theta(n^2)$**.
- **Stability**: **Stable**. Equal elements ($arr[j] == arr[j+1]$) never trigger the `>` condition, preserving order.

---

## 3. Selection Sort: The Write-Minimizing Architecture

Selection Sort operates on a different fundamental principle: instead of continuously swapping adjacent elements, it partitions the array into a **Sorted Prefix** on the left and an **Unsorted Suffix** on the right.

At each step, it scans the entire unsorted suffix, finds the **minimum element**, and performs **exactly ONE swap** to place it at the boundary:

```
Initial Array: [ 64,  25,  12,  22,  11 ]
Sorted Boundary: | Unsorted: [ 64, 25, 12, 22, 11 ]

Pass 1: Scan unsorted suffix. Minimum is 11 at index 4.
        Swap arr[0] (64) with arr[4] (11):
        [ 11 | 25, 12, 22, 64 ]

Pass 2: Scan from index 1. Minimum is 12 at index 2.
        Swap arr[1] (25) with arr[2] (12):
        [ 11, 12 | 25, 22, 64 ]

Pass 3: Scan from index 2. Minimum is 22 at index 3.
        Swap arr[2] (25) with arr[3] (22):
        [ 11, 12, 22 | 25, 64 ]

Pass 4: Scan from index 3. Minimum is 25 at index 3.
        Swap with itself (no-op).
        [ 11, 12, 22, 25, 64 ] -> SORT COMPLETE!
```

```java
package edu.se.dsa.sorting;

public class SelectionSortEngine {

    public static void selectionSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        int n = arr.length;

        for (int i = 0; i < n - 1; i++) {
            int minIdx = i; // Assume current boundary is minimum

            // Scan unsorted suffix to locate true minimum
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) {
                    minIdx = j; // Update index of minimum
                }
            }

            // Perform exactly ONE swap per outer pass
            if (minIdx != i) {
                int temp = arr[i];
                arr[i] = arr[minIdx];
                arr[minIdx] = temp;
            }
        }
    }
}
```

---

## 4. Stability Violation: Why Selection Sort is Unstable

Unlike Bubble Sort and Insertion Sort, standard Selection Sort is **fundamentally UNSTABLE**.

### The Proof by Counterexample:
Consider an array containing duplicate keys with distinct satellite identities:
`arr = [ 5a,  5b,  2 ]`
- Index 0: `5a`
- Index 1: `5b`
- Index 2: `2`

#### Step-by-Step Execution:
1. `i = 0`: The outer loop scans the entire array to locate the minimum.
2. The minimum element is `2` at index 2.
3. The algorithm swaps `arr[0]` (`5a`) with `arr[2]` (`2`):
   $$\\text{Result: } [ \\mathbf{2}, \\quad \\mathbf{5b}, \\quad \\mathbf{5a} ]$$
4. **ALERT**: In the original array, `5a` appeared **before** `5b`.
5. In the sorted array, `5b` now appears **before** `5a`!
6. **Conclusion**: Because Selection Sort swaps across long distances, jumping over intermediate elements, it **destroys the relative order of duplicate keys**.

---

## 5. Hardware Optimization: Flash & EEPROM Write Minimization

Why does Selection Sort exist in computer science if its time complexity is strictly $\\Theta(n^2)$ and it is unstable?

### The Physical Reality of Non-Volatile Memory:
1. **Flash Memory Physics (NAND Flash / EEPROM)**:
   - Microcontrollers (automotive ECUs, medical implants, IoT sensors) and Solid State Drives store data in floating-gate transistors.
   - Reading from flash memory is practically free and does not degrade hardware.
   - **Writing to flash memory physically degrades the oxide insulation layer**. A typical flash cell can endure only $10,000$ to $100,000$ write cycles before suffering permanent hardware failure!
2. **Data Movement Comparison ($n = 10,000$ records)**:
   - **Bubble Sort**: Performs up to $\\frac{n(n-1)}{2} \\approx \\mathbf{50,000,000\\text{ writes}}$! It will rapidly destroy an EEPROM chip!
   - **Selection Sort**: Performs at most $n - 1 = \\mathbf{9,999\\text{ writes}}$!
3. **Architectural Rule**: In embedded engineering where **memory writes are severely expensive or wear out physical silicon**, Selection Sort is provably superior to all other $O(n^2)$ sorting algorithms.

---

## 6. Comprehensive Trade-Off Matrix

| Metric / Dimension | Bubble Sort (Naive) | Bubble Sort (Adaptive) | Selection Sort |
| :--- | :--- | :--- | :--- |
| **Best-Case Time** | $\\Theta(n^2)$ Quadratic | $\\mathbf{\\Theta(n)}$ Linear | $\\Theta(n^2)$ Quadratic |
| **Worst-Case Time** | $\\Theta(n^2)$ Quadratic | $\\Theta(n^2)$ Quadratic | $\\Theta(n^2)$ Quadratic |
| **Average-Case Time** | $\\Theta(n^2)$ Quadratic | $\\Theta(n^2)$ Quadratic | $\\Theta(n^2)$ Quadratic |
| **Comparisons (All Cases)** | $\\frac{n(n-1)}{2}$ | Best: $n-1$, Worst: $\\frac{n(n-1)}{2}$ | **Always** $\\frac{n(n-1)}{2}$ |
| **Swaps (Writes)** | Up to $\\frac{n(n-1)}{2}$ | Up to $\\frac{n(n-1)}{2}$ | $\\mathbf{\\le n - 1}$ **Minimal** |
| **Auxiliary Space** | $\\mathbf{O(1)}$ In-place | $\\mathbf{O(1)}$ In-place | $\\mathbf{O(1)}$ In-place |
| **Algorithmic Stability** | **STABLE** | **STABLE** | **UNSTABLE** |
| **Adaptability** | Non-Adaptive | **Adaptive** (Fast on sorted data) | Non-Adaptive |

---

## 7. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Tracing Inversions & Swaps
**Objective**: Trace the execution of **Selection Sort** on the following array:
`arr = [ 29, 10, 14, 37, 13 ]`

Document the exact state of the array, the minimum index found, and whether a swap occurred for each of the $n-1$ passes.

<details>
<summary>View Level 1 Execution Trace</summary>

#### Step-by-Step Execution Table:
Array size $n = 5$. Total passes = $n - 1 = 4$.

| Pass `i` | Array State at Start of Pass | Unsorted Suffix | `minIdx` Located | Action & Swap Performed | Array State at End of Pass |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **0** | `[ 29, 10, 14, 37, 13 ]` | `[ 29, 10, 14, 37, 13 ]` | **1** (`val=10`) | Swap `arr[0]` (29) with `arr[1]` (10) | `[ 10, 29, 14, 37, 13 ]` |
| **1** | `[ 10 | 29, 14, 37, 13 ]` | `[ 29, 14, 37, 13 ]` | **4** (`val=13`) | Swap `arr[1]` (29) with `arr[4]` (13) | `[ 10, 13, 14, 37, 29 ]` |
| **2** | `[ 10, 13 | 14, 37, 29 ]` | `[ 14, 37, 29 ]` | **2** (`val=14`) | `minIdx == i` (No swap needed) | `[ 10, 13, 14, 37, 29 ]` |
| **3** | `[ 10, 13, 14 | 37, 29 ]` | `[ 37, 29 ]` | **4** (`val=29`) | Swap `arr[3]` (37) with `arr[4]` (29) | `[ 10, 13, 14, 29, 37 ]` |

- Total Comparisons: $4 + 3 + 2 + 1 = 10$.
- Total Swaps: Exactly **3 swaps** performed!
</details>

---

### Level 2: Scaffolded System Refactoring — Bidirectional Cocktail Shaker Sort
**Objective**: In standard Bubble Sort, large elements move quickly to the end ("rabbits"), but small elements near the end move towards the front very slowly ("turtles", moving only 1 position per pass).
Implement **Cocktail Shaker Sort** (Bidirectional Bubble Sort), which traverses alternately from left-to-right (bubbling the maximum) and right-to-left (sinking the minimum) in each cycle.

<details>
<summary>View Level 2 Complete Production Implementation</summary>

```java
package edu.se.dsa.sorting;

public class CocktailShakerSortEngine {

    /**
     * Bidirectional Bubble Sort (Cocktail Shaker Sort).
     * Eliminates turtle elements by alternating sweep directions.
     */
    public static void cocktailSort(int[] arr) {
        if (arr == null || arr.length < 2) return;

        boolean swapped = true;
        int start = 0;
        int end = arr.length - 1;

        while (swapped) {
            swapped = false;

            // 1. Forward Pass: Bubble largest element to the end
            for (int i = start; i < end; i++) {
                if (arr[i] > arr[i + 1]) {
                    swap(arr, i, i + 1);
                    swapped = true;
                }
            }

            // If nothing moved, array is fully sorted
            if (!swapped) break;

            swapped = false;
            end--; // Shrink upper boundary

            // 2. Backward Pass: Sink smallest element to the beginning
            for (int i = end - 1; i >= start; i--) {
                if (arr[i] > arr[i + 1]) {
                    swap(arr, i, i + 1);
                    swapped = true;
                }
            }

            start++; // Shrink lower boundary
        }
    }

    private static void swap(int[] arr, int i, int j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — Flash-Aware Stable Selection Sort
**Objective**: Standard Selection Sort is unstable because it swaps distant elements.
Design and implement **Stable Selection Sort** in Java:
- The algorithm must locate the minimum element in the unsorted suffix.
- Instead of swapping `arr[i]` with `arr[minIdx]`, it must shift all elements between $i$ and $minIdx - 1$ one position to the right, and place the minimum into index $i$.
- Prove that this variant restores $100\\%$ algorithmic stability while preserving $O(1)$ auxiliary space.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.dsa.sorting;

public class StableSelectionSortEngine {

    /**
     * Stable Selection Sort.
     * Restores algorithmic stability by shifting elements right instead of swapping distant keys.
     * Time Complexity: O(n^2) comparisons, O(n^2) element movements.
     * Auxiliary Space: O(1) in-place.
     */
    public static void stableSelectionSort(int[] arr) {
        if (arr == null || arr.length < 2) return;
        int n = arr.length;

        for (int i = 0; i < n - 1; i++) {
            int minIdx = i;

            // Find minimum element in unsorted suffix
            for (int j = i + 1; j < n; j++) {
                if (arr[j] < arr[minIdx]) {
                    minIdx = j;
                }
            }

            // Restore Stability: Shift elements right instead of jumping swap!
            int minValue = arr[minIdx];
            while (minIdx > i) {
                arr[minIdx] = arr[minIdx - 1]; // Shift element right
                minIdx--;
            }
            arr[i] = minValue; // Insert minimum into vacated slot
        }
    }

    public static void main(String[] args) {
        int[] data = {4, 5, 3, 2, 4, 1};
        stableSelectionSort(data);
        for (int v : data) System.out.print(v + " "); // 1 2 3 4 4 5
    }
}
```

#### Mathematical Proof of Restored Stability:
By shifting all intermediate elements right by one position, the relative order of all keys between $i$ and $minIdx$ is strictly preserved. Since equal elements are never chosen as the new minimum (due to strict `<` comparison), identical keys never cross each other, guaranteeing complete **Algorithmic Stability**!
</details>
