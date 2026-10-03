# Lesson 2 — Modern Layout Architectures: Panes, Constraints & Responsive GUI Design

> [!NOTE]
> **Learning Outcomes:**
> - Contrast obsolete hardcoded pixel positioning (`setLayoutX/Y`) with modern **coordinate-free responsive layout panes**.
> - Engineer linear flows using `HBox` and `VBox` with elastic spacers (`Priority.ALWAYS`) and geometric padding (`Insets`).
> - Master two-dimensional matrix positioning with `GridPane`: column/row indexing, cell spanning, and column constraints.
> - Structure enterprise desktop application frames using `BorderPane`'s five distinct layout regions.
> - Formulate composite, deeply nested pane hierarchies that scale smoothly across 4K displays, mobile tablets, and compact laptop screens.

{{media:layout-video}}

{{media:layout-visual}}

## Executive Summary & System Context

In early graphical programming (such as Visual Basic or legacy AWT `null` layouts), developers placed visual components on a canvas by specifying fixed pixel coordinates:
```java
// LETHAL ANTI-PATTERN: Fixed Pixel Positioning
button.setLayoutX(150);
button.setLayoutY(80);
button.setSize(100, 30);
```

While seemingly intuitive, **absolute positioning is completely unacceptable in production software engineering** for three fundamental reasons:
1. **DPI & Screen Scaling Diversity**: Modern displays range from standard 96 DPI monitors to 4K/Retina displays with 200–300% OS font scaling. Hardcoded pixel coordinates cause text to truncate, buttons to overlap, and entire forms to render off-screen.
2. **Dynamic Window Resizing**: Users routinely resize desktop windows, snap applications side-by-side, or maximize windows. Absolute coordinates leave vast areas of dead white space or clip interactive controls.
3. **Internationalization (i18n)**: Translating a UI from English to German or Amharic changes text length by up to 40%. A hardcoded button width of 100 pixels will clip translated labels.

To achieve device independence, JavaFX replaces absolute coordinates with **Layout Panes**. Panes compute the physical geometry, positions, and bounds of their children dynamically at runtime based on high-level constraints.

---

## 1. Principles of Responsive Layout Management

Every `Node` in JavaFX participates in a two-pass layout negotiation managed by its parent container:

```
[ Layout Pass 1: Sizing Measurement ]
Parent queries Child Nodes for size bounds:
├── getMinWidth() / getMinHeight()   (Smallest size node can occupy without clipping)
├── getPrefWidth() / getPrefHeight() (Optimal visual size designed for component)
└── getMaxWidth() / getMaxHeight()   (Largest allowable expansion)

[ Layout Pass 2: Positioning & Bounds Assignment ]
Parent calculates coordinates based on constraints:
└── Parent assigns final bounds to children: layoutChildren()
```

### Insets and Margins
- **Padding (`setPadding(new Insets(top, right, bottom, left))`):** Defines internal breathing room between the pane's outer border and its children.
- **Spacing (`setSpacing(double pixels)`):** Defines gap distance between adjacent sibling nodes inside linear containers.
- **Node Margin (`HBox.setMargin(node, insets)`):** Specific offset applied to an individual child node.

---

## 2. Linear Containers: `HBox` and `VBox`

Linear panes arrange children sequentially in a single dimension:
- `HBox`: Lays out children in a single horizontal row from left to right.
- `VBox`: Lays out children in a single vertical column from top to bottom.

```
       HBox (Horizontal Row)                     VBox (Vertical Column)
┌─────────────────────────────────┐         ┌───────────────────────────────┐
│ ┌─────┐   ┌─────┐   ┌─────────┐ │         │ ┌───────────────────────────┐ │
│ │Node1│   │Node2│   │  Node3  │ │         │ │           Node 1          │ │
│ └─────┘   └─────┘   └─────────┘ │         │ └───────────────────────────┘ │
└─────────────────────────────────┘         │ ┌───────────────────────────┐ │
                                            │ │           Node 2          │ │
                                            │ └───────────────────────────┘ │
                                            └───────────────────────────────┘
```

### Elastic Spacers (`Priority.ALWAYS`)
To push components to opposite edges of a toolbar (e.g., placing a Logo on the left and a Logout button on the right), engineers insert an invisible `Region` configured to absorb all remaining horizontal space:

