import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probabilities = {}
    CASUAL_LINK_PROBABILITY = (1 - damping_factor) / len(corpus)
    for p in corpus:
        probabilities[p] = CASUAL_LINK_PROBABILITY

    if corpus[page]:
        DIRECT_LINK_PROBABILITY = damping_factor / len(corpus[page])
        for p in corpus[page]:
            probabilities[p] += DIRECT_LINK_PROBABILITY

    return probabilities      


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    ranks = {}
    curr_page = random.choice(list(corpus.keys()))
    PROB_TO_ADD = 1 / n
    
    for _ in range(n - 1):
        ranks[curr_page] = ranks.get(curr_page, 0) + PROB_TO_ADD
        probabilities = transition_model(corpus, curr_page, damping_factor)
        curr_page = random.choices(list(probabilities.keys()), list(probabilities.values()))[0]

    return ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    INITIAL_PROB = 1 / len(corpus)
    PRECISION = 0.001
    ranks = {p: INITIAL_PROB for p in corpus}
    finished = False

    while not finished:
        finished = True
        new_ranks = {p: 0 for p in corpus}
        CONSTANT_PROB = (1 - damping_factor) / len(corpus)

        for starting_page in corpus:
            new_ranks[starting_page] += CONSTANT_PROB

            if corpus[starting_page]:
                num = damping_factor / len(corpus[starting_page])
                for landing_page in corpus[starting_page]:
                    new_ranks[landing_page] += num * ranks[starting_page]
                    if new_ranks[landing_page] - ranks[landing_page] > PRECISION:
                        finished = False

            else:
                num = damping_factor / len(corpus)
                for landing_page in corpus:
                    new_ranks[landing_page] += num * ranks[starting_page]
                if new_ranks[landing_page] - ranks[landing_page] > PRECISION:
                    finished = False

        ranks = new_ranks.copy()

    return ranks


if __name__ == "__main__":
    main()
