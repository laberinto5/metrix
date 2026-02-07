"""
Tests unitarios para el módulo output_generator.
"""

import pytest
import json
import csv
import tempfile
from pathlib import Path
from src.output_generator import (
    generate_csv_output,
    generate_json_output,
    generate_report,
    resolve_output_paths,
    check_and_confirm_overwrite
)


class TestGenerateCsvOutput:
    """Tests para generate_csv_output."""
    
    def test_generate_csv_output_wer(self):
        """Test generación de CSV para WER."""
        metrics = {
            'word_count': 10,
            'wer': 0.1,
            'word_accuracy': 0.9,
            'deletions': 1,
            'insertions': 0,
            'substitutions': 0,
            'correct': 9,
            'total_sentences': 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            generate_csv_output(metrics, temp_path, metric_type='wer')
            
            # Verificar que el archivo existe y tiene contenido
            assert temp_path.exists()
            with open(temp_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                row = next(reader)
                assert 'Word Count' in row
                assert 'WER' in row
        finally:
            temp_path.unlink()
    
    def test_generate_csv_output_cer(self):
        """Test generación de CSV para CER."""
        metrics = {
            'character_count': 50,
            'cer': 0.05,
            'character_accuracy': 0.95,
            'deletions': 1,
            'insertions': 0,
            'substitutions': 1,
            'correct': 48,
            'total_sentences': 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            generate_csv_output(metrics, temp_path, metric_type='cer')
            assert temp_path.exists()
        finally:
            temp_path.unlink()


class TestGenerateJsonOutput:
    """Tests para generate_json_output."""
    
    def test_generate_json_output(self):
        """Test generación de JSON."""
        metrics = {
            'wer': 0.1,
            'word_count': 10,
            'correct': 9
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            generate_json_output(metrics, temp_path)
            
            # Verificar que el archivo existe y es JSON válido
            assert temp_path.exists()
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data['wer'] == 0.1
                assert data['word_count'] == 10
        finally:
            temp_path.unlink()


class TestGenerateReport:
    """Tests para generate_report."""
    
    def test_generate_report_basic(self):
        """Test generación de reporte básico."""
        metrics = {
            'wer': 0.1,
            'word_count': 10,
            'word_accuracy': 0.9,
            'deletions': 1,
            'insertions': 0,
            'substitutions': 0,
            'correct': 9,
            'total_sentences': 1
        }
        
        alignments = [{
            'reference': 'hello world',
            'hypothesis': 'hello world',
            'alignment': [],
            'metrics': {}
        }]
        
        config = {
            'hypothesis_file': 'hyp.trn',
            'reference_file': 'ref.trn'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            generate_report(metrics, alignments, config, temp_path, metric_type='wer')
            assert temp_path.exists()
            
            # Verificar que el reporte contiene información esperada
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'WER' in content or 'wer' in content.lower()
                assert 'hello world' in content
        finally:
            temp_path.unlink()


class TestResolveOutputPaths:
    """Tests para resolve_output_paths."""
    
    def test_resolve_output_paths_directory(self):
        """Test resolución de rutas cuando se proporciona un directorio."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            paths = resolve_output_paths(base_path, metric_type='wer')
            
            assert 'csv' in paths
            assert 'json' in paths
            assert 'report' in paths
            assert 'wer_metrics.csv' in str(paths['csv'])
            assert 'wer_metrics.json' in str(paths['json'])
            assert 'wer_report.txt' in str(paths['report'])
    
    def test_resolve_output_paths_file(self):
        """Test resolución de rutas cuando se proporciona un archivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "output"
            paths = resolve_output_paths(base_path, metric_type='cer')
            
            assert paths['csv'].stem == "output"
            assert paths['json'].stem == "output"
            assert "output_report" in paths['report'].stem


class TestCheckAndConfirmOverwrite:
    """Tests para check_and_confirm_overwrite."""
    
    def test_check_and_confirm_overwrite_no_existing_files(self):
        """Test cuando no hay archivos existentes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = {
                'csv': Path(tmpdir) / 'test.csv',
                'json': Path(tmpdir) / 'test.json',
                'report': Path(tmpdir) / 'test.txt'
            }
            result = check_and_confirm_overwrite(paths)
            assert result is True
    
    def test_check_and_confirm_overwrite_existing_files(self):
        """Test cuando hay archivos existentes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / 'test.csv'
            csv_path.touch()
            
            paths = {
                'csv': csv_path,
                'json': Path(tmpdir) / 'test.json',
                'report': Path(tmpdir) / 'test.txt'
            }
            # Por ahora siempre retorna True (confirmación interactiva pendiente)
            result = check_and_confirm_overwrite(paths)
            assert result is True

