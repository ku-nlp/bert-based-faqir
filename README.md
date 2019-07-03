# bert-based-faqir
FAQ retrieval system that considers the similarity between a user’s query and a question as well as the relevance between the query and an answer.
The detail is on our paper([`arxiv`](https://arxiv.org/abs/1905.02851)).

## Requirements
```
tensorflow >= 1.11.0
```
## Usage
Download the BERT repository, BERT Japanese pre-trained model, QA pairs in Amagasaki City FAQ, testset(localgovFAQ) and samples of prediction results.
```shell
./download.sh
```
The data structure is below.
```shell
data
├── bert : BERT original repository
├── Japanese_L-12_H-768_A-12_E-30_BPE : BERT Japanese pre-trained model
└── localgovfaq
    ├── qas : QA pairs in Amagasaki City FAQ
    ├── testset_segmentation.txt : testset for evaluation
    └── samples : retrieval results by TSUBAKI, BERT, and Joint model

```
And we should add the task class to run_classifier.py in the original BERT repository as below.
```python
class CQAProcessor(DataProcessor):
  """Processor for the CoLA data set (GLUE version)."""

  def get_train_examples(self, data_dir):
    """See base class."""
    return self._create_examples(
        self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")

  def get_dev_examples(self, data_dir):
    """See base class."""
    return self._create_examples(
        self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")

  def get_test_examples(self, data_dir):
    """See base class."""
    return self._create_examples(
        self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")

  def get_labels(self):
    """See base class."""
    return ["0", "1"]

  def _create_examples(self, lines, set_type):
    """Creates examples for the training and dev sets."""
    examples = []
    for (i, line) in enumerate(lines):
      guid = "%s-%s" % (set_type, i)
      text_a = tokenization.convert_to_unicode(line[1])
      text_b = tokenization.convert_to_unicode(line[2])
      label = tokenization.convert_to_unicode(line[0])
      examples.append(
          InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
    return examples

def main(_):
  tf.logging.set_verbosity(tf.logging.INFO)

  processors = {
      "cqa": CQAProcessor,
  }
```

**For Japanese, we need to comment out `text = self._tokenize_chinese_chars(text)` in tokenization.py in BERT repository.**

Finetune and evaluate.
```shell
make -f Makefile.generate_dataset --OUTPUT_DIR=/path/to/data_dir
make -f Makefile.run_classifier --BERT_DATA_DIR=/path/to/data_dir --OUTPUT_DIR=/path/to/somewhere
```

The result example is below.
```
Hit@1 : 381, 3: 524, 5 : 578, all : 784
SR@1 : 0.486, 3: 0.668, 5 : 0.737
P@1 : 0.486, 3: 0.349, 5 : 0.286
MAP : 0.550, MRR : 0.596, MDCG : 0.524
```

### TSUBAKI + BERT

TSUBAKI is the open search engine based on BM25 ([`paper`]( http://nlp.ist.i.kyoto-u.ac.jp/local/pubdb/skeiji/IJCNLP2008/ijcnlp08.pdf ), [`github`]( https://github.com/ku-nlp/TSUBAKI ) ).
We can get the higher score by using both TSUBAKI and BERT.

We can evaluate the joint model by the below command.
```shell
python scripts/merge_tsubaki_bert_results.py --bert localgovfaq/samples/bert.txt \
    --tsubaki localgovfaq/samples/tsubaki.txt \
    --threshold 0.3 \
    --tsubaki_ratio 10 > /path/to/resultfile.txt
python scripts/calculate_score.py --testset data/localgovfaq/testset_segmentation.txt \
    --target_qs data/localgovfaq/qas/questions_in_Amagasaki.txt \
    --target_as data/localgovfaq/qas/answers_in_Amagasaki.txt \
    --search_result /path/to/resultfile.txt | tail -n 4
```
In this command, the results pre-computed by TSUBAKI and BERT are used.

The result example is below.
```
Hit@1 : 498, 3: 611, 5 : 661, all : 784
SR@1 : 0.635, 3: 0.779, 5 : 0.843
P@1 : 0.635, 3: 0.446, 5 : 0.360
MAP : 0.660, MRR : 0.720, MDCG : 0.625
```

## Reference
Wataru Sakata(LINE Corporation), Tomohide Shibata(Kyoto University), Ribeka Tanaka(Kyoto University) and Sadao Kurohashi(Kyoto University):
FAQ Retrieval using Query-Question Similarity and BERT-Based Query-Answer Relevance,
Proceedings of SIGIR2019: 42nd Intl ACM SIGIR Conference on Research and Development in Information Retrieval,  (2019.7).[`arxiv`](https://arxiv.org/abs/1905.02851)
