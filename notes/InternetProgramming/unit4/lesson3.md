# Unit 4 — Client-Side Scripting with JavaScript, DOM & Event-Driven Architecture
## Lesson 3 — Event-Driven Architecture, The Browser Event Loop & Event Delegation

### 1. The Browser Concurrency Model: Event Loop, Microtasks & Macrotasks

A core architectural pillar of modern web applications is JavaScript's **single-threaded, event-driven concurrency model**. Unlike multi-threaded operating system environments (such as C++ or Java runtime threads) where concurrent threads access shared memory using mutex locks, JavaScript achieves high-throughput, non-blocking I/O through a single execution thread coordinated by the **Browser Event Loop**.

#### The Tripartite Runtime Architecture
The JavaScript browser runtime consists of three cooperating components:
1. **The Call Stack (V8 Engine):** A single Last-In, First-Out (LIFO) stack executing synchronous JavaScript bytecode frames one instruction at a time.
2. **Host Web APIs (Browser C++ Threads):** Background browser worker threads managing asynchronous operations—network sockets (`fetch`, `XMLHttpRequest`), hardware timers (`setTimeout`), filesystem I/O, and DOM event listeners. When an asynchronous operation completes, the Web API thread pushes the associated callback into a task queue.
3. **The Event Loop Coordinator:** A continuous execution loop that monitors the Call Stack. When the Call Stack becomes completely empty, the Event Loop coordinates the dequeuing and transfer of callbacks from task queues into the Call Stack for execution.

{{ media:event-loop-propagation-diagram }}

#### Task Queue Hierarchy: Microtasks vs Macrotasks
Not all asynchronous tasks possess equal priority. The WHATWG HTML specification partitions asynchronous tasks into two distinct queues with strict execution precedence rules:

```
+------------------------------------------------------------------------------------+
|                         THE EVENT LOOP TICK CYCLE                                  |
|                                                                                    |
|  [Execute 1 Macrotask from Macrotask Queue]                                        |
|         |                                                                          |
|         v                                                                          |
|  [DRAIN MICROTASK QUEUE COMPLETELY] <----+                                         |
|  (Promises, queueMicrotask, MutationObs) |                                         |
|         |                                | (Loop until microtask queue is EMPTY)   |
|         +--------------------------------+                                         |
|         |                                                                          |
|         v                                                                          |
|  [Check Rendering Pipeline]                                                        |
|  (requestAnimationFrame -> Recalculate Style -> Reflow -> Repaint)                 |
|         |                                                                          |
|         +--------------------------------> Repeat Loop Tick                        |
+------------------------------------------------------------------------------------+
```

##### 1. Microtask Queue (High Priority)
- **Sources:** `Promise.prototype.then()`, `catch()`, `finally()`, `queueMicrotask()`, and `MutationObserver` callbacks.
- **Drain Rule:** Whenever the Call Stack empties, the engine **drains the entire Microtask Queue to exhaustion** before yielding control. If a microtask enqueues another microtask, the nested microtask runs during the **exact same tick**.
- **Starvation Warning:** An infinite recursion of microtasks (`function loop() { Promise.resolve().then(loop); }`) will permanently starve the browser rendering engine and macrotask queue, completely freezing the user interface.

##### 2. Macrotask (Task) Queue (Normal Priority)
- **Sources:** `setTimeout()`, `setInterval()`, `setImmediate()` (Node.js), DOM event callbacks (`click`, `keydown`), and network I/O completions.
- **Execution Rule:** The Event Loop dequeues and executes **strictly ONE macrotask** per iteration tick. After executing that single macrotask, it immediately checks and drains the Microtask Queue, evaluates whether to perform a display render, and only then proceeds to the next macrotask.

```javascript
// Microtask vs Macrotask Execution Order Demonstration
console.log("1. Synchronous Script Start");

setTimeout(() => {
  console.log("5. Macrotask: setTimeout 0ms callback");
}, 0);

Promise.resolve()
  .then(() => {
    console.log("3. Microtask: Promise 1 resolved");
    queueMicrotask(() => {
      console.log("4. Microtask: Nested queueMicrotask callback");
    });
  });

console.log("2. Synchronous Script End");

// Strict Output Order:
// 1. Synchronous Script Start
// 2. Synchronous Script End
// 3. Microtask: Promise 1 resolved
// 4. Microtask: Nested queueMicrotask callback
// 5. Macrotask: setTimeout 0ms callback
```

