# Lesson 2 — Hypermedia, Embedded Multimedia & Responsive Image Architectures

> [!NOTE]
> **Learning Outcomes:**
> - Engineer secure, accessible hypermedia links (`<a>`), analyzing fragment identifiers, protocol schemes (`mailto:`, `tel:`), and mitigating the critical **Reverse Tabnabbing** vulnerability via `rel="noopener noreferrer"`.
> - Compare digital image compression topologies (Raster vs. Vector: JPEG, PNG, WebP, AVIF, SVG) and design responsive asset delivery pipelines utilizing `srcset`, `sizes`, and the `<picture>` element.
> - Deconstruct native HTML5 multimedia architectures (`<video>`, `<audio>`), optimizing buffer lifecycles via the `preload` attribute, poster frames, and multi-source codec negotiation (H.264, VP9, AV1).
> - Author standardized **WebVTT (Web Video Text Tracks)** cue specifications and bind multi-lingual accessibility text tracks via the `<track>` element.
> - Eliminate Cumulative Layout Shift (CLS) in multimedia rendering by enforcing aspect-ratio reserving patterns.

{{media:picture-video}}

{{media:multimedia-picture-diagram}}

---

## 1. Hyperlink Engineering & Security Architecture

The hyperlink (`<a>` element, originating from "Anchor") is the fundamental connecting fabric of the World Wide Web, transforming isolated text documents into a unified, decentralized global hypermedia network.

### 1.1 Anatomy of a Production Hyperlink
```html
<a href="https://portal.aastu.edu.et/courses/sweg3103#syllabus" 
   target="_blank" 
   rel="noopener noreferrer" 
   type="text/html" 
   title="View the Internet Programming I course syllabus">
  Internet Programming Syllabus
</a>
```

#### Structural Attributes Analyzed:
1. **`href` (Hypertext Reference)**: The target destination. Can accept diverse URI schemes:
   - *Absolute URL*: `https://aastu.edu.et/research` (Full transport scheme, authority, and path).
   - *Root-Relative URL*: `/curriculum/dsa` (Inherits the current scheme and host; always starts at domain root).
   - *Document-Relative URL*: `../assets/report.pdf` (Evaluated relative to the directory path of the current document).
   - *Fragment Anchor*: `#syllabus` (Points to an element with `id="syllabus"` in the current document; scrolls the viewport instantaneously without network round-trips).
   - *Telecommunication Schemes*: `mailto:dean.se@aastu.edu.et?subject=Enrollment`, `tel:+251118960000`, `sms:+251911000000`.
2. **`download`**: Forces the browser to download the linked resource directly to local storage rather than opening it in a tab. Can specify a custom filename: `<a href="/exports/grades.csv" download="Fall2026_Grades.csv">`.
3. **`target`**: Governs the browsing context in which the linked URL will render:
   - `_self` (Default): Loads response into the current browsing context.
   - `_blank`: Spawns a new, independent top-level tab or window.
   - `_parent`: Loads into the parent frame context (when nested in iframes).
   - `_top`: Bypasses all nested frames, loading into the full top-level window.

### 1.2 The Critical "Reverse Tabnabbing" Vulnerability
When a link opens an external website with `target="_blank"`, a severe, often-overlooked security vulnerability emerges called **Reverse Tabnabbing** (CWE-1022).

```
 [User's Active Tab: portal.aastu.edu.et] ──(Clicks target="_blank" without rel)──> [New Tab: evil.com]
                       │                                                                   │
                       │                                                                   │ (JavaScript runs)
                       ▲                                                                   ▼
         [Tab rewritten to phishing-login.com!] <─────── window.opener.location = "..." ───┘
```

#### The Threat Execution Vector:
1. By default, when a new tab is created via `target="_blank"`, the new window retains an execution pointer to its parent window via the JavaScript DOM property `window.opener`.
2. The newly opened external page (which could be an external blog, discussion forum, or compromised resource) executes:
   ```javascript
   if (window.opener) {
     window.opener.location = "https://phishing-portal.com/login?session_timeout=1";
   }
   ```
