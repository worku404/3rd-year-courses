# Lesson 2 — Dynamic Polymorphism, Method Overriding & Virtual Method Tables (vtables)

> [!NOTE]
> **Learning Outcomes:**
> - Master **Dynamic Method Dispatch** (Runtime Polymorphism) and upcasting contracts (`Parent p = new Child()`).
> - Enforce the 5 strict compiler rules of **Method Overriding**, including **Covariant Return Types** and visibility widening.
> - Apply the **Liskov Substitution Principle (LSP)** to design behavioral contracts that never violate caller assumptions.
> - Dissect how the JVM achieves $O(1)$ dynamic dispatch using **Virtual Method Tables (vtables)** in Metaspace.
> - Leverage the **`final` modifier** to enable aggressive HotSpot JIT method inlining and prevent security breaches.

{{media:polymorphism-video}}

{{media:vtable-visual}}

## Executive Summary & System Context

Polymorphism—derived from the Greek for "many forms"—is the crowning architectural achievement of Object-Oriented software design. It allows client code to interact with high-level abstract interfaces without coupling itself to specific concrete implementations. A single payment routing pipeline can process credit cards, mobile wallets, and interbank wires identically, with the runtime engine automatically resolving the correct behavioral variant.

In the Java Virtual Machine, dynamic polymorphism is not accomplished via expensive runtime tree searches. It is implemented at the hardware-adjacent level through **Virtual Method Tables (vtables)**: dense pointer arrays allocated in native Metaspace that resolve method calls in $O(1)$ constant time.

However, polymorphism is easily corrupted when developers treat inheritance as mere code reuse rather than **behavioral equivalence**. Violations of the **Liskov Substitution Principle (LSP)** represent some of the most insidious architectural bugs in enterprise software.

This lesson explores dynamic method dispatch, the compiler invariants of method overriding, the low-level mechanics of vtables, and the performance implications of the `final` keyword.

---

## 1. Dynamic Method Dispatch & Runtime Polymorphism

**Dynamic Method Dispatch** is the mechanism by which a call to an overridden method is resolved at runtime rather than compile time.

```java
package com.aastu.fintech.payments;

import java.math.BigDecimal;

public abstract class PaymentGateway {
    public abstract void process(BigDecimal amount);
}

public class TelebirrGateway extends PaymentGateway {
    @Override
    public void process(BigDecimal amount) {
        System.out.println("Processing " + amount + " via Ethio Telecom Telebirr API");
    }
}

public class CbeBirrGateway extends PaymentGateway {
    @Override
    public void process(BigDecimal amount) {
        System.out.println("Processing " + amount + " via Commercial Bank of Ethiopia Birr API");
    }
}
```

When client code invokes the payment:

```java
public void executeCheckout(PaymentGateway gateway, BigDecimal total) {
    // The compiler sees only PaymentGateway.process(BigDecimal).
    // The JVM dynamically dispatches to TelebirrGateway or CbeBirrGateway at runtime!
    gateway.process(total);
}
```

---

## 2. The 5 Strict Compiler Rules for Method Overriding

To ensure type safety and preserve behavioral contracts, the Java compiler enforces five immutable invariants whenever a method is overridden:

### 2.1 Rule 1: Identical Signature
The method name and parameter types must match **exactly**. If the parameter types differ in any way, you have performed **Method Overloading**, not overriding!

### 2.2 Rule 2: Covariant Return Types (Java 5+)
In early Java, an overriding method had to return the exact same type as the base method. Since Java 5, the overriding method can return a **narrower subtype** of the superclass return type:

```java
public class AccountFactory {
    public BankAccount createAccount() {
        return new BankAccount("BASE", BigDecimal.ZERO);
    }
}

public class SavingsAccountFactory extends AccountFactory {
    // COVARIANT RETURN TYPE: SavingsAccount is a subtype of BankAccount!
    @Override
    public SavingsAccount createAccount() {
        return new SavingsAccount("SAVINGS", BigDecimal.ZERO, new BigDecimal("0.07"));
    }
}
```
*Client Benefit*: Callers invoking `new SavingsAccountFactory().createAccount()` receive a strongly-typed `SavingsAccount` without requiring an explicit cast!

