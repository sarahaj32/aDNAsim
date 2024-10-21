"""
Helper file with functions to downsample a VCF to a specified number of sites
and add missing genotypes to a VCF at a specified rate
"""

import subprocess
import random
import os.path
from helper_functions import parse_header

def get_keep_lines(vcf_path, num):
    """
    A helper function that determines how many data lines are in a vcf file (excluding header),
    downsamples to a specified number of lines, and outputs a list of the subsampled
    lines to keep 
    """
    # i should use bcftools - that would allow this to be gzipped
    # find out how many lines are in the file
    all_lines = subprocess.run(["wc", "-l", vcf_path], capture_output = True, text = True).stdout
    # also find out how many header rows there are
    header_lines = subprocess.run(["grep", "^#", "-c", vcf_path], capture_output = True, text = True).stdout
    header_lines = int(header_lines.strip().split(" ")[0])
    # calculate how many data lines there are in the file:
    all_lines = int(all_lines.strip().split(" ")[0]) - header_lines
    print(f"all lines: {all_lines}")
    print(num)
    # select num rows from the all_lines available data rows
    to_keep = random.sample(range(header_lines, all_lines), num)
    to_keep = to_keep + list(range(header_lines))
    to_keep.sort()
    # to_keep is the list of the lines that we're keeping
    return(to_keep)

def downsample(vcf_path, new_vcf, num):
    """
    A function that only saves a specified number 'num' of positions to the new vcf 
    These positions are randomly distributed across the input file
    """
    to_keep = get_keep_lines(vcf_path, num)
    with open(vcf_path, "r") as file1, open(new_vcf, "w") as outfile:
        line_count = 0
        for line in file1:
            if line_count > 10000 and line_count % 100000 == 0:
                print(f"line: {line_count}")
            if not to_keep:
                break
            elif line_count == to_keep[0]:
                line = line.strip().split("\t")
                to_keep.remove(line_count)
                outfile.write("\t".join(line) + "\n")
            line_count += 1   

def missing(gt, rate):
    """
    A helper function that returns a missing genotype at a specified rate
    """
    if random.random() <= rate:
        return("./.")
    else:
        return(gt)

def add_missingness(vcf_path, new_vcf, sample_list, rate):
    """
    A function that converts a specified rate of genotypes to missing in the 
    specified samples
    """
    with open(vcf_path, "r") as file1, open(new_vcf, "w") as outfile:
        for line in file1:
            line = line.strip().split("\t")
            if line[0].startswith("#"): 
                outfile.write("\t".join(line) + "\n")
                if "#CHROM" in line[0]:
                    header_ix, include = parse_header(line, sample_list)
                    print(f"adding missingness to: {sample_list}")
                    print(f"include:{include}")
            else:
                # convert genotypes in the specified samples to missing at the given rate
                line = [missing(line[i], rate) if i in include else line[i] for i in range(len(line))]
                outfile.write("\t".join(line) + "\n")

