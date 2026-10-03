# Unit 4 — Client-Side Scripting with JavaScript, DOM & Event-Driven Architecture
## Lesson 1 — JavaScript Engine Architecture, Execution Contexts & The Prototype Object Model

### 1. Architectural Foundations: The JavaScript Runtime & JIT Compilation Engine

JavaScript was conceived by Brendan Eich in 1995 as a lightweight scripting language for the Netscape Navigator browser. Over three decades of standardization under ECMA International (ECMA-262), it has evolved into a high-level, multi-paradigm, dynamically typed, prototype-based, single-threaded execution language powering mission-critical client and server architectures worldwide.

To write high-performance, robust client-side software, engineers must discard the naive mental model of JavaScript as an "interpreted" script. Modern JavaScript execution environments—exemplified by Google's **V8** (Chrome, Node.js), Mozilla's **SpiderMonkey** (Firefox), and Apple's **JavaScriptCore / Nitro** (Safari)—employ sophisticated **Just-In-Time (JIT) compilation pipelines** that compile source code directly to native machine instructions at runtime.

```
+-----------------------------------------------------------------------------------+
|                           V8 EXECUTION PIPELINE                                   |
|                                                                                   |
|  [JS Source Code]                                                                 |
|         |                                                                         |
|         v                                                                         |
|  [Stream Scanner / Lexer] ----> Emits Tokens (Keywords, Identifiers, Literals)    |
|         |                                                                         |
|         v                                                                         |
|  [Parser] --------------------> Abstract Syntax Tree (AST) + Scope Analysis       |
|         |                                                                         |
|         v                                                                         |
|  [Ignition Interpreter] ------> Generates Register-Based Bytecode (Fast Startup)  |
|         |                                                                         |
|         v (Feedback Vector / Profiler: Monitors Type Shapes & Function Calls)     |
|         |                                                                         |
|  [TurboFan JIT Compiler] -----> Emits Optimized Machine Code (Loop Unrolling,     |
|         ^                       Inline Caching, Speculative Type Specialization)  |
|         | (Bailout / Deoptimization)                                              |
|         +---------------------- Polymorphic / Shape Violation Reverts to Bytecode|
+-----------------------------------------------------------------------------------+
```

#### The JIT Pipeline Lifecycle
1. **Scanning (Lexical Analysis):** Converts the raw UTF-16 stream into atomic language tokens (`const`, `function`, `ident`, `operator`).
2. **Parsing & AST Construction:** The Parser verifies syntactic grammar rules and constructs an **Abstract Syntax Tree (AST)**. Modern engines perform *pre-parsing* (lazy parsing) for functions not immediately invoked, deferring full AST compilation until invocation to optimize First Meaningful Paint (FMP).
3. **Ignition (Bytecode Interpreter):** Converts the AST into compact register-based bytecode. Bytecode executes with negligible startup latency and uses an order of magnitude less RAM than uncompressed machine code.
4. **TurboFan (Optimizing Compiler):** While bytecode runs, the engine gathers runtime type feedback (e.g., "Are the arguments to function `add(a, b)` always 31-bit integers?"). When a function becomes "hot" (frequently called), TurboFan compiles the bytecode into highly tuned native machine code, optimizing register allocation, eliminating bounds checks, and inlining method bodies.
5. **Speculative De-optimization (Bailout):** JavaScript lacks static typing. If TurboFan optimizes a function assuming operands are integers, and the code subsequently invokes it with a String or an Object, the engine aborts the speculative optimization, invalidates the compiled machine code, and "bails out" back to Ignition bytecode.

```javascript
// Monomorphic vs Megamorphic Optimization Example
function calculateArea(shape) {
  // TurboFan optimizes property access shape.width and shape.height
  // using an Inline Cache (IC) pointing to a single hidden class (Shape Map).
  return shape.width * shape.height;
}

const rect1 = { width: 10, height: 20 }; // Hidden Class C0
const rect2 = { width: 15, height: 30 }; // Hidden Class C0 -> MONOMORPHIC (Extremely Fast!)
calculateArea(rect1);
calculateArea(rect2);

const skewed = { height: 40, width: 25 }; // Hidden Class C1 (Different property insertion order!)
calculateArea(skewed); // POLYMORPHIC -> Inline Cache misses, performance degrades

const circle = { radius: 10 }; // Missing width/height entirely -> BAILOUT to interpreter!
calculateArea(circle);
```

---

### 2. Execution Contexts, The Call Stack & Variable Lifecycle

