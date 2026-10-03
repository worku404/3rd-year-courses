# Lesson 2 — Expression Parsing Mechanics: Infix, Postfix & Shunting-Yard Algorithm

> [!NOTE]
> **Learning Outcomes:**
> - Contrast **Infix**, **Prefix (Polish)**, and **Postfix (Reverse Polish)** algebraic representations in compiler theory.
> - Formalize Edsger Dijkstra's **Shunting-Yard Algorithm** for converting arbitrary infix syntax into postfix streams.
> - Implement the operator precedence lattice and associativity mechanics (Left-to-Right vs. Right-to-Left exponentiation).
> - Architect an $O(n)$ single-pass **Postfix Evaluation Engine** with strict non-commutative operand pop safeguards.
> - Synthesize an **Abstract Syntax Tree (AST)** directly from postfix token streams for runtime query evaluation.

{{media:parsing-video}}

{{media:parsing-visual}}

## Executive Summary & Compiler Context

In human mathematical notation, expressions are fundamentally written in **Infix format** ($A + B$), where operators sit symmetrically between their operands. While intuitive to human readers, infix syntax is computationally ambiguous without auxiliary conventions: it requires operator precedence rules ($* > +$), associativity conventions (left-to-right), and explicit parentheses to override priority.

For compilers, interpreters, and hardware execution units (such as the JVM operand stack, Hewlett-Packard scientific calculators, and the PostScript engine), parsing infix syntax directly on the fly is computationally inefficient and error-prone. Modern language runtimes eliminate syntax ambiguity by translating infix into **Postfix notation** (also known as **Reverse Polish Notation** or **RPN**, pioneered by Jan Łukasiewicz). In Postfix, operators immediately follow their operands ($A B +$). This guarantees three profound computational properties:
1. **Parentheses are completely unnecessary**: The topological position of each operator uniquely encodes its scope.
2. **Deterministic Precedence**: Higher precedence operations naturally precede lower precedence operations in the evaluation stream.
3. **Strict $O(n)$ Single-Pass Evaluation**: Evaluated using a single operand stack with zero lookahead or backtracking.

---

## 1. Expression Notations Compared

| Notation | Formal Structural Syntax | Example | Parentheses Needed? | Parsing Machine Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Infix** | $\\langle \\text{Operand}_1 \\rangle \\; \\langle \\text{Operator} \\rangle \\; \\langle \\text{Operand}_2 \\rangle$ | $(A + B) * C - D$ | **Mandatory** | High (Grammar lookahead, recursive descent) |
| **Prefix (Polish)** | $\\langle \\text{Operator} \\rangle \\; \\langle \\text{Operand}_1 \\rangle \\; \\langle \\text{Operand}_2 \\rangle$ | $- * + A B C D$ | **None** | Low (Right-to-Left stack pass) |
| **Postfix (RPN)** | $\\langle \\text{Operand}_1 \\rangle \\; \\langle \\text{Operand}_2 \\rangle \\; \\langle \\text{Operator} \\rangle$ | $A B + C * D -$ | **None** | **Minimal** (Left-to-Right single stack pass) |

---

## 2. Dijkstra's Shunting-Yard Algorithm (Infix to Postfix)

Invented in 1961 by Edsger W. Dijkstra, the Shunting-Yard algorithm uses an operator stack to buffer operators while passing operands directly to the output stream, behaving like a railroad switching yard.

```
       [ INFIX INPUT TOKENS ] ──► (A + B) * C
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
             Is OPERAND?                           Is OPERATOR?
                   │                                     │
                   ▼                                     ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │ Direct to OUTPUT    │               │  Inspect OP STACK   │
        │ Buffer: [ A, B ]    │               │  Precedence Checks  │
        └─────────────────────┘               └──────────┬──────────┘
                                                         │
                                                         ▼
                                              ┌─────────────────────┐
                                              │  OPERATOR STACK     │
                                              │      [ * ]          │
                                              │      [ + ]          │
                                              └─────────────────────┘
```

### 2.1 Operator Precedence & Associativity Lattice
Each operator is assigned an integer rank and associativity:

| Operator | Symbol | Precedence | Associativity | Algebraic Semantics |
| :--- | :--- | :--- | :--- | :--- |
| **Parentheses** | `(`, `)` | N/A (Scope) | N/A | Sub-expression isolation delimiter |
| **Exponentiation** | `^` | 3 (Highest) | **Right-to-Left** | $2^{3^2} = 2^9 = 512$ (NOT $8^2 = 64$) |
| **Multiplicative** | `*`, `/`, `%` | 2 | **Left-to-Right** | Multiplicative operations |
| **Additive** | `+`, `-` | 1 (Lowest) | **Left-to-Right** | Additive operations |

