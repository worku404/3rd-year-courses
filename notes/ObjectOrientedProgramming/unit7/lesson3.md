# Lesson 3 — The Delegation Event Model, Reactive Handlers & Enterprise MVC Architecture

> [!NOTE]
> **Learning Outcomes:**
> - Master the **Delegation Event Model**: identify the distinct roles of Event Sources, Event Objects, and Event Handlers.
> - Trace the **Event Dispatch Chain**: analyze the mechanics of Event Capturing, Event Bubbling, and event suppression via `event.consume()`.
> - Compare the four historical approaches to event handling: External classes, Inner classes, Anonymous classes, and modern **Java Lambdas**.
> - Eliminate manual UI observer synchronization using **JavaFX Observable Properties** and **Bidirectional Binding**.
> - Architect decoupled, enterprise-grade desktop applications applying the **Model-View-Controller (MVC)** design pattern.

{{media:event-video}}

{{media:event-visual}}

## Executive Summary & System Context

In procedural command-line applications, execution flow is strictly sequential and driven by the program: the computer prompts the user for input, waits synchronously, processes data, and prints an output. In graphical user interfaces, this paradigm is completely inverted into **Event-Driven Programming**.

In an event-driven system, the user is in complete control:
- The user can click a button, type into a field, resize the window, press a shortcut key, or drag an item at any arbitrary time.
- The application runtime enters an infinite event polling loop (the **Event Loop**), waiting for physical hardware interrupts.
- When an interaction occurs, the runtime packages the event details into an object and delegates execution to registered listener callbacks.

To make event handling modular, scalable, and type-safe, Java uses the **Delegation Event Model**.

---

## 1. The Delegation Event Handling Model

The Delegation Event Model separates the entity that **generates** an event from the code that **handles** it:

```
┌────────────────────────┐              ┌────────────────────────┐              ┌────────────────────────┐
│      Event Source      │              │      Event Object      │              │      Event Handler     │
│  (e.g., javafx Button) │              │  (e.g., ActionEvent)   │              │ (EventHandler<Action>) │
│                        │              │                        │              │                        │
│ Fires interaction upon │─────────────>│ Encapsulates source,   │─────────────>│ Executes business      │
│ user mouse click       │              │ timestamp, & metadata  │              │ transaction logic      │
└────────────────────────┘              └────────────────────────┘              └────────────────────────┘
```

### The Three Core Pillars:
1. **Event Source**: The user-interface component where the interaction originates (e.g., `Button`, `TextField`, `MenuItem`). The source provides registration methods allowing listeners to subscribe:
   ```java
   button.setOnAction(handler);
   ```
2. **Event Object**: An instance of `javafx.event.Event` (or a subclass) encapsulating diagnostic data about the interaction:
   - `getSource()`: Reference to the object that fired the event.
   - `getTarget()`: The initial target node in the Scene Graph.
   - `getEventType()`: Hierarchical categorization (e.g., `ActionEvent.ACTION`).
3. **Event Handler (Listener)**: An implementation of the functional interface `javafx.event.EventHandler<T extends Event>`:
   ```java
   @FunctionalInterface
   public interface EventHandler<T extends Event> extends EventListener {
       void handle(T event);
   }
   ```

---

## 2. Event Dispatch Chain: Capturing vs. Bubbling

When a user clicks a node (e.g., a `Button` inside a `GridPane` inside a `BorderPane` inside a `Scene` inside a `Stage`), the event travels through a structured two-phase **Event Dispatch Chain**:

```
[ Stage ]
   │  ▲
   │  │  1. Capturing Phase (Event Filter)
   │  │     Traverses DOWN the tree from Stage to Target.
   ▼  │     Filters intercept events before children see them.
[ Scene ]
   │  ▲
   │  │  2. Bubbling Phase (Event Handler)
   │  │     Traverses UP the tree from Target to Stage.
   ▼  │     Standard handlers execute on target, then bubble to parents.
[ Target: Button ]
```

### Event Consumption (`event.consume()`)
Any handler or filter along the dispatch chain can invoke `event.consume()`. This immediately halts propagation, preventing downstream or parent nodes from receiving the event:

```java
button.addEventHandler(MouseEvent.MOUSE_CLICKED, event -> {
    System.out.println("Button Clicked");
    event.consume(); // Prevents parent Pane from receiving the click!
});
```

---

