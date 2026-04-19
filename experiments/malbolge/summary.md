# Malbolge Experiment Summary

## 📖 Overview
An investigation into the "Eighth Circle of Hell." This experiment tested if an AI agent could manage self-modifying ternary logic (base-3) without pre-training on Malbolge codebases. 

## 📂 Artifacts
* **[Language Spec](../../languages/malbolge/spec.txt)**: The official language definition.
* **[Research Log](../../experiments/malbolge/01-hello-world/research_log.md)**: The full Babel Loop chain-of-thought and error logs.
* **[Verification Script](../../tools/malbolge/verify.py)**: The harness used to validate ternary output.

## 🛠️ Codebase
* **[hello.mb](../../experiments/malbolge/01-hello-world/hello.mb)**: The final generated Malbolge source code.
* **[gen_malbolge4.py](../../experiments/malbolge/01-hello-world/gen_malbolge4.py)**: The final iteration of the generator script.

## 🧠 Reasoning Highlights
* **Key Challenge**: Malbolge’s self-modifying nature means that every operation changes the code itself, making standard debugging impossible.
* **Final Solution**: The agent utilized a "Trial-and-Error" feedback loop, re-writing the code based on specific failure offsets provided by the `verify.py` script.