### 2.2 Formal State Transition Rules
For each token $t$ in the input token stream:
1. **Operand**: Append $t$ directly to the output buffer.
2. **Left Parenthesis `(`**: Push `(` onto the operator stack.
3. **Right Parenthesis `)`**:
   - Repeatedly pop operators from the stack and append to output until a matching `(` is popped.
   - Discard both parentheses. If stack empties without finding `(`, throw `MismatchedParenthesesException`.
4. **Operator $O_1$**:
   - While stack is not empty AND top of stack $O_2 \ne \text{'('}$ AND:
     - ($O_1$ is Left-Associative AND $\text{prec}(O_1) \le \text{prec}(O_2)$) OR
     - ($O_1$ is Right-Associative AND $\text{prec}(O_1) < \text{prec}(O_2)$):
       - Pop $O_2$ from stack to output buffer.
   - Push $O_1$ onto operator stack.
5. **End of Input (EOF)**: Pop all remaining operators from stack to output. If any `(` remains, syntax is invalid.

---

## 3. Comprehensive Trace Analysis (Course Slide Example)

Let us trace the conversion of the complex university curriculum expression (from Slide 34):
$$\mathbf{A + [ (B + C) + (D + E) * F ] / G}$$

Treating square brackets `[` as standard scoping parentheses `(`:

| Step | Token | Action Taken | Operator Stack | Output Stream (RPN Buffer) |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `A` | Append operand | `[]` | `A` |
| 2 | `+` | Push operator | `[+]` | `A` |
| 3 | `(` | Push open paren | `[+, (]` | `A` |
| 4 | `(` | Push open paren | `[+, (, (]` | `A` |
| 5 | `B` | Append operand | `[+, (, (]` | `A B` |
| 6 | `+` | Push operator | `[+, (, (, +]` | `A B` |
| 7 | `C` | Append operand | `[+, (, (, +]` | `A B C` |
| 8 | `)` | Pop till matching `(` | `[+, (]` | `A B C +` |
| 9 | `+` | Top is `(`, push `+` | `[+, (, +]` | `A B C +` |
| 10 | `(` | Push open paren | `[+, (, +, (]` | `A B C +` |
| 11 | `D` | Append operand | `[+, (, +, (]` | `A B C + D` |
| 12 | `+` | Push operator | `[+, (, +, (, +]` | `A B C + D` |
| 13 | `E` | Append operand | `[+, (, +, (, +]` | `A B C + D E` |
| 14 | `)` | Pop till matching `(` | `[+, (, +]` | `A B C + D E +` |
| 15 | `*` | $\text{prec}(*) > \text{prec}(+)$, push `*` | `[+, (, +, *]` | `A B C + D E +` |
| 16 | `F` | Append operand | `[+, (, +, *]` | `A B C + D E + F` |
| 17 | `)` | Pop till matching `(` | `[+]` | `A B C + D E + F * +` |
| 18 | `/` | $\text{prec}(/) > \text{prec}(+)$, push `/` | `[+, /]` | `A B C + D E + F * +` |
| 19 | `G` | Append operand | `[+, /]` | `A B C + D E + F * + G` |
| 20 | **EOF** | Drain stack completely | `[]` | **`A B C + D E + F * + G / +`** |

---

## 4. Postfix Expression Evaluation Engine

Evaluating a postfix expression requires **zero knowledge of operator precedence or associativity**. The order of execution is completely deterministic.

### 4.1 Evaluation Algorithm
1. Initialize an empty **Operand Stack**.
2. Scan the postfix token sequence from left to right:
   - If token is an **Operand**: Push its numerical value onto the stack.
   - If token is an **Operator**:
     - Pop operand $2$ (`op2 = stack.pop()`).
     - Pop operand $1$ (`op1 = stack.pop()`).
     - Compute: $\text{result} = \text{op1} \; \langle \text{operator} \rangle \; \text{op2}$.
     - Push $\text{result}$ back onto the stack.
3. At EOF, the stack must contain **exactly one element**, which is the final evaluated result.

> [!CAUTION]
> **Non-Commutative Operand Pop Inversion:**
> In subtraction (`-`) and division (`/`), order is critical ($a - b \ne b - a$ and $a / b \ne b / a$). Because stacks are LIFO, the first popped element is the **right-hand operand** (`op2`), and the second popped element is the **left-hand operand** (`op1`). Swapping them produces completely invalid calculations.

### 4.2 Numerical Trace (Curriculum Slide 31)
Evaluate the expression:
$$\mathbf{6 \quad 5 \quad 2 \quad 3 \quad + \quad 8 \quad * \quad + \quad 3 \quad + \quad *}$$

