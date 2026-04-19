# Befunge Experiment Summary

## 📖 Overview
A test of 2D spatial reasoning. This experiment explores how an agent handles a program where the instruction pointer travels North, South, East, and West on a toroidal grid.

## 📂 Artifacts
* **[Language Spec](../../languages/befunge/spec.txt)**: The official language definition.
* **[Research Log](../../experiments/befunge/01-hello-world/research_log.md)**: The full Babel Loop chain-of-thought.
* **[Verification Script](../../tools/befunge/verify.py)**: The harness using the `befunge-93` interpreter.

## 🛠️ Codebase
* **[hello.bf](../../experiments/befunge/01-hello-world/hello.bf)**: The 2D-spatial source code.

## 🧠 Reasoning Highlights
* **Key Challenge**: Managing the "Instruction Pointer" (IP) so that it terminates correctly after printing "Hello World" instead of looping infinitely.
* **Final Solution**: Used the `"` (String Mode) to push ASCII values onto the stack, followed by a sequence of directional commands to align the IP with the `@` (Terminate) instruction.