```java
HBox toolbar = new HBox(10);
toolbar.setPadding(new Insets(10));
toolbar.setAlignment(Pos.CENTER_LEFT);

Label lblLogo = new Label("AASTU SE Portal");
lblLogo.setStyle("-fx-font-weight: bold; -fx-font-size: 16px;");

// Elastic Spacer Region:
Region spacer = new Region();
HBox.setHgrow(spacer, Priority.ALWAYS); // Instructs spacer to absorb all slack width!

Button btnProfile = new Button("My Profile");
Button btnLogout = new Button("Sign Out");

toolbar.getChildren().addAll(lblLogo, spacer, btnProfile, btnLogout);
```

---

## 3. Matrix Layouts: The `GridPane`

The `GridPane` arranges nodes in a flexible two-dimensional grid of rows and columns. Unlike rigid HTML tables, `GridPane` cells do not require explicit table elements—nodes are positioned directly using `(column, row)` coordinates.

```
                  Col 0                   Col 1
        ┌───────────────────────┬────────────────────────┐
  Row 0 │ Label: "First Name"   │ TextField: [ Abera   ] │
        ├───────────────────────┼────────────────────────┤
  Row 1 │ Label: "Department"   │ ComboBox:  [ SE    v ] │
        ├───────────────────────┴────────────────────────┤
  Row 2 │ Button: [ Submit Form ]  (ColumnSpan = 2)      │
        └────────────────────────────────────────────────┘
```

### The `pane.add(node, col, row)` Syntax
> [!IMPORTANT]
> **Coordinate Order Convention**: Unlike matrix mathematical notation $(row, col)$, JavaFX methods strictly use **`(columnIndex, rowIndex)`** order!
> - `grid.add(lblFirstName, 0, 0);` $\longrightarrow$ Column 0, Row 0.
> - `grid.add(txtFirstName, 1, 0);` $\longrightarrow$ Column 1, Row 0.

### Column & Row Spanning
A single node can span multiple columns or rows using `GridPane.setColumnSpan()` and `GridPane.setRowSpan()`:
```java
Button btnSubmit = new Button("Submit Application");
btnSubmit.setMaxWidth(Double.MAX_VALUE); // Expand to fill full cell width!
grid.add(btnSubmit, 0, 2);
GridPane.setColumnSpan(btnSubmit, 2); // Spans across both Column 0 and Column 1
```

### Dynamic Column Constraints
To build responsive forms where input fields automatically expand with window resizing:
```java
ColumnConstraints col0 = new ColumnConstraints();
col0.setMinWidth(120);
col0.setHalignment(HPos.RIGHT); // Labels right-aligned

ColumnConstraints col1 = new ColumnConstraints();
col1.setHgrow(Priority.ALWAYS); // Fields expand horizontally!

grid.getColumnConstraints().addAll(col0, col1);
```

---

## 4. Positional & Stacking Panes: `BorderPane`, `FlowPane` & `StackPane`

### 1. `BorderPane` (The Application Frame)
`BorderPane` divides the window into five distinct geometric regions: `Top`, `Bottom`, `Left`, `Right`, and `Center`.

```
┌────────────────────────────────────────────────────────┐
│                        TOP                             │
│               (ToolBar / MenuBar)                      │
├──────────────┬──────────────────────────┬──────────────┤
│              │                          │              │
│    LEFT      │          CENTER          │    RIGHT     │
│  (Navigation │     (Active Workspace /  │ (Inspector / │
│   Sidebar)   │       Data Table)        │   Details)   │
│              │   *EXPANDS IN BOTH DIMS* │              │
├──────────────┴──────────────────────────┴──────────────┤
│                       BOTTOM                           │
│                 (System Status Bar)                    │
└────────────────────────────────────────────────────────┘
```

- **The Center Region Invariant**: The `Center` region is unique: it automatically expands in both horizontal and vertical dimensions to consume all remaining space within the stage!
- **Optional Regions**: If an application does not set `Left` or `Right`, the `Center` seamlessly expands to fill the entire width.

### 2. `FlowPane` (The Dynamic Wrapping Container)
`FlowPane` arranges its children in sequence (horizontally or vertically). When the boundary of the window is reached, nodes automatically wrap to the next line or column, making it ideal for photo galleries, tag clouds, or responsive badge lists.

```java
FlowPane tagCloud = new FlowPane(Orientation.HORIZONTAL, 10, 10);
tagCloud.setPadding(new Insets(15));
for (String skill : List.of("Java", "OOP", "JavaFX", "PostgreSQL", "Docker", "Git")) {
    tagCloud.getChildren().add(new Button(skill));
}
```