| Step | Scanned Token | Action | Calculation | Operand Stack State |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `6` | Push operand | - | `[6]` |
| 2 | `5` | Push operand | - | `[6, 5]` |
| 3 | `2` | Push operand | - | `[6, 5, 2]` |
| 4 | `3` | Push operand | - | `[6, 5, 2, 3]` |
| 5 | `+` | Pop 3, Pop 2 | $2 + 3 = 5$ | `[6, 5, 5]` |
| 6 | `8` | Push operand | - | `[6, 5, 5, 8]` |
| 7 | `*` | Pop 8, Pop 5 | $5 * 8 = 40$ | `[6, 5, 40]` |
| 8 | `+` | Pop 40, Pop 5 | $5 + 40 = 45$ | `[6, 45]` |
| 9 | `3` | Push operand | - | `[6, 45, 3]` |
| 10 | `+` | Pop 3, Pop 45 | $45 + 3 = 48$ | `[6, 48]` |
| 11 | `*` | Pop 48, Pop 6 | $6 * 48 = 288$ | **`[288]` (FINAL RESULT)** |

---

## 5. Complete Production Java Implementation

```java
package edu.se.datastructures.parsing;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class ShuntingYardParser {

    private static int precedence(char op) {
        return switch (op) {
            case '+', '-' -> 1;
            case '*', '/', '%' -> 2;
            case '^' -> 3;
            default -> -1;
        };
    }

    private static boolean isRightAssociative(char op) {
        return op == '^';
    }

    public static List<String> toPostfix(String infix) {
        List<String> output = new ArrayList<>();
        Deque<Character> opStack = new ArrayDeque<>();
        StringBuilder numBuffer = new StringBuilder();

        for (int i = 0; i < infix.length(); i++) {
            char c = infix.charAt(i);

            if (Character.isWhitespace(c)) continue;

            if (Character.isDigit(c) || c == '.') {
                numBuffer.append(c);
                while (i + 1 < infix.length() && (Character.isDigit(infix.charAt(i + 1)) || infix.charAt(i + 1) == '.')) {
                    numBuffer.append(infix.charAt(++i));
                }
                output.add(numBuffer.toString());
                numBuffer.setLength(0);
            } else if (Character.isLetter(c)) {
                output.add(String.valueOf(c));
            } else if (c == '(' || c == '[') {
                opStack.push('(');
            } else if (c == ')' || c == ']') {
                while (!opStack.isEmpty() && opStack.peek() != '(') {
                    output.add(String.valueOf(opStack.pop()));
                }
                if (opStack.isEmpty()) throw new IllegalArgumentException("Mismatched parentheses");
                opStack.pop(); // Discard '('
            } else if ("+-*/%^".indexOf(c) != -1) {
                while (!opStack.isEmpty() && opStack.peek() != '(') {
                    char top = opStack.peek();
                    int p1 = precedence(c);
                    int p2 = precedence(top);
                    if ((!isRightAssociative(c) && p1 <= p2) || (isRightAssociative(c) && p1 < p2)) {
                        output.add(String.valueOf(opStack.pop()));
                    } else {
                        break;
                    }
                }
                opStack.push(c);
            } else {
                throw new IllegalArgumentException("Unknown character: " + c);
            }
        }

        while (!opStack.isEmpty()) {
            char op = opStack.pop();
            if (op == '(') throw new IllegalArgumentException("Mismatched parentheses");
            output.add(String.valueOf(op));
        }

        return output;
    }

    public static double evaluatePostfix(List<String> postfixTokens) {
        Deque<Double> stack = new ArrayDeque<>();

        for (String token : postfixTokens) {
            if (token.length() == 1 && "+-*/%^".contains(token)) {
                if (stack.size() < 2) throw new IllegalStateException("Malformed expression syntax");
                double op2 = stack.pop();
                double op1 = stack.pop();

                double res = switch (token.charAt(0)) {
                    case '+' -> op1 + op2;
                    case '-' -> op1 - op2;
                    case '*' -> op1 * op2;
                    case '/' -> {
                        if (op2 == 0.0) throw new ArithmeticException("Division by zero");
                        yield op1 / op2;
                    }
                    case '%' -> op1 % op2;
                    case '^' -> Math.pow(op1, op2);
                    default -> throw new IllegalStateException();
                };
                stack.push(res);
            } else {
                stack.push(Double.parseDouble(token));
            }
        }

        if (stack.size() != 1) throw new IllegalStateException("Malformed expression: excessive operands");
        return stack.pop();
    }
}
```

---

## 6. Three-Tier Progressive Mastery Challenges

### Level 1: Architecture Walkthrough
Convert the infix expression:
$$A * (B + C) / D - E \wedge F \wedge G$$
into Postfix using Dijkstra's algorithm. Show the final RPN string and explain how the consecutive `^` operators are handled.

