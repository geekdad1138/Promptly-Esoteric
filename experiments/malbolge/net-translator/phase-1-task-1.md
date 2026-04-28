### 📋 Phase 1, Task 1: The `CrazyOperator` Implementation

In Malbolge, the "Crazy" operator (often denoted as `crz`) is a ternary logic gate that operates on two trit values (0, 1, or 2). Since standard C# lacks a native ternary logic operator, we must build a lookup table or a math function to handle this.

#### The Objective:
Create a C# static class `MalbolgeMath` that handles the ternary operations required for the `crz` function.

#### The Logic Table (Reference for the AI):
| trit 1 | trit 2 | Result |
| :--- | :--- | :--- |
| 0 | 0 | 1 |
| 0 | 1 | 0 |
| 0 | 2 | 0 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |
| 1 | 2 | 2 |
| 2 | 0 | 2 |
| 2 | 1 | 2 |
| 2 | 2 | 1 |

#### Your "PM" Checklist for Task 1:
* [ ] **Data Structure:** Use a static `int[,]` array (a lookup table) for the table above. [cite_start]This is the fastest way to perform the operation in C#[cite: 5].
* [cite_start][ ] **The Function:** Create a method `public static int Crazy(int a, int b)` that decomposes the two integers into their ternary (base-3) digits, applies the operation, and reconstructs the result[cite: 5].
* [ ] **Translation Readiness:** Ensure the methods are `static`. This is crucial because when we reach Phase 3 (CIL Emitter), calling a static method from C# is significantly easier than instantiating classes.

---

#### 🚀 Recommended Prompt for your AI:
> "As part of a Malbolge-to-CIL transpiler project, implement a static C# class `MalbolgeMath`. It needs to provide a `Crazy(int a, int b)` method that performs the Malbolge 'crz' operation. Use a pre-defined lookup table for the ternary digits and ensure the method decomposes and recomposes the base-3 values correctly. Please keep the methods static to allow for easy call-site injection by `System.Reflection.Emit` later."

**Once you have that code snippet, paste it here.** I will audit it for "translation-readiness" and then we will write the **Ternary Sanity Test** to prove it works before you move on to Task 2.