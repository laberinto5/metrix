"""
Module for validating input files (encoding, format, structure).
"""

import json
import csv
import re
from pathlib import Path
from typing import List, Tuple, Dict, Set, Optional


def validate_utf8_encoding(file_path: Path) -> None:
    """
    Validates that a file is encoded in UTF-8.
    
    Args:
        file_path: Path to the file to validate
    
    Raises:
        ValueError: If file is not UTF-8 encoded
        FileNotFoundError: If file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
    except UnicodeDecodeError as e:
        raise ValueError(
            f"File '{file_path}' is not encoded in UTF-8. "
            f"Please convert the file to UTF-8 encoding. Error: {e}"
        )


def validate_trn_format(
    file_path: Path,
    sclite_format: bool = False,
    expected_ids: Optional[Set[str]] = None
) -> Tuple[List[Tuple[str, str]], Set[str]]:
    """
    Validates TRN file format and returns parsed data.
    
    Args:
        file_path: Path to the TRN file
        sclite_format: If True, expects sclite format "sentence (ID)"
                      If False, expects native format "ID: sentence"
        expected_ids: Optional set of expected IDs (for matching with other file)
    
    Returns:
        Tuple of (list of (id, text) tuples, set of found IDs)
    
    Raises:
        ValueError: If format is invalid or IDs don't match
        FileNotFoundError: If file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"TRN file not found: {file_path}")
    
    # Validate encoding first
    validate_utf8_encoding(file_path)
    
    results = []
    found_ids = set()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\n\r')  # Preserve original line for better error messages
            stripped_line = line.strip()
            
            if not stripped_line:  # Skip empty lines
                continue
            
            try:
                if sclite_format:
                    # Sclite format: "sentence (ID)"
                    # Search for pattern: text followed by (id) at the end
                    match = re.match(r'^(.+?)\s+\(([^)]+)\)\s*$', stripped_line)
                    if not match:
                        raise ValueError(
                            f"Invalid sclite format at line {line_num} in '{file_path}': "
                            f"Expected format 'sentence (ID)'. Got: {line}"
                        )
                    text, id_str = match.groups()
                    id_str = id_str.strip()
                    text = text.strip()
                else:
                    # Native format: "ID: sentence"
                    if ':' not in stripped_line:
                        raise ValueError(
                            f"Invalid native format at line {line_num} in '{file_path}': "
                            f"Expected format 'ID: sentence'. Missing ':' in: {line}"
                        )
                    
                    parts = stripped_line.split(':', 1)  # Split only at the first ':'
                    if len(parts) != 2:
                        raise ValueError(
                            f"Invalid native format at line {line_num} in '{file_path}': "
                            f"Expected format 'ID: sentence'. Got: {line}"
                        )
                    
                    id_str, text = parts
                    id_str = id_str.strip()
                    text = text.strip()
                
                # Validate ID is not empty
                if not id_str:
                    raise ValueError(
                        f"Empty ID at line {line_num} in '{file_path}': {line}"
                    )
                
                # Check for duplicate IDs
                if id_str in found_ids:
                    raise ValueError(
                        f"Duplicate ID '{id_str}' found at line {line_num} in '{file_path}'. "
                        f"Each ID must be unique."
                    )
                
                found_ids.add(id_str)
                results.append((id_str, text))
                
            except ValueError:
                raise  # Re-raise ValueError as-is
            except Exception as e:
                raise ValueError(
                    f"Error parsing line {line_num} of '{file_path}': {e}"
                )
    
    # Validate against expected IDs if provided
    if expected_ids is not None:
        missing_ids = expected_ids - found_ids
        extra_ids = found_ids - expected_ids
        
        if missing_ids:
            raise ValueError(
                f"File '{file_path}' is missing {len(missing_ids)} expected ID(s): "
                f"{sorted(list(missing_ids))[:10]}{'...' if len(missing_ids) > 10 else ''}"
            )
        
        if extra_ids:
            raise ValueError(
                f"File '{file_path}' has {len(extra_ids)} unexpected ID(s): "
                f"{sorted(list(extra_ids))[:10]}{'...' if len(extra_ids) > 10 else ''}"
            )
    
    return results, found_ids


