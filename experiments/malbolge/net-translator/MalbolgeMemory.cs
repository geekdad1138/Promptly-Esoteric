using System;

/// <summary>
/// MalbolgeMemory: Manages the Malbolge memory buffer.
/// Implements the 59,049-cell circular memory system with proper initialization.
/// </summary>
public class MalbolgeMemory
{
    /// <summary>
    /// Memory size: 3^10 = 59,049 cells
    /// </summary>
    public const int MemorySize = 59049;

    /// <summary>
    /// Valid Malbolge operations (used for character validation)
    /// </summary>
    private static readonly int[] ValidOperations = { 4, 5, 23, 39, 40, 62, 68, 81 };

    /// <summary>
    /// The memory buffer
    /// </summary>
    private readonly int[] _memory;

    /// <summary>
    /// Code pointer (C register)
    /// </summary>
    public int CodePointer { get; set; }

    /// <summary>
    /// Data pointer (D register)
    /// </summary>
    public int DataPointer { get; set; }

    /// <summary>
    /// Initializes a new instance of MalbolgeMemory with an empty buffer.
    /// </summary>
    public MalbolgeMemory()
    {
        _memory = new int[MemorySize];
        CodePointer = 0;
        DataPointer = 0;
    }

    /// <summary>
    /// Gets or sets a memory cell value with circular addressing.
    /// </summary>
    /// <param name="index">The memory index (will wrap around at MemorySize)</param>
    /// <returns>The value at the specified memory location</returns>
    public int this[int index]
    {
        get => _memory[index % MemorySize];
        set => _memory[index % MemorySize] = value;
    }

    /// <summary>
    /// Initializes memory from source code.
    /// Filters out whitespace, validates characters, loads program, and fills remaining memory.
    /// </summary>
    /// <param name="sourceCode">The Malbolge source code</param>
    public void InitializeMemory(string sourceCode)
    {
        // Reset memory and pointers
        Array.Clear(_memory, 0, MemorySize);
        CodePointer = 0;
        DataPointer = 0;

        // Load program into memory
        int programLength = LoadProgram(sourceCode);

        // Fill remaining memory using crazy operation
        FillRemainingMemory(programLength);
    }

    /// <summary>
    /// Loads the program into memory, filtering out whitespace and validating characters.
    /// </summary>
    /// <param name="sourceCode">The source code to load</param>
    /// <returns>The length of the loaded program</returns>
    private int LoadProgram(string sourceCode)
    {
        int position = 0;

        foreach (char c in sourceCode)
        {
            // Skip whitespace
            if (c == ' ' || c == '\n' || c == '\r' || c == '\t')
                continue;

            // Validate character (optional for transpiler, but good practice)
            if (!IsValidMalbolgeCharacter(c, position))
            {
                throw new ArgumentException($"Invalid Malbolge character '{c}' at position {position}");
            }

            // Check bounds
            if (position >= MemorySize)
            {
                throw new ArgumentException("Program is too long for Malbolge memory");
            }

            // Load character into memory
            _memory[position] = c;
            position++;
        }

        return position;
    }

    /// <summary>
    /// Fills the remaining memory using the crazy operation: mem[i] = crazy(mem[i-1], mem[i-2])
    /// </summary>
    /// <param name="programLength">The length of the loaded program</param>
    private void FillRemainingMemory(int programLength)
    {
        for (int i = programLength; i < MemorySize; i++)
        {
            // For the first few positions, use 0 for missing previous values
            int prev1 = (i >= 1) ? _memory[i - 1] : 0;
            int prev2 = (i >= 2) ? _memory[i - 2] : 0;

            _memory[i] = Crazy(prev1, prev2);
        }
    }

    /// <summary>
    /// Validates if a character is valid Malbolge at the given position.
    /// </summary>
    /// <param name="c">The character to validate</param>
    /// <param name="position">The position in the program</param>
    /// <returns>True if the character is valid</returns>
    private static bool IsValidMalbolgeCharacter(char c, int position)
    {
        // Must be printable ASCII
        if (c < 33 || c > 126)
            return false;

        // Must map to a valid operation
        int operation = (c + position) % 94;
        return Array.IndexOf(ValidOperations, operation) >= 0;
    }

    /// <summary>
    /// Performs the Malbolge 'crz' (Crazy) operation on two integers.
    /// </summary>
    /// <param name="a">First operand</param>
    /// <param name="b">Second operand</param>
    /// <returns>The result of the Crazy operation</returns>
    private static int Crazy(int a, int b)
    {
        // Lookup table for the ternary operation
        int[,] crazyLookup = {
            { 1, 0, 0 },  // trit1 = 0
            { 1, 0, 2 },  // trit1 = 1
            { 2, 2, 1 }   // trit1 = 2
        };

        int result = 0;
        int power = 1;

        // Process each ternary digit (10 digits for 3^10 = 59049)
        for (int i = 0; i < 10; i++)
        {
            int tritA = a % 3;
            int tritB = b % 3;

            int tritResult = crazyLookup[tritA, tritB];
            result += tritResult * power;

            a /= 3;
            b /= 3;
            power *= 3;
        }

        return result;
    }
}