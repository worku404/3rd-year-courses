# Lesson 1 — JavaFX Architecture, The Scene Graph & Core UI Controls

> [!NOTE]
> **Learning Outcomes:**
> - Trace the evolutionary trajectory of Java desktop toolkits: AWT $\to$ Swing $\to$ JavaFX.
> - Deconstruct the **Theater Metaphor**: contrast the responsibilities of `Stage`, `Scene`, `Parent`, and `Node`.
> - Analyze the four phases of the JavaFX Application Lifecycle: `launch()`, `init()`, `start()`, and `stop()`.
> - Assemble real-world desktop interfaces using core UI Controls: `Button`, `TextField`, `TextArea`, `CheckBox`, `RadioButton`, and `ComboBox`.
> - Enforce the **Single-Threaded UI Invariant** using `Platform.runLater()` to prevent race conditions and GUI freezes.

{{media:stage-video}}

{{media:stage-visual}}

## Executive Summary & System Context

Desktop user interfaces must bridge two conflicting computing realities:
1. **Low-Level Operating System Windowing**: Native OS display servers (Win32/DirectX on Windows, Cocoa/Metal on macOS, X11/Wayland on Linux) manage hardware video frames, DPI scaling, and hardware event queues.
2. **High-Level Object-Oriented Domain Logic**: Application developers require platform-independent, declarative, and composable abstractions to construct forms, charts, and reactive dashboards.

To solve this challenge, Java evolved through three major graphical toolkits:
- **AWT (Abstract Window Toolkit - 1995)**: Used heavyweight native OS peers. Highly brittle, suffered from platform-specific UI bugs ("least common denominator" approach).
- **Swing (1998)**: Replaced native peers with lightweight, pure Java software-rendered components (`JComponent`). Highly customizable, but relied on CPU-bound 2D rasterization without modern hardware acceleration.
- **JavaFX (Modern)**: The current standard enterprise desktop toolkit. Engineered from the ground up with a hardware-accelerated rendering pipeline (**Prism** via DirectX and OpenGL), CSS styling, FXML declarative markup, modern property binding, and high-DPI scaling.

---

## 1. The Theater Metaphor & The Scene Graph Architecture

JavaFX models desktop windowing using a physical theater metaphor:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Stage (Operating System Window)                 │
│  [ _  []  X ] Window Title Bar, OS Minimize/Maximize/Close Buttons     │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │                  Scene (Physical Drawing Canvas)                   │ │
│ │ ┌────────────────────────────────────────────────────────────────┐ │ │
│ │ │             Root Node (Parent / Layout Container)              │ │ │
│ │ │                                                                │ │ │
│ │ │    ┌────────────────────────┐    ┌────────────────────────┐    │ │ │
│ │ │    │   Branch Node (HBox)   │    │  Branch Node (Grid)    │    │ │ │
│ │ │    │  ┌──────┐    ┌──────┐  │    │  ┌──────┐    ┌──────┐  │    │ │ │
│ │ │    │  │Button│    │Label │  │    │  │Field │    │ Check│  │    │ │ │
│ │ │    │  └──────┘    └──────┘  │    │  └──────┘    └──────┘  │    │ │ │
│ │ │    └────────────────────────┘    └────────────────────────┘    │ │ │
│ │ └────────────────────────────────────────────────────────────────┘ │ │
│ └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. `javafx.stage.Stage` (The Window Frame)
The `Stage` represents the top-level operating system window.
- The JVM runtime instantiates and passes the `primaryStage` to the `start(Stage)` method.
- Developers can configure window decorations, title, min/max dimensions, and modalities:
  ```java
  primaryStage.setTitle("AASTU Software Engineering Portal");
  primaryStage.setWidth(1024);
  primaryStage.setHeight(768);
  primaryStage.setResizable(true);
  primaryStage.initStyle(StageStyle.DECORATED); // Options: UNDECORATED, TRANSPARENT, UTILITY
  primaryStage.show(); // Makes window visible on desktop
  ```

### 2. `javafx.scene.Scene` (The Container)
The `Scene` is the container holding the physical visual content for a specific view:
- A `Stage` can host only **one active `Scene` at a time**, but an application can switch scenes dynamically (e.g., swapping a Login Scene for a Dashboard Scene).
- A `Scene` requires a single **Root Node** upon instantiation:
  ```java
  Parent root = new StackPane();
  Scene scene = new Scene(root, 800, 600, Color.WHITE);
  primaryStage.setScene(scene);
  ```