def validate_trn_pair(
    hypothesis_path: Path,
    reference_path: Path,
    sclite_format: bool = False
) -> List[Tuple[str, str, str]]:
    """
    Validates that two TRN files have matching IDs and formats.
    
    Args:
        hypothesis_path: Path to hypothesis TRN file
        reference_path: Path to reference TRN file
        sclite_format: If True, expects sclite format
    
    Returns:
        List of tuples (id, reference, hypothesis) with matching IDs
    
    Raises:
        ValueError: If files don't match in IDs or format
        FileNotFoundError: If files don't exist
    """
    # Validate both files exist
    if not hypothesis_path.exists():
        raise FileNotFoundError(f"Hypothesis file not found: {hypothesis_path}")
    if not reference_path.exists():
        raise FileNotFoundError(f"Reference file not found: {reference_path}")
    
    # Parse reference file first
    references, ref_ids = validate_trn_format(reference_path, sclite_format)
    
    # Parse hypothesis file, validating against reference IDs
    hypotheses, hyp_ids = validate_trn_format(
        hypothesis_path, sclite_format, expected_ids=ref_ids
    )
    
    # Convert to dictionaries for easier matching
    ref_dict = {id_str: text for id_str, text in references}
    hyp_dict = {id_str: text for id_str, text in hypotheses}
    
    # Create list of tuples (id, reference, hypothesis) in sorted order
    results = []
    for id_str in sorted(ref_ids):
        ref_text = ref_dict[id_str]
        hyp_text = hyp_dict[id_str]
        results.append((id_str, ref_text, hyp_text))
    
    return results


