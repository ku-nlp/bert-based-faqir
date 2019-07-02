import sys
import argparse
import numpy

def print_result(question, answers, scores, questions,
                 topk_num=10):
    scores = numpy.array(scores)
    topk = numpy.argsort(scores)[-1::-1][:topk_num]
    print("Q : {}".format(question))
    for k, ind in enumerate(topk, start=1):
        print("{}\t{}\t{}\t{:.3f}".format(k, questions[ind], ind, scores[ind]))
        if k == topk_num:
            break
    print("---------------------------")

def read_question_file(question_file):
    questions = []
    with open(question_file, mode='r', encoding='utf-8') as file:
        for line in file:
            _, question = line.strip().split("\t")
            questions.append(question)
    
    return questions

def get_idmapping(test_set_file):
    idmapping = {}
    with open(test_set_file, mode='r', encoding='utf-8') as file:
        all, sub = 0, 0
        for line in file:
            category, question, gold_answer_id_string = line.strip().split("\t", 2)
            gold_answer_ids = gold_answer_id_string.split("\t")

            idmapping[sub] = all
            print(sub, all) 
            
            all += 1
            
            # 正解が複数ある場合をスキップ
            if category == "1" and len(gold_answer_ids) > 1:
                continue
            
            sub += 1

    return idmapping

def main(args):
    questions = None
    if args.question_file is not None:
        questions = read_question_file(args.question_file)

    print("---------------------------")        
    answers, scores = [], []
    pre_question = None
    for line in sys.stdin:
        # 0.9999597	4.0246192e-05	0	お 笑い に 関する 施設 など は あり ます か	■ 市 に は 乳幼児 ...
        _, score, _, question, answer = line.strip().split("\t")
        
        if pre_question is not None and pre_question != question:
            print_result(pre_question, answers, scores, questions)
            answers, scores = [], []

        scores.append(float(score))
        answers.append(answer)
            
        pre_question = question
    print_result(pre_question, answers, scores, questions)
        
# paste /larch/shibata/bert/CQA/test_output/test_results.tsv /larch/shibata/bert/CQA/test_output/../181112/data/test.tsv | python generate_evaluation_file.py
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_set_file', dest='test_set_file', type=str, action='store', default=None)
    parser.add_argument('--question_file', dest='question_file', type=str, action='store', default=None)    
    args = parser.parse_args()
    main(args)
