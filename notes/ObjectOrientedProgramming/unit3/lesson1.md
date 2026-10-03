# Lesson 1 — Class Anatomy, Object Instantiation & Memory Lifecycle

> [!NOTE]
> **Learning Outcomes:**
> - Distinguish between compile-time **Class Specifications** in Metaspace and runtime **Object Instances** in the Garbage-Collected Heap.
> - Trace the low-level bytecode execution sequence of object allocation (`new`, `dup`, `invokespecial <init>`).
> - Differentiate the memory topology, initialization defaults, and lifecycles of **Local**, **Instance**, and **Static** variables.
> - Master the foundational law of Java parameter passing: **Java is Strictly Pass-by-Value**.
> - Detect and resolve memory leaks caused by **loitering object references** in custom container structures.

{{media:class-video}}

{{media:class-anatomy-visual}}

## Executive Summary & System Context

At the core of object-oriented software engineering is the realization that a **Class** is not an execution artifact; it is an abstract type definition, a structural blueprint, and an invariant contract. At runtime, the Java Virtual Machine instantiates concrete **Objects** from these blueprints, managing their allocation in dynamic heap memory and governing their lifecycles through garbage collection.

Understanding how objects are laid out in memory, how references are manipulated on thread stacks, and how parameters are transferred across method boundaries is the dividing line between junior script coders and senior systems engineers. In enterprise systems processing millions of concurrent banking transactions or microservice events, a miscomprehension of reference semantics or variable lifecycles leads directly to subtle race conditions, silent data corruptions, and memory leaks.

This lesson explores class declarations, the exact bytecode mechanics of the `new` operator, the runtime memory topology of variables, and the absolute reality of Java's pass-by-value evaluation model.

---

## 1. Class Specification vs. Runtime Object Instantiation

In Java, a class serves as a user-defined reference type encapsulating **State** (attributes/fields) and **Behavior** (methods):

```java
package com.aastu.banking;

import java.math.BigDecimal;

public class BankAccount {
    // 1. Instance Fields (State stored in Heap)
    private String accountNumber;
    private BigDecimal balance;

    // 2. Static Field (Shared state stored in Metaspace / Class Object)
    private static BigDecimal baseInterestRate = new BigDecimal("0.07");

    // 3. Constructor (Initialization logic)
    public BankAccount(String accountNumber, BigDecimal initialBalance) {
        this.accountNumber = accountNumber;
        this.balance = initialBalance;
    }

    // 4. Instance Method (Behavior modifying Heap state)
    public void deposit(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Deposit amount must be strictly positive");
        }
        this.balance = this.balance.add(amount);
    }

    public BigDecimal getBalance() {
        return this.balance;
    }
}
```

### The Architectural Separation
- **Class in Metaspace**: When `BankAccount.class` is loaded by the ClassLoader, its bytecode instructions, constant pool, method tables (`vtable`), and static fields are allocated in native Metaspace memory. There is exactly **one** canonical `Class<BankAccount>` definition per ClassLoader.
- **Objects in the Heap**: Executing `new BankAccount("ET-1001", new BigDecimal("5000.00"))` allocates a new, independent 32-byte object payload on the Garbage-Collected Heap.

---

## 2. Bytecode Mechanics of the `new` Operator

How does the JVM physically allocate an object when you write `BankAccount acc = new BankAccount("ET-1001", balance);`?

Let us inspect the disassembled bytecode (`javap -c`):

```text
 0: new           #2      // class com/aastu/banking/BankAccount
 3: dup                   // Duplicate top operand stack item
 4: ldc           #3      // String "ET-1001"
 6: aload_1               // Load local variable 1 (balance)
 7: invokespecial #4      // Method "<init>":(Ljava/lang/String;Ljava/math/BigDecimal;)V
10: astore_2              // Store initialized reference into local variable 2 (acc)
```

### Deconstructing the Three-Step Allocation Pipeline:
1. `new #2`: 
   - The JVM searches Metaspace to determine the size of a `BankAccount` instance.
   - It allocates contiguous bytes in the JVM Heap's **Eden Space** (using Thread-Local Allocation Buffers - TLABs for lock-free memory allocation).
   - It sets up the 12-to-16 byte **Object Header** (Mark Word + Klass Pointer pointing to `BankAccount.class`).
   - It zeroes out all instance fields to their default values (`0`, `false`, `null`).
   - It pushes the raw, uninitialized object reference onto the Operand Stack.