### 2.3 Rule 3: Visibility Cannot Be Narrowed
An overriding method **cannot reduce the visibility** of the superclass method:
- If superclass declares `public`, subclass **must** be `public`.
- If superclass declares `protected`, subclass can be `protected` or `public` (widening is allowed; narrowing is prohibited).

*Why?* If a subclass could reduce visibility to `private`, upcasting to the superclass reference would allow callers to invoke a supposedly private method, breaking language security!

### 2.4 Rule 4: Confinement of Checked Exceptions
An overriding method cannot throw **new or broader checked exceptions** than declared by the superclass:
- If superclass declares `throws IOException`, subclass can throw `IOException`, `FileNotFoundException` (a subtype), or **no exceptions at all**.
- Subclass **cannot** declare `throws Exception` or `throws SQLException`.

### 2.5 Rule 5: Always Annotate with `@Override`
The `@Override` annotation instructs the compiler to verify that an actual superclass method is being overridden. If a developer accidentally writes `public boolean equals(BankAccount other)` instead of `public boolean equals(Object other)`, `@Override` immediately causes a compilation failure, preventing subtle bugs.

---

## 3. The Liskov Substitution Principle (LSP)

Formulated by Barbara Liskov in 1987, the **Liskov Substitution Principle (LSP)** is the "L" in SOLID:

> [!IMPORTANT]
> **Liskov Substitution Principle Definition**:
> If $S$ is a subtype of $T$, then objects of type $T$ in a program may be replaced with objects of type $S$ without altering any of the desirable properties of that program (correctness, task performed, etc.).

### The Canonical Violation: Rectangle and Square
In elementary geometry, a square is a rectangle with equal sides. Novice developers often model this as:

```java
// CATASTROPHIC ARCHITECTURAL MISTAKE
public class Rectangle {
    protected int width;
    protected int height;

    public void setWidth(int w) { this.width = w; }
    public void setHeight(int h) { this.height = h; }
    public int getArea() { return width * height; }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int w) {
        this.width = w;
        this.height = w; // Mutates both to enforce square geometry!
    }

    @Override
    public void setHeight(int h) {
        this.width = h;
        this.height = h;
    }
}
```

Now observe how client code breaks:

```java
public void verifyResize(Rectangle r) {
    r.setWidth(5);
    r.setHeight(10);
    // Invariant assumption: Area of any Rectangle with w=5, h=10 MUST BE 50!
    assert r.getArea() == 50; 
}
```

When passing `new Square()` to `verifyResize()`:
1. `setWidth(5)` sets both dimensions to 5.
2. `setHeight(10)` sets both dimensions to 10.
3. `getArea()` returns **100**, causing the assertion to fail!

**The Software Engineering Lesson**:
Subtyping is about **behavioral contracts**, not physical properties. In code, a `Square` is NOT a `Rectangle` because its width and height cannot vary independently!

---

## 4. Low-Level JVM Mechanics: The Virtual Method Table (vtable)

How does the JVM execute an `invokevirtual` opcode in constant $O(1)$ time without searching up the class inheritance tree?

```java
BankAccount acc = getAccount();
acc.withdraw(new BigDecimal("100"));
```

### The Metaspace vtable Architecture
During Class Loading, the JVM builds a **Virtual Method Table (vtable)** for each class in native Metaspace memory:
- The vtable is an indexed array of direct function pointers to executable machine code / bytecode offsets.
- Every method declared in `java.lang.Object` occupies the first several slots (Slots 0 to 4: `equals`, `hashCode`, `toString`, etc.).
- Subclass vtables inherit the exact same slot indices as their superclasses!

```
BankAccount vtable in Metaspace:
[Index 0] -> Object.toString()
[Index 1] -> BankAccount.deposit()
[Index 2] -> BankAccount.withdraw()  (Pointer to BankAccount bytecode)

SavingsAccount vtable in Metaspace:
[Index 0] -> Object.toString()       (Inherited pointer)
[Index 1] -> BankAccount.deposit()   (Inherited pointer)
[Index 2] -> SavingsAccount.withdraw() [OVERWRITTEN WITH SUBCLASS POINTER!]
[Index 3] -> SavingsAccount.applyInterest()
```

