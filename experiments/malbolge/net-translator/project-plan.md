### 🏗️ Project Plan: The "Malbolge.NET" Roadmap

We will tackle this in four distinct phases to ensure each piece is testable before moving to the next.

| Phase | Component | Goal |
| :--- | :--- | :--- |
| **Phase 1** | **The Ternary Core** | Create a C# library that simulates the 10-bit ternary memory space and the "Crazy Operator." |
| **Phase 2** | **The Intermediate Representation (IR)** | Build a parser that converts `.mb` source code into a linear sequence of Malbolge instructions (pre-modification). |
| **Phase 3** | **The CIL Emitter** | Implement a generator that maps these instructions to valid CIL opcodes using `System.Reflection.Emit`. |
| **Phase 4** | **The Runtime Support** | Connect the CIL output to the Core library to handle execution and memory wrapping. |

---

### 🧩 Phase 1: The Ternary Core (The "Brain")
Before we even look at CIL, we need a C# class that understands Malbolge's unique logic. We’ll call this `MalbolgeRuntime.cs`.

**Key Logic to implement:**
* [cite_start]**The Memory Space:** An array of $59,049$ ($3^{10}$) ternary values[cite: 3].
* [cite_start]**The "Crazy" Operator ($crz$):** The base-3 logical operation that defines the language's "hellish" nature[cite: 3].
* [cite_start]**Self-Modification:** Since every instruction modifies the memory and its own pointer upon execution, this logic must be decoupled from the instruction execution loop[cite: 3].

---

### 🚀 Taking the First Step
To start, I suggest we create a new sub-folder in your project structure: `experiments/malbolge/net-translator/`.

**Should we start by defining the `CrazyOperator` logic in C#?** This is the heart of Malbolge and the most critical piece of the "Brain" phase. Once we have a tested `CrazyOperator` library, the rest of the translation logic will be much easier to build upon. 
