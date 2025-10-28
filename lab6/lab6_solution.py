# Part 1: Using `Expr` and `tt_entails` from `logic.py`

import os
import sys
sys.path.append('./aima-python')  # Ensure correct path to aima-python


"""
In logic, entailment refers to a relationship between statements where one statement (the conclusion) necessarily follows from one or more others (the premises). If the premises are true, then the conclusion must also be true. Symbolically, if A⊨B, it means B is a logical consequence of A.

In logical notation, the symbol ⊨ (called the turnstile symbol) is used to denote entailment.
    The premises are written to the left of the turnstile.
    The conclusion is written to the right of the turnstile.
For example:
A,B⊨C

This means that the statements A and B (the premises) entail C (the conclusion). In other words, if A and B are true, then C must also be true.

Another way to interpret it is:
    The truth of C is guaranteed by the truth of A and B.
The symbol ⊨ captures this logical consequence relationship, where the conclusion follows necessarily from the premises.
"""



"""
The tt_entails function in the AIMA logic.py module determines if a set of premises logically entails a conclusion by using a truth table approach. It systematically checks all possible truth value assignments for the symbols in the premises and conclusion to verify whether the conclusion is true in every model where the premises are true.

In other words, tt_entails evaluates if the conclusion follows necessarily from the premises, ensuring there are no counterexamples where the premises are true and the conclusion is false. This function is a complete way to determine entailment in propositional logic using truth table enumeration.

The Expr class in the AIMA logic.py module represents logical expressions in symbolic form. It allows users to construct and manipulate logical sentences involving propositions and logical operators like AND (&), OR (|), NOT (~), IMPLIES (>>), and BICONDITIONAL (<<).

Expr is used to build atomic or compound logical statements that can be evaluated, parsed, and used for logical inference. The class provides operator overloading to make it easy to create complex logical formulas in a natural and readable manner.

"""

# Get the parent directory of the current directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
from logic import tt_entails, Expr

"""
Example provided
"""

# Define symbols for the logical expressions
H = Expr('H')    # It is hot
AC = Expr('AC')  # The air conditioner is on

# Define the premises using Expr
premise1 = Expr('==>', H, AC)  # Premise 1: If it is hot, then the air conditioner is on
premise2 = H                   # Premise 2: It is hot

# Combine the premises using logical AND
premises = premise1 & premise2

# Define the conclusion
conclusion = AC  # Conclusion: The air conditioner is on

# Check if the premises entail the conclusion
result = tt_entails(premises, conclusion)

# Output the result
print(f"Do the premises entail the conclusion? {result}")

""" Example end """

# constant Exprs used as part of the logical sentences:
A, B, C, D, E, F, G = map(Expr, 'ABCDEFG')


#Part A: Using `tt_entails` to Check Entailment
# Example 1: A AND B entails A
expr1 = A & B
conclusion1 = A
print(f"Example 1: {expr1} entails {conclusion1}")
print("Expected: True")
print("Actual:", tt_entails(expr1, conclusion1))

# Example 2: A OR B entails B OR A
expr2 = A | B
conclusion2 = B | A
print(f"\nExample 2: {expr2} entails {conclusion2}")
print("Expected: True")
print("Actual:", tt_entails(expr2, conclusion2))

# Example 3: A IMPLIES B entails NOT A OR B
# We need to generate NOT A using ~A as it was giving me problems with the parser and wasted a lot of time.
NOT_A = Expr('~', A)
expr3 = Expr('==>', A, B)
conclusion3 = Expr('|', NOT_A, B)
print(f"\nExample 3: {expr3} entails {conclusion3}")
print("Expected: True")
print("Actual:", tt_entails(expr3, conclusion3))

# Example 4: A AND (B OR C) entails (A AND B) OR (A AND C)
expr4 = A & (B | C)
conclusion4 = (A & B) | (A & C)
print(f"\nExample 4: {expr4} entails {conclusion4}")
print("Expected: True")
print("Actual:", tt_entails(expr4, conclusion4))

# Example 5: A AND B entails B AND A
expr5 = A & B
conclusion5 = B & A
print(f"\nExample 5: {expr5} entails {conclusion5}")
print("Expected: True")
print("Actual:", tt_entails(expr5, conclusion5))


# Part 2: Understanding Entailment

"""
Exercise: Understanding Logical Entailment with tt_entails (Using Expr Constructor Input)

Consider the following logical statements:
    Premise 1: If it rains, then the ground is wet. (Symbolically: R => W)
    Premise 2: It is raining. (Symbolically: R)
    Conclusion: The ground is wet. (Symbolically: W)

"""


# Define the symbols
R = Expr('R')  # It is raining
W = Expr('W')  # The ground is wet

# Define the premises using Expr constructor (verbose form)
premise1 = Expr('==>', R, W)  # Premise 1: If it rains, then the ground is wet
premise2 = R                  # Premise 2: It is raining

# Combine the premises
premises = Expr('&', premise1, premise2)  # Both Premise 1 and Premise 2 must hold

# Define the conclusion
conclusion = W  # The conclusion is: The ground is wet

# Check if premises entail the conclusion
result = tt_entails(premises, conclusion)

print(f"Do the premises entail the conclusion? {result}")


