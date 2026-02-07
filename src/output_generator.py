"""
Module for generating output files: CSV, JSON and detailed reports.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


def generate_csv_output(metrics: Dict, output_path: Path, metric_type: str = 'wer'):
    """
    Generates a CSV file with metrics.
    
    Args:
        metrics: Dictionary with metrics
        output_path: Path where to save the CSV
        metric_type: 'wer' or 'cer'
    """
    # Prepare data for CSV
    if metric_type == 'wer':
        row_data = {
            'Word Count': metrics.get('word_count', 0),
            'WER': f"{metrics.get('wer', 0.0):.6f}",
            'Word Accuracy': f"{metrics.get('word_accuracy', 0.0):.6f}",
            'Deletions': metrics.get('deletions', 0),
            'Insertions': metrics.get('insertions', 0),
            'Substitutions': metrics.get('substitutions', 0),
            'Correct': metrics.get('correct', 0),
            'Total Sentences': metrics.get('total_sentences', 0)
        }
    else:
        row_data = {
            'Character Count': metrics.get('character_count', 0),
            'CER': f"{metrics.get('cer', 0.0):.6f}",
            'Character Accuracy': f"{metrics.get('character_accuracy', 0.0):.6f}",
            'Deletions': metrics.get('deletions', 0),
            'Insertions': metrics.get('insertions', 0),
            'Substitutions': metrics.get('substitutions', 0),
            'Correct': metrics.get('correct', 0),
            'Total Sentences': metrics.get('total_sentences', 0)
        }
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=row_data.keys())
        writer.writeheader()
        writer.writerow(row_data)


def generate_json_output(metrics: Dict, output_path: Path):
    """
    Generates a JSON file with metrics.
    
    Args:
        metrics: Dictionary with metrics
        output_path: Path where to save the JSON
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)


def format_alignment_text(alignment_data: Dict, metric_type: str = 'wer') -> str:
    """
    Formats alignment as readable text.
    
    Args:
        alignment_data: Dictionary with reference, hypothesis and alignment
        metric_type: 'wer' or 'cer'
    
    Returns:
        Formatted string with alignment
    """
    ref = alignment_data['reference']
    hyp = alignment_data['hypothesis']
    alignment = alignment_data['alignment']
    
    # For now, show reference and hypothesis side by side
    # TODO: Improve format to show detailed alignment
    lines = []
    lines.append(f"Reference:  {ref}")
    lines.append(f"Hypothesis: {hyp}")
    
    return "\n".join(lines)