def validate_compact_csv(file_path: Path) -> List[Tuple[str, str, str]]:
    """
    Validates and parses compact CSV file, converting it to TRN-equivalent format.
    
    Args:
        file_path: Path to the CSV file
    
    Returns:
        List of tuples (id, reference, hypothesis)
    
    Raises:
        ValueError: If CSV format is invalid
        FileNotFoundError: If file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    # Validate encoding first
    validate_utf8_encoding(file_path)
    
    results = []
    seen_ids = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Validate required columns
            required_columns = {'ID', 'reference', 'hypothesis'}
            if reader.fieldnames is None:
                raise ValueError(
                    f"CSV file '{file_path}' appears to be empty or has no header row."
                )
            
            fieldnames_lower = {col.lower() for col in reader.fieldnames}
            required_lower = {col.lower() for col in required_columns}
            
            if not required_lower.issubset(fieldnames_lower):
                missing = required_columns - {col for col in reader.fieldnames if col.lower() in required_lower}
                raise ValueError(
                    f"CSV file '{file_path}' must have columns: ID, reference, hypothesis. "
                    f"Missing columns: {sorted(missing)}. Found columns: {sorted(reader.fieldnames)}"
                )
            
            # Find column names (case-insensitive matching)
            id_col = next(col for col in reader.fieldnames if col.lower() == 'id')
            ref_col = next(col for col in reader.fieldnames if col.lower() == 'reference')
            hyp_col = next(col for col in reader.fieldnames if col.lower() == 'hypothesis')
            
            for row_num, row in enumerate(reader, 2):  # Start at 2 because row 1 is the header
                id_str = row.get(id_col, '').strip()
                reference = row.get(ref_col, '').strip()
                hypothesis = row.get(hyp_col, '').strip()
                
                if not id_str:
                    raise ValueError(
                        f"Row {row_num} in '{file_path}': ID cannot be empty"
                    )
                
                # Check for duplicate IDs
                if id_str in seen_ids:
                    raise ValueError(
                        f"Row {row_num} in '{file_path}': Duplicate ID '{id_str}'. "
                        f"Each ID must be unique."
                    )
                
                seen_ids.add(id_str)
                results.append((id_str, reference, hypothesis))
    
    except csv.Error as e:
        raise ValueError(f"Error reading CSV file '{file_path}': {e}")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Unexpected error reading CSV file '{file_path}': {e}")
    
    if not results:
        raise ValueError(f"CSV file '{file_path}' contains no data rows (only header)")
    
    return results


def validate_adjustments_structure(file_path: Path) -> Dict:
    """
    Validates basic structure of adjustments JSON file.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Dictionary with loaded adjustments
    
    Raises:
        ValueError: If JSON structure is invalid
        FileNotFoundError: If file does not exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Adjustments file not found: {file_path}")
    
    # Validate encoding first
    validate_utf8_encoding(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in adjustments file '{file_path}': {e}. "
                f"Please check that the file is valid JSON."
            )
    
    if not isinstance(data, dict):
        raise ValueError(
            f"Adjustments file '{file_path}' must contain a JSON object (dictionary), "
            f"not {type(data).__name__}"
        )
    
    # Validate basic structure (fields are optional, but if they exist must be correct type)
    valid_keys = {'reference_replacements', 'equivalences', 'clean_up', 'case_sensitive'}
    for key in data.keys():
        if key not in valid_keys:
            raise ValueError(
                f"Unknown key '{key}' in adjustments JSON '{file_path}'. "
                f"Valid keys are: {', '.join(sorted(valid_keys))}"
            )
    
    # Validate types
    if 'reference_replacements' in data:
        if not isinstance(data['reference_replacements'], dict):
            raise ValueError(
                f"'reference_replacements' in '{file_path}' must be an object/dictionary, "
                f"not {type(data['reference_replacements']).__name__}"
            )
        # Validate that values are strings
        for key, value in data['reference_replacements'].items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(
                    f"'reference_replacements' in '{file_path}' must contain only string keys and values. "
                    f"Found: {type(key).__name__} -> {type(value).__name__}"
                )
    
    if 'equivalences' in data:
        if not isinstance(data['equivalences'], dict):
            raise ValueError(
                f"'equivalences' in '{file_path}' must be an object/dictionary, "
                f"not {type(data['equivalences']).__name__}"
            )
        # Validate structure: canonical -> list of variants
        for canonical, variants in data['equivalences'].items():
            if not isinstance(canonical, str):
                raise ValueError(
                    f"'equivalences' in '{file_path}': canonical form must be a string. "
                    f"Found: {type(canonical).__name__}"
                )
            if not isinstance(variants, list):
                raise ValueError(
                    f"'equivalences' in '{file_path}': variants for '{canonical}' must be a list, "
                    f"not {type(variants).__name__}"
                )
            for variant in variants:
                if not isinstance(variant, str):
                    raise ValueError(
                        f"'equivalences' in '{file_path}': variant in '{canonical}' must be a string, "
                        f"not {type(variant).__name__}"
                    )
    
    if 'clean_up' in data:
        if not isinstance(data['clean_up'], list):
            raise ValueError(
                f"'clean_up' in '{file_path}' must be a list, "
                f"not {type(data['clean_up']).__name__}"
            )
        for item in data['clean_up']:
            if not isinstance(item, str):
                raise ValueError(
                    f"'clean_up' in '{file_path}' must contain only strings. "
                    f"Found: {type(item).__name__}"
                )
    
    if 'case_sensitive' in data:
        if not isinstance(data['case_sensitive'], bool):
            raise ValueError(
                f"'case_sensitive' in '{file_path}' must be a boolean, "
                f"not {type(data['case_sensitive']).__name__}"
            )
    
    return data