## 3. Four Generations of Handler Implementation

Understanding how Java event handling syntax evolved from Java 1.1 to Java 21 is critical for reading legacy codebases and writing modern idiomatic software.

### Generation 1: Separate External Class (Obsolete & Cumbersome)
Requires passing references to all UI fields via constructor:
```java
public class SaveButtonHandler implements EventHandler<ActionEvent> {
    private final TextField txtInput;
    public SaveButtonHandler(TextField txtInput) { this.txtInput = txtInput; }

    @Override
    public void handle(ActionEvent event) {
        System.out.println("Saved: " + txtInput.getText());
    }
}
// Registration:
btnSave.setOnAction(new SaveButtonHandler(txtInput));
```

### Generation 2: Member Inner Class (Coupled)
Inner classes have access to enclosing class private fields, eliminating reference passing:
```java
public class MyWindow extends Application {
    private TextField txtInput;

    private class InnerSaveHandler implements EventHandler<ActionEvent> {
        @Override
        public void handle(ActionEvent event) {
            System.out.println("Saved: " + txtInput.getText());
        }
    }
}
```

### Generation 3: Anonymous Inner Class (Verbosity Smell)
Defined in-line without a class name. Eliminates dedicated classes, but introduces heavy boilerplate:
```java
btnSave.setOnAction(new EventHandler<ActionEvent>() {
    @Override
    public void handle(ActionEvent event) {
        System.out.println("Saved: " + txtInput.getText());
    }
});
```

### Generation 4: Modern Java Lambdas & Method References (Idiomatic)
Because `EventHandler<T>` is a `@FunctionalInterface` containing exactly one abstract method (`handle`), Java 8+ allows concise lambda expressions:

```java
// 1. Lambda Expression:
btnSave.setOnAction(e -> System.out.println("Saved: " + txtInput.getText()));

// 2. Multi-statement Lambda:
btnSubmit.setOnAction(e -> {
    validateForm();
    commitTransaction();
});

// 3. Method Reference:
btnClear.setOnAction(this::handleReset);
```

---

## 4. Reactive Property Binding: Eliminating Observer Boilerplate

In traditional GUI frameworks, synchronizing UI state with domain models required writing hundreds of lines of fragile listener code. JavaFX revolutionized desktop programming by introducing **Properties and Reactive Data Binding**.

```
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│       Source Property           │                 │       Target Property           │
│   slider.valueProperty()        │════════════════>│   lblValue.textProperty()       │
│                                 │   Auto-Sync     │                                 │
│ User drags slider to 75.0       │                 │ Text updates to "75.0" instantly│
└─────────────────────────────────┘                 └─────────────────────────────────┘
```

### Types of Property Binding:
#### 1. Unidirectional Binding (`target.bind(source)`)
The target property strictly mirrors the source property. The target becomes read-only:
```java
// Label text automatically updates whenever slider moves:
lblOutput.textProperty().bind(slider.valueProperty().asString("Volume: %.0f%%"));
```

#### 2. Bidirectional Binding (`propA.bindBidirectional(propB)`)
Both properties stay in mutual synchronization. Mutating either property immediately updates the other:
```java
// Text field and User Domain Model stay perfectly synchronized in real time:
txtUsername.textProperty().bindBidirectional(currentUser.nameProperty());
```

#### 3. Fluent Boolean Logic Binding
Dynamically enable or disable buttons based on input validity:
```java
// Submit button is disabled automatically if either field is empty!
btnSubmit.disableProperty().bind(
    txtName.textProperty().isEmpty().or(txtId.textProperty().isEmpty())
);
```

---

## 5. Enterprise Desktop Architecture: Model-View-Controller (MVC)

In enterprise engineering, UI layout, event handling, and domain logic must be strictly separated into the **MVC Triad**:

```
                       ┌───────────────────────────────┐
                       │             MODEL             │
                       │   (POJO Domain Objects &      │
                       │    Observable Properties)     │
                       └───────┬───────────────▲───────┘
                               │               │
                     Notifies  │               │ Mutates State
                     Property  │               │
                     Change    │               │
                               ▼               │
┌──────────────────────────────┐              ┌┴──────────────────────────────┐
│             VIEW             │              │          CONTROLLER           │
│   (JavaFX Scene Graph /      │─────────────>│   (Handles User Events &      │
│    Buttons, Labels, Tables)  │  User Action │    Coordinates Business Flow) │
└──────────────────────────────┘  (Click/Key) └───────────────────────────────┘
```

