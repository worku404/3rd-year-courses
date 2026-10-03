# Lesson 2 — Hash Tables: Functions, Collisions & Open Hashing

> [!NOTE]
> **Learning Outcomes:**
> - Design and evaluate hash functions using **Division**, **Mid-Square**, and **Folding** methods.
> - Implement **Separate Chaining** (Open Hashing) and prove the $O(1 + \alpha)$ expected search time where $\alpha = n/m$ is the load factor.
> - Implement **Open Addressing** (Closed Hashing) with Linear Probing, Quadratic Probing, and Double Hashing.
> - Explain the **Cluster Formation** problem with linear probing and why Double Hashing is superior.
> - Analyse load factor thresholds and implement table resizing with **Rehashing**.

{{media:mit-hash-video}}

{{media:hash-visual}}

## Executive Summary

Hashing is the dominant $O(1)$ data structure used in production systems — Java's `HashMap`, Python's `dict`, JavaScript's object properties, and database symbol tables all rely on hash tables internally. The key engineering challenge is designing hash functions and collision resolution strategies that maintain $O(1)$ expected performance as the table fills.

---

## 1. Hash Table Architecture

A **hash table** is a pair $(T, h)$ where:
- $T$ is an array of $m$ **buckets** (indexed $0$ to $m-1$).
- $h: U \to \{0, 1, \dots, m-1\}$ is a **hash function** mapping the universe of keys $U$ to bucket indices.

**Goal:** Distribute $n$ keys across $m$ buckets uniformly such that each bucket has $\approx n/m$ entries.

**Load Factor:** $\alpha = n/m$. This controls the trade-off between space and time:
- $\alpha < 0.7$: Open addressing works well.
- $\alpha$ can exceed $1.0$ with Separate Chaining (more keys than buckets is fine — chains get longer).

---

## 2. Hash Function Design (Curriculum Slides 16–17)

### 2.1 Division Method: $h(k) = k \bmod m$
```java
int divisionHash(int key, int m) {
    return key % m; // m should be prime, not close to a power of 2
}
```
- **Good:** Simple, fast.
- **Bad:** $m = 2^p$ would use only the low-order $p$ bits — waste of high bits.
- **Best $m$:** A prime not close to a power of 2. E.g., for 700 slots, use $m = 701$.

### 2.2 Mid-Square Method: $h(k) = \text{middle digits of } k^2$
```java
int midSquareHash(int key, int m) {
    long sq = (long) key * key;
    String s = Long.toString(sq);
    int mid = s.length() / 2;
    int extract = Integer.parseInt(s.substring(Math.max(0, mid-2), mid+2));
    return extract % m;
}
```
- Spreads the influence of all bits of $k$ into the hash.

### 2.3 Folding (Additive): $h(k) = (k_1 + k_2 + \cdots + k_r) \bmod m$
```java
int foldingHash(long key, int partSize, int m) {
    long hash = 0;
    while (key > 0) {
        hash += key % (long)Math.pow(10, partSize);
        key  /= (long)Math.pow(10, partSize);
    }
    return (int)(hash % m);
}
```
- Good for phone numbers, credit card numbers (long integer keys).

### 2.4 Polynomial Rolling Hash (Used by Java String)
$$h(s) = \sum_{i=0}^{L-1} s[i] \cdot 31^{L-1-i} \bmod 2^{32}$$
The multiplier $31$ is prime; $31x = (x << 5) - x$ — a single shift-subtract, extremely fast.

---

## 3. Separate Chaining (Open Hashing)

Each bucket holds a **linked list** of all keys that hash to that bucket. Collisions are handled by appending to the list.

