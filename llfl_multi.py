"""Solution to exercise 45 from http://www.ling.gu.se/~lager/python_exercises.html

A certain childrens game involves starting with a word in a particular category. Each participant in turn says a word, but that word must begin with the final letter of the previous word. Once a word has been given, it cannot be repeated. If an opponent cannot give a word in the category, they fall out of the game. For example, with "animals" as the category,

Child 1: dog 
Child 2: goldfish
Child 1: hippopotamus
Child 2: snake
...

Your task in this exercise is as follows: Take the following selection of 70 English Pokemon names (extracted from Wikipedia's list of Pokemon) and generate the/a sequence with the highest possible number of Pokemon names where the subsequent name starts with the final letter of the preceding name. No Pokemon name is to be repeated.

audino bagon baltoy banette bidoof braviary bronzor carracosta charmeleon
cresselia croagunk darmanitan deino emboar emolga exeggcute gabite
girafarig gulpin haxorus heatmor heatran ivysaur jellicent jumpluff kangaskhan
kricketune landorus ledyba loudred lumineon lunatone machamp magnezone mamoswine
nosepass petilil pidgeotto pikachu pinsir poliwrath poochyena porygon2
porygonz registeel relicanth remoraid rufflet sableye scolipede scrafty seaking
sealeo silcoon simisear snivy snorlax spoink starly tirtouga trapinch treecko
tyrogue vigoroth vulpix wailord wartortle whismur wingull yamask

---

Attempted to improve solution using multiprocessing. Didn't work for 151 Pokemon!

"""

import inspect
import pdb
from bulba_parse import get_pokemon_list
import sys
from multiprocessing import Process, Queue
from time import clock

POISON_PILL = 'POISON_PILL'
PROCESSES_COUNT = 12
CALLS_GAP = 1000000

args = sys.argv[1:]

use_all_names = False

for arg in args:
    if arg == '-h' or arg == '--help':
        print('usage: {0} [-h] [--all]\n\n'.format(sys.argv[0]) +
              'Solves LLFL (last letter-first letter) problem.\n' + 
              'See exercise 45 at http://www.ling.gu.se/~lager/python_exercises.html\n\n' + 
              'optional arguments:\n' +
              '-h, --help  show this help message and exit\n' +
              '--all       use all names in pokemon_list.txt; by default, 70 names are used')
        sys.exit(0)
    elif arg == '--all':
        use_all_names = True

def is_llfl_match(first_word, other_word):
    return first_word[-1] == other_word[0]

def hacky_is_llfl_match(first_word, other_word):
    return first_word == '' or first_word[-1] == other_word[0]


class Pokemon:
    def __init__(self, name, all_candidates, match_function):
        # match_function must take two arguments
        self.name = name
        self.matches = dict()
        for candidate in all_candidates:
            if match_function(name, candidate):
                self.matches[candidate] = None

    def get_matches(self):
        return self.matches

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name.__repr__()

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

