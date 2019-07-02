import sys
import argparse

def read_qaid_file(qa_id_file):
    qaids = []
    with open(qa_id_file, mode='r', encoding='utf-8') as file:
        for line in file:
            try:
                qaid, _ = line.strip().split("\t")
            except Exception as e:
                qaid = line.strip()
            qaids.append(qaid)
    return qaids

def read_question_file(question_file):
    questions = []
    with open(question_file, mode='r', encoding='utf-8') as file:
        for line in file:
            try:
                _, question = line.strip().split("\t")
            except Exception as e:
                question = line.strip()
                
            questions.append(question)
    
    return questions

def read_answer_file(answer_file):
    answers = []
    with open(answer_file, mode='r', encoding='utf-8') as file:
        for line in file:
            try:
                _, answer = line.strip().split("\t")
            except Exception as e:
                answer = line.strip()
            
            answers.append(answer)
    
    return answers

def main(args):
    answers = read_answer_file(args.answer_file)
    
    with open(args.test_set_file, mode='r', encoding='utf-8') as file:
        for line in file:
            if args.new_format is True:
                question, answer_A, answer_B, answer_C = line.strip().split("\t")
                for answer in answers:
                    print("0\t{}\t{}".format(question, answer))
            else:
                category, question, gold_answer_id_string = line.strip().split("\t", 2)
                gold_answer_ids = gold_answer_id_string.split("\t")

                # 正解が複数ある場合をスキップ
                if args.all is False and category == "1" and len(gold_answer_ids) > 1:
                    continue

                for answer in answers:
                    print("0\t{}\t{}".format(question, answer))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_set_file', dest='test_set_file', type=str, action='store', default=None)
    parser.add_argument('--answer_file', dest='answer_file', type=str, action='store', default=None)
    parser.add_argument('--all', dest='all', action='store_true', default=False)
    parser.add_argument('--new_format', dest='new_format', action='store_true', default=False)
    args = parser.parse_args()
    
    main(args)