2. `dup`:
   - Duplicates the uninitialized reference on top of the Operand Stack.
   - *Why is this necessary?* The upcoming constructor invocation (`invokespecial`) consumes the reference as the hidden `this` argument. The duplicated reference remains on the stack so it can subsequently be stored into `acc` via `astore_2`!
3. `invokespecial #4 <init>`:
   - Pushes the constructor arguments (`"ET-1001"`, `balance`) onto the stack.
   - Executes the constructor body. This initializes instance fields and executes superclass initializers.
4. `astore_2`:
   - Pops the fully initialized reference from the Operand Stack and stores it into Local Variable Array slot 2 (`acc`).

---

## 3. Variable Scopes & Memory Topology

Java enforces strict lexical scoping and distinct memory lifecycles for variables:

| Variable Type | Memory Location | Default Value? | Lifetime | Concurrency / Thread Safety |
| :--- | :--- | :--- | :--- | :--- |
| **Local Variables** | Thread Stack (Stack Frame Local Variable Array) | **NO** (Must be explicitly initialized before reading; compiler error otherwise!) | Exists only while the enclosing method/block executes | **Intrinsically Thread-Safe** (Each thread possesses its own isolated stack) |
| **Instance Variables** | JVM Heap (Embedded within enclosing object payload) | **YES** (`0`, `0.0`, `false`, `null`) | Bound to the enclosing object's lifetime (until GC reclaimed) | **Thread-Unsafe** (Shared if multiple threads hold a reference to the same object) |
| **Class (Static) Variables** | Metaspace (Stored in the java.lang.Class instance) | **YES** (`0`, `0.0`, `false`, `null`) | Entire lifetime of the defining ClassLoader (JVM process) | **High Concurrency Danger** (Global shared state across all threads) |

### 3.1 The Local Variable Initialization Invariant

```java
public void testScope() {
    int uninitializedVal;
    // System.out.println(uninitializedVal); // COMPILATION ERROR: Variable might not have been initialized!

    BankAccount acc; // Stack reference variable
    // acc.deposit(new BigDecimal("100")); // COMPILATION ERROR: Variable acc might not have been initialized!
}
```
Unlike instance fields on the heap (which the JVM automatically zeroes during `new` allocation for security reasons), local variables reside on stack memory that may contain leftover garbage bit-patterns from previously returned stack frames. To guarantee memory safety, the Java compiler strictly enforces **Definite Assignment Analysis** (JLS §16) on local variables.

---

## 4. The Canonical Principle: Java is Strictly Pass-by-Value

One of the most persistent misconceptions among developers transitioning from C++ or C# to Java is the belief that objects are passed "by reference."

> [!IMPORTANT]
> **Fundamental Law of Java Runtime Semantics**:
> Java is **STRICTLY PASS-BY-VALUE** at all times. There are zero exceptions.
> - When passing a primitive (`int`, `double`): The JVM copies the **primitive value bits**.
> - When passing an object: The JVM copies the **pointer memory address (the reference handle)**. It NEVER passes the object itself, nor does it pass an alias to the caller's stack variable!

### 4.1 Proof 1: The Failing Reference Swap

Consider this classic interview challenge:

```java
public class ReferenceDemonstration {
    public static void swap(BankAccount a, BankAccount b) {
        BankAccount temp = a;
        a = b;
        b = temp;
    }

    public static void main(String[] args) {
        BankAccount acc1 = new BankAccount("ACC-1", new BigDecimal("1000")); // Pointer 0x7FA2
        BankAccount acc2 = new BankAccount("ACC-2", new BigDecimal("2000")); // Pointer 0x9B10

        swap(acc1, acc2);

        System.out.println("acc1: " + acc1.getBalance()); // STILL 1000!
        System.out.println("acc2: " + acc2.getBalance()); // STILL 2000!
    }
}
```

#### Why did the swap fail?
1. In `main()`, `acc1` holds address `0x7FA2` and `acc2` holds address `0x9B10`.
2. When calling `swap(acc1, acc2)`, the JVM pushes copies of these two pointer values into `swap()`'s stack frame local variables `a` and `b`.
3. Inside `swap()`, reassigning `a = b` merely overwrites `swap()`'s local stack slot.
4. When `swap()` returns, its stack frame is popped.
5. In `main()`, the local slots `acc1` and `acc2` remain completely unchanged, still pointing to `0x7FA2` and `0x9B10`!

### 4.2 Proof 2: State Mutation Through Copied References

