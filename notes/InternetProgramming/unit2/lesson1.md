# Lesson 1 — Document Architecture, Text Semantics & Tabular Data Structures

> [!NOTE]
> **Learning Outcomes:**
> - Deconstruct the fundamental **HTML5 document execution lifecycle**, analyzing the Document Type Declaration (`<!DOCTYPE html>`), parser modes (Standard vs. Quirks Mode), and the conversion of tokens into an in-memory **DOM Tree**.
> - Engineer robust `<head>` metadata architectures, specifying character sets (`UTF-8`), responsive viewport constraints, Open Graph protocols, and canonical link relations.
> - Apply semantic text elements according to their formal W3C specifications, distinguishing stylistic tags from semantic phrase markers (`<strong>` vs `<b>`, `<em>` vs `<i>`, `<time datetime="...">`).
> - Model complex, multi-dimensional relational data structures using semantic tables (`<table>`, `<caption>`, `<thead>`, `<tbody>`, `<tfoot>`, `<colgroup>`), mastering `rowspan` and `colspan` algorithms.
> - Implement WCAG 2.1 accessible table architectures utilizing `scope="col|row"` and `headers` ID bindings to enable flawless screen reader matrix traversal.

{{media:html-crash-video}}

{{media:dom-tabular-diagram}}

---

## 1. The Anatomy of an HTML5 Document & DOM Tree Construction

HTML (HyperText Markup Language) is the structural ontology of the World Wide Web. Rather than defining visual aesthetics, HTML constructs a **semantic tree of objects** that the browser rendering engine parses, styles, and executes.

### 1.1 Document Type Declaration & Parser Modes
Every modern web document must begin with the **Document Type Declaration (Doctype)**:

```html
<!DOCTYPE html>
```

#### Why does the Doctype exist if HTML5 is no longer SGML-based?
Historically, in HTML 4.01, the doctype referenced a complex Standard Generalized Markup Language (SGML) Document Type Definition (DTD). In HTML5, `<!DOCTYPE html>` exists strictly for **browser parser mode switching**:
1. **Standard Mode**: When `<!DOCTYPE html>` is present, the browser enforces the full modern W3C/WHATWG HTML5 and CSS specifications.
2. **Quirks Mode**: If the doctype is omitted or malformed, modern browser engines (Blink, Gecko, WebKit) fall back to simulating the buggy, non-standard layout behaviors of Netscape Navigator 4 and Internet Explorer 5 (e.g., incorrect box model calculations where padding was absorbed inside width).
3. **Almost Standards Mode**: Triggered by transitional doctypes, rendering table cells with legacy vertical alignment quirks.

### 1.2 The Root Document Envelope
An enterprise HTML5 document conforms to the following minimal architectural skeleton:

```html
<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <!-- Document Metadata & Resource Pre-fetching -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Software Engineering Department | AASTU</title>
    
    <!-- SEO & Machine Directives -->
    <meta name="description" content="Official portal of the Department of Software Engineering at Addis Ababa Science and Technology University.">
    <link rel="canonical" href="https://aastu.edu.et/departments/se">

    <!-- Open Graph Protocol for Social Graph Ingestion -->
    <meta property="og:title" content="AASTU Software Engineering">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://aastu.edu.et/departments/se">
    <meta property="og:image" content="https://aastu.edu.et/assets/og-preview.jpg">

    <!-- Stylesheets & Fonts -->
    <link rel="stylesheet" href="/css/main.css">
  </head>
  <body>
    <!-- Visible Document Tree -->
    <main>
      <h1>Department of Software Engineering</h1>
      <p>Advancing computational theory and distributed systems engineering.</p>
    </main>
  </body>
</html>
```

