"""
Unit tests for input_validator module.
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.input_validator import (
    validate_utf8_encoding,
    validate_trn_format,
    validate_trn_pair,
    validate_compact_csv,
    validate_adjustments_structure,
    validate_adjustments_consistency,
    validate_adjustments
)


class TestValidateUtf8Encoding:
    """Tests for UTF-8 encoding validation."""
    
    def test_validate_utf8_encoding_valid(self, tmp_path):
        """Test validation of valid UTF-8 file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Hello world", encoding='utf-8')
        
        # Should not raise
        validate_utf8_encoding(file_path)
    
    def test_validate_utf8_encoding_file_not_found(self):
        """Test validation raises error for non-existent file."""
        file_path = Path("/nonexistent/file.txt")
        
        with pytest.raises(FileNotFoundError):
            validate_utf8_encoding(file_path)
    
    def test_validate_utf8_encoding_invalid(self, tmp_path):
        """Test validation raises error for non-UTF-8 file."""
        file_path = tmp_path / "test.txt"
        # Write Latin-1 encoded file
        file_path.write_bytes(b'\xe9')  # é in Latin-1
        
        with pytest.raises(ValueError, match="not encoded in UTF-8"):
            validate_utf8_encoding(file_path)
    
    def test_validate_utf8_encoding_spanish_utf8(self, tmp_path):
        """Test validation passes for Spanish text in UTF-8."""
        file_path = tmp_path / "test.txt"
        # Spanish text with special characters in UTF-8
        spanish_text = "El niño comió una manzana. ¿Dónde está la niña?"
        file_path.write_text(spanish_text, encoding='utf-8')
        
        # Should not raise
        validate_utf8_encoding(file_path)
    
    def test_validate_utf8_encoding_spanish_iso8859(self, tmp_path):
        """Test validation fails for Spanish text in ISO-8859-1."""
        file_path = tmp_path / "test.txt"
        # Spanish text with special characters in ISO-8859-1
        spanish_text = "El niño comió una manzana. ¿Dónde está la niña?"
        file_path.write_bytes(spanish_text.encode('iso-8859-1'))
        
        with pytest.raises(ValueError, match="not encoded in UTF-8"):
            validate_utf8_encoding(file_path)
    
    def test_validate_utf8_encoding_portuguese_utf8(self, tmp_path):
        """Test validation passes for Portuguese text in UTF-8."""
        file_path = tmp_path / "test.txt"
        # Portuguese text with special characters in UTF-8
        portuguese_text = "O menino comeu uma maçã. Onde está a menina?"
        file_path.write_text(portuguese_text, encoding='utf-8')
        
        # Should not raise
        validate_utf8_encoding(file_path)
    
    def test_validate_utf8_encoding_portuguese_iso8859(self, tmp_path):
        """Test validation fails for Portuguese text in ISO-8859-1."""
        file_path = tmp_path / "test.txt"
        # Portuguese text with special characters in ISO-8859-1
        portuguese_text = "O menino comeu uma maçã. Onde está a menina?"
        file_path.write_bytes(portuguese_text.encode('iso-8859-1'))
        
        with pytest.raises(ValueError, match="not encoded in UTF-8"):
            validate_utf8_encoding(file_path)