def validate_adjustments_consistency(adjustments: Dict) -> None:
    """
    Validates that adjustments are consistent (no conflicting rules).
    
    This checks for:
    - Equivalences where a variant is also used as a canonical form
    - Equivalences where a variant appears in reference_replacements
    - Equivalences where a canonical form appears in reference_replacements
    - Clean_up words that appear in equivalences or reference_replacements
    
    Args:
        adjustments: Dictionary with adjustments (already validated for structure)
    
    Raises:
        ValueError: If inconsistencies are found
    """
    errors = []
    
    reference_replacements = adjustments.get('reference_replacements', {})
    equivalences = adjustments.get('equivalences', {})
    clean_up = adjustments.get('clean_up', [])
    case_sensitive = adjustments.get('case_sensitive', False)
    
    # Normalize strings for comparison if case-insensitive
    def normalize(s: str) -> str:
        return s.lower() if not case_sensitive else s
    
    # Build sets of normalized strings
    ref_repl_keys = {normalize(k) for k in reference_replacements.keys()}
    ref_repl_values = {normalize(v) for v in reference_replacements.values()}
    equiv_canonicals = {normalize(c) for c in equivalences.keys()}
    equiv_variants = set()
    for variants_list in equivalences.values():
        equiv_variants.update(normalize(v) for v in variants_list)
    clean_up_normalized = {normalize(w) for w in clean_up}
    
    # Check 1: Equivalence variants that are also canonical forms
    overlapping_canonicals = equiv_variants & equiv_canonicals
    if overlapping_canonicals:
        errors.append(
            f"Equivalence inconsistency: The following variants are also used as canonical forms: "
            f"{sorted(overlapping_canonicals)}. A variant cannot be a canonical form."
        )
    
    # Check 2: Equivalence variants that appear in reference_replacements (as keys)
    overlapping_ref_repl = equiv_variants & ref_repl_keys
    if overlapping_ref_repl:
        errors.append(
            f"Equivalence inconsistency: The following equivalence variants are also used as keys "
            f"in reference_replacements: {sorted(overlapping_ref_repl)}. "
            f"This creates a conflict: should the variant be replaced or normalized?"
        )
    
    # Check 3: Equivalence canonical forms that appear in reference_replacements (as keys)
    overlapping_canon_ref = equiv_canonicals & ref_repl_keys
    if overlapping_canon_ref:
        errors.append(
            f"Equivalence inconsistency: The following canonical forms are also used as keys "
            f"in reference_replacements: {sorted(overlapping_canon_ref)}. "
            f"This creates a conflict: should the canonical form be replaced or kept?"
        )
    
    # Check 4: Equivalence variants that appear in reference_replacements (as values)
    overlapping_variant_ref_value = equiv_variants & ref_repl_values
    if overlapping_variant_ref_value:
        errors.append(
            f"Equivalence inconsistency: The following equivalence variants are also used as values "
            f"in reference_replacements: {sorted(overlapping_variant_ref_value)}. "
            f"This may create unexpected behavior."
        )
    
    # Check 5: Clean_up words that appear in equivalences (as canonical or variant)
    overlapping_clean_equiv = clean_up_normalized & (equiv_canonicals | equiv_variants)
    if overlapping_clean_equiv:
        errors.append(
            f"Clean_up inconsistency: The following words to remove are also defined in equivalences: "
            f"{sorted(overlapping_clean_equiv)}. "
            f"This creates a conflict: should the word be normalized or removed?"
        )
    
    # Check 6: Clean_up words that appear in reference_replacements
    overlapping_clean_ref = clean_up_normalized & (ref_repl_keys | ref_repl_values)
    if overlapping_clean_ref:
        errors.append(
            f"Clean_up inconsistency: The following words to remove are also used in "
            f"reference_replacements: {sorted(overlapping_clean_ref)}. "
            f"This creates a conflict: should the word be replaced or removed?"
        )
    
    if errors:
        error_msg = "Adjustments file contains inconsistencies:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)


def validate_adjustments(file_path: Path) -> Dict:
    """
    Complete validation of adjustments JSON file (structure + consistency).
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Dictionary with loaded and validated adjustments
    
    Raises:
        ValueError: If adjustments are invalid or inconsistent
        FileNotFoundError: If file does not exist
    """
    # First validate structure
    adjustments = validate_adjustments_structure(file_path)
    
    # Then validate consistency
    validate_adjustments_consistency(adjustments)
    
    return adjustments