#### Critical `<head>` Directives Analyzed:
- `<html lang="en">`: Declares the natural language of the document. Crucial for screen reader voice synthesis (selecting English phoneme libraries) and search engine language filtering.
- `<meta charset="UTF-8">`: Declares character encoding. **Must appear within the first 1,024 bytes of the document** so the parser can decode subsequent text without character corruption (Mojibake). UTF-8 encodes over 149,000 Unicode characters.
- `<meta name="viewport" content="width=device-width, initial-scale=1.0">`: Eliminates the legacy mobile browser default behavior of assuming a 980px desktop canvas and zooming out. Instructs the viewport to match the physical device width at a 1:1 scale factor.

### 1.3 How Browsers Construct the Document Object Model (DOM)
When raw bytes arrive from the network socket, the browser's HTML parser executes a 4-phase transformation:

```
 [Raw Bytes: 3C 68 74 6D...] ──> [Characters: "<html>"] ──> [Tokens: StartTag "html"]
                                                                   │
                                                                   ▼
 [Render Tree] ◄── [DOM Tree (Graph)] ◄── [Node Objects: HTMLHtmlElement]
```

1. **Byte Stream Decoding**: Translates raw network bytes into Unicode characters based on the specified `charset="UTF-8"`.
2. **Tokenization (Lexical Analysis)**: A state machine converts characters into discrete tokens (`StartTag: <html>`, `EndTag: </html>`, `CharacterTokens`, `Comment`).
3. **Tree Construction**: The parser processes tokens according to the HTML tree construction algorithm, instantiating C++ objects implementing the W3C DOM Node interfaces (`HTMLHtmlElement`, `HTMLHeadElement`, `HTMLBodyElement`) and attaching them into a parent-child pointer graph.
4. **DOM Tree**: The resulting in-memory tree represents both the document's structure and the live programmatic API accessible via JavaScript (`document.querySelector(...)`).

---

## 2. Text Semantics & Typography Architecture

HTML provides semantic tags that communicate document hierarchy and textual significance to search engines, screen readers, and automated web scrapers.

```
 Block-Level Elements (Form structural vertical flow; break onto new lines)
 ├── Headings: <h1> to <h6> (Hierarchical document outline)
 ├── Paragraphs: <p> (Blocks of prose)
 ├── Blockquotes: <blockquote cite="..."> (External long-form citations)
 └── Code Blocks: <pre><code> (Preformatted code preserving whitespace)

 Inline-Level Elements (Flow horizontally within block text; do not break line)
 ├── Importance: <strong> (Strong importance, urgency, or seriousness)
 ├── Emphasis: <em> (Stress emphasis changing the sentence meaning)
 ├── Highlighting: <mark> (Contextual search relevance highlight)
 ├── Temporal Data: <time datetime="YYYY-MM-DD"> (Machine-readable dates)
 └── Abbreviations: <abbr title="..."> (Acronym expansions)
```

### 2.1 The Heading Hierarchy Rule
Headings (`<h1>` through `<h6>`) communicate the **conceptual table of contents** of the document:
- **Exactly one `<h1>` per page**: Represents the primary subject matter of the entire document.
- **Never skip heading levels for visual sizing**: Jumping from `<h2>` directly to `<h4>` breaks the accessibility outline tree for assistive technologies. If an `<h2>` looks visually too large, modify its font size in CSS—never downgrade the semantic tag to `<h4>`!

### 2.2 Semantic Elements vs. Stylistic Equivalents
In modern software engineering, presentational tags are deprecated in favor of semantic equivalents:

| Semantic Element | Deprecated / Presentational Equivalent | Architectural & Screen Reader Difference |
| :--- | :--- | :--- |
| **`<strong>`** | `<b>` (Bold) | `<b>` merely applies CSS `font-weight: bold` with zero semantic weight. `<strong>` indicates critical importance; screen readers announce it with elevated pitch and inflection. |
| **`<em>`** | `<i>` (Italic) | `<i>` merely applies italic slant. `<em>` indicates verbal stress emphasis, altering the semantic meaning of the sentence. |
| **`<del>` / `<ins>`** | `<s>` / `<u>` | `<del>` and `<ins>` explicitly document document revisions and editorial tracking (with optional `cite` and `datetime` attributes). |
| **`<time>`** | `<span>` | Enables search engines to parse calendar events, indexing deadlines into Google Calendar/Search. |

