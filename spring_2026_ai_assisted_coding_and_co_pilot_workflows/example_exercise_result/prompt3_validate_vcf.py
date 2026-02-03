import argparse
import gzip


def load_fasta(fasta_path):
    sequences = {}
    try:
        with open(fasta_path) as f:
            chrom = None
            seq = []
            for line in f:
                line = line.strip()
                if not line:  # skip blank lines
                    continue
                if line.startswith(">"):
                    if chrom:
                        sequences[chrom] = "".join(seq)
                    chrom = line[1:].split()[0]
                    seq = []
                elif chrom is None:
                    raise ValueError(
                        f"Invalid FASTA format: sequence data before header in {fasta_path}"
                    )
                else:
                    seq.append(line)
            if chrom:
                sequences[chrom] = "".join(seq)
    except OSError as e:
        raise RuntimeError(f"Error opening FASTA file '{fasta_path}': {e}")
    if not sequences:
        raise ValueError(f"No sequences found in FASTA file '{fasta_path}'")
    return sequences


def validate_vcf(vcf_entries, fasta_sequences):
    for vcf_entry in vcf_entries:
        chrom = vcf_entry["chrom"]
        if chrom not in fasta_sequences:
            raise ValueError(f"Reference chromosome '{chrom}' not found in FASTA.")
        ref_base = fasta_sequences[chrom][
            vcf_entry["pos"] - 1 : vcf_entry["pos"] - 1 + len(vcf_entry["ref"])
        ]
        if vcf_entry["ref"] != ref_base:
            print(
                f"Mismatch: {vcf_entry['chrom']}\t{vcf_entry['pos']}\t{vcf_entry['id']}\t"
                f"VCF_REF={vcf_entry['ref']}\tFASTA_REF={ref_base}\tALT={vcf_entry['alt']}"
            )


def parse_vcf(vcf_path):
    opener = gzip.open if vcf_path.endswith(".gz") else open
    try:
        with opener(vcf_path, "rt") as vcf:
            for lineno, line in enumerate(vcf, 1):
                if line.startswith("#"):
                    continue
                fields = line.strip().split("\t")
                if len(fields) < 5:
                    raise ValueError(
                        f"Malformed VCF line {lineno} in '{vcf_path}': fewer than 5 columns"
                    )
                alts = fields[4].split(",") if fields[4] else []
                if not alts or any(not alt for alt in alts):
                    raise ValueError(
                        f"Missing or empty ALT field at line {lineno} in '{vcf_path}'"
                    )
                try:
                    pos = int(fields[1])
                except Exception:
                    raise ValueError(
                        f"Non-integer POS at line {lineno} in '{vcf_path}': {fields[1]}"
                    )
                for alt in alts:
                    yield {
                        "chrom": fields[0],
                        "pos": pos,
                        "id": fields[2],
                        "ref": fields[3],
                        "alt": alt,
                    }
    except OSError as e:
        raise RuntimeError(f"Error opening VCF file '{vcf_path}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate VCF reference alleles against a reference FASTA."
    )
    parser.add_argument("vcf", help="Path to the VCF file")
    parser.add_argument("fasta", help="Path to the reference FASTA file")
    args = parser.parse_args()
    fasta = load_fasta(args.fasta)
    validate_vcf(parse_vcf(args.vcf), fasta)