3. While the user is browsing the new tab, their original, trusted background tab quietly navigates to a pixel-perfect fake login screen.
4. When the user closes the external tab and returns to what they believe was their university portal, they see a "Session Timed Out - Please Log In" prompt and unknowingly submit their enterprise credentials to the attacker!

#### The Engineering Remedy:
Always bind `rel="noopener noreferrer"` on all links targeting `_blank`:
- **`noopener`**: Instructs the browser engine to set `window.opener = null` in the child tab, completely isolating the two execution threads.
- **`noreferrer`**: In addition to enforcing `noopener`, strips the HTTP `Referer` header from the outgoing HTTP request, preventing the destination server from learning the originating private URL.

```html
<!-- ✅ PRODUCTION-SECURE EXTERNAL LINK -->
<a href="https://external-resource.org" target="_blank" rel="noopener noreferrer">
  External Documentation
</a>
```

---

## 2. Embedded Image Architectures & Modern Web Codecs

Images account for over **60% of total transfer weight** on median modern web pages. Optimizing image delivery is the single highest-impact performance optimization in web engineering.

### 2.1 Raster vs. Vector Graphics: The Architectural Division

```
                               Digital Image Topologies
                              /                        \
                    Raster Graphics                  Vector Graphics
             Grid of discrete color pixels            Mathematical Cartesian formulas
             (Lossy / Lossless pixel arrays)          (XML-based scalable curves)
             ├── JPEG (Photographs, lossy)           └── SVG (Logos, icons, UI shapes,
             ├── PNG (Lossless, transparency)             infinitely scalable, 0 pixelation)
             ├── WebP (Modern high-efficiency)
             └── AVIF (Next-gen AV1 compression)
```

| Image Format | Type | Compression Algorithm | Alpha (Transparency) | Animation | Production Use Case |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **SVG** | Vector | Deflate / XML Text | **YES** | **YES** | Logos, UI icons, system architecture diagrams. Infinitely scalable with zero byte increase. |
| **JPEG** | Raster | Discrete Cosine Transform (DCT) | NO | NO | Photographic imagery with complex gradients where file size must be constrained. |
| **PNG** | Raster | Lossless Deflate / LZ77 | **YES** | NO | Screenshots, diagrams requiring crisp text edges, graphics requiring pixel-perfect transparency. |
| **WebP** | Raster | VP8 Intra-frame prediction | **YES** | **YES** | Universal modern web standard. Delivers 26%–34% smaller footprints than equivalent PNG/JPEG. |
| **AVIF** | Raster | AV1 Intra-frame synthesis | **YES** | **YES** | Next-generation standard. Delivers up to 50% savings over JPEG with superior HDR color fidelity. |

### 2.2 The Anatomy of a High-Performance `<img>` Element
```html
<img src="/assets/campus-main.jpg" 
     alt="Aerial view of the AASTU campus administration block and engineering towers" 
     width="1200" 
     height="675" 
     loading="lazy" 
     decoding="async" 
     fetchpriority="high">
```

#### Performance Attributes Analyzed:
1. **`alt` (Alternative Text)**:
   - **Informative Images**: Must provide a concise, equivalent textual description of the visual information.
   - **Decorative Images**: Must use an empty string (`alt=""`). This informs screen readers to skip the element entirely. *Never omit the `alt` attribute entirely! If omitted, screen readers are forced to read aloud the raw image filename and URL path.*
2. **`width` and `height` (Aspect-Ratio Reservation)**:
   - **Eliminating Cumulative Layout Shift (CLS)**: If dimensions are omitted, the browser renders the image container with 0px height. When the image download completes 800ms later, the browser is forced to reflow the layout, pushing down all text below it.
   - By supplying explicit integer dimensions (`width="1200" height="675"`), modern browsers automatically calculate the CSS aspect ratio (`1200 / 675 = 16:9`) and reserve the exact spatial placeholder on the page *before* a single image byte arrives.
