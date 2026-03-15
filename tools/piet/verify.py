import sys
from PietInterpreter import Interpreter

def run_piet(image_path):
    # This library typically prints to stdout directly
    interpreter = Interpreter(image_path)
    try:
        print(f"--- Executing {image_path} ---")
        interpreter.run()
        print("\n--- Execution Finished ---")
    except Exception as e:
        print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    run_piet(sys.argv[1])