def generate_report(
    metrics: Dict,
    alignments: List[Dict],
    config: Dict,
    output_path: Path,
    metric_type: str = 'wer',
    metrics_with_adjustments: Optional[Dict] = None,
    metrics_without_adjustments: Optional[Dict] = None
):
    """
    Generates a detailed text report.
    
    Args:
        metrics: Final metrics (or with adjustments if provided)
        alignments: List of alignments per sentence
        config: Dictionary with used configuration (flags, files, etc.)
        output_path: Path where to save the report
        metric_type: 'wer' or 'cer'
        metrics_with_adjustments: Metrics with adjustments (if applicable)
        metrics_without_adjustments: Metrics without adjustments (if applicable)
    """
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append(f"METRIX - {metric_type.upper()} Report")
    lines.append("=" * 80)
    lines.append("")
    
    # Configuration
    lines.append("CONFIGURATION")
    lines.append("-" * 80)
    if config.get('hypothesis_file'):
        lines.append(f"Hypothesis file: {config['hypothesis_file']}")
    if config.get('reference_file'):
        lines.append(f"Reference file: {config['reference_file']}")
    if config.get('compact_input_file'):
        lines.append(f"Compact input file: {config['compact_input_file']}")
    if config.get('adjustments_file'):
        lines.append(f"Adjustments file: {config['adjustments_file']}")
    lines.append(f"Case sensitive: {config.get('case_sensitive', False)}")
    lines.append(f"Keep punctuation: {config.get('keep_punctuation', False)}")
    lines.append(f"Neutralize hyphens: {config.get('neutralize_hyphens', False)}")
    lines.append(f"Neutralize apostrophes: {config.get('neutralize_apostrophes', False)}")
    lines.append(f"Sclite format: {config.get('sclite_format', False)}")
    lines.append("")
    
    # Numerical results
    lines.append("RESULTS")
    lines.append("-" * 80)
    
    # If there are adjustments, show both results
    if metrics_with_adjustments and metrics_without_adjustments:
        lines.append("WITHOUT ADJUSTMENTS:")
        lines.append(format_metrics_section(metrics_without_adjustments, metric_type))
        lines.append("")
        lines.append("WITH ADJUSTMENTS:")
        lines.append(format_metrics_section(metrics_with_adjustments, metric_type))
    else:
        lines.append(format_metrics_section(metrics, metric_type))
    
    lines.append("")
    
    # Detailed alignments
    lines.append("DETAILED ALIGNMENTS")
    lines.append("-" * 80)
    lines.append("")
    
    for i, alignment_data in enumerate(alignments, 1):
        lines.append(f"Sentence {i}:")
        lines.append(format_alignment_text(alignment_data, metric_type))
        lines.append("")
    
    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def format_metrics_section(metrics: Dict, metric_type: str) -> str:
    """
    Formats a metrics section as text.
    
    Args:
        metrics: Dictionary with metrics
        metric_type: 'wer' or 'cer'
    
    Returns:
        Formatted string
    """
    lines = []
    
    if metric_type == 'wer':
        lines.append(f"  Word Count:        {metrics.get('word_count', 0)}")
        lines.append(f"  WER:               {metrics.get('wer', 0.0):.6f} ({metrics.get('wer', 0.0)*100:.2f}%)")
        lines.append(f"  Word Accuracy:     {metrics.get('word_accuracy', 0.0):.6f} ({metrics.get('word_accuracy', 0.0)*100:.2f}%)")
    else:
        lines.append(f"  Character Count:   {metrics.get('character_count', 0)}")
        lines.append(f"  CER:               {metrics.get('cer', 0.0):.6f} ({metrics.get('cer', 0.0)*100:.2f}%)")
        lines.append(f"  Character Accuracy: {metrics.get('character_accuracy', 0.0):.6f} ({metrics.get('character_accuracy', 0.0)*100:.2f}%)")
    
    lines.append(f"  Deletions:         {metrics.get('deletions', 0)}")
    lines.append(f"  Insertions:        {metrics.get('insertions', 0)}")
    lines.append(f"  Substitutions:     {metrics.get('substitutions', 0)}")
    lines.append(f"  Correct:           {metrics.get('correct', 0)}")
    lines.append(f"  Total Sentences:   {metrics.get('total_sentences', 0)}")
    
    return '\n'.join(lines)