"""
Exercise 2: Logical Entailment with Multiple Conditions

Consider the following logical statements:

    Premise 1: If John studies, he will pass the exam. (Symbolically: S => P)
    Premise 2: If John passes the exam, he will get a certificate. (Symbolically: P => C)
    Premise 3: John studies. (Symbolically: S)
    Conclusion: John will get a certificate. (Symbolically: C)

"""

# Define the symbols
Study = Expr('Study')  # You study
Pass = Expr('Pass')    # You pass the exam
MSc = Expr('MSc')      # You get an MSc in AI

# Define the premises using Expr constructor (verbose form)
premise1 = Expr('==>', Study, Pass)  # Premise 1: If you study, you will pass the exam
premise2 = Expr('==>', Pass, MSc)    # Premise 2: If you pass the exam, you will get an MSc in AI
premise3 = Study                     # Premise 3: You study

# Combine the premises
premises = Expr('&', premise1, Expr('&', premise2, premise3))  # Combine Premise 1, 2, and 3

# Define the conclusion
conclusion = MSc  # The conclusion is: You get an MSc in AI

# Check if the premises entail the conclusion
result = tt_entails(premises, conclusion)

print(f"Do the premises entail the conclusion? {result}")

"""
Exercise 3: 
"""

from logic import PropKB


# Initialize the knowledge base
wumpus_kb = PropKB()

# Define the symbols for pits and breezes in the grid
P11, P12, P13 = Expr('P11'), Expr('P12'), Expr('P13')
P21, P22, P23 = Expr('P21'), Expr('P22'), Expr('P23')
P31, P32, P33 = Expr('P31'), Expr('P32'), Expr('P33')

B11, B12, B13 = Expr('B11'), Expr('B12'), Expr('B13')
B21, B22, B23 = Expr('B21'), Expr('B22'), Expr('B23')
B31, B32, B33 = Expr('B31'), Expr('B32'), Expr('B33')

# Add knowledge about pits and breezes to the KB

# No pit in [1,1]
wumpus_kb.tell(~P11)

# There is a pit in [2,2]
wumpus_kb.tell(P22)

# Breezes in adjacent tiles: a tile is breezy if there is a pit in an adjacent tile
# B11 ⇔ (P12 ∨ P21)
wumpus_kb.tell(B11 | '<=>' | (P12 | P21))

# B12 ⇔ (P11 ∨ P22 ∨ P13)
wumpus_kb.tell(B12 | '<=>' | (P11 | P22 | P13))

# B13 ⇔ (P12 ∨ P23)
wumpus_kb.tell(B13 | '<=>' | (P12 | P23))

# B21 ⇔ (P11 ∨ P22 ∨ P31)
wumpus_kb.tell(B21 | '<=>' | (P11 | P22 | P31))

# B22 ⇔ (P12 ∨ P21 ∨ P23 ∨ P32)
wumpus_kb.tell(B22 | '<=>' | (P12 | P21 | P23 | P32))

# B23 ⇔ (P13 ∨ P22 ∨ P33)
wumpus_kb.tell(B23 | '<=>' | (P13 | P22 | P33))

# B31 ⇔ (P21 ∨ P32)
wumpus_kb.tell(B31 | '<=>' | (P21 | P32))

# B32 ⇔ (P22 ∨ P31 ∨ P33)
wumpus_kb.tell(B32 | '<=>' | (P22 | P31 | P33))

# B33 ⇔ (P23 ∨ P32)
wumpus_kb.tell(B33 | '<=>' | (P23 | P32))

# Add percepts: Breeze felt in [2, 1], no breeze in [1, 1]
wumpus_kb.tell(~B11)  # No breeze in [1, 1]
wumpus_kb.tell(B21)   # Breeze in [2, 1]


# Check the KB to see the clauses it contains
print("Clauses in the knowledge base:")
for clause in wumpus_kb.clauses:
    print(clause)

# Print out an ASCII representation of the world
world = [[' ' for _ in range(3)] for _ in range(3)]

# Update each square with the correct symbol: 'P' for pit, 'B' for breeze, '.' for empty
world[0][0] = 'P' if wumpus_kb.ask_if_true(P11) else 'B' if wumpus_kb.ask_if_true(B11) else '.'
world[0][1] = 'P' if wumpus_kb.ask_if_true(P12) else 'B' if wumpus_kb.ask_if_true(B12) else '.'
world[0][2] = 'P' if wumpus_kb.ask_if_true(P13) else 'B' if wumpus_kb.ask_if_true(B13) else '.'
world[1][0] = 'P' if wumpus_kb.ask_if_true(P21) else 'B' if wumpus_kb.ask_if_true(B21) else '.'
world[1][1] = 'P' if wumpus_kb.ask_if_true(P22) else 'B' if wumpus_kb.ask_if_true(B22) else '.'
world[1][2] = 'P' if wumpus_kb.ask_if_true(P23) else 'B' if wumpus_kb.ask_if_true(B23) else '.'
world[2][0] = 'P' if wumpus_kb.ask_if_true(P31) else 'B' if wumpus_kb.ask_if_true(B31) else '.'
world[2][1] = 'P' if wumpus_kb.ask_if_true(P32) else 'B' if wumpus_kb.ask_if_true(B32) else '.'
world[2][2] = 'P' if wumpus_kb.ask_if_true(P33) else 'B' if wumpus_kb.ask_if_true(B33) else '.'

print("\nASCII representation of the world:")
for row in world:
    print(' '.join(row))