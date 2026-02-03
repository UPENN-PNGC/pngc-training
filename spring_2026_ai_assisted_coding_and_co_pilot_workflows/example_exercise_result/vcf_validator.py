"""
VCF Validator: Validate VCF reference alleles against a reference FASTA and summarize variant types.

This module provides a VCFValidator class for validating VCF files against a reference FASTA file,
reporting mismatches, and summarizing variant types (SNV, INDEL, DEL, INS).
"""

import argparse
import gzip
import json
import logging
import sys
from typing import Any, Dict, Generator, Optional

# Configure logging globally
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr
)


class VCFValidator:
    """
    Validates VCF reference alleles against a reference FASTA and summarizes variant types.
    """

    def __init__(self, fasta_path: str, vcf_path: str) -> None:
        """
        Initialize the VCFValidator.

        Args:
            fasta_path (str): Path to the reference FASTA file.
            vcf_path (str): Path to the VCF file.
        """
        self._fasta_path: str = fasta_path
        self._vcf_path: str = vcf_path
        self._fasta_sequences: Optional[Dict[str, str]] = None
        self._variant_summary: Optional[Dict[str, int]] = None
        self._logger = logging.getLogger("VCFValidator")

    def load_fasta(self) -> None:
        """
        Load the reference FASTA file into memory.

        Raises:
            RuntimeError: If the FASTA file cannot be opened.
            ValueError: If the FASTA file is empty or malformed.
        """
        sequences = {}
        try:
            with open(self._fasta_path) as f:
                chrom = None
                seq = []
                for line in f:
                    line = line.strip()
                    if not line:
                        continue  # skip blank lines

                    # Start of a new sequence record
                    if line.startswith(">"):
                        if chrom:
                            # Save the previous chromosome's sequence
                            sequences[chrom] = "".join(seq)
                        chrom = line[1:].split()[0]
                        seq = []
                    elif chrom is None:
                        # Sequence data before any header is invalid
                        raise ValueError(
                            f"Invalid FASTA format: sequence data before header in {self._fasta_path}"
                        )
                    else:
                        # Accumulate sequence lines for the current chromosome
                        seq.append(line)
                # Save the last chromosome's sequence
                if chrom:
                    sequences[chrom] = "".join(seq)
        except OSError as e:
            raise RuntimeError(f"Error opening FASTA file '{self._fasta_path}': {e}")
        if not sequences:
            raise ValueError(f"No sequences found in FASTA file '{self._fasta_path}'")
        self._fasta_sequences = sequences

    def parse_vcf(self) -> Generator[Dict[str, Any], None, None]:
        """
        Parse the VCF file and yield VCF entry dictionaries.

        Yields:
            Dict[str, Any]: Dictionary for each VCF entry (chrom, pos, id, ref, alt).

        Raises:
            RuntimeError: If the VCF file cannot be opened.
            ValueError: If a VCF line is malformed.
        """
        opener = gzip.open if self._vcf_path.endswith(".gz") else open
        try:
            with opener(self._vcf_path, "rt") as vcf:
                for lineno, line in enumerate(vcf, 1):
                    if line.startswith("#"):
                        continue  # skip header lines

                    fields = line.strip().split("\t")
                    if len(fields) < 5:
                        # VCF must have at least 5 columns
                        raise ValueError(
                            f"Malformed VCF line {lineno} in '{self._vcf_path}': fewer than 5 columns"
                        )
                    alts = fields[4].split(",") if fields[4] else []
                    if not alts or any(not alt for alt in alts):
                        # ALT field must not be empty or contain empty alleles
                        raise ValueError(
                            f"Missing or empty ALT field at line {lineno} in '{self._vcf_path}'"
                        )
                    try:
                        pos = int(fields[1])
                    except Exception:
                        # POS must be an integer
                        raise ValueError(
                            f"Non-integer POS at line {lineno} in '{self._vcf_path}': {fields[1]}"
                        )
                    # Yield a separate entry for each ALT allele
                    for alt in alts:
                        yield {
                            "chrom": fields[0],
                            "pos": pos,
                            "id": fields[2],
                            "ref": fields[3],
                            "alt": alt,
                        }
        except OSError as e:
            raise RuntimeError(f"Error opening VCF file '{self._vcf_path}': {e}")

    def _summarize_variant_types(self, entry: Dict[str, Any]) -> None:
        """
        Update the variant summary for a single VCF entry.

        Args:
            entry (Dict[str, Any]): A VCF entry dictionary.
        """
        ref = entry["ref"]
        alt = entry["alt"]
        if len(ref) == 1 and len(alt) == 1:
            self._variant_summary["snv"] += 1
        elif len(ref) != len(alt):
            self._variant_summary["indel"] += 1
            if len(ref) > len(alt):
                self._variant_summary["del"] += 1
            elif len(ref) < len(alt):
                self._variant_summary["ins"] += 1

    def validate(self) -> None:
        """
        Validate VCF reference alleles against the loaded FASTA sequences.

        Raises:
            RuntimeError: If FASTA is not loaded.
            ValueError: If a chromosome is missing in the FASTA.
        """
        if self._fasta_sequences is None:
            raise RuntimeError("FASTA sequences not loaded. Call load_fasta() first.")
        # Initialize summary counters
        self._variant_summary = {"snv": 0, "indel": 0, "del": 0, "ins": 0}
        for vcf_entry in self.parse_vcf():
            # Update variant type summary for each entry
            self._summarize_variant_types(vcf_entry)

            chrom = vcf_entry["chrom"]
            if chrom not in self._fasta_sequences:
                # Chromosome in VCF not found in FASTA
                raise ValueError(f"Reference chromosome '{chrom}' not found in FASTA.")

            # Extract the reference sequence from the FASTA for the variant position
            ref_base = self._fasta_sequences[chrom][
                vcf_entry["pos"] - 1 : vcf_entry["pos"] - 1 + len(vcf_entry["ref"])
            ]

            # Log a warning if the VCF reference allele does not match the FASTA
            if vcf_entry["ref"] != ref_base:
                self._logger.warning(
                    f"Mismatch: {vcf_entry['chrom']}\t{vcf_entry['pos']}\t{vcf_entry['id']}\t"
                    f"VCF_REF={vcf_entry['ref']}\tFASTA_REF={ref_base}\tALT={vcf_entry['alt']}"
                )

    def log_variant_summary(self) -> None:
        """
        Log the variant summary as a single JSON line.

        Raises:
            RuntimeError: If no variant summary is available (validate() not run).
        """

        if self._variant_summary is None:
            raise RuntimeError("No variant summary available. Run validate() first.")
        self._logger.info(
            f"Variant type summary: {json.dumps(self._variant_summary, indent=4)}"
        )

    def run(self) -> None:
        """
        Load the FASTA file and validate the VCF, logging exceptions and exiting on error.
        """
        try:
            self.load_fasta()
            self.validate()
            self.log_variant_summary()
        except Exception as e:
            self.logger.exception(f"Error during validation: {e}")
            sys.exit(1)


def main() -> None:
    """
    Command-line entry point for validating a VCF against a reference FASTA.
    """
    parser = argparse.ArgumentParser(
        description="Validate VCF reference alleles against a reference FASTA."
    )
    parser.add_argument("vcf", help="Path to the VCF file")
    parser.add_argument("fasta", help="Path to the reference FASTA file")
    args = parser.parse_args()
    validator = VCFValidator(args.fasta, args.vcf)
    validator.run()
    validator.log_variant_summary()


if __name__ == "__main__":
    main()
