import random
import argparse
import os


class POSLabeler:
    def __init__(self):
        self.language_model = {'transitions': {}, 'emissions': {}}
        self.training_file = None
        self.test_file = None
        self.default_context = [""]

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

            # TODO: should we clean up the text at all?

            # split the text up into tokens
            for token in input_str.split():
                # split the token into word, part-of-speech
                word, pos = token.split('_')

                # update the emission probabilities for the current part-of-speech and word
                self.update_emission_probabilities(pos, word)

                # update the transition probabilities for the current context and part-of-speech
                self.update_transition_probabilities(context, pos)

                # update the context with the current word
                context = self.update_context(context, pos)



    def update_emission_probabilities(self, pos, word):
        # get the emissions probabilities from the language model
        emissions = self.language_model.get('emissions')

        # get the word counts from the emissions for the part-of-speech (create one if necessary)
        word_counts = emissions.setdefault(pos, {word: 0})

        # get the word count for the current word
        word_count = word_counts.setdefault(word, 0)

        # increment the word count and add it back to the word counts
        word_counts[word] = word_count + 1

    def update_transition_probabilities(self, context, pos):
        # get the transition probabilities from the language model
        transitions = self.language_model.get('transitions')

        # get the part-of-speech counts for the current context (create one if it doesn't already exist)
        pos_counts = transitions.setdefault(context, {pos: 0})

        # get the part-of-speech count for the current pos
        pos_count = pos_counts.setdefault(pos, 0)

        # increment the word count and add it to the word counts dictionary
        pos_counts[pos] = pos_count + 1

        # put the word counts dictionary back into the model
        transitions[context] = pos_counts

    # def generate_output(self):
    #     print "Generating text ..."
    #     print
    #
    #     # get a context to start with
    #     context = self.select_context()
    #
    #     # select words up to the desired length
    #     for i in range(self.output_length):
    #         # select the word given the current context
    #         word = self.select_word(context)
    #
    #         # print out the word (followed by a space)
    #         print word,
    #
    #         # update the context with the last word
    #         context = self.update_context(context, word)
    #
    #     print
    #     print

    def select_context(self):
        return random.sample(self.language_model.keys(), 1)[0]

    def select_word(self, context):
        # get the dictionary of words for the current context
        word_counts = self.language_model[context]

        # if there is only one word, then just return that
        if len(word_counts) == 1:
            return word_counts.keys()[0]

        # get the total number of words for the given context
        total_words = sum(word_counts.values())

        # pick a number, any number, between 1 and the total number of words
        num = random.randint(1, total_words)

        word_low = word_high = 0
        for word in word_counts:
            word_low = word_high
            word_high = word_low + word_counts[word]

            if word_low < num <= word_high:
                return word

        return word_counts.keys()[0]

    @staticmethod
    def update_context(context, word):
        return tuple((list(context) + [word])[1:])


if __name__ == '__main__':
    try:
        labeler = POSLabeler()
        labeler.generate_language_model()
    except Exception, e:
        print e.message