The fundamental unit of execution in JavaScript is the **Execution Context (EC)**. An Execution Context is an internal runtime abstraction that encapsulates the environment within which a script or function evaluates.

#### Anatomy of an Execution Context
Every Execution Context consists of three operational components:
1. **Variable Environment (VE):** Manages local variable declarations declared with `var`, function declarations, and the `arguments` object.
2. **Lexical Environment (LE):** Identical in structure to the Variable Environment, but specifically manages block-scoped identifiers (`let`, `const`, `class`) and holds a reference to the **Outer Lexical Environment** (the Scope Chain).
3. **ThisBinding:** Resolves the dynamic reference of the `this` keyword based on the call-site invocation pattern.

{{ media:v8-execution-context-diagram }}

#### The Two-Phase Execution Lifecycle
Whenever JavaScript enters a scope (the script root or a function call), the engine executes in two distinct phases:

##### Phase 1: Creation Phase (Memory Allocation & Hoisting)
The engine scans the code block before executing a single statement:
- **Global Object Binding:** In the browser, the Global Execution Context (GEC) creates `window` and binds `this` to `window`.
- **Function Declarations:** The engine allocates memory for the function identifier and stores the entire function definition in memory. Functions can therefore be called before their syntactic declaration.
- **`var` Declarations:** Variables declared with `var` are allocated memory and initialized immediately to `undefined`.
- **`let` and `const` Declarations:** Identifiers declared with `let` and `const` are allocated in the Lexical Environment record, but **remain uninitialized**. Accessing them prior to their lexical declaration throws a `ReferenceError`. This span between scope entry and declaration is the **Temporal Dead Zone (TDZ)**.

##### Phase 2: Execution Phase (Evaluation & Assignment)
The engine executes code synchronously, line-by-line:
- Values are evaluated and assigned to variables in memory.
- Function invocations push a new **Function Execution Context (FEC)** onto the **Call Stack**.
- When a function returns or terminates, its FEC is popped from the Call Stack.

```javascript
// Demonstration of Hoisting and the Temporal Dead Zone (TDZ)
console.log(hoistedVar); // Output: undefined (Allocated and initialized to undefined)
// console.log(hoistedLet); // ReferenceError: Cannot access 'hoistedLet' before initialization (TDZ!)

var hoistedVar = "I am var";
let hoistedLet = "I am let";

console.log(declaredFunction()); // Output: "Callable anywhere!"

// Function Declaration: Hoisted entirely with implementation
function declaredFunction() {
  return "Callable anywhere!";
}

// Function Expression: Identifier 'expressedFunction' is hoisted as var (undefined)!
// expressedFunction(); // TypeError: expressedFunction is not a function
var expressedFunction = function() {
  return "Expressed";
};
```

---

### 3. Lexical Scoping, Scope Chains & The Closure Mechanism

#### Lexical Scope & Identifier Resolution
JavaScript is **lexically scoped** (also known as static scoping). The scope of an identifier is determined strictly by its geographic position within the source code text at parse time, *not* by where or how the function is called at runtime.

Every Lexical Environment contains:
- An **Environment Record**: Maps identifier names to values.
- A **Reference to Outer Environment**: Points directly to the Lexical Environment where the function was physically defined.

When the engine resolves a variable identifier, it performs an $O(d)$ lookup along the **Scope Chain** (where $d$ is the nesting depth):
$$	ext{Local Environment} \longrightarrow 	ext{Outer Environment}_1 \longrightarrow \dots \longrightarrow 	ext{Global Environment} \longrightarrow 	ext{ReferenceError}$$

```javascript
const globalVar = "GLOBAL";

function outerScope() {
  const outerVar = "OUTER";

  function innerScope() {
    const innerVar = "INNER";
    // Scope chain lookup:
    // 1. innerVar found in Local Environment
    // 2. outerVar found in Outer Environment (outerScope)
    // 3. globalVar found in Outer.Outer Environment (Global)
    return `${innerVar} -> ${outerVar} -> ${globalVar}`;
  }

  return innerScope;
}

const execFn = outerScope();
console.log(execFn()); // "INNER -> OUTER -> GLOBAL"
```

#### The Closure Memory Retention Mechanism
A **Closure** is the formal combination of a function bundled together with references to its enclosing lexical state (the Lexical Environment).

In traditional stack-based architectures (such as standard C), local variables reside in stack frames. When a function returns, its stack frame is popped, and its memory is reclaimed immediately. 