### The 2-Step $O(1)$ Dispatch Algorithm:
When the CPU encounters `invokevirtual #withdraw`:
1. The JVM inspects the object header of the target heap instance to read its **Klass pointer**, identifying the concrete class (`SavingsAccount`).
2. The compiler already knows at compile time that `withdraw()` is located at **Index 2**.
3. The JVM immediately reads `vtable[2]` of `SavingsAccount` and jumps to `SavingsAccount.withdraw()`!
$$	ext{Target Address} = 	ext{vtable\_base} + (2 	imes 	ext{pointer\_size})$$

This executes in **zero hierarchy traversal time**!

---

## 5. The `final` Modifier & JIT Method Inlining

The `final` keyword serves as a powerful architectural and performance tool in Java:

| Context | Semantic Meaning | JVM Performance & Architectural Impact |
| :--- | :--- | :--- |
| **`final` Variable** | Assigned exactly once; reference cannot be redirected | Enables safe multi-threaded publishing without volatile locks. |
| **`final` Method** | Method cannot be overridden by any subclass | **Removes virtual dispatch overhead**: The HotSpot JIT compiler can aggressively perform **Method Inlining**, replacing the call with raw CPU machine code! |
| **`final` Class** | Class cannot be extended (e.g. `String`, `Integer`) | Guarantees immutability and prevents malicious spoofing of core security abstractions. |

---

## 6. Progressive 3-Tier Interactive Practice

### Level 1: Multi-Level Dispatch & Overriding vs Overloading Trace
**Challenge**: Trace the console output of the following program:

```java
class Alpha {
    public void print(Alpha a)  { System.out.println("1. Alpha-Alpha"); }
    public void print(Beta b)   { System.out.println("2. Alpha-Beta"); }
}

class Beta extends Alpha {
    @Override
    public void print(Beta b)   { System.out.println("3. Beta-Beta"); }
    public void print(Alpha a)  { System.out.println("4. Beta-Alpha"); }
}

public class DispatchTrace {
    public static void main(String[] args) {
        Alpha a = new Beta();
        Beta b = new Beta();
        
        a.print(b);
        a.print(a);
    }
}
```

<details>
<summary>View Level 1 Architectural Trace Walkthrough</summary>

**Exact Console Output**:
```text
3. Beta-Beta
4. Beta-Alpha
```

**Deep Architectural Explanation**:
1. Method dispatch in Java is a two-step process:
   - **Step 1 (Compile Time)**: The compiler determines the **method signature** based on the declared type of the reference and the arguments.
   - **Step 2 (Runtime)**: The JVM executes dynamic dispatch (`invokevirtual`) on that signature based on the concrete heap object.
2. For `a.print(b)`:
   - Compile time: `a` is declared as `Alpha`. The argument `b` is `Beta`. The compiler selects signature `print(Beta)` in class `Alpha`.
   - Runtime: The object is `Beta`. The JVM looks up `print(Beta)` in `Beta`'s vtable, executing `Beta.print(Beta)`. Prints `3. Beta-Beta`.
3. For `a.print(a)`:
   - Compile time: `a` is declared as `Alpha`. The argument `a` is declared as `Alpha`. The compiler selects signature `print(Alpha)` in class `Alpha`.
   - Runtime: The object is `Beta`. The JVM looks up `print(Alpha)` in `Beta`'s vtable, executing `Beta.print(Alpha)`. Prints `4. Beta-Alpha`.
</details>

---

### Level 2: Scaffolded System Refactoring (Fixing LSP Violation)
**Scenario**: In a document processing pipeline, a legacy developer created a hierarchy where `ReadOnlyDocument` extends `Document`, but throws an unsupported operation exception when mutated:

```java
// VIOLATING LISKOV SUBSTITUTION PRINCIPLE
public class Document {
    private String content = "";
    public void write(String text) { this.content += text; }
    public String read() { return content; }
}

public class ReadOnlyDocument extends Document {
    @Override
    public void write(String text) {
        // CATASTROPHIC LSP VIOLATION: Throws unexpected runtime exception!
        throw new UnsupportedOperationException("Read-only document cannot be modified");
    }
}
```