class TestValidateTrnFormat:
    """Tests for TRN format validation."""
    
    def test_validate_trn_format_native_valid(self, tmp_path):
        """Test validation of valid native format TRN."""
        file_path = tmp_path / "test.trn"
        file_path.write_text("id1: hello world\nid2: test sentence", encoding='utf-8')
        
        results, ids = validate_trn_format(file_path, sclite_format=False)
        
        assert len(results) == 2
        assert ids == {'id1', 'id2'}
        assert results[0] == ('id1', 'hello world')
        assert results[1] == ('id2', 'test sentence')
    
    def test_validate_trn_format_sclite_valid(self, tmp_path):
        """Test validation of valid sclite format TRN."""
        file_path = tmp_path / "test.trn"
        file_path.write_text("hello world (id1)\ntest sentence (id2)", encoding='utf-8')
        
        results, ids = validate_trn_format(file_path, sclite_format=True)
        
        assert len(results) == 2
        assert ids == {'id1', 'id2'}
        assert results[0] == ('id1', 'hello world')
        assert results[1] == ('id2', 'test sentence')
    
    def test_validate_trn_format_native_invalid_missing_colon(self, tmp_path):
        """Test validation fails for native format without colon."""
        file_path = tmp_path / "test.trn"
        file_path.write_text("id1 hello world", encoding='utf-8')
        
        with pytest.raises(ValueError, match="Missing ':'"):
            validate_trn_format(file_path, sclite_format=False)
    
    def test_validate_trn_format_sclite_invalid(self, tmp_path):
        """Test validation fails for invalid sclite format."""
        file_path = tmp_path / "test.trn"
        file_path.write_text("hello world id1", encoding='utf-8')
        
        with pytest.raises(ValueError, match="Invalid sclite format"):
            validate_trn_format(file_path, sclite_format=True)
    
    def test_validate_trn_format_empty_id(self, tmp_path):
        """Test validation fails for empty ID."""
        file_path = tmp_path / "test.trn"
        file_path.write_text(": hello world", encoding='utf-8')
        
        with pytest.raises(ValueError, match="Empty ID"):
            validate_trn_format(file_path, sclite_format=False)
    
    def test_validate_trn_format_duplicate_id(self, tmp_path):
        """Test validation fails for duplicate IDs."""
        file_path = tmp_path / "test.trn"
        file_path.write_text("id1: hello\nid1: world", encoding='utf-8')
        
        with pytest.raises(ValueError, match="Duplicate ID"):
            validate_trn_format(file_path, sclite_format=False)
    
    def test_validate_trn_format_expected_ids_match(self, tmp_path):
        """Test validation with expected IDs that match."""
        file_path = tmp_path / "test.trn"
        file_path.write_text("id1: hello\nid2: world", encoding='utf-8')
        
        results, ids = validate_trn_format(file_path, sclite_format=False, expected_ids={'id1', 'id2'})
        assert ids == {'id1', 'id2'}
    
    def test_validate_trn_format_expected_ids_missing(self, tmp_path):
        """Test validation fails when expected IDs are missing."""
        file_path = tmp_path / "test.trn"
        file_path.write_text("id1: hello", encoding='utf-8')
        
        with pytest.raises(ValueError, match="missing.*expected ID"):
            validate_trn_format(file_path, sclite_format=False, expected_ids={'id1', 'id2'})
    
    def test_validate_trn_format_expected_ids_extra(self, tmp_path):
        """Test validation fails when there are extra IDs."""
        file_path = tmp_path / "test.trn"
        file_path.write_text("id1: hello\nid2: world\nid3: test", encoding='utf-8')
        
        with pytest.raises(ValueError, match="unexpected ID"):
            validate_trn_format(file_path, sclite_format=False, expected_ids={'id1', 'id2'})
    
    def test_validate_trn_format_spanish_utf8(self, tmp_path):
        """Test validation works with Spanish text in UTF-8."""
        file_path = tmp_path / "test.trn"
        file_path.write_text(
            "id1: El niño comió una manzana\n"
            "id2: ¿Dónde está la niña?\n"
            "id3: La calle tiene aceras",
            encoding='utf-8'
        )
        
        results, ids = validate_trn_format(file_path, sclite_format=False)
        
        assert len(results) == 3
        assert results[0][1] == "El niño comió una manzana"
        assert results[1][1] == "¿Dónde está la niña?"
        assert results[2][1] == "La calle tiene aceras"
    
    def test_validate_trn_format_spanish_sclite_utf8(self, tmp_path):
        """Test validation works with Spanish text in sclite format UTF-8."""
        file_path = tmp_path / "test.trn"
        file_path.write_text(
            "El niño comió una manzana (id1)\n"
            "¿Dónde está la niña? (id2)",
            encoding='utf-8'
        )
        
        results, ids = validate_trn_format(file_path, sclite_format=True)
        
        assert len(results) == 2
        assert results[0] == ('id1', 'El niño comió una manzana')
        assert results[1] == ('id2', '¿Dónde está la niña?')
    
    def test_validate_trn_format_spanish_iso8859_fails(self, tmp_path):
        """Test validation fails for Spanish text in ISO-8859-1."""
        file_path = tmp_path / "test.trn"
        # Write in ISO-8859-1
        spanish_text = "id1: El niño comió una manzana"
        file_path.write_bytes(spanish_text.encode('iso-8859-1'))
        
        with pytest.raises(ValueError, match="not encoded in UTF-8"):
            validate_trn_format(file_path, sclite_format=False)


class TestValidateTrnPair:
    """Tests for TRN pair validation."""
    
    def test_validate_trn_pair_matching_ids(self, tmp_path):
        """Test validation of TRN pair with matching IDs."""
        hyp_path = tmp_path / "hyp.trn"
        ref_path = tmp_path / "ref.trn"
        
        hyp_path.write_text("id1: hello\nid2: world", encoding='utf-8')
        ref_path.write_text("id1: hi\nid2: universe", encoding='utf-8')
        
        results = validate_trn_pair(hyp_path, ref_path, sclite_format=False)
        
        assert len(results) == 2
        assert results[0] == ('id1', 'hi', 'hello')
        assert results[1] == ('id2', 'universe', 'world')
    
    def test_validate_trn_pair_mismatched_ids(self, tmp_path):
        """Test validation fails when IDs don't match."""
        hyp_path = tmp_path / "hyp.trn"
        ref_path = tmp_path / "ref.trn"
        
        hyp_path.write_text("id1: hello", encoding='utf-8')
        ref_path.write_text("id2: hi", encoding='utf-8')
        
        with pytest.raises(ValueError, match="missing.*expected ID"):
            validate_trn_pair(hyp_path, ref_path, sclite_format=False)