```java
package edu.se.search;

import java.util.LinkedList;

public class HashTableChaining<K, V> {
    private static final int DEFAULT_CAPACITY = 16;
    private LinkedList<Entry<K,V>>[] table;
    private int size;

    @SuppressWarnings("unchecked")
    public HashTableChaining(int m) {
        table = new LinkedList[m];
        for (int i = 0; i < m; i++) table[i] = new LinkedList<>();
    }

    private int hash(K key) {
        return (key.hashCode() & Integer.MAX_VALUE) % table.length;
    }

    public void put(K key, V value) {
        int idx = hash(key);
        for (Entry<K,V> e : table[idx]) {
            if (e.key.equals(key)) { e.value = value; return; } // Update
        }
        table[idx].add(new Entry<>(key, value)); // Insert at tail
        size++;
    }

    public V get(K key) {
        int idx = hash(key);
        for (Entry<K,V> e : table[idx])
            if (e.key.equals(key)) return e.value;
        return null; // Not found
    }

    public boolean remove(K key) {
        int idx = hash(key);
        return table[idx].removeIf(e -> e.key.equals(key));
    }

    private static class Entry<K,V> {
        K key; V value;
        Entry(K k, V v) { key = k; value = v; }
    }
}
```

### 3.1 Expected Performance Analysis (with Simple Uniform Hashing)
**Theorem:** Under Simple Uniform Hashing (each key equally likely to hash to any bucket independently), the expected search time for element `x` is:
- **Unsuccessful search:** $\Theta(1 + \alpha)$ — hash (O(1)) plus traverse $\alpha$ elements on average.
- **Successful search:** $\Theta(1 + \alpha/2) = \Theta(1 + \alpha)$ — on average, half the chain.

If $m = \Omega(n)$, then $\alpha = O(1)$ and all operations are $O(1)$ expected.

---

## 4. Open Addressing (Closed Hashing)

All entries are stored **within the array itself**. On collision, we probe alternative positions using a probe sequence $h(k, 0), h(k, 1), h(k, 2), \ldots$ until an empty slot is found.

