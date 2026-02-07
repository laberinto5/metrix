"""
Module for handling input file reading (TRN and compact CSV).
"""

import re
import csv
from pathlib import Path
from typing import List, Tuple, Optional


def parse_trn_file(file_path: Path, sclite_format: bool = False) -> List[Tuple[str, str]]:
    """
    Parses a TRN file and returns a list of tuples (id, text).
    
    Args:
        file_path: Path to the TRN file
        sclite_format: If True, expects sclite format "sentence (ID)"
                       If False, expects native format "ID: sentence"
    
    Returns:
        List of tuples (id, text)
    """
    results = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            try:
                if sclite_format:
                    # Sclite format: "sentence (ID)"
                    # Search for pattern: text followed by (id) at the end
                    match = re.match(r'^(.+?)\s+\(([^)]+)\)\s*$', line)
                    if match:
                        text, id_str = match.groups()
                        results.append((id_str.strip(), text.strip()))
                    else:
                        raise ValueError(f"Invalid sclite format at line {line_num}: {line}")
                else:
                    # Native format: "ID: sentence"
                    if ':' not in line:
                        raise ValueError(f"Invalid native format at line {line_num}: missing ':' in {line}")
                    
                    parts = line.split(':', 1)  # Split only at the first ':'
                    if len(parts) != 2:
                        raise ValueError(f"Invalid native format at line {line_num}: {line}")
                    
                    id_str, text = parts
                    results.append((id_str.strip(), text.strip()))
            except Exception as e:
                raise ValueError(f"Error parsing line {line_num} of {file_path}: {e}")
    
    return results


def parse_compact_csv(file_path: Path) -> List[Tuple[str, str, str]]:
    """
    Parses a compact CSV file with columns: ID, reference, hypothesis.
    
    Args:
        file_path: Path to the CSV file
    
    Returns:
        List of tuples (id, reference, hypothesis)
    """
    results = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate required columns
        required_columns = {'ID', 'reference', 'hypothesis'}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV must have columns: ID, reference, hypothesis. "
                f"Found: {reader.fieldnames}"
            )
        
        for row_num, row in enumerate(reader, 2):  # Start at 2 because row 1 is the header
            id_str = row.get('ID', '').strip()
            reference = row.get('reference', '').strip()
            hypothesis = row.get('hypothesis', '').strip()
            
            if not id_str:
                raise ValueError(f"Row {row_num}: ID cannot be empty")
            
            results.append((id_str, reference, hypothesis))
    
    return results


def load_inputs(
    hypothesis_path: Optional[Path] = None,
    reference_path: Optional[Path] = None,
    compact_input_path: Optional[Path] = None,
    sclite_format: bool = False
) -> List[Tuple[str, str, str]]:
    """
    Loads inputs from TRN files or compact CSV.
    
    Args:
        hypothesis_path: Path to the hypothesis TRN file
        reference_path: Path to the reference TRN file
        compact_input_path: Path to the compact CSV file
        sclite_format: If True, TRN files are in sclite format
    
    Returns:
        List of tuples (id, reference, hypothesis)
    
    Raises:
        ValueError: If options are incompatible or there are format errors
    """
    # Validate that correct options are provided
    if compact_input_path is not None:
        if hypothesis_path is not None or reference_path is not None:
            raise ValueError(
                "Options --compact-input (-ci) and --hypothesis/--reference (-h/-r) "
                "are mutually exclusive. Use one or the other."
            )
        
        # Load from compact CSV
        return parse_compact_csv(compact_input_path)
    
    else:
        if hypothesis_path is None or reference_path is None:
            raise ValueError(
                "Must provide both --hypothesis (-h) and --reference (-r), "
                "or use --compact-input (-ci)"
            )
        
        # Validate that files exist
        if not hypothesis_path.exists():
            raise FileNotFoundError(f"Hypothesis file not found: {hypothesis_path}")
        if not reference_path.exists():
            raise FileNotFoundError(f"Reference file not found: {reference_path}")
        
        # Load from TRN files
        hypotheses = parse_trn_file(hypothesis_path, sclite_format)
        references = parse_trn_file(reference_path, sclite_format)
        
        # Convert to dictionaries to match by ID
        hyp_dict = {id_str: text for id_str, text in hypotheses}
        ref_dict = {id_str: text for id_str, text in references}
        
        # Get all unique IDs
        all_ids = set(hyp_dict.keys()) | set(ref_dict.keys())
        
        # Create list of tuples (id, reference, hypothesis)
        results = []
        for id_str in sorted(all_ids):
            ref_text = ref_dict.get(id_str, '')
            hyp_text = hyp_dict.get(id_str, '')
            results.append((id_str, ref_text, hyp_text))
        
        return results