---

### 2. W3C Event Flow Architecture: Capturing, Target & Bubbling

When a user interacts with a rendered web document (e.g., clicking a button nested inside an article, section, and body), the browser does not merely fire a single isolated event handler. It executes the **W3C DOM Level 2/3 Event Flow Pipeline**.

The W3C Event Flow partitions event propagation across three contiguous phases:

```
[Window] --------------------------------------------------------> [Window]
   |                                                                  ^
   | Phase 1: CAPTURING PHASE                                         | Phase 3: BUBBLING PHASE
   v (Trickles down from root to target)                              | (Bubbles up from target to root)
[Document]                                                        [Document]
   |                                                                  ^
   v                                                                  |
[<html>]                                                          [<html>]
   |                                                                  ^
   v                                                                  |
[<body>]                                                          [<body>]
   |                                                                  ^
   v                                                                  |
[<div class="card">]                                            [<div class="card">]
   |                                                                  ^
   v                                                                  |
   +------------------> [<button id="btn">] --------------------------+
                        Phase 2: TARGET PHASE
                        (Direct execution on target)
```

#### The Three Propagation Phases Explained
1. **Capturing Phase (Trickling Down):** The event originates at the `window` object and travels downward through the ancestor hierarchy (`document` $	o$ `<html>` $	o$ `<body>` $	o$ container elements) toward the target node. Event listeners configured with `{ capture: true }` fire during this phase.
2. **Target Phase:** The event arrives at the innermost element that was clicked (`event.target`). Listeners registered directly on this element execute.
3. **Bubbling Phase (Bubbling Up):** The event reverses direction and travels upward from the target element through all parent ancestors until reaching `window`. Standard listeners registered via `addEventListener(type, handler)` (which defaults to `{ capture: false }`) fire during this phase.

#### `event.target` vs `event.currentTarget`
Understanding this distinction is essential for mastering event propagation:
- **`event.target`:** The innermost element that **initiated the event** (the exact node under the mouse pointer).
- **`event.currentTarget`:** The element **whose event listener is currently running**.

```javascript
document.getElementById("parent-container").addEventListener("click", function(event) {
  console.log(`Target: ${event.target.tagName}`);               // E.g., "BUTTON"
  console.log(`CurrentTarget: ${event.currentTarget.tagName}`); // "DIV" (parent-container)
  console.log(this === event.currentTarget);                    // true (in standard functions)
});
```

#### Non-Bubbling Events
Certain DOM events represent state changes unique to a specific element and **do not bubble**:
- `focus` and `blur` (Use bubbling counterparts `focusin` and `focusout` instead).
- `mouseenter` and `mouseleave` (Use `mouseover` and `mouseout` if bubbling is required).
- `scroll` (Does not bubble on element containers; bubbles only on `document` / `window`).

---

### 3. `addEventListener` Configuration & Event Propagation Controls

#### The Modern Options Parameter
The W3C standard `addEventListener` method supports an `options` dictionary providing fine-grained runtime control:

```javascript
target.addEventListener(type, listener, {
  capture: false, // If true, listener executes during Capturing Phase
  once: false,    // If true, listener is automatically unregistered after firing once
  passive: false, // If true, indicates listener will NEVER invoke preventDefault()
  signal: abortController.signal // Allows declarative teardown via AbortController!
});
```

##### 1. High-Performance Scrolling with `passive: true`
In mobile and touch-screen browsers, touch and wheel events (`touchstart`, `touchmove`, `wheel`) can call `event.preventDefault()` to cancel scrolling. To check whether the listener calls `preventDefault()`, the browser main thread **must pause scrolling** until the JavaScript handler finishes executing, causing severe UI scroll stutter (jank).

Marking a touch or wheel listener as `passive: true` promises the browser that `preventDefault()` will never be called. The browser can immediately execute 60 FPS compositor scrolling on a background GPU thread without waiting for JavaScript!

##### 2. Modern Cleanup with `AbortSignal`
Historically, unbinding event listeners required saving function references for `removeEventListener`. Modern web development uses `AbortController` for clean, single-call component lifecycle unbinding:

```javascript
function setupDataStreamWidget() {
  const controller = new AbortController();
  const { signal } = controller;

  // Bind multiple listeners bound to the same AbortSignal
  window.addEventListener("resize", onResize, { signal });
  window.addEventListener("keydown", onKeyDown, { signal });
  document.getElementById("btn-submit").addEventListener("click", onSubmit, { signal });

  // Single teardown call removes ALL registered listeners instantaneously!
  return function teardown() {
    controller.abort();
  };
}
```

#### Propagation and Default Action Controls

| Control Method | Functional Scope |
| :--- | :--- |
| **`event.preventDefault()`** | Prevents the browser's built-in default behavior (e.g., stops a form `<button type="submit">` from triggering a full page reload, or stops an `<a>` tag from navigating). **Does NOT stop event propagation.** |
| **`event.stopPropagation()`** | Prevents the event from traveling further along the propagation path (halts subsequent capturing or bubbling). Other listeners registered on the **current element** will still execute. |
| **`event.stopImmediatePropagation()`** | Halts propagation AND immediately prevents any other event listeners registered on the **exact same element** from executing. |

```javascript
document.getElementById("modal-overlay").addEventListener("click", function(e) {
  closeModal();
});

document.getElementById("modal-content").addEventListener("click", function(e) {
  // Prevent clicks inside the white modal box from bubbling up to the overlay!
  e.stopPropagation();
});
```

---

### 4. The Event Delegation Pattern & Accessible Production Validation

#### Architectural Pattern: Event Delegation ($O(1)$ Memory)
In high-density dynamic user interfaces (e.g., e-commerce product grids, data tables, chat message feeds), attaching individual event listeners to thousands of child elements is an anti-pattern:
- **Memory Overhead:** Allocating 10,000 listener closures consumes tens of megabytes of Heap memory.
- **Dynamic Mutation Overhead:** Whenever new items are dynamically rendered or fetched via AJAX, newly created nodes must be individually bound.
- **Garbage Collection Pressure:** Removing elements without cleaning up listeners creates detached DOM memory leaks.

**The Solution:** Attach a **single** listener to a common ancestor element and exploit Phase 3 (Bubbling). Use `element.closest()` to identify the originating interactive child.

```javascript
// ENTERPRISE EVENT DELEGATION PATTERN
const transactionTable = document.getElementById("transaction-grid");

// Single listener handles unlimited past and future dynamic rows!
transactionTable.addEventListener("click", function(event) {
  // Find the closest ancestor matching the button selector
  const deleteBtn = event.target.closest("button.btn-delete");
  const editBtn = event.target.closest("button.btn-edit");

  if (deleteBtn && transactionTable.contains(deleteBtn)) {
    const row = deleteBtn.closest("tr");
    const transactionId = row.dataset.id;
    handleDeleteTransaction(transactionId, row);
    return;
  }

  if (editBtn && transactionTable.contains(editBtn)) {
    const row = editBtn.closest("tr");
    const transactionId = row.dataset.id;
    handleEditTransaction(transactionId, row);
    return;
  }
});

function handleDeleteTransaction(id, rowElement) {
  console.log(`Deleting transaction ID: ${id}`);
  rowElement.remove(); // No need to manually unbind listeners!
}
```

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Event Loop & Queue Execution Order Trace
Trace the exact sequence of console outputs for the code below. Construct a step-by-step state transition table showing the Call Stack, Microtask Queue, and Macrotask Queue.

```javascript
console.log("A");

setTimeout(() => {
  console.log("B");
  Promise.resolve().then(() => console.log("C"));
}, 0);

new Promise((resolve) => {
  console.log("D");
  resolve();
}).then(() => {
  console.log("E");
});

queueMicrotask(() => {
  console.log("F");
});

console.log("G");
```

