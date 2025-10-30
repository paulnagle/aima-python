"""
A2_COMP9016_Nagle_JohnPaul_R00065426.py

Name:         (John) Paul Nagle
Student ID:   R00065426
Class:        Knowledge Representation
Assignment:   2

"""
import sys
import os


# Get the parent directory of the current directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now you can import a module from the parent directory

from logic import Expr, FolKB, fol_fc_ask, fol_bc_ask
from utils import expr

def print_clauses(kb, message="Clauses in the Knowledge Base:", bool_print=True):
    if bool_print:
        print("\n" + message)
        for clause in kb.clauses:
            print(clause)
    print("Total Clauses: ", len(kb.clauses))

# 1.1.1 Define the Knowledge Base
print("1.1.1 Define the Knowledge Base" )
# Create the First Order Logic Knowledge Base
print("- Creating KB ✔️")
assignment2_kb = FolKB()

# Define the constants
print("- Defining constants ✔️")
Student = Expr('S')         # S is a Student
Lecturer = Expr('L')        # L is a Lecturer
Module = Expr('M')          # M is a Module

# Define the predicates
print("- Defining predicates ✔️")
Takes = Expr('T')               # T(s, m) s is currently taking module m
Passed = Expr('P')              # P(s, m) s has already passed module m
Teaches = Expr('Teaches')       # Teaches(l, m) l teaches module m
Prereq = Expr('Prereq')        # Prereq(p, m) p is a prerequisite for m
Eligible = Expr('Eligible')     # Eligible(s, m) s has satisfied all prerequisites for m
CanEnroll = Expr('CanEnroll')   # CanEnroll(s, m) s is eligible and has not already passed m
TaughtBy = Expr('TaughtBy')     # TaughtBy(s, l) s is taught by lecturer l
Classmate = Expr('Classmate')   # Classmate(s, t) share a module and s =\= t
NotPassed = Expr('NotPassed')   # NotPassed(s, m) s has not passed m
IndirectPrereq = Expr('IndirectPrereq')  # IndirectPrereq(x, z) x is an indirect prerequisite for z
NotEqual = Expr('NotEqual')

# Define the premises
print("- Defining premises ✔️")
# 1. Teaching implies “taught by” when a student is enrolled
assignment2_kb.tell(expr('Takes(s, m) & Teaches(l, m) ==> TaughtBy(s, l)'))

# 2. Two students are classmates if they take the same module and are not the same person:
assignment2_kb.tell(expr('Student(x) & Student(y) & Takes(x, m) & Takes(y, m) & NotEqual(x, y) ==> Classmate(x, y)'))

# 3. A student is eligible for a module if they have passed all of its prerequisites:
assignment2_kb.tell(expr('Prereq(p, m) & Passed(s, p) ==> Eligible(s, m)'))

# 4. A student can enroll in a module if they are eligible and have not already passed it
assignment2_kb.tell(expr('NotPassed(s, m) & Eligible(s, m) ==> CanEnroll(s, m)'))

# 5. Prerequisites are transitive
assignment2_kb.tell(expr('Prereq(x, y) & Prereq(y, z) ==> IndirectPrereq(x, z)'))

# 1.1.2 Provide the facts
print("1.1.2 Provide the facts")
# Modules
print("- Modules ✔️")
assignment2_kb.tell(expr('Module(COMP9016)'))
assignment2_kb.tell(expr('Module(COMP9062)'))
assignment2_kb.tell(expr('Module(COMP9061)'))
assignment2_kb.tell(expr('Module(COMP9058)'))
# Students
print("- Students ✔️")
assignment2_kb.tell(expr('Student(Alice)'))
assignment2_kb.tell(expr('Student(Bob)'))
assignment2_kb.tell(expr('Student(Eve)'))
assignment2_kb.tell(expr('NotEqual(Alice, Bob)'))
assignment2_kb.tell(expr('NotEqual(Alice, Eve)'))
assignment2_kb.tell(expr('NotEqual(Bob, Eve)'))
# Lecturers
print("- Lecturers ✔️")
assignment2_kb.tell(expr('Lecturer(DrDan)'))
assignment2_kb.tell(expr('Lecturer(DrSophie)'))
assignment2_kb.tell(expr('Lecturer(DrLisa)'))
# Prerequisites
print("- Prerequisites ✔️")
assignment2_kb.tell(expr('Prereq(COMP9016, COMP9062)'))
assignment2_kb.tell(expr('Prereq(COMP9062, COMP9061)'))
# Teaching
print("- Teaches ✔️")
assignment2_kb.tell(expr('Teaches(DrDan, COMP9016)'))
assignment2_kb.tell(expr('Teaches(DrSophie, COMP9062)'))
assignment2_kb.tell(expr('Teaches(DrLisa, COMP9061)'))
# Student Record
print("- Student records ✔️")
assignment2_kb.tell(expr('Passed(Alice, COMP9016)'))
assignment2_kb.tell(expr('Passed(Alice, COMP9058)'))
assignment2_kb.tell(expr('Passed(Bob, COMP9016)'))
assignment2_kb.tell(expr('Passed(Bob, COMP9062)'))

