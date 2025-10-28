import sys
sys.path.append('./aima-python')  # Ensure correct path to aima-python

from logic import Expr, PropKB,expr

def q1_smart_home_system():

    #1  Propositional Logic - Smart Home System
    """
    Step 1: Represent the facts as propositional variables

    We will represent the facts from the problem description using propositional variables:

        A: It's dark outside.
        B: The living room lights are on.
        C: It's cold outside.
        D: The heater is on.
        E: It's 7 pm.
        F: The temperature inside is below 18°C.

    Step 2: Construct rules in propositional logic

    The rules provided in the problem can be written in propositional logic as follows:

        If it's 7 pm, it is dark outside:
        E ⇒ A
        If it’s dark outside, the living room lights should be turned on:
        A ⇒ B
        If the temperature inside is below 18°C, it’s considered cold:
        F ⇒ C
        If the living room lights are on and it’s cold outside, the heater should be turned on:
        B ∧ C ⇒ D

    Scenario 1: Bob enters his home at 7 pm, and the temperature outside is 17°C (below 18°C).

        Given facts: E=True,F=TrueE=True,F=True
        Inference steps:
            E⇒A: Since E=True, A=True (It’s dark outside).
            A⇒B: Since A=True, B=True (Living room lights are on).
            F⇒C: Since F=True, C=True (It’s cold outside).
            B∧C⇒D: Since both B=True and C=True, D=True (The heater is on).
        Result: The heater is on. (Expected: True)

    Scenario 2: The temperature outside is 19°C (above 18°C).

        Given facts: E=True,F=False
        Inference steps:
            E⇒A: Since E=True, A=True (It’s dark outside).
            A⇒B: Since A=True, B=True (Living room lights are on).
            F⇒C: Since F=False, C=False (It’s not cold outside).
            B∧C⇒D: Since C=False, D=False (The heater is not on).
        Result: The heater is off. (Expected: False)

    """

    # Step 1: Define the facts using propositional variables
    A = Expr('A')  # It's dark outside
    B = Expr('B')  # The living room lights are on
    C = Expr('C')  # It's cold outside
    D = Expr('D')  # The heater is on
    E = Expr('E')  # It's 7 pm
    F = Expr('F')  # The temperature inside is below 18°C

    # Step 2: Construct rules in propositional logic
    kb = PropKB()  # Initialize the knowledge base (KB)

    # Add the rules to the KB
    kb.tell(E |'==>'| A)           # E implies A (If it's 7 pm, it's dark outside)
    kb.tell(A |'==>'|  B)           # A implies B (If it's dark outside, the living room lights are on)
    kb.tell(F |'==>'|  C)           # F implies C (If the temperature is below 18°C, it's cold)
    kb.tell(B & C |'==>'| D)       # B and C imply D (If the lights are on and it's cold, the heater is on)

    # Step 3: Scenario 1 - Bob enters his home at 7 pm, and the temperature is below 18°C.
    kb.tell(E)  # It's 7 pm (E is True)
    kb.tell(F)  # The temperature is below 18°C (F is True)

    # Perform inference to check if the heater (D) is on
    print("Scenario 1: Is the heater on?", kb.ask_if_true(D))  # Expected: True

    # Step 4: Scenario 2 - The temperature is above 18°C.
    kb.retract(F)  # Now the temperature is not below 18°C (F is False)
    kb.tell(~F)    # Assert that F is False (the temperature is not below 18°C)

    # Perform inference to check if the heater (D) is on
    print("Scenario 2: Is the heater on?", kb.ask_if_true(D))  # Expected: False


