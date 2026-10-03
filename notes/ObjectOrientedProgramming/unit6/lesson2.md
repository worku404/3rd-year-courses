# Lesson 2 — Exception Control Flow: Try-Catch-Finally, Throw/Throws & Clean Resource Management

> [!NOTE]
> **Learning Outcomes:**
> - Master the deterministic execution paths of `try-catch-finally` under normal, exceptional, and returning conditions.
> - Contrast explicit failure creation via `throw` with method contract specification using `throws`.
> - Apply Liskov Substitution rules to method overriding with the `throws` clause.
> - Replace leak-prone legacy nested `finally` blocks with modern **Try-With-Resources** and the `AutoCloseable` protocol.
> - Utilize **Multi-Catch** blocks (`|`) while respecting disjoint type hierarchy constraints.
> - Navigate the trade-offs between defensive validation checks and exceptional signaling in concurrent systems (TOCTOU).

{{media:control-video}}

{{media:control-visual}}

## Executive Summary & System Context

Software systems do not operate in a vacuum of pure CPU calculations; they interact with volatile physical environments—network sockets, disk sectors, relational database connections, and external APIs. When exceptional conditions disrupt execution, the system must guarantee two orthogonal requirements:
1. **Control Flow Redirection**: Immediate suspension of the faulted transaction and transfer of control to an authorized recovery handler.
2. **Deterministic Resource Reclamation**: Guaranteed release of scarce operating system handles (file descriptors, sockets, thread locks) regardless of whether execution succeeded, failed, or returned prematurely.

In Java, this contract is implemented through structured control-flow blocks (`try`, `catch`, `finally`) and modern **Automatic Resource Management (ARM)** via `AutoCloseable`.

---

## 1. Execution Semantics of `try-catch-finally`

The `try-catch-finally` construct provides deterministic execution guarantees across three distinct execution scenarios:

```
               ┌─────────────────────────────┐
               │         try Block           │
               └──────────────┬──────────────┘
                              │
             ┌────────────────┴────────────────┐
             │                                 │
     (No Exception)                   (Exception Thrown)
             │                                 │
             │                        ┌────────▼────────┐
             │                        │   catch Block   │
             │                        └────────┬────────┘
             │                                 │
             └────────────────┬────────────────┘
                              │
               ┌──────────────▼──────────────┐
               │        finally Block        │ <--- ALWAYS EXECUTES!
               └──────────────┬──────────────┘
                              │
               ┌──────────────▼──────────────┐
               │    Downstream Execution     │
               └─────────────────────────────┘
```

### The Three Invariant Execution Paths:
1. **Path A (Normal Completion)**:
   - The `try` block executes completely.
   - All `catch` blocks are bypassed.
   - The `finally` block executes immediately.
   - Execution resumes with statements following the `finally` block.
2. **Path B (Handled Exception)**:
   - The `try` block throws an exception at line $N$. Statements $N+1 \dots$ in the `try` block are skipped.
   - The runtime locates the first matching `catch` block; that `catch` block executes to completion.
   - The `finally` block executes immediately after the `catch` block terminates.
   - Execution resumes normally past the `finally` block.
3. **Path C (Unhandled Exception or Method Return)**:
   - The `try` block executes a `return` statement OR throws an exception not handled by any `catch` block.
   - If returning: The return value is evaluated, pushed to an internal temporary JVM register slot.
   - The `finally` block **executes before the method returns or unwinds to the caller!**

### The Critical "Return in Finally" Anti-Pattern
Never place a `return` or throw an exception inside a `finally` block. A return in `finally` will **swallow and discard** any pending exception thrown in the `try` block and will overwrite any return value computed in the `try` block!

```java
public class FinallyTrap {
    public static int compute() {
        try {
            int x = 10 / 0; // Throws ArithmeticException!
            return 1;
        } finally {
            // CATASTROPHIC ANTI-PATTERN:
            // This return executes unconditionally, SILENTLY SWALLOWING the ArithmeticException!
            return 99; 
        }
    }

    public static void main(String[] args) {
        // Prints 99! The division by zero is completely hidden from the caller!
        System.out.println("Result: " + compute());
    }
}
```

### When Does `finally` NOT Execute?
The JVM guarantees `finally` execution in virtually all circumstances, with only four extreme exceptions:
1. An explicit call to `System.exit(status)` or `Runtime.getRuntime().halt(status)`.
2. The JVM process receives an uncatchable OS kill signal (e.g., `kill -9` or Windows Task Manager termination).
3. Host hardware failure, sudden power loss, or kernel panic.
4. An infinite loop or permanent thread deadlock occurs inside the `try` block before reaching `finally`.

---

## 2. Explicit Signaling: `throw` vs. `throws`

