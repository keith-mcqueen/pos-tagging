# import random
import argparse
import os
from math import log

TOTAL = '#####'


class POSLabeler:
    def __init__(self):
        self.training_file = None
        self.test_file = None
        self.default_context = [""]

        self.transition_probabilities = {}
        self.emission_probabilities = {}
        self.initial_probabilities = {}

        self.token_count = 0

        # parse the command line args
        self.parse_args()

    def parse_args(self):
        # set up the arg-parser
        parser = argparse.ArgumentParser(prog="Part-of-speech labeler",
                                         description="This program analyzes input text to generate an n-gram model and "
                                                     "then generates random text based on the model",
                                         add_help=True)

        # add the <training-data> argument
        parser.add_argument("--training-data",
                            action="store",
                            help="The path to a file containing training data for part-of-speech labeling")

        # add the <training-data> argument
        parser.add_argument("--test-data",
                            action="store",
                            help="The path to a file containing test data for part-of-speech labeling")

        # add the <n> argument
        parser.add_argument("--n",
                            type=int,
                            action="store",
                            default=1,
                            help="the 'n' in n-gram")

        # parse the arguments
        args = parser.parse_args()

        # check the training file
        self.training_file = args.training_data
        if self.training_file is None:
            raise Exception("No training file provided")
        if not os.path.exists(self.training_file):
            raise Exception("Training file %s does not exist" % self.training_file)
        if not os.path.isfile(self.training_file):
            raise Exception("Path %s is not a file" % self.training_file)

        # check the test file
        self.test_file = args.test_data
        if self.test_file is None:
            raise Exception("No test file provided")
        if not os.path.exists(self.training_file):
            raise Exception("Test file %s does not exist" % self.test_file)
        if not os.path.isfile(self.training_file):
            raise Exception("Path %s is not a file" % self.test_file)

        # pre-generate the context
        self.default_context = [""] * args.n

    def generate_language_model(self):
        print
        print "Creating model from %s ..." % self.training_file
        print

        # start with the default context
        context = tuple(self.default_context)

        with open(self.training_file, 'r') as in_file:
            input_str = in_file.read()

            # split the text up into tokens
            for token in input_str.split():
                # increment the token count
                self.token_count += 1

                # split the token into word, part-of-speech
                word, pos = token.split('_')

                # update the emission probabilities for the current part-of-speech and word
                self.update_emission_probabilities(pos, word)

                # update the transition probabilities for the current context and part-of-speech
                self.update_transition_probabilities(context, pos)

                # update the context with the current word
                context = self.update_context(context, pos)

        # perform some model post-processing
        self.compute_initial_probabilities()

    def update_emission_probabilities(self, pos, word):
        # get the word counts from the emissions for the part-of-speech (create one if necessary)
        word_counts = self.emission_probabilities.setdefault(pos, {word: 0, TOTAL: 0})

        # get the word count for the current word
        word_count = word_counts.setdefault(word, 0)

        # increment the word count and add it back to the word counts
        word_counts[word] = word_count + 1
        word_counts[TOTAL] += 1

    def update_transition_probabilities(self, context, pos):
        # get the part-of-speech counts for the current context (create one if it doesn't already exist)
        pos_counts = self.transition_probabilities.setdefault(context, {pos: 0, TOTAL: 0})

        # get the part-of-speech count for the current pos
        pos_count = pos_counts.setdefault(pos, 0)

        # increment the word count and add it to the word counts dictionary
        pos_counts[pos] = pos_count + 1
        pos_counts[TOTAL] += 1

    def do_pos_labeling(self):
        print
        print "Performing Part-of-Speech labeling on %s ..." % self.test_file
        print

        # context = tuple(self.default_context)
        v = {}

        with open(self.test_file, 'r') as test_file:
            input_str = test_file.read()

            # split the text up into tokens
            tokens = input_str.split()

            # compute the initial probability for the 0th token
            word, pos = tokens[0].split('_')
            for pos_tag in self.initial_probabilities:
                e_prob = self.emission_probabilities[pos_tag]
                count = float(e_prob.setdefault(word, 1))
                total = float(e_prob[TOTAL])
                v[pos_tag] = log(self.initial_probabilities[pos_tag] * (count / total))

            for token in tokens[1:]:
                # split the token into word and part-of-speech
                word, pos = token.split('_')

                for context in self.transition_probabilities:
                    # best_prob, best_pos = max((v[tag] * (float(self.transition_probabilities[context].setdefault(tag, 1)) / float(self.transition_probabilities[context][TOTAL])) * (float(self.emission_probabilities[tag].setdefault(word, 1)) / float(self.emission_probabilities[tag][TOTAL])), tag) for tag in self.emission_probabilities)
                    best_prob, best_pos = max((v[tag] + log(float(self.transition_probabilities[context].setdefault(tag, 1)) / float(self.transition_probabilities[context][TOTAL])) + log(float(self.emission_probabilities[tag].setdefault(word, 1)) / float(self.emission_probabilities[tag][TOTAL])), tag) for tag in self.emission_probabilities)
                    v[best_pos] = best_prob


                best_prob, best_pos = max((v[tag], tag) for tag in v)
                print "%5s  %5s  %14.13f" % (pos, best_pos, best_prob)

    @staticmethod
    def update_context(context, word):
        return tuple((list(context) + [word])[1:])

    def compute_initial_probabilities(self):
        print "Total number of words read: %s" % self.token_count
        print
        print "POS Tag  POS Tokens  POS Probability"
        print "=======  ==========  ==============="

        for pos in self.emission_probabilities:
            pos_token_count = self.emission_probabilities[pos][TOTAL]
            pos_probability = float(pos_token_count) / float(self.token_count)
            self.initial_probabilities[pos] = pos_probability
            print " %5s    %7s    %12.13f" % (pos, pos_token_count, pos_probability)

if __name__ == '__main__':
    # try:
    #     labeler = POSLabeler()
    #     labeler.generate_language_model()
    # except Exception, e:
    #     print e.message

    labeler = POSLabeler()
    labeler.generate_language_model()
    labeler.do_pos_labeling()
