# Evaluating Verifiability in Generative Search Engines

This repository contains accompanying material for [Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848).

## AllSouls

The data for `allsouls` queries can be found at [`./allsouls`](./allsouls).
See [`./allsouls/README.md`](./allsouls/README.md) for more details.

## davinci-debate

The data for the `davinci-debate` queries (debate queries generated with `text-davinci-003`) can be found at [`./davinci_debate`](./davinci_debate).
In particular, you can find the seed queries at [`./davinci_debate/seed.jsonl`](./davinci_debate/seed.jsonl),
a script for prompting `text-davinci-003` to generate new queries at [`./davinci_debate/generate_questions.py`](./davinci_debate/generate_questions.py), and 1K generated queries at [`./davinci_debate/davinci-debate-1k.jsonl`](./davinci_debate/davinci-debate-1k.jsonl).

## Verifiability Judgments

We've released a dataset of verifiability judgments, which we hope will be useful for
future work in developing automated metrics for verifiability judgement, document-level NLI, or other
related topics.

We split the data into train, development, and testing (80%/10%/10%). The data is split such that the same query does not appear in multiple splits. Each data file is a gzipped file of new-line separated JSON objects. The files are at:

- [verifiability_judgments/verifiability_judgments_train.jsonl.gz](./verifiability_judgments/verifiability_judgments_train.jsonl.gz)
- [verifiability_judgments/verifiability_judgments_dev.jsonl.gz](./verifiability_judgments/verifiability_judgments_dev.jsonl.gz)
- [verifiability_judgments/verifiability_judgments_test.jsonl.gz](./verifiability_judgments/verifiability_judgments_test.jsonl.gz)

There are 8834 training examples, 1106 dev examples, and 1097 test examples. The
label distribution is as follows:

- Train: `{'complete_support': 6415, 'partial_support': 1552, 'no_support': 867}`
- Dev: `{'complete_support': 830, 'partial_support': 165, 'no_support': 111}`
- Test: `{'complete_support': 797, 'partial_support': 183, 'no_support': 117}`

Each JSON object has the following fields:

- `query`: `str` with the original user query
- `response`: `str` with the complete system response
- `statement`: `str` with the statement to make the verification judgment on
- `source_title`: `Optional[str]` HTML `<title>` of the cited webpage, if one exists.
- `source_content_title`: `Optional[str]` extracted title from the content of the cited webpage.
- `source_date`: `Optional[str]` with the article's date, if one is provided. 
- `source_author`: `Optional[str]` with the article's author, if one is provided.
- `source_text`: `str` with the article's text, with formatting.
- `source_raw_text`: `str` with the article's text, without formatting.
- `source_supports_statement`: `str` verifiability judgment provided by the annotator. One of `complete_support`, `partial_support`, or `no_support`.
- `source_localized_evidence`: `Optional[str]` copy-and-pasted portions of the target webpage that annotators used to justify their verifiability judgement. Annotators were instructed to set the minimal set of sentences necessary to support their judgment, with each sentence on different lines. The evidence is not guaranteed to exactly appear in the `source_text`, since they may have selected portions of the page that were not preserved by our HTML-to-text pipeline.
- `source_url`: `str` URL cited webpage.

### Converting HTML to text