In JavaScript:
1. When `outerScope()` completes execution, its Execution Context is popped from the Call Stack.
2. However, because `innerScope` maintains an active outer reference to `outerScope`'s Lexical Environment, the V8 Garbage Collector (GC) recognizes an active reference path from the root.
3. Therefore, V8 promotes the referenced variables from the transient stack to the **persistent Memory Heap**.
4. The inner function retains access to these variables for its entire lifetime.

```javascript
// Enterprise Pattern: Encapsulated State Machine using Closures
function createSecureTokenManager(initialSubject, secretSalt) {
  // Private variables residing in the Heap Lexical Environment
  let subject = initialSubject;
  let accessCount = 0;
  const createdAt = Date.now();

  function hashToken(data) {
    let hash = 0;
    const combined = data + secretSalt;
    for (let i = 0; i < combined.length; i++) {
      hash = (hash << 5) - hash + combined.charCodeAt(i);
      hash |= 0; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16);
  }

  // Public Interface returned as an object literal
  return {
    generateToken: function() {
      accessCount++;
      return `TKN-${hashToken(subject + accessCount)}-${Date.now()}`;
    },
    getMetrics: function() {
      return {
        subject: subject,
        accessCount: accessCount,
        uptimeMs: Date.now() - createdAt
      };
    },
    rotateSubject: function(newSubject) {
      if (typeof newSubject !== "string" || newSubject.trim() === "") {
        throw new TypeError("Subject must be a non-empty string");
      }
      subject = newSubject.trim();
    }
  };
}

const authManager = createSecureTokenManager("user-9842", "k8!mX9#z");
console.log(authManager.generateToken()); // TKN-3d84f...
console.log(authManager.getMetrics());    // { subject: 'user-9842', accessCount: 1, ... }
console.log(authManager.secretSalt);     // undefined (Private variable is strictly inaccessible!)
```

---

### 4. Data Types, First-Class Functions & The Prototype Object Model

#### ECMAScript Type Taxonomy
ECMAScript standardizes 8 fundamental data types divided into two operational categories:

| Category | Type | Storage Semantics | Equality Mechanics |
| :--- | :--- | :--- | :--- |
| **Primitives** | `Number` | IEEE 754 64-bit double precision float | Value equality (`===`) |
| | `BigInt` | Arbitrary precision integer | Value equality (`===`) |
| | `String` | Immutable sequence of 16-bit code units | Value equality (`===`) |
| | `Boolean` | Logical entity (`true` / `false`) | Value equality (`===`) |
| | `Undefined` | Primitive value assigned to uninitialized variables | Value equality (`===`) |
| | `Null` | Intentional absence of any object value | Value equality (`===`) |
| | `Symbol` | Unique, immutable identifier token | Unique identity equality |
| **Reference** | `Object` | Allocated on the Memory Heap; variables hold memory pointers | Reference identity equality |

*Note on `typeof null`:* The expression `typeof null === "object"` is a legacy bug dating back to JavaScript's first 1995 implementation, where type tags were stored in the lower 3 bits of a 32-bit word, with `000` representing objects; since null was a NULL pointer (`0x00`), it erroneously reported `"object"`.

#### First-Class Functions & Execution Invocation Patterns
In JavaScript, functions are **first-class citizens**—they can be assigned to variables, stored in data structures, passed as arguments, and returned from other functions.

```javascript
// Function Invocation Forms and 'this' Binding Semantics

// 1. Default Binding (Standalone invocation)
function showContext() {
  return this;
}
console.log(showContext()); // window (in non-strict mode) or undefined (in 'use strict')

// 2. Implicit Binding (Method invocation)
const service = {
  name: "AuthCluster",
  log() {
    return `Service: ${this.name}`;
  }
};
console.log(service.log()); // "Service: AuthCluster" (this bound to service)

// 3. Explicit Binding (call, apply, bind)
const standalone = service.log;
console.log(standalone.call({ name: "PaymentCluster" })); // "Service: PaymentCluster"

// 4. Lexical 'this' (Arrow Functions)
// Arrow functions do NOT possess their own 'this', 'arguments', or 'prototype'.
// They lexically capture 'this' from their enclosing scope.
const logger = {
  prefix: "[GATEWAY]",
  messages: ["REQ_200", "ERR_500"],
  print() {
    this.messages.forEach(msg => {
      // 'this' refers to 'logger' because arrow function does not create a new this-binding
      console.log(`${this.prefix} ${msg}`);
    });
  }
};
logger.print();
```

