# Lesson 3 — Java HashMap Internals, String Hashing & Production Applications

> [!NOTE]
> **Learning Outcomes:**
> - Trace the internal operations of **Java's HashMap**: hash spreading, bucket treeification at chain length 8, and capacity doubling with rehashing.
> - Implement the **polynomial rolling hash** used by `String.hashCode()` and explain the multiplier choice.
> - Apply hash tables to four real-world domains: compiler symbol tables, LRU caches, distributed hash tables, and cryptographic hashing.
> - Contrast **data structure hashing** (fast, reversible, collision-tolerant) from **cryptographic hashing** (slow, one-way, collision-resistant).

{{media:hashmap-video}}

{{media:hashmap-visual}}

## Executive Summary

This lesson bridges the academic theory of hash tables with the production systems every software engineer encounters: Java's `HashMap`, caching infrastructure, distributed databases, and password security. Understanding the engineering decisions baked into `HashMap` — why it uses bit-masking instead of modulo, why it switches from linked lists to Red-Black Trees at chain length 8, why the load factor is $0.75$ — builds intuition for designing and debugging production systems.

---

## 1. Java HashMap Internal Architecture (Java 8+)

### 1.1 Core Data Structure
```java
// Simplified internal structure
transient Node<K,V>[] table; // The bucket array, size always power-of-2
int size;                     // Number of key-value pairs stored
float loadFactor = 0.75f;    // Threshold for resize
int threshold;                // = capacity * loadFactor
```

### 1.2 The Hash Spreading Step
Java doesn't use `key.hashCode() % capacity` directly. It applies a **hash spreading** step first:
```java
// From JDK source (simplified)
static final int hash(Object key) {
    int h;
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```
This XORs the high 16 bits with the low 16 bits. **Why?** When capacity is a small power of 2, the modulo operation (`& (capacity-1)`) only uses the low-order bits, ignoring the high bits entirely. The spreading step ensures high bits influence the bucket index.

### 1.3 Bit-Masking vs Modulo
Since capacity is always a power of 2 (`capacity = 2^k`):
```java
int bucketIndex = hash & (capacity - 1); // Equivalent to hash % capacity, but WAY faster!
```
A single AND instruction vs an integer division — typically $5\times$ faster on modern CPUs.

### 1.4 Treeification (Java 8 Feature)
When a bucket's linked list exceeds 8 nodes, it converts to a **Red-Black Tree**:
- Linked list bucket: $O(n)$ worst-case search for $n$ keys in bucket.
- Red-Black Tree bucket: $O(\log n)$ search.
- Triggered at `TREEIFY_THRESHOLD = 8`. Reversed at `UNTREEIFY_THRESHOLD = 6`.
- **Why 8?** Probability of 8 elements in one bucket (with good hash function) is $10^{-6}$ — rare but non-zero for adversarial inputs.

### 1.5 Rehashing (Table Resize)
```java
void resize() {
    int newCapacity = oldCapacity * 2;    // Double the size
    Node<K,V>[] newTable = new Node[newCapacity];

    // Re-insert all existing entries (rehash each key)
    for (int i = 0; i < oldCapacity; i++) {
        Node<K,V> e = table[i];
        while (e != null) {
            Node<K,V> next = e.next;
            // Because newCapacity = 2*oldCapacity, new bucket index = oldIndex OR oldIndex+oldCapacity
            int newBucket = (e.hash & newCapacity) == 0 ? i : i + oldCapacity;
            // Prepend to new bucket (O(1))
            e.next = newTable[newBucket];
            newTable[newBucket] = e;
            e = next;
        }
    }
    table = newTable;
}
```
> [!IMPORTANT]
> Rehashing is $O(n)$ total but amortised $O(1)$ per insertion (capacity doubles, so rehashing frequency is $O(\log n)$ times over $n$ insertions, total cost = $n + n/2 + n/4 + \ldots = O(n)$).

---

## 2. String.hashCode() — Polynomial Rolling Hash

```java
// JDK source (simplified)
public int hashCode() {
    int h = 0;
    for (char c : toCharArray()) {
        h = h * 31 + c;
    }
    return h;
}
```

This computes: $h = s[0] \cdot 31^{L-1} + s[1] \cdot 31^{L-2} + \ldots + s[L-1]$

**Why 31?**
1. Prime — avoids patterns in hash distribution.
2. $31 = 2^5 - 1$ — JIT compilers optimise `h * 31` to `(h << 5) - h` (shift + subtract, faster than multiply).
3. Produces good avalanche: small string changes cause large hash changes.

```java
// Efficient Java implementation using JIT-friendly form
public static int stringHash(String s) {
    int h = 0;
    for (int i = 0; i < s.length(); i++) {
        h = (h << 5) - h + s.charAt(i); // = h*31 + c
    }
    return h;
}
```

---

## 3. Real-World Application Domains

### 3.1 Compiler Symbol Tables
Every identifier in source code (`variableName`, `ClassName`, method name) is stored in a symbol table — a hash map from identifier string to `Symbol` record (type, scope, memory address).
```java
Map<String, Symbol> symbolTable = new HashMap<>();
symbolTable.put("x", new Symbol(Type.INT, Scope.LOCAL, offset));
```
Fast $O(1)$ lookup eliminates $O(\log n)$ BST overhead during parsing and type-checking.

### 3.2 LRU Caching (LinkedHashMap Pattern)
```java
// CPU instruction cache, HTTP response cache, browser DNS cache
Map<String, Response> cache = new LinkedHashMap<String, Response>(16, 0.75f, true) {
    protected boolean removeEldestEntry(Map.Entry<String, Response> e) {
        return size() > MAX_SIZE; // Evict LRU when full
    }
};
```