Client code expecting a `Document` crashes when passed a `ReadOnlyDocument`!

**Task**: Refactor this hierarchy into an LSP-compliant architecture by:
1. Extracting a shared read-only abstraction (`ReadableDocument`).
2. Ensuring that subtypes never violate the behavioral contracts of their parent types.

<details>
<summary>View Level 2 Refactored Production Solution</summary>

```java
package com.aastu.documents;

import java.util.Objects;

// Base Contract: Pure reading capability
public interface ReadableDocument {
    String read();
}

// Specialization: Mutable document contract
public interface WritableDocument extends ReadableDocument {
    void write(String text);
}

// Implementation 1: Immutable Read-Only Document
public final class ImmutableDocument implements ReadableDocument {
    private final String content;

    public ImmutableDocument(String content) {
        this.content = Objects.requireNonNull(content);
    }

    @Override
    public String read() {
        return content;
    }
}

// Implementation 2: Mutable Document (Complies with LSP!)
public final class EditableDocument implements WritableDocument {
    private final StringBuilder content = new StringBuilder();

    @Override
    public synchronized void write(String text) {
        this.content.append(Objects.requireNonNull(text));
    }

    @Override
    public synchronized String read() {
        return content.toString();
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge (Megamorphic Call Site Optimization)
**Scenario**: In an ultra-high-throughput financial messaging gateway processing 100,000,000 FIX messages per minute, profiling reveals that a polymorphic validation call site is running 12x slower than expected:

```java
public void validateAll(List<Validator> validators, Message msg) {
    for (Validator v : validators) {
        v.validate(msg); // Megamorphic Call Site!
    }
}
```

The HotSpot JIT compiler log (`-XX:+PrintCompilation -XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining`) shows that the call site has de-optimized to **Megamorphic Dispatch**:
```text
@ 12 com.aastu.gateway.Validator::validate (megamorphic)
```

**Diagnostic Challenge**:
1. Explain the three polymorphic call site states in the HotSpot JIT compiler: **Monomorphic**, **Bimorphic**, and **Megamorphic**.
2. Why does a megamorphic call site prevent JIT inlining and degrade CPU branch predictor caches?
3. How can the architecture be refactored to restore monomorphic JIT inlining without sacrificing extensibility?

<details>
<summary>View Level 3 Senior SE Architectural Solution</summary>

### 1. HotSpot Call Site Optimization States:
1. **Monomorphic (1 concrete class seen)**: The JIT compiler generates a single check (`if (klass == A)`) and **inlines the method body directly**, achieving raw native execution speed (0ns method call overhead).
2. **Bimorphic (2 concrete classes seen)**: The JIT generates a two-way branch (`if (klass == A) ... else if (klass == B) ...`) and inlines both branches.
3. **Megamorphic (>= 3 concrete classes seen)**: The JIT compiler gives up on inlining! It falls back to full runtime **vtable pointer lookup** on every single invocation, incurring CPU pipeline stalls and cache line fetches.

### 2. Architectural Remediation: Batching by Concrete Type
Instead of interleaving diverse polymorphic instances in a flat loop, group validators by concrete type, or flatten them into a single compiled composite validator:

```java
package com.aastu.gateway;

import java.util.List;

public final class CompositeValidator implements Validator {
    // Concrete array references: Allows HotSpot to inline each validation step!
    private final ChecksumValidator checksum = new ChecksumValidator();
    private final SequenceValidator sequence = new SequenceValidator();
    private final SecurityValidator security = new SecurityValidator();

    @Override
    public void validate(Message msg) {
        // Monomorphic calls: JIT inlines all three checks into a single contiguous machine code block!
        checksum.validate(msg);
        sequence.validate(msg);
        security.validate(msg);
    }
}
```
By composing known validators statically, the hot loop operates on a single `CompositeValidator` instance, restoring **Monomorphic Inlining** and achieving a 10x throughput surge!
</details>