#### Prototypal Inheritance vs Class Sugar
Unlike classical object-oriented languages (Java, C++) where classes serve as blueprints and objects are concrete instances instantiated in distinct memory layouts, JavaScript utilizes **Prototypal Inheritance**. 

Every JavaScript object contains an internal slot `[[Prototype]]` (exposed in browsers via `__proto__`) which points to another object. When a property or method is accessed on an object, the engine searches the object itself; if missing, it traverses the **Prototype Chain** until it reaches `Object.prototype`, whose `[[Prototype]]` is `null`.

```javascript
// Prototypal Chain Mechanics under ES6 Class Syntax
class NetworkNode {
  constructor(nodeId, ipAddress) {
    this.nodeId = nodeId;
    this.ipAddress = ipAddress;
    this.status = "OFFLINE";
  }

  ping() {
    return `Node ${this.nodeId} (${this.ipAddress}) is ${this.status}`;
  }
}

class EdgeRouter extends NetworkNode {
  constructor(nodeId, ipAddress, throughputGbps) {
    super(nodeId, ipAddress); // Invokes NetworkNode.prototype.constructor
    this.throughputGbps = throughputGbps;
  }

  routePacket(packet) {
    return `Routing packet ${packet.id} via ${this.ipAddress} at ${this.throughputGbps} Gbps`;
  }
}

const router = new EdgeRouter("RTR-01", "192.168.1.1", 100);

// Prototypal Link Inspection:
console.log(router.__proto__ === EdgeRouter.prototype);               // true
console.log(EdgeRouter.prototype.__proto__ === NetworkNode.prototype); // true
console.log(NetworkNode.prototype.__proto__ === Object.prototype);     // true
console.log(Object.prototype.__proto__ === null);                      // true
```

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Execution Context State Trace
Trace the exact memory state transitions of the V8 engine executing the script below. Detail the contents of the Call Stack, Variable Environment, and Lexical Environment through both Phase 1 and Phase 2.

```javascript
// Script to trace
var systemKey = "SYS-101";
let authStatus = false;

function authenticate(user) {
  var sessionToken = "TOK-" + Math.random().toString(36).substring(7);
  let isValid = user.role === "ADMIN";

  function generateAuditLog() {
    return `AUDIT: [${systemKey}] User ${user.name} valid=${isValid} (${sessionToken})`;
  }

  return generateAuditLog;
}

const auditFn = authenticate({ name: "Grace", role: "ADMIN" });
const logMessage = auditFn();
```

##### Step-by-Step State Transition Table:
| Step | Active Execution Context | Call Stack (Top to Bottom) | Memory / Scope State |
| :--- | :--- | :--- | :--- |
| **1. GEC Creation** | Global Execution Context | `[GEC]` | `VE: { systemKey: undefined, authenticate: <func> }`<br>`LE: { authStatus: <uninitialized/TDZ>, auditFn: <TDZ>, logMessage: <TDZ> }`<br>`ThisBinding: window` |
| **2. GEC Execution (Lines 1-2)** | GEC | `[GEC]` | `VE.systemKey = "SYS-101"`<br>`LE.authStatus = false` |
| **3. Call `authenticate()`** | Function Execution Context (`authenticate`) | `[FEC: authenticate, GEC]` | **Creation Phase:**<br>`VE: { sessionToken: undefined, generateAuditLog: <func> }`<br>`LE: { user: {name: "Grace", role: "ADMIN"}, isValid: <TDZ> }`<br>`Outer Reference: GEC`<br>**Execution Phase:**<br>`sessionToken = "TOK-xyz"`, `isValid = true` |
| **4. Return `generateAuditLog`** | GEC | `[GEC]` | FEC popped from Call Stack. Because `generateAuditLog` closes over `{ sessionToken, isValid, user }`, this Lexical Environment is persisted in the **Heap**. `auditFn` assigned function reference in GEC. |
| **5. Call `auditFn()`** | Function Execution Context (`generateAuditLog`) | `[FEC: generateAuditLog, GEC]` | **Execution Phase:** Evaluates template literal. Resolves `systemKey` via Scope Chain $	o$ GEC. Resolves `user`, `isValid`, `sessionToken` via Closure Scope $	o$ Heap. Returns `"AUDIT: [SYS-101] User Grace valid=true (TOK-xyz)"`. |
| **6. Termination** | GEC | `[GEC]` | `LE.logMessage` assigned result string. GEC terminates upon script completion. |

---

#### Level 2 — Scaffolded Bug-Fix: The Shared Reference Asynchronous Closure Bug
In client-side data dashboards, asynchronous pollers and click dispatchers frequently exhibit subtle closure bugs when iterating over collections.

