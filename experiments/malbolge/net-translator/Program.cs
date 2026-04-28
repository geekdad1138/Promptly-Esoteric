using System;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("=== Malbolge Transpiler Components Test ===\n");
        TestMalbolgeMath();
        TestMalbolgeMemory();
        Console.WriteLine("\n=== All Tests Complete ===");
    }

    static void TestMalbolgeMath()
    {
        Console.WriteLine("Testing MalbolgeMath.Crazy()...");
        RunCrazyTests();
    }

    static void TestMalbolgeMemory()
    {
        Console.WriteLine("Testing MalbolgeMemory...");
        RunMemoryTests();
    }

    static void RunCrazyTests()
    {
        int passCount = 0;
        int totalTests = 3;

        // Test 1: Crazy(0, 0) should return 1
        int result1 = MalbolgeMath.Crazy(0, 0);
        bool test1Passed = result1 == 1;
        passCount += test1Passed ? 1 : 0;
        Console.WriteLine($"  Crazy(0, 0) = {result1} -> {(test1Passed ? "PASS" : "FAIL")}");

        // Test 2: Crazy(1, 2) should return 2
        int result2 = MalbolgeMath.Crazy(1, 2);
        bool test2Passed = result2 == 2;
        passCount += test2Passed ? 1 : 0;
        Console.WriteLine($"  Crazy(1, 2) = {result2} -> {(test2Passed ? "PASS" : "FAIL")}");

        // Test 3: Crazy(2, 2) should return 1
        int result3 = MalbolgeMath.Crazy(2, 2);
        bool test3Passed = result3 == 1;
        passCount += test3Passed ? 1 : 0;
        Console.WriteLine($"  Crazy(2, 2) = {result3} -> {(test3Passed ? "PASS" : "FAIL")}");

        Console.WriteLine($"  Crazy tests: {passCount}/{totalTests} passed");
    }

    static void RunMemoryTests()
    {
        try
        {
            // Test memory initialization with a simple valid Malbolge program
            string testProgram = "b";  // Valid Malbolge character (maps to operation 4 at position 0)
            var memory = new MalbolgeMemory();

            Console.WriteLine($"  Initializing memory with program: {testProgram}");
            memory.InitializeMemory(testProgram);

            // Check that program was loaded
            int firstChar = memory[0];
            bool programLoaded = firstChar == 'b';
            Console.WriteLine($"  Memory[0] = {(char)firstChar} -> {(programLoaded ? "PASS" : "FAIL")}");

            // Check that remaining memory is filled (should not be 0)
            int someLaterValue = memory[100];
            bool memoryFilled = someLaterValue != 0;
            Console.WriteLine($"  Memory[100] filled: {someLaterValue != 0} -> {(memoryFilled ? "PASS" : "FAIL")}");

            // Test circular access
            int wrappedValue = memory[MalbolgeMemory.MemorySize];
            bool circularWorks = wrappedValue == memory[0];
            Console.WriteLine($"  Circular access works: {circularWorks} -> {(circularWorks ? "PASS" : "FAIL")}");

            Console.WriteLine("  Memory tests completed successfully");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"  Memory test failed with exception: {ex.Message}");
        }
    }
}
