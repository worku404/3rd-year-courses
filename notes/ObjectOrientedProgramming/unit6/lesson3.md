# Lesson 3 — Enterprise Exception Architecture: Custom Domain Exceptions, Chaining & Anti-Patterns

> [!NOTE]
> **Learning Outcomes:**
> - Architect domain-specific exception hierarchies using Domain-Driven Design (DDD) principles.
> - Implement the four canonical `Throwable` constructor overloads to ensure robust telemetry and diagnostic tracking.
> - Master **Root Cause Chaining** to preserve low-level infrastructure stack traces without leaking implementation details.
> - Execute **Exception Translation** across Clean Architecture boundaries (translating SQL/RPC errors into RFC 7807 Web APIs).
> - Identify and eliminate lethal enterprise anti-patterns: silent swallowing, duplicate logging, and control flow through exceptions.
> - Engineer a resilient **Circuit Breaker** pattern to protect distributed systems from cascading microservice failures.

{{media:custom-video}}

{{media:custom-visual}}

## Executive Summary & System Context

Standard Java exceptions (`IllegalArgumentException`, `NullPointerException`, `IOException`) communicate technical anomalies from the perspective of the JVM runtime or the host operating system. However, in enterprise software systems, applications fail primarily due to **domain contract violations**—an account has insufficient balance, an order has expired, an inventory reservation failed, or a user lacks administrative authorization.

Modeling business failures with generic runtime exceptions (`throw new RuntimeException("No money")`) severely degrades system maintainability:
1. Calling layers cannot differentiate between a bug in code and an anticipated business constraint.
2. Error logs lack contextual metadata (user IDs, transaction timestamps, correlation IDs).
3. Technical implementation details (database table names, driver versions, SQL syntax errors) bleed through architectural layers into user-facing presentation tiers.

To build fault-tolerant, maintainable software, senior engineers design **Custom Domain Exceptions**, strictly maintain **Root Cause Chains**, and enforce **Exception Translation** across architectural boundaries.

---

## 1. Domain-Driven Design: Crafting Custom Exception Hierarchies

### Checked vs. Unchecked for Custom Exceptions
When designing custom exceptions, the primary architectural decision is whether to extend `Exception` (checked) or `RuntimeException` (unchecked):

```
                       ┌────────────────────────────────────────┐
                       │     Base Domain Exception (Abstract)   │
                       │     extends RuntimeException           │
                       └───────────────────┬────────────────────┘
                                           │
             ┌─────────────────────────────┼─────────────────────────────┐
             │                             │                             │
┌────────────▼────────────┐   ┌────────────▼────────────┐   ┌────────────▼────────────┐
│ EntityNotFoundException │   │ InvariantBreachException│   │ PaymentFailedException  │
└─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘
```

#### Modern Senior SE Invariant: Prefer Unchecked Domain Exceptions
- **Domain Invariant Violations**: Should almost universally extend `java.lang.RuntimeException`. Business constraints (e.g., overdrafting an account) represent an invalid operation that cannot proceed; polluting every service method with `throws InsufficientFundsException` creates brittle, tightly coupled code.
- **Recoverable External Contracts**: Subclass `java.lang.Exception` only when the caller is strictly expected to execute an immediate, programmatic alternate recovery pathway (e.g., prompting the user to re-enter a security PIN).

---

### The Four Canonical Constructors of `Throwable`
Any production custom exception must implement all four standard constructor overloads to support diagnostic logging and causal chaining:

```java
package edu.se.domain.exceptions;

public abstract class BaseDomainException extends RuntimeException {
    
    // 1. Default No-Arg Constructor
    public BaseDomainException() {
        super();
    }

    // 2. Message-Only Constructor (Most Common)
    public BaseDomainException(String message) {
        super(message);
    }

    // 3. Message and Root Cause Constructor (CRITICAL for Chaining)
    public BaseDomainException(String message, Throwable cause) {
        super(message, cause);
    }

    // 4. Cause-Only Constructor
    public BaseDomainException(Throwable cause) {
        super(cause);
    }
}
```