Java clearly delineates between the **imperative action** of raising an error and the **declarative contract** in a method signature.

### The `throw` Keyword (Imperative Action)
The `throw` keyword transfers control out of the current execution path by creating an active exception instance:

```java
public void setDepositAmount(double amount) {
    if (amount <= 0.0) {
        // Imperative: Instantiates and dispatches the exception object
        throw new IllegalArgumentException("Deposit amount must be strictly positive: " + amount);
    }
    this.balance += amount;
}
```

### The `throws` Keyword (Declarative Contract)
The `throws` keyword is part of a method's public API contract. It notifies callers and the Java compiler that this method (or dependencies it calls) may propagate one or more checked exceptions:

```java
public byte[] readSecureConfig(Path path) throws IOException, SecurityException {
    return Files.readAllBytes(path);
}
```

### Subtyping & Method Overriding Rules with `throws`
Under the **Liskov Substitution Principle (LSP)**, a subclass method overriding a superclass method cannot break client expectations:

```
        ┌──────────────────────────────────────────────────────────┐
        │ Superclass: public void save() throws IOException        │
        └────────────────────────────┬─────────────────────────────┘
                                     │
           ┌─────────────────────────┴────────────────────────┐
           ▼                                                  ▼
[ VALID OVERRIDES ]                                  [ INVALID OVERRIDES ]
1. throws IOException (Identical)                    1. throws Exception
2. throws FileNotFoundException (Narrower Subclass)     (Broader superclass! Breaks LSP!)
3. (No throws clause at all! Narrower/Safer)         2. throws SQLException
4. throws RuntimeException (Unchecked)                  (Brand new checked exception!)
```

```java
class StorageService {
    public void persist() throws IOException { /* ... */ }
}

class CloudStorageService extends StorageService {
    // COMPILE ERROR: Cannot throw broader checked Exception!
    // @Override
    // public void persist() throws Exception { ... }

    // COMPILE ERROR: Cannot throw new unrelated checked exception!
    // @Override
    // public void persist() throws SQLException { ... }

    // VALID: Narrower checked exception (FileNotFoundException is-a IOException)
    @Override
    public void persist() throws FileNotFoundException { /* ... */ }
}
```

---

## 3. Modern Resource Management: Try-With-Resources & `AutoCloseable`

Prior to Java 7, releasing I/O resources safely was notoriously error-prone, requiring deeply nested, defensive `finally` blocks.

### The Legacy Anti-Pattern (Leak Hazard)
```java
// LEGACY JAVA 6 NIGHTMARE:
InputStream in = null;
OutputStream out = null;
try {
    in = new FileInputStream("source.dat");
    out = new FileOutputStream("dest.dat");
    in.transferTo(out);
} finally {
    // If in.close() throws an IOException, out.close() is NEVER REACHED! Leak occurs!
    try {
        if (in != null) in.close();
    } catch (IOException e) { /* logged */ }

    try {
        if (out != null) out.close();
    } catch (IOException e) { /* logged */ }
}
```

### Modern Try-With-Resources (ARM)
Introduced in Java 7, **Try-With-Resources** guarantees that every resource declared in the resource specification header is closed deterministically at block exit:

```java
public void copyFile(String src, String dst) throws IOException {
    // Resources declared in parentheses; auto-closed at end of block
    try (InputStream in = new FileInputStream(src);
         OutputStream out = new FileOutputStream(dst)) {
        
        in.transferTo(out);
    } // in and out are closed HERE, in REVERSE order of declaration!
}
```

### The `java.lang.AutoCloseable` Contract
Any class whose instances are managed by try-with-resources must implement the `AutoCloseable` interface:

```java
package java.lang;

public interface AutoCloseable {
    /**
     * Closes this resource, relinquishing underlying resources.
     * Throws Exception rather than IOException to support arbitrary domain resources.
     */
    void close() throws Exception;
}
```

> [!TIP]
> **Idempotent `close()` Convention**: The Java specification strongly recommends (though does not strictly enforce) that `close()` implementations be **idempotent**—calling `close()` a second time on an already closed resource should be a safe no-op.

### Exception Suppression Mechanics
What happens if the `try` block throws an exception (`Ex1: Disk Corrupt`), and when closing the file, `close()` *also* throws an exception (`Ex2: Lock Release Failed`)?
- In legacy code, `Ex2` in `finally` would completely overwrite and erase `Ex1`, hiding the original root cause from developers!
- In **Try-With-Resources**, the primary exception (`Ex1`) is propagated to the caller, while `Ex2` is attached to `Ex1` as a **Suppressed Exception**!

