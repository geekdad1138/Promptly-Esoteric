import sys
from malbolge import eval

def test_code(file_path, expected_output="Hello World"):
    with open(file_path, 'r') as f:
        code = f.read()
    try:
        # Run the malbolge code
        actual_output = eval(code)
        if actual_output.strip() == expected_output:
            print("✅ PASS: Output matches!")
        else:
            print(f"❌ FAIL: Expected '{expected_output}', got '{actual_output}'")
    except Exception as e:
        print(f"💥 INTERPRETER ERROR: {str(e)}")

if __name__ == "__main__":
    test_code(sys.argv[1])