### 3.3 Consistent Hashing for Distributed Systems
**Problem:** A distributed cache has $N$ servers. If we use `server = hash(key) % N`, adding/removing a server invalidates $\approx N/(N+1)$ of all cached keys!

**Consistent Hashing Solution:**
- Map both servers and keys onto a ring of $2^{32}$ positions.
- Each key is served by the first server encountered clockwise on the ring.
- Adding one server invalidates only $1/N$ of keys on average.

```java
// Consistent Hashing ring (simplified)
TreeMap<Integer, String> ring = new TreeMap<>();

void addServer(String serverId) {
    for (int i = 0; i < VIRTUAL_NODES; i++) { // Virtual nodes for better balance
        int hash = hash(serverId + "#" + i);
        ring.put(hash, serverId);
    }
}

String getServer(String key) {
    int hash = hash(key);
    Map.Entry<Integer, String> entry = ring.ceilingEntry(hash);
    return entry != null ? entry.getValue() : ring.firstEntry().getValue(); // Wrap around
}
```
Used by: **Amazon DynamoDB**, **Apache Cassandra**, **Redis Cluster**, **Memcached**.

### 3.4 Cryptographic Hash vs Data-Structure Hash

| Property | Data-Structure Hash | Cryptographic Hash (SHA-256) |
|:---------|:--------------------|:------------------------------|
| **Speed** | Very fast ($O(1)$ ns) | Slow (hundreds of ns) |
| **Reversibility** | Collision-tolerant | One-way (irreversible) |
| **Collision resistance** | Not required | Computationally infeasible |
| **Key length** | 32-bit int | 256-bit fixed digest |
| **Use case** | HashMap buckets | Passwords, blockchain, signatures |

```java
// NEVER store passwords with HashMap's hashCode!
// Use BCrypt (adaptive, salted, slow-by-design):
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
String hash = new BCryptPasswordEncoder(12).encode(rawPassword); // 12 rounds
boolean match = new BCryptPasswordEncoder(12).matches(attempt, hash);
```

---

## 4. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Given a Java `HashMap` with default capacity 16 and load factor 0.75:
1. After how many insertions will the map first rehash?
2. What will the new capacity be after the first rehash?
3. Trace the bucket index for key `"hello"` (hashCode = 99162322) using HashMap's hash spreading formula.

<details>
<summary>View Level 1 Answer</summary>

1. **Threshold = 16 * 0.75 = 12**. Rehash occurs when inserting the 13th element.
2. New capacity = **32**.
3. Hash spreading: `h = 99162322 ^ (99162322 >>> 16) = 99162322 ^ 1513 = 99161019`. Bucket index: `99161019 & (16-1) = 99161019 & 15 = 11`.
</details>

---

### Level 2: Scaffolded Refactoring — Word Frequency Counter
**Problem:** Given a large text file, count the frequency of each unique word in $O(n)$ time using Java HashMap.

<details>
<summary>View Word Frequency Implementation</summary>

```java
package edu.se.search;

import java.io.*;
import java.util.*;

public class WordFrequency {

    public static Map<String, Integer> count(String filename) throws IOException {
        Map<String, Integer> freq = new HashMap<>();

        try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
            String line;
            while ((line = br.readLine()) != null) {
                for (String word : line.toLowerCase().split("\\W+")) {
                    if (!word.isEmpty()) {
                        freq.merge(word, 1, Integer::sum); // O(1) per word
                    }
                }
            }
        }
        return freq;
    }

    /** Top-K frequent words using a min-heap of size k. O(n log k). */
    public static List<String> topK(Map<String, Integer> freq, int k) {
        PriorityQueue<Map.Entry<String,Integer>> heap =
            new PriorityQueue<>(Comparator.comparingInt(Map.Entry::getValue));

        for (Map.Entry<String,Integer> e : freq.entrySet()) {
            heap.offer(e);
            if (heap.size() > k) heap.poll(); // Keep only k largest
        }

        List<String> result = new ArrayList<>();
        while (!heap.isEmpty()) result.add(0, heap.poll().getKey());
        return result;
    }
}
```
</details>

---

### Level 3: Senior Engineering Challenge — Implement Consistent Hashing Ring
**Problem:** Implement a full consistent hashing ring with **virtual nodes** supporting `addServer`, `removeServer`, and `getServer(key)` operations. Use `TreeMap` as the ring backbone.

<details>
<summary>View Consistent Hashing Implementation</summary>

```java
package edu.se.search;

import java.util.TreeMap;
import java.util.Map;
import java.util.HashSet;
import java.util.Set;

public class ConsistentHashRing {
    private final int virtualNodes;
    private final TreeMap<Integer, String> ring = new TreeMap<>();

    public ConsistentHashRing(int virtualNodes) {
        this.virtualNodes = virtualNodes;
    }

    private int hash(String key) {
        // FNV-1a hash (fast, good distribution)
        int h = 0x811c9dc5;
        for (byte b : key.getBytes()) {
            h ^= (b & 0xff);
            h *= 0x01000193;
        }
        return h;
    }

    public void addServer(String server) {
        for (int i = 0; i < virtualNodes; i++) {
            ring.put(hash(server + "#VN" + i), server);
        }
    }

    public void removeServer(String server) {
        for (int i = 0; i < virtualNodes; i++) {
            ring.remove(hash(server + "#VN" + i));
        }
    }

    public String getServer(String key) {
        if (ring.isEmpty()) throw new IllegalStateException("No servers in ring");
        int h = hash(key);
        Map.Entry<Integer, String> entry = ring.ceilingEntry(h);
        // Wrap around to first server if no server clockwise
        return (entry != null ? entry : ring.firstEntry()).getValue();
    }

    public Set<String> getServers() {
        return new HashSet<>(ring.values());
    }
}
```
</details>
