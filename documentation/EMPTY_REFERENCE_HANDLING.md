# Empty Reference Handling in WER/CER Calculation

This document explains how Metrix handles special cases where the reference text is empty, which cannot be processed by Jiwer directly.

## Problem Statement

Jiwer's `process_words()` and `process_characters()` functions cannot handle empty reference strings properly. When the reference is empty but the hypothesis is not, Jiwer returns incorrect WER values (it returns the number of words/characters instead of 1.0).

## Cases Handled

### Case 1: Both Reference and Hypothesis Empty

**Input:**
```
Reference:  ""
Hypothesis: ""
```

**Handling:**
- **Manually calculated** (not using Jiwer)
- **Logic**: Both texts are empty, so there are no errors
- **Result:**
  - WER = 0.0 (no errors)
  - Word Accuracy = 1.0 (100% correct)
  - Word Count = 0
  - All error counts (deletions, insertions, substitutions) = 0

**Implementation:**
```python
if not reference.strip():
    if not hypothesis.strip():
        # Both empty: WER = 0, accuracy = 1
        return {
            'wer': 0.0,
            'word_accuracy': 1.0,
            'deletions': 0,
            'insertions': 0,
            'substitutions': 0,
            'correct': 0,
            'word_count': 0
        }
```

### Case 2: Empty Reference, Non-Empty Hypothesis

**Input:**
```
Reference:  ""
Hypothesis: "hello world"
```

**Handling:**
- **Manually calculated** (not using Jiwer)
- **Logic**: All words in hypothesis are insertions (errors)
- **Result:**
  - WER = 1.0 (100% error, since N=0, we define WER=1.0 by convention)
  - Word Accuracy = 0.0 (0% correct)
  - Insertions = number of words in hypothesis (2 in this example)
  - Word Count = 0

**Why WER = 1.0?**
- Standard WER formula: `WER = (S + D + I) / N`
- When N = 0 (empty reference), we cannot divide
- Industry convention: WER = 1.0 when reference is empty but hypothesis is not
- This represents 100% error rate

**Implementation:**
```python
else:
    # Empty reference but hypothesis not: WER = 1 (100% error)
    hyp_words = len(hypothesis.split())
    return {
        'wer': 1.0,
        'word_accuracy': 0.0,
        'deletions': 0,
        'insertions': hyp_words,
        'substitutions': 0,
        'correct': 0,
        'word_count': 0
    }
```

### Case 3: Non-Empty Reference, Empty Hypothesis

**Input:**
```
Reference:  "hello world"
Hypothesis: ""
```

**Handling:**
- **Processed by Jiwer** (Jiwer can handle this case correctly)
- **Logic**: All words in reference are deletions (errors)
- **Result:**
  - WER = 1.0 (100% error)
  - Word Accuracy = 0.0 (0% correct)
  - Deletions = number of words in reference (2 in this example)
  - Word Count = number of words in reference

**Why Jiwer can handle this?**
- Jiwer correctly calculates WER when hypothesis is empty
- It identifies all reference words as deletions
- Returns WER = 1.0, which is mathematically correct: `WER = (0 + 2 + 0) / 2 = 1.0`

### Case 4: Whitespace-Only Strings

**Input:**
```
Reference:  "   "  (only spaces)
Hypothesis: "hello"
```

**Handling:**
- **Treated as empty** (using `.strip()` before checking)
- **Logic**: Same as Case 2 (empty reference, non-empty hypothesis)
- **Result:** Same as Case 2

**Implementation:**
```python
if not reference.strip():  # .strip() removes whitespace
    # Treated as empty reference
```

## Why Not Use Jiwer for Empty References?

When we tested Jiwer with empty references, we found:

```python
# Jiwer behavior with empty reference
process_words("", "hello world")
# Returns: WER = 2 (number of words), not WER = 1.0
```

This is **incorrect** because:
1. WER should be between 0.0 and 1.0 (or 0% and 100%)
2. When reference is empty, WER should be 1.0 by convention
3. Jiwer returns the raw count of words/characters, not a normalized error rate

## Edge Cases in Batch Processing

When processing multiple sentence pairs in batch:

1. **Mixed cases**: Some pairs may have empty references, others may not
2. **Aggregation**: Empty reference cases contribute:
   - `word_count = 0` (doesn't affect denominator in aggregated WER)
   - `insertions = N` (where N is number of words in hypothesis)
   - These are correctly aggregated with other cases

**Example:**
```python
references = ["", "hello world", "test"]
hypotheses = ["", "hello", ""]

# Pair 1: Both empty -> WER=0, word_count=0, insertions=0
# Pair 2: Normal case -> WER calculated by Jiwer
# Pair 3: Empty hypothesis -> WER=1.0, word_count=1, deletions=1

# Aggregated metrics correctly combine all cases
```

## Testing

All special cases are covered by unit tests:

- `test_calculate_wer_metrics_empty_reference_and_hypothesis`
- `test_calculate_wer_metrics_empty_reference_non_empty_hypothesis`
- `test_calculate_wer_metrics_whitespace_only_reference`
- `test_calculate_wer_metrics_whitespace_only_both`
- `test_calculate_wer_metrics_empty_hypothesis_non_empty_reference`
- `test_calculate_metrics_batch_mixed_empty_cases`

Similar tests exist for CER.

## Summary

| Case | Reference | Hypothesis | Handled By | WER | Notes |
|------|-----------|------------|------------|-----|-------|
| 1 | Empty | Empty | Manual | 0.0 | No errors possible |
| 2 | Empty | Non-empty | Manual | 1.0 | All words are insertions |
| 3 | Non-empty | Empty | Jiwer | 1.0 | All words are deletions |
| 4 | Whitespace | Any | Manual | 1.0 or 0.0 | Treated as empty |

**Key Principle**: Empty references (after `.strip()`) are always handled manually to ensure correct WER/CER values according to industry standards.