### 3. `javafx.scene.Node` & The Scene Graph
The visual structure of a JavaFX window is represented as an in-memory **Tree data structure** called the **Scene Graph**:
- **Root Node**: The foundational node directly attached to the `Scene` (typically an instance of `Parent` or a layout `Pane`).
- **Branch Nodes**: Internal container nodes (`HBox`, `VBox`, `BorderPane`, `GridPane`, `Group`) that manage the positioning and sizing of their children.
- **Leaf Nodes**: Terminal interactive controls or visual primitives that cannot contain children (`Button`, `Label`, `TextField`, `Rectangle`, `Circle`, `ImageView`).

> [!IMPORTANT]
> **Directed Acyclic Graph (DAG) Invariant**: A `Node` can appear in **exactly ONE place** in the Scene Graph at any given moment. Attempting to add the same `Button` or `Label` instance to multiple panes or multiple times to the same pane throws an `IllegalArgumentException`.

---

## 2. The JavaFX Application Lifecycle

Every JavaFX application must extend `javafx.application.Application` and implement the abstract `start(Stage)` method. The runtime executes a strict four-phase lifecycle:

```
[ OS Process Start ]
         │
         ▼
 1. main(String[] args) ─────────> Application.launch(args)
                                         │
         ┌───────────────────────────────┘
         ▼
 2. init() Method ───────────────> Runs on Launcher Thread (Non-UI)
                                   (Safe for DB connection, config loading)
         │
         ▼
 3. start(Stage primaryStage) ───> Runs on JavaFX Application Thread
                                   (Constructs Scene Graph, stage.show())
         │
         ▼
[ Active Event Loop ] ───────────> 60 FPS Pulse Engine & Event Dispatch
         │
         ▼
 4. stop() Method ───────────────> Runs on JavaFX Application Thread
                                   (Triggered by window close or Platform.exit())
```

### Complete Lifecycle Verification Code:
```java
package edu.se.lifecycle;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;

public class LifecycleDemo extends Application {

    public LifecycleDemo() {
        System.out.printf("[1] Constructor: Thread = %s%n", Thread.currentThread().getName());
    }

    @Override
    public void init() throws Exception {
        // EXCELLENT LOCATION: Initialize database connection pools or read disk configs
        System.out.printf("[2] init() Hook: Thread = %s%n", Thread.currentThread().getName());
    }

    @Override
    public void start(Stage primaryStage) {
        // MANDATORY: Build UI on the JavaFX Application Thread
        System.out.printf("[3] start() Hook: Thread = %s%n", Thread.currentThread().getName());

        Label label = new Label("AASTU Software Engineering - JavaFX Active");
        StackPane root = new StackPane(label);
        Scene scene = new Scene(root, 400, 200);

        primaryStage.setTitle("Lifecycle Test");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    @Override
    public void stop() throws Exception {
        // CLEANUP: Close network sockets and active threads
        System.out.printf("[4] stop() Hook: Thread = %s%n", Thread.currentThread().getName());
    }

    public static void main(String[] args) {
        System.out.printf("[0] main(): Thread = %s%n", Thread.currentThread().getName());
        Application.launch(args);
    }
}
```

#### Thread Execution Trace:
- `main()`: Thread = `main`
- `Constructor`: Thread = `JavaFX-Launcher`
- `init()`: Thread = `JavaFX-Launcher`
- `start()`: Thread = `JavaFX Application Thread`
- `stop()`: Thread = `JavaFX Application Thread`

---

## 3. Essential UI Controls & Interaction Primitives

All user-interface controls inherit from `javafx.scene.control.Control`, which provides styling via CSS (`-fx-background-color`, `-fx-font-size`), skinning, and sizing properties (`prefWidth`, `minHeight`, `maxHeight`).

### 1. Text Presentation & Input Controls
- `Label`: Displays non-editable text or icons.
  ```java
  Label lblTitle = new Label("Enter Student ID:");
  ```
- `TextField`: Single-line editable text input.
  ```java
  TextField txtStudentId = new TextField();
  txtStudentId.setPromptText("e.g. ETS/0123/14");
  ```
