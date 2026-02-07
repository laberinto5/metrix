"""
Module for basic text transformations (case, punctuation, hyphens, apostrophes, stop words).
"""

import re
import string
from typing import Optional, Tuple

try:
    import nltk
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


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


def remove_stop_words(text: str, language: str) -> str:
    """
    Removes stop words from text using NLTK.
    
    This function should be called AFTER basic transformations and adjustments,
    just before WER calculation.
    
    Args:
        text: Text from which to remove stop words
        language: Language code (e.g., 'english', 'spanish', 'portuguese')
    
    Returns:
        Text with stop words removed
    
    Raises:
        ImportError: If NLTK is not available
        LookupError: If stop words for the language are not available
        ValueError: If language is not supported
    """
    if not NLTK_AVAILABLE:
        raise ImportError(
            "NLTK is required for stop word removal. "
            "Install it with: pip install nltk"
        )
    
    # Normalize language name (lowercase, handle common variations)
    language_lower = language.lower().strip()
    language_map = {
        'es': 'spanish',
        'spa': 'spanish',
        'esp': 'spanish',
        'pt': 'portuguese',
        'por': 'portuguese',
        'en': 'english',
        'eng': 'english',
    }
    
    # Map common language codes to NLTK language names
    nltk_language = language_map.get(language_lower, language_lower)
    
    try:
        # Download stop words if not already available
        try:
            stop_words = set(stopwords.words(nltk_language))
        except LookupError:
            # Try to download the stop words corpus
            try:
                nltk.download('stopwords', quiet=True)
                stop_words = set(stopwords.words(nltk_language))
            except Exception as download_error:
                available_languages = ['english', 'spanish', 'portuguese', 'french', 'german', 'italian']
                raise ValueError(
                    f"Failed to download NLTK stopwords corpus for language '{language}'. "
                    f"Please download it manually with: python -c \"import nltk; nltk.download('stopwords')\" "
                    f"or check your internet connection. "
                    f"Supported languages: {', '.join(available_languages)}. "
                    f"Error: {download_error}"
                )
        
        # Split text into words
        words = text.split()
        
        # Remove stop words
        filtered_words = [word for word in words if word.lower() not in stop_words]
        
        # Join back with spaces
        result = ' '.join(filtered_words)
        
        # Normalize spaces
        result = re.sub(r'\s+', ' ', result)
        result = result.strip()
        
        return result
        
    except (LookupError, OSError) as e:
        available_languages = ['english', 'spanish', 'portuguese', 'french', 'german', 'italian']
        # Check if it's a language not supported by NLTK
        if isinstance(e, OSError) and 'No such file or directory' in str(e):
            raise ValueError(
                f"Stop words for language '{language}' are not supported by NLTK. "
                f"Supported languages: {', '.join(available_languages)}. "
                f"Please use one of the supported languages or check the language name spelling."
            )
        else:
            raise ValueError(
                f"Stop words for language '{language}' not available. "
                f"Supported languages: {', '.join(available_languages)}. "
                f"Make sure NLTK stopwords corpus is downloaded. "
                f"You can download it with: python -c \"import nltk; nltk.download('stopwords')\" "
                f"Error: {e}"
            )


def apply_stop_words_removal(
    reference: str,
    hypothesis: str,
    language: Optional[str] = None
) -> Tuple[str, str]:
    """
    Removes stop words from both reference and hypothesis.
    
    Args:
        reference: Reference text
        hypothesis: Hypothesis text
        language: Language code for stop words (e.g., 'english', 'spanish')
                 If None, no stop words are removed
    
    Returns:
        Tuple (reference_without_stopwords, hypothesis_without_stopwords)
    """
    if language is None:
        return reference, hypothesis
    
    ref_result = remove_stop_words(reference, language)
    hyp_result = remove_stop_words(hypothesis, language)
    
    return ref_result, hyp_result
