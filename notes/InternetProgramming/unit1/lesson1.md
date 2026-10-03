# Lesson 1 — Internet Architecture, TCP/IP Protocol Stack & DNS Lifecycle

> [!NOTE]
> **Learning Outcomes:**
> - Contrast the physical **Internet infrastructure** with the application-layer **World Wide Web (WWW)** and trace the evolution of distributed hypertext systems.
> - Deconstruct the **TCP/IP 4-layer protocol stack** and analyze the transport-layer mechanisms (TCP sliding windows, 3-way handshake) that guarantee reliable byte streams for web applications.
> - Formalize the syntax and semantic constraints of **URIs, URLs, and URNs** according to RFC 3986, including character normalization, reserved sets, and percent-encoding algorithms.
> - Trace the end-to-end **DNS resolution lifecycle**, distinguishing recursive resolver queries from iterative root, TLD, and authoritative nameserver delegations.
> - Evaluate DNS record topologies (A, AAAA, CNAME, MX, TXT, PTR) and design robust caching strategies using Time-To-Live (TTL) engineering.

{{media:dns-video}}

{{media:dns-architecture-diagram}}

---

## 1. The Global Network Fabric: Internet vs. World Wide Web

A foundational requirement for professional software engineering is maintaining a strict conceptual separation between the **underlying internetwork transport infrastructure** and the **application protocols operating on top of it**.

```
 +--------------------------------------------------------------------------------+
 |                           World Wide Web (WWW)                                 |
 |        Application-layer hypermedia network: HTTP, HTML, CSS, JavaScript       |
 +--------------------------------------------------------------------------------+
                                         │
                                         ▼ (operates over)
 +--------------------------------------------------------------------------------+
 |                             The Internet                                       |
 |   Global decentralized network of networks communicating via TCP/IP protocols  |
 +--------------------------------------------------------------------------------+
```

### 1.1 The Internet: Infrastructure and Packet Switching
Originating in 1969 with the US Department of Defense's **ARPANET**, the Internet was engineered to solve the vulnerability of circuit-switched telecommunications networks. In traditional circuit switching (like legacy telephony), a physical path is dedicated between two endpoints for the duration of the communication session. If any intermediate switch fails, the entire circuit is severed.

The Internet replaced circuit switching with **packet switching**:
- Data streams are fragmented into independent units called **packets** (datagrams).
- Each packet contains addressing metadata (source and destination IP addresses) alongside its payload.
- Intermediate network devices (**routers**) inspect each packet independently and forward it along the optimal path available at that microsecond (**dynamic routing** via BGP and OSPF).
- Packets can travel completely disparate geographical routes and arrive out of order; the receiving host's transport layer is responsible for reassembly.

### 1.2 The World Wide Web: The Hypermedia Revolution
Conceived in 1989 by Sir Tim Berners-Lee at CERN, the **World Wide Web (WWW)** is an application-level distributed information system layered atop the Internet. Berners-Lee integrated three foundational innovations:
1. **Hypertext Transfer Protocol (HTTP)**: A stateless, request-response application protocol for transmitting hypermedia documents.
2. **HyperText Markup Language (HTML)**: A structured text document formatting language featuring non-linear references (**hyperlinks**) that connect arbitrary documents across different physical servers globally.
3. **Uniform Resource Identifier (URI)**: A universal addressing scheme giving every document on the planetary network a unique, unambiguous address.

---

## 2. The TCP/IP Protocol Suite & Layer Abstractions

Modern network communication relies on layered abstractions. The **TCP/IP model** (RFC 1122) organizes protocols into four functional layers, operating as an encapsulation pipeline.

```
 +------------------------+--------------------------------------------------------+
 | TCP/IP Layer           | Protocols & Responsibilities                           |
 +------------------------+--------------------------------------------------------+
 | 4. Application Layer   | HTTP/1.1, HTTP/2, HTTP/3, DNS, SMTP, SSH, WebSockets   |
 |                        | Direct interface with software; user data serialization|
 +------------------------+--------------------------------------------------------+
 | 3. Transport Layer     | TCP (Reliable stream), UDP (Datagram, Low latency)     |
 |                        | End-to-end process-to-process delivery; Port numbers   |
 +------------------------+--------------------------------------------------------+
 | 2. Internet Layer      | IPv4, IPv6, ICMP, ARP                                  |
 |                        | Host-to-host logical routing across diverse networks   |
 +------------------------+--------------------------------------------------------+
 | 1. Network Access Layer| Ethernet (802.3), Wi-Fi (802.11), Fiber Optic (DOCSIS) |
 |                        | Physical frame transmission over local hardware links  |
 +------------------------+--------------------------------------------------------+
```

