#!/usr/bin/env python3
"""
Metrix - Metrics calculator for ASR and NLP system evaluation.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich import print as rprint

# Add src to path to import modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from input_handler import load_inputs
from text_transformer import apply_basic_transformations
from adjustments_processor import load_adjustments, apply_adjustments
from metrics_calculator import calculate_metrics_batch
from output_generator import (
    generate_csv_output,
    generate_json_output,
    generate_report,
    print_on_screen,
    resolve_output_paths,
    check_and_confirm_overwrite
)

app = typer.Typer(help="Metrix - Metrics calculator for ASR system evaluation")
console = Console()


def validate_input_options(
    hypothesis: Optional[Path],
    reference: Optional[Path],
    compact_input: Optional[Path]
):
    """Validates that input options are correct."""
    if compact_input is not None:
        if hypothesis is not None or reference is not None:
            raise typer.BadParameter(
                "Options --compact-input (-ci) and --hypothesis/--reference (-h/-r) "
                "are mutually exclusive. Use one or the other."
            )
    else:
        if hypothesis is None or reference is None:
            raise typer.BadParameter(
                "Must provide both --hypothesis (-h) and --reference (-r), "
                "or use --compact-input (-ci)"
            )


@app.command()
def wer(
    hypothesis: Optional[Path] = typer.Option(
        None, "--hypothesis", "-h", help="TRN file with hypotheses"
    ),
    reference: Optional[Path] = typer.Option(
        None, "--reference", "-r", help="TRN file with references"
    ),
    compact_input: Optional[Path] = typer.Option(
        None, "--compact-input", "-ci", help="Compact CSV file (ID, reference, hypothesis)"
    ),
    adjustments: Optional[Path] = typer.Option(
        None, "--adjustments", "-a", help="JSON file with adjustments"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output path (folder or file)"
    ),
    case_sensitive: bool = typer.Option(
        False, "--case-sensitive", "-cs", help="Enable case-sensitive"
    ),
    keep_punctuation: bool = typer.Option(
        False, "--keep-punctuation", "-kp", help="Keep punctuation"
    ),
    neutralize_hyphens: bool = typer.Option(
        False, "--neutralize-hyphens", "-nh", help="Replace hyphens with spaces"
    ),
    neutralize_apostrophes: bool = typer.Option(
        False, "--neutralize-apostrophes", "-na", help="Remove apostrophes"
    ),
    on_screen: bool = typer.Option(
        False, "--on-screen", "-os", help="Display results on screen"
    ),
    sclite_format: bool = typer.Option(
        False, "--sclite-format", "-S", help="Use sclite format in TRN files"
    ),
):
    """
    Calculates Word Error Rate (WER) between hypothesis and reference.
    """
    try:
        # Validate input options
        validate_input_options(hypothesis, reference, compact_input)
        
        # Load inputs
        console.print("[cyan]Loading inputs...[/cyan]")
        inputs = load_inputs(
            hypothesis_path=hypothesis,
            reference_path=reference,
            compact_input_path=compact_input,
            sclite_format=sclite_format
        )
        
        console.print(f"[green]✓[/green] Loaded {len(inputs)} sentence pairs")
        
        # Separate references and hypotheses
        references = [ref for _, ref, _ in inputs]
        hypotheses = [hyp for _, _, hyp in inputs]
        
        # Apply basic transformations
        console.print("[cyan]Applying basic transformations...[/cyan]")
        transformed_pairs = []
        for ref, hyp in zip(references, hypotheses):
            ref_transformed, hyp_transformed = apply_basic_transformations(
                ref, hyp,
                case_sensitive=case_sensitive,
                keep_punctuation=keep_punctuation,
                neutralize_hyphens=neutralize_hyphens,
                neutralize_apostrophes=neutralize_apostrophes
            )
            transformed_pairs.append((ref_transformed, hyp_transformed))
        
        refs_transformed = [ref for ref, _ in transformed_pairs]
        hyps_transformed = [hyp for _, hyp in transformed_pairs]
        
        # Process adjustments if provided
        adjustments_data = None
        if adjustments:
            console.print("[cyan]Loading adjustments...[/cyan]")
            adjustments_data = load_adjustments(adjustments)
            console.print("[green]✓[/green] Adjustments loaded")
        
        # Calculate metrics
        console.print("[cyan]Calculating metrics...[/cyan]")
        
        metrics_without_adjustments = None
        metrics_with_adjustments = None
        alignments_without = None
        alignments_with = None
        
        # Calculate without adjustments first
        metrics_without_adjustments, alignments_without = calculate_metrics_batch(
            refs_transformed, hyps_transformed, metric_type='wer'
        )
        
        # If there are adjustments, also calculate with adjustments
        if adjustments_data:
            refs_adjusted = []
            hyps_adjusted = []
            for ref, hyp in zip(refs_transformed, hyps_transformed):
                ref_adj, hyp_adj = apply_adjustments(ref, hyp, adjustments_data)
                refs_adjusted.append(ref_adj)
                hyps_adjusted.append(hyp_adj)
            
            metrics_with_adjustments, alignments_with = calculate_metrics_batch(
                refs_adjusted, hyps_adjusted, metric_type='wer'
            )
        
        # Use metrics with adjustments if they exist, otherwise without adjustments
        final_metrics = metrics_with_adjustments if metrics_with_adjustments else metrics_without_adjustments
        final_alignments = alignments_with if alignments_with else alignments_without
        
        console.print("[green]✓[/green] Metrics calculated")
        
        # Prepare configuration for report
        config = {
            'hypothesis_file': str(hypothesis) if hypothesis else None,
            'reference_file': str(reference) if reference else None,
            'compact_input_file': str(compact_input) if compact_input else None,
            'adjustments_file': str(adjustments) if adjustments else None,
            'case_sensitive': case_sensitive,
            'keep_punctuation': keep_punctuation,
            'neutralize_hyphens': neutralize_hyphens,
            'neutralize_apostrophes': neutralize_apostrophes,
            'sclite_format': sclite_format
        }
        
        # Display on screen if requested
        if on_screen:
            print_on_screen(
                final_metrics,
                final_alignments,
                config,
                metric_type='wer',
                metrics_with_adjustments=metrics_with_adjustments,
                metrics_without_adjustments=metrics_without_adjustments
            )
        
        # Generate output files if output is provided
        if output:
            console.print(f"[cyan]Generating output files...[/cyan]")
            
            # Resolve output paths
            output_paths = resolve_output_paths(output, metric_type='wer')
            
            # Check overwrite
            if not check_and_confirm_overwrite(output_paths):
                console.print("[yellow]Operation cancelled by user[/yellow]")
                raise typer.Exit()
            
            # Generate CSV
            generate_csv_output(final_metrics, output_paths['csv'], metric_type='wer')
            console.print(f"[green]✓[/green] CSV saved: {output_paths['csv']}")
            
            # Generate JSON
            generate_json_output(final_metrics, output_paths['json'])
            console.print(f"[green]✓[/green] JSON saved: {output_paths['json']}")
            
            # Generate report
            generate_report(
                final_metrics,
                final_alignments,
                config,
                output_paths['report'],
                metric_type='wer',
                metrics_with_adjustments=metrics_with_adjustments,
                metrics_without_adjustments=metrics_without_adjustments
            )
            console.print(f"[green]✓[/green] Report saved: {output_paths['report']}")
        
        console.print("\n[bold green]✓ Done![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def cer(
    hypothesis: Optional[Path] = typer.Option(
        None, "--hypothesis", "-h", help="TRN file with hypotheses"
    ),
    reference: Optional[Path] = typer.Option(
        None, "--reference", "-r", help="TRN file with references"
    ),
    compact_input: Optional[Path] = typer.Option(
        None, "--compact-input", "-ci", help="Compact CSV file (ID, reference, hypothesis)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output path (folder or file)"
    ),
    case_sensitive: bool = typer.Option(
        False, "--case-sensitive", "-cs", help="Enable case-sensitive"
    ),
    keep_punctuation: bool = typer.Option(
        False, "--keep-punctuation", "-kp", help="Keep punctuation"
    ),
    neutralize_hyphens: bool = typer.Option(
        False, "--neutralize-hyphens", "-nh", help="Replace hyphens with spaces"
    ),
    neutralize_apostrophes: bool = typer.Option(
        False, "--neutralize-apostrophes", "-na", help="Remove apostrophes"
    ),
    on_screen: bool = typer.Option(
        False, "--on-screen", "-os", help="Display results on screen"
    ),
    sclite_format: bool = typer.Option(
        False, "--sclite-format", "-S", help="Use sclite format in TRN files"
    ),
):
    """
    Calculates Character Error Rate (CER) between hypothesis and reference.
    """
    try:
        # Validate input options
        validate_input_options(hypothesis, reference, compact_input)
        
        # Load inputs
        console.print("[cyan]Loading inputs...[/cyan]")
        inputs = load_inputs(
            hypothesis_path=hypothesis,
            reference_path=reference,
            compact_input_path=compact_input,
            sclite_format=sclite_format
        )
        
        console.print(f"[green]✓[/green] Loaded {len(inputs)} sentence pairs")
        
        # Separate references and hypotheses
        references = [ref for _, ref, _ in inputs]
        hypotheses = [hyp for _, _, hyp in inputs]
        
        # Apply basic transformations
        console.print("[cyan]Applying basic transformations...[/cyan]")
        transformed_pairs = []
        for ref, hyp in zip(references, hypotheses):
            ref_transformed, hyp_transformed = apply_basic_transformations(
                ref, hyp,
                case_sensitive=case_sensitive,
                keep_punctuation=keep_punctuation,
                neutralize_hyphens=neutralize_hyphens,
                neutralize_apostrophes=neutralize_apostrophes
            )
            transformed_pairs.append((ref_transformed, hyp_transformed))
        
        refs_transformed = [ref for ref, _ in transformed_pairs]
        hyps_transformed = [hyp for _, hyp in transformed_pairs]
        
        # Calculate metrics (CER does not use adjustments)
        console.print("[cyan]Calculating metrics...[/cyan]")
        final_metrics, final_alignments = calculate_metrics_batch(
            refs_transformed, hyps_transformed, metric_type='cer'
        )
        
        console.print("[green]✓[/green] Metrics calculated")
        
        # Prepare configuration for report
        config = {
            'hypothesis_file': str(hypothesis) if hypothesis else None,
            'reference_file': str(reference) if reference else None,
            'compact_input_file': str(compact_input) if compact_input else None,
            'adjustments_file': None,  # CER does not use adjustments
            'case_sensitive': case_sensitive,
            'keep_punctuation': keep_punctuation,
            'neutralize_hyphens': neutralize_hyphens,
            'neutralize_apostrophes': neutralize_apostrophes,
            'sclite_format': sclite_format
        }
        
        # Display on screen if requested
        if on_screen:
            print_on_screen(
                final_metrics,
                final_alignments,
                config,
                metric_type='cer'
            )
        
        # Generate output files if output is provided
        if output:
            console.print(f"[cyan]Generating output files...[/cyan]")
            
            # Resolve output paths
            output_paths = resolve_output_paths(output, metric_type='cer')
            
            # Check overwrite
            if not check_and_confirm_overwrite(output_paths):
                console.print("[yellow]Operation cancelled by user[/yellow]")
                raise typer.Exit()
            
            # Generate CSV
            generate_csv_output(final_metrics, output_paths['csv'], metric_type='cer')
            console.print(f"[green]✓[/green] CSV saved: {output_paths['csv']}")
            
            # Generate JSON
            generate_json_output(final_metrics, output_paths['json'])
            console.print(f"[green]✓[/green] JSON saved: {output_paths['json']}")
            
            # Generate report
            generate_report(
                final_metrics,
                final_alignments,
                config,
                output_paths['report'],
                metric_type='cer'
            )
            console.print(f"[green]✓[/green] Report saved: {output_paths['report']}")
        
        console.print("\n[bold green]✓ Done![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
