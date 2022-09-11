#!/usr/bin/env python3

import sys
import json
from collections import OrderedDict, deque
from itertools import product
from glob import glob
from os.path import isdir, basename, join

# Performing list alignment may take **a ton** of time, especially for large JSONs
PERFORM_LIST_ALIGNMENT = False

def merge_votes(old_votes, new_votes):
    for name, new_vote_info in new_votes.items():
        old_votes_for_name = old_votes.get(name, {})
        for name_candidate, new_vote_score in new_vote_info.items():
            old_votes_for_name[name_candidate] = old_votes_for_name.get(name_candidate, 0) + new_vote_score
        old_votes[name] = old_votes_for_name
    return old_votes

def needleman_wunsch(x, y, s = lambda a,b: int(a==b)):
    """Run the Needleman-Wunsch algorithm on two sequences.

    x, y -- sequences.

    Code based on pseudocode in Section 3 of:

    Naveed, Tahir; Siddiqui, Imitaz Saeed; Ahmed, Shaftab.
    "Parallel Needleman-Wunsch Algorithm for Grid." n.d.
    https://upload.wikimedia.org/wikipedia/en/c/c4/ParallelNeedlemanAlgorithm.pdf
    """
    N, M = len(x), len(y)
    #s = lambda a, b: int(a == b)

    DIAG = -1, -1
    LEFT = -1, 0
    UP = 0, -1

    # Create tables F and Ptr
    F = {}
    Ptr = {}

    F[-1, -1] = 0
    for i in range(N):
        F[i, -1] = -i
    for j in range(M):
        F[-1, j] = -j

    option_Ptr = DIAG, LEFT, UP
    for i, j in product(range(N), range(M)):
        option_F = (
            F[i - 1, j - 1] + s(x[i], y[j]),
            F[i - 1, j] - 1,
            F[i, j - 1] - 1,
        )
        F[i, j], Ptr[i, j] = max(zip(option_F, option_Ptr))

    # Work backwards from (N - 1, M - 1) to (0, 0)
    # to find the best alignment.
    alignment = deque()
    i, j = N - 1, M - 1
    while i >= 0 and j >= 0:
        direction = Ptr[i, j]
        if direction == DIAG:
            element = i, j
        elif direction == LEFT:
            element = i, None
        elif direction == UP:
            element = None, j
        alignment.appendleft(element)
        di, dj = direction
        i, j = i + di, j + dj
    while i >= 0:
        alignment.appendleft((i, None))
        i -= 1
    while j >= 0:
        alignment.appendleft((None, j))
        j -= 1

    return list(alignment)

def alignment_score(x, y, alignment, comparator = lambda a, b: int(a == b)):
    """Score an alignment.

    x, y -- sequences.
    alignment -- an alignment of x and y.
    """
    score_gap = -1
    score_same = +1
    score_different = -1

    score = 0
    for i, j in alignment:
        if (i is None) or (j is None):
            score += score_gap
        else:
            comp = comparator(x[i], y[j])
            score += comp * score_same + (1-comp)*score_different

    return score

def comparator(x,y):
    if x == y:
        return 1

    if type(x) != type(y):
        return 0
    else:
        if isinstance(x, list) or isinstance(x, dict):
            if isinstance(x, dict):
                x = list(x.values())
                y = list(y.values())
            max_len = max(len(x), len(y))
            if max_len == 0:
                return 1 # Empty collections are the same
            return (alignment_score(x, y, needleman_wunsch(x, y, comparator), comparator) + max_len) / (2 * max_len)
        else:
            return int(x == y)

