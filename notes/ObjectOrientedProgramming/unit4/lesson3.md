# Lesson 3 — Abstract Classes vs Interfaces & Modern Contract Architecture

> [!NOTE]
> **Learning Outcomes:**
> - Architect decoupled systems using **Abstract Classes** for shared mutable state and **Interfaces** for capability contracts.
> - Implement the **Template Method Design Pattern** using `abstract` methods and `final` execution templates.
> - Leverage modern Java interface capabilities: **`default` methods**, **`static` factory methods**, and **`private` helper methods**.
> - Resolve multi-interface default method collisions using Java's **3 Invariant Conflict Resolution Rules**.
> - Design framework-grade enterprise APIs using the **Skeletal Implementation Pattern** (Interface + Abstract Adapter).

{{media:interface-video}}

{{media:contract-visual}}

## Executive Summary & System Context

One of the most consequential architectural decisions an enterprise software engineer makes is selecting between an **Abstract Class** and an **Interface**. Both constructs define incomplete type specifications that cannot be instantiated directly, yet they serve fundamentally different roles in system design.

An **Abstract Class** models an **IS-A identity relationship**: it represents a core structural foundation that can hold mutable instance state, maintain non-public constructors, and enforce lifecycle templates. However, it binds subclasses to a strict single-inheritance hierarchy.

An **Interface** models a **CAN-DO capability contract**: it defines behavioral guarantees completely detached from the class hierarchy. With the evolution of Java 8 and 9 (introducing `default`, `static`, and `private` methods), interfaces have evolved from simple method signatures into sophisticated, backward-compatible API contracts capable of providing default behavioral logic.

This lesson explores the mechanics of abstract classes, the modern capabilities of interfaces, default method conflict resolution, and the enterprise **Skeletal Implementation Pattern**.

---

## 1. Abstract Classes & The Template Method Pattern

An **Abstract Class** is a class declared with the `abstract` keyword. It serves as a partial blueprint:

```java
package com.aastu.fintech.processing;

import java.math.BigDecimal;
import java.util.Objects;

public abstract class BasePaymentProcessor {

    // 1. Can maintain shared mutable instance state!
    private final String processorId;
    private long totalTransactionsProcessed = 0;

    // 2. Protected constructor for subclass super() chaining
    protected BasePaymentProcessor(String processorId) {
        this.processorId = Objects.requireNonNull(processorId, "Processor ID required");
    }

    // 3. THE TEMPLATE METHOD PATTERN:
    // Final method guarantees the invariant algorithm cannot be corrupted by subclasses!
    public final void processTransaction(String orderId, BigDecimal amount) {
        validateInputs(orderId, amount);
        authenticateGateway();
        
        // Abstract hook executed polymorphically by concrete provider:
        executeTransfer(orderId, amount);
        
        totalTransactionsProcessed++;
        emitAuditReceipt(orderId, amount);
    }

    // Invariant private validation routines
    private void validateInputs(String orderId, BigDecimal amount) {
        if (orderId == null || amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Invalid transaction parameters");
        }
    }

    private void authenticateGateway() {
        System.out.println("Gateway authenticated for: " + processorId);
    }

    private void emitAuditReceipt(String orderId, BigDecimal amount) {
        System.out.println("Receipt logged. Total processed: " + totalTransactionsProcessed);
    }

    // 4. Abstract Method: Must be implemented by subclasses
    protected abstract void executeTransfer(String orderId, BigDecimal amount);
}
```

### The Architectural Beauty of Template Method:
- The execution lifecycle (`validate` $	o$ `authenticate` $	o$ `executeTransfer` $	o$ `emitReceipt`) is locked down and immutable via `final`.
- Subclasses implement **only** the variable business logic (`executeTransfer`) without having to worry about authentication, error logging, or transaction counting.

---

## 2. Modern Java Interfaces: `default`, `static`, and `private` Methods

Prior to Java 8, interfaces were pure abstract contracts: they could declare only `public static final` constants and `public abstract` method signatures.

To permit the evolution of standard library collections (such as adding `.stream()` to `java.util.Collection` without breaking thousands of third-party implementations), modern Java revolutionized interfaces:

### 2.1 The 5 Capabilities of Modern Interfaces:
1. **Abstract Methods**: Standard contract signatures.
2. **Constants**: Implicitly `public static final`.
3. **`default` Methods (Java 8+)**: Provides a concrete default implementation. Implementing classes inherit this logic without being forced to override it.
4. **`static` Utility Methods (Java 8+)**: Provides factory and helper methods bound to the interface namespace (e.g. `List.of()`, `Comparator.comparing()`).
5. **`private` / `private static` Methods (Java 9+)**: Allows complex default methods to share reusable helper logic without leaking that logic into the public API.

