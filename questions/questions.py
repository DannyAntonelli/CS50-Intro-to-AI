import nltk
import sys
import os
import string
import math
import collections

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files_contents = {}

    # Iterate through the files inside the directory
    for root, _, files in os.walk(directory):
        for f in files:
            # If the file is a txt
            if f.endswith(".txt"):
                # Update the result dictionary
                files_contents[f] = open(os.path.join(root, f), "r", encoding="UTF_8").read()

    return files_contents


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    not_words = set(string.punctuation) | set(nltk.corpus.stopwords.words("english"))
    words = nltk.word_tokenize(document.lower())
    return list(filter(lambda w: w not in not_words, words))


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Create a dictionary with the occurencies of each word
    occ = {}

    for document in documents:
        added = set()

        # For each word in the document
        for word in documents[document]:

            # If the word wasn't already added update the dictionary
            if word not in added:
                added.add(word)
                occ[word] = occ.get(word, 0) + 1

    return {word: math.log(len(documents) / occ[word]) for word in occ}


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idf = {}

    for f in files:
        counter = collections.Counter(files[f])
        for word in query:
            tf_idf[f] = tf_idf.get(f, 0) + counter[word] * idfs[word]

    rank = sorted(tf_idf.items(), key=lambda f: f[1], reverse=True)
    return [f[0] for f in rank][:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    rank = []

    for sentence in sentences:
        # sentence, idf, query term density
        x = [sentence, 0, 0]
        counter = collections.Counter(sentences[sentence])

        for word in query:
            if word in counter:
                # Update idf
                x[1] += idfs[word]
                # Update query term density
                x[2] = counter[word] / len(sentences[sentence])

        rank.append(x)

    # Sort by tfs and query term density
    rank.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return [sentence for sentence, _, _ in rank][:n]


if __name__ == "__main__":
    main()