### 4.1 Linear Probing
$$h(k, i) = (h'(k) + i) \bmod m$$

```java
package edu.se.search;

public class HashTableLinearProbing<K, V> {
    private Object[] keys;
    private Object[] values;
    private int m, n;

    public HashTableLinearProbing(int m) {
        this.m = m;
        keys = new Object[m];
        values = new Object[m];
    }

    private int hash(K key) {
        return (key.hashCode() & Integer.MAX_VALUE) % m;
    }

    @SuppressWarnings("unchecked")
    public void put(K key, V value) {
        if (n >= m * 0.75) resize(2 * m); // Maintain load factor
        int i = hash(key);
        while (keys[i] != null) {
            if (keys[i].equals(key)) { values[i] = value; return; }
            i = (i + 1) % m;
        }
        keys[i] = key; values[i] = value; n++;
    }

    @SuppressWarnings("unchecked")
    public V get(K key) {
        int i = hash(key);
        while (keys[i] != null) {
            if (keys[i].equals(key)) return (V) values[i];
            i = (i + 1) % m;
        }
        return null;
    }

    private void resize(int newM) {
        HashTableLinearProbing<K, V> temp = new HashTableLinearProbing<>(newM);
        for (int i = 0; i < m; i++)
            if (keys[i] != null) temp.put((K)keys[i], (V)values[i]);
        keys = temp.keys; values = temp.values; m = temp.m;
    }
}
```

> [!WARNING]
> **Primary Clustering**: Linear probing causes long runs of occupied slots (clusters). An element hashing to **any position in a cluster** adds to the cluster's length. Performance degrades from $O(1)$ to $O(n)$ as $\alpha \to 1$.

### 4.2 Double Hashing (Best Open Addressing Strategy)
$$h(k, i) = (h_1(k) + i \cdot h_2(k)) \bmod m$$

```java
// Two independent hash functions
int h1 = key % m;
int h2 = 1 + key % (m - 1); // h2 must be coprime to m

// Probe sequence: h1, h1+h2, h1+2*h2, ... (mod m)
int probe = (h1 + i * h2) % m;
```
- If $m$ is prime, any $h_2 \in [1, m-1]$ generates all $m$ positions.
- **Eliminates clustering** — probe sequences are independent of each other.

---

## 5. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Insert the following keys into a hash table of size $m = 11$ using the **Division method** $h(k) = k \bmod 11$ and **Separate Chaining**: keys = `[22, 33, 3, 73, 85, 26]`.

<details>
<summary>View Level 1 Answer</summary>

| Key | h(k) = k mod 11 | Bucket | Chain |
|-----|-----------------|--------|-------|
| 22 | 0 | 0 | [22] |
| 33 | 0 | 0 | [22, 33] — **collision**, append |
| 3 | 3 | 3 | [3] |
| 73 | 7 | 7 | [73] |
| 85 | 8 | 8 | [85] |
| 26 | 4 | 4 | [26] |

Load factor: $\alpha = 6/11 \approx 0.55$. Expected search: $O(1 + 0.55) = O(1.55)$ — excellent!
</details>

---

### Level 2: Scaffolded Refactoring — LRU Cache using LinkedHashMap
**Problem:** Implement an **LRU Cache** with $O(1)$ `get` and `put` operations using Java's `LinkedHashMap` (a hash map with insertion/access ordering).

<details>
<summary>View LRU Cache Implementation</summary>

```java
package edu.se.search;

import java.util.LinkedHashMap;
import java.util.Map;

public class LRUCache<K, V> {
    private final int capacity;
    private final LinkedHashMap<K, V> cache;

    public LRUCache(int capacity) {
        this.capacity = capacity;
        // accessOrder=true: get() moves entry to tail (most recently used)
        this.cache = new LinkedHashMap<K, V>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<K,V> eldest) {
                return size() > capacity; // Evict LRU (head) when over capacity
            }
        };
    }

    public synchronized V get(K key) {
        return cache.getOrDefault(key, null);
    }

    public synchronized void put(K key, V value) {
        cache.put(key, value);
    }
}
```
</details>

---

### Level 3: Senior Engineering Challenge — Custom Open-Addressed HashMap with Tombstones
**Problem:** Deletion in open-addressed hash tables is non-trivial. A naively deleted slot breaks probe chains. Implement a hash map using **tombstone** markers to correctly support `remove()` while maintaining probe chain integrity.

<details>
<summary>View Tombstone Delete Implementation</summary>

```java
package edu.se.search;

public class TombstoneHashMap<K, V> {
    @SuppressWarnings("unchecked")
    private static final Object TOMBSTONE = new Object();
    private Object[] keys;
    private Object[] values;
    private int m, n;

    public TombstoneHashMap(int m) {
        this.m = m;
        keys = new Object[m];
        values = new Object[m];
    }

    private int hash(K key) { return (key.hashCode() & Integer.MAX_VALUE) % m; }

    @SuppressWarnings("unchecked")
    public void put(K key, V value) {
        int i = hash(key);
        int firstTombstone = -1;
        while (keys[i] != null) {
            if (keys[i] == TOMBSTONE) {
                if (firstTombstone == -1) firstTombstone = i;
            } else if (keys[i].equals(key)) {
                values[i] = value; return; // Update existing
            }
            i = (i + 1) % m;
        }
        // Place at first tombstone (reuse) or first empty slot
        int slot = (firstTombstone != -1) ? firstTombstone : i;
        keys[slot] = key; values[slot] = value; n++;
    }

    @SuppressWarnings("unchecked")
    public V get(K key) {
        int i = hash(key);
        while (keys[i] != null) {
            if (keys[i] != TOMBSTONE && keys[i].equals(key))
                return (V) values[i];
            i = (i + 1) % m;
        }
        return null;
    }

    public boolean remove(K key) {
        int i = hash(key);
        while (keys[i] != null) {
            if (keys[i] != TOMBSTONE && keys[i].equals(key)) {
                keys[i] = TOMBSTONE; // Mark as deleted, do NOT null out!
                values[i] = null;
                n--;
                return true;
            }
            i = (i + 1) % m;
        }
        return false;
    }
}
```
</details>
