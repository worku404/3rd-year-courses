# Lesson 2 — The Core Pillars of Object-Oriented Engineering

> [!NOTE]
> **Learning Outcomes:**
> - Define and contrast the four foundational pillars of Object-Oriented Engineering: **Abstraction**, **Encapsulation**, **Inheritance**, and **Polymorphism**.
> - Distinguish clearly between **Abstraction** (*what* an entity does) and **Encapsulation** (*how* its state and implementation mechanics are shielded).
> - Apply the **Liskov Substitution Principle (LSP)** to inheritance hierarchies and evaluate the architectural trade-offs of **Composition over Inheritance**.
> - Formalize the mechanics of **Polymorphism**, comparing compile-time static overloading against runtime dynamic dispatch (Virtual Method Tables).
> - Architect an extensible, decoupled payment processing subsystem demonstrating all four pillars in production Java.

{{media:four-pillars-video}}

{{media:four-pillars-architecture-visual}}

## 1. The Architectural Triad: Why Four Pillars?

In enterprise software engineering, building a system that merely "works" is trivial; building a system that remains maintainable, extensible, and defect-resistant across five years of evolving requirements is extraordinarily difficult.

The **Four Pillars of Object-Oriented Programming** are not isolated academic definitions—they are complementary architectural safeguards designed to manage software entropy:

```
  ┌─────────────────┐       ┌─────────────────┐
  │   ABSTRACTION   │ <───> │  ENCAPSULATION  │
  │ (Contract/What) │       │ (Boundary/How)  │
  └────────┬────────┘       └────────┬────────┘
           │                         │
           ▼                         ▼
  ┌─────────────────┐       ┌─────────────────┐
  │   INHERITANCE   │ <───> │  POLYMORPHISM   │
  │   (Taxonomy)    │       │(Dynamic Dispatch)│
  └─────────────────┘       └─────────────────┘
```

---

## 2. Pillar 1: Abstraction (Managing Cognitive Complexity)

**Abstraction** is the engineering discipline of isolating the essential conceptual qualities of an entity while filtering out, suppressing, or deferring non-essential operational mechanics.

### 2.1 The Abstraction Barrier
Abstraction creates a rigid boundary between the **client** (the caller of code) and the **implementation** (the worker):
- The client only needs to know the **contract** (method signature, preconditions, and postconditions).
- The implementation details (e.g., whether a sorted list uses Quicksort, Mergesort, or an in-memory B-Tree) are strictly quarantined.

```java
// Client interacts with the high-level abstraction:
List<String> userList = new ArrayList<>();
userList.sort(Comparator.naturalOrder()); // Client knows WHAT happens, not HOW memory is shifted
```

> [!IMPORTANT]
> **The Law of Demeter (Principle of Least Knowledge)**:
> A module should not know about the internal workings of the objects it manipulates. Avoid "train wrecks" like `order.getCustomer().getAddress().getCity().getZipCode()`. High abstraction demands interacting directly with immediate collaborators: `order.getDeliveryPostalCode()`.

---

## 3. Pillar 2: Encapsulation (Information Hiding & Invariant Protection)

While **Abstraction** is about *hiding complexity* (the interface), **Encapsulation** is about *shielding state* (the boundary).

### 3.1 Parnas' Information Hiding Principle (1972)
Formulated by David Parnas, true encapsulation dictates that **a module should hide a secret**. The secret is typically:
1. The physical representation of data in RAM.
2. An algorithm that is likely to change.
3. Hardware-dependent drivers.

### 3.2 Invariant Self-Defense
Encapsulation packages data with the routines that operate upon it, erecting access control barriers (`private`, `protected`, `public`):

```java
public class TemperatureSensor {
    // Encapsulated state: cannot be corrupted to below Absolute Zero (-273.15 C)
    private double kelvin;

    public void setCelsius(double celsius) {
        if (celsius < -273.15) {
            throw new IllegalArgumentException("Violates thermodynamic limit: Temperature below Absolute Zero.");
        }
        this.kelvin = celsius + 273.15;
    }

    public double getCelsius() {
        return this.kelvin - 273.15;
    }
}
```
*Architectural Guarantee*: No external developer can put the `TemperatureSensor` into a physically impossible state because no direct write access exists to `kelvin`.

