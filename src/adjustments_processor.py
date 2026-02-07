"""
Module for processing JSON adjustment files (replacements, equivalences, cleanup).
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_adjustments(file_path: Path) -> Dict:
    """
    Loads and validates the JSON adjustments file.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Dictionary with loaded adjustments
    
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If JSON is invalid or has incorrect structure
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Adjustments file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing adjustments JSON: {e}")
    
    # Validate basic structure (fields are optional, but if they exist must be correct type)
    valid_keys = {'reference_replacements', 'equivalences', 'clean_up', 'case_sensitive'}
    for key in data.keys():
        if key not in valid_keys:
            raise ValueError(f"Unknown key in adjustments JSON: {key}")
    
    # Validate types
    if 'reference_replacements' in data and not isinstance(data['reference_replacements'], dict):
        raise ValueError("'reference_replacements' must be an object/dictionary")
    
    if 'equivalences' in data and not isinstance(data['equivalences'], dict):
        raise ValueError("'equivalences' must be an object/dictionary")
    
    if 'clean_up' in data and not isinstance(data['clean_up'], list):
        raise ValueError("'clean_up' must be a list")
    
    if 'case_sensitive' in data and not isinstance(data['case_sensitive'], bool):
        raise ValueError("'case_sensitive' must be a boolean")
    
    return data


def apply_reference_replacements(
    text: str,
    replacements: Dict[str, str],
    case_sensitive: bool = False
) -> str:
    """
    Applies replacements only to the reference text.
    Replacements use word boundaries to avoid substring matches.
    
    Args:
        text: Text to transform
        replacements: Dictionary {search: replace}
        case_sensitive: If replacements should be case-sensitive
    
    Returns:
        Text with replacements applied
    """
    result = text
    
    for search, replace in replacements.items():
        # Escape special regex characters
        escaped_search = re.escape(search)
        
        # Create pattern with word boundaries
        if case_sensitive:
            pattern = r'\b' + escaped_search + r'\b'
        else:
            pattern = r'(?i)\b' + escaped_search + r'\b'
        
        result = re.sub(pattern, replace, result)
    
    return result


def apply_equivalences(
    text: str,
    equivalences: Dict[str, List[str]],
    case_sensitive: bool = False
) -> str:
    """
    Applies equivalences, normalizing all variants to canonical form
    (first word in the list).
    
    Args:
        text: Text to transform
        equivalences: Dictionary {equivalence_name: [canonical, variant1, variant2, ...]}
        case_sensitive: If equivalences should be case-sensitive
    
    Returns:
        Text with normalized equivalences
    """
    result = text
    
    for eq_name, variants in equivalences.items():
        if not variants or len(variants) == 0:
            continue
        
        canonical = variants[0]  # First is the canonical form
        
        # Normalize all variants (except canonical) to canonical
        for variant in variants[1:]:
            if variant == canonical:
                continue  # Skip if same as canonical
            
            # Escape special characters
            escaped_variant = re.escape(variant)
            
            # Create pattern with word boundaries
            if case_sensitive:
                pattern = r'\b' + escaped_variant + r'\b'
            else:
                pattern = r'(?i)\b' + escaped_variant + r'\b'
            
            result = re.sub(pattern, canonical, result)
    
    return result


def apply_clean_up(text: str, clean_up_list: List[str], case_sensitive: bool = False) -> str:
    """
    Removes elements from the clean_up list from text.
    
    Args:
        text: Text to clean
        clean_up_list: List of strings to remove
        case_sensitive: If cleanup should be case-sensitive
    
    Returns:
        Text with elements removed
    """
    result = text
    
    for item in clean_up_list:
        # Escape special characters
        escaped_item = re.escape(item)
        
        # Create pattern with word boundaries
        if case_sensitive:
            pattern = r'\b' + escaped_item + r'\b'
        else:
            pattern = r'(?i)\b' + escaped_item + r'\b'
        
        result = re.sub(pattern, '', result)
    
    # Normalize multiple spaces after removing elements
    result = re.sub(r'\s+', ' ', result)
    result = result.strip()
    
    return result


def apply_adjustments(
    reference: str,
    hypothesis: str,
    adjustments: Dict
) -> Tuple[str, str]:
    """
    Applies all adjustments to reference and hypothesis.
    
    Application order:
    1. reference_replacements (only in reference)
    2. equivalences (in both texts)
    3. clean_up (in both texts)
    
    Args:
        reference: Reference text
        hypothesis: Hypothesis text
        adjustments: Dictionary with loaded adjustments
    
    Returns:
        Tuple (adjusted_reference, adjusted_hypothesis)
    """
    ref_result = reference
    hyp_result = hypothesis
    
    # Get case_sensitive flag from adjustments (default False)
    case_sensitive = adjustments.get('case_sensitive', False)
    
    # 1. Apply reference_replacements (only in reference)
    if 'reference_replacements' in adjustments and adjustments['reference_replacements']:
        ref_result = apply_reference_replacements(
            ref_result,
            adjustments['reference_replacements'],
            case_sensitive=case_sensitive
        )
    
    # 2. Apply equivalences (in both texts)
    if 'equivalences' in adjustments and adjustments['equivalences']:
        ref_result = apply_equivalences(
            ref_result,
            adjustments['equivalences'],
            case_sensitive=case_sensitive
        )
        hyp_result = apply_equivalences(
            hyp_result,
            adjustments['equivalences'],
            case_sensitive=case_sensitive
        )
    
    # 3. Apply clean_up (in both texts)
    if 'clean_up' in adjustments and adjustments['clean_up']:
        ref_result = apply_clean_up(
            ref_result,
            adjustments['clean_up'],
            case_sensitive=case_sensitive
        )
        hyp_result = apply_clean_up(
            hyp_result,
            adjustments['clean_up'],
            case_sensitive=case_sensitive
        )
    
    return ref_result, hyp_result