### 3. `StackPane` (The Z-Order Layering Container)
`StackPane` places its children directly on top of each other along the Z-axis.
- By default, nodes are centered within the pane.
- Ideal for placing text over background images, custom shaped buttons, or displaying loading spinners/scrims over an active view.

---

## 5. Composite Layout Engineering: Scalable Enterprise Wireframe

In enterprise software engineering, complex windows are never built with a single layout pane. Instead, engineers use **Composite Layout Engineering**—nesting specialized panes together into a cohesive hierarchy:

```
[ Root Container: BorderPane ]
├── TOP:    HBox (Application Header & Global Search Bar)
├── LEFT:   VBox (Navigation Sidebar Menu)
├── CENTER: GridPane (Interactive Registration Form & Inputs)
└── BOTTOM: HBox (Connection Status & System Telemetry)
```

```java
package edu.se.composite;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;

public class CompositeDashboardApp extends Application {

    @Override
    public void start(Stage stage) {
        stage.setTitle("AASTU Software Engineering - Enterprise Dashboard");

        BorderPane root = new BorderPane();

        // 1. TOP REGION: HBox Header
        HBox topBar = new HBox(15);
        topBar.setPadding(new Insets(12, 20, 12, 20));
        topBar.setStyle("-fx-background-color: #0f172a;");
        topBar.setAlignment(Pos.CENTER_LEFT);

        Label lblBrand = new Label("AASTU SE ERP");
        lblBrand.setStyle("-fx-text-fill: #38bdf8; -fx-font-weight: bold; -fx-font-size: 16px;");

        Region topSpacer = new Region();
        HBox.setHgrow(topSpacer, Priority.ALWAYS);

        TextField txtSearch = new TextField();
        txtSearch.setPromptText("Search students or records...");
        txtSearch.setPrefWidth(250);

        Button btnProfile = new Button("Admin: gold");
        btnProfile.setStyle("-fx-background-color: #1e293b; -fx-text-fill: white;");

        topBar.getChildren().addAll(lblBrand, topSpacer, txtSearch, btnProfile);
        root.setTop(topBar);

        // 2. LEFT REGION: VBox Navigation Sidebar
        VBox leftNav = new VBox(10);
        leftNav.setPadding(new Insets(20, 15, 20, 15));
        leftNav.setStyle("-fx-background-color: #1e293b; -fx-min-width: 180px;");

        Label lblNav = new Label("SYSTEM MODULES");
        lblNav.setStyle("-fx-text-fill: #94a3b8; -fx-font-size: 11px; -fx-font-weight: bold;");

        Button btnDash = createNavButton("Overview Dashboard");
        Button btnStudents = createNavButton("Student Registry");
        Button btnCourses = createNavButton("Curriculum & Units");
        Button btnSettings = createNavButton("System Preferences");

        leftNav.getChildren().addAll(lblNav, btnDash, btnStudents, btnCourses, btnSettings);
        root.setLeft(leftNav);

        // 3. CENTER REGION: GridPane Main Workspace
        GridPane centerForm = new GridPane();
        centerForm.setPadding(new Insets(30));
        centerForm.setHgap(15);
        centerForm.setVgap(15);

        ColumnConstraints col0 = new ColumnConstraints();
        col0.setPrefWidth(140);
        ColumnConstraints col1 = new ColumnConstraints();
        col1.setHgrow(Priority.ALWAYS);
        centerForm.getColumnConstraints().addAll(col0, col1);

        Label lblFormTitle = new Label("Add Course Unit Record");
        lblFormTitle.setStyle("-fx-font-size: 18px; -fx-font-weight: bold; -fx-text-fill: #0284c7;");
        centerForm.add(lblFormTitle, 0, 0, 2, 1);

        centerForm.add(new Label("Course Code:"), 0, 1);
        TextField txtCode = new TextField("SWEG3101");
        centerForm.add(txtCode, 1, 1);

        centerForm.add(new Label("Unit Title:"), 0, 2);
        TextField txtTitle = new TextField();
        txtTitle.setPromptText("e.g. Unit 7: Graphical User Interfaces");
        centerForm.add(txtTitle, 1, 2);

        centerForm.add(new Label("Description:"), 0, 3);
        TextArea txtDesc = new TextArea();
        txtDesc.setPrefRowCount(4);
        centerForm.add(txtDesc, 1, 3);

        Button btnSave = new Button("Commit Unit to Database");
        btnSave.setStyle("-fx-background-color: #0284c7; -fx-text-fill: white; -fx-font-weight: bold;");
        btnSave.setMaxWidth(Double.MAX_VALUE);
        centerForm.add(btnSave, 1, 4);

        root.setCenter(centerForm);

        // 4. BOTTOM REGION: HBox Status Bar
        HBox bottomBar = new HBox(20);
        bottomBar.setPadding(new Insets(6, 15, 6, 15));
        bottomBar.setStyle("-fx-background-color: #0f172a;");
        bottomBar.setAlignment(Pos.CENTER_LEFT);

        Label lblStatus = new Label("System Status: Online | PostgreSQL 16 Active | Session: Secure");
        lblStatus.setStyle("-fx-text-fill: #94a3b8; -fx-font-size: 11px;");
        bottomBar.getChildren().add(lblStatus);
        root.setBottom(bottomBar);

        stage.setScene(new Scene(root, 900, 550));
        stage.show();
    }

    private Button createNavButton(String text) {
        Button b = new Button(text);
        b.setMaxWidth(Double.MAX_VALUE);
        b.setAlignment(Pos.CENTER_LEFT);
        b.setStyle("-fx-background-color: transparent; -fx-text-fill: #e2e8f0; -fx-padding: 8 12;");
        return b;
    }

    public static void main(String[] args) {
        launch(args);
    }
}
```