---

## 4. Pillar 3: Inheritance (Taxonomic Specialization & Substitution)

**Inheritance** is a mechanism where a new class (derived / subclass) is defined in terms of an existing class (base / superclass).

### 4.1 "Is-A" vs. "Has-A"
- **Inheritance models "Is-A"**: A `SavingsAccount` *is an* `Account`. A `Circle` *is a* `Shape`.
- **Composition models "Has-A"**: An `Account` *has a* `TransactionHistory`. A `Car` *has an* `Engine`.

```
        Taxonomic Specialization (Is-A)           Composition (Has-A)
                   [Account]                          [Order]
                       ▲                                 │
              ┌────────┴────────┐                        ▼
      [SavingsAccount]  [CheckingAccount]       [PaymentProcessor]
```

### 4.2 The Liskov Substitution Principle (LSP)
Inheritance must **never** be used solely for code sharing. It must satisfy behavioral subtyping as formalized by Barbara Liskov (1987):

$$	ext{Let } \phi(x) 	ext{ be a property provable about objects } x 	ext{ of type } T.$$
$$	ext{Then } \phi(y) 	ext{ should be true for objects } y 	ext{ of type } S 	ext{ where } S 	ext{ is a subtype of } T.$$

*In plain English*: **If code works correctly with a Superclass, it MUST continue to work correctly without modification when passed any Subclass!**

> [!WARNING]
> **The Classic Square-Rectangle Violation**:
> If class `Square` extends `Rectangle`, and a function changes the width expecting height to stay constant, `Square` violates LSP because setting width in a square forces height to change. **Square is NOT a behavioral subtype of Rectangle**!

### 4.3 Why Senior Engineers "Prefer Composition Over Inheritance"
Inheritance creates the tightest coupling available in OOP (the **Fragile Base Class Problem**). When a base class method changes internal behavior, it can silently break derived classes. Composition builds flexibility through loose coupling.

---

## 5. Pillar 4: Polymorphism (Dynamic Binding & The Open-Closed Principle)

**Polymorphism** (Greek: *"many forms"*) allows a single interface or reference variable to represent different underlying types at runtime.

### 5.1 Static vs. Dynamic Polymorphism

| Dimension | Static (Compile-Time) Polymorphism | Dynamic (Runtime) Polymorphism |
| :--- | :--- | :--- |
| **Primary Mechanism** | **Method Overloading** & Generics | **Method Overriding** via inheritance/interfaces |
| **Binding Time** | Compile time (Early binding) | Runtime execution (Late binding) |
| **Internal Mechanism** | Resolved by compiler based on argument types | Resolved via **Virtual Method Table (vtable)** dispatch |
| **Performance Overhead** | Zero runtime cost (direct instruction jump) | Negligible indirection pointer jump in JVM |
| **Example** | `Math.max(int, int)` vs `Math.max(double, double)` | `shape.draw()` executing `Circle.draw()` |

### 5.2 The Virtual Method Table (vtable) Under the Hood
How does the Java Virtual Machine know which method to execute when calling `animal.speak()`?

```
 Variable Reference: Animal a ──> [Dog Object in Heap]
                                       │
                                       ▼ (Metadata Pointer)
                                  [Dog Class vtable]
                                       │
                                       ├─ speak() ───> Code at memory 0x7FFF0042 (Dog.speak)
                                       └─ eat()   ───> Code at memory 0x7FFF0010 (Animal.eat)
```

At runtime, the JVM looks up the object's actual class vtable pointer and branches directly to the overriding implementation. This decouples the caller entirely from knowing the concrete class.

### 5.3 The Open-Closed Principle (OCP - Bertrand Meyer)
*"Software entities (classes, modules, functions) should be **open for extension**, but **closed for modification**."*
Polymorphism is the primary instrument of OCP: you can introduce 10 new payment types or notification channels into an enterprise application without changing a single line of the core checkout pipeline.

---

## 6. Progressive Engineering Practice & Case Studies

### Level 1 — Production Architectural Walkthrough: Multi-Gateway Payment System

Let us synthesize all Four Pillars into a cohesive enterprise architecture for a multi-provider payment engine supporting Stripe, PayPal, and Telebirr.

