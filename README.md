# Python calculator example

This calculator uses the [Shunting Yard algorithm](https://en.wikipedia.org/wiki/Shunting_yard_algorithm) to create a stack of tokens in [postfix notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation) that can easily be consumed into an evaluated result.

I initially started this blind, without any research. My first approach was to add the token to the stack immediately after tokenisation and consume the stack into an evaluated result later. Of course, only using one stack rather than the two stacks used in Shunting Yard would make it nearly impossible to apply a [per operator precedence](https://en.wikipedia.org/wiki/Order_of_operations).

There are a few issues with this calculator I didn't have time to fix:

- The float operator doesn't check if the left operand is being used by another float operator: `1.2.3.4` evaluates to `1.234`
- The unary operator tokeniser doesn't handle the case of these two expressions, resulting in an error: `1.+1` and `1.-1`
- Division by zero error is not caught. There's many ways this can be implemented, i.e. try-catch in the division operation, a simple check to see if the right operand is 0 at runtime, or just simply encourage the API user to wrap the function call in a try-catch.
- At 10 decimal places, the evaluated result exhibits weird behaviour: `1.6666666666` evaluates to `1.237169937`.
