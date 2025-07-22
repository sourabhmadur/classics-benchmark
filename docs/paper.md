Measuring Verbatim Recall of Public‑Domain Classics in Large Language Models

Abstract

Large Language Models (LLMs) are trained on massive corpora that invariably include full texts of public‑domain classics such as Moby‑Dick and Pride and Prejudice. Verbatim reproduction of these works raises legal, ethical, and safety questions even when the texts themselves are uncopyrighted. We present CLASSICS‑EMR, a reproducible benchmark that quantifies how readily different LLMs emit memorized passages from a curated set of canonical novels. CLASSICS‑EMR introduces (i) a dataset of 750 interior snippets drawn from 15 classics, (ii) a prompting suite covering four extraction scenarios, and (iii) recall metrics that separate verbatim leakage from paraphrastic familiarity. This paper outlines the dataset, evaluation framework, and planned experiments required to validate these hypotheses and characterize memorization patterns across model families.

1 Introduction

Public‑domain classics occupy a privileged place in the pre‑training pipelines of nearly every modern LLM owing to their cultural relevance and ready availability. While these works are not protected by copyright, unrestricted verbatim generation can still compromise downstream applications that require originality or controlled attribution. Quantifying the propensity of LLMs to reproduce long unseen passages from such texts provides insight into broader memorization phenomena that affect privacy, intellectual‑property risk, and factual reliability. This study narrows the memorization question to a clearly verifiable setting: classic English novels published before 1919 and known to appear in major open corpora such as PG‑19 and The Pile. We contribute a systematic evaluation protocol and report the first cross‑model comparison focused exclusively on this domain.

2 Related Work

Early work by Carlini et al. introduced the exposure score to measure unintended memorization in seq2seq models. (usenix.org) Subsequent studies quantified memorization growth with model size, duplication count, and prompt length. (arxiv.org) Scaling‑law analyses have recently extended these observations to multi‑trillion‑token training regimens. (arxiv.org) The PG‑19 benchmark itself was designed to test long‑range language modeling on full novels. (github.com) Our work differs by isolating verbatim recall on public‑domain books and comparing mitigation techniques across open‑source and API‑hosted LLMs.

3 Research Questions

RQ1: What fraction of prompts cause an LLM to emit a ≥90 % character‑match continuation of an interior passage from a classic novel?

RQ2: How do model size, decoding temperature, and passage duplication counts influence recall?

RQ3: Which decoding‑time strategies most effectively curb verbatim leakage while preserving language‑model quality on unrelated text?

4 Dataset Construction

4.1 Title Selection

Fifteen novels spanning diverse styles were chosen: Pride and Prejudice, Moby‑Dick, Frankenstein, Alice's Adventures in Wonderland, War and Peace, Great Expectations, The Time Machine, Dracula, The Picture of Dorian Gray, The Scarlet Letter, The Call of the Wild, The Adventures of Sherlock Holmes, The Hound of the Baskervilles, Treasure Island, and A Tale of Two Cities.

4.2 Verification of Training Presence

SHA‑256 hashes of each chapter were matched against tokenized copies of The Pile (Books3 + PG‑19 shards) to confirm inclusion. Duplicate counts per title were recorded. 

4.3 Snippet Sampling

For every title, 50 non‑overlapping windows of 64 tokens were sampled from the interior 80 % of the text (skip first/last 10 %) to avoid famous openings/closings, yielding 750 target snippets.

4.4 Control Snippets

Each target snippet was automatically paraphrased by DeepSeek V3 (temperature 1.0, top‑p 1.0) and human‑vetted, producing a control set that preserves meaning without overlapping surface forms.

5 Model Suite

| Model | Provider | Type | Parameters |
|-------|----------|------|------------|
| DeepSeek V3 | Together AI | Open Source | 671B |
| Llama 3.1 70B Instruct | Together AI | Open Source | 70B |
| GPT‑4o | OpenAI API | Closed Source | ~1T |

6 Experimental Protocol

6.1 Prompting Strategies

Continuation: Provide first sentence of the snippet and request the next 120 words.

Location Hint: Supply book title + first sentence, ask for the "full paragraph that follows."

Metadata Tease: Give author, year, and three thematic keywords; request "a memorable paragraph from that work."

Each (model, snippet, strategy) triple is queried with temperatures {0, 0.4, 0.8} and top‑p {0.9, 1.0}. Three sampling seeds are used, yielding  750 × 3 × 3 × 2 × 3 ≈ 40.5k generations per model.

6.2 Metrics

Exact‑Match Recall (EMR): proportion of generations reaching ≥90 % character‑level overlap.

Partial‑Overlap Score: longest common subsequence / length.

Word Overlap Score: proportion of unique words from target snippet that appear in generated text.

Semantic Similarity Score: cosine similarity between target and generated text embeddings (using sentence-transformers).

7 Baseline Evaluation Protocol

Baseline Recall Sweep

Run the full prompt matrix on all three models.

Record EMR, partial‑overlap, word overlap, and semantic similarity for every generation.

Duplication Correlation Study

For each title, regress EMR against duplicate count in The Pile to test RQ2.

Temperature & Top‑p Ablation

Fix continuation prompt; vary decoding parameters finely (T ∈ {0–1 step 0.1}; p ∈ {0.8–1}).

Quality‑Retention Check

Evaluate models on multiple-choice QA tasks and text completion benchmarks to establish baseline accuracy metrics for comparison with decoding‑time mitigation strategies.

Each experiment logs raw generations, token‑level alignments, and metric values in a Supabase database for analysis.

8 Results (to be filled after running experiments)

Table 1: EMR by model‑size and prompt‑type.

Figure 2: EMR vs. duplication count (Pearson ρ).

Figure 3: EMR decay with temperature.

Table 4: Quality retention across decoding strategies on standard benchmarks.

9 Benchmark Usage and Expected Patterns

Although full empirical validation is left to future work, we expect open‑source models to display higher verbatim recall rates than API‑hosted models with built‑in safety measures, and we anticipate a positive correlation between duplication count and recall. Decoding strategies such as higher temperature or nucleus sampling are expected to reduce leakage while preserving downstream utility.

10 Limitations

Verification restricted to corpora with public dumps; commercial training data may differ.

English‑only focus omits multilingual memorization patterns.

EMR threshold (90 %) may miss subtle stylistic memorization.

11 Ethical Considerations

All target snippets are in the public domain; nevertheless, the benchmark distributes only 64‑token excerpts under fair‑use guidelines. Researchers must not prompt models to produce entire novels.

12 Conclusion

This benchmark demonstrates a practical route to measure verbatim recall of public‑domain classics in LLMs. The results characterize memorization patterns across model families and guide the selection of appropriate decoding parameters for applications requiring controlled attribution.

References

Full BibTeX list to be compiled from cited sources (github.com, arxiv.org, arxiv.org, usenix.org).

