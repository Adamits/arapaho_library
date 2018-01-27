
examples = text.examples

from collections import Counter

lines = [line.strip() for line in open('./data/pos_tags.txt') if "\t" in line]
wordtags = []
tags = ["<s>"]
unigrams = []

for index, l in enumerate(lines):
    # store previous tag
    prev_tag = lines[index - 1].split("\t")[1] if index > 0 else "<s>"
    # check if end sentence
    if prev_tag == ".":
        tags.extend(("</s>", "<s>"))
        # Append extra tags to unigrams list
        unigrams.extend([' ', "</s>", ' ', "<s>"])
        wordtags.extend([(' ', "</s>"), (' ', "<s>")])
    unigrams.extend([l.split("\t")[0], l.split("\t")[1]])
    tags.append(l.split("\t")[1])
    wordtags.append((l.split("\t")[0],l.split("\t")[1]))

# Add final end-sentence tag
tags.append("</s>")

# get the counts
emit_counts = Counter(wordtags)
trans_counts = Counter(zip(tags, tags[1:]))
unigram_counts = Counter(unigrams)

def viterbi(input_list, trans_counts, emit_counts):
    # Pad input_list with blank spaces
    input_list.insert(0, ' ')
    input_list.append(' ')
    trellis = []
    unique_tags = set(tags)
    hidden_pos = []

    # Loop over the input of words
    for index, obs in enumerate(input_list):
        time_step_dict = {}
        # loop over the 'hidden state' tags
        for tag in unique_tags:
            prev_tags_and_probs = {}
            probs_and_prev_tags = {}
            # loop over same to check every permutation of current_tag, prev_tag
            for prev_tag in unique_tags:
                # store each prob for current tag given each previous tag, * previous tag's running prob
                if index < 1:
                    # Fix prob of first state to be 1
                    temp_prob = 1
                else:
                    temp_prob = (float(trans_counts[(prev_tag, tag)]) / (float(unigram_counts[(prev_tag)]) + 0.5)) * trellis[index - 1][prev_tag]["prob"]
                prev_tags_and_probs[prev_tag] = temp_prob
                # store reverse dict for lookup
                probs_and_prev_tags[temp_prob] = prev_tag

            # Find tag for max_prob, and multiply emission prob by max_prob to get a final probability
            max_prob_initial = max(prev_tags_and_probs.values())
            max_prob = (float(emit_counts[(obs, tag)]) / (float(unigram_counts[obs]) + 0.5)) * max_prob_initial
            time_step_dict[tag] = {"prob": max_prob, "prev_tag": probs_and_prev_tags[max_prob_initial]}

        # put the dict of max_probs for thetags in the trellis at the next time_step
        trellis.append(time_step_dict)

    # Find the max prob for the state of the final time step
    final_prob = max(trellis[-1][tag]["prob"] for tag in trellis[-1])

    for tag in trellis[-1]:
        if trellis[-1][tag]["prob"] == final_prob:
            hidden_pos.append(tag)
    # Iterate over trellis backwards, to perform backtrace of tags
    trellis.reverse()
    for index, tags_dict in enumerate(trellis):
        if  tags_dict[hidden_pos[0]]['prev_tag'] == "<s>":
            break
        else:
            hidden_pos.insert(0, tags_dict[hidden_pos[0]]['prev_tag'])

    return hidden_pos

print examples[20].get_mb_list()
print viterbi(examples[20].get_mb_list(), trans_counts, emit_counts)