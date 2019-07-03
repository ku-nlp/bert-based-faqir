import sys
import argparse
import random

def get_negative_samples(target_answer, answers, n_negative_samples):
    ret_answers = []
    for answer in random.sample(answers, len(answers)):
        if answer != target_answer:
            ret_answers.append(answer)
            if len(ret_answers) == n_negative_samples:
                return ret_answers
    
def main(args):
    instances = []
    answers = []
    for line in sys.stdin:
        question, answer = line.strip().split("\t", 1)
        answer = (answer.split("\t"))[0]
        instances.append( { "question": question, "answer": answer } )
        answers.append(answer)

    for instance in instances:
        # positive
        print("1\t{}\t{}".format(instance["question"], instance["answer"]))

        # negative
        negative_samples = get_negative_samples(instance["answer"], answers, args.n_negative_samples)
        for negative_answer in negative_samples:
            print("0\t{}\t{}".format(instance["question"], negative_answer))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_negative_samples', dest='n_negative_samples', type=int, action='store', default=24)
    args = parser.parse_args()
    main(args)