##### The Broken Code:
```javascript
// BROKEN: An engineer attempted to create a fleet of 5 metrics pollers
function initMetricsPollers() {
  var pollers = [];

  for (var i = 0; i < 5; i++) {
    pollers.push(function() {
      console.log(`Polling server endpoint index: ${i}`);
    });
  }

  return pollers;
}

const pollerFleet = initMetricsPollers();
// Executing the pollers:
pollerFleet[0](); // Expected: 0, Actual: 5!
pollerFleet[1](); // Expected: 1, Actual: 5!
pollerFleet[2](); // Expected: 2, Actual: 5!
pollerFleet[3](); // Expected: 3, Actual: 5!
pollerFleet[4](); // Expected: 4, Actual: 5!
```

<details>
<summary><strong>View Root Cause Analysis & Refactored Enterprise Solutions</strong></summary>

##### Root Cause Analysis:
1. `var i` possesses **function scope**, hoisted to the Variable Environment of `initMetricsPollers()`. There is only **one** instance of variable `i` allocated in memory.
2. The loop runs synchronously from `i = 0` through `i = 4`, terminating when `i = 5`.
3. All 5 closure functions pushed to the array capture a reference to the **exact same** lexical variable `i` in the heap.
4. When any poller function is subsequently executed, it resolves `i` from its enclosing lexical environment, which currently holds the final loop value `5`.

##### Refactored Solution 1: ES6 Block-Scoped `let` (Idiomatic & Efficient)
By changing `var i` to `let i`, the JavaScript engine creates a brand-new lexical scope binding for **each iteration** of the loop. Every closure captures its own independent instance of `i`:

```javascript
function initMetricsPollersModern() {
  const pollers = [];

  for (let i = 0; i < 5; i++) {
    // 'let i' creates a distinct Lexical Environment per loop iteration
    pollers.push(function() {
      console.log(`Polling server endpoint index: ${i}`);
    });
  }

  return pollers;
}

const modernFleet = initMetricsPollersModern();
modernFleet[0](); // Output: "Polling server endpoint index: 0"
modernFleet[4](); // Output: "Polling server endpoint index: 4"
```

##### Refactored Solution 2: Immediately Invoked Function Expression (IIFE) / Factory Pattern (ES5 Compatible)
In environments requiring legacy compatibility or functional currying, pass the variable into an IIFE to capture its primitive value by value into the parameter's local scope:

```javascript
function initMetricsPollersIIFE() {
  var pollers = [];

  for (var i = 0; i < 5; i++) {
    (function(capturedIndex) {
      pollers.push(function() {
        console.log(`Polling server endpoint index: ${capturedIndex}`);
      });
    })(i); // Pass current value of i into independent parameter scope
  }

  return pollers;
}
```
</details>

---

#### Level 3 — Production System Design: High-Throughput In-Memory LRU Cache with TTL & Event Closures

##### Architectural Challenge:
Design an enterprise-grade In-Memory **Least Recently Used (LRU) Cache** with Time-To-Live (TTL) expiration. The cache must provide:
1. $O(1)$ time complexity for both `get(key)` and `put(key, value, ttlMs)`.
2. Automatic eviction of the least recently accessed item when the cache exceeds capacity $C$.
3. Lazy expiration of stale keys on access and active background purging.
4. Strict encapsulation using closures and `WeakMap` to prevent external consumers from mutating internal doubly-linked list nodes.

<details>
<summary><strong>View Production Architectural Implementation</strong></summary>