---

## 6. Comprehensive Trade-Off Matrix

| Layout Pane | Dimensionality | Primary Positioning Mechanism | Resizing / Growth Behavior | Best Use-Case Scenario |
| :--- | :--- | :--- | :--- | :--- |
| **`BorderPane`** | 2D (5 Regions) | Positional (`Top`, `Left`, `Center`, etc.) | `Center` expands in both axes | Primary top-level application skeleton |
| **`GridPane`** | 2D (Matrix) | Coordinate Indices `(col, row)` | Highly configurable via `ColumnConstraints` | Forms, data input grids, calculators |
| **`HBox`** | 1D (Horizontal) | Sequential Linear Order | Controlled via `HBox.setHgrow()` | Toolbars, button groups, headers |
| **`VBox`** | 1D (Vertical) | Sequential Linear Order | Controlled via `VBox.setVgrow()` | Navigation sidebars, vertical form fields |
| **`FlowPane`** | 1D / 2D (Reflow) | Flow sequence with line wrap | Wraps nodes when border is reached | Tag clouds, image galleries, badges |
| **`StackPane`** | 3D (Z-Order) | Layered depth order (Z-axis) | Resizes all layers to fill container | Overlays, modal dialogs, loading scrims |

---

## 7. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Tracing Grid Coordinates & Spanning
**Objective**: Analyze the following `GridPane` construction. Map each component to its exact cell location and identify if any overlaps occur.

```java
GridPane grid = new GridPane();
Label l1 = new Label("L1");
Label l2 = new Label("L2");
Button b1 = new Button("B1");
Button b2 = new Button("B2");

grid.add(l1, 0, 0);
grid.add(l2, 1, 0);
grid.add(b1, 0, 1, 2, 1); // Notice 4-argument overload!
grid.add(b2, 1, 1);       // What happens here?
```

<details>
<summary>View Level 1 Layout Analysis</summary>

#### Coordinate Mapping & Overlap Analysis:
1. `l1` is placed at **Column 0, Row 0** (occupies 1 cell).
2. `l2` is placed at **Column 1, Row 0** (occupies 1 cell).
3. `grid.add(b1, 0, 1, 2, 1)` uses the 4-argument overload: `add(Node child, int columnIndex, int rowIndex, int colSpan, int rowSpan)`.
   - `b1` starts at **Column 0, Row 1** and spans **2 columns** (occupying Column 0 and Column 1 in Row 1).
4. `b2` is placed at **Column 1, Row 1**.
5. **COLLISION DETECTED**: `b1` spans across Column 1 of Row 1, and `b2` is explicitly added to Column 1 of Row 1!
   - In JavaFX, `GridPane` does NOT prevent cell collisions. Both `b1` and `b2` will be rendered in the same geometric area, drawing `b2` on top of `b1` and corrupting the UI!
   - **Fix**: Move `b2` to `(0, 2)` or remove the column span on `b1`.
</details>

---

