# Metrix

[![Tests](https://github.com/USERNAME/metrix/actions/workflows/tests.yml/badge.svg)](https://github.com/USERNAME/metrix/actions/workflows/tests.yml)

> **Note:** Replace `USERNAME` in the badge with your GitHub username.

**Metrix** is a Python CLI tool for calculating evaluation metrics for ASR (Automatic Speech Recognition) systems and other natural language processing systems. Designed as a robust and modern alternative to `sctk sclite`, Metrix offers advanced text transformation capabilities and custom adjustments.

## Main Features

- ✅ **Word Error Rate (WER)** - Robust calculation with special case handling
  - Support for stop words removal in multiple languages
  - Comparison of results with and without adjustments/stop words
- ✅ **Character Error Rate (CER)** - Character-level evaluation
- 🔄 **Adjustments System** - Replacements, equivalences, and text cleanup
- 📊 **Multiple output formats** - CSV, JSON, and detailed reports
- 🎨 **Modern CLI** - Beautiful and easy-to-use interface with Rich and Typer
- 📁 **Flexible formats** - Support for TRN files (native and sclite) and compact CSV
- ✅ **Robust validation** - UTF-8 encoding validation, file format validation, and data consistency checks

## Installation

### Requirements

- Python 3.7 or higher
- pip

### Installation Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd metrix
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) If you plan to use the stop words removal feature (`--remove-stopwords`), download the NLTK corpus:
```bash
python -c "import nltk; nltk.download('stopwords')"
```

**Note:** The stop words corpus will be automatically downloaded the first time you use `--remove-stopwords`, but it's recommended to download it manually to avoid connection issues during execution.

## Quick Start

### Basic Example - WER

```bash
python metrix.py wer \
  --hypothesis samples/example_hypothesis.trn \
  --reference samples/example_reference.trn \
  --on-screen
```

### Example with Adjustments

```bash
python metrix.py wer \
  --hypothesis samples/example_hypothesis.trn \
  --reference samples/example_reference.trn \
  --adjustments samples/example_adjustments.json \
  --output results/ \
  --on-screen
```

### Example with Compact CSV

```bash
python metrix.py wer \
  --compact-input data/input.csv \
  --output results/output
```

This will generate: `results/output.txt`, `results/output.json`, `results/output.csv`

## Available Commands

### `wer` - Word Error Rate

Calculates Word Error Rate between hypothesis and reference.

**Main options:**

| Option | Abbreviation | Description |
|--------|-------------|-------------|
| `--hypothesis` | `-h` | TRN file with hypotheses |
| `--reference` | `-r` | TRN file with references |
| `--compact-input` | `-ci` | Compact CSV file (ID, reference, hypothesis) |
| `--adjustments` | `-a` | JSON file with adjustments |
| `--output` | `-o` | Output path (folder or file) |
| `--case-sensitive` | `-cs` | Enable case-sensitive |
| `--keep-punctuation` | `-kp` | Keep punctuation |
| `--neutralize-hyphens` | `-nh` | Replace hyphens with spaces |
| `--neutralize-apostrophes` | `-na` | Remove apostrophes |
| `--on-screen` | `-os` | Display results on screen |
| `--sclite-format` | `-S` | Use sclite format in TRN files |
| `--remove-stopwords` | `-rs` | Remove stop words for specified language (e.g., 'english', 'spanish', 'portuguese') |

**Note:** Options `-h/-r` and `-ci` are mutually exclusive. You must use one or the other.

**Important note:** You must specify at least one output option: `--output` (`-o`) or `--on-screen` (`-os`). There's no point in calculating metrics if you won't see the results.

**Note about `--remove-stopwords`:**
- Requires NLTK installed
- Only available for WER (not for CER)
- Supported languages: english, spanish, portuguese, french, german, italian
- The stop words corpus will be automatically downloaded the first time it's used
- Applied after adjustments, just before metrics calculation

### `cer` - Character Error Rate

Calculates Character Error Rate between hypothesis and reference. Has the same options as `wer`, except `--adjustments` and `--remove-stopwords` (do not apply to CER).

**Important note:** You must specify at least one output option: `--output` (`-o`) or `--on-screen` (`-os`).

## File Formats

### TRN Files

Metrix supports two TRN file formats:

**Native Metrix format:**
```
audio0001.wav: this is a test sentence
audio0002.wav: want to go to the store
```

**Sclite format:**
```
this is a test sentence (audio0001.wav)
want to go to the store (audio0002.wav)
```

Use the `--sclite-format` (`-S`) option when working with sclite format files.

### Compact CSV

The compact CSV format allows you to provide hypothesis and reference in a single file:

```csv
ID,reference,hypothesis
audio0001.wav,this is a test sentence,this is a test sentence
audio0002.wav,want to go to the store,wanna go to the store
```

### Adjustments File (JSON)

The adjustments file allows you to define advanced transformations:

```json
{
  "case_sensitive": false,
  "reference_replacements": {
    "teh": "the",
    "adn": "and"
  },
  "equivalences": {
    "want_to": ["want to", "wanna"],
    "going_to": ["going to", "gonna"],
    "dont_know": ["don't know", "dunno"]
  },
  "clean_up": [
    "wow", "huh", "ugh", "uh", "ah", "eh"
  ]
}
```

**Adjustments JSON fields:**

- `case_sensitive` (boolean): Whether replacements should be case-sensitive (default: `false`)
- `reference_replacements` (object): Replacements only in the reference (error correction). Uses word boundaries.
- `equivalences` (object): Equivalences between valid forms. The first form in the list is the canonical one.
- `clean_up` (array): List of words/interjections to remove from both texts

**Application order:**
1. Basic transformations (case, punctuation, etc.)
2. `reference_replacements` (only in reference)
3. `equivalences` (in both texts)
4. `clean_up` (in both texts)
5. Stop words removal (if `--remove-stopwords` is specified, only for WER)

## Outputs

Metrix generates three types of output files when `--output` is specified:

**File naming:**
- If you specify `-o output.txt` or `-o output`: generates `output.txt`, `output.json`, `output.csv`
- If you specify `-o results/`: generates `results/output.txt`, `results/output.json`, `results/output.csv`
- Files do not include suffixes like `_report` or `_metrics`

**File types:**

1. **CSV** (`.csv`) - Metrics in tabular format
2. **JSON** (`.json`) - Metrics in JSON format
3. **Report** (`.txt`) - Detailed report with:
   - Configuration summary
   - Numerical results (with and without adjustments/stop words if applicable)
   - Sentence-by-sentence alignments

**Note:** If you use `--adjustments` or `--remove-stopwords`, the report will show metrics both with and without these transformations for comparison.

**On-screen output:**
If you use `--on-screen` (`-os`), results will be displayed directly in the terminal with beautiful formatting using Rich.

## Project Structure

```
metrix/
├── metrix.py              # Main entry point (CLI)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── src/                   # Code modules
│   ├── input_handler.py   # TRN and CSV file reading
│   ├── input_validator.py # Encoding, format and ID validation
│   ├── text_transformer.py # Basic transformations and stop words removal
│   ├── adjustments_processor.py # Adjustments processing
│   ├── metrics_calculator.py # WER/CER calculation with Jiwer
│   └── output_generator.py # Output generation
├── test/                  # Unit tests
├── samples/               # Example files
│   ├── example_hypothesis.trn
│   ├── example_reference.trn
│   ├── example_compact.csv
│   └── example_adjustments.json
└── documentation/         # Additional documentation
    ├── WER_GUIDE.md       # Technical guide for WER
    └── CER_GUIDE.md       # Technical guide for CER
```

## Implemented Metrics

### ✅ Word Error Rate (WER)

WER is the standard metric for evaluating ASR systems. Metrix calculates WER robustly:

- Special case handling (empty references)
- Integration with Jiwer for alignment and calculation
- Support for custom adjustments
- Calculation with and without adjustments for comparison
- Stop words removal support (optional)

**Formula:** `WER = (S + D + I) / N`

Where:
- S = Substitutions
- D = Deletions
- I = Insertions
- N = Total number of words in the reference

### ✅ Character Error Rate (CER)

CER evaluates performance at the character level. Useful for systems that process text without spaces or for more granular analysis.

**Formula:** `CER = (S + D + I) / N`

Where N is the total number of characters in the reference.

### 🔜 Coming Soon

- MER (Match Error Rate)
- TER (Translation Error Rate)
- DER (Diarization Error Rate)
- Precision, Recall, F1 and confusion matrix (for classification systems)

## Dependencies

- **Typer** - Modern CLI framework
- **Rich** - Beautiful terminal formatting
- **Jiwer** - WER/CER metrics calculation
- **NumPy** - Numerical operations
- **pandas** - Tabular data handling
- **Matplotlib** - Visualizations (for future features)
- **NLTK** - Stop words removal (optional, only if you use `--remove-stopwords`)

## Usage Examples

### Example 1: Basic WER calculation

```bash
python metrix.py wer \
  -h data/hypothesis.trn \
  -r data/reference.trn \
  -o results/
```

This will generate: `results/output.txt`, `results/output.json`, `results/output.csv`

### Example 2: WER with adjustments and visualization

```bash
python metrix.py wer \
  -h data/hypothesis.trn \
  -r data/reference.trn \
  -a adjustments.json \
  -os \
  -o results/
```

### Example 3: Using compact CSV

```bash
python metrix.py wer \
  -ci data/evaluation.csv \
  -o results/output
```

This will generate: `results/output.txt`, `results/output.json`, `results/output.csv`

### Example 4: WER with stop words removal

```bash
python metrix.py wer \
  -h data/hypothesis.trn \
  -r data/reference.trn \
  --remove-stopwords spanish \
  -o results/wer_spanish
```

This will generate: `results/wer_spanish.txt`, `results/wer_spanish.json`, `results/wer_spanish.csv`

### Example 5: CER with transformations

```bash
python metrix.py cer \
  -h data/hypothesis.trn \
  -r data/reference.trn \
  -cs \
  -kp \
  -o results/cer_results
```

This will generate: `results/cer_results.txt`, `results/cer_results.json`, `results/cer_results.csv`

## Technical Notes

- **Empty reference handling:** Metrix correctly handles cases where the reference is empty, calculating them manually since Jiwer doesn't support them natively.
- **Word boundaries:** All replacements in adjustments use word boundaries to avoid substring matches.
- **Transformation order:** Transformations are applied in a specific order to ensure consistent results:
  1. Basic transformations (case, punctuation, hyphens, apostrophes)
  2. Adjustments (reference_replacements, equivalences, clean_up)
  3. Stop words removal (if specified, only for WER)
  4. Metrics calculation
- **Sclite compatibility:** Metrix is compatible with the TRN file format used by sclite, facilitating migration.
- **Input validation:** Metrix validates UTF-8 encoding, file formats, ID matching, and adjustments consistency before processing.
- **Mandatory output:** You must specify at least `--output` or `--on-screen` to see the results.

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[Specify license here]

## References

- [Jiwer Documentation](https://github.com/jitsi/jiwer)
- [NIST SCTK sclite](https://github.com/usnistgov/SCTK)

## Technical Documentation

For technical details on how metrics are calculated and how transformations work:

- [`documentation/WER_GUIDE.md`](documentation/WER_GUIDE.md) - Detailed technical guide on Word Error Rate (WER)
  - Text transformation process
  - Adjustments system
  - Metrics calculation
  - Special cases
  - Jiwer integration

- [`documentation/CER_GUIDE.md`](documentation/CER_GUIDE.md) - Detailed technical guide on Character Error Rate (CER)
  - Applied transformations
  - Character-level calculation
  - Differences with WER
  - Recommended use cases

---