3. **`loading="lazy"`**: Defers downloading the image until it approaches within a designated threshold of the user's viewport, saving cellular data on long-scrolling pages.
4. **`decoding="async"`**: Allows the image decoder to unpack raster bytes asynchronously off the main execution thread, preventing UI jank.

---

## 3. Advanced Responsive Images: `srcset`, `sizes`, and `<picture>`

Modern web applications serve users across devices ranging from 320px mobile displays on slow 3G networks to 5K 32-inch desktop monitors on high-speed fiber. A single static image cannot serve both efficiently.

```
 [User Device Approaches Edge]
               │
               ▼
 Is Art Direction required? (Different cropping per screen size?)
        ├── YES ──> Use <picture> with <source media="...">
        └── NO  ──> Use <img> with srcset (w-descriptors) + sizes
```

### 3.1 Resolution Switching: `srcset` with `w`-Descriptors and `sizes`
Instead of using JavaScript to sniff screen sizes, we declare available image variations to the browser using `srcset` with width descriptors (`w`), and specify the visual layout footprint using `sizes`:

```html
<img srcset="/img/lab-320.jpg 320w,
             /img/lab-640.jpg 640w,
             /img/lab-1024.jpg 1024w,
             /img/lab-1920.jpg 1920w"
     sizes="(max-width: 600px) 100vw,
            (max-width: 1200px) 50vw,
            1024px"
     src="/img/lab-640.jpg"
     alt="Students conducting micro-architecture simulations in the computer lab"
     loading="lazy">
```

#### How the Browser Evaluates This Markup:
1. The browser inspects its viewport width (e.g. 500px).
2. It evaluates the `sizes` media conditions: `(max-width: 600px)` matches $\to$ the image will display at `100vw` (500 CSS pixels wide).
3. The browser checks the physical **Device Pixel Ratio (DPR)** of the display:
   - If DPR = 1 (Standard screen): Target physical width = $500 \times 1 = 500\text{px}$. Browser selects `lab-640.jpg`.
   - If DPR = 2 (Retina display): Target physical width = $500 \times 2 = 1000\text{px}$. Browser selects `lab-1024.jpg`.
4. *Result*: The client always downloads the exact optimal image resolution without JavaScript calculation!

### 3.2 Art Direction & Next-Gen Format Negotiation with `<picture>`
The `<picture>` wrapper is an architectural container that provides fine-grained control over **Art Direction** (different aspect ratios/crops for mobile vs desktop) and **Format Negotiation**:

```html
<picture>
  <!-- 1. Next-Gen Format Negotiation (AVIF -> WebP -> JPEG Fallback) -->
  <source type="image/avif" 
          srcset="/img/hero-large.avif 1200w, /img/hero-small.avif 600w" 
          sizes="(max-width: 768px) 100vw, 1200px">
  
  <source type="image/webp" 
          srcset="/img/hero-large.webp 1200w, /img/hero-small.webp 600w" 
          sizes="(max-width: 768px) 100vw, 1200px">

  <!-- 2. Art Direction: Serve square crop on mobile; panoramic landscape on desktop -->
  <source media="(max-width: 768px)" 
          srcset="/img/hero-mobile-square.jpg">

  <!-- 3. Mandatory Default Fallback Img -->
  <img src="/img/hero-desktop.jpg" 
       alt="Department of Software Engineering graduation ceremony" 
       width="1200" 
       height="675">
</picture>
```

The browser evaluates `<source>` tags from top to bottom and binds the first source whose `type` and `media` criteria are satisfied. If the browser does not recognize `<picture>`, it ignores the wrapper and safely renders the fallback `<img>`.

---

## 4. Native HTML5 Video & Audio Streaming Pipelines

