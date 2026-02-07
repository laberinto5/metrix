"""
Module for basic text transformations (case, punctuation, hyphens, apostrophes).
"""

import re
import string
from typing import Optional, Tuple


def transform_text(
    text: str,
    case_sensitive: bool = False,
    keep_punctuation: bool = False,
    neutralize_hyphens: bool = False,
    neutralize_apostrophes: bool = False
) -> str:
    """
    Applies basic transformations to text.
    
    Application order:
    1. Case normalization (if not case-sensitive)
    2. Hyphen neutralization (replace with space)
    3. Apostrophe neutralization (remove)
    4. Punctuation removal (if not keeping punctuation)
    
    Args:
        text: Text to transform
        case_sensitive: If True, preserve case
        keep_punctuation: If True, keep punctuation
        neutralize_hyphens: If True, replace hyphens with spaces
        neutralize_apostrophes: If True, remove apostrophes
    
    Returns:
        Transformed text
    """
    result = text
    
    # 1. Case normalization
    if not case_sensitive:
        result = result.lower()
    
    # 2. Neutralize hyphens (replace with space)
    if neutralize_hyphens:
        result = result.replace('-', ' ')
        result = result.replace('—', ' ')  # Em dash
        result = result.replace('–', ' ')   # En dash
    
    # 3. Neutralize apostrophes (remove)
    if neutralize_apostrophes:
        result = result.replace("'", '')
        result = result.replace("'", '')  # Apostrophe typographic
        result = result.replace('"', '')  # Also remove quotes if present
        result = result.replace('"', '')
    
    # 4. Remove punctuation (if not keeping it)
    if not keep_punctuation:
        # Define punctuation to remove (excluding hyphens and apostrophes already handled)
        punctuation_to_remove = string.punctuation.replace('-', '').replace("'", '').replace('"', '')
        # Also include other common Unicode punctuation characters
        punctuation_to_remove += '¿¡«»„‚'
        
        # Remove punctuation
        result = ''.join(char for char in result if char not in punctuation_to_remove)
    
    # Normalize multiple spaces to single spaces
    result = re.sub(r'\s+', ' ', result)
    
    # Remove leading and trailing spaces
    result = result.strip()
    
    return result


def apply_basic_transformations(
    reference: str,
    hypothesis: str,
    case_sensitive: bool = False,
    keep_punctuation: bool = False,
    neutralize_hyphens: bool = False,
    neutralize_apostrophes: bool = False
) -> Tuple[str, str]:
    """
    Applies the same basic transformations to reference and hypothesis.
    
    Args:
        reference: Reference text
        hypothesis: Hypothesis text
        case_sensitive: If True, preserve case
        keep_punctuation: If True, keep punctuation
        neutralize_hyphens: If True, replace hyphens with spaces
        neutralize_apostrophes: If True, remove apostrophes
    
    Returns:
        Tuple (transformed_reference, transformed_hypothesis)
    """
    ref_transformed = transform_text(
        reference,
        case_sensitive=case_sensitive,
        keep_punctuation=keep_punctuation,
        neutralize_hyphens=neutralize_hyphens,
        neutralize_apostrophes=neutralize_apostrophes
    )
    
    hyp_transformed = transform_text(
        hypothesis,
        case_sensitive=case_sensitive,
        keep_punctuation=keep_punctuation,
        neutralize_hyphens=neutralize_hyphens,
        neutralize_apostrophes=neutralize_apostrophes
    )
    
    return ref_transformed, hyp_transformed