class TestValidateCompactCsv:
    """Tests for compact CSV validation."""
    
    def test_validate_compact_csv_valid(self, tmp_path):
        """Test validation of valid compact CSV."""
        file_path = tmp_path / "test.csv"
        file_path.write_text(
            "ID,reference,hypothesis\n"
            "id1,hello world,hi universe\n"
            "id2,test,check",
            encoding='utf-8'
        )
        
        results = validate_compact_csv(file_path)
        
        assert len(results) == 2
        assert results[0] == ('id1', 'hello world', 'hi universe')
        assert results[1] == ('id2', 'test', 'check')
    
    def test_validate_compact_csv_missing_columns(self, tmp_path):
        """Test validation fails when required columns are missing."""
        file_path = tmp_path / "test.csv"
        file_path.write_text("ID,reference\nid1,hello", encoding='utf-8')
        
        with pytest.raises(ValueError, match="Missing columns"):
            validate_compact_csv(file_path)
    
    def test_validate_compact_csv_empty_id(self, tmp_path):
        """Test validation fails for empty ID."""
        file_path = tmp_path / "test.csv"
        file_path.write_text(
            "ID,reference,hypothesis\n"
            ",hello,hi",
            encoding='utf-8'
        )
        
        with pytest.raises(ValueError, match="ID cannot be empty"):
            validate_compact_csv(file_path)
    
    def test_validate_compact_csv_duplicate_id(self, tmp_path):
        """Test validation fails for duplicate IDs."""
        file_path = tmp_path / "test.csv"
        file_path.write_text(
            "ID,reference,hypothesis\n"
            "id1,hello,hi\n"
            "id1,world,universe",
            encoding='utf-8'
        )
        
        with pytest.raises(ValueError, match="Duplicate ID"):
            validate_compact_csv(file_path)
    
    def test_validate_compact_csv_case_insensitive_columns(self, tmp_path):
        """Test validation works with case-insensitive column names."""
        file_path = tmp_path / "test.csv"
        file_path.write_text(
            "id,Reference,Hypothesis\n"
            "id1,hello,hi",
            encoding='utf-8'
        )
        
        results = validate_compact_csv(file_path)
        assert len(results) == 1
        assert results[0] == ('id1', 'hello', 'hi')
    
    def test_validate_compact_csv_spanish_utf8(self, tmp_path):
        """Test validation works with Spanish text in UTF-8 CSV."""
        file_path = tmp_path / "test.csv"
        file_path.write_text(
            "ID,reference,hypothesis\n"
            "id1,El niño comió una manzana,El niño comió una manzana\n"
            "id2,¿Dónde está la niña?,¿Dónde está la niña?",
            encoding='utf-8'
        )
        
        results = validate_compact_csv(file_path)
        
        assert len(results) == 2
        assert results[0] == ('id1', 'El niño comió una manzana', 'El niño comió una manzana')
        assert results[1] == ('id2', '¿Dónde está la niña?', '¿Dónde está la niña?')
    
    def test_validate_compact_csv_spanish_iso8859_fails(self, tmp_path):
        """Test validation fails for Spanish text in ISO-8859-1 CSV."""
        file_path = tmp_path / "test.csv"
        # Write header in UTF-8, but data in ISO-8859-1 would fail
        # Actually, we need to write the whole file in ISO-8859-1
        csv_content = "ID,reference,hypothesis\nid1,El niño,El niño"
        file_path.write_bytes(csv_content.encode('iso-8859-1'))
        
        with pytest.raises(ValueError, match="not encoded in UTF-8"):
            validate_compact_csv(file_path)