### 1. Model:
Pure business state. Uses JavaFX properties so the View can observe changes automatically without polling:
```java
public class Student {
    private final StringProperty name = new SimpleStringProperty();
    private final DoubleProperty gpa = new SimpleDoubleProperty();

    public Student(String name, double gpa) {
        this.name.set(name);
        this.gpa.set(gpa);
    }

    public StringProperty nameProperty() { return name; }
    public DoubleProperty gpaProperty() { return gpa; }
    public String getName() { return name.get(); }
    public double getGpa() { return gpa.get(); }
}
```

### 2. View:
Pure visual components (e.g., `TableView<Student>`, input controls, buttons). Does not perform business calculations.

### 3. Controller:
Glues the Model and View together. Registers event listeners, enforces validation rules, and dispatches asynchronous background tasks.

---

## 6. Comprehensive Trade-Off Matrix

| Paradigm / Pattern | Coupling | Lines of Code | Reusability | Debuggability |
| :--- | :--- | :--- | :--- | :--- |
| **Anonymous Inner Class** | Moderate | Verbose | Zero (In-line only) | Moderate |
| **Java Lambda (`e ->`)** | Low | Extremely Concise | Low (In-line) | High |
| **Manual Listeners** | High | Massive Boilerplate | Low | Fragile (Risk of memory leaks) |
| **Property Binding** | Zero (Declarative) | 1-2 lines | High | Optimal |
| **Desktop MVC** | Decoupled | Structured | Maximum | High |

---

## 7. Progressive 3-Tier Practical Challenges

### Level 1: Architecture Walkthrough — Tracing Event Bubbling & Consumption
**Objective**: Analyze the following JavaFX hierarchy. Predict the exact console output when the user clicks the `targetBtn`.

```java
StackPane root = new StackPane();
VBox box = new VBox();
Button targetBtn = new Button("Click Me");

box.getChildren().add(targetBtn);
root.getChildren().add(box);

// 1. Root Handler
root.addEventHandler(MouseEvent.MOUSE_CLICKED, e -> System.out.println("1: Root Caught Click"));

// 2. Box Handler
box.addEventHandler(MouseEvent.MOUSE_CLICKED, e -> {
    System.out.println("2: Box Caught Click");
    e.consume(); // Consumes event!
});

// 3. Button Handler
targetBtn.addEventHandler(MouseEvent.MOUSE_CLICKED, e -> System.out.println("3: Button Caught Click"));
```

<details>
<summary>View Level 1 Event Dispatch Analysis</summary>

#### Exact Console Output:
```text
3: Button Caught Click
2: Box Caught Click
```

#### Step-by-Step Dispatch Walkthrough:
1. The mouse click targets `targetBtn`.
2. **Bubbling Phase Commences**:
   - `targetBtn`'s handler executes first $\longrightarrow$ Prints `"3: Button Caught Click"`.
   - The event bubbles up to parent node `box`.
   - `box`'s handler executes second $\longrightarrow$ Prints `"2: Box Caught Click"`.
   - Inside `box`, `e.consume()` is invoked!
3. **Propagation Terminated**: Because the event was marked as consumed, the JVM stops bubbling. `root` never receives the event, and statement `"1: Root Caught Click"` is **never printed**!
</details>

---

### Level 2: Scaffolded System Refactoring — Replacing Fragile Observers with Reactive Binding
**Objective**: Refactor a legacy form that uses clunky `TextListener` callbacks to update a character count and submit button state into modern declarative property bindings.

#### Legacy Fragile Code:
```java
public class LegacyFormSync {
    private TextField txtBio = new TextField();
    private Label lblCount = new Label();
    private Button btnSubmit = new Button("Post");

    public void initListeners() {
        // Clunky manual listener: Must remember to trigger on every keystroke!
        txtBio.textProperty().addListener((obs, oldVal, newVal) -> {
            int len = newVal.length();
            lblCount.setText(len + " / 100 characters");
            if (len == 0 || len > 100) {
                btnSubmit.setDisable(true);
            } else {
                btnSubmit.setDisable(false);
            }
        });
    }
}
```

<details>
<summary>View Level 2 Refactored Reactive Solution</summary>

