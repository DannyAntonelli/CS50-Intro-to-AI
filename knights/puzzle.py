from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

RULES_A = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave))
)

RULES_B = And(
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave))
)

RULES_C = And(
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave))
)

# Puzzle 0
# A says "I am both a knight and a knave."
A0 = And(AKnight, AKnave)
knowledge0 = And(
    RULES_A,

    Implication(AKnight, A0),
    Implication(AKnave, Not(A0))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
A1 = And(AKnave, BKnave)
knowledge1 = And(
    RULES_A,
    RULES_B,

    Implication(AKnight, A1),
    Implication(AKnave, Not(A1))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
A2 = Or(And(AKnight, BKnight), And(AKnave, BKnave))
B2 = Or(And(AKnight, BKnave), And(AKnave, BKnight))
knowledge2 = And(
    RULES_A,
    RULES_B,

    Implication(AKnight, A2),
    Implication(AKnave, Not(A2)),
    Implication(BKnight, B2),
    Implication(BKnave, Not(B2))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
A3_1 = And(Implication(AKnight, AKnight), Implication(AKnave, Not(AKnight)))
A3_2 = And(Implication(AKnight, AKnave), Implication(AKnave, Not(AKnave)))
knowledge3 = And(
    RULES_A,
    RULES_B,
    RULES_C,

    Or(A3_1, A3_2),
    Implication(BKnight, And(A3_2, CKnave)),
    Implication(BKnave, And(Not(A3_2), Not(CKnave))),
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
