"""
Unit tests for metrics_calculator module.
"""

import pytest
from src.metrics_calculator import (
    calculate_wer_metrics,
    calculate_cer_metrics,
    get_alignment,
    calculate_metrics_batch
)


class TestCalculateWerMetrics:
    """Tests for calculate_wer_metrics."""
    
    def test_calculate_wer_metrics_perfect_match(self):
        """Test WER with perfect match."""
        result = calculate_wer_metrics("hello world", "hello world")
        assert result['wer'] == 0.0
        assert result['word_accuracy'] == 1.0
        assert result['correct'] == 2
        assert result['word_count'] == 2
    
    def test_calculate_wer_metrics_spanish_utf8(self):
        """Test WER with Spanish text in UTF-8."""
        # Test perfect match with Spanish characters
        result = calculate_wer_metrics("El niño comió una manzana", "El niño comió una manzana")
        assert result['wer'] == 0.0
        assert result['word_accuracy'] == 1.0
        assert result['correct'] == 5
        assert result['word_count'] == 5
        
        # Test with errors
        result = calculate_wer_metrics("El niño comió una manzana", "El niño comió una pera")
        assert result['wer'] > 0.0
        assert result['substitutions'] == 1
        assert result['word_count'] == 5
    
    def test_calculate_wer_metrics_portuguese_utf8(self):
        """Test WER with Portuguese text in UTF-8."""
        result = calculate_wer_metrics("O menino comeu uma maçã", "O menino comeu uma maçã")
        assert result['wer'] == 0.0
        assert result['word_accuracy'] == 1.0
        assert result['correct'] == 5
        assert result['word_count'] == 5
    
    def test_calculate_wer_metrics_substitution(self):
        """Test WER with substitution."""
        result = calculate_wer_metrics("hello world", "hello universe")
        assert result['wer'] > 0.0
        assert result['substitutions'] == 1
        assert result['word_count'] == 2
    
    def test_calculate_wer_metrics_deletion(self):
        """Test WER with deletion."""
        result = calculate_wer_metrics("hello world", "hello")
        assert result['deletions'] > 0
        assert result['wer'] > 0.0
    
    def test_calculate_wer_metrics_insertion(self):
        """Test WER with insertion."""
        result = calculate_wer_metrics("hello", "hello world")
        assert result['insertions'] > 0
        assert result['wer'] > 0.0
    
    def test_calculate_wer_metrics_empty_reference_and_hypothesis(self):
        """Test WER with both reference and hypothesis empty."""
        result = calculate_wer_metrics("", "")
        assert result['wer'] == 0.0
        assert result['word_accuracy'] == 1.0
        assert result['deletions'] == 0
        assert result['insertions'] == 0
        assert result['substitutions'] == 0
        assert result['correct'] == 0
        assert result['word_count'] == 0
    
    def test_calculate_wer_metrics_empty_reference_non_empty_hypothesis(self):
        """Test WER with empty reference but non-empty hypothesis."""
        result = calculate_wer_metrics("", "hello world")
        assert result['wer'] == 1.0
        assert result['word_accuracy'] == 0.0
        assert result['deletions'] == 0
        assert result['insertions'] == 2  # Both words are insertions
        assert result['substitutions'] == 0
        assert result['correct'] == 0
        assert result['word_count'] == 0
    
    def test_calculate_wer_metrics_whitespace_only_reference(self):
        """Test WER with reference containing only whitespace."""
        # Whitespace-only reference should be treated as empty
        result = calculate_wer_metrics("   ", "hello")
        assert result['wer'] == 1.0
        assert result['word_accuracy'] == 0.0
        assert result['insertions'] == 1
        assert result['word_count'] == 0
    
    def test_calculate_wer_metrics_whitespace_only_both(self):
        """Test WER with both reference and hypothesis containing only whitespace."""
        result = calculate_wer_metrics("   ", "   ")
        assert result['wer'] == 0.0
        assert result['word_accuracy'] == 1.0
        assert result['word_count'] == 0
    
    def test_calculate_wer_metrics_empty_hypothesis_non_empty_reference(self):
        """Test WER with non-empty reference but empty hypothesis."""
        # This case is handled by Jiwer, not manually
        result = calculate_wer_metrics("hello world", "")
        assert result['wer'] == 1.0  # All words are deletions
        assert result['word_accuracy'] == 0.0
        assert result['deletions'] == 2  # Both words are deletions
        assert result['insertions'] == 0
        assert result['word_count'] == 2