```javascript
/**
 * Production LRU Cache with TTL and Encapsulated State
 * Implemented via Doubly Linked List + Hash Map (JavaScript Map)
 */
const LRUCache = (function() {
  // Private node class for doubly linked list
  class Node {
    constructor(key, value, expiresAt) {
      this.key = key;
      this.value = value;
      this.expiresAt = expiresAt;
      this.prev = null;
      this.next = null;
    }

    isExpired() {
      return this.expiresAt !== null && Date.now() > this.expiresAt;
    }
  }

  // WeakMap ensuring strict encapsulation of private fields
  const privateState = new WeakMap();

  class Cache {
    constructor(capacity = 100, cleanupIntervalMs = 60000) {
      if (!Number.isInteger(capacity) || capacity <= 0) {
        throw new TypeError("Capacity must be a positive integer");
      }

      // Initialize dummy sentinel head and tail nodes
      const head = new Node(null, null, null);
      const tail = new Node(null, null, null);
      head.next = tail;
      tail.prev = head;

      // Encapsulate internal data structures in WeakMap
      privateState.set(this, {
        capacity: capacity,
        map: new Map(), // Maps key -> Node pointer: O(1) lookups
        head: head,
        tail: tail,
        stats: { hits: 0, misses: 0, evictions: 0, expirations: 0 }
      });

      // Background TTL cleanup poller
      if (cleanupIntervalMs > 0) {
        const intervalId = setInterval(() => this.purgeExpired(), cleanupIntervalMs);
        if (typeof intervalId.unref === "function") {
          intervalId.unref(); // Prevent poller from holding Node.js event loop alive
        }
      }
    }

    // Helper: Remove node from its current position in doubly linked list
    _detach(state, node) {
      node.prev.next = node.next;
      node.next.prev = node.prev;
    }

    // Helper: Insert node at head of doubly linked list (Most Recently Used)
    _attachHead(state, node) {
      node.next = state.head.next;
      node.prev = state.head;
      state.head.next.prev = node;
      state.head.next = node;
    }

    get(key) {
      const state = privateState.get(this);
      const node = state.map.get(key);

      if (!node) {
        state.stats.misses++;
        return undefined;
      }

      // Check TTL expiration
      if (node.isExpired()) {
        this._detach(state, node);
        state.map.delete(key);
        state.stats.expirations++;
        state.stats.misses++;
        return undefined;
      }

      // Move accessed node to head (MRU)
      this._detach(state, node);
      this._attachHead(state, node);
      state.stats.hits++;
      return node.value;
    }

    put(key, value, ttlMs = null) {
      const state = privateState.get(this);
      const expiresAt = ttlMs ? Date.now() + ttlMs : null;

      // Update existing key
      if (state.map.has(key)) {
        const existingNode = state.map.get(key);
        existingNode.value = value;
        existingNode.expiresAt = expiresAt;
        this._detach(state, existingNode);
        this._attachHead(state, existingNode);
        return;
      }

      // Evict Least Recently Used (Tail node) if capacity reached
      if (state.map.size >= state.capacity) {
        const lruNode = state.tail.prev;
        if (lruNode !== state.head) {
          this._detach(state, lruNode);
          state.map.delete(lruNode.key);
          state.stats.evictions++;
        }
      }

      // Create new node and attach at head
      const newNode = new Node(key, value, expiresAt);
      state.map.set(key, newNode);
      this._attachHead(state, newNode);
    }

    purgeExpired() {
      const state = privateState.get(this);
      const now = Date.now();
      let purgedCount = 0;

      for (const [key, node] of state.map.entries()) {
        if (node.expiresAt !== null && now > node.expiresAt) {
          this._detach(state, node);
          state.map.delete(key);
          purgedCount++;
        }
      }
      state.stats.expirations += purgedCount;
      return purgedCount;
    }

    getStats() {
      const state = privateState.get(this);
      const totalRequests = state.stats.hits + state.stats.misses;
      return {
        ...state.stats,
        size: state.map.size,
        capacity: state.capacity,
        hitRatio: totalRequests === 0 ? 0 : (state.stats.hits / totalRequests).toFixed(4)
      };
    }
  }

  return Cache;
})();

// Verification and execution
const cache = new LRUCache(3);
cache.put("session_1", { user: "Alice" });
cache.put("session_2", { user: "Bob" });
cache.put("session_3", { user: "Charlie" });

console.log(cache.get("session_1")); // Hits session_1; moves it to MRU position
cache.put("session_4", { user: "David" }); // Evicts session_2 (LRU)!

console.log(cache.get("session_2")); // undefined (Evicted)
console.log(cache.get("session_3")); // { user: 'Charlie' }
console.log(cache.getStats());      // { hits: 2, misses: 1, evictions: 1, ... }
```

##### Complexity Verification:
- **Time Complexity:** 
  - `get(key)`: $O(1)$ lookup in `Map` + $O(1)$ pointer adjustments in doubly linked list.
  - `put(key, value)`: $O(1)$ insertion in `Map` + $O(1)$ list splice.
- **Space Complexity:** $O(C)$ where $C$ is the specified maximum capacity.
- **Encapsulation:** Complete. Internal pointers (`head`, `tail`, `map`) are unreachable from instances, shielded by the module closure and `WeakMap`.
</details>

---

### 6. Reference Video Lecture
Review this foundational engineering lecture exploring the V8 call stack, execution contexts, and the memory creation phase:

{{ media:execution-context-video }}
