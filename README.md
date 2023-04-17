# Evaluating Verifiability in Generative Search Engines

This repository contains accompanying material for [Evaluating Verifiability in Generative Search Engines]().

## AllSouls

The data for `allsouls` queries can be found at [`./allsouls`](./allsouls).
See [`./allsouls/README.md`](./allsouls/README.md) for more details.

## davinci-debate

The data for the `davinci-debate` queries (debate queries generated with `text-davinci-003`) can be found at [`./davinci_debate`](./davinci_debate).
In particular, you can find the seed queries at [`./davinci_debate/seed.jsonl`](./davinci_debate/seed.jsonl),
a script for prompting `text-davinci-003` to generate new queries at [`./davinci_debate/generate_questions.py`](./davinci_debate/generate_questions.py), and 1K generated queries at [`./davinci_debate/davinci-debate-1k.jsonl`](./davinci_debate/davinci-debate-1k.jsonl).

## Human Evaluation Annotations

We've released the human evaluation annotations at [`human_evaluation_annotations.jsonl`](./human_evaluation_annotations.jsonl).

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

# References

Please consider citing our work if you found this code or our paper beneficial to your research.

```
@misc{liu-zhang-liang:2023:arxiv,
  title={Evaluating Verifiability in Generative Search Engines},
  author={Liu, Nelson F.  and  Zhang, Tianyi  and  Liang, Percy},
  note={arXiv},
  year={2023}
}
```
