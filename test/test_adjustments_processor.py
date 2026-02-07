"""
Tests unitarios para el módulo adjustments_processor.
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.adjustments_processor import (
    load_adjustments,
    apply_reference_replacements,
    apply_equivalences,
    apply_clean_up,
    apply_adjustments
)


class TestLoadAdjustments:
    """Tests para load_adjustments."""
    
    def test_load_adjustments_valid(self):
        """Test carga de adjustments válido."""
        adjustments_data = {
            "case_sensitive": False,
            "reference_replacements": {"teh": "the"},
            "equivalences": {"want_to": ["want to", "wanna"]},
            "clean_up": ["uh", "ah"]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(adjustments_data, f)
            temp_path = Path(f.name)
        
        try:
            result = load_adjustments(temp_path)
            assert result == adjustments_data
        finally:
            temp_path.unlink()
    
    def test_load_adjustments_file_not_found(self):
        """Test que lanza error si el archivo no existe."""
        fake_path = Path("/nonexistent/adjustments.json")
        with pytest.raises(FileNotFoundError):
            load_adjustments(fake_path)
    
    def test_load_adjustments_invalid_json(self):
        """Test que lanza error con JSON inválido."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Error parsing adjustments JSON"):
                load_adjustments(temp_path)
        finally:
            temp_path.unlink()
    
    def test_load_adjustments_invalid_key(self):
        """Test que lanza error con clave inválida."""
        adjustments_data = {"invalid_key": "value"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(adjustments_data, f)
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Unknown key"):
                load_adjustments(temp_path)
        finally:
            temp_path.unlink()
    
    def test_load_adjustments_invalid_type(self):
        """Test que lanza error con tipo inválido."""
        adjustments_data = {"reference_replacements": "should be dict"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(adjustments_data, f)
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="must be an object"):
                load_adjustments(temp_path)
        finally:
            temp_path.unlink()


class TestApplyReferenceReplacements:
    """Tests para apply_reference_replacements."""
    
    def test_apply_reference_replacements_basic(self):
        """Test reemplazo básico."""
        text = "teh cat"
        replacements = {"teh": "the"}
        result = apply_reference_replacements(text, replacements)
        assert result == "the cat"
    
    def test_apply_reference_replacements_word_boundaries(self):
        """Test que respeta word boundaries."""
        text = "tehater"
        replacements = {"teh": "the"}
        result = apply_reference_replacements(text, replacements)
        assert result == "tehater"  # No debe reemplazar porque no hay word boundary
    
    def test_apply_reference_replacements_case_sensitive(self):
        """Test reemplazo case-sensitive."""
        text = "Teh cat"
        replacements = {"teh": "the"}
        result = apply_reference_replacements(text, replacements, case_sensitive=True)
        assert result == "Teh cat"  # No reemplaza porque es case-sensitive
    
    def test_apply_reference_replacements_case_insensitive(self):
        """Test reemplazo case-insensitive."""
        text = "Teh cat"
        replacements = {"teh": "the"}
        result = apply_reference_replacements(text, replacements, case_sensitive=False)
        assert result == "the cat"


class TestApplyEquivalences:
    """Tests para apply_equivalences."""
    
    def test_apply_equivalences_basic(self):
        """Test equivalencias básicas."""
        text = "wanna go"
        equivalences = {"want_to": ["want to", "wanna"]}
        result = apply_equivalences(text, equivalences)
        assert result == "want to go"
    
    def test_apply_equivalences_multiple_variants(self):
        """Test con múltiples variantes."""
        text = "wanna gonna"
        equivalences = {
            "want_to": ["want to", "wanna"],
            "going_to": ["going to", "gonna"]
        }
        result = apply_equivalences(text, equivalences)
        assert "want to" in result
        assert "going to" in result
    
    def test_apply_equivalences_case_sensitive(self):
        """Test equivalencias case-sensitive."""
        text = "Wanna go"
        equivalences = {"want_to": ["want to", "wanna"]}
        result = apply_equivalences(text, equivalences, case_sensitive=True)
        assert result == "Wanna go"  # No reemplaza porque es case-sensitive


class TestApplyCleanUp:
    """Tests para apply_clean_up."""
    
    def test_apply_clean_up_basic(self):
        """Test limpieza básica."""
        text = "uh hello ah world"
        clean_up_list = ["uh", "ah"]
        result = apply_clean_up(text, clean_up_list)
        assert result == "hello world"
    
    def test_apply_clean_up_normalizes_spaces(self):
        """Test que normaliza espacios después de limpiar."""
        text = "uh  hello  ah"
        clean_up_list = ["uh", "ah"]
        result = apply_clean_up(text, clean_up_list)
        assert result == "hello"
    
    def test_apply_clean_up_case_sensitive(self):
        """Test limpieza case-sensitive."""
        text = "Uh hello"
        clean_up_list = ["uh"]
        result = apply_clean_up(text, clean_up_list, case_sensitive=True)
        assert result == "Uh hello"  # No remueve porque es case-sensitive


class TestApplyAdjustments:
    """Tests para apply_adjustments."""
    
    def test_apply_adjustments_full_workflow(self):
        """Test aplicación completa de adjustments."""
        reference = "teh cat wanna go"
        hypothesis = "the cat wanna go"
        adjustments = {
            "case_sensitive": False,
            "reference_replacements": {"teh": "the"},
            "equivalences": {"want_to": ["want to", "wanna"]},
            "clean_up": []
        }
        
        ref_result, hyp_result = apply_adjustments(reference, hypothesis, adjustments)
        assert "the" in ref_result  # Reemplazo aplicado
        assert "want to" in ref_result  # Equivalencia aplicada
        assert "want to" in hyp_result  # Equivalencia aplicada
    
    def test_apply_adjustments_only_reference_replacements(self):
        """Test que reference_replacements solo se aplica a reference."""
        reference = "teh cat"
        hypothesis = "teh cat"
        adjustments = {
            "reference_replacements": {"teh": "the"},
            "equivalences": {},
            "clean_up": []
        }
        
        ref_result, hyp_result = apply_adjustments(reference, hypothesis, adjustments)
        assert ref_result == "the cat"
        assert hyp_result == "teh cat"  # No se aplica a hypothesis
    
    def test_apply_adjustments_empty_adjustments(self):
        """Test con adjustments vacío."""
        reference = "hello world"
        hypothesis = "hello world"
        adjustments = {}
        
        ref_result, hyp_result = apply_adjustments(reference, hypothesis, adjustments)
        assert ref_result == reference
        assert hyp_result == hypothesis

