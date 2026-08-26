# Implementation Plan: Google Colab Jupyter Notebooks with Serial Numbering for ACOS

**Timestamp:** 26-08-2026 21:20 WIB  
**Repository:** `haisyamalawwab/ACOS` (`ACOS-ASLI`)  
**Objective:** Create a structured suite of serialized Jupyter Notebooks (`.ipynb`) tailored for seamless execution on Google Colab (with GPU acceleration, Google Drive integration, automated dependency handling, and interactive inference) based on the **Aspect-Category-Opinion-Sentiment (ACOS) Quadruple Extraction** benchmark framework.

---

## 1. Overview & Architecture

The ACOS Quadruple Extraction framework decomposes the fine-grained sentiment analysis task into two coordinated stages:
1. **Step 1 (Aspect-Opinion Co-Extraction):** Uses `BertForQuadABSA` (BERT + linear layers + CRF sequence tagging for explicit aspect and opinion spans, with multi-label classification on the `[CLS]` token for implicit aspect and opinion detection).
2. **Bridge (Candidate Pair Generation):** Constructs Cartesian candidate pairs $(a, o)$ combining detected aspect spans and opinion spans (including `[-1, -1]` for implicit aspect/opinion).
3. **Step 2 (Category-Sentiment Classification):** Uses `CategorySentiClassification` (BERT with candidate span representations and classification heads) to predict corresponding aspect categories and sentiment polarities for each candidate pair.

---

## 2. Configuration & Compatibility Enhancements (Completed)

To ensure smooth execution across modern PyTorch and Google Colab environments:
- **`Extract-Classify-ACOS/dataset_utils.py`**: Cleaned up hardcoded server paths (`/mnt/nfs-storage-titan/...`) and redirected imports to local `bert_utils.tokenization`.
- **`Extract-Classify-ACOS/manager.py`**: Made `GPUManager` resilient for Colab single-GPU (T4/V100/A100) and CPU environments, preventing infinite loops on memory checks.
- **`Extract-Classify-ACOS/tokenized_data/get_1st_pairs.py`**: Added dynamic and flexible path handling for input predictions and output TSV generation.
- **`Extract-Classify-ACOS/modeling.py` & `bert_utils/tokenization.py`**: Updated legacy S3 URLs to official HuggingFace Hub endpoints (`https://huggingface.co/bert-base-uncased/...`).

---

## 3. Serial Numbered Notebook Suite Structure (`notebooks/`)

The following serialized notebooks are designed for Google Colab and local execution:

### 📑 `00_ACOS_Master_Pipeline_Colab.ipynb` *(Master All-in-One Notebook)*
- **Purpose:** Full end-to-end execution from zero to complete evaluation and live inference in one notebook.
- **Features:**
  - Google Drive mounting & working directory setup.
  - Automatic dependency installation (`torchcrf`, `transformers`, `huggingface_hub`, `seaborn`, `scikit-learn`).
  - BERT base model local caching.
  - Step 1 training & evaluation (`rest16` / `laptop`).
  - Candidate pair generation pipeline.
  - Step 2 training & evaluation.
  - Comprehensive metric computation across all 15 subtasks and 4 implicit/explicit subsets.
  - Interactive Custom Review Inference widget.

### 📑 `01_ACOS_Setup_and_Data_Exploration.ipynb` *(Environment & EDA)*
- **Purpose:** Environment validation and comprehensive Exploratory Data Analysis (EDA).
- **Features:**
  - Colab GPU check (`torch.cuda.get_device_name()`).
  - Download & cache pretrained `bert-base-uncased` assets (`config.json`, `pytorch_model.bin`, `vocab.txt`).
  - Dataset analysis for `Restaurant-ACOS` (`rest16`) and `Laptop-ACOS` (`laptop`).
  - Data visualization: Explicit vs Implicit aspects/opinions distribution, aspect/opinion sequence lengths, category and sentiment distribution charts.
  - Inspection of tokenized datasets and label vocabularies.

### 📑 `02_ACOS_Step1_Aspect_Opinion_Extraction.ipynb` *(Step 1: Co-Extraction)*
- **Purpose:** Train and evaluate the Aspect-Opinion extraction model.
- **Features:**
  - Architecture breakdown: `BertForQuadABSA` (BERT + CRF Sequence Tagger + Implicit Heads).
  - Training loop configuration (learning rate, warmup, batch size, epochs).
  - Evaluation on Dev and Test sets.
  - Output extraction to `pred4pipeline.txt`.

### 📑 `03_ACOS_Step1_to_Step2_Pair_Generation.ipynb` *(Pipeline Bridge)*
- **Purpose:** Generate candidate pairs from Step 1 predictions for Step 2 ingestion.
- **Features:**
  - Parsing `pred4pipeline.txt`.
  - Cartesian combination of detected aspect and opinion spans + implicit tokens `[-1, -1]`.
  - Generation of `[domain]_test_pair_1st.tsv` in `text####a_span o_span` format.
  - Yield statistics and recall analysis against gold standard pairs.

### 📑 `04_ACOS_Step2_Category_Sentiment_Classification.ipynb` *(Step 2: Classification)*
- **Purpose:** Train and evaluate the Category & Sentiment classification model.
- **Features:**
  - Architecture breakdown: `CategorySentiClassification` (Joint Category & Sentiment Multi-label Classification).
  - Training on gold candidate pairs (`[domain]_train_pair.tsv`).
  - Evaluation on predicted candidate pairs (`[domain]_test_pair_1st.tsv`) and gold pairs.
  - Saving checkpoints and prediction logs.

### 📑 `05_ACOS_Evaluation_and_Interactive_Inference.ipynb` *(Benchmark & Demo)*
- **Purpose:** End-to-end benchmark evaluation and interactive demonstration.
- **Features:**
  - Detailed performance breakdown:
    - **Subset 0:** Explicit Aspect + Explicit Opinion
    - **Subset 1:** Implicit Aspect + Explicit Opinion
    - **Subset 2:** Explicit Aspect + Implicit Opinion
    - **Subset 3:** Implicit Aspect + Implicit Opinion
    - **Subset 4:** Overall Full Quadruples
    - **15 Subtasks:** Aspect, Opinion, Category, Sentiment, Aspect-Opinion, Category-Sentiment, Quadruple, etc.
  - **Interactive Inference Demo:** Custom user input -> End-to-end extraction -> Structured pandas DataFrame & color-coded quadruple cards.

---

## 4. Verification & Validation Plan

1. **Schema & JSON Validation:** Ensure all generated `.ipynb` files comply with standard Jupyter Notebook v4 JSON schema.
2. **Syntax Checks:** Verify Python syntax across all code cells.
3. **Colab Compatibility:** Ensure all paths use relative/cross-platform structures, `%cd`, and `!pip install` statements.
4. **Execution Test:** Validate imports, dataset loading, and model architectures.