### Enriching Exceptions with Domain Metadata
Unlike standard exceptions which only carry an arbitrary string message, enterprise custom exceptions should encapsulate structured domain fields:

```java
public class InsufficientLiquidityException extends BaseDomainException {
    private final String accountId;
    private final double attemptedAmount;
    private final double availableBalance;

    public InsufficientLiquidityException(String accountId, double attemptedAmount, double availableBalance) {
        super(String.format("Account '%s' cannot withdraw $%.2f (Available: $%.2f)", 
            accountId, attemptedAmount, availableBalance));
        this.accountId = accountId;
        this.attemptedAmount = attemptedAmount;
        this.availableBalance = availableBalance;
    }

    public String getAccountId() { return accountId; }
    public double getAttemptedAmount() { return attemptedAmount; }
    public double getAvailableBalance() { return availableBalance; }
}
```

---

## 2. Root Cause Diagnostics & Exception Chaining

When low-level infrastructure code fails (e.g., a database driver drops a socket connection), higher-level domain code must catch the low-level exception and wrap it in a domain-meaningful exception. However, **the original technical exception must never be lost!**

### The Mechanism of Exception Chaining
Exception chaining links an antecedent failure (the "cause") to a newly created exception via `initCause()` or the `(message, cause)` constructor.

```java
// REPOSITORY LAYER: Translating SQLException to Domain Exception
public UserAccount findAccountById(String id) {
    try {
        return jdbcTemplate.queryForObject("SELECT * FROM accounts WHERE id = ?", id);
    } catch (java.sql.SQLException sqlEx) {
        // CATASTROPHIC BUG: Stripping the cause!
        // throw new AccountPersistenceException(sqlEx.getMessage()); // NEVER DO THIS!

        // CORRECT: Preserving the root cause!
        throw new AccountPersistenceException("Failed to load account from DB for id: " + id, sqlEx);
    }
}
```

```
========================================================================================
                      ROOT CAUSE CHAINING DIAGRAM
========================================================================================
[ AccountPersistenceException: "Failed to load account from DB for id: 104" ]
   │
   └───> Cause Pointer (e.getCause())
            │
            ▼
         [ java.sql.SQLException: "Connection timeout after 3000ms" ]
            │
            └───> Cause Pointer (e.getCause())
                     │
                     ▼
                  [ java.net.SocketTimeoutException: "Read timed out" ]
========================================================================================
```

### Extracting Root Causes in Production Telemetry
When analyzing enterprise logs, utilities traverse the cause graph to pinpoint the physical root cause:

```java
public static Throwable getRootCause(Throwable throwable) {
    Objects.requireNonNull(throwable);
    Throwable rootCause = throwable;
    while (rootCause.getCause() != null && rootCause.getCause() != rootCause) {
        rootCause = rootCause.getCause();
    }
    return rootCause;
}
```

---

## 3. Clean Architecture: Exception Translation Across Boundaries

