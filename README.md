# Promptly-Esoteric 🌀

An experimental framework designed to test the limits of LLM reasoning through the lens of **Esoteric Programming Languages (Esolangs)**.

Inspired by recent research (e.g., USC’s Idris/GPT-5 study), this repository documents the process of using **closed-loop compiler feedback** to "teach" AI how to program in languages with near-zero training data.

## 🔬 The Hypothesis

Most LLMs are trained on massive datasets of Python, JavaScript, and C++. By forcing an AI to write in languages like **Malbolge**, **Brainfuck**, or **LOLCODE**, we strip away its "memory" of common patterns and force it to rely purely on:

1. **Syntactic Logic:** Following a provided grammar or specification.
2. **Iterative Correction:** Learning from interpreter/compiler error logs in a recursive loop.
3. **Abstract Reasoning:** Solving logic puzzles in environments designed to be "human-impossible."

## 🛠️ The "Babel Loop" Workflow

This project utilizes a feedback loop between the LLM and the local environment:

1. **Prompt:** The AI is given the language specification and a task (e.g., "Output 'Hello World'").
2. **Execution:** The generated code is run through a local interpreter (via VS Code/Terminal).
3. **Feedback:** If it fails, the error log (or incorrect output) is fed back to the AI.
4. **Refinement:** The AI adjusts its logic until the unit test passes.

## 🗂️ Language Roadmap

* [ ] **Malbolge:** The "Eight Circle of Hell." Testing if AI can navigate self-modifying ternary code.
* [ ] **Brainfuck:** Minimalist pointer manipulation and memory management.
* [ ] **Piet:** Visual programming—can the AI describe/generate a functional bitmap image?
* [ ] **Befunge:** Two-dimensional code flow that defies standard top-down parsing.

## 🚀 Getting Started

To run these experiments locally, you will need the following interpreters installed in your environment:

```bash
# Example: Installing a Malbolge interpreter (C-based)
gcc malbolge.c -o malbolge
./malbolge your_ai_generated_code.mb

```
