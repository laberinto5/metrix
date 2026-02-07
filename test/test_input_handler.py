"""
Unit tests for input_handler module.
Note: parse_trn_file and parse_compact_csv are now internal functions.
Tests for parsing functionality are in test_input_validator.py.
This module tests load_inputs which uses the validation functions.
"""

import pytest
import tempfile
from pathlib import Path
from src.input_handler import load_inputs


class TestLoadInputs:
    """Tests for load_inputs."""
    
    def test_load_inputs_from_trn_files(self):
        """Test loading from TRN files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as hyp_file:
            hyp_file.write("audio0001.wav: hypothesis one\n")
            hyp_file.write("audio0002.wav: hypothesis two\n")
            hyp_path = Path(hyp_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as ref_file:
            ref_file.write("audio0001.wav: reference one\n")
            ref_file.write("audio0002.wav: reference two\n")
            ref_path = Path(ref_file.name)
        
        try:
            results = load_inputs(hypothesis_path=hyp_path, reference_path=ref_path)
            assert len(results) == 2
            assert results[0][0] == "audio0001.wav"
            assert results[0][1] == "reference one"
            assert results[0][2] == "hypothesis one"
        finally:
            hyp_path.unlink()
            ref_path.unlink()
    
    def test_load_inputs_from_compact_csv(self):
        """Test loading from compact CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("ID,reference,hypothesis\n")
            f.write("audio0001.wav,ref one,hyp one\n")
            temp_path = Path(f.name)
        
        try:
            results = load_inputs(compact_input_path=temp_path)
            assert len(results) == 1
            assert results[0] == ("audio0001.wav", "ref one", "hyp one")
        finally:
            temp_path.unlink()
    
    def test_load_inputs_incompatible_options(self):
        """Test that raises error with incompatible options."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as hyp_file:
            hyp_file.write("audio0001.wav: test\n")
            hyp_path = Path(hyp_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as csv_file:
            csv_file.write("ID,reference,hypothesis\n")
            csv_file.write("audio0001.wav,ref,hyp\n")
            csv_path = Path(csv_file.name)
        
        try:
            with pytest.raises(ValueError, match="mutually exclusive"):
                load_inputs(hypothesis_path=hyp_path, compact_input_path=csv_path)
        finally:
            hyp_path.unlink()
            csv_path.unlink()
    
    def test_load_inputs_missing_both_trn(self):
        """Test that raises error if both TRN files are missing."""
        with pytest.raises(ValueError, match="Must provide both"):
            load_inputs(hypothesis_path=None, reference_path=None)
    
    def test_load_inputs_file_not_found(self):
        """Test that raises error if file does not exist."""
        fake_path = Path("/nonexistent/file.trn")
        with pytest.raises(FileNotFoundError):
            load_inputs(hypothesis_path=fake_path, reference_path=fake_path)
    
    def test_load_inputs_mismatched_ids(self):
        """Test that raises error when IDs don't match between hyp and ref."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as hyp_file:
            hyp_file.write("audio0001.wav: hyp one\n")
            hyp_file.write("audio0002.wav: hyp two\n")
            hyp_path = Path(hyp_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as ref_file:
            ref_file.write("audio0001.wav: ref one\n")
            ref_file.write("audio0003.wav: ref three\n")  # ID diferente
            ref_path = Path(ref_file.name)
        
        try:
            # Now validation should fail when IDs don't match
            with pytest.raises(ValueError, match="missing.*expected ID|unexpected ID"):
                load_inputs(hypothesis_path=hyp_path, reference_path=ref_path)
        finally:
            hyp_path.unlink()
            ref_path.unlink()
    
    def test_load_inputs_spanish_utf8_trn(self):
        """Test loading TRN files with Spanish text in UTF-8."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as hyp_file:
            hyp_file.write("id1: El niño comió una manzana\n")
            hyp_file.write("id2: ¿Dónde está la niña?\n")
            hyp_path = Path(hyp_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as ref_file:
            ref_file.write("id1: El niño comió una manzana\n")
            ref_file.write("id2: ¿Dónde está la niña?\n")
            ref_path = Path(ref_file.name)
        
        try:
            results = load_inputs(hypothesis_path=hyp_path, reference_path=ref_path)
            assert len(results) == 2
            assert results[0][1] == "El niño comió una manzana"
            assert results[0][2] == "El niño comió una manzana"
            assert results[1][1] == "¿Dónde está la niña?"
            assert results[1][2] == "¿Dónde está la niña?"
        finally:
            hyp_path.unlink()
            ref_path.unlink()
    
    def test_load_inputs_spanish_utf8_csv(self):
        """Test loading CSV file with Spanish text in UTF-8."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("ID,reference,hypothesis\n")
            f.write("id1,El niño comió una manzana,El niño comió una manzana\n")
            f.write("id2,¿Dónde está la niña?,¿Dónde está la niña?\n")
            temp_path = Path(f.name)
        
        try:
            results = load_inputs(compact_input_path=temp_path)
            assert len(results) == 2
            assert results[0] == ("id1", "El niño comió una manzana", "El niño comió una manzana")
            assert results[1] == ("id2", "¿Dónde está la niña?", "¿Dónde está la niña?")
        finally:
            temp_path.unlink()
    
    def test_load_inputs_spanish_iso8859_trn_fails(self):
        """Test loading TRN files with Spanish text in ISO-8859-1 fails."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.trn', delete=False) as hyp_file:
            hyp_file.write("id1: El niño comió una manzana\n".encode('iso-8859-1'))
            hyp_path = Path(hyp_file.name)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.trn', delete=False) as ref_file:
            ref_file.write("id1: El niño comió una manzana\n".encode('iso-8859-1'))
            ref_path = Path(ref_file.name)
        
        try:
            with pytest.raises(ValueError, match="not encoded in UTF-8"):
                load_inputs(hypothesis_path=hyp_path, reference_path=ref_path)
        finally:
            hyp_path.unlink()
            ref_path.unlink()
    
    def test_load_inputs_spanish_iso8859_csv_fails(self):
        """Test loading CSV file with Spanish text in ISO-8859-1 fails."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            csv_content = "ID,reference,hypothesis\nid1,El niño,El niño\n"
            f.write(csv_content.encode('iso-8859-1'))
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="not encoded in UTF-8"):
                load_inputs(compact_input_path=temp_path)
        finally:
            temp_path.unlink()
    
    def test_load_inputs_portuguese_utf8(self):
        """Test loading files with Portuguese text in UTF-8."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as hyp_file:
            hyp_file.write("id1: O menino comeu uma maçã\n")
            hyp_file.write("id2: Onde está a menina?\n")
            hyp_path = Path(hyp_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as ref_file:
            ref_file.write("id1: O menino comeu uma maçã\n")
            ref_file.write("id2: Onde está a menina?\n")
            ref_path = Path(ref_file.name)
        
        try:
            results = load_inputs(hypothesis_path=hyp_path, reference_path=ref_path)
            assert len(results) == 2
            assert results[0][1] == "O menino comeu uma maçã"
            assert results[1][1] == "Onde está a menina?"
        finally:
            hyp_path.unlink()
            ref_path.unlink()