```html
<p>
  Registration for the 
  <abbr title="Addis Ababa Science and Technology University">AASTU</abbr> 
  autumn semester begins on 
  <time datetime="2026-10-15T09:00:00+03:00">October 15, 2026</time>. 
  <strong>Failure to submit documents before the deadline will result in forfeiture of enrollment.</strong>
</p>
```

---

## 3. List Architectures & Hierarchical Topologies

HTML defines three distinct list types, each serving unique informational topologies:

```
                            HTML List Topologies
                            /        |         \
                           /         |          \
                 Unordered (<ul>)  Ordered (<ol>) Description (<dl>)
                 Non-sequential    Strict numeric  Key-Value association
                 groupings (nav)   workflow steps  (glossaries, specs)
```

### 3.1 Unordered Lists (`<ul>`)
Used when the physical sequence of items does not alter their semantic meaning (e.g. navigation links, feature matrices).
```html
<nav aria-label="Department Navigation">
  <ul>
    <li><a href="/curriculum">Curriculum</a></li>
    <li><a href="/faculty">Faculty Staff</a></li>
    <li><a href="/research">Research Labs</a></li>
  </ul>
</nav>
```

### 3.2 Ordered Lists (`<ol>`)
Used when sequence is mandatory (e.g., software compilation steps, algorithmic execution recipes). Supports attributes:
- `start="5"`: Begins numbering at integer 5.
- `reversed`: Renders numbers in descending order (useful for top-10 countdowns).
- `type="A|a|I|i|1"`: Defines numeral system (default is decimal `1`).

### 3.3 Description Lists (`<dl>`, `<dt>`, `<dd>`)
An essential element for software engineering architectures, used to structure **Name-Value Groups** (glossaries, server metadata, API parameters):
- `<dl>`: Description List container.
- `<dt>`: Description Term (the key or name).
- `<dd>`: Description Details (the corresponding value).

```html
<dl class="server-metrics">
  <dt>Kernel Architecture</dt>
  <dd>Linux 6.8.0-45-generic x86_64</dd>

  <dt>HTTP Gateway</dt>
  <dd>Nginx 1.24.0 (Ubuntu LTS)</dd>

  <dt>Active Connection Pooling</dt>
  <dd>PostgreSQL 16.2 via PgBouncer</dd>
</dl>
```

---

## 4. Complex Tabular Data Engineering & Accessibility (WCAG 2.1)

Tables in HTML (`<table>`) are engineered exclusively for **two-dimensional relational data**. 

> [!CAUTION]
> **The Table Layout Anti-Pattern:**
> In the late 1990s, web developers abused nested `<table>` tags for visual page layouts. In modern engineering, using tables for layout is a catastrophic anti-pattern: it bloats DOM depth, ruins responsive reflow, and destroys accessibility for screen readers. **Tables must only be used for tabular data.**

### 4.1 Complete Semantic Table Anatomy
A production data table conforms to a multi-tiered hierarchy:

```
 <table>
 ├── <caption> (Accessible title and summary of table contents)
 ├── <colgroup> (Column group specification for bulk formatting)
 │    ├── <col class="col-id">
 │    └── <col class="col-data" span="3">
 ├── <thead> (Header rows containing column labels)
 │    └── <tr> ──> <th> (Table Header cells with scope="col")
 ├── <tbody> (Core data rows containing records)
 │    └── <tr> ──> <th> (Row Header with scope="row") + <td> (Data cells)
 └── <tfoot> (Summary, total, or aggregate footer rows)
      └── <tr> ──> <td> or <th>
```

### 4.2 Multi-Dimensional Merging: `colspan` and `rowspan`
- `colspan="N"`: Merges a cell horizontally across $N$ adjacent columns.
- `rowspan="N"`: Merges a cell vertically across $N$ consecutive rows.