In Clean Architecture (Hexagonal / Ports-and-Adapters), inner domain layers must remain completely agnostic of outer infrastructure details.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        API / Presentation Layer                        │
│            Translates Domain Exception to HTTP 404 / 409 / 502         │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│                       Service / Application Layer                      │
│             Catches Repo error; throws OrderProcessingException        │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│                     Infrastructure / Database Layer                    │
│             Throws low-level SQLException / SocketTimeoutException     │
└────────────────────────────────────────────────────────────────────────┘
```

### The Inversion Rule:
1. **Never leak infrastructure types to callers**: If a REST Controller catches a raw `com.mysql.cj.jdbc.exceptions.MySQLTimeoutException`, your system is tightly coupled to MySQL!
2. **Translate at the boundary**: The Database Adapter intercepts `SQLException` and translates it into an application-level `RepositoryException` before bubbling up to services.
3. **Map to Standard Web Protocols (RFC 7807)**: At the API boundary, global exception controllers map domain exceptions into standardized JSON problem details:

```json
{
  "type": "https://api.aastu.edu.et/errors/insufficient-liquidity",
  "title": "Insufficient Funds",
  "status": 422,
  "detail": "Account 'acc_9021' cannot withdraw $500.00 (Available: $120.50)",
  "instance": "/v1/transfers/tx_48912"
}
```

---

## 4. Lethal Enterprise Anti-Patterns to Eliminate

### 1. Swallowing Exceptions (The Black Hole)
```java
// LETHAL ANTI-PATTERN:
try {
    paymentGateway.charge(card, amount);
} catch (Exception e) {
    // Empty catch block: The payment failed, but the caller assumes it succeeded!
}
```
**Consequence**: Silent data corruption, missing financial ledgers, and catastrophic audit failures.

---

### 2. Catching `java.lang.Throwable`
```java
// LETHAL ANTI-PATTERN:
try {
    processTask();
} catch (Throwable t) {
    logger.warn("Task failed, continuing...");
}
```
**Consequence**: `Throwable` catches `OutOfMemoryError`, `StackOverflowError`, and `ThreadDeath`. By swallowing an `OutOfMemoryError`, the application keeps a corrupted JVM alive in an unpredictable, half-dead zombie state!

---

### 3. Log and Re-throw (The Cascade Explosion)
```java
// ANTI-PATTERN:
try {
    dao.save(entity);
} catch (SQLException e) {
    logger.error("Database save failed", e); // Logged at Layer 1
    throw e;                                // Logged AGAIN at Layer 2, Layer 3...
}
```
**Consequence**: A single failure generates 15 identical multi-page stack traces in production logs, flooding log aggregation pipelines (Elasticsearch/Datadog) and confusing on-call engineers.
**Golden Rule**: **Either handle and log, OR wrap and re-throw. Never do both!**

---

### 4. Control Flow via Exceptions
```java
// ANTI-PATTERN: Using exception handling for normal loop termination
try {
    int i = 0;
    while (true) {
        processItem(list.get(i++));
    }
} catch (IndexOutOfBoundsException e) {
    // Normal termination: HORRIBLE PERFORMANCE!
}
```
**Consequence**: Halts JIT compiler optimizations, forces JVM stack frame allocations, and runs 100x to 1000x slower than a standard `for (Item item : list)` loop.

---

## 5. Comprehensive Trade-Off Matrix

| Strategy / Pattern | Maintainability | Production Telemetry | Runtime Performance | Architectural Coupling |
| :--- | :--- | :--- | :--- | :--- |
| **Generic RuntimeException** | Extremely Poor | Poor (Message string only) | Standard | Low |
| **Domain-Specific Exceptions** | High | Excellent (Structured fields) | Standard | Decoupled |
| **Chained Exceptions (`initCause`)** | Optimal | Flawless (Full trace graph) | Standard | Preserves debuggability |
| **Log and Re-throw** | Terrible | Log pollution / spam | Wastes I/O | High |
| **Flow-Control via Exceptions** | Unacceptable | Misleading stack traces | Catastrophic ($100	imes$ slower) | Spaghetti code |

---

## 6. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Root Cause Inspection
**Objective**: Trace the chained exception structure and predict the output of the diagnostic method.

```java
public class ChainedExceptionTrace {
    public static void main(String[] args) {
        try {
            orchestrate();
        } catch (Exception e) {
            printChain(e);
        }
    }

    static void orchestrate() {
        try {
            subSystemA();
        } catch (IllegalStateException e) {
            throw new IllegalArgumentException("Layer A Configuration Invalid", e);
        }
    }

    static void subSystemA() {
        try {
            subSystemB();
        } catch (NullPointerException e) {
            throw new IllegalStateException("Layer B Returned Null Handle", e);
        }
    }

    static void subSystemB() {
        String ptr = null;
        ptr.length(); // Throws NullPointerException
    }

