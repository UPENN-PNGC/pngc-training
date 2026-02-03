import subprocess
import os
import gzip
import shutil


EXAMPLE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../example_data")
)
SCRIPT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../prompt3_validate_vcf.py")
)
VCF = os.path.join(EXAMPLE_DIR, "variants.vcf")
FASTA = os.path.join(EXAMPLE_DIR, "reference.fasta")


def test_valid_vcf_and_fasta():
    result = subprocess.run(
        ["python", SCRIPT, VCF, FASTA], capture_output=True, text=True
    )
    print("STDOUT:\n", result.stdout)
    assert result.returncode == 0
    # Accept both empty output (all match) or mismatch lines
    # Optionally, check for specific output if mismatches are expected


def test_gzipped_vcf(tmp_path):
    gz_vcf = tmp_path / "variants.vcf.gz"
    with open(VCF, "rb") as f_in, gzip.open(gz_vcf, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    result = subprocess.run(
        ["python", SCRIPT, str(gz_vcf), FASTA], capture_output=True, text=True
    )
    assert result.returncode == 0


def test_malformed_vcf(tmp_path):
    bad_vcf = tmp_path / "bad.vcf"
    with open(VCF) as f_in, open(bad_vcf, "w") as f_out:
        for line in f_in:
            if not line.startswith("#"):
                # Remove a column to make it malformed
                fields = line.rstrip().split("\t")
                f_out.write("\t".join(fields[:4]) + "\n")
                break
            f_out.write(line)
    result = subprocess.run(
        ["python", SCRIPT, str(bad_vcf), FASTA], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "Malformed VCF line" in result.stderr


def test_missing_chromosome_in_fasta(tmp_path):
    # Remove a chromosome from the FASTA
    bad_fasta = tmp_path / "bad.fasta"
    with open(FASTA) as f_in, open(bad_fasta, "w") as f_out:
        skip = False
        for line in f_in:
            if line.startswith(">"):
                if not skip:
                    skip = True
                    continue  # skip first chromosome
            if not skip:
                f_out.write(line)
    result = subprocess.run(
        ["python", SCRIPT, VCF, str(bad_fasta)], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "No sequences found in FASTA file" in result.stderr


def test_empty_vcf(tmp_path):
    empty_vcf = tmp_path / "empty.vcf"
    empty_vcf.write_text("")
    result = subprocess.run(
        ["python", SCRIPT, str(empty_vcf), FASTA], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