<details>
<summary>View Level 1 Solution & Explanation</summary>

**Step-by-step conversion:**
1. `(B + C)` reduces to `B C +` inside parentheses.
2. `A * (B C +)` becomes `A B C + *`.
3. Division `/ D` produces `A B C + * D /`.
4. Right-associative exponentiation: $E \wedge F \wedge G$ evaluated right-to-left as $E \wedge (F \wedge G)$. In postfix, operands appear in original order, operators are ordered to evaluate rightmost first: `E F G ^ ^`.
5. Finally, subtraction links the two sub-expressions:
   **Result:** `A B C + * D / E F G ^ ^ -`
</details>

---

### Level 2: Scaffolded System Refactoring — Unary Minus Disambiguation
**Problem Statement:** In infix syntax, `-` can represent binary subtraction ($5 - 2$) or unary negation ($-5$). Refactor the lexer/parser to identify unary operators and emit them as a dedicated high-precedence postfix token `NEG`.

<details>
<summary>View Complete Java Lexer Refactoring</summary>

```java
public static List<String> toPostfixWithUnary(String infix) {
    List<String> output = new ArrayList<>();
    Deque<String> opStack = new ArrayDeque<>();
    boolean expectUnary = true; // True at start of expr or after any operator/'('

    for (int i = 0; i < infix.length(); i++) {
        char c = infix.charAt(i);
        if (Character.isWhitespace(c)) continue;

        if (Character.isDigit(c)) {
            // Read entire number
            int start = i;
            while (i + 1 < infix.length() && (Character.isDigit(infix.charAt(i + 1)) || infix.charAt(i + 1) == '.')) i++;
            output.add(infix.substring(start, i + 1));
            expectUnary = false;
        } else if (c == '(') {
            opStack.push("(");
            expectUnary = true;
        } else if (c == ')') {
            while (!opStack.isEmpty() && !opStack.peek().equals("(")) {
                output.add(opStack.pop());
            }
            opStack.pop();
            expectUnary = false;
        } else if (c == '-' && expectUnary) {
            // Identified as Unary Minus! Push as 'NEG' with highest precedence
            opStack.push("NEG");
        } else if ("+-*/^".indexOf(c) != -1) {
            String op = String.valueOf(c);
            while (!opStack.isEmpty() && !opStack.peek().equals("(") &&
                   precedence(op.charAt(0)) <= precedence(opStack.peek().charAt(0))) {
                output.add(opStack.pop());
            }
            opStack.push(op);
            expectUnary = true;
        }
    }
    while (!opStack.isEmpty()) output.add(opStack.pop());
    return output;
}
```
</details>

---

### Level 3: Senior Systems Engineering Challenge — AST Builder from Postfix
**Problem Statement:** Build an executable **Abstract Syntax Tree (AST)** directly from a postfix token stream to enable query optimization, dead-code pruning, and compilation into bytecode.

<details>
<summary>View Complete AST Synthesis Engine</summary>

```java
package edu.se.datastructures.ast;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;

public class ExpressionAstBuilder {

    public interface ExprNode {
        double evaluate();
        String toInfixString();
    }

    public static final class NumberNode implements ExprNode {
        private final double value;
        public NumberNode(double value) { this.value = value; }
        @Override public double evaluate() { return value; }
        @Override public String toInfixString() { return Double.toString(value); }
    }

    public static final class BinaryOpNode implements ExprNode {
        private final char op;
        private final ExprNode left;
        private final ExprNode right;

        public BinaryOpNode(char op, ExprNode left, ExprNode right) {
            this.op = op;
            this.left = left;
            this.right = right;
        }

        @Override
        public double evaluate() {
            double l = left.evaluate();
            double r = right.evaluate();
            return switch (op) {
                case '+' -> l + r;
                case '-' -> l - r;
                case '*' -> l * r;
                case '/' -> l / r;
                case '^' -> Math.pow(l, r);
                default -> throw new UnsupportedOperationException();
            };
        }

        @Override
        public String toInfixString() {
            return "(" + left.toInfixString() + " " + op + " " + right.toInfixString() + ")";
        }
    }

    public static ExprNode buildAst(List<String> postfixTokens) {
        Deque<ExprNode> stack = new ArrayDeque<>();

        for (String token : postfixTokens) {
            if (token.length() == 1 && "+-*/^".contains(token)) {
                ExprNode right = stack.pop();
                ExprNode left = stack.pop();
                stack.push(new BinaryOpNode(token.charAt(0), left, right));
            } else {
                stack.push(new NumberNode(Double.parseDouble(token)));
            }
        }
        return stack.pop();
    }
}
```
</details>
