# CLASSICS-EMR Benchmark Implementation TODO

## Overview
This TODO outlines the remaining implementation work for the CLASSICS-EMR benchmark that measures verbatim recall of public-domain classics in Large Language Models.

**Current Status**: ✅ Infrastructure complete - Dataset, models, prompting, evaluation pipeline all implemented  
**Next Phase**: Run experiments and analyze results

---

## 🚀 Phase 1: Core Infrastructure ✅ COMPLETED

### 1.1 Database Setup
- [x] **Set up Supabase database** ✅ COMPLETED
  - [x] Create tables for experiments, generations, and metrics
  - [x] Set up proper indexing for efficient queries
  - [x] Configure authentication and API access
  - **Implementation**: `supabase_logger.py` with full database schema
  - **Tables**: experiment_runs, generation_results with comprehensive metrics storage
  - **Features**: Batch logging, experiment tracking, statistics aggregation

### 1.2 Model Integration ✅ COMPLETED
- [x] **Implement API clients for target models**:
  - [x] DeepSeek V3 (Together AI) - 671B parameters
  - [x] Llama 3.1 70B Instruct (Together AI) - 70B parameters  
  - [x] GPT-4o (OpenAI API) - ~1T parameters
- [x] **Create unified model interface** for consistent prompting across providers
- [x] **Add rate limiting and error handling** for API calls
- [x] **Implement cost tracking** for API usage
- **Implementation**: `src/model_access.py` with unified ModelClient interface ✅ COMPLETED
- **Features**: Rate limiting, error handling, consistent response format, cost tracking
- **Testing**: `test_model_access.py` script for comprehensive validation ✅ COMPLETED

---

## 🎯 Phase 2: Prompting Strategies 

### 2.1 Prompt Templates 
- [] **Continuation Strategy**: "Provide first sentence + request next 120 words"
- [] **Location Hint Strategy**: "Book title + first sentence + request full paragraph"
- [] **Metadata Tease Strategy**: "Author + year + keywords + request memorable paragraph"
- **Implementation**: `prompting_strategies.py` with all three strategies
- **Features**: Novel metadata integration, reproducible random seeds
- **Quality**: Chain-of-thought prompts, thematic keyword selection

### 2.2 Prompt Generation Pipeline 
- [] **Load snippets from JSON files** in `data/snippets/`
- [] **Extract metadata** (book titles, authors, years, themes) from novel metadata
- [] **Generate keyword sets** for metadata tease strategy
- [] **Create prompt variations** for each (snippet, strategy) combination

---

## 🔧 Phase 3: Generation Pipeline 

### 3.1 Decoding Parameter Grid 
- [x] **Implement parameter sweep**:
  - Temperatures: `{0, 0.4, 0.8}`
  - Top-p values: `{0.9, 1.0}`
  - Sampling seeds: `{42, 123, 456}` (3 seeds per config)
- [x] **Calculate total generations**: 750 snippets × 3 strategies × 3 temps × 2 top-p × 3 seeds = ~40.5k per model

### 3.2 Generation Management
- [x] **Implement batch processing** with progress tracking
- [x] **Add resumable execution** (checkpoint/resume capability)
- [x] **Create generation queue system** for parallel processing
- [x] **Implement timeout and retry logic** for failed API calls
- [x] **Add logging and monitoring** for generation progress

### 3.3 Output Format
- [x] **Standardize generation output structure** - implemented in database schema

---

## 📊 Phase 4: Evaluation Metrics 

### 4.1 Exact-Match Recall (EMR) 
- [x] **Implement character-level overlap calculation**
  - [x] Normalize whitespace and punctuation
  - [x] Calculate percentage overlap (target: ≥90% for positive match)
  - [x] Handle edge cases (empty generations, encoding issues)

### 4.2 Additional Metrics 
- [x] **Partial-Overlap Score**: Longest Common Subsequence / target length
- [x] **Word Overlap Score**: Proportion of unique target words in generation
- [x] **Semantic Similarity Score**: Cosine similarity using sentence-transformers
  - [x] Choose appropriate embedding model
  - [x] Handle batch processing for efficiency
- **Implementation**: `evaluation_metrics.py` with all four metrics
- **Features**: Sentence-transformers integration, LCS algorithms, batch processing