class TestCalculateCerMetrics:
    """Tests for calculate_cer_metrics."""
    
    def test_calculate_cer_metrics_perfect_match(self):
        """Test CER with perfect match."""
        result = calculate_cer_metrics("hello", "hello")
        assert result['cer'] == 0.0
        assert result['character_accuracy'] == 1.0
        assert result['correct'] == 5
        assert result['character_count'] == 5
    
    def test_calculate_cer_metrics_spanish_utf8(self):
        """Test CER with Spanish text in UTF-8."""
        # Test perfect match with Spanish characters (including ñ, ¿, etc.)
        result = calculate_cer_metrics("niño", "niño")
        assert result['cer'] == 0.0
        assert result['character_accuracy'] == 1.0
        assert result['correct'] == 4
        assert result['character_count'] == 4
        
        # Test with error
        result = calculate_cer_metrics("niño", "nino")
        assert result['cer'] > 0.0
        assert result['substitutions'] > 0
    
    def test_calculate_cer_metrics_portuguese_utf8(self):
        """Test CER with Portuguese text in UTF-8."""
        result = calculate_cer_metrics("maçã", "maçã")
        assert result['cer'] == 0.0
        assert result['character_accuracy'] == 1.0
        assert result['correct'] == 4
        assert result['character_count'] == 4
    
    def test_calculate_cer_metrics_substitution(self):
        """Test CER with substitution."""
        result = calculate_cer_metrics("hello", "hallo")
        assert result['cer'] > 0.0
        assert result['substitutions'] > 0
    
    def test_calculate_cer_metrics_empty_reference_and_hypothesis(self):
        """Test CER with both reference and hypothesis empty."""
        result = calculate_cer_metrics("", "")
        assert result['cer'] == 0.0
        assert result['character_accuracy'] == 1.0
        assert result['deletions'] == 0
        assert result['insertions'] == 0
        assert result['substitutions'] == 0
        assert result['correct'] == 0
        assert result['character_count'] == 0
    
    def test_calculate_cer_metrics_empty_reference_non_empty_hypothesis(self):
        """Test CER with empty reference but non-empty hypothesis."""
        result = calculate_cer_metrics("", "hello")
        assert result['cer'] == 1.0
        assert result['character_accuracy'] == 0.0
        assert result['deletions'] == 0
        assert result['insertions'] == 5  # All characters are insertions
        assert result['substitutions'] == 0
        assert result['correct'] == 0
        assert result['character_count'] == 0
    
    def test_calculate_cer_metrics_whitespace_only_reference(self):
        """Test CER with reference containing only whitespace."""
        # Whitespace-only reference should be treated as empty
        result = calculate_cer_metrics("   ", "hello")
        assert result['cer'] == 1.0
        assert result['character_accuracy'] == 0.0
        assert result['insertions'] == 5
        assert result['character_count'] == 0
    
    def test_calculate_cer_metrics_empty_hypothesis_non_empty_reference(self):
        """Test CER with non-empty reference but empty hypothesis."""
        # This case is handled by Jiwer, not manually
        result = calculate_cer_metrics("hello", "")
        assert result['cer'] == 1.0  # All characters are deletions
        assert result['character_accuracy'] == 0.0
        assert result['deletions'] == 5  # All characters are deletions
        assert result['insertions'] == 0
        assert result['character_count'] == 5


class TestGetAlignment:
    """Tests for get_alignment."""
    
    def test_get_alignment_wer(self):
        """Test alignment retrieval for WER."""
        alignment = get_alignment("hello world", "hello universe", metric_type='wer')
        assert alignment is not None
        assert isinstance(alignment, list)
    
    def test_get_alignment_cer(self):
        """Test alignment retrieval for CER."""
        alignment = get_alignment("hello", "hallo", metric_type='cer')
        assert alignment is not None
        assert isinstance(alignment, list)