def map_dict(obf, deobf): # Does take order into account
    #print("Mapping dict")
    votes = {}
    obf_fields = list(obf.items())
    deobf_fields = list(deobf.items())
    # Here, we perform sequence alignment, because new fields sometimes introduced in between old ones,
    # and sometimes some fields are removed from the data
    seq_alignment = needleman_wunsch(list(obf.values()), list(deobf.values()), comparator)
    for i, j in seq_alignment:
        if (i == None) or (j == None):
            #print("Skipping unaligned field(s) {} - {}".format(
            #    obf_fields[i] if i is not None else None,
            #    deobf_fields[j] if j is not None else None
            #))
            continue

        obf_i,obf_value = obf_fields[i]
        deobf_j,deobf_value = deobf_fields[j]

        if type(obf_value) != type(deobf_value):
            #print ("{} ({}) and {} ({}) have different types, skipping...".format(obf_i, obf_value, deobf_j, deobf_value))
            continue

        similarity = comparator(obf_value, deobf_value)

        if similarity > 0.8: # Just some random threshold
            #print ("Mapping {} ({}) to {} ({})".format(obf_i, obf_value, deobf_j, deobf_value))
            counter_for_name = votes.get(obf_i, {})
            count_for_name = counter_for_name.get(deobf_j, 0)
            counter_for_name[deobf_j] = count_for_name + 1
            votes[obf_i] = counter_for_name
            if isinstance(obf_value, list) or isinstance(obf_value, dict):
                # Go recirsive
                new_votes = map_json(obf_value, deobf_value)
                votes = merge_votes(votes, new_votes)
        else:
            pass
            #print ("{} ({}) and {} ({}) have same types but different values (similarity {}), skipping...".format(
            #    obf_i, obf_value,
            #    deobf_j, deobf_value, 
            #    similarity
            #))

    return votes

def map_list(obf, deobf):
    #print("Mapping list")
    votes = {}
    # List contains several objects of same type
    #assert(len(obf) >= len(deobf))
    if PERFORM_LIST_ALIGNMENT:
        # Here, we perform sequence alignment, because new items sometimes introduced in between old ones,
        # and sometimes some items are removed from the data
        seq_alignment = needleman_wunsch(obf, deobf, comparator)
    else:
        # Skip alignment for the sake of speed and simplicity
        seq_alignment = zip(range(len(obf)), range(len(deobf)))
    for i, j in seq_alignment:
        if (i == None) or (j == None):
            #print("Skipping unaligned item(s) {} - {}".format(
            #    obf[i] if i is not None else None,
            #    deobf[j] if j is not None else None
            #))
            continue
        item_votes = map_json(obf[i], deobf[j])
        votes = merge_votes(votes, item_votes)
    return votes

def map_json(obf, deobf):
    if isinstance(obf, list):
        return map_list(obf, deobf)
    elif isinstance(obf, dict):
        return map_dict(obf, deobf)
    else:
        return {}

def output_NT(deobf_map):
    strings = []
    for name, votes in deobf_map.items():
        item = next(iter(sorted(votes.items(), key = lambda x: -x[1])))
        strings.append((name, item[0], item[1]))
    return strings

def deobfuscate_list(obf, NT):
    return [deobfuscate_json(x, NT) for x in obf]

def deobfuscate_dict(obf, NT):
    return {NT.get(x, x): deobfuscate_json(y, NT) for x,y in obf.items()}

def deobfuscate_json(obf, NT):
    if isinstance(obf, list):
        return deobfuscate_list(obf, NT)
    elif isinstance(obf, dict):
        return deobfuscate_dict(obf, NT)
    else:
        return obf

def json_load(x):
    # JSON objects are unordered per se, but our dumper produces files where keys are ordered
    # We're going to take advantage of that
    # By default Python dictionaries (3.6 and below) don't preserve order from JSON file,
    # so we need to explicitly use OrderedDict for objects
    return json.load(open(x), object_pairs_hook=OrderedDict)

def process_file(obf_file, deobf_file):
    obf = json_load(obf_file)
    deobf = json_load(deobf_file)
    res = map_json(obf, deobf)
    NT = {x[0]: x[1] for x in output_NT(res)}
    new_json = deobfuscate_json(obf, NT)
    return json.dumps(new_json, indent = 4)

if __name__ == '__main__':
    if isdir(sys.argv[1]):
        obf_files = set([basename(x) for x in glob("{}/*.json".format(sys.argv[1]))])
        deobf_files = set([basename(x) for x in glob("{}/*.json".format(sys.argv[2]))])
        common_files = obf_files.intersection(deobf_files)
        for f in common_files:
            print(f)
            with open("OUT/{}".format(f), "wt") as io:
                io.write(
                    process_file(
                        join(sys.argv[1], f),
                        join(sys.argv[2], f)
                    )
                )
    else:
        print(process_file(sys.argv[1], sys.argv[2]))