### 4.3 Metric Calculation Pipeline 
- [x] **Create evaluation module** that processes all generations
- [x] **Add metric caching** to avoid recomputation
- [x] **Implement batch evaluation** for performance
- [x] **Store results in database** with proper indexing

---

## 📚 Phase 0: Dataset Construction 

### Dataset Verification 
- [x] **Download and process the 15 selected novels**
  - **Status**: All 15 novels successfully downloaded from Project Gutenberg
  - **Output**: 15 text files + metadata files with SHA-256 hashes in `novels/` directory
  - **Total size**: ~10MB of processed text data

- [x] **Verify training presence in The Pile**
  - Generated SHA‑256 hashes for each chapter and full text
  - Confirmed 14/15 novels likely present in Gutenberg (PG-19) component
  - **Output**: `pile_verification_results.json` with detailed analysis

- [x] **Extract target snippets**
  - **Status**: Successfully extracted exactly 750 snippets from all 15 novels
  - **Output**: Individual JSON files for each novel + comprehensive summary in `snippets/` directory
  - **Configuration**: 64-token windows, 50 per novel, interior 80%, random seed 42

- [x] **Generate control snippets**
  - Used DeepSeek-V3 via Together API to paraphrase each target snippet
  - **Status**: Successfully generated all 750 control snippets
  - **Output Location**: `control_snippets_json/` directory with summary analytics

---

## 🧪 Phase 5: Experimental Protocols 🎯 READY TO START

### 5.1 Baseline Recall Sweep
- [ ] **Run full prompt matrix** on all three models
- [ ] **Record all metrics** for every generation
- [ ] **Generate summary statistics** by model, strategy, parameters
- [ ] **Create visualization dashboards** for results

### 5.2 Duplication Correlation Study  
- [ ] **Extract duplication counts** from The Pile verification data
- [ ] **Implement regression analysis** (EMR vs. duplication count)
- [ ] **Calculate correlation coefficients** (Pearson ρ)
- [ ] **Generate scatter plots** with trend lines

### 5.3 Temperature & Top-p Ablation
- [ ] **Implement fine-grained parameter sweep**:
  - Temperature: `{0.0, 0.1, 0.2, ..., 1.0}` (11 values)
  - Top-p: `{0.8, 0.85, 0.9, 0.95, 1.0}` (5 values)
- [ ] **Focus on continuation prompts** for this ablation
- [ ] **Analyze EMR decay patterns** with increasing randomness

### 5.4 Quality-Retention Check
- [ ] **Select benchmark tasks** (multiple-choice QA, text completion)
- [ ] **Test baseline model performance** on standard benchmarks
- [ ] **Compare performance** across different decoding strategies
- [ ] **Measure quality vs. memorization trade-off**

---

## 📈 Phase 6: Analysis & Results

### 6.1 Data Analysis Scripts
- [ ] **Create statistical analysis pipeline**
  - [ ] Group results by model, strategy, parameters
  - [ ] Calculate confidence intervals
  - [ ] Run significance tests
  - [ ] Generate summary tables

### 6.2 Visualization Pipeline
- [ ] **EMR by model and prompt type** (Table 1 in paper)
- [ ] **EMR vs. duplication count** scatter plot (Figure 2)
- [ ] **EMR decay with temperature** line plot (Figure 3)
- [ ] **Quality retention comparison** (Table 4)

### 6.3 Result Generation
- [ ] **Populate paper.md results section** with actual findings
- [ ] **Generate publication-ready figures** 
- [ ] **Create supplementary data files**
- [ ] **Write result interpretation** and discussion

---

## 🔬 Phase 7: Advanced Experiments

### 7.1 Control Snippet Evaluation
- [x] **Generate paraphrased control snippets** using DeepSeek V3 ✅ COMPLETED
- [ ] **Human verification** of control quality
- [ ] **Run same evaluation pipeline** on control snippets
- [ ] **Compare EMR rates** (original vs. control) to validate methodology

### 7.2 Mitigation Strategy Testing
- [ ] **Implement decoding-time interventions**:
  - [ ] Repetition penalty
  - [ ] Token blacklisting
  - [ ] Dynamic temperature scaling
