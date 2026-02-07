"""
Module for calculating WER and CER metrics using Jiwer, with special cases handling.
"""

from typing import List, Tuple, Dict, Optional
from jiwer import process_words, process_characters


def calculate_wer_metrics(reference: str, hypothesis: str) -> Dict:
    """
    Calculates WER metrics using Jiwer.
    
    Args:
        reference: Reference text
        hypothesis: Hypothesis text
    
    Returns:
        Dictionary with metrics: {
            'wer': float,
            'word_accuracy': float,
            'deletions': int,
            'insertions': int,
            'substitutions': int,
            'correct': int,
            'word_count': int
        }
    """
    # Handle special cases of empty references
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
    
    # Use Jiwer for normal calculation
    try:
        output = process_words(reference, hypothesis)
        
        # Calculate word count from reference
        ref_words = reference.split()
        word_count = len(ref_words)
        
        # Extract metrics from WordOutput object
        h = output.hits  # Correct words
        s = output.substitutions
        d = output.deletions
        i = output.insertions
        wer_value = output.wer  # WER already calculated by jiwer
        
        # Calculate Word Accuracy
        word_accuracy = h / word_count if word_count > 0 else 0.0
        
        return {
            'wer': float(wer_value),
            'word_accuracy': word_accuracy,
            'deletions': int(d),
            'insertions': int(i),
            'substitutions': int(s),
            'correct': int(h),
            'word_count': word_count
        }
    except Exception as e:
        # Fallback in case of error
        raise ValueError(f"Error calculating WER: {e}")


def calculate_cer_metrics(reference: str, hypothesis: str) -> Dict:
    """
    Calculates CER metrics using Jiwer.
    
    Args:
        reference: Reference text
        hypothesis: Hypothesis text
    
    Returns:
        Dictionary with metrics: {
            'cer': float,
            'character_accuracy': float,
            'deletions': int,
            'insertions': int,
            'substitutions': int,
            'correct': int,
            'character_count': int
        }
    """
    # Handle special cases of empty references
    if not reference.strip():
        if not hypothesis.strip():
            # Both empty: CER = 0, accuracy = 1
            return {
                'cer': 0.0,
                'character_accuracy': 1.0,
                'deletions': 0,
                'insertions': 0,
                'substitutions': 0,
                'correct': 0,
                'character_count': 0
            }
        else:
            # Empty reference but hypothesis not: CER = 1 (100% error)
            hyp_chars = len(hypothesis)
            return {
                'cer': 1.0,
                'character_accuracy': 0.0,
                'deletions': 0,
                'insertions': hyp_chars,
                'substitutions': 0,
                'correct': 0,
                'character_count': 0
            }
    
    # Use Jiwer for normal calculation
    try:
        output = process_characters(reference, hypothesis)
        
        # Calculate character count from reference
        character_count = len(reference)
        
        # Extract metrics from CharacterOutput object
        h = output.hits  # Correct characters
        s = output.substitutions
        d = output.deletions
        i = output.insertions
        cer_value = output.cer  # CER already calculated by jiwer
        
        # Calculate Character Accuracy
        character_accuracy = h / character_count if character_count > 0 else 0.0
        
        return {
            'cer': float(cer_value),
            'character_accuracy': character_accuracy,
            'deletions': int(d),
            'insertions': int(i),
            'substitutions': int(s),
            'correct': int(h),
            'character_count': character_count
        }
    except Exception as e:
        # Fallback in case of error
        raise ValueError(f"Error calculating CER: {e}")


def get_alignment(reference: str, hypothesis: str, metric_type: str = 'wer') -> List[Dict]:
    """
    Gets detailed alignment between reference and hypothesis.
    
    Args:
        reference: Reference text
        hypothesis: Hypothesis text
        metric_type: 'wer' or 'cer'
    
    Returns:
        List of dictionaries with alignment information
    """
    if metric_type == 'wer':
        # Process by words
        out = process_words(reference, hypothesis)
        return out.alignments
    else:
        # Process by characters
        out = process_characters(reference, hypothesis)
        return out.alignments


def calculate_metrics_batch(
    references: List[str],
    hypotheses: List[str],
    metric_type: str = 'wer',
    with_adjustments: Optional[Dict] = None,
    without_adjustments: Optional[Dict] = None
) -> Tuple[Dict, List[Dict]]:
    """
    Calculates metrics for a batch of references and hypotheses.
    
    Args:
        references: List of reference texts
        hypotheses: List of hypothesis texts
        metric_type: 'wer' or 'cer'
        with_adjustments: Metrics calculated with adjustments (if applicable)
        without_adjustments: Metrics calculated without adjustments (if applicable)
    
    Returns:
        Tuple (aggregated_metrics, alignment_list_per_sentence)
    """
    if len(references) != len(hypotheses):
        raise ValueError("Reference and hypothesis lists must have the same length")
    
    # Calculate metrics per sentence
    alignments = []
    total_correct = 0
    total_deletions = 0
    total_insertions = 0
    total_substitutions = 0
    total_count = 0
    
    for ref, hyp in zip(references, hypotheses):
        if metric_type == 'wer':
            metrics = calculate_wer_metrics(ref, hyp)
            count_key = 'word_count'
        else:
            metrics = calculate_cer_metrics(ref, hyp)
            count_key = 'character_count'
        
        total_correct += metrics['correct']
        total_deletions += metrics['deletions']
        total_insertions += metrics['insertions']
        total_substitutions += metrics['substitutions']
        total_count += metrics[count_key]
        
        # Get alignment
        alignment = get_alignment(ref, hyp, metric_type)
        alignments.append({
            'reference': ref,
            'hypothesis': hyp,
            'alignment': alignment,
            'metrics': metrics
        })
    
    # Calculate aggregated metrics
    total_errors = total_substitutions + total_deletions + total_insertions
    
    # Handle special case: all references empty but there are errors (insertions)
    # When total_count = 0 but total_errors > 0, WER should be 1.0 (100% error)
    if total_count == 0:
        if total_errors > 0:
            # All references empty but hypotheses have words -> WER = 1.0
            aggregated_wer = 1.0
            aggregated_accuracy = 0.0
        else:
            # All references and hypotheses empty -> WER = 0.0 (no errors)
            aggregated_wer = 0.0
            aggregated_accuracy = 1.0
    else:
        # Normal case: calculate WER from total errors and total count
        aggregated_wer = total_errors / total_count
        aggregated_accuracy = total_correct / total_count
    
    if metric_type == 'wer':
        aggregated_metrics = {
            'wer': aggregated_wer,
            'word_accuracy': aggregated_accuracy,
            'deletions': total_deletions,
            'insertions': total_insertions,
            'substitutions': total_substitutions,
            'correct': total_correct,
            'word_count': total_count,
            'total_sentences': len(references)
        }
    else:
        aggregated_metrics = {
            'cer': aggregated_wer,
            'character_accuracy': aggregated_accuracy,
            'deletions': total_deletions,
            'insertions': total_insertions,
            'substitutions': total_substitutions,
            'correct': total_correct,
            'character_count': total_count,
            'total_sentences': len(references)
        }
    
    return aggregated_metrics, alignments
