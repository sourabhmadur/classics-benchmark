# CLASSICS-EMR: Measuring Verbatim Recall of Public-Domain Classics in LLMs

CLASSICS-EMR is a benchmark for measuring **how often a large language model reproduces passages from classic novels word for word** when prompted. It uses 15 public-domain novels from Project Gutenberg and 750 snippets taken from the middle of each book, plus a prompting and decoding grid and a set of overlap metrics.

**Why it matters:** verbatim regurgitation is a proxy for training-data memorization, which matters for privacy, IP and attribution risk. Public-domain classics make it possible to check memorization against known ground truth without legal ambiguity, because the source texts are freely available.

> **Status: dataset built, results pending.** The corpus and the 750-snippet benchmark set are committed and reproducible. **No model generations or scores have been committed yet**, so this README reports no recall numbers. See [Roadmap](#roadmap--status).

---

## What is in this repo (verified)

| Component | File(s) | State |
|---|---|---|
| 15 Gutenberg novels + per-chapter SHA-256 metadata | `data/novels/*.txt`, `data/novels/*_metadata.json` | Committed |
| 750 benchmark snippets (50 per novel) | `data/snippets/*_snippets.json`, `data/snippets/extraction_summary.json` | Committed, reproducible |
| Pile-presence check | `data/novels/pile_verification_results.json` | Committed (sample-based, see below) |
| Downloader / snippet extractor | `scripts/download_novels.py`, `scripts/extract_snippets.py` | Committed |
| Model access (Together AI) with rate limiting + cost tracking | `src/model_access.py` | Committed |
| Supabase result logger | `src/database/supabase_logger.py`, `scripts/setup_supabase.py` | Committed |
| Prompting strategies, metric implementation, experiment runner, tests | — | **Not in repo yet** |
| Model generations / scores | — | **Not in repo yet** |

### Dataset

From `data/snippets/extraction_summary.json` and the per-novel snippet files:

- **15 novels, 750 snippets** (exactly 50 per novel), spread evenly across detected chapters.
- Snippets are aligned to sentence boundaries, with a **target length of 64 tokens** (allowed range 40-100). The median is 64 tokens. Tokens are whitespace-delimited words.
- Fixed `random_seed: 42`. Re-running `python scripts/extract_snippets.py` on the committed novels reproduces all 15 snippet files byte for byte (checked locally).
- Each snippet records `snippet_id`, `chapter_num`, character offsets, `token_count`, `text` and `first_sentence`. The first sentence is used as the prompt prefix.

Novels: Pride and Prejudice, Moby-Dick, Frankenstein, Alice's Adventures in Wonderland, War and Peace, Great Expectations, The Time Machine, Dracula, The Picture of Dorian Gray, The Scarlet Letter, The Call of the Wild, The Adventures of Sherlock Holmes, The Hound of the Baskervilles, Treasure Island, A Tale of Two Cities.

**Pile check (be careful with this one):** `pile_verification_results.json` hashed every chapter and compared the hashes against a **1,000-document sample of `NeelNanda/pile-10k`**. It found **0 full-text matches and 0 chapter matches**. The file marks 14/15 titles as `likely_in_gutenberg` using a heuristic. That is *not* confirmation that the texts appear in The Pile.

## Method

### Prompting strategies (planned, from `docs/paper.md`)
1. **Continuation**: give the snippet's first sentence and ask for the next ~120 words.
2. **Location hint**: give the book title and the first sentence, then ask for the full paragraph that follows.
3. **Metadata tease**: give the author, the year and three thematic keywords, then ask for "a memorable paragraph".

### Decoding grid
Temperature ∈ {0, 0.4, 0.8} × top-p ∈ {0.9, 1.0} × 3 seeds {42, 123, 456}. That gives 750 × 3 strategies × 18 configs = **40,500 generations per model**.

### Models
`src/model_access.py` currently wires up these models through **Together AI**: `deepseek-v3` (DeepSeek-V3), `llama-3.1-70b` (Llama 3.1 70B Instruct Turbo), `kimi-k2-instruct`, `llama-4-maverick` and `qwen3-235b`. GPT-4o appears in the paper plan but has **no client implemented yet**.

### Metric: Exact-Match Recall (EMR)

For a target snippet *t* and a model generation *g*, both normalized for whitespace and punctuation:

- A generation is an **exact match** if its character-level overlap with *t* is **≥ 90%** of the characters in *t*.
- **EMR** = (number of exact-match generations) / (total generations) for a given model × strategy × decoding setting.

Secondary metrics:
- **Partial-overlap score**: LCS(*t*, *g*) / |*t*|
- **Word-overlap score**: the fraction of *t*'s unique words that also appear in *g*
- **Semantic similarity**: cosine similarity of sentence-transformer embeddings. This separates paraphrastic familiarity from verbatim recall.

A **control set** of paraphrased snippets is planned. It is meant to show that high EMR reflects memorization rather than easy-to-guess text.

## How to run

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in TOGETHER_API_KEY (and Supabase vars if logging)
set -a; source .env; set +a  # the code reads os.environ; it does not auto-load .env

# 1. Build / rebuild the dataset (no API calls)
python scripts/download_novels.py     # fetches the 15 texts from Project Gutenberg
python scripts/extract_snippets.py    # writes data/snippets/*.json (seed 42)

# 2. Optional: create Supabase tables for logging results
python scripts/setup_supabase.py

# 3. Query a model (paid API call)
python -c "
import sys; sys.path.insert(0, 'src')
from model_access import ModelFactory, GenerationConfig
c = ModelFactory.create_client('deepseek-v3')
print(c.generate('It is a truth universally acknowledged,', GenerationConfig(temperature=0)).text)
"
```

## Roadmap / status

- [x] Corpus download + chapter hashing
- [x] 750-snippet extraction (deterministic)
- [x] Together AI client, rate limiting, cost tracking
- [x] Supabase logging schema
- [ ] Commit the prompting-strategy and metric (EMR/LCS/word/semantic) modules
- [ ] Commit an experiment runner and tests. Note: `.gitignore` currently ignores `test_*.py` and `results/`, so they are excluded from git.
- [ ] Run the baseline sweep and commit the per-model × per-strategy EMR table and figures
- [ ] Control-snippet evaluation, duplication-correlation study, temperature ablation

Known data caveats: 3 of the 750 snippets (2 in Moby-Dick, 1 in Dracula) are table-of-contents text rather than prose. Chapter detection for Treasure Island found only 3 chapters.

See [`docs/paper.md`](docs/paper.md) for the full research design and [`docs/TODO.md`](docs/TODO.md) for the task list.

## License

No license file yet. The source novels are public domain (Project Gutenberg).