    static void printChain(Throwable t) {
        int depth = 1;
        while (t != null) {
            System.out.printf("[%d] %s: %s%n", depth++, t.getClass().getSimpleName(), t.getMessage());
            t = t.getCause();
        }
    }
}
```

<details>
<summary>View Level 1 Diagnostic Chain Output</summary>

#### Exact Console Output:
```text
[1] IllegalArgumentException: Layer A Configuration Invalid
[2] IllegalStateException: Layer B Returned Null Handle
[3] NullPointerException: Cannot invoke "String.length()" because "ptr" is null
```

#### Architectural Breakdown:
1. `subSystemB()` triggers root fault: `NullPointerException`.
2. `subSystemA()` catches NPE and wraps it inside an `IllegalStateException`, passing the NPE as `cause`.
3. `orchestrate()` catches `IllegalStateException` and wraps it inside an `IllegalArgumentException`, passing the ISE as `cause`.
4. `printChain()` traverses the linked pointer list (`t = t.getCause()`) from outermost envelope down to the underlying root cause!
</details>

---

### Level 2: Scaffolded System Refactoring — Clean Exception Translation
**Objective**: Refactor an e-commerce checkout service that leaks raw `SQLException` and vendor-specific payment errors into a clean, decoupled domain exception architecture.

#### Legacy Fragile Code:
```java
public class LeakyOrderService {
    public void checkout(String cartId, String cardNum) throws SQLException, Exception {
        // Leaking database errors and payment gateway errors directly to callers
        Order order = db.loadOrder(cartId); 
        PaymentResult res = stripeGateway.charge(cardNum, order.getTotal());
        if (!res.isSuccess()) {
            throw new Exception("Stripe Error Code: " + res.getErrorCode());
        }
        db.saveOrder(order);
    }
}
```

<details>
<summary>View Level 2 Refactored Solution (Clean Architecture Translation)</summary>

```java
// 1. Domain Exceptions
public class OrderCheckoutException extends RuntimeException {
    public OrderCheckoutException(String message, Throwable cause) {
        super(message, cause);
    }
}

public class PaymentDeclinedException extends RuntimeException {
    private final String declineCode;
    public PaymentDeclinedException(String declineCode, String message) {
        super(message);
        this.declineCode = declineCode;
    }
    public String getDeclineCode() { return declineCode; }
}