```java
try {
    processData();
} catch (IOException primaryEx) {
    System.err.println("Primary error: " + primaryEx.getMessage());
    
    // Inspect suppressed exceptions that occurred during auto-closing:
    for (Throwable suppressed : primaryEx.getSuppressed()) {
        System.err.println("  [Suppressed during close]: " + suppressed.getMessage());
    }
}
```

---

## 4. Multi-Catch Syntax (`|`) & Disjoint Type Constraints

Java 7 introduced **Multi-Catch** syntax to eliminate repetitive, identical catch blocks:

```java
// CLEAN & CONCISE:
try {
    executeRemoteRpc();
} catch (IOException | SQLException | InterruptedException e) {
    // 'e' is implicitly final! Cannot reassign: e = new Exception();
    logger.error("Transaction failed across external boundary", e);
    rollback();
}
```

### The Disjoint Type Constraint
The compiler requires that types listed in a multi-catch expression be **disjoint** (i.e., not related by inheritance):

```java
// COMPILE ERROR:
try {
    readFile();
} catch (FileNotFoundException | IOException e) {
    // COMPILE ERROR: The exception FileNotFoundException is already 
    // caught by the alternative IOException!
}
```

---

## 5. Defensive Validation vs. Exceptional Signaling (TOCTOU)

In high-concurrency systems, developers often debate whether to use **defensive pre-checks** or **exception handling**.

```java
// Approach A: Defensive Pre-check (EAFP vs LBYL)
if (file.exists()) {
    // RACE CONDITION: Another process might delete the file right HERE!
    readFile(file); 
}
```

### The TOCTOU Race Condition
In concurrent or multi-process environments, **Time-of-Check to Time-of-Use (TOCTOU)** creates subtle bugs. Checking `file.exists()` before opening creates a window where state can change.
- In distributed environments, relying solely on defensive checks is impossible.
- **Rule of Thumb**: Perform pre-validation on internal invariant state (e.g., non-null arguments, valid ranges). However, when interacting with external resources (disks, networks, databases), **always embrace structured exception handling**.

---

## 6. Comprehensive Trade-Off Matrix

| Dimension | Legacy try-finally | Try-With-Resources | Defensive Validation | Multi-Catch (`\|`) |
| :--- | :--- | :--- | :--- | :--- |
| **Boilerplate Volume** | Extreme (Nested try-catch) | Minimal (Single header line) | Moderate (Branching checks) | Low (Consolidates handlers) |
| **Leak Safety** | Low (Vulnerable to early exit) | 100% Guaranteed | N/A | High |
| **Exception Preservation** | Secondary exception masks root | Primary preserved; secondary suppressed | Avoids exception overhead | Preserves stack trace |
| **Concurrency Safety** | Manual synchronization | Deterministic thread exit | Vulnerable to TOCTOU race | Thread-safe |
| **Closure Order** | Manual (Usually forward) | Strict reverse declaration order | N/A | N/A |

---

## 7. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Tracing Complex Control Flow
**Objective**: Predict the exact console output and return value of the following method.

```java
public class FlowQuiz {
    public static void main(String[] args) {
        System.out.println("Returned: " + executeFlow());
    }

    public static String executeFlow() {
        StringBuilder log = new StringBuilder("Start");
        try {
            log.append(" -> Try");
            if (true) throw new IllegalStateException("Fault");
            log.append(" -> Unreachable");
            return log.toString();
        } catch (IllegalStateException e) {
            log.append(" -> Catch");
            return log.toString(); // Evaluates current log string!
        } finally {
            log.append(" -> Finally");
            System.out.println("Inside Finally: " + log.toString());
        }
    }
}
```

<details>
<summary>View Level 1 Analysis & Exact Output</summary>

#### Console Output:
```text
Inside Finally: Start -> Try -> Catch -> Finally
Returned: Start -> Try -> Catch
```

#### Step-by-Step Execution Walkthrough:
1. `log` initialized with `"Start"`.
2. Inside `try`: appends `" -> Try"`.
3. `throw new IllegalStateException("Fault")` triggers. `" -> Unreachable"` is bypassed.
4. `catch (IllegalStateException e)` matches: appends `" -> Catch"`.
5. The `catch` block encounters `return log.toString();`. The return value `"Start -> Try -> Catch"` is evaluated and stored in an internal JVM temporary return register.
6. Before returning, the `finally` block runs:
   - Appends `" -> Finally"` to `log`.
   - Prints `"Inside Finally: Start -> Try -> Catch -> Finally"`.
7. Because the `finally` block did NOT contain a `return` statement, the method finishes returning the previously held register value: `"Start -> Try -> Catch"`!
</details>

---

### Level 2: Scaffolded System Refactoring — Multi-Resource Export Pipeline
**Objective**: Refactor an unsafe, legacy JDBC-to-CSV data exporter with nested `finally` blocks into clean, robust Try-With-Resources.

