# localgovFAQ
## qas/questions_Amagasaki.txt
Each of line contains ID of QA pair and a question of QA.

## qas/answers_in_Amagasaki.txt
Each of line contains ID of QA pair and an answer of QA.

## testset.txt
Each of line is tab-separated.
First column is user's query.
2nd, 3th, 4th columns are the QA pair IDs in relevance level A, B, C, respectively.
The IDs corresponds to ones in qas/questions_Amagasaki.txt and qas/answers_in_Amagasaki.txt.
The description about relevance levels is below.
```
A, Contain correct information.
B, Contain relevant information.
C, The topic is same as a query, but do not contain relevant information.
```

## testset_segmentation.txt
testset.txt after word segmentation by [`Juman++`]( http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?JUMAN++ )