```java
package edu.se.reactive;

import javafx.beans.binding.Bindings;
import javafx.scene.control.*;

public class ModernFormSync {
    private final TextField txtBio = new TextField();
    private final Label lblCount = new Label();
    private final Button btnSubmit = new Button("Post");

    public void initBindings() {
        // 1. Declarative Character Count Display:
        // Automatically updates label text as string changes without manual string concatenation!
        lblCount.textProperty().bind(
            Bindings.createStringBinding(
                () -> txtBio.getText().length() + " / 100 characters",
                txtBio.textProperty()
            )
        );

        // 2. Fluent Boolean Binding:
        // Disable button if text is empty OR length exceeds 100 characters:
        btnSubmit.disableProperty().bind(
            txtBio.textProperty().isEmpty().or(
                Bindings.createBooleanBinding(
                    () -> txtBio.getText().length() > 100, 
                    txtBio.textProperty()
                )
            )
        );
    }
}
```
</details>

---

### Level 3: Senior SE Systems Challenge — Full MVC Student Registry Desktop Application
**Objective**: Architect a complete, production-grade desktop application implementing the **Model-View-Controller (MVC)** architecture.
- **Model**: `Student` entity using `StringProperty` and `DoubleProperty`.
- **View**: A `TableView<Student>` displaying records, dynamic filter input field, and live statistics dashboard.
- **Controller**: Manages an `ObservableList<Student>` and `FilteredList<Student>`, binding table columns to model properties and computing live class average GPAs reactively.

<details>
<summary>View Level 3 Complete Production Architecture</summary>

