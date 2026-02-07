"""
Tests unitarios para el módulo input_handler.
"""

import pytest
import tempfile
from pathlib import Path
from src.input_handler import parse_trn_file, parse_compact_csv, load_inputs


class TestParseTrnFile:
    """Tests para parse_trn_file."""
    
    def test_parse_trn_native_format(self):
        """Test parseo de archivo TRN en formato nativo."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as f:
            f.write("audio0001.wav: this is a test\n")
            f.write("audio0002.wav: another sentence\n")
            f.write("audio0003.wav: third line\n")
            temp_path = Path(f.name)
        
        try:
            results = parse_trn_file(temp_path, sclite_format=False)
            assert len(results) == 3
            assert results[0] == ("audio0001.wav", "this is a test")
            assert results[1] == ("audio0002.wav", "another sentence")
            assert results[2] == ("audio0003.wav", "third line")
        finally:
            temp_path.unlink()
    
    def test_parse_trn_sclite_format(self):
        """Test parseo de archivo TRN en formato sclite."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as f:
            f.write("this is a test (audio0001.wav)\n")
            f.write("another sentence (audio0002.wav)\n")
            temp_path = Path(f.name)
        
        try:
            results = parse_trn_file(temp_path, sclite_format=True)
            assert len(results) == 2
            assert results[0] == ("audio0001.wav", "this is a test")
            assert results[1] == ("audio0002.wav", "another sentence")
        finally:
            temp_path.unlink()
    
    def test_parse_trn_skips_empty_lines(self):
        """Test que se saltan líneas vacías."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as f:
            f.write("audio0001.wav: first line\n")
            f.write("\n")
            f.write("audio0002.wav: second line\n")
            temp_path = Path(f.name)
        
        try:
            results = parse_trn_file(temp_path, sclite_format=False)
            assert len(results) == 2
        finally:
            temp_path.unlink()
    
    def test_parse_trn_invalid_native_format(self):
        """Test que lanza error con formato nativo inválido."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as f:
            f.write("no colon here\n")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="missing ':'"):
                parse_trn_file(temp_path, sclite_format=False)
        finally:
            temp_path.unlink()
    
    def test_parse_trn_invalid_sclite_format(self):
        """Test que lanza error con formato sclite inválido."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as f:
            f.write("no parentheses here\n")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Invalid sclite format"):
                parse_trn_file(temp_path, sclite_format=True)
        finally:
            temp_path.unlink()


class TestParseCompactCsv:
    """Tests para parse_compact_csv."""
    
    def test_parse_compact_csv_valid(self):
        """Test parseo de CSV compacto válido."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("ID,reference,hypothesis\n")
            f.write("audio0001.wav,this is a test,this is a test\n")
            f.write("audio0002.wav,another sentence,different sentence\n")
            temp_path = Path(f.name)
        
        try:
            results = parse_compact_csv(temp_path)
            assert len(results) == 2
            assert results[0] == ("audio0001.wav", "this is a test", "this is a test")
            assert results[1] == ("audio0002.wav", "another sentence", "different sentence")
        finally:
            temp_path.unlink()
    
    def test_parse_compact_csv_missing_columns(self):
        """Test que lanza error si faltan columnas."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("ID,reference\n")  # Falta hypothesis
            f.write("audio0001.wav,test\n")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="columns: ID, reference, hypothesis"):
                parse_compact_csv(temp_path)
        finally:
            temp_path.unlink()
    
    def test_parse_compact_csv_empty_id(self):
        """Test que lanza error si ID está vacío."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("ID,reference,hypothesis\n")
            f.write(",test,hyp\n")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="ID cannot be empty"):
                parse_compact_csv(temp_path)
        finally:
            temp_path.unlink()


class TestLoadInputs:
    """Tests para load_inputs."""
    
    def test_load_inputs_from_trn_files(self):
        """Test carga desde archivos TRN."""
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
        """Test carga desde CSV compacto."""
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
        """Test que lanza error con opciones incompatibles."""
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
        """Test que lanza error si faltan ambos archivos TRN."""
        with pytest.raises(ValueError, match="Must provide both"):
            load_inputs(hypothesis_path=None, reference_path=None)
    
    def test_load_inputs_file_not_found(self):
        """Test que lanza error si el archivo no existe."""
        fake_path = Path("/nonexistent/file.trn")
        with pytest.raises(FileNotFoundError):
            load_inputs(hypothesis_path=fake_path, reference_path=fake_path)
    
    def test_load_inputs_mismatched_ids(self):
        """Test que maneja IDs que no coinciden entre hyp y ref."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as hyp_file:
            hyp_file.write("audio0001.wav: hyp one\n")
            hyp_file.write("audio0002.wav: hyp two\n")
            hyp_path = Path(hyp_file.name)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.trn', delete=False, encoding='utf-8') as ref_file:
            ref_file.write("audio0001.wav: ref one\n")
            ref_file.write("audio0003.wav: ref three\n")  # ID diferente
            ref_path = Path(ref_file.name)
        
        try:
            results = load_inputs(hypothesis_path=hyp_path, reference_path=ref_path)
            # Debe incluir todos los IDs, con strings vacíos donde falte
            assert len(results) == 3
            ids = [r[0] for r in results]
            assert "audio0001.wav" in ids
            assert "audio0002.wav" in ids
            assert "audio0003.wav" in ids
        finally:
            hyp_path.unlink()
            ref_path.unlink()