class StackBuster:
    def __init__(self, all_candidates):
        self.all_candidates = all_candidates
        self.stack_frames = 0
        self.max_stack_frames = 0
        self.lib_max_stack_frames = 0
        self.total_calls = 0

    def stack_buster(self, root_word, curr_candidates):
        """Returns longest last letter-first letter sequence starting with root_word formed from curr_candidates dictionary.

        curr_candidates: Dictionary containing all candidates, except those that are already in the sequence.

        A recursive function that will probably kill your stack if you try to catch'em all.
        Builds longest sequence "backwards".
        """
        self.total_calls += 1
        if not self.total_calls % 1000:
            print("Made {0} calls so far.".format(self.total_calls))
        # Keep track of number of open stack frames, just for fun
        if len(inspect.stack()) > self.lib_max_stack_frames:
            self.lib_max_stack_frames = len(inspect.stack())

        self.stack_frames += 1
        if self.stack_frames > self.max_stack_frames:
            self.max_stack_frames = self.stack_frames

        sequences = []
        for candidate in curr_candidates:
            if hacky_is_llfl_match(root_word, candidate):
                next_candidates = curr_candidates.copy()
                del next_candidates[candidate]
                sequences.append(self.stack_buster(candidate, next_candidates))
        
        print("root: {0}".format(root_word))
        print("seqs: {0}".format(sequences))
        pdb.set_trace()

        self.stack_frames -= 1

        if len(sequences) < 1:
            return [root_word]
        else:
            return [root_word] + max(sequences, key=len)

    def fast_stack_buster(self, root_word, not_candidates):
        """Returns longest last letter-first letter sequence starting with root_word formed from curr_candidates dictionary.

        curr_candidates: Dictionary containing all candidates, except those that are already in the sequence.

        A recursive function that will probably kill your stack if you try to catch'em all.
        Builds longest sequence "backwards".
        """
        self.total_calls += 1
        if not self.total_calls % 1000:
            print("Made {0} calls so far.".format(self.total_calls))
        # Keep track of number of open stack frames, just for fun
        if len(inspect.stack()) > self.lib_max_stack_frames:
            self.lib_max_stack_frames = len(inspect.stack())

        self.stack_frames += 1
        if self.stack_frames > self.max_stack_frames:
            self.max_stack_frames = self.stack_frames

        sequences = []
        for candidate in self.all_candidates:
            if candidate not in not_candidates and hacky_is_llfl_match(root_word, candidate):
                next_not_candidates = not_candidates.copy()
                next_not_candidates[candidate] = None
                sequences.append(self.fast_stack_buster(candidate, next_not_candidates))
        
        self.stack_frames -= 1

        if len(sequences) < 1:
            return [root_word]
        else:
            return [root_word] + max(sequences, key=len)

    def solve_llfl(self):
        longest_sequence = self.stack_buster('', self.all_candidates)[1:]
        print("Max length: {0}".format(len(longest_sequence)))
        print("Max sequence: ")
        print(longest_sequence)
        print("Current stack frames: {0}".format(self.stack_frames))
        print("Max stack frames: {0}".format(self.max_stack_frames))
        print("Max stack frames from module inspect: {0}".format(self.lib_max_stack_frames))

    def fast_solve_llfl(self):
        longest_sequence = self.fast_stack_buster('', dict())[1:]
        print("Max length: {0}".format(len(longest_sequence)))
        print("Max sequence: ")
        print(longest_sequence)
        print("Current stack frames: {0}".format(self.stack_frames))
        print("Max stack frames: {0}".format(self.max_stack_frames))
        print("Max stack frames from module inspect: {0}".format(self.lib_max_stack_frames))

    def pokemon_stack_buster(self, root_pokemon, curr_candidates):
        """Returns longest last letter-first letter sequence starting with root_pokemon formed from curr_candidates dictionary.

        curr_candidates: Dictionary containing all candidates, except those that are already in the sequence.

        A recursive function that will probably kill your stack if you try to catch'em all.
        Builds longest sequence "backwards".
        USE THIS! Faster than other stack buster methods.
        """
        self.total_calls += 1
        if not self.total_calls % 1000000:
            print("Made {0:,} calls so far.".format(self.total_calls))
        # Keep track of number of open stack frames, just for fun
        # Using this is crazy slow, don't use this.
        #if len(inspect.stack()) > self.lib_max_stack_frames:
        #    self.lib_max_stack_frames = len(inspect.stack())

        self.stack_frames += 1
        if self.stack_frames > self.max_stack_frames:
            self.max_stack_frames = self.stack_frames

        #print("root: {0}".format(root_pokemon))
        #pdb.set_trace()

        sequences = []
        for match in root_pokemon.matches:
            if match in curr_candidates:
                #print("mtch: {0}".format(match))
                #print("seqs: {0}".format(sequences))
                #pdb.set_trace()
                next_candidates = curr_candidates.copy()
                next_root = next_candidates.pop(match)
                #pdb.set_trace()
                sequences.append(self.pokemon_stack_buster(next_root, next_candidates))

        self.stack_frames -= 1

        if len(sequences) < 1:
            return [root_pokemon]
        else:
            return [root_pokemon] + max(sequences, key=len)     

    def pokemon_solve_llfl(self):
        longest_sequence = self.pokemon_stack_buster(Pokemon('', self.all_candidates, hacky_is_llfl_match), self.all_candidates)[1:]
        print("Max length: {0}".format(len(longest_sequence)))
        print("Max sequence: ")
        print(longest_sequence)
        print("Current stack frames: {0}".format(self.stack_frames))
        print("Max stack frames: {0}".format(self.max_stack_frames))
        print("Total calls: {0:,}".format(self.total_calls))

    def fast_pokemon_stack_buster(self, root_pokemon, already_used_candidates, track_total_calls=True):
        """Returns longest last letter-first letter sequence starting with root_pokemon formed from curr_candidates dictionary.

        curr_candidates: Dictionary containing all candidates, except those that are already in the sequence.

        A recursive function that will probably kill your stack if you try to catch'em all.
        Builds longest sequence "backwards".
        USE THIS! Faster than other stack buster methods.
        """
        if track_total_calls:
            self.total_calls += 1
            if not self.total_calls % 1000000:
                print("Made {0:,} calls so far.".format(self.total_calls))
        # Keep track of number of open stack frames, just for fun
        # Using this is crazy slow, don't use this.
        #if len(inspect.stack()) > self.lib_max_stack_frames:
        #    self.lib_max_stack_frames = len(inspect.stack())

        self.stack_frames += 1
        if self.stack_frames > self.max_stack_frames:
            self.max_stack_frames = self.stack_frames

        #print("root: {0}".format(root_pokemon))
        #pdb.set_trace()

        #print("Root:", root_pokemon.name)
        sequences = []
        for match in root_pokemon.matches:
            if match not in already_used_candidates:
                #print("mtch: {0}".format(match))
                #print("seqs: {0}".format(sequences))
                #pdb.set_trace()
                next_already_used_candidates = already_used_candidates.copy()
                next_already_used_candidates[match] = None
                next_root = self.all_candidates[match]
                #pdb.set_trace()
                sequences.append(self.fast_pokemon_stack_buster(next_root, next_already_used_candidates, track_total_calls))

        self.stack_frames -= 1

        if len(sequences) < 1:
            return [root_pokemon]
        else:
            return [root_pokemon] + max(sequences, key=len)     

    def fast_pokemon_solve_llfl(self):
        longest_sequence = self.fast_pokemon_stack_buster(Pokemon('', self.all_candidates, hacky_is_llfl_match), dict())[1:]
        print("Max length: {0}".format(len(longest_sequence)))
        print("Max sequence: ")
        print(longest_sequence)
        print("Current stack frames: {0}".format(self.stack_frames))
        print("Max stack frames: {0}".format(self.max_stack_frames))
        print("Total calls: {0:,}".format(self.total_calls))

    def multi_stack_buster(self, in_queue, out_queue):
        """Returns longest last letter-first letter sequence starting with root_pokemon formed from curr_candidates dictionary.

        curr_candidates: Dictionary containing all candidates, except those that are already in the sequence.

        A recursive function that will probably kill your stack if you try to catch'em all.
        Builds longest sequence "backwards".
        USE THIS! Faster than other stack buster methods.
        """
        while not in_queue.empty():
            task = in_queue.get()
            if task == POISON_PILL:
                out_queue.put(POISON_PILL)
                return

            print("Starting task:", task)
            self.total_calls = 0
            self.max_stack_frames = 0
            next_already_used_candidates = dict()
            next_already_used_candidates[task.name] = None
            # Don't call multi version for now
            result = self.fast_pokemon_stack_buster(task, next_already_used_candidates, False)
            print("Finishing task:", task)
            out_queue.put((result, self.total_calls, self.max_stack_frames))

