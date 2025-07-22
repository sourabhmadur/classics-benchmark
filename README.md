# CLASSICS-EMR: Measuring Verbatim Recall of Public-Domain Classics in Large Language Models

A benchmark for quantifying how readily different LLMs emit memorized passages from a curated set of canonical novels.

## 📁 Project Structure

```
classics_benchmark/
├── src/classics_emr/           # Main package source code
│   ├── strategies/             # Prompting strategies
│   │   └── prompting_strategies.py
│   ├── models/                 # Model access and handling  
│   │   └── model_access.py
│   ├── evaluation/             # Evaluation metrics
│   │   └── evaluation_metrics.py
│   ├── database/               # Database logging
│   │   ├── supabase_logger.py
│   │   └── supabase_schema_fixed.sql
│   └── utils/                  # Utility functions
│       └── load_env.py
├── tests/                      # Test files
│   ├── test_end_to_end_pipeline.py
│   ├── test_model_access.py
│   ├── test_supabase_logger.py
│   └── test_json_paraphrasing.py
├── scripts/                    # Standalone scripts
│   ├── download_novels.py
│   ├── extract_snippets.py
│   ├── generate_control_snippets_json.py
│   └── setup_experiment.py
├── docs/                       # Documentation
│   ├── paper.md
│   ├── work.md
│   ├── supabase_setup_guide.md
│   └── pipeline_improvements_summary.md
├── data/                       # Data directories (preserved structure)
│   ├── novels/                 # Source novel texts
│   ├── snippets/               # Extracted snippets
│   └── control_snippets_json/  # Control/paraphrased snippets
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── environment_config_template.txt
└── .env                        # Environment variables (create from template)
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
cp environment_config_template.txt .env
# Edit .env with your API keys
```

### 3. Install Package in Development Mode
```bash
pip install -e .
```

### 4. Run Tests
```bash
# Test model access
python tests/test_model_access.py

# Test end-to-end pipeline
python tests/test_end_to_end_pipeline.py

# Test database logging
python tests/test_supabase_logger.py
```

## 📦 Package Usage

The package can be used programmatically:

```python
from classics_emr import (
    ModelClient, 
    PromptGenerator, 
    PromptStrategy,
    evaluate_single,
    SupabaseLogger
)

# Initialize components
client = ModelClient()
generator = PromptGenerator(random_seed=42)

# Generate prompts and evaluate responses
# ... your experiment code here
```

## 🧪 Experimental Design

### Prompting Strategies
1. **Continuation**: Provide first sentence and request continuation
2. **Location Hint**: Supply book title and first sentence  
3. **Metadata Tease**: Give author, year, and thematic keywords

### Models Tested
- DeepSeek V3 (671B parameters, open-source)
- Llama 3.1 70B Instruct (open-source)
- GPT-4o (~1T parameters, closed-source)

### Evaluation Metrics
- **EMR (Exact Match Recall)**: ≥90% character-level overlap
- **Partial Overlap Score**: Longest common subsequence ratio
- **Word Overlap Score**: Proportion of shared unique words
- **Semantic Similarity**: Cosine similarity using sentence transformers

## 📚 Data

The benchmark includes 750 snippets from 15 classic novels:
- Pride and Prejudice, Moby-Dick, Frankenstein
- Alice's Adventures in Wonderland, War and Peace
- Great Expectations, The Time Machine, Dracula
- The Picture of Dorian Gray, The Scarlet Letter
- The Call of the Wild, Adventures of Sherlock Holmes
- The Hound of the Baskervilles, Treasure Island
- A Tale of Two Cities

## 🔧 Development

### Adding New Models
1. Add model configuration to `src/classics_emr/models/model_access.py`
2. Update `AVAILABLE_MODELS` dictionary
3. Test with `python tests/test_model_access.py`

### Adding New Strategies
1. Add strategy to `PromptStrategy` enum in `src/classics_emr/strategies/prompting_strategies.py`
2. Implement corresponding `_generate_*_prompt` method
3. Update strategy descriptions

### Running Experiments
```bash
# Setup data (if not already done)
python scripts/download_novels.py
python scripts/extract_snippets.py
python scripts/generate_control_snippets_json.py

# Run experiments
python tests/test_end_to_end_pipeline.py
```

## 📄 License

This project uses public-domain texts and is available under the MIT License.

## 📧 Contact

For questions about the benchmark or to report issues, please open a GitHub issue. 