class TestCalculateMetricsBatch:
    """Tests for calculate_metrics_batch."""
    
    def test_calculate_metrics_batch_wer(self):
        """Test batch metrics calculation for WER."""
        references = ["hello world", "test sentence"]
        hypotheses = ["hello world", "test phrase"]
        
        metrics, alignments = calculate_metrics_batch(
            references, hypotheses, metric_type='wer'
        )
        
        assert 'wer' in metrics
        assert 'word_count' in metrics
        assert 'total_sentences' in metrics
        assert metrics['total_sentences'] == 2
        assert len(alignments) == 2
    
    def test_calculate_metrics_batch_cer(self):
        """Test batch metrics calculation for CER."""
        references = ["hello", "test"]
        hypotheses = ["hallo", "test"]
        
        metrics, alignments = calculate_metrics_batch(
            references, hypotheses, metric_type='cer'
        )
        
        assert 'cer' in metrics
        assert 'character_count' in metrics
        assert 'total_sentences' in metrics
        assert metrics['total_sentences'] == 2
        assert len(alignments) == 2
    
    def test_calculate_metrics_batch_different_lengths(self):
        """Test that raises error if lists have different lengths."""
        references = ["hello", "world"]
        hypotheses = ["hello"]
        
        with pytest.raises(ValueError, match="same length"):
            calculate_metrics_batch(references, hypotheses, metric_type='wer')
    
    def test_calculate_metrics_batch_empty_lists(self):
        """Test with empty lists."""
        references = []
        hypotheses = []
        
        metrics, alignments = calculate_metrics_batch(
            references, hypotheses, metric_type='wer'
        )
        
        assert metrics['total_sentences'] == 0
        assert len(alignments) == 0
    
    def test_calculate_metrics_batch_mixed_empty_cases(self):
        """Test batch calculation with mixed empty cases."""
        references = ["", "hello world", "test"]
        hypotheses = ["", "hello", ""]
        
        metrics, alignments = calculate_metrics_batch(
            references, hypotheses, metric_type='wer'
        )
        
        # First pair: both empty -> WER=0, word_count=0
        # Second pair: ref="hello world", hyp="hello" -> has errors
        # Third pair: ref="test", hyp="" -> all deletions, WER=1.0
        
        assert metrics['total_sentences'] == 3
        assert len(alignments) == 3
        
        # Check first sentence (both empty)
        assert alignments[0]['metrics']['wer'] == 0.0
        assert alignments[0]['metrics']['word_count'] == 0
        
        # Check third sentence (empty hypothesis)
        assert alignments[2]['metrics']['wer'] == 1.0
        assert alignments[2]['metrics']['deletions'] == 1
        assert alignments[2]['metrics']['word_count'] == 1
    
    def test_calculate_metrics_batch_all_empty_references(self):
        """Test batch calculation when all references are empty."""
        references = ["", ""]
        hypotheses = ["hello world", "test"]
        
        metrics, alignments = calculate_metrics_batch(
            references, hypotheses, metric_type='wer'
        )
        
        # Both pairs have empty references -> all words are insertions
        # Total: 2 + 1 = 3 insertions, 0 word_count
        assert metrics['insertions'] == 3
        assert metrics['word_count'] == 0
        assert metrics['wer'] == 1.0  # Should be 1.0 when all refs empty but there are errors
        assert metrics['word_accuracy'] == 0.0
        
        # Check individual sentences
        assert alignments[0]['metrics']['insertions'] == 2
        assert alignments[1]['metrics']['insertions'] == 1
    
    def test_calculate_metrics_batch_all_empty_both(self):
        """Test batch calculation when all references and hypotheses are empty."""
        references = ["", ""]
        hypotheses = ["", ""]
        
        metrics, alignments = calculate_metrics_batch(
            references, hypotheses, metric_type='wer'
        )
        
        # All empty -> no errors
        assert metrics['insertions'] == 0
        assert metrics['word_count'] == 0
        assert metrics['wer'] == 0.0  # Should be 0.0 when all empty
        assert metrics['word_accuracy'] == 1.0

