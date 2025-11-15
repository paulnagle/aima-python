"""
A2_COMP9016_Nagle_JohnPaul_R00065426.py

Name:         (John) Paul Nagle
Student ID:   R00065426
Class:        Knowledge Representation
Assignment:   2

"""
from collections import Counter
import random
import sys
import os
import numpy as np


# Get the parent directory of the current directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now you can import a module from the parent directory

from logic import Expr, FolKB, fol_fc_ask, fol_bc_ask
from utils import expr
from probability import BayesNet, enumeration_ask, elimination_ask, rejection_sampling, likelihood_weighting, JointProbDist, ProbDist

# Copied from module labs
def print_clauses(kb, message="Clauses in the Knowledge Base:", bool_print=True):
    if bool_print:
        print("\n" + message)
        for clause in kb.clauses:
            print(clause)
    print("Total Clauses: ", len(kb.clauses))

def Q1_1():
    print("*" * 80)
    print("* Q 1.1")
    print("*" * 80)
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
    for student_1 in ["Alice", "Bob", "Eve"]:
        for student_2 in ["Alice", "Bob", "Eve"]:
            if student_1 != student_2:
                assignment2_kb.tell(expr(f'NotEqual({student_1}, {student_2})'))

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

    def infer_all(kb):
        print("\n=== Forward Chaining Results ===")

        students = ["Alice", "Bob", "Eve"]
        lecturers = ["DrDan", "DrSophie", "DrLisa"]
        modules = ["COMP9016", "COMP9058", "COMP9061", "COMP9062"]

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
    logical_inferences = infer_all(assignment2_kb)

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

    query = assignment2_kb.ask(expr('TaughtBy(Eve, DrDan)'))
    print(f"Is Eve TaughtBy l? {query}")

    query = assignment2_kb.ask(expr('Classmate(Alice, Eve)'))
    print(f"Is Alice a classmate of Eve (before adding Takes(Alice, COMP9016))? {query}")

    assignment2_kb.tell(expr('Classmate(Alice, Eve)'))

    query = assignment2_kb.ask(expr('Classmate(Alice, Eve)'))
    print(f"Is Alice a classmate of Eve (After adding Takes(Alice, COMP9016))? {query}")


def Q1_2():
    print("*" * 80)
    print("* Q 1.2")
    print("*" * 80)

    # Create the Bayesnet based on the values from the Conditional Probability Tables in the doc
    # We only need to add the True values, the bayes net will add the normalisations
    print("- Creating Bayesnet ✔️")
    ai_market = BayesNet([
        ('HypeLevel', '', 0.6),
        ('ComputeCosts', '', 0.7),
        ('RegulatoryPressure', '', 0.8),
        ('VCInvestment', 'HypeLevel', {True: 0.8, False: 0.3 }),
        ('EnterpriseAdoption', 'VCInvestment ComputeCosts RegulatoryPressure', {
            (True, False, False): 0.9,
            (True, True, False): 0.8,
            (False, False, False): 0.7,
            (False, True, False): 0.2,
            (True, False, True): 0.6,
            (True, True, True): 0.5,
            (False, False, True): 0.4,
            (False, True, True): 0.3
        }),
        ('LabourMarketImpact', 'HypeLevel RegulatoryPressure', {
            (True, True): 0.6,
            (True, False): 0.9,
            (False, True): 0.2,
            (False, False): 0.5
        })
    ])

    print("- Querying the Network for probability of EnterpriseAdoption ✔️")
    result = enumeration_ask('EnterpriseAdoption', {}, ai_market)
    print(f"  P(EnterpriseAdoption=High) = {result[True]:.4f}")
    print(f"  P(EnterpriseAdoption=Low) = {result[False]:.4f}")
    
    print("- Querying the Network for probability of EnterpriseAdoption given high HypeLevel ✔️")
    result = enumeration_ask('EnterpriseAdoption', {'HypeLevel': True}, ai_market)
    print(f"  P(EnterpriseAdoption=High | HypeLevel=High) = {result[True]:.4f}")
    print(f"  P(EnterpriseAdoption=Low | HypeLevel=High) = {result[False]:.4f}")

    print("- Querying the Network for probability of EnterpriseAdoption given low ComputeCosts ✔️")
    result = enumeration_ask('EnterpriseAdoption', {'ComputeCosts': False}, ai_market)
    print(f"  P(EnterpriseAdoption=High | ComputeCosts=Low) = {result[True]:.4f}")
    print(f"  P(EnterpriseAdoption=Low | ComputeCosts=Low) = {result[False]:.4f}")

    print("- Conditional Independence ✔️")
    print("  - When VCInvestment is observed, HypeLevel becomes conditionally independent of EnterpriseAdoption")
    result_with_hype = enumeration_ask('EnterpriseAdoption',{'HypeLevel': True, 'VCInvestment': True}, ai_market)
    result_with_low_hype = enumeration_ask('EnterpriseAdoption',{'HypeLevel': False, 'VCInvestment': True}, ai_market)
    result_with_no_hype = enumeration_ask('EnterpriseAdoption',{'VCInvestment': True},  ai_market)
    print(f"    P(EA=High | HypeLevel=High, VCI=High) = {result_with_hype[True]:.4f}")
    print(f"    P(EA=High | HypeLevel=Low, VCI=High) = {result_with_low_hype[True]:.4f}")
    print(f"    P(EA=High | VCI=High) = {result_with_no_hype[True]:.4f}")
    print(f"    --> Results are equal, showing conditional independence")


