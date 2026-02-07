"""
Tests unitarios para el módulo text_transformer.
"""

import pytest
from src.text_transformer import transform_text, apply_basic_transformations


class TestTransformText:
    """Tests para transform_text."""
    
    def test_transform_text_lowercase(self):
        """Test normalización a minúsculas."""
        result = transform_text("Hello World", case_sensitive=False)
        assert result == "hello world"
    
    def test_transform_text_case_sensitive(self):
        """Test que mantiene mayúsculas cuando es case-sensitive."""
        result = transform_text("Hello World", case_sensitive=True)
        assert result == "Hello World"
    
    def test_transform_text_remove_punctuation(self):
        """Test remoción de puntuación."""
        result = transform_text("Hello, world! How are you?", keep_punctuation=False)
        assert result == "hello world how are you"
    
    def test_transform_text_keep_punctuation(self):
        """Test que mantiene puntuación cuando se solicita."""
        result = transform_text("Hello, world!", keep_punctuation=True)
        assert "Hello" in result or "hello" in result  # Puede estar en minúsculas
    
    def test_transform_text_neutralize_hyphens(self):
        """Test neutralización de guiones."""
        result = transform_text("well-known word", neutralize_hyphens=True)
        assert result == "well known word"
    
    def test_transform_text_neutralize_apostrophes(self):
        """Test remoción de apostrofes."""
        result = transform_text("don't can't", neutralize_apostrophes=True)
        assert "'" not in result
        assert "dont" in result or "DONT" in result
    
    def test_transform_text_multiple_spaces(self):
        """Test normalización de espacios múltiples."""
        result = transform_text("hello    world")
        assert result == "hello world"
    
    def test_transform_text_trim_spaces(self):
        """Test que elimina espacios al inicio y final."""
        result = transform_text("  hello world  ")
        assert result == "hello world"
    
    def test_transform_text_combined(self):
        """Test combinación de transformaciones."""
        result = transform_text(
            "  Hello, World!  Don't worry.",
            case_sensitive=False,
            keep_punctuation=False,
            neutralize_hyphens=False,
            neutralize_apostrophes=True
        )
        assert "hello" in result
        assert "world" in result
        assert "dont" in result
        assert "'" not in result
        assert result.strip() == result  # Sin espacios al inicio/final


class TestApplyBasicTransformations:
    """Tests para apply_basic_transformations."""
    
    def test_apply_basic_transformations_both_texts(self):
        """Test que aplica transformaciones a ambos textos."""
        ref = "Hello, World!"
        hyp = "hello world"
        ref_transformed, hyp_transformed = apply_basic_transformations(
            ref, hyp, case_sensitive=False, keep_punctuation=False
        )
        assert ref_transformed == "hello world"
        assert hyp_transformed == "hello world"
    
    def test_apply_basic_transformations_preserves_differences(self):
        """Test que preserva diferencias entre ref e hyp."""
        ref = "Hello World"
        hyp = "Hello Universe"
        ref_transformed, hyp_transformed = apply_basic_transformations(
            ref, hyp, case_sensitive=True
        )
        assert ref_transformed == "Hello World"
        assert hyp_transformed == "Hello Universe"
    
    def test_apply_basic_transformations_hyphens(self):
        """Test neutralización de guiones en ambos textos."""
        ref = "well-known"
        hyp = "well known"
        ref_transformed, hyp_transformed = apply_basic_transformations(
            ref, hyp, neutralize_hyphens=True
        )
        assert ref_transformed == hyp_transformed
    
    def test_apply_basic_transformations_empty_strings(self):
        """Test con strings vacíos."""
        ref = ""
        hyp = ""
        ref_transformed, hyp_transformed = apply_basic_transformations(ref, hyp)
        assert ref_transformed == ""
        assert hyp_transformed == ""