Prior to HTML5, embedding audio or video required third-party, proprietary, security-vulnerable browser plugins (such as Adobe Flash or Microsoft Silverlight). HTML5 formalized multimedia as first-class DOM citizens via `<video>` and `<audio>`.

### 4.1 HTML5 Video Architecture
```html
<video controls 
       poster="/media/thumbnails/lecture1.jpg" 
       preload="metadata" 
       width="1280" 
       height="720"
       playsinline>
  <!-- Modern VP9/WebM for open web engines -->
  <source src="/media/lectures/ch2_lecture.webm" 
          type='video/webm; codecs="vp9, opus"'>
  
  <!-- H.264/MP4 for legacy and Apple Safari compatibility -->
  <source src="/media/lectures/ch2_lecture.mp4" 
          type='video/mp4; codecs="avc1.42E01E, mp4a.40.2"'>

  <!-- Timed Text Tracks for Accessibility -->
  <track src="/media/subtitles/ch2_en.vtt" 
         kind="subtitles" 
         srclang="en" 
         label="English Subtitles" 
         default>
  
  <track src="/media/subtitles/ch2_am.vtt" 
         kind="subtitles" 
         srclang="am" 
         label="Amharic Subtitles">

  <p>Your browser does not support HTML5 video streaming. 
     <a href="/media/lectures/ch2_lecture.mp4" download>Download the MP4 file directly</a>.
  </p>
</video>
```

#### Core Operational Attributes:
- **`controls`**: Displays native browser UI widgets (Play/Pause, scrub bar, volume, fullscreen).
- **`poster`**: Image displayed while the video is downloading or until the user hits Play.
- **`preload`**: Crucial bandwidth control policy:
  - `none`: Buffers zero media bytes until the user clicks Play (essential for mobile data savings).
  - `metadata` (Recommended): Fetches only metadata (video duration, audio track count, first frame dimensions).
  - `auto`: Eagerly buffers the initial video segments immediately upon page load.
- **`playsinline`**: Prevents mobile browsers (e.g. iOS Safari) from forcibly breaking into full-screen mode, allowing inline layout playback.

---

## 5. Timed Text Tracks & WebVTT Accessibility (W3C Standard)

Video accessibility is a legal and ethical mandate under **WCAG 2.1 (Level AA)**. The `<track>` element integrates standardized **WebVTT (Web Video Text Tracks)** files into the media pipeline.

### 5.1 Subtitles vs. Captions: The Critical Difference
- **`kind="subtitles"`**: Translates spoken dialogue into another language for viewers who can hear audio but do not understand the language spoken.
- **`kind="captions"` (Closed Captions - CC)**: Transcribes dialogue **plus non-speech audio cues** (e.g., *[Door slams]*, *[Upbeat orchestral music]*, *[Professor whispers]*). Designed specifically for deaf or hard-of-hearing users.

### 5.2 WebVTT File Format (`.vtt`)
A WebVTT file is a UTF-8 text document structured into time-coded blocks called **cues**:

```vtt
WEBVTT - Internet Programming I: Chapter 2 Lecture

1
00:00:01.000 --> 00:00:04.500 line:80% align:middle
Welcome to Unit 2: Web Development Using HTML.

2
00:00:05.200 --> 00:00:09.800
In this lecture, we examine the <ruby>Document Object Model<rt>DOM</rt></ruby> tree.

3
00:00:10.500 --> 00:00:14.000
<v Instructor>[Upbeat intro music fades]</v>
Notice how CSS aspect-ratio reservation prevents Cumulative Layout Shift.
```

#### WebVTT Cue Settings:
- `line:80%`: Specifies vertical positioning of the cue (preventing subtitles from obscuring code on slides).
- `align:middle|start|end`: Text alignment within the cue box.
- `<v Instructor>`: Voice tags specifying speaker identities.

---

## 6. Progressive Engineering Practice (3-Tier)

