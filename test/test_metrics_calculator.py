"""
Tests unitarios para el módulo metrics_calculator.
"""

import pytest
from src.metrics_calculator import (
    calculate_wer_metrics,
    calculate_cer_metrics,
    get_alignment,
    calculate_metrics_batch
)


class TestCalculateWerMetrics:
    """Tests para calculate_wer_metrics."""
    
    def test_calculate_wer_metrics_perfect_match(self):
        """Test WER con coincidencia perfecta."""
        result = calculate_wer_metrics("hello world", "hello world")
        assert result['wer'] == 0.0
        assert result['word_accuracy'] == 1.0
        assert result['correct'] == 2
        assert result['word_count'] == 2
    
    def test_calculate_wer_metrics_substitution(self):
        """Test WER con substitución."""
        result = calculate_wer_metrics("hello world", "hello universe")
        assert result['wer'] > 0.0
        assert result['substitutions'] == 1
        assert result['word_count'] == 2
    
    def test_calculate_wer_metrics_deletion(self):
        """Test WER con deleción."""
        result = calculate_wer_metrics("hello world", "hello")
        assert result['deletions'] > 0
        assert result['wer'] > 0.0
    
    def test_calculate_wer_metrics_insertion(self):
        """Test WER con inserción."""
        result = calculate_wer_metrics("hello", "hello world")
        assert result['insertions'] > 0
        assert result['wer'] > 0.0
    
    def test_calculate_wer_metrics_empty_reference_and_hypothesis(self):
        """Test WER con referencia e hypothesis vacías."""
        result = calculate_wer_metrics("", "")
        assert result['wer'] == 0.0
        assert result['word_accuracy'] == 1.0
        assert result['word_count'] == 0
    
    def test_calculate_wer_metrics_empty_reference_non_empty_hypothesis(self):
        """Test WER con referencia vacía pero hypothesis no."""
        result = calculate_wer_metrics("", "hello world")
        assert result['wer'] == 1.0
        assert result['word_accuracy'] == 0.0
        assert result['insertions'] == 2
        assert result['word_count'] == 0


class TestCalculateCerMetrics:
    """Tests para calculate_cer_metrics."""
    
    def test_calculate_cer_metrics_perfect_match(self):
        """Test CER con coincidencia perfecta."""
        result = calculate_cer_metrics("hello", "hello")
        assert result['cer'] == 0.0
        assert result['character_accuracy'] == 1.0
        assert result['correct'] == 5
        assert result['character_count'] == 5
    
    def test_calculate_cer_metrics_substitution(self):
        """Test CER con substitución."""
        result = calculate_cer_metrics("hello", "hallo")
        assert result['cer'] > 0.0
        assert result['substitutions'] > 0
    
    def test_calculate_cer_metrics_empty_reference_and_hypothesis(self):
        """Test CER con referencia e hypothesis vacías."""
        result = calculate_cer_metrics("", "")
        assert result['cer'] == 0.0
        assert result['character_accuracy'] == 1.0
        assert result['character_count'] == 0
    
    def test_calculate_cer_metrics_empty_reference_non_empty_hypothesis(self):
        """Test CER con referencia vacía pero hypothesis no."""
        result = calculate_cer_metrics("", "hello")
        assert result['cer'] == 1.0
        assert result['character_accuracy'] == 0.0
        assert result['insertions'] == 5


class TestGetAlignment:
    """Tests para get_alignment."""
    
    def test_get_alignment_wer(self):
        """Test obtención de alineación para WER."""
        alignment = get_alignment("hello world", "hello universe", metric_type='wer')
        assert alignment is not None
        assert isinstance(alignment, list)
    
    def test_get_alignment_cer(self):
        """Test obtención de alineación para CER."""
        alignment = get_alignment("hello", "hallo", metric_type='cer')
        assert alignment is not None
        assert isinstance(alignment, list)


class TestCalculateMetricsBatch:
    """Tests para calculate_metrics_batch."""
    
    def test_calculate_metrics_batch_wer(self):
        """Test cálculo de métricas por batch para WER."""
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
        """Test cálculo de métricas por batch para CER."""
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
        """Test que lanza error si las listas tienen diferente longitud."""
        references = ["hello", "world"]
        hypotheses = ["hello"]
        
        with pytest.raises(ValueError, match="same length"):
            calculate_metrics_batch(references, hypotheses, metric_type='wer')
    
    def test_calculate_metrics_batch_empty_lists(self):
        """Test con listas vacías."""
        references = []
        hypotheses = []
        
        metrics, alignments = calculate_metrics_batch(
            references, hypotheses, metric_type='wer'
        )
        
        assert metrics['total_sentences'] == 0
        assert len(alignments) == 0

