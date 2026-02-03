import sys


def load_fasta(fasta_path):
    sequences = {}
    with open(fasta_path) as f:
        chrom = None
        seq = []
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if chrom:
                    sequences[chrom] = "".join(seq)
                chrom = line[1:].split()[0]
                seq = []
            else:
                seq.append(line)
        if chrom:
            sequences[chrom] = "".join(seq)
    return sequences


def validate_vcf(vcf_path, fasta_sequences):
    with open(vcf_path) as vcf:
        for line in vcf:
            if line.startswith("#"):
                continue
            fields = line.strip().split("\t")
            chrom, pos, vid, ref, alt = (
                fields[0],
                int(fields[1]),
                fields[2],
                fields[3],
                fields[4],
            )
            ref_base = fasta_sequences.get(chrom, "")[pos - 1 : pos - 1 + len(ref)]
            if ref != ref_base:
                print(
                    f"Mismatch: {chrom}\t{pos}\t{vid}\tVCF_REF={ref}\tFASTA_REF={ref_base}\tALT={alt}"
                )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python prompt2_validate_vcf.py <variants.vcf> <reference.fasta>")
        sys.exit(1)
    fasta = load_fasta(sys.argv[2])
    validate_vcf(sys.argv[1], fasta)
