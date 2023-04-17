#!/usr/bin/env python3
"""Given a file of seed questions, generate more questions.

Running:

```
python -u ./davinci_debate/generate_questions.py \
    --input-path davinci_debate/seed.jsonl \
    --openai-api-key 'paste api key here' \
    --output-path davinci_debate/generated_questions.jsonl
```
"""
import argparse
import json
import logging
import os
import random
import sys
import time

import openai
from tqdm import tqdm
from unidecode import unidecode

logger = logging.getLogger(__name__)


def main(input_path, num_examples, openai_api_key, sleep, output_path):
    openai.api_key = openai_api_key
    already_generated_queries = set()
    if os.path.exists(output_path):
        logger.info(f"Reading already-generated queries from {output_path}")
        with open(output_path) as f:
            for line in f:
                already_generated_queries.add(json.loads(line)["query"])
        logger.info(f"Read {len(already_generated_queries)} queries from {output_path}")

    seed_queries = set()
    with open(input_path) as fin:
        for line in tqdm(fin):
            seed_queries.add(json.loads(line)["query"])
    logger.info(f"Read {len(seed_queries)} seed queries from {input_path}")

    num_examples_to_generate = num_examples - len(already_generated_queries)
    if num_examples_to_generate < 1:
        logger.info(
            f"Already generated {len(already_generated_queries)} examples, "
            f"which is equal to or more than desired number of examples {num_examples}"
        )
        return

    logger.info(f"Generating {num_examples_to_generate} queries")
    num_generated = 0
    with open(output_path, "a") as fout, tqdm(total=num_examples_to_generate) as pbar:
        while num_generated < num_examples_to_generate:
            generated_query = generate_query(seed_queries)
            if not generated_query.endswith("?"):
                logger.info(f"generated query {generated_query} does not end with ?")
                continue
            if "should" not in generated_query.lower():
                logger.info(f"generated query {generated_query} does not contain 'should'")
                continue
            if len(generated_query) <= 15:
                logger.info(
                    f"generated query {generated_query} is equal to or shorter than 15 chars."
                )
                continue

            if (
                generated_query not in already_generated_queries
                and generated_query not in seed_queries
            ):
                fout.write(json.dumps({"query": generated_query}) + "\n")
                already_generated_queries.add(generated_query)
                num_generated += 1
                pbar.update(1)
            time.sleep(sleep)


def generate_query(seed_queries, seed_queries_to_sample=10):
    sampled_seed_queries = random.sample(seed_queries, k=seed_queries_to_sample)
    prompt_formatted_sampled_seed_queries = [f"Question: {query}" for query in sampled_seed_queries]

    prompt_lines = [
        (
            "An intelligent computer system is constructed. It is friendly and safe. "
            "The system generates debate questions that can be used to have interesting "
            "discussions between people. The questions the system came up with are:"
        ),
        "",
        *prompt_formatted_sampled_seed_queries,
        "Question:",
    ]
    prompt = "\n".join(prompt_lines)
    completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
    completion_text = unidecode(completion.choices[0].text.lstrip().split("\n")[0])
    return completion_text


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(module)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", help="Path to file of seed queries.", required=True)
    parser.add_argument("--num-examples", help="Number of queries to generate", default=1000)
    parser.add_argument("--sleep", type=float, default=10, help="Time to sleep between queries")
    parser.add_argument(
        "--openai-api-key",
        type=str,
        required=True,
        help="OpenAI API Key",
    )
    parser.add_argument("--output-path", help="Path to write output JSONL", required=True)
    args = parser.parse_args()

    logger.info("running %s", " ".join(sys.argv))
    main(args.input_path, args.num_examples, args.openai_api_key, args.sleep, args.output_path)
    logger.info("finished running %s", sys.argv[0])
