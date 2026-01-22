"""
Helper file with functions to deaminate genotypes of a 
target individual. 
"""

from helper_functions import parse_header, multiallelic
import random

# function to create the heterozygous deaminated genome call
def deam_geno_call(base, rate):
    """
    Helper function that adds contamination to homozygous
    reference positions at a specified rate
    base is a biallelic genotype 
    rate is the rate of deamination
    simulation retains phasing 
    """
    # only change homozygous reference positions
    if base[0] != '0' or base[2] != '0':
        return base
    # if NOT deaminated (by chance), don't alter
    elif random.random() >= rate:
        return base
    # randomly select which allele is deaminated
    if base[1] == "/":
        return(f"0/1{base[3:]}")
    elif round(random.random()):
        return(f"1{base[1]}0{base[3:]}")
    else:
        return(f"0{base[1]}1{base[3:]}")

def add_deam(vcf_path, new_vcf, sample_list, rate, ts_proportion):
    """
    converts homozygous reference transition genotypes 
    to heterozygous at specified deamination rate. 
    Transtions are either defined by the alleles in the VCF,
    or specified as a proportion of all sites (ts_proportion).
    """
    with open(vcf_path, "r") as file1, open(new_vcf, "w") as outfile:
        for line in file1:
            line = line.strip().split("\t")
            if line[0].startswith("#"): 
                outfile.write("\t".join(line) + "\n")
                if "#CHROM" in line[0]:
                    # header_idx: dictionary with indices of VCF header columns
                    # include: the indices of the samples for the simulation to be applied to
                    # names: the sample names corresponding to the include indices
                    header_ix, include, names = parse_header(line, sample_list)
                    
                    # print information about the samples being deaminated
                    if sample_list != []:
                        print(f"\nmaking {names} samples deaminated at {rate} rate\n")
                    else:
                        print(f"\nmaking all samples deaminated at {rate} rate\n")
                    
                    # print information about the deamination simulation
                    if ts_proportion:
                        print(f"\ndefining transition sites as a {ts_proportion} of all sites\n")
                    else:
                        print(f"\ndefining transition sites based on VCF alleles\n")
            else:
                if not multiallelic(line, header_ix):
                    # if we are defining transition sites as a proportion of all sites:
                    if ts_proportion:
                        # determine if this is a transition site based on that proportion
                        if random.random() <= ts_proportion:
                            line = [deam_geno_call(line[i], rate) if i in include else line[i] for i in range(len(line))]
                    
                    # otherwise, use the alleles in the VCF to determine if it's a transition site
                    else:
                        # find the transition sites and add deamination
                        # at all transition sites, convert homozygous reference to heterozygous 
                        if (line[header_ix["ref_ix"]] == "C" and line[header_ix["alt_ix"]] == "T") or (line[header_ix["ref_ix"]] == "G" and line[header_ix["alt_ix"]] == "A"):
                            line = [deam_geno_call(line[i], rate) if i in include else line[i] for i in range(len(line))]
                        elif (line[header_ix["ref_ix"]] == "T" and line[header_ix["alt_ix"]] == "C") or (line[header_ix["ref_ix"]] == "A" and line[header_ix["alt_ix"]] == "G"):
                            line = [deam_geno_call(line[i], rate) if i in include else line[i] for i in range(len(line))]
                    # the line may be updated by the above steps or not. Regardless, write it out
                    outfile.write("\t".join(line) + "\n")