```html
<table class="academic-report">
  <caption>Software Engineering Year 3 Academic Standing Matrix</caption>
  
  <colgroup>
    <col class="student-meta" span="2">
    <col class="grades" span="3">
    <col class="standing">
  </colgroup>

  <thead>
    <tr>
      <!-- Two-level nested column headers -->
      <th scope="col" rowspan="2">Student ID</th>
      <th scope="col" rowspan="2">Full Name</th>
      <th scope="colgroup" colspan="3">Course Performance (Grade Points)</th>
      <th scope="col" rowspan="2">Academic Status</th>
    </tr>
    <tr>
      <th scope="col">DSA (SWEG3101)</th>
      <th scope="col">OOP (SWEG3102)</th>
      <th scope="col">IP (SWEG3103)</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <th scope="row">ETS0412/13</th>
      <td>Abebe Kebede</td>
      <td>4.0 (A)</td>
      <td>3.75 (A-)</td>
      <td>4.0 (A)</td>
      <td>Dean's List</td>
    </tr>
    <tr>
      <th scope="row">ETS0413/13</th>
      <td>Sara Mohammed</td>
      <td>3.5 (B+)</td>
      <td>4.0 (A)</td>
      <td>3.75 (A-)</td>
      <td>Good Standing</td>
    </tr>
  </tbody>

  <tfoot>
    <tr>
      <th scope="row" colspan="2">Cohort Average GPA</th>
      <td>3.75</td>
      <td>3.88</td>
      <td>3.88</td>
      <td>Accredited</td>
    </tr>
  </tfoot>
</table>
```

### 4.3 Screen Reader Navigation: The `scope` and `headers` Attributes
Screen reader users do not perceive a visual two-dimensional grid; they navigate sequentially via keyboard controls (e.g. `Ctrl + Alt + Arrow Keys`).
1. **The `scope` Attribute**:
   - `scope="col"`: Associates the `<th>` cell with all data cells in the column below it.
   - `scope="row"`: Associates the `<th>` cell with all data cells in the row to its right.
   - `scope="colgroup"` / `scope="rowgroup"`: Associates header cells with multi-column or multi-row structural spans.
2. **The `headers` Attribute (For Irregular Matrices)**:
   When tables have non-rectangular, irregular multi-level headers, the `scope` attribute becomes ambiguous. In such cases, assign a unique `id` to each `<th>`, and link each `<td>` explicitly via a space-separated list of IDs:
   ```html
   <th id="term1">Fall 2026</th>
   <th id="dsa">DSA (SWEG3101)</th>
   ...
   <td headers="term1 dsa">3.75</td>
   ```
   When the screen reader reaches that `<td>`, it synthesizes speech automatically: *"Fall 2026, DSA (SWEG3101): 3.75"*, providing complete contextual comprehension.

---

## 5. Architectural Summary & System Design Matrix

| HTML Component | Semantic Intent | Primary Failure Mode | WCAG / Engineering Standard |
| :--- | :--- | :--- | :--- |
| **`<!DOCTYPE html>`** | Parser mode activation | Triggering Quirks Mode; non-standard box model calculations | WHATWG Living Standard |
| **`<meta name="viewport">`** | Responsive canvas control | Tiny unreadable text on mobile screens; artificial 980px desktop zoom | Responsive Web Design Principle |
| **Headings (`<h1>`-`<h6>`)** | Document structural outline | Skipping levels; using multiple `<h1>`s per document | WCAG 2.1 Success Criterion 1.3.1 |
| **`<table>`** | Relational tabular data | Using tables for visual layout; missing `<th scope="...">` | WCAG 2.1 Success Criterion 1.3.2 |
| **`<time>`** | Machine-readable temporal representation | Malformed `datetime` strings preventing automated parsing | ISO 8601 Temporal Standard |

---

## 6. Progressive Engineering Practice (3-Tier)

### Level 1: Document Tree & Screen Reader Traversal Trace
Examine the following HTML snippet and trace the exact DOM tree parent-child pointers and the accessibility announcements generated for the data cell:

```html
<table aria-describedby="fee-desc">
  <caption>Tuition Fee Structure</caption>
  <thead>
    <tr>
      <th scope="col" id="prog">Academic Program</th>
      <th scope="col" id="fee">Tuition (ETB)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row" id="se">Software Engineering</th>
      <td headers="prog se fee">12,500.00</td>
    </tr>
  </tbody>
</table>
<p id="fee-desc">Fees are calculated per semester for non-sponsored candidates.</p>
```

**Walkthrough:**
1. **DOM Tree Mapping**:
   - `HTMLTableElement` $\to$ contains `HTMLTableCaptionElement`, `HTMLTableSectionElement` (`thead`), and `HTMLTableSectionElement` (`tbody`).
   - `tbody` $\to$ contains `HTMLTableRowElement` $\to$ contains `HTMLTableHeaderCellElement` and `HTMLTableCellElement`.
2. **Screen Reader Vocalization**:
   - When entering the table: Screen reader announces *"Table: Tuition Fee Structure. Fees are calculated per semester for non-sponsored candidates. 2 columns, 1 row."*
   - When focus moves to the cell `12,500.00`: Assistive software resolves the `headers` attribute bindings and announces: *"Academic Program, Software Engineering, Tuition (ETB): 12,500.00"*.

---

### Level 2: Scaffolded Refactoring — Remediating Div-Soup into Semantic Architecture
> **Scenario:** A frontend junior developer wrote the following course list component using generic non-semantic `<div>` tags and inline click handlers:
> ```html
> <div class="course-item">
>   <div class="title" style="font-weight: bold; font-size: 24px;">Internet Programming I</div>
>   <div class="desc">Covers web architectures, HTTP wire formats, and client-side engineering.</div>
>   <div class="meta">Published: 2026-10-03 | Code: SWEG3103</div>
>   <div class="topics">
>     <div>Topic 1: DNS and TCP/IP</div>
>     <div>Topic 2: HTTP Specifications</div>
>     <div>Topic 3: Semantic HTML5</div>
>   </div>
>   <div class="btn" onclick="enroll('SWEG3103')">Enroll Now</div>
> </div>
> ```
> 
> Identify the **architectural deficiencies** in accessibility, keyboard navigation, and machine discoverability, and refactor the component into production-grade HTML5.

<details>
<summary>Click to view solution & analysis</summary>

#### Architectural Deficiencies:
1. **Zero Keyboard Accessibility**: The `<div class="btn">` cannot be focused via the `Tab` key, nor can it be activated via `Enter` or `Space`. It is completely invisible to keyboard-only and screen reader users.
2. **Broken Document Outline**: The title is styled with bold and large font, but search engines and screen readers do not recognize it as a heading landmark.
3. **Missing Machine-Readable Dates**: The date string `2026-10-03` is plain text; automated indexing bots cannot parse it as an ISO 8601 timestamp.
4. **List Abuse**: The topics are separate `<div>` tags instead of an ordered or unordered list, preventing screen readers from announcing *"List of 3 items"*.

#### Production-Hardened Refactoring:
```html
<article class="course-card" aria-labelledby="course-sweg3103">
  <header>
    <h2 id="course-sweg3103">Internet Programming I</h2>
    <p class="course-meta">
      Course Code: <span class="badge">SWEG3103</span> | 
      Published: <time datetime="2026-10-03">October 3, 2026</time>
    </p>
  </header>

  <p class="course-description">
    Covers web architectures, HTTP wire formats, and client-side engineering.
  </p>

  <section aria-label="Course Curriculum Outline">
    <h3>Curriculum Modules</h3>
    <ol>
      <li>DNS and TCP/IP Architecture</li>
      <li>HTTP Protocol Specifications</li>
      <li>Semantic HTML5 & Accessible Engineering</li>
    </ol>
  </section>

  <footer>
    <button type="button" class="btn-enroll" onclick="enroll('SWEG3103')">
      Enroll in Course <span class="visually-hidden">SWEG3103</span>
    </button>
  </footer>
</article>
```

