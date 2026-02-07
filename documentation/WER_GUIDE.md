# Technical Guide: Word Error Rate (WER)

This guide provides technical details on how Metrix calculates Word Error Rate (WER), including the text transformation process, metrics calculation, and handling of special cases.

## Table of Contents

1. [General Process](#general-process)
2. [Text Transformations](#text-transformations)
3. [Adjustments System](#adjustments-system)
4. [WER Calculation](#wer-calculation)
5. [Special Cases](#special-cases)
6. [Jiwer Integration](#jiwer-integration)

## General Process

WER calculation in Metrix follows this flow:

```
Input (TRN/CSV) 
  ↓
File parsing
  ↓
Basic transformations (case, punctuation, hyphens, apostrophes)
  ↓
Adjustments application (if provided)
  ↓
WER calculation with Jiwer
  ↓
Special cases handling
  ↓
Metrics and alignments generation
```

## Text Transformations

### Application Order

Basic transformations are applied in the following **strict** order:

1. **Case normalization** (if `--case-sensitive` is not enabled)
   - Converts all text to lowercase using `str.lower()`
   - Applied before any other transformation

2. **Hyphen neutralization** (if `--neutralize-hyphens` is enabled)
   - Replaces hyphens with spaces: `-`, `—` (em dash), `–` (en dash) → ` `
   - **Technical reason**: Better to replace with space than remove to preserve word separation

3. **Apostrophe neutralization** (if `--neutralize-apostrophes` is enabled)
   - Removes: `'`, `'` (typographic), `"`, `"` (quotes)
   - **Technical reason**: Apostrophes can cause issues in word alignment

4. **Punctuation removal** (if `--keep-punctuation` is not enabled)
   - Removes all punctuation characters except hyphens and apostrophes (already processed)
   - Includes: `.,;:!?()[]{}` and Unicode characters: `¿¡«»„‚`
   - **Note**: Hyphens and apostrophes are handled separately because they have their own flags

5. **Space normalization**
   - Converts multiple spaces to single spaces: `\s+` → ` `
   - Removes leading and trailing spaces: `str.strip()`

### Technical Implementation

```python
# Application order in transform_text()
result = text

# 1. Case normalization
if not case_sensitive:
    result = result.lower()

# 2. Neutralize hyphens
if neutralize_hyphens:
    result = result.replace('-', ' ')
    result = result.replace('—', ' ')
    result = result.replace('–', ' ')

# 3. Neutralize apostrophes
if neutralize_apostrophes:
    result = result.replace("'", '')
    result = result.replace("'", '')
    result = result.replace('"', '')
    result = result.replace('"', '')

# 4. Remove punctuation
if not keep_punctuation:
    punctuation_to_remove = string.punctuation.replace('-', '').replace("'", '').replace('"', '')
    punctuation_to_remove += '¿¡«»„‚'
    result = ''.join(char for char in result if char not in punctuation_to_remove)

# 5. Normalize spaces
result = re.sub(r'\s+', ' ', result)
result = result.strip()
```

### Transformation Example

**Input:**
```
Reference: "Hello, World! Don't worry—it's fine."
Hypothesis: "hello world dont worry its fine"
```

**With default flags** (`case_sensitive=False`, `keep_punctuation=False`, `neutralize_hyphens=False`, `neutralize_apostrophes=False`):

```
Transformed reference: "hello world dont worry its fine"
Transformed hypothesis: "hello world dont worry its fine"
```

**With `--neutralize-hyphens` and `--neutralize-apostrophes`:**
```
Transformed reference: "hello world dont worry it s fine"
Transformed hypothesis: "hello world dont worry its fine"
```

## Adjustments System

Adjustments are applied **after** basic transformations and in this order:

### 1. Reference Replacements

- **When applied**: Only to the reference text
- **Purpose**: Correct errors in the reference
- **Implementation**: Uses word boundaries (`\b`) to avoid substring matches
- **Case sensitivity**: Controlled by the `case_sensitive` field in the JSON

```python
# Technical example
text = "teh cat"
replacements = {"teh": "the"}
# Result: "the cat"

# With word boundaries (doesn't replace in "tehater")
text = "tehater"
# Result: "tehater" (unchanged)
```

**Regex pattern used:**
```python
if case_sensitive:
    pattern = r'\b' + re.escape(search) + r'\b'
else:
    pattern = r'(?i)\b' + re.escape(search) + r'\b'  # (?i) = case-insensitive
```

### 2. Equivalences

- **When applied**: To both texts (reference and hypothesis)
- **Purpose**: Normalize valid variants to canonical form
- **Canonical form**: First word in the list in the JSON
- **Implementation**: Replaces all variants (except canonical) with the canonical form

```python
# Technical example
equivalences = {
    "want_to": ["want to", "wanna"]  # "want to" is the canonical form
}

text = "wanna go"
# Result: "want to go"
```

**Process:**
1. Canonical form is identified (first element)
2. All other variants are replaced with the canonical form
3. Word boundaries are used to avoid partial replacements

### 3. Clean Up

- **When applied**: To both texts
- **Purpose**: Remove interjections and unwanted words
- **Implementation**: Removes complete words using word boundaries

```python
# Technical example
text = "uh hello ah world"
clean_up = ["uh", "ah"]
# Result: "hello world"
```

**Post-cleanup normalization:**
- Multiple spaces are normalized to single spaces
- Leading and trailing spaces are removed

## WER Calculation

### Formula

```
WER = (S + D + I) / N
```

Where:
- **S** = Number of substitutions (incorrect words)
- **D** = Number of deletions (missing words)
- **I** = Number of insertions (extra words)
- **N** = Total number of words in the reference

### Word Accuracy

```
Word Accuracy = H / N
```

Where:
- **H** = Number of correct words (hits)
- **N** = Total number of words in the reference

### Jiwer Integration

Metrix uses `jiwer.process_words()` to:
1. Calculate Levenshtein distance at word level
2. Generate alignment between reference and hypothesis
3. Obtain metrics: hits, substitutions, deletions, insertions

**Technical code:**
```python
from jiwer import process_words

output = process_words(reference, hypothesis)

# Extracted metrics
h = output.hits           # Correct words
s = output.substitutions  # Substitutions
d = output.deletions      # Deletions
i = output.insertions     # Insertions
wer_value = output.wer    # WER calculated by Jiwer

# Word Accuracy calculated manually
word_count = len(reference.split())
word_accuracy = h / word_count if word_count > 0 else 0.0
```

### Calculation Example

**Input:**
```
Reference:  "the cat sat on the mat"
Hypothesis: "the cat sat on a mat"
```

**Process:**
1. Jiwer aligns the words
2. Identifies: `the` (correct), `cat` (correct), `sat` (correct), `on` (correct), `the` → `a` (substitution), `mat` (correct)
3. Calculates: H=5, S=1, D=0, I=0, N=6
4. WER = (1 + 0 + 0) / 6 = 0.1667 (16.67%)
5. Word Accuracy = 5 / 6 = 0.8333 (83.33%)

## Special Cases

### Empty Reference

**Case 1: Both Reference and Hypothesis empty**
```
Reference:  ""
Hypothesis: ""
```
**Result:**
- WER = 0.0 (no errors)
- Word Accuracy = 1.0 (100% correct)
- Word Count = 0

**Technical reason**: Both texts are empty, no errors to count.

**Case 2: Empty reference, non-empty hypothesis**
```
Reference:  ""
Hypothesis: "hello world"
```
**Result:**
- WER = 1.0 (100% error)
- Word Accuracy = 0.0 (0% correct)
- Insertions = 2 (number of words in hypothesis)
- Word Count = 0

**Technical reason**: Jiwer cannot handle empty references, so Metrix calculates this case manually. All words in hypothesis are insertions.

**Implementation:**
```python
if not reference.strip():
    if not hypothesis.strip():
        # Case 1: Both empty
        return {'wer': 0.0, 'word_accuracy': 1.0, ...}
    else:
        # Case 2: Only reference empty
        hyp_words = len(hypothesis.split())
        return {'wer': 1.0, 'word_accuracy': 0.0, 'insertions': hyp_words, ...}
```

## Batch Processing

When processing multiple reference/hypothesis pairs:

1. Individual metrics are calculated for each pair
2. Total values are summed:
   - `total_correct = sum(hits)`
   - `total_substitutions = sum(substitutions)`
   - `total_deletions = sum(deletions)`
   - `total_insertions = sum(insertions)`
   - `total_word_count = sum(word_counts)`

3. Aggregated metrics are calculated:
   ```python
   total_errors = total_substitutions + total_deletions + total_insertions
   aggregated_wer = total_errors / total_word_count
   aggregated_accuracy = total_correct / total_word_count
   ```

**Important note**: Aggregated metrics are not the average of individual WERs, but the WER calculated over the total word count.

## Alignments

Metrix generates detailed alignments using `jiwer.process_words().alignments`, which shows how each word in the reference aligns with words in the hypothesis (or is marked as deletion/insertion/substitution).

These alignments are included in the detailed report for sentence-by-sentence analysis.

## Technical References

- **Jiwer Documentation**: https://github.com/jitsi/jiwer
- **Levenshtein Distance**: Base algorithm for word alignment
- **NIST SCTK sclite**: Industry standard for WER calculation