To extract text from HTML pages,  we first used [`single-filez`](https://github.com/gildas-lormeau/single-filez-cli) to download cited webpages and their associated assets (e.g., CSS and images). Then, we use the [Chrome DOM Distiller](https://github.com/chromium/dom-distiller) to extract the "readable" portion of the page (this is the view that appears when you use "Reader Mode" in the Chrome browswer). Finally, we used [Trafilatura](https://trafilatura.readthedocs.io/en/latest/) to extract the text from the DOM-distilled HTML.

## Human Evaluation Annotations
We've released the human evaluation annotations at
[`human_evaluation_annotations.jsonl`](./human_evaluation_annotations.jsonl).

Each line of `human_evaluation_annotations.jsonl` contains a query-response pair with a human evaluation annotation.
The format of the data is described by the following Python dataclasses:

``` python
class AnnotatedQueryResponse:
    id: str  # ID for this annotated query-response pair. Format is '<query_hash>-<system_name>'.
    query: str  # Input user query.
    response: str  # Generative search engine response.
    split: SplitEnum  # The data split that this query belongs to.
    system_name: SystemNameEnum  # Name of the generative search engine that provided the response.
    citations: List[Citation]  # List of citations in the response.
    statements_to_citation_texts: Dict[str, List[str]]  # Mapping between statements in the response (sentences, in this work) to associated citation texts.
    annotation: Annotation  # Human evaluation annotation.

class SplitEnum(str, Enum):
    allsouls = "allsouls"
    davinci_debate = "davinci_debate"
    wikihow_keywords = "wikihow_keywords"
    eli5_kilt = "eli5_kilt"
    eli5_live = "eli5_live"
    nq_list_with_short_answer = "nq_list_with_short_answer"
    nq_list_without_short_answer = "nq_list_without_short_answer"
    nq_paragraph_with_short_answer = "nq_paragraph_with_short_answer"
    nq_paragraph_without_short_answer = "nq_paragraph_without_short_answer"
    nq_table_with_short_answer = "nq_table_with_short_answer"
    nq_table_without_short_answer = "nq_table_without_short_answer"
    nq_no_long_answer = "nq_no_long_answer"

class SystemNameEnum(str, Enum):
    bing_chat = "bing_chat"
    neeva = "neeva"
    perplexity = "perplexity"
    you = "you"

class Citation:
    text: str  # The text of the citation in the response, e.g., [1]
    start_index: int  # Character start index of the citation text in the response
    end_index: int  # Character end index of the citation text in the response
    link_target: str  # Link that this citation points to.

class Annotation:
    fluency: LikertRatingEnum  # Likert rating for fluency.
    perceived_utility: LikertRatingEnum  # Likert rating for perceived utility.
    statement_to_annotation: Dict[str, StatementAnnotation]  # Mapping between statements in the response (sentences in this work) to human evaluation judgments.

class LikertRatingEnum(str, Enum):
    """
    Possible Likert ratings.
    """
    one = "Strongly Disagree"
    two = "Disagree"
    three = "Neutral"
    four = "Agree"
    five = "Strongly Agree"

class StatementAnnotation:
    statement_is_verification_worthy: bool  # Whether the statement is verification-worthy (i.e., a statement about the external world).
    statement_supported: Optional[StatementSupportedEnum]  # Whether or not the statement is supported by the union of its citations. `null` if `statement_is_verification_worthy` is False
    citation_annotations: Optional[List[StatementCitationAnnotation]]  # Judgments for each citation associated with this statement. `null` if `statement_is_verification_worthy` is False

class StatementSupportedEnum(str, Enum):
    """
    Possible values for `statement_supported` in `StatementAnnotation`.
    `contradict` and `false` are counted as "no support", and `yes` is counted as full support.
    """
    true = "Yes"
    false = "No"
    contradict = "Citations Contradict Each Other"

class StatementCitationAnnotation:
    citation_text: str  # The text of the evaluated citation.
    citation_supports: CitationSupportsEnum  # Whether or not this citation supports its associated statement. 
    evidence: Optional[str]  # Annotator-provided evidence for the judgement. `null` if `citation_supports` is not complete or partial.

class CitationSupportsEnum(str, Enum):
    """
    Possible values for `citation_supports` in `StatementCitationAnnotation`.
    `complete` is counted as full support, `partial` is counted as partial support,
    and all other options are considered no support.
    """
    complete = "Citation Completely Supports Statement"
    partial = "Citation Partially Supports Statement"
    none = "Citation Provides No Support for Statement"
    inaccessible = "Citation Inaccessible"
    contradict = "Citation Completely Supports but Also Refutes Statement"
    unclear = "Statement is Unclear, Can't Make Judgment"
```

## Bing + OpenAI minimal baseline

We've released code for an extremely minimal baseline that uses
`text-davinci-003` to answer input queries from retrieved Bing Search results.
We found playing with this to be pretty useful for getting intuition about how
models might be using in-context retrieved documents.

See [`predict_bing_openai.py`](./predict_bing_openai.py) for more information. To run, use:

```sh
python scripts/predict_bing_openai.py \
    --openai-api-key '<put your openai API key here>' \
    --bing-api-key '<put your bing API key here>' \
    --query 'what is the difference between llamas and alpacas?'
```

## References

Please consider citing our work if you found this code or our paper beneficial to your research.

```
@misc{liu-zhang-liang:2023:arxiv,
  author    = {Nelson F. Liu  and  Tianyi Zhang  and  Percy Liang},
  title     = {Evaluating Verifiability in Generative Search Engines},
  note      = {arXiv:2304.09848},
  year      = {2023}
}
```