### 2.1 Protocol Encapsulation: The Onion Model
When a web browser executes an HTTP request, data moves vertically downward through the stack on the sending machine, with each layer wrapping the higher-layer payload in its own protocol header:

```
 Application:  [ HTTP Request Body ]
 Transport:    [ TCP Header (Src Port, Dst Port: 80, Seq#) | HTTP Payload ]
 Internet:     [ IP Header (Src IP, Dst IP: 197.156.73.161) | TCP Segment ]
 Link/Network: [ Ethernet Header (Src MAC, Dst MAC) | IP Packet | Frame Check ]
```

Upon receipt by the destination server, the reverse process occurs (**decapsulation**), stripping headers until the pure application payload reaches the server process.

### 2.2 Transport Layer Mechanics: TCP vs. UDP
Every internet communication operates over one of two primary transport protocols:

| Architectural Metric | Transmission Control Protocol (TCP) | User Datagram Protocol (UDP) |
| :--- | :--- | :--- |
| **Connection State** | Connection-oriented (Requires explicit handshake) | Connectionless (No handshake; fire-and-forget) |
| **Reliability** | Guaranteed delivery (Retransmission via ACKs) | Best-effort (Packets may be dropped silently) |
| **Ordering** | Strict sequential ordering via sequence numbers | Unordered (Packets arrive in arbitrary order) |
| **Flow & Congestion** | Dynamic sliding window; Congestion control algorithms | None (Transmits at application generation rate) |
| **Header Overhead** | 20–60 bytes per segment | 8 bytes fixed header |
| **Web Use Cases** | Standard HTTP/1.1 and HTTP/2 traffic, WebSockets | DNS lookups, WebRTC media, HTTP/3 (QUIC) |

#### The TCP 3-Way Handshake
Before a single byte of HTTP data can traverse a TCP socket, the client and server must synchronize their sequence numbers and establish connection parameters through a **3-way handshake**:

```
 Client (Browser)                                    Server (Web Server)
       │                                                      │
       │─────── 1. SYN (seq=x, MSS=1460, WinScale=7) ────────>│ (LISTEN)
       │                                                      │
       │<────── 2. SYN-ACK (seq=y, ack=x+1) ──────────────────│ (SYN-RCVD)
       │                                                      │
(ESTAB)│─────── 3. ACK (ack=y+1) + [HTTP GET /index.html] ───>│ (ESTABLISHED)
       │                                                      │
```

1. **SYN (Synchronize)**: Client selects a randomized Initial Sequence Number (ISN) $x$ and sends a segment with the SYN flag set.
2. **SYN-ACK**: Server acknowledges client's ISN by returning $ACK = x + 1$, and generates its own random ISN $y$, returning a segment with both SYN and ACK flags set.
3. **ACK**: Client acknowledges server's ISN with $ACK = y + 1$. In modern implementations (**TCP Fast Open** or immediate pipelining), the client can attach the initial HTTP payload directly to this third packet, saving one Round Trip Time (RTT).

---

## 3. Universal Addressing: URI, URL, and URN Specifications (RFC 3986)

In distributed web engineering, resource identification is governed by **RFC 3986: Uniform Resource Identifier (URI): Generic Syntax**.

```
                         URI (Uniform Resource Identifier)
                                /                 \
                               /                   \
        URL (Uniform Resource Locator)       URN (Uniform Resource Name)
    Identifies resource via location/access   Identifies resource persistently by name
    (e.g., https://aastu.edu.et/index.php)     (e.g., urn:isbn:978-0134685991)
```

### 3.1 The Canonical URL Anatomy
Every URL conforms to a strict hierarchical grammar:

$$\text{URI} = \text{scheme} \text{ ":" } [ \text{"//" authority} ] \text{ path } [ \text{"?" query} ] [ \text{"\#" fragment} ]$$

