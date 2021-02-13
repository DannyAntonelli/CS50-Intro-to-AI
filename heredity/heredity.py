import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def get_genes(person, one_gene, two_genes):
    """
    Return the number of genes a person has
    """
    if person in one_gene:
        return 1
    if person in two_genes:
        return 2
    return 0


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Tuple of the probability of inheriting a gene given
    # the number of genes of the parent (index of the tuple)
    PARENTS_PROB = (PROBS["mutation"], 0.5, 1 - PROBS["mutation"])

    # Initial probability
    probability = 1

    for person in people:
        n_genes, trait = get_genes(person, one_gene, two_genes), person in have_trait
        mother, father = people[person]["mother"], people[person]["father"]

        # if we have no information about the parents, we use unconditional probability
        if not mother and not father:
            probability *= PROBS["gene"][n_genes]

        else:
            mother_prob = PARENTS_PROB[get_genes(mother, one_gene, two_genes)]
            father_prob = PARENTS_PROB[get_genes(father, one_gene, two_genes)]

            # If two genes then mother and father has passed them
            if n_genes == 2:
                probability *= mother_prob * father_prob

            # If one gene then one between the mother and the father has passed it
            elif n_genes == 1:
                probability *= mother_prob * (1 - father_prob) + father_prob * (1 - mother_prob)
            
            # If no genes then no one passed them
            else:
                probability *= (1 - father_prob) * (1 - mother_prob)

        # Probability of trait given the number of genes
        probability *= PROBS["trait"][n_genes][trait]

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        n_genes = get_genes(person, one_gene, two_genes)
        trait = person in have_trait

        probabilities[person]["gene"][n_genes] += p
        probabilities[person]["trait"][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # Each probability is divided by the sum of all probabilities

        traits_probabilities = probabilities[person]["trait"].values()
        n = sum(traits_probabilities)
        for t in probabilities[person]["trait"]:
            probabilities[person]["trait"][t] /= n

        genes_probabilities = probabilities[person]["gene"].values()
        n = sum(genes_probabilities)
        for g in probabilities[person]["gene"]:
            probabilities[person]["gene"][g] /= n


if __name__ == "__main__":
    main()