class TestValidateAdjustmentsStructure:
    """Tests for adjustments JSON structure validation."""
    
    def test_validate_adjustments_structure_valid(self, tmp_path):
        """Test validation of valid adjustments JSON."""
        file_path = tmp_path / "adjustments.json"
        data = {
            "reference_replacements": {"want_to": "want to"},
            "equivalences": {"canonical": ["variant1", "variant2"]},
            "clean_up": ["word1", "word2"],
            "case_sensitive": False
        }
        file_path.write_text(json.dumps(data), encoding='utf-8')
        
        result = validate_adjustments_structure(file_path)
        assert result == data
    
    def test_validate_adjustments_structure_invalid_json(self, tmp_path):
        """Test validation fails for invalid JSON."""
        file_path = tmp_path / "adjustments.json"
        file_path.write_text("{ invalid json }", encoding='utf-8')
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            validate_adjustments_structure(file_path)
    
    def test_validate_adjustments_structure_unknown_key(self, tmp_path):
        """Test validation fails for unknown keys."""
        file_path = tmp_path / "adjustments.json"
        data = {"unknown_key": "value"}
        file_path.write_text(json.dumps(data), encoding='utf-8')
        
        with pytest.raises(ValueError, match="Unknown key"):
            validate_adjustments_structure(file_path)
    
    def test_validate_adjustments_structure_wrong_type(self, tmp_path):
        """Test validation fails for wrong types."""
        file_path = tmp_path / "adjustments.json"
        data = {"reference_replacements": "not a dict"}
        file_path.write_text(json.dumps(data), encoding='utf-8')
        
        with pytest.raises(ValueError, match="must be an object/dictionary"):
            validate_adjustments_structure(file_path)


class TestValidateAdjustmentsConsistency:
    """Tests for adjustments consistency validation."""
    
    def test_validate_adjustments_consistency_valid(self):
        """Test validation of consistent adjustments."""
        adjustments = {
            "reference_replacements": {"a": "b"},
            "equivalences": {"canonical": ["variant"]},
            "clean_up": ["word"],
            "case_sensitive": False
        }
        
        # Should not raise
        validate_adjustments_consistency(adjustments)
    
    def test_validate_adjustments_consistency_variant_as_canonical(self):
        """Test validation fails when variant is also canonical."""
        adjustments = {
            "equivalences": {
                "canonical1": ["variant"],
                "variant": ["other"]
            }
        }
        
        with pytest.raises(ValueError, match="Equivalence inconsistency"):
            validate_adjustments_consistency(adjustments)
    
    def test_validate_adjustments_consistency_variant_in_replacements(self):
        """Test validation fails when variant appears in reference_replacements."""
        adjustments = {
            "reference_replacements": {"variant": "replacement"},
            "equivalences": {"canonical": ["variant"]}
        }
        
        with pytest.raises(ValueError, match="Equivalence inconsistency"):
            validate_adjustments_consistency(adjustments)
    
    def test_validate_adjustments_consistency_cleanup_in_equivalences(self):
        """Test validation fails when clean_up word is in equivalences."""
        adjustments = {
            "equivalences": {"canonical": ["word"]},
            "clean_up": ["word"]
        }
        
        with pytest.raises(ValueError, match="Clean_up inconsistency"):
            validate_adjustments_consistency(adjustments)


class TestValidateAdjustments:
    """Tests for complete adjustments validation."""
    
    def test_validate_adjustments_complete(self, tmp_path):
        """Test complete validation (structure + consistency)."""
        file_path = tmp_path / "adjustments.json"
        data = {
            "reference_replacements": {"a": "b"},
            "equivalences": {"canonical": ["variant"]},
            "clean_up": ["word"],
            "case_sensitive": False
        }
        file_path.write_text(json.dumps(data), encoding='utf-8')
        
        result = validate_adjustments(file_path)
        assert result == data
    
    def test_validate_adjustments_inconsistent(self, tmp_path):
        """Test validation fails for inconsistent adjustments."""
        file_path = tmp_path / "adjustments.json"
        data = {
            "equivalences": {
                "canonical": ["variant"],
                "variant": ["other"]
            }
        }
        file_path.write_text(json.dumps(data), encoding='utf-8')
        
        with pytest.raises(ValueError, match="inconsistencies"):
            validate_adjustments(file_path)
    
    def test_validate_adjustments_spanish_utf8(self, tmp_path):
        """Test validation works with Spanish text in UTF-8 adjustments."""
        file_path = tmp_path / "adjustments.json"
        data = {
            "reference_replacements": {
                "niño": "niño",
                "mañana": "mañana"
            },
            "equivalences": {
                "canonical": ["variante", "otra variante"]
            },
            "clean_up": ["palabra", "otra palabra"],
            "case_sensitive": False
        }
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        
        result = validate_adjustments(file_path)
        assert result == data
    
    def test_validate_adjustments_spanish_iso8859_fails(self, tmp_path):
        """Test validation fails for Spanish text in ISO-8859-1 adjustments."""
        file_path = tmp_path / "adjustments.json"
        # Write JSON in ISO-8859-1
        json_content = '{"reference_replacements": {"niño": "niño"}}'
        file_path.write_bytes(json_content.encode('iso-8859-1'))
        
        with pytest.raises(ValueError, match="not encoded in UTF-8"):
            validate_adjustments(file_path)