assignment2_kb.tell(expr('NotPassed(Alice, COMP9061)'))
assignment2_kb.tell(expr('NotPassed(Alice, COMP9062)'))
assignment2_kb.tell(expr('NotPassed(Eve, COMP9016)'))
assignment2_kb.tell(expr('NotPassed(Eve, COMP9058)'))
assignment2_kb.tell(expr('NotPassed(Eve, COMP9062)'))
assignment2_kb.tell(expr('NotPassed(Eve, COMP9058)'))
assignment2_kb.tell(expr('NotPassed(Bob, COMP9058)'))
assignment2_kb.tell(expr('NotPassed(Bob, COMP9061)'))

# Current Enrolements
print("- Enrolements ✔️")
assignment2_kb.tell(expr('Takes(Alice, COMP9062)'))
assignment2_kb.tell(expr('Takes(Bob, COMP9061)'))
assignment2_kb.tell(expr('Takes(Eve, COMP9016)'))


# 1.1.3 INFERENCE AND ANALYSIS
print("1.1.3 INFERENCE AND ANALYSIS => 1 Forward Chaining")

def run_forward_chaining(kb):
    print("\n=== Forward Chaining Results ===")

    students = ["Alice", "Bob", "Eve"]
    lecturers = ["DrDan", "DrSophie", "DrLisa"]
    modules = ["COMP9016", "COMP9058", "COMP9061", "COMP9062", ]
    
    logical_inferences = []
    
    # Check TaughtBy logical inferences
    print("\nTaughtBy logical inferences:")
    for student in students:
        for lecturer in lecturers:
            query = expr(f'TaughtBy({student}, {lecturer})')
            results = list(fol_fc_ask(kb, query))
            if results:
                print(f"- {query}")
                logical_inferences.append(query)
    
    # Check Classmate logical inferences
    print("\nClassmate logical inferences:")
    for s1 in students:
        for s2 in students:
            query = expr(f'Classmate({s1}, {s2})')
            results = list(fol_fc_ask(kb, query))
            if results:
                print(f"- {query}")
                logical_inferences.append(query)
    
    # Check Prereq logical inferences
    print("\nPrereq logical inferences:")
    for m1 in modules:
        for m2 in modules:
            if m1 != m2:
                query = expr(f'Prereq({m1}, {m2})')
                results = list(fol_fc_ask(kb, query))
                if results:
                    print(f"- {query}")
                    logical_inferences.append(query)

    # Check IndirectPrereq logical inferences
    print("\nIndirectPrereq logical inferences:")
    for m1 in modules:
        for m2 in modules:
            if m1 != m2:
                query = expr(f'IndirectPrereq({m1}, {m2})')
                results = list(fol_fc_ask(kb, query))
                if results:
                    print(f"- {query}")
                    logical_inferences.append(query)

    # Check Eligible logical inferences
    print("\nEligible logical inferences:")
    for student in students:
        for module in modules:
            query = expr(f'Eligible({student}, {module})')
            results = list(fol_fc_ask(kb, query))
            if results:
                print(f"- {query}")
                logical_inferences.append(query)
    
    # Check CanEnroll logical inferences
    print("\nCanEnroll logical inferences:")
    for student in students:
        for module in modules:
            query = expr(f'CanEnroll({student}, {module})')
            results = list(fol_fc_ask(kb, query))
            if results:
                print(f"- {query}")
                logical_inferences.append(query)
    
    print(f"\nTotal logical inferences: {len(logical_inferences)}")
    return logical_inferences



print_clauses(assignment2_kb, "BEFORE INFERENCE:")
# Run the forward chaining
logical_inferences = run_forward_chaining(assignment2_kb)

print_clauses(assignment2_kb, "AFTER INFERENCE:")

print("1.1.3 INFERENCE AND ANALYSIS => 2 Backward Chaining")
# Backward Chaining (BC): Demonstrate reasoning for the following queries:
# • Eligible(Alice, COMP9061)
# • Eligible(Bob, COMP9061)
# • TaughtBy(Eve, l)
# • Classmate(Alice, Eve) (before and after adding Takes(Alice, COMP9016))

query = assignment2_kb.ask(expr('Eligible(Alice, COMP9061)'))
print(f"Is Alice Eligible for COMP9061? {query}")

query = assignment2_kb.ask(expr('Eligible(Bob, COMP9061)'))
print(f"Is Bob Eligible for COMP9061? {query}")

query = assignment2_kb.ask(expr('TaughtBy(Eve, l)'))
print(f"Is Eve TaughtBy l? {query}")

query = assignment2_kb.ask(expr('Classmate(Alice, Eve)'))
print(f"Is Alice a classmate of Eve (before adding Takes(Alice, COMP9016))? {query}")

assignment2_kb.tell(expr('Classmate(Alice, Eve)'))

query = assignment2_kb.ask(expr('Classmate(Alice, Eve)'))
print(f"Is Alice a classmate of Eve (After adding Takes(Alice, COMP9016))? {query}")