def q2_smart_medical_system():

    """
    #2 First-Order Logic - Smart Medical System

    Step 1: Define the knowledge base in FOL

    We will use predicates to define the facts:
        HasFever(x): x has a fever.
        HasCough(x): x has a cough.
        HasFlu(x): x has the flu.
        NeedsAntiviral(x): x needs antiviral medication.
        HasRash(x): x has a rash.
        HasItchiness(x): x has itchiness.
        HasAllergicReaction(x): x has an allergic reaction.
        NeedsAntihistamines(x): x needs antihistamines.

    Step 2: Rules in FOL

    We represent the rules from the problem description using FOL:

        If someone has a fever and a cough, they might have the flu:
        ∀x HasFever(x) ∧ HasCough(x) ⇒ HasFlu(x)
        
        If someone has the flu, they need antiviral medication:
        ∀x HasFlu(x) ⇒ NeedsAntiviral(x)
        
        If someone has a rash and itchiness, they might have an allergic reaction:
        ∀x HasRash(x) ∧ HasItchiness(x) ⇒ HasAllergicReaction(x)
        
        If someone has an allergic reaction, they need antihistamines:
        ∀x HasAllergicReaction(x) ⇒ NeedsAntihistamines(x)
        

    Step 3: Given facts

        John has a fever and a cough:
        HasFever(John),HasCough(John)
        Alice has a rash:
        HasRash(Alice)

    Step 4: Forward Chaining to Determine Treatments

    Using forward chaining, we can infer:

        For John:
        Since John has a fever and a cough, 
        HasFever(John) ∧ HasCough(John) ⇒ HasFlu(John), so John has the flu.
            Since John has the flu, 
        HasFlu(John) ⇒ NeedsAntiviral(John), so John needs antiviral medication.

        For Alice:
            Since Alice has a rash, but no information about itchiness is provided, we cannot infer if Alice has an allergic reaction, and thus we cannot determine if she needs antihistamines.

    Step 5: Results

        John's treatment: John needs antiviral medication.
        Alice's treatment: No treatment determined from the given information.
    """

    from logic import FolKB, fol_fc_ask

    # # Step 1: Define the knowledge base in FOL
    kb = FolKB()

    # # Step 2: Add rules in FOL

    # If someone has a fever and a cough, they might have the flu
    kb.tell(expr('(HasFever(x) & HasCough(x)) ==> HasFlu(x)'))
    # If someone has the flu, they need antiviral medication
    kb.tell(expr('HasFlu(x) ==> NeedsAntiviral(x)'))
    # If someone has a rash and itchiness, they might have an allergic reaction
    kb.tell(expr('(HasRash(x) & HasItchiness(x)) ==> HasAllergicReaction(x)'))
    # If someone has an allergic reaction, they need antihistamines
    kb.tell(expr('HasAllergicReaction(x) ==> NeedsAntihistamines(x)'))

    # Step 3: Add facts about John and Alice

    # John has a fever and a cough
    kb.tell(expr('HasFever(John)'))
    kb.tell(expr('HasCough(John)'))

    # Alice has a rash (but no information about itchiness)
    kb.tell(expr('HasRash(Alice)'))

    #Sanity check - review clauses in the knowledge base
    print_clauses(kb)

    # Step 4: Use forward chaining to infer treatments
    infer_john_flu = fol_fc_ask(kb, expr('HasFlu(John)'))

    print('\nDoes John have the flu?', list(infer_john_flu))  
    print('\n So why are you getting [{}]?\n [{}] indicates that the KB infers that John has the flu, and the empty dictionary {} represents the substitution where no variables need to be instantiated.')

    #Ok, so at this point the fol_fc_ask has added the new clauses to the kb, negating the need for the substitution which would be returned. We can try asking the KB directly if John has the flu.

    #Sanity check - review clauses in the knowledge base
    print_clauses(kb, "See the new clauses in the KB after forward chaining:")

       
    print("\nNow querying the kb:")
    query_flu = kb.ask(expr('HasFlu(x)'))
    print("Who has the flu?", query_flu)  # Expected: substitutions for John
    
    query_flu_john = kb.ask(expr('HasFlu(John)'))
    print("Does John have the flu?", query_flu_john)# Expected: John
    
    query_antiviral = kb.ask(expr('NeedsAntiviral(x)'))
    print("Who needs antiviral medication", query_antiviral)  # Expected: John substitutions

    query_antiviral_john = kb.ask(expr('NeedsAntiviral(John)'))
    print("Does John needs antiviral medication?", query_antiviral_john)# 
    
        
    # Check if Alice has both a rash and itchiness before inferring allergic reaction
    
    print_clauses(kb, "Before", False)
    
    
    infer_rash_alice = fol_fc_ask(kb, Expr('HasRash(Alice)'))
    # fol_fc_ask function is used to infer new information based on the existing rules and facts in the KB. When you query fol_fc_ask(kb, expr('HasRash(Alice)')), it checks if it can infer that Alice has a rash. Since HasRash(Alice) is already a fact in the KB, there's no need to infer it. Therefore, fol_fc_ask returns an empty list [], indicating that no new inferences were made.
    print('\nDoes Alice have a rash?', list(infer_rash_alice))  

    query_rash = kb.ask(expr('HasRash(x)'))
    # Searches the KB for any facts that match the pattern HasRash(x). It finds that Alice has a rash and returns a list containing one substitution: {'x': Alice}
    print('\nWho has a rash?', query_rash)  

    query_rash_alice = kb.ask(expr('HasRash(Alice)'))
    # Checks if the specific fact HasRash(Alice) exists in the KB. Since this fact is present, it returns an empty dictionary {}. In this context, an empty dictionary signifies that the query is true without requiring any variable substitutions.
    print("Does Alice have a rash?", query_rash_alice)# 
    
    query_antihistamines_alice = fol_fc_ask(kb, expr('NeedsAntihistamines(Alice)'))
    # Returns an empty list, it means that no new inferences could be made based on the current KB. Occurs when the queried fact is already present or cannot be inferred due to missing information.
    print("Does Alice need an antihistamine?", list(query_antihistamines_alice))
 

def print_clauses(kb, message="Clauses in the Knowledge Base:", bool_print=True):
    if bool_print:
        print("\n" + message)
        for clause in kb.clauses:
            print(clause)
    print("Total Clauses: ", len(kb.clauses))

q1_smart_home_system()
q2_smart_medical_system()