##### Step-by-Step Transition State Table:
| Step | Action Taken | Call Stack | Microtask Queue | Macrotask Queue | Output |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Synchronous `console.log("A")` | `[log("A")]` | `[]` | `[]` | **A** |
| **2** | `setTimeout(..., 0)` scheduled | `[setTimeout]` | `[]` | `[CB_B]` | *(None)* |
| **3** | `new Promise` executor runs synchronously! | `[PromiseExecutor]` | `[]` | `[CB_B]` | **D** |
| **4** | `resolve()` queues `.then` callback | `[resolve]` | `[CB_E]` | `[CB_B]` | *(None)* |
| **5** | `queueMicrotask` enqueues callback | `[queueMicrotask]`| `[CB_E, CB_F]` | `[CB_B]` | *(None)* |
| **6** | Synchronous `console.log("G")` | `[log("G")]` | `[CB_E, CB_F]` | `[CB_B]` | **G** |
| **7** | Call Stack empty! Drain Microtask Queue: Run `CB_E` | `[CB_E]` | `[CB_F]` | `[CB_B]` | **E** |
| **8** | Run `CB_F` | `[CB_F]` | `[]` | `[CB_B]` | **F** |
| **9** | Microtask Queue drained! Dequeue 1 Macrotask: Run `CB_B` | `[CB_B]` | `[]` | `[]` | **B** |
| **10** | `CB_B` resolves a promise, queueing `CB_C` as microtask | `[CB_B]` | `[CB_C]` | `[]` | *(None)* |
| **11** | Macrotask finishes; drain Microtask Queue: Run `CB_C` | `[CB_C]` | `[]` | `[]` | **C** |

**Final Output Sequence:** `A -> D -> G -> E -> F -> B -> C`

---

#### Level 2 — Scaffolded Bug-Fix: Modal Dialog Background Click-Through & Memory Leaks
The modal component below suffers from two critical flaws:
1. Clicking inside the modal dialog accidentally closes the modal because the click bubbles to the overlay container.
2. Every time `openModal()` is called, new window `keydown` listeners are registered without unbinding, leaking memory and multiplying keyboard shortcuts.

##### The Broken Code:
```javascript
// BROKEN MODAL CONTROLLER
class ModalManager {
  constructor(overlayEl, contentEl) {
    this.overlay = overlayEl;
    this.content = contentEl;
    this._bindEvents();
  }

  _bindEvents() {
    // BUG 1: Clicking contentEl bubbles to overlay, closing modal immediately!
    this.overlay.addEventListener("click", () => {
      this.close();
    });
  }

  open() {
    this.overlay.style.display = "flex";
    // BUG 2: Adds a new listener on EVERY open without teardown!
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.close();
      }
    });
  }

  close() {
    this.overlay.style.display = "none";
  }
}
```

<details>
<summary><strong>View Root Cause Analysis & Enterprise Solution</strong></summary>

##### Refactored Robust Implementation:
```javascript
class ModalManagerSecure {
  constructor(overlayEl, contentEl) {
    this.overlay = overlayEl;
    this.content = contentEl;
    this.abortController = null;
    this._bindOverlay();
  }

  _bindOverlay() {
    this.overlay.addEventListener("click", (event) => {
      // Fix 1: Verify whether the actual click occurred on the backdrop overlay itself,
      // rather than blindly closing when child content bubbles up!
      if (event.target === this.overlay) {
        this.close();
      }
    });
  }

  open() {
    this.overlay.style.display = "flex";
    this.overlay.setAttribute("aria-hidden", "false");

    // Clean up any pre-existing listener signal
    if (this.abortController) {
      this.abortController.abort();
    }
    this.abortController = new AbortController();

    // Fix 2: Bind window keydown with AbortSignal for deterministic unbinding
    window.addEventListener(
      "keydown",
      (e) => {
        if (e.key === "Escape") {
          this.close();
        }
      },
      { signal: this.abortController.signal }
    );
  }

  close() {
    this.overlay.style.display = "none";
    this.overlay.setAttribute("aria-hidden", "true");

    // Immediately teardown keyboard listener on close
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }
}
```
</details>

---

#### Level 3 — Production System Design: High-Scale Interactive Kanban Board with Accessible Drag & Drop

##### Architectural Challenge:
Design an enterprise-grade **Kanban Board** with columns (*Backlog, In Progress, Review, Done*) supporting:
1. Event Delegation on the root board container ($O(1)$ memory consumption for thousands of cards).
2. Smooth Drag and Drop mechanics with visual ghost drop indicators.
3. Fully accessible keyboard drag-and-drop navigation via WAI-ARIA (`role="region"`, `aria-grabbed`, `aria-dropeffect`).
4. Reversible State Management (Undo/Redo command stack) tracking card column re-locations.

<details>
<summary><strong>View Production Architectural Implementation</strong></summary>