def print_on_screen(
    metrics: Dict,
    alignments: List[Dict],
    config: Dict,
    metric_type: str = 'wer',
    metrics_with_adjustments: Optional[Dict] = None,
    metrics_without_adjustments: Optional[Dict] = None
):
    """
    Prints results on screen using Rich.
    
    Args:
        metrics: Final metrics
        alignments: List of alignments
        config: Used configuration
        metric_type: 'wer' or 'cer'
        metrics_with_adjustments: Metrics with adjustments (if applicable)
        metrics_without_adjustments: Metrics without adjustments (if applicable)
    """
    console = Console()
    
    # Configuration panel
    config_text = []
    if config.get('hypothesis_file'):
        config_text.append(f"Hypothesis: {config['hypothesis_file']}")
    if config.get('reference_file'):
        config_text.append(f"Reference: {config['reference_file']}")
    if config.get('adjustments_file'):
        config_text.append(f"Adjustments: {config['adjustments_file']}")
    
    console.print(Panel('\n'.join(config_text), title="Configuration", border_style="blue"))
    console.print()
    
    # Metrics table
    if metrics_with_adjustments and metrics_without_adjustments:
        # Show both tables
        console.print("[bold]Results WITHOUT Adjustments:[/bold]")
        _print_metrics_table(console, metrics_without_adjustments, metric_type)
        console.print()
        console.print("[bold]Results WITH Adjustments:[/bold]")
        _print_metrics_table(console, metrics_with_adjustments, metric_type)
    else:
        _print_metrics_table(console, metrics, metric_type)
    
    console.print()
    
    # Alignments
    console.print("[bold]Detailed Alignments:[/bold]")
    for i, alignment_data in enumerate(alignments, 1):
        console.print(f"\n[cyan]Sentence {i}:[/cyan]")
        console.print(f"  Reference:  {alignment_data['reference']}")
        console.print(f"  Hypothesis: {alignment_data['hypothesis']}")


def _print_metrics_table(console: Console, metrics: Dict, metric_type: str):
    """Prints a metrics table using Rich."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    if metric_type == 'wer':
        table.add_row("Word Count", str(metrics.get('word_count', 0)))
        table.add_row("WER", f"{metrics.get('wer', 0.0):.6f} ({metrics.get('wer', 0.0)*100:.2f}%)")
        table.add_row("Word Accuracy", f"{metrics.get('word_accuracy', 0.0):.6f} ({metrics.get('word_accuracy', 0.0)*100:.2f}%)")
    else:
        table.add_row("Character Count", str(metrics.get('character_count', 0)))
        table.add_row("CER", f"{metrics.get('cer', 0.0):.6f} ({metrics.get('cer', 0.0)*100:.2f}%)")
        table.add_row("Character Accuracy", f"{metrics.get('character_accuracy', 0.0):.6f} ({metrics.get('character_accuracy', 0.0)*100:.2f}%)")
    
    table.add_row("Deletions", str(metrics.get('deletions', 0)))
    table.add_row("Insertions", str(metrics.get('insertions', 0)))
    table.add_row("Substitutions", str(metrics.get('substitutions', 0)))
    table.add_row("Correct", str(metrics.get('correct', 0)))
    table.add_row("Total Sentences", str(metrics.get('total_sentences', 0)))
    
    console.print(table)


def resolve_output_paths(base_path: Path, metric_type: str = 'wer') -> Dict[str, Path]:
    """
    Resolves output paths for CSV, JSON and report.
    
    Args:
        base_path: Base path provided by user (can be folder or file)
        metric_type: 'wer' or 'cer'
    
    Returns:
        Dictionary with paths: {'csv': Path, 'json': Path, 'report': Path}
    """
    # If it's a directory, create files with default names
    if base_path.is_dir():
        csv_path = base_path / f"{metric_type}_metrics.csv"
        json_path = base_path / f"{metric_type}_metrics.json"
        report_path = base_path / f"{metric_type}_report.txt"
    else:
        # It's a file, determine extensions
        base_name = base_path.stem
        parent = base_path.parent
        
        csv_path = parent / f"{base_name}.csv"
        json_path = parent / f"{base_name}.json"
        report_path = parent / f"{base_name}_report.txt"
    
    return {
        'csv': csv_path,
        'json': json_path,
        'report': report_path
    }


def check_and_confirm_overwrite(paths: Dict[str, Path]) -> bool:
    """
    Checks if files exist and asks user if they want to overwrite them.
    
    Args:
        paths: Dictionary with paths to check
    
    Returns:
        True if should proceed, False if cancelled
    """
    existing_files = [name for name, path in paths.items() if path.exists()]
    
    if not existing_files:
        return True
    
    # For now, return True (CLI implementation will ask for confirmation)
    # TODO: Implement interactive confirmation
    return True
