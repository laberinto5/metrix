"""
Module for handling input file reading (TRN and compact CSV).
This module now uses input_validator for all validation.
"""

from pathlib import Path
from typing import List, Tuple, Optional

try:
    from .input_validator import (
        validate_trn_pair,
        validate_compact_csv
    )
except ImportError:
    from input_validator import (
        validate_trn_pair,
        validate_compact_csv
    )


def load_inputs(
    hypothesis_path: Optional[Path] = None,
    reference_path: Optional[Path] = None,
    compact_input_path: Optional[Path] = None,
    sclite_format: bool = False
) -> List[Tuple[str, str, str]]:
    """
    Loads inputs from TRN files or compact CSV with full validation.
    
    This function validates:
    - UTF-8 encoding
    - TRN format (native or sclite)
    - Matching IDs between hypothesis and reference
    - CSV format and structure
    
    Args:
        hypothesis_path: Path to the hypothesis TRN file
        reference_path: Path to the reference TRN file
        compact_input_path: Path to the compact CSV file
        sclite_format: If True, TRN files are in sclite format
    
    Returns:
        List of tuples (id, reference, hypothesis)
    
    Raises:
        ValueError: If options are incompatible or there are format errors
        FileNotFoundError: If files don't exist
    """
    # Validate that correct options are provided
    if compact_input_path is not None:
        if hypothesis_path is not None or reference_path is not None:
            raise ValueError(
                "Options --compact-input (-ci) and --hypothesis/--reference (-h/-r) "
                "are mutually exclusive. Use one or the other."
            )
        
        # Load and validate compact CSV
        # validate_compact_csv handles encoding, format, and structure validation
        return validate_compact_csv(compact_input_path)
    
    else:
        if hypothesis_path is None or reference_path is None:
            raise ValueError(
                "Must provide both --hypothesis (-h) and --reference (-r), "
                "or use --compact-input (-ci)"
            )
        
        # Load and validate TRN pair
        # validate_trn_pair handles encoding, format, and ID matching validation
        return validate_trn_pair(hypothesis_path, reference_path, sclite_format)