#### Legacy Fragile Code:
```java
public class LegacyReportExporter {
    public void exportData(Connection conn, String query, String outPath) throws Exception {
        Statement stmt = null;
        ResultSet rs = null;
        BufferedWriter writer = null;
        try {
            stmt = conn.createStatement();
            rs = stmt.executeQuery(query);
            writer = new BufferedWriter(new FileWriter(outPath));
            while (rs.next()) {
                writer.write(rs.getString(1) + "," + rs.getDouble(2));
                writer.newLine();
            }
        } finally {
            if (rs != null) rs.close();
            if (stmt != null) stmt.close();
            if (writer != null) writer.close();
        }
    }
}
```

<details>
<summary>View Level 2 Refactored Solution (Try-With-Resources)</summary>

```java
import java.io.*;
import java.nio.file.*;
import java.sql.*;

public class ModernReportExporter {
    public void exportData(Connection conn, String query, Path outPath) throws SQLException, IOException {
        // All three resources are managed in strict reverse order of closure:
        // writer closed first, then rs, then stmt!
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query);
             BufferedWriter writer = Files.newBufferedWriter(outPath)) {
            
            while (rs.next()) {
                writer.write(rs.getString(1) + "," + rs.getDouble(2));
                writer.newLine();
            }
            writer.flush();
        } // Guaranteed deterministic closure of all 3 resources even if disk fills or query fails!
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — Distributed Lock Lease with AutoCloseable
**Objective**: In distributed systems, failure to release distributed locks (e.g., Redis or ZooKeeper locks) leads to system-wide deadlock. Design an `AutoCloseable` distributed lock lease wrapper that guarantees lock release on block exit and prevents premature expiration.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.concurrency;

import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;

// 1. Domain Lock Exception
public class DistributedLockException extends RuntimeException {
    public DistributedLockException(String message) {
        super(message);
    }
}

// 2. Mock Distributed Lock Backend (e.g., Redis / Consul)
public interface DistributedLockClient {
    boolean acquire(String lockKey, String ownerToken, long ttlMillis);
    boolean release(String lockKey, String ownerToken);
}

// 3. AutoCloseable Lock Lease Wrapper
public final class LockLease implements AutoCloseable {
    private final DistributedLockClient client;
    private final String lockKey;
    private final String ownerToken;
    private final AtomicBoolean isReleased = new AtomicBoolean(false);

    private LockLease(DistributedLockClient client, String lockKey, String ownerToken) {
        this.client = client;
        this.lockKey = lockKey;
        this.ownerToken = ownerToken;
    }

    public static LockLease acquire(DistributedLockClient client, String lockKey, long ttlMillis) {
        String token = UUID.randomUUID().toString();
        boolean acquired = client.acquire(lockKey, token, ttlMillis);
        if (!acquired) {
            throw new DistributedLockException("Failed to acquire distributed lock for key: " + lockKey);
        }
        return new LockLease(client, lockKey, token);
    }

    @Override
    public void close() {
        // Enforce Idempotent Release: only release once
        if (isReleased.compareAndSet(false, true)) {
            boolean released = client.release(lockKey, ownerToken);
            if (!released) {
                System.err.printf("[CRITICAL] Lock lease for '%s' had expired or was stolen!%n", lockKey);
            } else {
                System.out.printf("[LOCK RELEASED] Successfully relinquished lock '%s'%n", lockKey);
            }
        }
    }

    public static void main(String[] args) {
        DistributedLockClient mockClient = new DistributedLockClient() {
            @Override
            public boolean acquire(String key, String token, long ttl) {
                System.out.printf("[LOCK ACQUIRED] Key='%s' Token='%s' TTL=%dms%n", key, token, ttl);
                return true;
            }

            @Override
            public boolean release(String key, String token) {
                return true;
            }
        };

        // Usage in Try-With-Resources: Deadlock impossible!
        try (LockLease lease = LockLease.acquire(mockClient, "order-settlement-lock", 5000)) {
            System.out.println("Executing mission-critical database ledger settlement...");
            // Simulate work
            Thread.sleep(100);
        } catch (Exception e) {
            System.err.println("Ledger processing failed: " + e.getMessage());
        } // lease.close() is guaranteed to execute here!
    }
}
```

#### Architectural Highlights:
- **Zero Deadlocks**: The lock is guaranteed to be released even if a runtime exception or unhandled error occurs within the business block.
- **Ownership Verification Token**: The lock stores a unique UUID token so that a worker cannot accidentally release another node's lock if its own lease expired.
- **Idempotent Atomic Release**: `AtomicBoolean.compareAndSet` guarantees thread-safe, single-execution release semantics.
</details>