class MultiStackBuster(Process):
    def __init__(self, in_queue, out_queue, all_candidates):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.sb = StackBuster(all_candidates)
        Process.__init__(self)

    def run(self):
        try:
            print("In", self.name)
            self.sb.multi_stack_buster(self.in_queue, self.out_queue)
            print("Exiting", self.name)
        except Exception as e:
            self.out_queue.put(POISON_PILL)
            raise e


if __name__ == '__main__':

    start_time = clock()

    if use_all_names:
        pokemon_list = get_pokemon_list() # from bulba_parse
    else:
        pokemon_string = '''audino bagon baltoy banette bidoof braviary bronzor carracosta charmeleon
        cresselia croagunk darmanitan deino emboar emolga exeggcute gabite
        girafarig gulpin haxorus heatmor heatran ivysaur jellicent jumpluff kangaskhan
        kricketune landorus ledyba loudred lumineon lunatone machamp magnezone mamoswine
        nosepass petilil pidgeotto pikachu pinsir poliwrath poochyena porygon2
        porygonz registeel relicanth remoraid rufflet sableye scolipede scrafty seaking
        sealeo silcoon simisear snivy snorlax spoink starly tirtouga trapinch treecko
        tyrogue vigoroth vulpix wailord wartortle whismur wingull yamask'''
        pokemon_list = pokemon_string.split()

    pokemon_dict = dict()

    #for pokemon in pokemon_list:
    #   pokemon_dict[pokemon] = None

    for pokemon_name in pokemon_list:
        pokemon_dict[pokemon_name] = Pokemon(pokemon_name, pokemon_list, is_llfl_match)

    in_queue = Queue()
    out_queue = Queue()

    for pokemon_name in pokemon_dict:
        in_queue.put(pokemon_dict[pokemon_name])

    for i in range(PROCESSES_COUNT):
        in_queue.put(POISON_PILL)

    print("Starting processes...")

    process_list = []

    for i in range(PROCESSES_COUNT):
        process = MultiStackBuster(in_queue, out_queue, pokemon_dict)
        process_list.append(process)
        process.start()

    # Watch processes
    alive_processes = PROCESSES_COUNT
    max_sequence = []
    max_length = 0
    total_calls = 0
    max_stack_frames = 0
    calls_threshold = CALLS_GAP
    while alive_processes > 0:
        result = out_queue.get()
        if result == POISON_PILL:
            alive_processes -= 1
        else:
            # Check sequence
            sequence = result[0]
            if len(sequence) > max_length:
                max_sequence = sequence
                max_length = len(sequence)
            # Check calls
            total_calls += result[1]
            if total_calls > calls_threshold:
                while total_calls > calls_threshold:
                    calls_threshold += CALLS_GAP
                print("Made {0:,} calls so far.".format(total_calls))
                
            # Check stack frames
            stack_frames = result[2]
            if stack_frames > max_stack_frames:
                max_stack_frames = stack_frames

    # Join processes
    print("Joining processes...")
    for process in process_list:
        process.join()

    # Print final results
    print("Max length: {0}".format(max_length))
    print("Max sequence: ")
    print(max_sequence)
    print("Max stack frames: {0}".format(max_stack_frames))
    print("Total calls: {0:,}".format(total_calls))

    end_time = clock()

    print("Runtime: {0}".format(end_time - start_time))