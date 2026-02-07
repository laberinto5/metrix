# Technical Guide: Character Error Rate (CER)

This guide provides technical details on how Metrix calculates Character Error Rate (CER), including the text transformation process and character-level metrics calculation.

## Table of Contents

1. [General Process](#general-process)
2. [Text Transformations](#text-transformations)
3. [CER Calculation](#cer-calculation)
4. [Special Cases](#special-cases)
5. [Differences with WER](#differences-with-wer)

## General Process

CER calculation in Metrix follows this flow:

```
Input (TRN/CSV) 
  ↓
File parsing
  ↓
Basic transformations (case, punctuation, hyphens, apostrophes)
  ↓
CER calculation with Jiwer (at character level)
  ↓
Special cases handling
  ↓
Metrics and alignments generation
```

**Important note**: CER **does not** use adjustments (replacements, equivalences, clean_up). It only applies basic transformations.

## Text Transformations

CER uses the same basic transformations as WER, applied in the same order:

1. **Case normalization** (if `--case-sensitive` is not enabled)
2. **Hyphen neutralization** (if `--neutralize-hyphens` is enabled)
3. **Apostrophe neutralization** (if `--neutralize-apostrophes` is enabled)
4. **Punctuation removal** (if `--keep-punctuation` is not enabled)
5. **Space normalization**

See [WER_GUIDE.md](./WER_GUIDE.md#text-transformations) for complete details on transformations.

### Key Difference

Unlike WER, CER evaluates at **character** level instead of words. This means:

- Spaces are also considered characters
- Alignment is done character by character
- Useful for systems that process text without spaces or for more granular analysis

## CER Calculation

### Formula

```
CER = (S + D + I) / N
```

Where:
- **S** = Number of character substitutions
- **D** = Number of character deletions
- **I** = Number of character insertions
- **N** = Total number of characters in the reference

### Character Accuracy

```
Character Accuracy = H / N
```

Where:
- **H** = Number of correct characters (hits)
- **N** = Total number of characters in the reference

### Jiwer Integration

Metrix uses `jiwer.process_characters()` to:
1. Calculate Levenshtein distance at character level
2. Generate character-by-character alignment
3. Obtain metrics: hits, substitutions, deletions, insertions

**Technical code:**
```python
from jiwer import process_characters

output = process_characters(reference, hypothesis)

# Extracted metrics
h = output.hits           # Correct characters
s = output.substitutions  # Character substitutions
d = output.deletions      # Character deletions
i = output.insertions     # Character insertions
cer_value = output.cer     # CER calculated by Jiwer

# Character Accuracy calculated manually
character_count = len(reference)
character_accuracy = h / character_count if character_count > 0 else 0.0
```

### Calculation Example

**Input:**
```
Reference:  "hello"
Hypothesis: "hallo"
```

**Process:**
1. Jiwer aligns character by character:
   - `h` (correct)
   - `e` → `a` (substitution)
   - `l` (correct)
   - `l` (correct)
   - `o` (correct)

2. Calculates: H=4, S=1, D=0, I=0, N=5
3. CER = (1 + 0 + 0) / 5 = 0.2 (20%)
4. Character Accuracy = 4 / 5 = 0.8 (80%)

**Alignment visualization:**
```
Reference:  h e l l o
Hypothesis: h a l l o
            ✓ ✗ ✓ ✓ ✓
```

## Special Cases

### Empty Reference

**Case 1: Both Reference and Hypothesis empty**
```
Reference:  ""
Hypothesis: ""
```
**Result:**
- CER = 0.0 (no errors)
- Character Accuracy = 1.0 (100% correct)
- Character Count = 0

**Case 2: Empty reference, non-empty hypothesis**
```
Reference:  ""
Hypothesis: "hello"
```
**Result:**
- CER = 1.0 (100% error)
- Character Accuracy = 0.0 (0% correct)
- Insertions = 5 (number of characters in hypothesis)
- Character Count = 0

**Implementation:**
```python
if not reference.strip():
    if not hypothesis.strip():
        # Case 1: Both empty
        return {'cer': 0.0, 'character_accuracy': 1.0, ...}
    else:
        # Case 2: Only reference empty
        hyp_chars = len(hypothesis)
        return {'cer': 1.0, 'character_accuracy': 0.0, 'insertions': hyp_chars, ...}
```

## Batch Processing

Similar to WER, when processing multiple pairs:

1. Individual metrics are calculated for each pair
2. Total values are summed:
   - `total_correct = sum(hits)`
   - `total_substitutions = sum(substitutions)`
   - `total_deletions = sum(deletions)`
   - `total_insertions = sum(insertions)`
   - `total_character_count = sum(character_counts)`

3. Aggregated metrics are calculated:
   ```python
   total_errors = total_substitutions + total_deletions + total_insertions
   aggregated_cer = total_errors / total_character_count
   aggregated_accuracy = total_correct / total_character_count
   ```

## Differences with WER

| Aspect | WER | CER |
|---------|-----|-----|
| **Evaluation unit** | Words | Characters |
| **Alignment** | Word by word | Character by character |
| **Spaces** | Word separators | Evaluable characters |
| **Typical use** | ASR systems with segmented text | Systems without spaces, OCR, granular analysis |
| **Adjustments** | Supported (replacements, equivalences, clean_up) | Not supported |
| **Sensitivity** | Less sensitive to minor spelling errors | More sensitive to spelling errors |

### When to Use CER vs WER

**Use CER when:**
- Evaluating systems that process text without spaces (e.g., Chinese, Japanese)
- You need more granular error analysis
- Evaluating OCR (Optical Character Recognition) systems
- You want to detect minor spelling errors

**Use WER when:**
- Evaluating ASR systems with text segmented into words
- You need industry-standard metrics
- You want to use adjustments (equivalences, etc.)
- Text is naturally segmented into words

## Alignments

Metrix generates detailed alignments using `jiwer.process_characters().alignments`, which shows how each character in the reference aligns with characters in the hypothesis.

These alignments are included in the detailed report for character-by-character analysis.

## Technical References

- **Jiwer Documentation**: https://github.com/jitsi/jiwer
- **Levenshtein Distance**: Base algorithm for character alignment
- **Character-level evaluation**: Useful for languages without spaces or granular analysis