- `TextArea`: Multi-line text input with automatic scrollbars.
  ```java
  TextArea txtComments = new TextArea();
  txtComments.setPrefRowCount(4);
  txtComments.setWrapText(true);
  ```

### 2. Action Controls
- `Button`: Standard clickable button that fires an `ActionEvent`.
  ```java
  Button btnSubmit = new Button("Register Student");
  btnSubmit.setDefaultButton(true); // Triggers automatically when user hits Enter
  ```

### 3. Selection Controls
- `CheckBox`: Represents an independent binary state (`isSelected() == true/false`).
  ```java
  CheckBox chkAgreed = new CheckBox("I accept the academic honor code");
  ```
- `RadioButton`: Represents mutually exclusive choices grouped via a `ToggleGroup`.
  ```java
  ToggleGroup roleGroup = new ToggleGroup();
  RadioButton rbStudent = new RadioButton("Undergraduate Student");
  RadioButton rbPostgrad = new RadioButton("Postgraduate Student");
  rbStudent.setToggleGroup(roleGroup);
  rbPostgrad.setToggleGroup(roleGroup);
  rbStudent.setSelected(true); // Default selection
  ```
- `ComboBox<T>`: Drop-down selection menu populated with items.
  ```java
  ComboBox<String> cmbDept = new ComboBox<>();
  cmbDept.getItems().addAll("Software Engineering", "Computer Science", "Electrical Eng", "Civil Eng");
  cmbDept.getSelectionModel().selectFirst();
  ```

---

## 4. The Single-Threaded UI Rule & Concurrency

The most frequent source of fatal bugs and crashing applications in desktop software is **violating the UI Thread invariant**.

### The Rule:
**The JavaFX Scene Graph is NOT thread-safe.** All modifications to the visual state—changing text, adding nodes, disabling buttons, resizing components—MUST occur on the **JavaFX Application Thread**.

```
[ Background Worker Thread ]                      [ JavaFX Application Thread ]
           │                                                    │
   Performs Heavy I/O                                   Renders Scene Graph
   (HTTP / Database Query)                                     │
           │                                                    │
           ├─── Attempting direct UI update:                    │
           │    lblStatus.setText("Done!");                     │
           │    ❌ THROWS: IllegalStateException!               │
           │                                                    │
           └─── CORRECT: Queue task via Platform.runLater()     │
                Platform.runLater(() -> {                       │
                    lblStatus.setText("Done!"); ───────────────>│ Executes safely!
                });                                             │ No race condition!
```

### If you update UI from a Background Thread:
```java
new Thread(() -> {
    // RUNS ON WORKER THREAD:
    label.setText("Query Complete"); 
    // CRASH: java.lang.IllegalStateException: Not on FX application thread;
}).start();
```

### If you run heavy work on the JavaFX Application Thread:
```java
button.setOnAction(e -> {
    // RUNS ON JAVAFX APPLICATION THREAD:
    Thread.sleep(10000); // FREEZES GUI! OS marks window as "Not Responding"!
});
```

### The Solution: `Platform.runLater(Runnable)`
```java
new Thread(() -> {
    // 1. Perform long-running background computation or network request
    String result = queryDatabaseRemote();

    // 2. Marshal visual update back to JavaFX Application Thread
    Platform.runLater(() -> {
        label.setText("Query Finished: " + result);
        progressBar.setProgress(1.0);
    });
}).start();
```

---

## 5. Comprehensive Trade-Off Matrix

| Feature / Metric | AWT (1995) | Swing (1998) | JavaFX (Modern) |
| :--- | :--- | :--- | :--- |
| **Component Architecture** | Heavyweight (OS Peers) | Lightweight (Pure Java) | Lightweight (Prism Node Graph) |
| **Rendering Acceleration** | OS CPU GDI/X11 | Pure Software 2D CPU Rasterizer | Hardware 3D/2D (DirectX/OpenGL) |
| **Styling Mechanism** | Inflexible OS Defaults | LookAndFeel (`UIManager`) | Full W3C CSS3 Support |
| **Declarative UI** | None | None | FXML (XML-based scene description) |
| **Reactive Binding** | Manual PropertyChangeListeners | Manual PropertyChangeListeners | High-level `Property` & `Observable` |
| **Modern Multimedia** | Primitive Audio | Poor Video Support | Native H.264 Video, Audio & 3D Meshes |