```java
package edu.se.mvc;

import javafx.application.Application;
import javafx.beans.binding.Bindings;
import javafx.beans.property.*;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.collections.transformation.FilteredList;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;

// ============================================================================
// 1. MODEL TIER
// ============================================================================
public class StudentRecordApp extends Application {

    public static class Student {
        private final StringProperty id = new SimpleStringProperty();
        private final StringProperty name = new SimpleStringProperty();
        private final DoubleProperty gpa = new SimpleDoubleProperty();

        public Student(String id, String name, double gpa) {
            this.id.set(id);
            this.name.set(name);
            this.gpa.set(gpa);
        }

        public StringProperty idProperty() { return id; }
        public StringProperty nameProperty() { return name; }
        public DoubleProperty gpaProperty() { return gpa; }
        public String getId() { return id.get(); }
        public String getName() { return name.get(); }
        public double getGpa() { return gpa.get(); }
    }

    // ============================================================================
    // 2. CONTROLLER & VIEW ASSEMBLY
    // ============================================================================
    private final ObservableList<Student> masterData = FXCollections.observableArrayList();

    @Override
    public void start(Stage stage) {
        stage.setTitle("AASTU SE - Student Academic Records (MVC Architecture)");

        // Seed Sample Enterprise Data
        masterData.addAll(
            new Student("ETS/0101/14", "Abera Kassa", 3.85),
            new Student("ETS/0102/14", "Bethlehem Tadesse", 3.92),
            new Student("ETS/0103/14", "Chala Gemechu", 3.45),
            new Student("ETS/0104/14", "Dawit Haile", 2.95)
        );

        BorderPane root = new BorderPane();
        root.setPadding(new Insets(15));

        // --- TOP: Filter Bar ---
        HBox filterBar = new HBox(10);
        filterBar.setPadding(new Insets(0, 0, 15, 0));
        filterBar.setAlignment(Pos.CENTER_LEFT);

        Label lblSearch = new Label("Search Registry:");
        lblSearch.setStyle("-fx-font-weight: bold;");

        TextField txtFilter = new TextField();
        txtFilter.setPromptText("Filter by student name or ID...");
        txtFilter.setPrefWidth(300);

        filterBar.getChildren().addAll(lblSearch, txtFilter);
        root.setTop(filterBar);

        // --- CENTER: Reactive TableView ---
        TableView<Student> table = new TableView<>();
        table.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY);

        TableColumn<Student, String> colId = new TableColumn<>("Student ID");
        colId.setCellValueFactory(cellData -> cellData.getValue().idProperty());

        TableColumn<Student, String> colName = new TableColumn<>("Full Name");
        colName.setCellValueFactory(cellData -> cellData.getValue().nameProperty());

        TableColumn<Student, Number> colGpa = new TableColumn<>("Cumulative GPA");
        colGpa.setCellValueFactory(cellData -> cellData.getValue().gpaProperty());

        table.getColumns().addAll(colId, colName, colGpa);

        // Reactive Filtering via FilteredList
        FilteredList<Student> filteredData = new FilteredList<>(masterData, p -> true);
        txtFilter.textProperty().addListener((observable, oldValue, newValue) -> {
            filteredData.setPredicate(student -> {
                if (newValue == null || newValue.isBlank()) return true;
                String lowerFilter = newValue.toLowerCase();
                return student.getName().toLowerCase().contains(lowerFilter) ||
                       student.getId().toLowerCase().contains(lowerFilter);
            });
        });
        table.setItems(filteredData);
        root.setCenter(table);

        // --- BOTTOM: Add Record Form & Live Telemetry ---
        VBox bottomContainer = new VBox(12);
        bottomContainer.setPadding(new Insets(15, 0, 0, 0));

        // Form Inputs
        HBox form = new HBox(10);
        form.setAlignment(Pos.CENTER_LEFT);

        TextField txtNewId = new TextField();
        txtNewId.setPromptText("ID (ETS/...)");
        txtNewId.setPrefWidth(120);

        TextField txtNewName = new TextField();
        txtNewName.setPromptText("Student Name");
        txtNewName.setPrefWidth(180);

        TextField txtNewGpa = new TextField();
        txtNewGpa.setPromptText("GPA (0.0 - 4.0)");
        txtNewGpa.setPrefWidth(110);

        Button btnAdd = new Button("Enroll Student");
        btnAdd.setStyle("-fx-background-color: #0284c7; -fx-text-fill: white; -fx-font-weight: bold;");

        // Reactive Button Enabler: disabled if fields are empty
        btnAdd.disableProperty().bind(
            txtNewId.textProperty().isEmpty().or(
            txtNewName.textProperty().isEmpty().or(
            txtNewGpa.textProperty().isEmpty()))
        );

        // Add Record Event Action
        btnAdd.setOnAction(e -> {
            try {
                double gpaVal = Double.parseDouble(txtNewGpa.getText().trim());
                if (gpaVal < 0.0 || gpaVal > 4.0) {
                    showError("GPA must be between 0.0 and 4.0");
                    return;
                }
                masterData.add(new Student(txtNewId.getText().trim(), txtNewName.getText().trim(), gpaVal));
                txtNewId.clear();
                txtNewName.clear();
                txtNewGpa.clear();
            } catch (NumberFormatException ex) {
                showError("Invalid numerical format for GPA.");
            }
        });

        form.getChildren().addAll(txtNewId, txtNewName, txtNewGpa, btnAdd);

        // Reactive Telemetry Summary
        HBox statsBar = new HBox(25);
        statsBar.setPadding(new Insets(8));
        statsBar.setStyle("-fx-background-color: #0f172a; -fx-border-radius: 4px;");

        Label lblTotal = new Label();
        lblTotal.setStyle("-fx-text-fill: #38bdf8; -fx-font-weight: bold;");
        lblTotal.textProperty().bind(Bindings.size(filteredData).asString("Visible Students: %d"));

        Label lblAvg = new Label();
        lblAvg.setStyle("-fx-text-fill: #10b981; -fx-font-weight: bold;");
        lblAvg.textProperty().bind(Bindings.createStringBinding(() -> {
            if (filteredData.isEmpty()) return "Average GPA: N/A";
            double sum = filteredData.stream().mapToDouble(Student::getGpa).sum();
            return String.format("Average GPA: %.2f", sum / filteredData.size());
        }, filteredData));

        statsBar.getChildren().addAll(lblTotal, lblAvg);
        bottomContainer.getChildren().addAll(form, statsBar);
        root.setBottom(bottomContainer);

        stage.setScene(new Scene(root, 750, 520));
        stage.show();
    }

    private void showError(String msg) {
        Alert alert = new Alert(Alert.AlertType.ERROR, msg, ButtonType.OK);
        alert.showAndWait();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
```

#### Architectural Highlights:
1. **Zero Synchronization Overhead**: Adding a student to `masterData` automatically refreshes the `TableView`, recalculates the `FilteredList`, updates the count label, and recomputes the average GPA via bindings.
2. **Decoupled Architecture**: The Model contains zero GUI references, making it unit-testable without launching the JavaFX runtime.
</details>