```
                           ┌──────────────────────────┐
                           │ <<interface>>            │
                           │ PaymentGateway (Abstract)│
                           ├──────────────────────────┤
                           │ + process(PaymentRequest)│
                           └─────────────▲────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │                       │                       │
      ┌──────────┴──────────┐ ┌──────────┴──────────┐ ┌──────────┴──────────┐
      │ StripeGateway       │ │ PayPalGateway       │ │ TelebirrGateway     │
      ├─────────────────────┤ ├─────────────────────┤ ├─────────────────────┤
      │ - apiKey (Encaps.)  │ │ - oauthToken (Enc.) │ │ - appSecret (Enc.)  │
      │ + process()         │ │ + process()         │ │ + process()         │
      └─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

#### 1. The Abstraction & Value Object Layer:
```java
package com.aastu.fintech.domain;

import java.math.BigDecimal;
import java.util.Currency;

// Value Object: Encapsulates currency and monetary amount invariants
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Amount must be strictly positive.");
        }
        if (currency == null) {
            throw new IllegalArgumentException("Currency cannot be null.");
        }
        this.amount = amount;
        this.currency = currency;
    }

    public BigDecimal getAmount() { return amount; }
    public Currency getCurrency() { return currency; }
}
```

#### 2. The Abstract Interface (Polymorphic Contract):
```java
package com.aastu.fintech.gateway;

import com.aastu.fintech.domain.Money;

public interface PaymentGateway {
    PaymentResult executePayment(String customerId, Money money);
}
```

#### 3. Concrete Implementations (Encapsulating Provider Secrets):
```java
package com.aastu.fintech.gateway.impl;

import com.aastu.fintech.domain.Money;
import com.aastu.fintech.gateway.PaymentGateway;
import com.aastu.fintech.gateway.PaymentResult;

public class TelebirrGateway implements PaymentGateway {
    // Encapsulation: Sensitive credentials hidden from client
    private final String merchantId;
    private final String appSecret;

    public TelebirrGateway(String merchantId, String appSecret) {
        this.merchantId = merchantId;
        this.appSecret = appSecret;
    }

    @Override
    public PaymentResult executePayment(String customerId, Money money) {
        // Telebirr specific API protocol payload & hashing
        System.out.println("[Telebirr] Dispatching USSD prompt for " + money.getAmount() + " ETB");
        return new PaymentResult("TB-" + System.currentTimeMillis(), true);
    }
}
```

#### 4. The Client Checkout Pipeline (Open-Closed):
```java
package com.aastu.fintech.service;

import com.aastu.fintech.domain.Money;
import com.aastu.fintech.gateway.PaymentGateway;
import com.aastu.fintech.gateway.PaymentResult;

public class CheckoutService {
    // Polymorphic Dependency: Decoupled from concrete implementations!
    private final PaymentGateway paymentGateway;

    public CheckoutService(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }

    public void checkout(String customerId, Money total) {
        System.out.println("Initiating checkout validation...");
        PaymentResult result = paymentGateway.executePayment(customerId, total);
        if (!result.isSuccess()) {
            throw new RuntimeException("Checkout failed: " + result.getTransactionId());
        }
        System.out.println("Checkout successful. Txn: " + result.getTransactionId());
    }
}
```

---

### Level 2 — Guided / Scaffolded Engineering Challenge

**Scenario**:
A junior developer creates a `ReadOnlyFile` class that inherits from `StandardFile`. 

```java
public class StandardFile {
    protected String content;

    public void write(String newContent) {
        this.content += newContent;
    }

    public String read() {
        return this.content;
    }
}

public class ReadOnlyFile extends StandardFile {
    @Override
    public void write(String newContent) {
        throw new UnsupportedOperationException("Cannot write to a Read-Only file!");
    }
}
```

A document batch-processing engine contains:
```java
public void appendFooter(StandardFile file) {
    file.write("\n--- Copyright 2026 ---");
}
```

**Your Tasks**:
1. Explain which fundamental Object-Oriented principle is violated when passing `ReadOnlyFile` to `appendFooter()`.
2. Redesign the architecture using clean interface segregation and composition.

<details>
<summary>Click to reveal Architecture Diagnostic & Solution</summary>

#### 1. The Core Violation:
This is a blatant violation of the **Liskov Substitution Principle (LSP)**. 
Client code expects any subtype of `StandardFile` to safely support `write()`. Subclassing `StandardFile` and throwing `UnsupportedOperationException` breaks the contract of the superclass and causes runtime crashes in consumers that relied on the superclass abstraction.

#### 2. The Clean Interface Segregation Architecture:
Segregate reading from writing contracts:

```java
public interface ReadableFile {
    String read();
}