def Q1_3():
    print("*" * 80)
    print("* Q 1.3")
    print("*" * 80)
    # 1.3.1
    # Select two appropriate datasets with a manageable number of features and classes from the
    # UCI Machine Learning Repository: https://archive.ics.uci.edu/ml/index.php.
    # Extract a relevant subset from each dataset and perform the following analyses:
    # • Calculate the Prior probabilities for the classes in each dataset.
    # • Estimate the probability of the evidence within the dataset.
    # • Determine the likelihood of the evidence (the numerator of Bayes’ formula).

    print("-" * 80)
    print("- Abalone DataSet")
    print("-" * 80)
    # Read abalone.csv file
    # Column names based on abalone.names file:
    # Sex, Length, Diameter, Height, Whole weight, Shucked weight, Viscera weight, Shell weight, Rings
    abalone_column_names = ['Sex', 'Length', 'Diameter', 'Height', 'Whole_weight',
                            'Shucked_weight', 'Viscera_weight', 'Shell_weight', 'Rings']
    abalone_data = []
    
    # Open and read the CSV file
    with open('abalone.csv', 'r') as file:
        for line in file:
            values = line.strip().split(',')                            # Strip whitespace and split by comma
            row_dict = {}                                               # Create a dictionary for this row
            row_dict[abalone_column_names[0]] = values[0]               # The only non-numneric column is [0] Sex
            # Convert numeric values to float
            for i in range(1, len(abalone_column_names)):
                if i < len(values):
                    row_dict[abalone_column_names[i]] = float(values[i])
            abalone_data.append(row_dict)

    # Extract a relevant subset
    SUBSET_SIZE = 400
    random.seed(65426)
    abalone_subset = random.sample(abalone_data, min(SUBSET_SIZE, len(abalone_data)))


    # Calculate Prior probabilities using the formula:
    #         Number of instances of C
    #  P(C) = ------------------------
    #         Tot. no. of instances in the dataset

    # - Sex
    prior_prob_sex_male =  sum(1 for row in abalone_subset if row['Sex'] == 'M')/SUBSET_SIZE
    prior_prob_sex_female = sum(1 for row in abalone_subset if row['Sex'] == 'F')/SUBSET_SIZE
    prior_prob_sex_indetermined = sum(1 for row in abalone_subset if row['Sex'] == 'I')/SUBSET_SIZE
    print("Prior probabilities for Sex category:")
    print(f"  P(M) = {prior_prob_sex_male:.4f}")  
    print(f"  P(F) = {prior_prob_sex_female:.4f}")  
    print(f"  P(I) = {prior_prob_sex_indetermined:.4f}")
    print("\n")

    # For the categories with continuous variables, I chose the following bins
    # Length (Small < 0.3, Medium < 0.5, Large < 0.7, Very Large)
    # Diameter (Small < 0.25, Medium < 0.4, Large < 0.55, Very Large)
    # Height (Small < 0.08, Medium < 0.12, Large < 0.16, Very Large)
    # Whole_weight (Light < 0.4, Medium < 0.8, Heavy < 1.2, Very Heavy)
    # Shucked_weight Light < 0.2, Medium < 0.4, Heavy < 0.6, Very Heavy)
    # Viscera_weight (Light < 0.1, Medium < 0.2, Heavy < 0.3, Very Heavy)
    # Shell_weight (Light < 0.15, Medium < 0.25, Heavy < 0.35, Very Heavy)
    # Rings - 4 age categories (Young < 8, Adult < 11, Mature < 15, Old)

    # Helper function to calculate prior probabilities for continuous variables
    def calculate_continuous_priors(data, column_name, bin_function, category_suffix='_Category'):

        # Add category column
        category_col = column_name + category_suffix
        for row in data:
            row[category_col] = bin_function(row[column_name])
        
        # Count occurrences
        counts = {}
        for row in data:
            category = row[category_col]
            counts[category] = counts.get(category, 0) + 1
        
        # Calculate probabilities
        priors = {category: count / SUBSET_SIZE for category, count in counts.items()}
        
        return priors

    # - Length
    # For Length, we will use the following bins:
    def length_bins(length):
        if length < 0.3:
            return 'Small'
        elif length < 0.5:
            return 'Medium'
        elif length < 0.7:
            return 'Large'
        else:
            return 'Very Large'

    length_priors = calculate_continuous_priors(abalone_subset, 'Length', length_bins)
    print("\nPrior probabilities for Length categories:")
    for category, prob in length_priors.items():
        print(f"  P({category}) = {prob:.4f}")

    # - Diameter
    def diameter_bins(diameter):
        if diameter < 0.25:
            return 'Small'
        elif diameter < 0.4:
            return 'Medium'
        elif diameter < 0.55:
            return 'Large'
        else:
            return 'Very Large'
    
    diameter_priors = calculate_continuous_priors(abalone_subset, 'Diameter', diameter_bins)
    print("\nPrior probabilities for Diameter categories:")
    for category, prob in diameter_priors.items():
        print(f"  P({category}) = {prob:.4f}")

    # - Height
    def height_bins(height):
        if height < 0.08:
            return 'Small'
        elif height < 0.12:
            return 'Medium'
        elif height < 0.16:
            return 'Large'
        else:
            return 'Very Large'
    
    height_priors = calculate_continuous_priors(abalone_subset, 'Height', height_bins)
    print("\nPrior probabilities for Height categories:")
    for category, prob in height_priors.items():
        print(f"  P({category}) = {prob:.4f}")

    # - Whole_weight
    def whole_weight_bins(weight):
        if weight < 0.4:
            return 'Light'
        elif weight < 0.8:
            return 'Medium'
        elif weight < 1.2:
            return 'Heavy'
        else:
            return 'Very Heavy'
    
    whole_weight_priors = calculate_continuous_priors(abalone_subset, 'Whole_weight', whole_weight_bins)
    print("\nPrior probabilities for Whole_weight categories:")
    for category, prob in whole_weight_priors.items():
        print(f"  P({category}) = {prob:.4f}")

    # - Shucked_weight
    def shucked_weight_bins(weight):
        if weight < 0.2:
            return 'Light'
        elif weight < 0.4:
            return 'Medium'
        elif weight < 0.6:
            return 'Heavy'
        else:
            return 'Very Heavy'
    
    shucked_weight_priors = calculate_continuous_priors(abalone_subset, 'Shucked_weight', shucked_weight_bins)
    print("\nPrior probabilities for Shucked_weight categories:")
    for category, prob in shucked_weight_priors.items():
        print(f"  P({category}) = {prob:.4f}")

    # - Viscera_weight
    def viscera_weight_bins(weight):
        if weight < 0.1:
            return 'Light'
        elif weight < 0.2:
            return 'Medium'
        elif weight < 0.3:
            return 'Heavy'
        else:
            return 'Very Heavy'
    
    viscera_weight_priors = calculate_continuous_priors(abalone_subset, 'Viscera_weight', viscera_weight_bins)
    print("\nPrior probabilities for Viscera_weight categories:")
    for category, prob in viscera_weight_priors.items():
        print(f"  P({category}) = {prob:.4f}")

    # - Shell_weight
    def shell_weight_bins(weight):
        if weight < 0.15:
            return 'Light'
        elif weight < 0.25:
            return 'Medium'
        elif weight < 0.35:
            return 'Heavy'
        else:
            return 'Very Heavy'
    
    shell_weight_priors = calculate_continuous_priors(abalone_subset, 'Shell_weight', shell_weight_bins)
    print("\nPrior probabilities for Shell_weight categories:")
    for category, prob in shell_weight_priors.items():
        print(f"  P({category}) = {prob:.4f}")

    # - Rings (this is already discrete/integer, but we can group into age categories)
    def rings_bins(rings):
        if rings < 8:
            return 'Young'
        elif rings < 11:
            return 'Adult'
        elif rings < 15:
            return 'Mature'
        else:
            return 'Old'
    
    rings_priors = calculate_continuous_priors(abalone_subset, 'Rings', rings_bins)
    print("\nPrior probabilities for Rings (Age) categories:")
    for category, prob in rings_priors.items():
        print(f"  P({category}) = {prob:.4f}")

    print("-" * 80)
    print("- Car DataSet")
    print("-" * 80)
    # Read car.data file
    # Column names based on car.c54-names file:
    # buying:   vhigh, high, med, low.
    # maint:    vhigh, high, med, low.
    # doors:    2, 3, 4, 5more.
    # persons:  2, 4, more.
    # lug_boot: small, med, big.
    # safety:   low, med, high.
    car_column_names = ['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety', 'acceptability']
    car_data = []

    # Open and read the CSV file
    with open('car.data', 'r') as file:
        for line in file:
            values = line.strip().split(',')  # Strip whitespace and split by comma
            row_dict = {}  # Create a dictionary for this row
            for i in range(0, len(car_column_names)):
                if i < len(values):
                    row_dict[car_column_names[i]] = values[i]
            car_data.append(row_dict)

    # Extract a relevant subset
    SUBSET_SIZE = 200
    random.seed(65426)
    car_subset = random.sample(car_data, min(SUBSET_SIZE, len(car_data)))

    # Calculate prior probabilities for each attribute value
    prior_probs = {}

    for col_index, col_name in enumerate(car_column_names[:-1]):  # exclude target class
        counts = {}
        for row in car_subset:
            value = row[col_name]  # Use column name instead of index
            if value not in counts:
                counts[value] = 0
            counts[value] += 1

        # Compute probabilities
        prior_probs[col_name] = {}
        for val, count in counts.items():
            prior_probs[col_name][val] = round(count / SUBSET_SIZE, 4)

    # Display prior probabilities
    print("Prior Probabilities for Each Attribute Value:\n")
    for attribute, probs in prior_probs.items():
        print(f"{attribute}:")
        for val, prob in probs.items():
            print(f"  {val}: {prob}")
        print()

    # Estimate the probability of the evidence within the dataset using NumPy
    print("\n" + "="*60)
    print("PROBABILITY OF EVIDENCE ESTIMATION")
    print("="*60)




    # Determine the likelihood of the evidence (the numerator of Bayes' formula).

    pass

if __name__ == "__main__":
    # Q1_1()
    # Q1_2()
    Q1_3()
