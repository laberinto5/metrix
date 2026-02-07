"""
Unit tests for stop words removal functionality.
"""

import pytest
from src.text_transformer import remove_stop_words, apply_stop_words_removal


class TestRemoveStopWords:
    """Tests for remove_stop_words function."""
    
    def test_remove_stop_words_english(self):
        """Test removing English stop words."""
        text = "the quick brown fox jumps over the lazy dog"
        result = remove_stop_words(text, "english")
        
        # Should remove: the, over, the
        assert "the" not in result
        assert "over" not in result
        assert "quick" in result
        assert "brown" in result
        assert "fox" in result
    
    def test_remove_stop_words_spanish(self):
        """Test removing Spanish stop words."""
        text = "el niño comió una manzana"
        result = remove_stop_words(text, "spanish")
        
        # Should remove: el, una
        assert "el" not in result
        assert "una" not in result
        assert "niño" in result
        assert "comió" in result
        assert "manzana" in result
    
    def test_remove_stop_words_portuguese(self):
        """Test removing Portuguese stop words."""
        text = "o menino comeu uma maçã"
        result = remove_stop_words(text, "portuguese")
        
        # Should remove: o, uma (as complete words, not substrings)
        words = result.split()
        assert "o" not in words  # "o" should be removed as a word
        assert "uma" not in words  # "uma" should be removed as a word
        assert "menino" in words  # "menino" contains "o" but is not removed
        assert "comeu" in words
        assert "maçã" in words
    
    def test_remove_stop_words_language_code_mapping(self):
        """Test that language codes are correctly mapped."""
        text = "the quick brown fox"
        
        # Test various language code formats
        result1 = remove_stop_words(text, "english")
        result2 = remove_stop_words(text, "en")
        result3 = remove_stop_words(text, "ENG")
        
        # All should produce the same result
        assert result1 == result2 == result3
    
    def test_remove_stop_words_empty_text(self):
        """Test removing stop words from empty text."""
        result = remove_stop_words("", "english")
        assert result == ""
    
    def test_remove_stop_words_only_stopwords(self):
        """Test text with only stop words."""
        text = "the the a an"
        result = remove_stop_words(text, "english")
        # Should be empty or only spaces
        assert len(result.strip()) == 0
    
    def test_remove_stop_words_invalid_language(self):
        """Test that invalid language raises error with clear message."""
        with pytest.raises(ValueError) as exc_info:
            remove_stop_words("test text", "invalid_language")
        
        error_message = str(exc_info.value)
        assert ("not supported" in error_message or "not available" in error_message)
        assert "Supported languages" in error_message
        assert "english" in error_message.lower() or "spanish" in error_message.lower()
    
    def test_remove_stop_words_nltk_not_installed(self):
        """Test that missing NLTK raises ImportError with clear message."""
        import sys
        from unittest.mock import patch
        
        # Mock NLTK_AVAILABLE to be False
        with patch('src.text_transformer.NLTK_AVAILABLE', False):
            with pytest.raises(ImportError) as exc_info:
                remove_stop_words("test text", "english")
            
            error_message = str(exc_info.value)
            assert "NLTK is required" in error_message
            assert "pip install nltk" in error_message
    
    def test_remove_stop_words_preserves_word_order(self):
        """Test that word order is preserved."""
        text = "the quick brown fox"
        result = remove_stop_words(text, "english")
        
        # Should preserve order: quick brown fox
        words = result.split()
        assert words == ["quick", "brown", "fox"]


class TestApplyStopWordsRemoval:
    """Tests for apply_stop_words_removal function."""
    
    def test_apply_stop_words_removal_both_texts(self):
        """Test removing stop words from both reference and hypothesis."""
        ref = "the quick brown fox"
        hyp = "the quick brown dog"
        
        ref_result, hyp_result = apply_stop_words_removal(ref, hyp, "english")
        
        assert "the" not in ref_result
        assert "the" not in hyp_result
        assert "quick" in ref_result
        assert "quick" in hyp_result
    
    def test_apply_stop_words_removal_none_language(self):
        """Test that None language returns original texts."""
        ref = "the quick brown fox"
        hyp = "the quick brown dog"
        
        ref_result, hyp_result = apply_stop_words_removal(ref, hyp, None)
        
        assert ref_result == ref
        assert hyp_result == hyp
    
    def test_apply_stop_words_removal_spanish(self):
        """Test removing stop words from Spanish texts."""
        ref = "el niño comió una manzana"
        hyp = "el niño comió una pera"
        
        ref_result, hyp_result = apply_stop_words_removal(ref, hyp, "spanish")
        
        # Should remove: el, una
        assert "el" not in ref_result
        assert "una" not in ref_result
        assert "el" not in hyp_result
        assert "una" not in hyp_result
        assert "niño" in ref_result
        assert "comió" in ref_result
        assert "manzana" in ref_result
        assert "pera" in hyp_result