public interface WritableFile extends ReadableFile {
    void write(String newContent);
}

public class ReadOnlyDocument implements ReadableFile {
    private final String content;
    public ReadOnlyDocument(String content) { this.content = content; }
    @Override public String read() { return content; }
}

public class EditableDocument implements WritableFile {
    private StringBuilder content = new StringBuilder();
    @Override public void write(String newContent) { content.append(newContent); }
    @Override public String read() { return content.toString(); }
}
```
Now, `appendFooter(WritableFile file)` strictly demands a writable abstraction, making LSP violations impossible at compile-time!
</details>

---

### Level 3 — Production Systems Interview Scenario

**Scenario (Meta / Uber Systems Architecture Interview)**:
> *"You are designing an alerting and notification subsystem for a ride-sharing dispatch backend. The system must notify users across multiple channels (SMS via Twilio, Push Notifications via Firebase FCM, Email via AWS SES, and WhatsApp). 
> Furthermore, users can configure dynamic fallback routing (e.g., if Push fails, fallback to SMS). 
> How would you architect this subsystem using the **Strategy Pattern** and the **Decorator Pattern** to enforce the Open-Closed Principle and Dependency Inversion?"*

<details>
<summary>Click to reveal Enterprise Solution & UML Architecture</summary>

#### 1. Architectural Strategy:
- **Strategy Pattern (`NotificationChannel`)**: An abstract interface defining `void send(Notification n)`. Concrete strategies (`SmsChannel`, `PushChannel`, `EmailChannel`) encapsulate vendor-specific SDK calls.
- **Decorator Pattern (`FallbackNotificationDecorator`)**: Wraps a primary `NotificationChannel` with a secondary fallback channel, intercepting exceptions and delegating upon failure without changing client code.
- **Dependency Inversion**: The `DispatchService` depends solely on the high-level `NotificationChannel` abstraction.

#### 2. Production Java Architecture:

```java
public interface NotificationChannel {
    void send(String recipient, String message);
}

// 1. Concrete Strategies
public class FcmPushChannel implements NotificationChannel {
    @Override
    public void send(String recipient, String message) {
        System.out.println("[FCM Push] Sending: " + message + " to " + recipient);
    }
}

public class TwilioSmsChannel implements NotificationChannel {
    @Override
    public void send(String recipient, String message) {
        System.out.println("[Twilio SMS] Sending SMS: " + message + " to " + recipient);
    }
}

// 2. Resilient Decorator for Fallback Routing
public class ResilientFallbackDecorator implements NotificationChannel {
    private final NotificationChannel primary;
    private final NotificationChannel fallback;

    public ResilientFallbackDecorator(NotificationChannel primary, NotificationChannel fallback) {
        this.primary = primary;
        this.fallback = fallback;
    }

    @Override
    public void send(String recipient, String message) {
        try {
            primary.send(recipient, message);
        } catch (Exception ex) {
            System.err.println("Primary channel failed (" + ex.getMessage() + "). Triggering fallback...");
            fallback.send(recipient, message);
        }
    }
}

// 3. Composition at Startup:
NotificationChannel resilientPipeline = new ResilientFallbackDecorator(
    new FcmPushChannel(),
    new TwilioSmsChannel()
);

resilientPipeline.send("+251911223344", "Your driver has arrived!");
```
This architecture satisfies:
- **Abstraction**: Client triggers `send()`, oblivious to FCM or Twilio.
- **Encapsulation**: Vendor API keys and retry logic hidden inside channels.
- **Polymorphism**: Decorator and strategies share identical contracts.
- **Open-Closed**: Adding a Discord or Slack notification channel requires 0 changes to dispatch pipelines.
</details>