```java
package com.aastu.fintech.crypto;

public interface CryptographicSigner {

    // 1. Abstract contract
    byte[] sign(byte[] payload);

    // 2. Default method providing convenient overload
    default String signText(String plainText) {
        validatePayload(plainText); // Calling private helper
        byte[] signature = sign(plainText.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        return java.util.Base64.getEncoder().encodeToString(signature);
    }

    // 3. Static Factory Method
    static CryptographicSigner createHmacSigner(String secretKey) {
        return new HmacSignerImpl(secretKey);
    }

    // 4. Private Helper Method (Java 9+)
    private void validatePayload(String text) {
        if (text == null || text.isBlank()) {
            throw new IllegalArgumentException("Payload cannot be blank");
        }
    }
}
```

---

## 3. Interface Default Method Conflicts: The 3 Invariant Rules

Because a class can implement multiple interfaces, what happens if two interfaces declare an identical default method?

```java
interface LoggingService {
    default void log(String msg) { System.out.println("Log: " + msg); }
}

interface AuditService {
    default void log(String msg) { System.out.println("Audit: " + msg); }
}

// COMPILATION ERROR: Duplicate default methods named log with parameters (String)
// inherited from types LoggingService and AuditService!
class EnterpriseManager implements LoggingService, AuditService {
}
```

### The 3 Invariant Resolution Rules in Java:
1. **Rule 1: Classes Beat Interfaces**:
   If a superclass provides a concrete method, it **always takes precedence** over any interface default method!
2. **Rule 2: Most Specific Sub-Interface Wins**:
   If `InterfaceB extends InterfaceA`, and both define `default void execute()`, the more specific sub-interface (`InterfaceB`) wins.
3. **Rule 3: Explicit Disambiguation Required**:
   If neither Rule 1 nor Rule 2 resolves the collision, the compiler **mandates that the implementing class override the method explicitly** and resolve the ambiguity using `<InterfaceName>.super.<method>()`:

```java
public class EnterpriseManager implements LoggingService, AuditService {
    @Override
    public void log(String msg) {
        // Explicitly choose which default implementation to execute, or write custom logic:
        AuditService.super.log(msg);
        LoggingService.super.log(msg);
    }
}
```

---

## 4. Architectural Decision Matrix: Abstract Class vs. Interface

| Architectural Dimension | Abstract Class | Interface |
| :--- | :--- | :--- |
| **Relationship Model** | **IS-A Identity**: Defines the core identity and nature of the object. | **CAN-DO Capability**: Defines functional capabilities or roles. |
| **Inheritance Limit** | **Strictly Single**: A class can extend only one abstract class. | **Unlimited Multiple**: A class can implement $N$ interfaces. |
| **State Storage** | **Mutable State**: Can declare non-static, non-final fields in heap memory. | **Stateless**: Can only declare `public static final` constants. |
| **Constructors** | **Supported**: Can define constructors invoked via `super()`. | **Prohibited**: Cannot define constructors; no instance allocation. |
| **Access Modifiers** | Full spectrum: `private`, `protected`, package-private, `public`. | Public by default (plus private helpers since Java 9). |
| **Primary Design Pattern** | **Template Method Pattern**: Locking down execution flow. | **Strategy Pattern / Decorator Pattern**: Swappable behaviors. |

---

## 5. The Skeletal Implementation Pattern (Effective Java Item 20)

How do world-class frameworks (such as the Java Collections Framework, Spring Framework, and Jackson) reconcile the flexibility of interfaces with the code-reuse benefits of abstract classes?

They employ the **Skeletal Implementation Pattern** (Interface + Abstract Adapter):

```
       [<<interface>> List<E>]   <--- Public Contract (Mockable, pluggable)
                  ^
                  |
     [abstract class AbstractList<E>] <--- Skeletal Adapter (Implements common boilerplate)
                  ^
                  |
       [class ArrayList<E>]      <--- Concrete Implementation (High-performance arrays)
```

1. **The Interface** (`List<E>`) defines the public API contract, allowing callers to program to interfaces.
2. **The Skeletal Abstract Class** (`AbstractList<E>`) implements the repetitive, generic methods (such as `isEmpty()`, `contains()`, `equals()`, `hashCode()`) in terms of basic primitive methods.
3. **The Concrete Class** (`ArrayList<E>`) extends the skeletal class, needing to implement only a tiny handful of primitive methods (`get(int)`, `set(int, E)`, `size()`).

---

## 6. Progressive 3-Tier Interactive Practice

### Level 1: Default Method Collision Resolution Trace
**Challenge**: Analyze the class hierarchy below. What is printed when `main()` executes?

```java
interface Reader {
    default String getName() { return "Generic Reader"; }
}

interface FastReader extends Reader {
    @Override
    default String getName() { return "Fast Reader"; }
}

class BaseDevice {
    public String getName() { return "Base Device"; }
}

class SensorDevice extends BaseDevice implements FastReader {
}

public class DefaultMethodPuzzle {
    public static void main(String[] args) {
        SensorDevice d = new SensorDevice();
        System.out.println(d.getName());
    }
}
```

<details>
<summary>View Level 1 Resolution Walkthrough</summary>

**Exact Console Output**:
```text
Base Device
```