// 2. Refactored Clean Service
public class ModernOrderService {
    public void checkout(String cartId, String cardNum) {
        Order order;
        try {
            order = db.loadOrder(cartId);
        } catch (SQLException e) {
            throw new OrderCheckoutException("Failed to access order repository for cart: " + cartId, e);
        }

        PaymentResult res;
        try {
            res = stripeGateway.charge(cardNum, order.getTotal());
        } catch (Exception e) {
            throw new OrderCheckoutException("Payment gateway unreachable during checkout", e);
        }

        if (!res.isSuccess()) {
            // Business constraint breach: strongly typed domain exception
            throw new PaymentDeclinedException(res.getErrorCode(), "Card declined: " + res.getErrorMessage());
        }

        try {
            db.saveOrder(order);
        } catch (SQLException e) {
            throw new OrderCheckoutException("Failed to persist confirmed order state", e);
        }
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — Resilient Circuit Breaker Engine
**Objective**: In microservice architectures, when a remote service fails, repeatedly throwing exceptions overwhelms the network and exhausts thread pools.

Architect a production-grade **Circuit Breaker** with three states:
1. `CLOSED`: Normal operation; requests pass through.
2. `OPEN`: Remote service is failing (failures exceed threshold); requests fail immediately with `CircuitBreakerOpenException` without hitting the network.
3. `HALF_OPEN`: After a cooldown period, allows a trial request to probe if the remote service has recovered.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.resilience;

import java.time.Instant;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;

// 1. Domain Exception for Circuit Breaker
public class CircuitBreakerOpenException extends RuntimeException {
    public CircuitBreakerOpenException(String circuitName) {
        super(String.format("Circuit breaker '%s' is OPEN. Downstream service unavailable.", circuitName));
    }
}

// 2. High-Performance Thread-Safe Circuit Breaker
public final class CircuitBreaker {
    public enum State { CLOSED, OPEN, HALF_OPEN }

    private final String name;
    private final int failureThreshold;
    private final long resetTimeoutMillis;

    private volatile State state = State.CLOSED;
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private volatile long lastFailureTime = 0;

    public CircuitBreaker(String name, int failureThreshold, long resetTimeoutMillis) {
        this.name = name;
        this.failureThreshold = failureThreshold;
        this.resetTimeoutMillis = resetTimeoutMillis;
    }

    public synchronized <T> T execute(Supplier<T> protectedOperation, Supplier<T> fallback) {
        checkStateTransition();

        if (state == State.OPEN) {
            if (fallback != null) {
                return fallback.get(); // Graceful degradation!
            }
            throw new CircuitBreakerOpenException(name);
        }

        try {
            T result = protectedOperation.get();
            onSuccess();
            return result;
        } catch (Exception ex) {
            onFailure(ex);
            if (fallback != null) {
                return fallback.get();
            }
            throw ex;
        }
    }

    private void checkStateTransition() {
        if (state == State.OPEN) {
            long elapsed = System.currentTimeMillis() - lastFailureTime;
            if (elapsed > resetTimeoutMillis) {
                state = State.HALF_OPEN;
                System.out.printf("[CIRCUIT %s] Entering HALF-OPEN probe state...%n", name);
            }
        }
    }

    private void onSuccess() {
        if (state == State.HALF_OPEN) {
            System.out.printf("[CIRCUIT %s] Probe succeeded. Resetting to CLOSED state.%n", name);
        }
        failureCount.set(0);
        state = State.CLOSED;
    }

    private void onFailure(Exception ex) {
        lastFailureTime = System.currentTimeMillis();
        int failures = failureCount.incrementAndGet();
        System.err.printf("[CIRCUIT %s] Recorded failure #%d: %s%n", name, failures, ex.getMessage());

        if (state == State.HALF_OPEN || failures >= failureThreshold) {
            state = State.OPEN;
            System.err.printf("[CIRCUIT %s] Threshold breached! Circuit TRIPPED to OPEN!%n", name);
        }
    }

    public State getState() { return state; }

    public static void main(String[] args) throws InterruptedException {
        CircuitBreaker cb = new CircuitBreaker("PaymentRpcService", 2, 1000);

        Supplier<String> remoteCall = () -> {
            throw new RuntimeException("503 Gateway Timeout");
        };

        Supplier<String> fallback = () -> "FALLBACK: Cached Response";

        // Iteration 1: Failure 1
        System.out.println("Call 1: " + cb.execute(remoteCall, fallback));
        // Iteration 2: Failure 2 -> Trips Circuit!
        System.out.println("Call 2: " + cb.execute(remoteCall, fallback));

        // Iteration 3: Circuit is OPEN -> Fails fast without hitting remoteCall!
        System.out.println("Call 3: " + cb.execute(remoteCall, fallback));

        // Wait for cooldown
        System.out.println("Sleeping 1100ms for cooldown...");
        Thread.sleep(1100);

        // Iteration 4: HALF-OPEN probe (will fail and re-open)
        System.out.println("Call 4 (Probe): " + cb.execute(remoteCall, fallback));
    }
}
```

#### Architectural Highlights:
- **Fast-Fail Defense**: When a downstream microservice is dead, requests do not hang thread pools or exhaust memory sockets—they fail fast in microseconds.
- **Graceful Fallbacks**: Callers can supply a fallback `Supplier<T>` returning cached data or safe defaults.
- **State Machine Transitions**: Automatically moves between `CLOSED`, `OPEN`, and `HALF_OPEN` based on error frequency and cooldown timers.
</details>