Now observe what happens when a method dereferences the copied pointer:

```java
public static void creditBonus(BankAccount account, BigDecimal bonus) {
    account.deposit(bonus); // Mutates shared Heap state!
}

public static void main(String[] args) {
    BankAccount myAcc = new BankAccount("ACC-1", new BigDecimal("1000"));
    creditBonus(myAcc, new BigDecimal("250"));
    System.out.println(myAcc.getBalance()); // 1250.00!
}
```

#### Why did this succeed?
The pointer passed to `creditBonus` was a copy of `myAcc`'s address (`0x7FA2`). When `creditBonus` invokes `.deposit()`, the JVM follows that pointer directly to the object located at `0x7FA2` in the Heap and mutates its internal `balance` field. The mutation is visible to `main()` because both `myAcc` and `account` point to the exact same physical heap memory address!

---

## 5. Progressive 3-Tier Interactive Practice

### Level 1: Stack & Heap Reference Tracing
**Challenge**: Trace the state of the JVM Thread Stack and Heap for the following snippet. What is printed?

```java
public class TracingExercise {
    public static void main(String[] args) {
        int val = 50;
        Point p1 = new Point(10, 20);
        Point p2 = p1;

        p2.x = 99;
        modify(p1, val);

        System.out.println("p1.x = " + p1.x + ", val = " + val);
    }

    public static void modify(Point p, int val) {
        val = 500;
        p = new Point(0, 0);
        p.x = 777;
    }
}
```

<details>
<summary>View Level 1 Architectural Trace & Explanation</summary>

**Printed Output**:
```text
p1.x = 99, val = 50
```

**Step-by-Step Memory Tracing**:
1. `Point p1 = new Point(10, 20)`: Allocates `Point` object at heap address `0x100`. `p1` holds `0x100`.
2. `Point p2 = p1`: Copies the pointer `0x100` into `p2`. Both `p1` and `p2` reference the same object.
3. `p2.x = 99`: Dereferences `0x100` and mutates `x` to `99`. Since `p1` shares this object, `p1.x` is now `99`.
4. `modify(p1, val)`:
   - A copy of `0x100` is passed to parameter `p`.
   - A copy of primitive `50` is passed to parameter `val`.
5. Inside `modify()`:
   - `val = 500`: Mutates only `modify()`'s stack frame local variable. `main()`'s `val` remains `50`.
   - `p = new Point(0, 0)`: Allocates a **new** object at heap address `0x200` and reassigns `modify()`'s local reference `p` to `0x200`.
   - `p.x = 777`: Mutates `0x200`.
   - `modify()` returns and its stack frame is popped.
6. In `main()`: `p1` still points to `0x100` (where `x = 99`), and `val` is still `50`.
</details>

---

### Level 2: Scaffolded System Refactoring
**Scenario**: You are auditing a multi-tenant authentication gateway. The existing code uses a public static registry to track authenticated user sessions, creating severe thread-safety bugs and race conditions across concurrent HTTP requests:

```java
// BUGGY PROCEDURAL SESSION REGISTRY
public class SessionManager {
    // Shared public static state: Disastrous in concurrent multi-tenant environments!
    public static String currentUser;
    public static long sessionExpiry;
    public static boolean isAuthenticated;

    public static void login(String user, long ttl) {
        currentUser = user;
        sessionExpiry = System.currentTimeMillis() + ttl;
        isAuthenticated = true;
    }
}
```

**Task**: Refactor `SessionManager` into an encapsulated, immutable domain entity model:
1. Create a `UserSession` domain class encapsulating tenant credentials, expiration timestamps, and permissions.
2. Eliminate all public mutable static fields.
3. Provide factory methods and methods that enforce session validity invariants (`isValid()`).

<details>
<summary>View Level 2 Refactored Production Solution</summary>