### Level 2: Scaffolded System Refactoring — Eliminating Fragile Hardcoded Coordinates
**Objective**: Refactor a brittle, hardcoded legacy calculator interface using absolute coordinates into an elegant, responsive `GridPane` architecture.

#### Legacy Fragile Code:
```java
public class BrittleCalculator {
    public void buildUI(Pane pane) {
        // Hardcoded pixels: Breaks completely on different resolutions!
        Button b7 = new Button("7"); b7.setLayoutX(10); b7.setLayoutY(50); b7.setPrefSize(40, 40);
        Button b8 = new Button("8"); b8.setLayoutX(60); b8.setLayoutY(50); b8.setPrefSize(40, 40);
        Button b9 = new Button("9"); b9.setLayoutX(110); b9.setLayoutY(50); b9.setPrefSize(40, 40);
        Button bDiv = new Button("/"); bDiv.setLayoutX(160); bDiv.setLayoutY(50); bDiv.setPrefSize(40, 40);
        pane.getChildren().addAll(b7, b8, b9, bDiv);
    }
}
```

<details>
<summary>View Level 2 Refactored Responsive Solution</summary>

```java
package edu.se.calc;

import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.Button;
import javafx.scene.control.TextField;
import javafx.scene.layout.*;

public class ModernCalculatorPane extends VBox {

    public ModernCalculatorPane() {
        setSpacing(10);
        setPadding(new Insets(15));
        setAlignment(Pos.CENTER);
        setStyle("-fx-background-color: #0f172a; -fx-border-radius: 8px;");

        // 1. Digital Display Field
        TextField display = new TextField("0");
        display.setEditable(false);
        display.setAlignment(Pos.CENTER_RIGHT);
        display.setStyle("-fx-font-size: 20px; -fx-background-color: #1e293b; -fx-text-fill: #38bdf8;");

        // 2. Responsive Keypad Grid
        GridPane keypad = new GridPane();
        keypad.setHgap(8);
        keypad.setVgap(8);

        // Make all 4 columns expand equally
        for (int i = 0; i < 4; i++) {
            ColumnConstraints cc = new ColumnConstraints();
            cc.setPercentWidth(25);
            cc.setHgrow(Priority.ALWAYS);
            keypad.getColumnConstraints().add(cc);
        }

        String[][] buttons = {
            {"7", "8", "9", "/"},
            {"4", "5", "6", "*"},
            {"1", "2", "3", "-"},
            {"0", "C", "=", "+"}
        };

        for (int row = 0; row < buttons.length; row++) {
            for (int col = 0; col < buttons[row].length; col++) {
                Button btn = new Button(buttons[row][col]);
                btn.setMaxSize(Double.MAX_VALUE, Double.MAX_VALUE);
                btn.setStyle("-fx-font-size: 16px; -fx-font-weight: bold; -fx-background-color: #334155; -fx-text-fill: white;");
                GridPane.setVgrow(btn, Priority.ALWAYS);
                keypad.add(btn, col, row);
            }
        }

        getChildren().addAll(display, keypad);
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — Dynamic Responsive Viewport with Collapsible Sidebar
**Objective**: Build an enterprise desktop dashboard featuring an animated collapsible sidebar (toggling between expanded icon+label mode and collapsed icon-only mode) while maintaining fluid responsive auto-expansion of the central data workspace.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.advanced;

import javafx.animation.Animation;
import javafx.animation.Transition;
import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import javafx.util.Duration;

public class CollapsibleDashboardApp extends Application {

    private boolean isSidebarExpanded = true;
    private final double EXPANDED_WIDTH = 220;
    private final double COLLAPSED_WIDTH = 60;

    @Override
    public void start(Stage stage) {
        stage.setTitle("Responsive Enterprise Workspace");

        BorderPane root = new BorderPane();

        // 1. Sidebar Container
        VBox sidebar = new VBox(12);
        sidebar.setPadding(new Insets(15, 10, 15, 10));
        sidebar.setStyle("-fx-background-color: #1e293b;");
        sidebar.setPrefWidth(EXPANDED_WIDTH);

        // Sidebar Toggle Button
        Button btnToggle = new Button("<<");
        btnToggle.setStyle("-fx-background-color: #334155; -fx-text-fill: white; -fx-font-weight: bold;");

        VBox navItems = new VBox(8);
        navItems.getChildren().addAll(
            createItem("[D]", "Dashboard"),
            createItem("[S]", "Students"),
            createItem("[G]", "Grades"),
            createItem("[C]", "Courses"),
            createItem("[?]", "System Help")
        );

        // Sidebar Collapsing Logic
        btnToggle.setOnAction(e -> {
            isSidebarExpanded = !isSidebarExpanded;
            btnToggle.setText(isSidebarExpanded ? "<<" : ">>");

            double startW = sidebar.getWidth();
            double targetW = isSidebarExpanded ? EXPANDED_WIDTH : COLLAPSED_WIDTH;

            // Smooth Width Transition
            Transition transition = new Transition() {
                { setCycleDuration(Duration.millis(200)); }
                @Override
                protected void interpolate(double frac) {
                    double current = startW + (targetW - startW) * frac;
                    sidebar.setPrefWidth(current);
                }
            };
            transition.play();

            // Toggle Label Visibility
            for (javafx.scene.Node n : navItems.getChildren()) {
                if (n instanceof HBox itemBox) {
                    Label lbl = (Label) itemBox.getChildren().get(1);
                    lbl.setVisible(isSidebarExpanded);
                    lbl.setManaged(isSidebarExpanded);
                }
            }
        });

        sidebar.getChildren().addAll(btnToggle, new Separator(), navItems);
        root.setLeft(sidebar);

        // 2. Central Active Workspace (Fluid Grid)
        GridPane centerGrid = new GridPane();
        centerGrid.setPadding(new Insets(25));
        centerGrid.setHgap(15);
        centerGrid.setVgap(15);

        ColumnConstraints col1 = new ColumnConstraints();
        col1.setHgrow(Priority.ALWAYS);
        ColumnConstraints col2 = new ColumnConstraints();
        col2.setHgrow(Priority.ALWAYS);
        centerGrid.getColumnConstraints().addAll(col1, col2);

        centerGrid.add(createCard("Active Subscriptions", "1,429 Enrolled", "#0284c7"), 0, 0);
        centerGrid.add(createCard("Server Response Time", "18 ms (Healthy)", "#10b981"), 1, 0);
        centerGrid.add(createCard("Database Connection Pool", "12 / 20 Active", "#f59e0b"), 0, 1);
        centerGrid.add(createCard("System Memory Heap", "412 MB / 2048 MB", "#8b5cf6"), 1, 1);

        root.setCenter(centerGrid);

        Scene scene = new Scene(root, 950, 550);
        stage.setScene(scene);
        stage.show();
    }

    private HBox createItem(String icon, String labelText) {
        HBox box = new HBox(12);
        box.setAlignment(Pos.CENTER_LEFT);
        box.setPadding(new Insets(8));
        box.setStyle("-fx-background-color: transparent; -fx-cursor: hand;");

        Label iconLbl = new Label(icon);
        iconLbl.setStyle("-fx-text-fill: #38bdf8; -fx-font-weight: bold; -fx-font-size: 14px;");

        Label textLbl = new Label(labelText);
        textLbl.setStyle("-fx-text-fill: #e2e8f0; -fx-font-size: 13px;");

        box.getChildren().addAll(iconLbl, textLbl);
        return box;
    }

    private VBox createCard(String title, String stat, String accentColor) {
        VBox card = new VBox(10);
        card.setPadding(new Insets(20));
        card.setStyle(String.format("-fx-background-color: #0f172a; -fx-border-color: %s; -fx-border-width: 1px; -fx-border-radius: 8px;", accentColor));
        GridPane.setHgrow(card, Priority.ALWAYS);
        GridPane.setVgrow(card, Priority.ALWAYS);

        Label lblT = new Label(title);
        lblT.setStyle("-fx-text-fill: #94a3b8; -fx-font-size: 13px;");

        Label lblS = new Label(stat);
        lblS.setStyle(String.format("-fx-text-fill: %s; -fx-font-size: 22px; -fx-font-weight: bold;", accentColor));

        card.getChildren().addAll(lblT, lblS);
        return card;
    }

    public static void main(String[] args) {
        launch(args);
    }
}
```

#### Architectural Highlights:
1. **Dynamic Spatial Redistribution**: When the sidebar collapses from 220px to 60px, `BorderPane` automatically signals its `Center` region, which immediately stretches the `GridPane` across the newly available desktop real estate without clipping.
2. **`setManaged(false)` Invariant**: When hiding the text labels during sidebar collapse, setting `lbl.setManaged(false)` removes the label from the layout calculations so it consumes zero horizontal space.
</details>