---

## 6. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Tracing Node Parentage
**Objective**: Analyze the following JavaFX snippet and identify the structural bug preventing compilation or runtime execution.

```java
public class DuplicateNodeBug extends Application {
    @Override
    public void start(Stage stage) {
        Button submitBtn = new Button("Submit");
        
        HBox topBar = new HBox(submitBtn);
        VBox sideBar = new VBox(submitBtn); // Notice submitBtn used again!

        BorderPane root = new BorderPane();
        root.setTop(topBar);
        root.setLeft(sideBar);

        stage.setScene(new Scene(root, 400, 300));
        stage.show();
    }
}
```

<details>
<summary>View Level 1 Architecture Walkthrough Analysis</summary>

#### Runtime Execution Failure:
The application throws:
`java.lang.IllegalArgumentException: Children: duplicate children added: parent = VBox@...`

#### Architectural Explanation:
1. JavaFX enforces that the Scene Graph is a **strict Tree (Directed Acyclic Graph)**.
2. Every `Node` holds an internal private reference: `private ReadOnlyObjectWrapper<Parent> parent`.
3. When `topBar.getChildren().add(submitBtn)` executes, `submitBtn.parent` is set to `topBar`.
4. When `sideBar.getChildren().add(submitBtn)` executes, JavaFX verifies whether `submitBtn` already has an active parent. Because it belongs to `topBar`, it throws an `IllegalArgumentException`.
5. **Solution**: UI controls cannot be shared across multiple containers. If the application requires a button in both the top bar and sidebar, two distinct `Button` instances must be instantiated: `Button topSubmit = new Button("Submit");` and `Button sideSubmit = new Button("Submit");`.
</details>

---

### Level 2: Scaffolded System Refactoring — Multi-Control Student Registration Form
**Objective**: Construct a complete, production-ready student registration form implementing `Button`, `TextField`, `CheckBox`, `RadioButton` (with `ToggleGroup`), and `ComboBox`.

<details>
<summary>View Level 2 Complete JavaFX Implementation</summary>

