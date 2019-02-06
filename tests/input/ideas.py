Here’s a list of the features we would like your engine to support.
You can only get100% of the grade by implementing all of them.
•"AND" conditions. For example,"If A and B and [...]  then X"
•"OR" conditions. For example,"If C or D then Z"
•"XOR" conditions.  For example,"If A xor E then V".  Remember that thismeans "exclusive OR". It is only true if one and only one of the operands is true.
•Negation. For example,"If A and not B then Y"
•Multiple rules can have the same fact as a conclusion
•"AND" in conclusions. For example,"If A then B and C"
•Parentheses in expressions.  Interpreted in much the same way as an arithmeticexpressio


Bonuses
•Interactive fact validation : The system allows the user to change facts interactivelyto check the same query against
a different input without changing the source file,or to clarify an undeterminable fact, for example from an OR
conclusion withoutfurther information.
•Reasoning visualisation : For a given query, provide some feedback to explain theanswer to the user,
for example "We know that A is true. Since we know A | B =>C, then C is true", or any other type of visualization you
like. Even better, outputeverything in formal logic notation, and go show Thor : If he likes it, you’ll win abeer.
•"OR" and "XOR" in conclusions. For example,"If A then B or C"•Biconditional rules.
For example,"A and B if-and-only-if D". In case it’s un-clear, this means not only"If A and B then D"
but also"If D then A and B"
•Whatever other interesting bonus you want, as long as it’s coherent with the restof the project.


Rules of precedence
(and)which are fairly obvious. Example :A + (B | C) => D
•!which means NOT. Example :!B
•+which means AND. Example :A + B
•|which means OR. Example :A | B
•ˆwhich means XOR. Example :A ˆ B
•=>which means "implies". Example :A + B => C
•<=>which means "if and only if". Example :A + B <=> C