### Level 1: Responsive Picture Bandwidth Analysis
An engineering team is deploying a university portal homepage banner viewed by 50,000 daily active users, with 70% browsing on mobile devices (375px viewport, 2x Retina DPR) and 30% browsing on desktop displays (1440px viewport, 1x DPR).

Calculate the daily bandwidth consumption under **Architecture A** (single legacy uncompressed 1920x1080 JPEG at 850KB) versus **Architecture B** (responsive `<picture>` pipeline serving WebP at 45KB for mobile and 180KB for desktop):

**Calculation:**
- **Architecture A (Single Heavy Image)**:
  $$\text{Daily Bandwidth} = 50,000 \times 850\text{ KB} = 42,500,000\text{ KB} \approx \mathbf{40.53\text{ GB/day}}$$
- **Architecture B (Responsive `<picture>` Pipeline)**:
  - Mobile Users ($35,000$): $35,000 \times 45\text{ KB} = 1,575,000\text{ KB}$
  - Desktop Users ($15,000$): $15,000 \times 180\text{ KB} = 2,700,000\text{ KB}$
  - Total Daily Bandwidth: $1,575,000 + 2,700,000 = 4,275,000\text{ KB} \approx \mathbf{4.08\text{ GB/day}}$
- **Performance Impact**: Architecture B achieves an **89.9% bandwidth reduction** (saving 36.45 GB daily), dramatically reducing CDN egress costs and delivering sub-second Largest Contentful Paint (LCP) across mobile networks.

---

### Level 2: Scaffolded Bug Fix — Remediating Layout Shift & Security Flaws
> **Scenario:** Review the following multimedia hero component authored by an intern:
> ```html
> <div class="hero-container">
>   <a href="https://external-certifications.org" target="_blank">
>     <img src="/img/cert-banner.jpg" alt="Get certified today">
>   </a>
>   <video autoplay loop>
>     <source src="/media/promo.mp4" type="video/mp4">
>   </video>
> </div>
> ```
> 
> Identify the **three critical engineering and security flaws** in this snippet and refactor it into production-hardened HTML5.

<details>
<summary>Click to view solution & analysis</summary>

#### Flaws Identified:
1. **Critical Reverse Tabnabbing Vulnerability**: The `<a>` tag opens external destination `https://external-certifications.org` with `target="_blank"` without declaring `rel="noopener noreferrer"`. The external site can manipulate `window.opener.location`.
2. **Severe Cumulative Layout Shift (CLS)**: The `<img>` tag lacks explicit `width` and `height` attributes. Until the image loads from the network, its height is 0px, causing the subsequent video and text to jump down when it renders.
3. **Autoplay Failure Mode**: Modern browser engines (Chrome, Safari, Firefox) **strictly block unmuted autoplaying videos** to prevent jarring user experiences. Because the `<video>` lacks the `muted` attribute, the video will throw an unhandled `NotAllowedError` promise rejection in JavaScript and stall permanently on the first frame. Furthermore, it lacks accessible controls, poster fallback, and `playsinline`.

#### Production-Hardened Refactoring:
```html
<div class="hero-container">
  <!-- 1. Secure Hyperlink with Noopener -->
  <a href="https://external-certifications.org" 
     target="_blank" 
     rel="noopener noreferrer"
     aria-label="Visit external certification partner portal (opens in new tab)">
    
    <!-- 2. Zero-CLS Image with Dimensions and Lazy Loading -->
    <img src="/img/cert-banner.jpg" 
         alt="Official Software Engineering certification accreditation banner" 
         width="1200" 
         height="300" 
         loading="lazy" 
         decoding="async">
  </a>

  <!-- 3. Muted Autoplay Video with Poster, Playsinline and Controls -->
  <video autoplay 
         loop 
         muted 
         playsinline 
         poster="/media/promo-poster.jpg" 
         preload="metadata" 
         width="1200" 
         height="675"
         aria-label="Department promotional video showing software labs">
    <source src="/media/promo.webm" type='video/webm; codecs="vp9, opus"'>
    <source src="/media/promo.mp4" type='video/mp4; codecs="avc1.42E01E, mp4a.40.2"'>
    <track src="/media/promo_en.vtt" kind="captions" srclang="en" label="English" default>
  </video>
</div>
```

