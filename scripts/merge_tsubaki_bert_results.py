import re
import sys
import argparse
def main(args):
    tsubaki_list = []
    dd = dict()
    titles = dict()
    for line in open(args.tsubaki): 
        if "----" in line:
            if len(dd) == 0:
                continue
            tsubaki_list.append(dd)
            dd = {}
            continue
        q_match = re.match("Q : (.*)$", line.strip())
        if q_match:
            q = q_match.group(1).strip()
            dd["question"] = q
            dd["result"] = {}
            continue
        rnk_match = re.match("(\d*)\t", line.strip())
        if rnk_match:
            if int(rnk_match.group(1)) > 10:
                continue
        _, title, t_id, x = line.strip().split("\t")
        if float(x) < args.threshold:
            dd["result"][t_id] = 1 * float(x)
        else:
            dd["result"][t_id] = 322121000 + float(x)
        titles[t_id] = title

    result = None
    ith_q = -1
    tids = set()
    for line in open(args.bert):
        if "----" in line:
            if result == None:
                pass
            elif len(result) >= 0:
                print(

                    "\n".join(
                        [
                            "{}".format(i+1) + "\t" + x[0] + "\t" + x[1] + "\t" + "{:.3f}".format(x[2]) 
                            for i, x in enumerate(sorted(result, key = lambda x : x[2])[::-1][:])
                            ]
                            )
                    )
            result = []
            tids = set()
            ith_q += 1
            print(line.strip())
            counter = 0
            continue
        q_match = re.match("Q : (.*)$", line.strip())
        if q_match:
            q = q_match.group(1).strip()
            print(line.strip())
            continue
        rank, tq, tid, score = line.strip().split("\t")
        tq = tq.strip()
        score = float(score)
        if counter >= 10:
            result.append((tq, tid, score))
            continue
        if tid in tsubaki_list[ith_q]["result"]:
            result.append((tq, tid, score + args.tsubaki_ratio * tsubaki_list[ith_q]["result"][tid]))
            tids.add(tid)
        else:
            result.append((tq, tid, score))
            tids.add(tid)
        counter += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--threshold",
            type = float,
            action = 'store'
            )
    parser.add_argument(
            "--tsubaki_ratio",
            type = float,
            action = 'store',
            default = 1.0
            )
    parser.add_argument(
            "--bert",
            type = str,
            action = 'store',
            )
    parser.add_argument(
            "--tsubaki",
            type = str,
            action = 'store',
            )
    args = parser.parse_args()
    main(args)