```javascript
/**
 * Production Enterprise Kanban Board Component
 * Features: Event Delegation, Accessible Keyboard Reordering, Command Pattern Undo/Redo
 */
class EnterpriseKanbanBoard {
  constructor(rootContainer) {
    this.root = rootContainer;
    this.historyStack = [];
    this.redoStack = [];
    this.draggedCard = null;

    this._initDom();
    this._bindEventDelegation();
  }

  _initDom() {
    this.root.className = "kanban-board-root";
    this.root.setAttribute("role", "application");
    this.root.setAttribute("aria-label", "Kanban Project Management Board");
  }

  _bindEventDelegation() {
    // 1. Drag & Drop Lifecycle using Event Delegation
    this.root.addEventListener("dragstart", (e) => {
      const card = e.target.closest(".kanban-card");
      if (!card) return;

      this.draggedCard = card;
      card.classList.add("is-dragging");
      card.setAttribute("aria-grabbed", "true");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", card.dataset.id);
    });

    this.root.addEventListener("dragend", (e) => {
      const card = e.target.closest(".kanban-card");
      if (!card) return;

      card.classList.remove("is-dragging");
      card.setAttribute("aria-grabbed", "false");
      this.draggedCard = null;

      // Clean up drop target highlights
      this.root.querySelectorAll(".kanban-column").forEach(col => {
        col.classList.remove("drag-over");
      });
    });

    this.root.addEventListener("dragover", (e) => {
      const column = e.target.closest(".kanban-column");
      if (!column || !this.draggedCard) return;

      e.preventDefault(); // Necessary to allow drop!
      e.dataTransfer.dropEffect = "move";
      column.classList.add("drag-over");
    });

    this.root.addEventListener("dragleave", (e) => {
      const column = e.target.closest(".kanban-column");
      if (column && !column.contains(e.relatedTarget)) {
        column.classList.remove("drag-over");
      }
    });

    this.root.addEventListener("drop", (e) => {
      const column = e.target.closest(".kanban-column");
      if (!column || !this.draggedCard) return;

      e.preventDefault();
      column.classList.remove("drag-over");

      const card = this.draggedCard;
      const targetList = column.querySelector(".card-list");
      const fromList = card.parentElement;

      if (targetList !== fromList) {
        this._executeMove(card, fromList, targetList);
      }
    });

    // 2. Accessible Keyboard Reordering (Space to pick up, Arrows to move, Enter to drop)
    this.root.addEventListener("keydown", (e) => {
      const card = e.target.closest(".kanban-card");
      if (!card) return;

      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        const isGrabbed = card.getAttribute("aria-grabbed") === "true";
        card.setAttribute("aria-grabbed", isGrabbed ? "false" : "true");
        card.classList.toggle("keyboard-grabbed", !isGrabbed);
      }

      if (card.getAttribute("aria-grabbed") === "true") {
        const currentColumn = card.closest(".kanban-column");
        if (e.key === "ArrowRight") {
          const nextCol = currentColumn.nextElementSibling;
          if (nextCol) {
            this._executeMove(card, card.parentElement, nextCol.querySelector(".card-list"));
            card.focus();
          }
        } else if (e.key === "ArrowLeft") {
          const prevCol = currentColumn.previousElementSibling;
          if (prevCol) {
            this._executeMove(card, card.parentElement, prevCol.querySelector(".card-list"));
            card.focus();
          }
        }
      }
    });
  }

  _executeMove(card, fromList, toList) {
    // Record command in history stack for Undo
    const command = {
      card: card,
      from: fromList,
      to: toList,
      execute() { this.to.appendChild(this.card); },
      undo() { this.from.appendChild(this.card); }
    };

    command.execute();
    this.historyStack.push(command);
    this.redoStack = []; // Clear redo stack on new action
  }

  undo() {
    const cmd = this.historyStack.pop();
    if (cmd) {
      cmd.undo();
      this.redoStack.push(cmd);
    }
  }

  redo() {
    const cmd = this.redoStack.pop();
    if (cmd) {
      cmd.execute();
      this.historyStack.push(cmd);
    }
  }
}
```

##### Architectural Verification:
- **Memory Scalability:** A single listener pair on `.kanban-board-root` manages infinite cards and columns.
- **Accessibility:** Full WAI-ARIA keyboard navigation compliant with screen readers.
- **State Reliability:** Reversible command pattern prevents data desynchronization.
</details>

---

### 6. Reference Video Lecture
Review this masterclass lecture on the JavaScript Event Loop, asynchronous task queues, and browser concurrency:

{{ media:event-loop-video }}