</details>

---

### Level 3: Advanced System Design — Designing an Enterprise Media Delivery Platform
> **Scenario:** Design the multimedia distribution architecture for the university's online video learning management system (Educamind). The platform must deliver 1080p recorded lecture videos to 15,000 concurrent students across Ethiopia, accommodating network connections fluctuating between 200 Kbps mobile data and 50 Mbps campus fiber.
> 
> Architect the client-side HTML5 media pipeline, contrast Progressive Download with Adaptive Bitrate Streaming (HLS/DASH), and design the WebVTT subtitle localization pipeline.

<details>
<summary>Click to view architectural solution</summary>

#### High-Scale Architectural Blueprint:

```
 [Raw MP4 Video Upload from Professor]
                    │
                    ▼ (AWS MediaConvert / FFmpeg Ingestion Pipeline)
       [HLS Video Segmentation Engine]
        ├── 1080p Stream (.m3u8 index + 6s .ts chunks @ 4500 Kbps)
        ├── 720p  Stream (.m3u8 index + 6s .ts chunks @ 2200 Kbps)
        ├── 480p  Stream (.m3u8 index + 6s .ts chunks @ 800  Kbps)
        ├── 360p  Stream (.m3u8 index + 6s .ts chunks @ 350  Kbps)
        └── Master Playlist: master.m3u8 (Manifest binding all bitrates)
                    │
                    ▼ (Edge Storage & Geo-Replication)
 [Amazon S3 Origin + CloudFront CDN Edge Caching]
                    │
                    ▼ (Encrypted HTTPS Delivery)
 [Client HTML5 Media Player: Hls.js / Video.js atop HTML5 <video>]
```

#### Key Architectural Implementations:
1. **Adaptive Bitrate Streaming (ABR) vs Progressive Download**:
   - *Progressive Download (`<video src="lecture.mp4">`)*: Downloads the monolithic file sequentially over HTTP. If a mobile user's bandwidth drops from 2 Mbps to 300 Kbps, playback stalls completely with a spinning buffer wheel.
   - *HTTP Live Streaming (HLS / RFC 8216)*: Video is sliced into 6-second chunk files. The client player continuously monitors packet arrival latency. When bandwidth drops, the player seamlessly requests the next 6-second chunk from the 360p stream; when connection speeds recover, it steps back up to 1080p with zero playback interruption.
2. **Client-Side HTML5 Video Binding**:
   ```html
   <video id="lecture-player" 
          controls 
          crossorigin="anonymous" 
          poster="/posters/lec4.jpg" 
          preload="none">
     <!-- For Safari native HLS support -->
     <source src="https://cdn.aastu.edu.et/hls/lec4/master.m3u8" 
             type="application/x-mpegURL">
     
     <!-- Multi-lingual WebVTT tracks -->
     <track kind="captions" src="https://cdn.aastu.edu.et/subtitles/lec4_en.vtt" srclang="en" label="English" default>
     <track kind="subtitles" src="https://cdn.aastu.edu.et/subtitles/lec4_am.vtt" srclang="am" label="Amharic">
     <track kind="subtitles" src="https://cdn.aastu.edu.et/subtitles/lec4_om.vtt" srclang="om" label="Afaan Oromoo">
   </video>
   ```
3. **CORS Requirement for Text Tracks**:
   - Because WebVTT track files are fetched across domain boundaries from a CDN (`cdn.aastu.edu.et`), the `<video>` element must declare `crossorigin="anonymous"`.
   - The CDN edge server must return the HTTP header:
     ```http
     Access-Control-Allow-Origin: https://portal.aastu.edu.et
     ```
   - If this header is omitted, the browser's Same-Origin Policy will block the subtitle cues from rendering.

</details>