```java
package com.aastu.auth;

import java.time.Instant;
import java.util.Objects;
import java.util.Set;

public final class UserSession {

    private final String sessionId;
    private final String username;
    private final Set<String> roles;
    private final Instant expiresAt;

    public UserSession(String sessionId, String username, Set<String> roles, Instant expiresAt) {
        this.sessionId = Objects.requireNonNull(sessionId, "Session ID cannot be null");
        this.username = Objects.requireNonNull(username, "Username cannot be null");
        // Defensive copy of mutable collection to guarantee immutability
        this.roles = Set.copyOf(Objects.requireNonNull(roles, "Roles cannot be null"));
        this.expiresAt = Objects.requireNonNull(expiresAt, "Expiration instant cannot be null");

        if (expiresAt.isBefore(Instant.now())) {
            throw new IllegalArgumentException("Cannot create an already-expired session");
        }
    }

    public boolean isExpired() {
        return Instant.now().isAfter(this.expiresAt);
    }

    public boolean hasRole(String role) {
        return this.roles.contains(role);
    }

    public String getSessionId() {
        return sessionId;
    }

    public String getUsername() {
        return username;
    }

    public Instant getExpiresAt() {
        return expiresAt;
    }

    @Override
    public String toString() {
        return "UserSession[id=" + sessionId + ", user=" + username + ", active=" + !isExpired() + "]";
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge (Loitering Reference Memory Leak)
**Scenario**: You are tasked with profiling a low-latency custom cache stack deployed in an electronic trading gateway. Over several days of continuous operation under heavy load, the service exhausts Heap memory with `java.lang.OutOfMemoryError: Java heap space`.
Heap dump analysis (`jmap -dump:live,format=b,file=heap.hprof <PID>`) reveals that millions of discarded `Order` objects remain retained in memory even though the application popped them hours ago!

Inspect the custom stack implementation:

```java
// DEFECTIVE CUSTOM STACK
public class BoundedStack<T> {
    private Object[] elements;
    private int size = 0;

    public BoundedStack(int capacity) {
        this.elements = new Object[capacity];
    }

    public void push(T item) {
        elements[size++] = item;
    }

    @SuppressWarnings("unchecked")
    public T pop() {
        if (size == 0) throw new IllegalStateException("Stack is empty");
        return (T) elements[--size]; // CATASTROPHIC LOITERING REFERENCE!
    }
}
```

**System Challenge**:
1. Why does `return (T) elements[--size];` prevent the Garbage Collector from freeing popped objects?
2. Explain the concept of **Loitering Object References** (Memory Leaks in managed runtimes).
3. Provide the production fix to eliminate the leak and explain how modern standard collections (e.g. `java.util.ArrayList`) handle element removal.

<details>
<summary>View Level 3 Senior SE Architectural Diagnostic & Resolution</summary>

### 1. Root Cause: Loitering Reference
In managed runtimes like the JVM, Garbage Collection operates via **Reachability Analysis** (tracing object reference graphs from GC Roots such as thread stacks, static variables, and JNI handles).

When `pop()` executes `--size`:
- The internal integer counter `size` decreases.
- From the perspective of the stack abstraction, the element is "gone."
- **However, the internal array slot `elements[size]` STILL holds a live pointer to the popped object in the Heap!**
- Because `elements` itself is reachable from the stack instance, the GC traverses `elements[size]`, considers the popped object live, and cannot reclaim its memory!

This condition is formally known as a **Loitering Reference** (an obsolete reference retained in internal storage).

### 2. Production Fix: Nulling Out Obsolete References
To permit the Garbage Collector to reclaim the popped object, the obsolete array slot **must be explicitly cleared to `null`**:

```java
package com.aastu.collections;

import java.util.Arrays;
import java.util.EmptyStackException;
import java.util.Objects;

public final class SafeBoundedStack<T> {

    private final Object[] elements;
    private int size = 0;

    public SafeBoundedStack(int capacity) {
        if (capacity <= 0) {
            throw new IllegalArgumentException("Capacity must be positive: " + capacity);
        }
        this.elements = new Object[capacity];
    }

    public synchronized void push(T item) {
        Objects.requireNonNull(item, "Cannot push null item");
        if (size == elements.length) {
            throw new IllegalStateException("Stack capacity reached (" + elements.length + ")");
        }
        elements[size++] = item;
    }

    @SuppressWarnings("unchecked")
    public synchronized T pop() {
        if (size == 0) {
            throw new EmptyStackException();
        }
        int index = --size;
        T item = (T) elements[index];
        elements[index] = null; // CRITICAL: Null out reference to enable Garbage Collection!
        return item;
    }

    public synchronized int size() {
        return size;
    }
}
```

*Note*: This exact pattern is implemented in OpenJDK's `java.util.ArrayList`:
```java
// OpenJDK ArrayList.remove(int index):
int numMoved = size - index - 1;
if (numMoved > 0)
    System.arraycopy(elementData, index + 1, elementData, index, numMoved);
elementData[--size] = null; // clear to let GC do its work
```
</details>