</details>

---

### Level 3: Advanced System Design — Designing an Accessible, Scalable Data Grid
> **Scenario:** Design the HTML and accessibility architecture for an enterprise university registrar dashboard that displays 50,000 student academic records in a responsive, sortable, filterable data grid.
> 
> Specify the structural HTML hierarchy, the ARIA grid role bindings, and how live dynamic updates (such as asynchronous GPA recalculations or sorting column changes) are communicated to assistive screen readers without page reload.

<details>
<summary>Click to view architectural solution</summary>

#### Enterprise Architectural Blueprint: Virtualized ARIA Data Grid

```
 +-------------------------------------------------------------------------------+
 | <div role="region" aria-labelledby="grid-title" tabindex="0">                 |
 |   <h2 id="grid-title">Registrar Master Academic Registry (50,000 Records)</h2>|
 |                                                                               |
 |   <table role="grid" aria-rowcount="50000" aria-colcount="6">                 |
 |     <thead>                                                                   |
 |       <tr role="row" aria-rowindex="1">                                       |
 |         <th role="columnheader" aria-sort="ascending" tabindex="0">ID</th>   |
 |         <th role="columnheader" aria-sort="none" tabindex="-1">Full Name</th> |
 |         <th role="columnheader" aria-sort="none" tabindex="-1">Department</th>|
 |         <th role="columnheader" aria-sort="descending" tabindex="-1">CGPA</th>|
 |       </tr>                                                                   |
 |     </thead>                                                                  |
 |     <tbody role="rowgroup">                                                   |
 |       <!-- Virtualized Viewport: Only 25 DOM rows rendered at any instant --> |
 |       <tr role="row" aria-rowindex="1042">                                    |
 |         <td role="gridcell" tabindex="0">ETS0412/13</td>                      |
 |         <td role="gridcell" tabindex="-1">Abebe Kebede</td>                   |
 |         <td role="gridcell" tabindex="-1">Software Engineering</td>           |
 |         <td role="gridcell" tabindex="-1">3.92</td>                           |
 |       </tr>                                                                   |
 |     </tbody>                                                                  |
 |   </table>                                                                    |
 |                                                                               |
 |   <!-- Live Region for Asynchronous Status Announcements -->                  |
 |   <div aria-live="polite" aria-atomic="true" class="visually-hidden" id="sr">  |
 |     Filtered to 450 Software Engineering records. Sorted by CGPA descending.  |
 |   </div>                                                                      |
 +-------------------------------------------------------------------------------+
```

#### Key Architectural Implementations:
1. **DOM Virtualization with Virtual Row Indices**:
   - Rendering 50,000 physical `<tr>` nodes creates 300,000 DOM elements, crashing mobile browser memory and stalling the rendering engine.
   - The UI virtualizes the grid, rendering only ~25 rows visible in the viewport.
   - **Accessibility Fix**: Add `aria-rowcount="50000"` to the table, and assign dynamic `aria-rowindex="N"` to each rendered row. When a user navigates to a student record, the screen reader announces: *"Row 1,042 of 50,000"*, maintaining full spatial awareness.
2. **Keyboard Roving Tabindex Grid Traversal**:
   - Following W3C Grid design patterns, only the single active cell has `tabindex="0"`; all other cells have `tabindex="-1"`.
   - JavaScript listens for `ArrowUp`, `ArrowDown`, `ArrowLeft`, and `ArrowRight` to shift focus instantaneously across coordinates $(x, y)$.
3. **Non-Disruptive Live Updates (`aria-live="polite"`)**:
   - When a user filters the grid (e.g., selecting "Software Engineering"), an asynchronous fetch updates the viewport.
   - A hidden live region (`aria-live="polite"`) is updated with text: *"Filtered to 450 records. Showing rows 1 to 25."*
   - The screen reader announces this status update politely as soon as the user pauses typing, without interrupting active speech.

</details>