Where the `authority` component is decomposed into:

$$[\text{userinfo "@"}] \text{ host } [ \text{":" port} ]$$

Let us analyze a production URL in detail:

$$\underbrace{\text{https}}_{\text{Scheme}} \text{://} \underbrace{\text{admin:sec404@}}_{\text{User Info}} \underbrace{\text{portal.aastu.edu.et}}_{\text{Host / FQDN}} \underbrace{\text{:443}}_{\text{Port}} \underbrace{\text{/departments/se/students}}_{\text{Hierarchical Path}} \underbrace{\text{?semester=2\&sort=asc}}_{\text{Query String}} \underbrace{\text{\#honors}}_{\text{Fragment}}$$

1. **Scheme (`https`)**: Identifies the protocol and transport mechanisms used to fetch the resource (e.g., `http`, `https`, `ftp`, `mailto`, `wss`).
2. **User Info (`admin:sec404@`)**: Optional authentication credentials. *Security standard: Passing passwords in cleartext URLs is strictly prohibited in modern production due to browser history and access log exposure.*
3. **Host (`portal.aastu.edu.et`)**: The Fully Qualified Domain Name (FQDN) or literal IP address (IPv4 or `[IPv6]` enclosed in brackets).
4. **Port (`:443`)**: The transport-layer TCP port. If omitted, the default port for the scheme is implicitly bound (Port `80` for HTTP, Port `443` for HTTPS).
5. **Path (`/departments/se/students`)**: Hierarchical sequence of path segments identifying the resource within the server's namespace.
6. **Query (`?semester=2&sort=asc`)**: Non-hierarchical data passed to the resource handler as key-value pairs separated by ampersands (`&`).
7. **Fragment (`#honors`)**: An internal document anchor or client-side routing identifier. **Crucial architectural property: The fragment is never transmitted over the wire to the web server.** It is stripped by the browser and evaluated exclusively on the client machine.

### 3.2 Percent-Encoding (URL Encoding)
URLs are constrained to a restricted subset of the US-ASCII character set. Characters outside this set, or characters with structural meaning within the grammar, must be escaped using **Percent-Encoding** (`%HH`, where `HH` is the hexadecimal byte value):

- **Unreserved Characters**: `[A-Za-z0-9]`, `_`, `.`, `-`, `~`. These are never encoded.
- **Reserved Characters**: `:`, `/`, `?`, `#`, `[`, `]`, `@`, `!`, `$`, `&`, `'`, `(`, `)`, `*`, `+`, `,`, `;`, `=`. These serve as syntactic delimiters. If used as literal data (e.g., an ampersand inside a query parameter value), they **must** be percent-encoded:
  - Space $\to$ `%20` (or `+` in `application/x-www-form-urlencoded` query contexts)
  - `&` $\to$ `%26`
  - `=` $\to$ `%3D`
  - `?` $\to$ `%3F`

---

## 4. The Domain Name System (DNS): Distributed Name Resolution

While humans navigate the web using intuitive domain names (`aastu.edu.et`), IP routing hardware routes packets exclusively using numeric binary IP addresses (`197.156.73.161` for IPv4 or `2001:db8::1` for IPv6).

The **Domain Name System (DNS)** is the planet-scale, globally distributed, fault-tolerant hierarchical database that performs bidirectional translation between names and network addresses.

### 4.1 The Hierarchical DNS Namespace
The DNS namespace forms an inverted tree rooted at the invisible **Root Zone** (represented syntactically by a trailing dot: `aastu.edu.et.`):

```
                                  . (Root Zone)
                     ┌───────────────┴───────────────┐
                   .com                            .et (Country-Code TLD)
             ┌───────┴───────┐                       │
          google.com     github.com                .edu.et (Second-Level Domain)
                                                     │
                                                 aastu.edu.et (Domain)
                                                     │
                                            portal.aastu.edu.et (Subdomain)
```

1. **Root Nameservers (`.`)**: At the apex of the hierarchy. Managed across 13 logical root cluster addresses (`a.root-servers.net` through `m.root-servers.net`), distributed across thousands of physical server nodes globally via **IP Anycast** routing.
2. **Top-Level Domain (TLD) Nameservers**: Handle specific top-level domains:
   - **Generic TLDs (gTLDs)**: `.com`, `.org`, `.net`, `.io`.
   - **Country-Code TLDs (ccTLDs)**: `.et` (Ethiopia), `.uk` (United Kingdom), `.de` (Germany).
3. **Authoritative Nameservers**: The final authority for a domain. They hold the definitive **DNS Zone Files** configured by the domain owner and return official answers with an authoritative flag (`AA`).

### 4.2 Core DNS Resource Record (RR) Types
Every DNS zone file contains structured Resource Records:

```
; Example DNS Zone File for aastu.edu.et
$TTL 86400 ; Default TTL: 24 hours (86,400 seconds)
@       IN  SOA     ns1.aastu.edu.et. hostmaster.aastu.edu.et. (
                    2026100301 ; Serial number (YYYYMMDDNN)
                    7200       ; Refresh (2 hours)
                    3600       ; Retry (1 hour)
                    1209600    ; Expire (2 weeks)
                    3600 )     ; Negative Cache TTL (1 hour)

; Nameservers
@       IN  NS      ns1.aastu.edu.et.
@       IN  NS      ns2.aastu.edu.et.

; Address Records (IPv4 & IPv6)
@       IN  A       197.156.73.161
@       IN  AAAA    2001:db8:85a3::8a2e:370:7334
portal  IN  A       197.156.73.162

; Canonical Name (Alias)
www     IN  CNAME   aastu.edu.et.

; Mail Exchange Records (Priority: lower number = higher priority)
@       IN  MX  10  mail.aastu.edu.et.
@       IN  MX  20  backupmail.aastu.edu.et.

; Verification & Security Text Records
@       IN  TXT     "v=spf1 mx ip4:197.156.73.0/24 -all"
```

| Record Type | Name | Purpose & Engineering Semantics |
| :--- | :--- | :--- |
| **`A`** | Address Record | Maps a domain name to a 32-bit **IPv4 address** (`197.156.73.161`). |
| **`AAAA`** | Quad-A Record | Maps a domain name to a 128-bit **IPv6 address** (`2001:db8::1`). |
| **`CNAME`** | Canonical Name | Maps an alias to another true canonical domain name. *RFC Rule: A CNAME record cannot coexist with other records for the same label (e.g. root domain apex cannot be a CNAME).* |
| **`MX`** | Mail Exchange | Directs incoming email to designated mail transfer agents with integer priority ranking. |
| **`TXT`** | Text Record | Arbitrary human- or machine-readable text; universally used for domain ownership validation, SPF, DKIM, and DMARC email spoof prevention. |
| **`NS`** | Name Server | Delegates a DNS zone to use a specific authoritative nameserver. |
| **`PTR`** | Pointer Record | Resolves an IP address back into a domain name (**Reverse DNS lookup**, configured in `in-addr.arpa`). |

### 4.3 The End-to-End Resolution Pipeline
When a user navigates to `https://portal.aastu.edu.et/`:

```
 [Browser] ──(1. Cache?)──> [OS Resolver Cache] ──(2. Query)──> [Recursive Resolver]
                                                                        │
        ┌───────────────────────────────────────────────────────────────┤
        │ (3) Query "."                                                 ▼
        │<──(4) Referral to .et TLD NS ────────────────────── [Root Server (. )]
        │
        │ (5) Query ".et"
        │<──(6) Referral to aastu.edu.et NS ───────────────── [TLD Server (.et)]
        │
        │ (7) Query "portal.aastu.edu.et"
        │<──(8) A Record: 197.156.73.162 (TTL=3600) ───────── [Authoritative NS]
        │
        ▼
   Caches locally & returns IP to Client OS ──> Browser initiates TCP Handshake
```

1. **Local Cache Inspection**: The browser checks its internal DNS cache (Chrome: `chrome://net-internals/#dns`). If missed, it queries the Operating System DNS cache via the getaddrinfo system call. If missed, it checks the local `/etc/hosts` file.
2. **Recursive Query**: The OS client dispatches a **recursive query** to the configured DNS resolver (typically the ISP resolver, or public resolvers like Cloudflare `1.1.1.1` or Google `8.8.8.8`). In a recursive query, the client demands: *"Give me the final IP address or an error; do not make me do the legwork."*
3. **Iterative Resolution by the Resolver**: The recursive resolver executes a series of **iterative queries**:
   - Queries a Root Nameserver: Root responds, *"I do not know `portal.aastu.edu.et`, but here are the NS records for the `.et` TLD."*
   - Queries the `.et` TLD Nameserver: TLD responds, *"Here are the authoritative NS records for `aastu.edu.et`."*
   - Queries the `aastu.edu.et` Authoritative Nameserver: Authoritative server returns the `A` record for `portal.aastu.edu.et` (`197.156.73.162`) with a **Time-To-Live (TTL)** of 3600 seconds.
4. **Client Connection**: The resolver caches the record for 3600 seconds and returns it to the client OS, which returns it to the browser. The browser initiates the TCP socket handshake to `197.156.73.162:443`.

---

## 5. Architectural Summary & System Design Matrix

| Architectural Layer | Core Entity | Primary Standard / RFC | Failure Mode / Engineering Risk |
| :--- | :--- | :--- | :--- |
| **Application Layer** | HTTP / WWW | RFC 9110, RFC 9112 | High latency without HTTP keep-alive or connection reuse. |
| **Resource Addressing** | URI / URL | RFC 3986 | Insecure parameter passing in URLs; unencoded reserved characters. |
| **Name Resolution** | DNS | RFC 1034, RFC 1035 | DNS cache poisoning, TTL misconfigurations causing extended migration downtime. |
| **Transport Layer** | TCP / UDP | RFC 793, RFC 768 | Head-of-line blocking in TCP; socket exhaustion under high connection rates. |

---

## 6. Progressive Engineering Practice (3-Tier)

### Level 1: Protocol & URL Decomposition Walkthrough
Deconstruct the following production API webhook URL into its syntactic components according to RFC 3986, and explain why the password and fragment components represent specific architectural concerns:

```
https://service_bot:P%40ssw0rd!@internal.gateway.aastu.edu.et:8443/v2/webhooks/listener?format=json&retry=true#event-trace
```

**Deconstruction:**
- **Scheme**: `https` (Transport Layer Security over TCP).
- **Userinfo**: `service_bot:P%40ssw0rd!` (Username `service_bot`, password `P@ssw0rd!`, where `@` was percent-encoded to `%40` to avoid terminating the userinfo component prematurely).
- **Host**: `internal.gateway.aastu.edu.et` (FQDN resolving to an internal gateway).
- **Port**: `8443` (Non-standard HTTPS port).
- **Path**: `/v2/webhooks/listener` (Hierarchical resource target).
- **Query**: `?format=json&retry=true` (Parameter payload).
- **Fragment**: `#event-trace` (Client-side identifier).

**Architectural Concerns:**
1. *Credential Leakage*: Placing credentials in the authority component exposes secrets to proxy logs, browser histories, shell history, and HTTP `Referer` headers. Credentials must always be moved to the `Authorization: Bearer <token>` HTTP header.
2. *Fragment Handling*: The `#event-trace` fragment is **never transmitted across the network by HTTP client libraries**. If the server was expecting this fragment to identify an event category, the application architecture will fail silently.

---

### Level 2: Scaffolded Debugging — The Production DNS Migration Disaster
> **Scenario:** A software engineering team is preparing to migrate an enterprise university student portal from an on-premise server (`197.156.73.10`) to an AWS cloud environment (`52.14.88.200`).
> At 00:00 on Sunday, the DevOps engineer updates the DNS zone file `A` record:
> ```
> portal.aastu.edu.et.  86400  IN  A  52.14.88.200
> ```
> At 08:00 on Monday, the old on-premise server is decommissioned and powered off. Instantly, over 40% of the student body reports that the portal is down with `ERR_CONNECTION_REFUSED`, while the remaining 60% can access the new portal normally.
>
> Explain the root cause of this outage and specify the correct pre-migration TTL reduction procedure.

<details>
<summary>Click to view solution & analysis</summary>

#### Root Cause Analysis:
The outage was caused by **TTL (Time-To-Live) cache persistence**:
1. The `A` record had a TTL of **86,400 seconds (24 hours)**.
2. Global ISP recursive resolvers cache DNS query responses for the exact duration of the TTL.
3. Any student whose ISP resolver resolved `portal.aastu.edu.et` prior to the DNS change on Sunday will continue serving the old IP (`197.156.73.10`) from cache until that 24-hour window expires for that specific resolver.
4. When the old server was shut down 8 hours after the DNS change, thousands of client resolvers still had up to 16 hours remaining on their cached records, causing connection requests to fail.

#### Standard Pre-Migration Procedure:
1. **T - 72 hours (3 days prior)**: Lower the TTL of the `A` record from 86,400 seconds to **300 seconds (5 minutes)**:
   ```
   portal.aastu.edu.et.  300  IN  A  197.156.73.10
   ```
2. **Wait for 86,400 seconds**: Allow all existing resolver caches across the globe to expire their 24-hour entries and inherit the new 300-second TTL.
3. **Execution Window (00:00 Sunday)**: Update the IP address to the cloud host:
   ```
   portal.aastu.edu.et.  300  IN  A  52.14.88.200
   ```
   *Any clients accessing the old IP will transition to the new IP within a maximum of 5 minutes.*
4. **Post-Migration Stabilization**: Once metrics verify all traffic has safely cut over and stabilized, restore the TTL to 86,400 seconds to reduce DNS query load and ISP latency.

</details>

---

### Level 3: Advanced System Design — Multi-Region DNS Anycast & Split-Horizon Routing
> **Scenario:** Design a DNS routing topology for a university application that must satisfy two strict requirements:
> 1. Internal campus workstations on subnet `10.20.0.0/16` must resolve `grades.aastu.edu.et` directly to a high-speed internal intranet server (`10.20.5.50`) without traffic exiting through the public campus firewall.
> 2. Remote students connecting from external ISPs across Ethiopia or abroad must resolve `grades.aastu.edu.et` to public Anycast edge proxy addresses (`197.156.73.20`), with sub-second failover between data centers.
>
> Architect the DNS infrastructure to solve this requirement and evaluate potential cache pollution risks.

<details>
<summary>Click to view architectural solution</summary>

#### Architectural Blueprint: Split-Horizon (Split-Brain) DNS
To fulfill requirement 1, implement **Split-Horizon DNS** (using BIND views, Unbound, or AWS Route 53 Private Hosted Zones):

```
                        Client Query: "grades.aastu.edu.et"
                                         │
                         Is Client IP in 10.20.0.0/16?
                                  /            \
                           YES   /              \  NO
                                ▼                ▼
                  [Internal DNS View]      [Public DNS Authoritative]
                  Returns: 10.20.5.50      Returns: 197.156.73.20 (Anycast)
                  (Zero firewall hop)      (Encrypted HTTPS reverse proxy)
```

1. **Configuration**:
   - The campus DNS resolver evaluates the client's source IP address.
   - For queries originating within `10.20.0.0/16`, the internal zone file is served, mapping the hostname directly to the LAN IP `10.20.5.50`.
   - For all external queries, the public authoritative nameserver responds with the public Anycast VIP `197.156.73.20`.

#### BGP Anycast Routing for Remote Resilience:
To fulfill requirement 2:
- Multiple physical edge data centers (e.g., Addis Ababa DC and Hawassa DC) announce the **identical IP prefix** (`197.156.73.0/24`) to upstream telecom providers using Border Gateway Protocol (BGP).
- The global Internet routing mesh naturally routes packets to the topologically closest data center using BGP AS-Path length.
- If a data center suffers catastrophic failure, its BGP daemon withdraws the route announcement; Internet routers automatically reconverge traffic to the surviving site in seconds.

#### Cache Pollution Risk & Mitigation:
- *Risk*: A laptop inside the campus network resolves `10.20.5.50`. The student then disconnects, takes the laptop home, and connects to an external ISP. If the laptop's OS DNS cache has not expired, the browser will attempt to send packets to `10.20.5.50` over public Internet routing, which fails because RFC 1918 private IPs are non-routable over the public Internet.
- *Mitigation*: Ensure the internal DNS view specifies an aggressive TTL (e.g. 60–120 seconds) for internal intranet hostnames, or implement network change listeners in enterprise agent software that flushes the local OS resolver cache upon interface reconnection.

</details>