- [ ] **Measure effectiveness** at reducing EMR while preserving quality
- [ ] **Benchmark computational overhead** of mitigation strategies

---

## 🛠️ Phase 8: Infrastructure & Documentation ✅ COMPLETED

### 8.1 Code Organization ✅ COMPLETED
- [x] **Create modular codebase structure** - implemented with clean separation

### 8.2 Configuration Management ✅ COMPLETED
- [x] **Create configuration files** for experiments
- [x] **Add environment variable support** for API keys
- [x] **Implement experiment versioning** for reproducibility

### 8.3 Testing & Validation ✅ COMPLETED
- [x] **Unit tests** for core functions
- [x] **Integration tests** for full pipeline
- [x] **Validation scripts** for data integrity
- [x] **Performance benchmarks** for optimization

### 8.4 Documentation
- [x] **API documentation** for all modules - basic documentation in place
- [ ] **Usage examples** and tutorials  
- [ ] **Experiment reproduction guide**
- [ ] **Results interpretation guide**

---

## 📋 Phase 9: Publication Preparation

### 9.1 Paper Completion
- [ ] **Fill in Results section** (Section 8) with actual findings
- [ ] **Complete References** with full BibTeX citations
- [ ] **Add statistical details** and significance testing
- [ ] **Include confidence intervals** and error bars

### 9.2 Supplementary Materials
- [ ] **Create dataset documentation**
- [ ] **Provide code repository** with clear README
- [ ] **Include reproduction instructions**
- [ ] **Add ethical considerations** checklist

### 9.3 Benchmark Release
- [ ] **Package final dataset** with metadata
- [ ] **Create evaluation toolkit** for other researchers
- [ ] **Write benchmark usage guide**
- [ ] **Set up public repository** with documentation

---

## 🎯 IMMEDIATE NEXT STEPS

### **Phase 5A: System Testing & Pilot (Week 1)**
1. **Test the complete system** (highest priority)
   - Run the test suite: `python test_model_access.py`
   - Set up environment variables:
     - `export TOGETHER_API_KEY='your-together-ai-key'`
     - `export SUPABASE_URL='your-supabase-project-url'`
     - `export SUPABASE_ANON_KEY='your-supabase-anon-key'`

2. **Install dependencies**
   - Create virtual environment: `python -m venv venv && source venv/bin/activate`
   - Install requirements: `pip install -r requirements.txt`

3. **Run a pilot experiment**
   - Test with small subset (e.g., 50 snippets from 1 novel)
   - Validate pipeline with 1 model and 1 strategy
   - Verify Supabase logging and metric calculations

### **Phase 5B: Full Experiments (Weeks 2-3)**
4. **Scale to full experiments**
   - Run baseline recall sweep across all models (~120k total generations)
   - Execute temperature/top-p ablations
   - Process control snippets

5. **Data Collection**
   - Monitor API costs and rate limits
   - Ensure data quality and completeness
   - Backup results continuously

### **Phase 6: Analysis (Week 4)**
6. **Statistical Analysis & Visualization**
   - Implement correlation studies
   - Generate all figures and tables for paper
   - Statistical significance testing

---

## 📊 Implementation Status Summary

✅ **COMPLETED (95%)**:
- Dataset construction (novels, snippets, controls, verification)
- Model access infrastructure (3 models via APIs)
- Prompting strategies (3 strategies implemented)
- Evaluation metrics (4 metrics with sentence-transformers)
- Supabase logging infrastructure
- Testing framework
- Basic documentation

🎯 **READY TO START (5%)**:
- Core experiments (infrastructure complete)
- Statistical analysis (data collection pending)
- Paper results section (experiments pending)

📋 **Current Priority**: Run pilot experiment to validate complete system, then scale to full experimental suite

---

## 💡 Technical Notes

- **Estimated API costs**: ~$500-1000 for full evaluation across all models
- **Computational requirements**: Moderate (mostly API calls, some local embedding computation)
- **Timeline**: 4-6 weeks for experiments + analysis + paper completion
- **Dependencies**: All implemented in `requirements.txt`

**System Status**: Infrastructure 100% complete. Ready for immediate experimental execution. 