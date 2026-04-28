/// <summary>
/// MalbolgeMath: Static utilities for Malbolge operations.
/// Provides ternary logic operations required by the Malbolge language.
/// </summary>
public static class MalbolgeMath
{
    /// <summary>
    /// Lookup table for the Malbolge 'crz' (Crazy) ternary operation.
    /// Indexed as [trit1, trit2] where each trit is 0, 1, or 2.
    /// </summary>
    private static readonly int[,] CrazyLookup = new int[3, 3]
    {
        // trit2:  0  1  2
        { 1, 0, 0 },  // trit1=0
        { 1, 0, 2 },  // trit1=1
        { 2, 2, 1 }   // trit1=2
    };

    /// <summary>
    /// Performs the Malbolge 'crz' (Crazy) operation on two integers.
    /// Decomposes each integer into base-3 (ternary) digits, applies the
    /// ternary lookup table to corresponding digit pairs, and recomposes
    /// the result.
    /// </summary>
    /// <param name="a">First operand.</param>
    /// <param name="b">Second operand.</param>
    /// <returns>The result of the Crazy operation.</returns>
    public static int Crazy(int a, int b)
    {
        int result = 0;
        int power = 1; // 3^digit_position

        // Process each ternary digit position (at least once for 0,0 case)
        do
        {
            // Extract the current ternary digit (0, 1, or 2)
            int tritA = a % 3;
            int tritB = b % 3;

            // Apply the Crazy lookup table
            int tritResult = CrazyLookup[tritA, tritB];

            // Accumulate the result
            result += tritResult * power;

            // Move to the next ternary digit
            a /= 3;
            b /= 3;
            power *= 3;
        }
        while (a > 0 || b > 0);

        return result;
    }
}
