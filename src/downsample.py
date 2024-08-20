# can I get this all to work with bcf/bzipped files?? That would really improve things 

import subprocess
import random
import os.path
from helper_functions import parse_header

def get_keep_lines(vcf_path, num):
    # i should use bcftools - that would allow this to be gzipped
    all_lines = subprocess.run(["wc", "-l", vcf_path], capture_output = True, text = True).stdout
    # also find out how many header rows there are
    header_lines = subprocess.run(["grep", "^#", "-c", vcf_path], capture_output = True, text = True).stdout
    header_lines = int(header_lines.strip().split(" ")[0])
    # this is how many data lines there are in the file:
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

# def make_index_file(vcf_path, index_file):

#    # write index file
#     if index_file == "":
#         index_file = f"{vcf_path}.index"
#         print("INDEX FILE:")
#         print(index_file)

#     make = True

#     # if file exists and has lines - then don't make it
#     if os.path.isfile(index_file):
#         lines = subprocess.run(["wc", "-l", index_file], capture_output = True, text = True).stdout
#         print("LINE COUNT:")
#         line_count = int(lines.strip().split(" ")[0])
#         print(line_count)
#         if line_count > 0:
#             make = False
 
#     if make:
#         print("writing file of indices for downsampling")
#         with open(index_file, "w") as f:
#             subprocess.run(["cut", "-f1-2", vcf_path], stdout=f)
#     else:
#         print("indices already made, processing")
#     return(index_file)

# def get_header(vcf_path):
#     # helper function to count the number of "#" lines (header lines)
#     header_lines = subprocess.run(["grep", "^#", "-c", vcf_path], capture_output = True, text = True).stdout
#     header_lines = int(header_lines.strip().split(" ")[0])
#     print(f"header lines: {header_lines}")
#     return(header_lines)

# def downsample(vcf_path, new_vcf, num, indices, rep):
#     # use a uniqe ID (either the rep or create one)
#     if rep == None:
#         rep = uuid.uuid4()

#     # create a file with the first two columns of the vcf file (if necessary)
#     indices = make_index_file(vcf_path, indices)

#     # file with the SNP lines that we want to keep for downsampling
#     line_file = f"tmp_ds{num}_{rep}"
#     print(f"tmp: {line_file}")
#     # number of lines in the header
#     header_lines = get_header(vcf_path)
#     print(f"tmp line file")
    
#     # shuffle the indices and select the first n positions
#     print(f"number: {num}")
#     with open(line_file, "a") as lf:
#         command = f"tail -n +{header_lines} {indices} | sort -R | head -{num}"
#         subprocess.run(command, shell=True, stdout=lf, stderr=subprocess.PIPE, text=True)
#     print("tmp file written")
    
#     # write the header to the dowsampled file
#     with open(new_vcf, "w") as nf:
#         subprocess.run(["sed", f"{header_lines}q;d", indices], stdout=nf)
#     # now select those positions from the vcf
#     with open(new_vcf, "a") as nf:
#         subprocess.run(["bcftools", "view", vcf_path, "-T", line_file], stdout=nf)
#         print("DONE")
#         print(new_vcf)
#     #os.remove(line_file)
#     print("done")
    


def missing(gt, rate):
    if random.random() <= rate:
        return("./.")
    else:
        return(gt)

def add_missingness(vcf_path, new_vcf, sample_list, rate):
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
                line = [missing(line[i], rate) if i in include else line[i] for i in range(len(line))]
               # the line may be updated by the above step or not. Regardless, write it out
                outfile.write("\t".join(line) + "\n")

