from utils import gen_word_set, load_wordlist
import matplotlib.pyplot as plt
import round

TRIALS = 10000

NUMBER_OF_ROUNDS = 21

class Experiment_Stub:

    def add_round(self, x):
        pass

    def add_words(self, x):
        pass


WORDLIST = load_wordlist(f"./data/trustwords.csv")

exp = Experiment_Stub()


all_data = []
for _ in range(TRIALS):

    r = []

    words = gen_word_set(WORDLIST, exp)

    for w in words:
        r.append(int(w.isAttackRound()))

    all_data.append(r)

# tally
overall = [0] * NUMBER_OF_ROUNDS
for d in all_data:

    for i, v in enumerate(d):
        if v == 1:

            if not i == 2:
                overall[i + 1] += 1

print(overall)
plt.bar(range(NUMBER_OF_ROUNDS), overall)
plt.xticks(range(1,NUMBER_OF_ROUNDS))
plt.show()