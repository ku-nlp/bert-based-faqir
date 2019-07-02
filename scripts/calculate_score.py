import argparse
from math import log2
import sys
import re
from collections import defaultdict

def format_result(result, correct_As, target_qs, target_as, correct_ABCs):
    str_result = ""
    str_result += "---------------------------\n"
    q = result["question"]
    str_result += "Q : " + q + '\n'
    class_result = "FP"
    AP = 0
    RR = 0
    DCG = 0
    Pn = [0] * (len(target_qs)+1)
    counter = 0
    for i_result in result["result"]:
        if i_result["rank"] > 10000:
            break
        str_result += "{}\t{}\t{}\n".format(
                ('#' if i_result["q_id"] in correct_As else '') +\
                        str(i_result["rank"]),
                str(i_result["question"]),
                "{:.3f}".format(i_result["score"])
                )
        if i_result["q_id"] in correct_As:
            if i_result["q_id"] in correct_ABCs[0]:
                s = 3
            elif i_result["q_id"] in correct_ABCs[1]:
                s = 2
            elif i_result["q_id"] in correct_ABCs[2]:
                s = 1
            DCG += (pow(2, s)- 1) / log2(i_result["rank"] + 1)

            counter += 1
            AP += float(counter) / float(i_result["rank"])
            for i in range(len(target_as)):
                prnk = i+1
                if i_result["rank"] <= prnk:
                    Pn[prnk] += 1.0/prnk
            if class_result == "FP":
                class_result = "top{:04d}".format(i_result["rank"])
                RR += 1.0 / i_result["rank"]

    idea_ranks = [3] * len(correct_ABCs[0]) + [2] * len(correct_ABCs[1]) + [1] * len(correct_ABCs[2])
    idea_DCG = 0
    for i, s in enumerate(idea_ranks):
        idea_DCG += (pow(2, s)- 1) / log2(i+1 + 1)
    DCG = (DCG / idea_DCG) if idea_DCG != 0 else 0
    str_result += "result : {}, correct answer : {}\n".format(
            class_result,
            "\t".join([target_qs[int(A)] for A in correct_As]) if len(correct_As) != 0 else "None")
    if len(correct_As) == 0:
        return False
    return class_result, str_result, Pn, AP/counter if counter != 0 else 0, RR, DCG

def main(args):

    target_qs = [x.split("\t")[1] for x in open(args.target_qs).read().split("\n") if len(x.strip()) != 0]
    target_as = [x.split("\t")[1] for x in open(args.target_as).read().split("\n") if len(x.strip()) != 0]
    target_num = len(target_qs)

    results = []
    q2correct_As = dict()
    q2correct_ABCs = dict()
    deno_dd = defaultdict(int)

    for line in open(args.testset):
        q, As, Bs, Cs = line.strip().split("\t")
        As = As.split(" ") if As != "None" else []
        Bs = Bs.split(" ") if Bs != "None" else []
        Cs = Cs.split(" ") if Cs != "None" else []
        q2correct_As[q] = As + Bs + Cs
        q2correct_ABCs[q] = (As, Bs, Cs)
        if len(As + Bs + Cs) == 0:
            deno_dd['NoAnswer'] += 1
        else:
            deno_dd['Exist'] += 1
        deno_dd['all'] += 1

    result = None
    stat = {"FP" : 0, "TN" : 0, "FN" : 0, "TP" : 0}
    top1_num = 0
    topn = [0] * (target_num + 1)

    query_id = -1
    conf_dict = defaultdict(int)
    result = {}
    first = True

    MPn = [0] * (target_num+1)
    MAP = 0
    MRR = 0
    MDCG = 0
    for line in open(args.search_result):
        if line[:4] == "----":
            if len(result) != 0:
                t_question = result["question"]
                if t_question not in q2correct_As:
                    result = dict()
                    continue
                result_rq = format_result(
                        result,
                        q2correct_As[t_question],
                        target_qs,
                        target_as,
                        q2correct_ABCs[t_question]
                        )
                if result_rq:
                    r, str_result, Pn, AP, RR, DCG = result_rq
                    for i in range(target_num):
                        MPn[i+1] += Pn[i+1]
                    MAP += AP
                    MRR += RR
                    MDCG += DCG
                    print(str_result, end="")
                    stat["{}".format(r if len(r) == 2 else "TP")] += 1
                    topmatch = re.match("top(\d*)", r)
                    if topmatch:
                        for i in range(target_num - int(topmatch.group(1)) + 1):
                            topn[target_num-i] += 1
            result = dict()
            continue
        q_match = re.match("Q : (.*)$", line.strip())
        if q_match:
            query_id += 1
            q = q_match.group(1).strip()
            result["question"] = q
            result["result"] = []
            continue
        if line[0].isdigit():
            rank, q, qid, score = line.split("\t")
            result["result"].append(
                    {
                        "rank" : int(rank),
                        "question" : q,
                        "q_id" : qid,
                        "score" : float(score),
                        }
                    )
            continue

    print("------------------------------")
    print("Hit@1 : {}, 3: {}, 5 : {}, all : {}".format(topn[1], topn[3], topn[5], deno_dd["Exist"]))
    print("SR@1 : {:.3f}, 3: {:.3f}, 5 : {:.3f}".format(float(topn[1])/deno_dd["Exist"], float(topn[3])/deno_dd["Exist"], float(topn[5])/deno_dd["Exist"]))
    print("P@1 : {:.3f}, 3: {:.3f}, 5 : {:.3f}".format(float(MPn[1])/deno_dd["Exist"], float(MPn[3])/deno_dd["Exist"], float(MPn[5])/deno_dd["Exist"]))
    print("MAP : {:.3f}".format(MAP/deno_dd["Exist"]), end=", ")
    print("MRR : {:.3f}".format(MRR/deno_dd["Exist"]), end=", ")
    print("MDCG : {:.3f}".format(MDCG/deno_dd["Exist"]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--testset",
            action = 'store'
            )
    parser.add_argument(
            "--search_result",
            action = 'store'
            )
    parser.add_argument(
            "--target_qs",
            action = 'store'
            )
    parser.add_argument(
            "--target_as",
            action = 'store'
            )
    args = parser.parse_args()
    main(args)
