using System;

/// <summary>
/// MalbolgeExecutor: Executes Malbolge instructions step by step.
/// Implements the fetch-decode-execute-mutate cycle for Malbolge operations.
/// </summary>
public class MalbolgeExecutor
{
    /// <summary>
    /// The memory instance used by this executor.
    /// </summary>
    private readonly MalbolgeMemory _memory;

    /// <summary>
    /// The accumulator register (A).
    /// </summary>
    public int Accumulator { get; set; }

    /// <summary>
    /// Encryption table for Malbolge instruction mutation.
    /// </summary>
    private static readonly char[] EncryptTable = "5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G\"i@".ToCharArray();

    /// <summary>
    /// Valid operation codes and their mappings.
    /// </summary>
    private enum Operation
    {
        Jmp = 4,    // Set C = mem[D]
        Out = 5,    // Print chr(A % 256)
        In = 23,    // Read input (not implemented yet)
        Rotr = 39,  // A = mem[D] = rotate(mem[D])
        Mov = 40,   // D = mem[D]
        Crz = 62,   // A = mem[D] = crazy(A, mem[D])
        Nop = 68,   // Do nothing
        End = 81    // Halt execution
    }

    /// <summary>
    /// Execution state.
    /// </summary>
    public bool IsHalted { get; private set; }

    /// <summary>
    /// Output collected during execution.
    /// </summary>
    public string Output { get; private set; } = string.Empty;

    /// <summary>
    /// Initializes a new instance of MalbolgeExecutor.
    /// </summary>
    /// <param name="memory">The Malbolge memory instance to use.</param>
    public MalbolgeExecutor(MalbolgeMemory memory)
    {
        _memory = memory ?? throw new ArgumentNullException(nameof(memory));
        Accumulator = 0;
        IsHalted = false;
    }

    /// <summary>
    /// Executes a single Malbolge instruction step.
    /// </summary>
    /// <returns>True if execution should continue, false if halted.</returns>
    public bool ExecuteStep()
    {
        if (IsHalted)
            return false;

        // Fetch: Get instruction from memory[CodePointer]
        int instruction = _memory[_memory.CodePointer];

        // Check if instruction is printable (33-126), if not, halt
        if (instruction < 33 || instruction > 126)
        {
            IsHalted = true;
            return false;
        }

        // Decode: Apply Malbolge instruction translation
        int decodedOp = (instruction + _memory.CodePointer) % 94;

        // Execute: Map to operation and execute
        ExecuteOperation((Operation)decodedOp);

        // Mutate: Update memory[CodePointer] using encryption
        MutateInstruction();

        // Increment pointers (with wraparound)
        _memory.CodePointer = (_memory.CodePointer + 1) % MalbolgeMemory.MemorySize;
        _memory.DataPointer = (_memory.DataPointer + 1) % MalbolgeMemory.MemorySize;

        return !IsHalted;
    }

    /// <summary>
    /// Executes the decoded operation.
    /// </summary>
    /// <param name="operation">The operation to execute.</param>
    private void ExecuteOperation(Operation operation)
    {
        switch (operation)
        {
            case Operation.Jmp: // Set C = mem[D]
                _memory.CodePointer = _memory[_memory.DataPointer];
                break;

            case Operation.Out: // Print chr(A % 256)
                char outputChar = (char)(Accumulator % 256);
                Output += outputChar;
                break;

            case Operation.In: // Read input (not implemented yet)
                // For now, set A to 0 (EOF)
                Accumulator = 0;
                break;

            case Operation.Rotr: // A = mem[D] = rotate(mem[D])
                int rotatedValue = Rotate(_memory[_memory.DataPointer]);
                _memory[_memory.DataPointer] = rotatedValue;
                Accumulator = rotatedValue;
                break;

            case Operation.Mov: // D = mem[D]
                _memory.DataPointer = _memory[_memory.DataPointer];
                break;

            case Operation.Crz: // A = mem[D] = crazy(A, mem[D])
                int crazyValue = MalbolgeMath.Crazy(Accumulator, _memory[_memory.DataPointer]);
                _memory[_memory.DataPointer] = crazyValue;
                Accumulator = crazyValue;
                break;

            case Operation.Nop: // Do nothing
                break;

            case Operation.End: // Halt execution
                IsHalted = true;
                break;

            default:
                // Invalid operation - this shouldn't happen with proper validation
                throw new InvalidOperationException($"Invalid Malbolge operation: {operation}");
        }
    }

    /// <summary>
    /// Mutates the current instruction in memory using the Malbolge encryption table.
    /// </summary>
    private void MutateInstruction()
    {
        int currentValue = _memory[_memory.CodePointer];
        if (currentValue >= 33 && currentValue <= 126)
        {
            int encryptedValue = EncryptTable[currentValue - 33];
            _memory[_memory.CodePointer] = encryptedValue;
        }
    }

    /// <summary>
    /// Performs the Malbolge rotate operation (ternary right rotate).
    /// </summary>
    /// <param name="value">The value to rotate.</param>
    /// <returns>The rotated value.</returns>
    private static int Rotate(int value)
    {
        const int Pow9 = 19683; // 3^9
        return Pow9 * (value % 3) + value / 3;
    }
}