```java
package edu.se.ui;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;

public class StudentRegistrationApp extends Application {

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("AASTU SE - Student Registration Gateway");

        // 1. Text Inputs
        Label lblHeader = new Label("Student Registration Form");
        lblHeader.setStyle("-fx-font-size: 18px; -fx-font-weight: bold; -fx-text-fill: #0284c7;");

        TextField txtName = new TextField();
        txtName.setPromptText("Full Legal Name");

        TextField txtId = new TextField();
        txtId.setPromptText("Student ID (e.g., ETS/1200/14)");

        // 2. Dropdown (ComboBox)
        ComboBox<String> cmbDept = new ComboBox<>();
        cmbDept.getItems().addAll("Software Engineering", "Computer Science", "Information Systems");
        cmbDept.setPromptText("Select Department");
        cmbDept.setMaxWidth(Double.MAX_VALUE);

        // 3. Mutually Exclusive Radio Buttons (ToggleGroup)
        ToggleGroup programGroup = new ToggleGroup();
        RadioButton rbRegular = new RadioButton("Regular Program");
        RadioButton rbExtension = new RadioButton("Extension Program");
        rbRegular.setToggleGroup(programGroup);
        rbExtension.setToggleGroup(programGroup);
        rbRegular.setSelected(true);

        HBox radioBox = new HBox(15, rbRegular, rbExtension);

        // 4. CheckBox
        CheckBox chkTerms = new CheckBox("I confirm all academic records provided are accurate");

        // 5. Submit Button & Status Feedback
        Label lblStatus = new Label();
        lblStatus.setStyle("-fx-font-weight: bold;");

        Button btnSubmit = new Button("Complete Enrollment");
        btnSubmit.setMaxWidth(Double.MAX_VALUE);
        btnSubmit.setStyle("-fx-background-color: #0284c7; -fx-text-fill: white; -fx-font-weight: bold;");

        // Form Validation Action
        btnSubmit.setOnAction(e -> {
            if (txtName.getText().isBlank() || txtId.getText().isBlank()) {
                lblStatus.setText("Validation Error: Name and ID cannot be blank!");
                lblStatus.setStyle("-fx-text-fill: #ef4444;");
                return;
            }
            if (cmbDept.getValue() == null) {
                lblStatus.setText("Validation Error: Please select an academic department.");
                lblStatus.setStyle("-fx-text-fill: #ef4444;");
                return;
            }
            if (!chkTerms.isSelected()) {
                lblStatus.setText("Validation Error: You must accept the terms confirmation.");
                lblStatus.setStyle("-fx-text-fill: #ef4444;");
                return;
            }

            RadioButton selectedProgram = (RadioButton) programGroup.getSelectedToggle();
            lblStatus.setText(String.format("Enrolled: %s (%s) - %s [%s]", 
                txtName.getText(), txtId.getText(), cmbDept.getValue(), selectedProgram.getText()));
            lblStatus.setStyle("-fx-text-fill: #10b981;");
        });

        // Assembly in Layout Container
        VBox layout = new VBox(12);
        layout.setPadding(new Insets(20));
        layout.setAlignment(Pos.TOP_LEFT);
        layout.getChildren().addAll(
            lblHeader, 
            new Label("Full Name:"), txtName,
            new Label("Student ID:"), txtId,
            new Label("Department:"), cmbDept,
            new Label("Program Type:"), radioBox,
            chkTerms,
            btnSubmit,
            lblStatus
        );

        Scene scene = new Scene(layout, 420, 480);
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — Non-Blocking Background Data Processing Gateway
**Objective**: Build a high-throughput network data fetcher with a progress bar and status indicator. Violating the Single-Threaded UI rule must be prevented: long-running simulation tasks must run on a background thread pool, and visual progress updates must be safely dispatched via `Platform.runLater()`.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.concurrency;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class AsyncWorkerApp extends Application {
    
    // Dedicated bounded thread pool for background I/O operations
    private final ExecutorService executor = Executors.newFixedThreadPool(2);

    @Override
    public void start(Stage stage) {
        stage.setTitle("Non-Blocking Background I/O Monitor");

        Label lblTitle = new Label("Distributed Data Synchronization");
        lblTitle.setStyle("-fx-font-size: 16px; -fx-font-weight: bold;");

        ProgressBar progressBar = new ProgressBar(0.0);
        progressBar.setPrefWidth(350);

        Label lblStatus = new Label("Status: Idle");
        Button btnStart = new Button("Start Remote Sync (5000 Records)");

        btnStart.setOnAction(e -> {
            btnStart.setDisable(true);
            lblStatus.setText("Status: Connecting to remote cluster...");
            progressBar.setProgress(0.0);

            // Dispatch task to background thread pool
            executor.submit(() -> {
                final int totalRecords = 5000;
                for (int i = 1; i <= totalRecords; i++) {
                    // Simulate physical network packet transfer delay
                    try {
                        Thread.sleep(1); 
                    } catch (InterruptedException ignored) {}

                    final double progress = (double) i / totalRecords;
                    final int currentCount = i;

                    // Marshal update every 50 records to avoid flooding the FX Application Thread
                    if (i % 50 == 0 || i == totalRecords) {
                        Platform.runLater(() -> {
                            progressBar.setProgress(progress);
                            lblStatus.setText(String.format("Synchronized %d / %d records (%.0f%%)", 
                                currentCount, totalRecords, progress * 100));
                        });
                    }
                }

                // Final task completion notification
                Platform.runLater(() -> {
                    lblStatus.setText("Status: Synchronization Complete! All ledgers committed.");
                    btnStart.setDisable(false);
                });
            });
        });

        VBox root = new VBox(15, lblTitle, btnStart, progressBar, lblStatus);
        root.setPadding(new Insets(25));
        root.setAlignment(Pos.CENTER);

        stage.setScene(new Scene(root, 420, 240));
        stage.show();
    }

    @Override
    public void stop() {
        // Guaranteed clean teardown of background threads when window is closed
        executor.shutdownNow();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
```

#### Key Architectural Details:
1. **Thread Pool Isolation**: Background work is offloaded to a managed `ExecutorService`, keeping the JavaFX Application Thread free to process OS mouse clicks, keyboard events, and window repaints at 60 FPS.
2. **Event Rate Limiting**: The worker thread batches visual updates (`i % 50 == 0`), preventing event-queue congestion on the UI thread.
3. **Application Teardown Hook (`stop()`)**: Ensures background daemon threads terminate immediately when the user closes the window, preventing zombie JVM processes.
</details>