**Deep Architectural Explanation**:
Apply the **3 Invariant Conflict Resolution Rules**:
1. `SensorDevice` inherits `getName()` from both superclass `BaseDevice` and interface `FastReader`.
2. **Rule 1 states: "Classes beat Interfaces."**
3. Any concrete method inherited from a superclass (`BaseDevice.getName()`) takes absolute precedence over all interface default methods, regardless of interface specificity!
4. Therefore, `BaseDevice.getName()` is invoked, printing `Base Device`.
</details>

---

### Level 2: Scaffolded System Refactoring (Pluggable Exporter Architecture)
**Scenario**: You are refactoring an enterprise report generator. The legacy codebase uses a monolithic class with a massive `switch` statement to generate JSON, XML, and CSV outputs:

```java
// MONOLITHIC FRAGILE EXPORTER
public class ReportExporter {
    public void export(Report report, String format) {
        if (format.equals("JSON")) {
            System.out.println("Header: JSON");
            System.out.println(report.data());
            System.out.println("Footer: JSON");
        } else if (format.equals("CSV")) {
            System.out.println("Header: CSV");
            System.out.println(report.data());
        }
    }
}
```

**Task**: Refactor this into a pluggable, production-grade architecture:
1. Define a `ReportFormatter` interface defining the formatting contract.
2. Create an `AbstractReportFormatter` implementing the **Template Method Pattern** (`exportReport`), managing header formatting, content emission, and checksum validation.
3. Provide concrete implementations for `JsonReportFormatter` and `CsvReportFormatter`.

<details>
<summary>View Level 2 Refactored Production Solution</summary>

```java
package com.aastu.reporting;

import java.util.Objects;

// 1. Capability Interface
public interface ReportFormatter {
    String format(Report report);
}

// 2. Skeletal Abstract Class enforcing Template Method
public abstract class AbstractReportFormatter implements ReportFormatter {

    @Override
    public final String format(Report report) {
        Objects.requireNonNull(report, "Report cannot be null");
        
        StringBuilder sb = new StringBuilder();
        sb.append(generateHeader(report)).append('
');
        sb.append(formatBody(report)).append('
');
        sb.append(generateFooter(report));
        
        return sb.toString();
    }

    protected abstract String generateHeader(Report report);
    protected abstract String formatBody(Report report);
    protected abstract String generateFooter(Report report);
}

// 3. Concrete JSON Formatter
public final class JsonReportFormatter extends AbstractReportFormatter {
    @Override
    protected String generateHeader(Report report) {
        return "{
  "reportId": "" + report.id() + "",
  "content": [";
    }

    @Override
    protected String formatBody(Report report) {
        return "    "" + report.data().replace(""", "\"") + """;
    }

    @Override
    protected String generateFooter(Report report) {
        return "  ]
}";
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge (Non-Breaking API Evolution)
**Scenario**: You are the lead architect of a financial payment gateway SDK distributed to 50+ banking institutions. The core interface is:

```java
public interface PaymentGateway {
    PaymentResult charge(PaymentRequest request);
    RefundResult refund(RefundRequest request);
}
```

Regulatory authorities mandate that all payment gateways must now support **Two-Factor Biometric Step-Up Verification**:
```java
BiometricVerificationResult verifyBiometrics(String biometricToken);
```

If you add `BiometricVerificationResult verifyBiometrics(String biometricToken);` directly to `PaymentGateway`, every single client bank's codebase will fail compilation immediately upon upgrading the SDK!

**System Challenge**:
1. How do modern Java `default` methods enable non-breaking backward-compatible API evolution?
2. Design the updated `PaymentGateway` interface providing a default backward-compatible fallback, and explain the architectural trade-offs involved.

<details>
<summary>View Level 3 Senior SE Architectural Solution</summary>

### 1. Architectural Solution: Backward-Compatible `default` Method
By providing a `default` implementation inside the interface, all existing third-party implementing classes continue to compile and run without modification:

```java
package com.aastu.fintech.sdk;

public interface PaymentGateway {

    PaymentResult charge(PaymentRequest request);
    RefundResult refund(RefundRequest request);

    /**
     * Non-breaking API evolution (Java 8+):
     * Provides a default fallback implementation. Existing client implementations
     * that have not yet updated to biometric standards will default to gracefully
     * declaring the capability unsupported, rather than breaking compilation!
     */
    default BiometricVerificationResult verifyBiometrics(String biometricToken) {
        // Fallback implementation: Fail safe with descriptive status
        return BiometricVerificationResult.unsupported(
            "Biometric verification not supported by this payment provider implementation"
        );
    }
}
```

### 2. Architectural Trade-offs:
- **Advantage**: Zero breaking changes across client codebases; seamless dependency version upgrades.
- **Risk**: If a client bank is legally required to implement biometric verification, the compiler can no longer enforce that they implement it (because the default method satisfies the compiler). 
- **Remediation**: Use runtime capability checks (`gateway.isBiometricSupported()`) or architectural linters to audit production deployment compliance.
</details>
