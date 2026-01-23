# ArchSim
## A package for simulating archaic sediment and skeletal DNA features in VCF's

---
1. [Installation](#Installation)
2. [Usage](#Usage)
3. [Simulation Details](#Simulation Details)
3. [Examples](#Examples)
---

## Installation

Clone the repository:
```bash
git clone https://github.com/sarahaj32/archSim.git
```

Dependencies: Python3, json
Ensure that python3 is installed

## Usage 
```note

The package is run on command line 
### Required arguments for all simulation modes:
**simulation mode** (options: psuedohaploid, deaminate, contaminate, downsample, missing, dpFilter)

-**vcf** <vcf_path>

### Optional arguments for all simulation modes:
-**out** [name and path to output file] default = out.vcf

-**targets** [comma separated list of target populations] default = all
or a json file with "targets": 

### Module specific arguments:

> psuedohaploid         
    -vcf                [required] path to the vcf to simulate data in
    -out                outputfile (defaults to pseudohaploid.bed)
    -targets            a comma separated list of targets sample names, or path to a json file containing target sample names. These target samples are the ones that will become psuedohaploid

> deaminate:
    -vcf                [required] path to the vcf to simulate data in
    -out                outputfile (defaults to deaminate.bed)
    -targets            a comma separated list of targets sample names, or path to a json file containing target sample names. These target samples are the ones that will become psuedohaploid
    -rate               rate at which deamination will be simulated in the sites of the target population. Default = 0.05. (at this rate, homozygous reference gentoypes at transition sites in the selected individuals will convert to heterozygous)
    -proportion         The proportion of sites that will be specified as transitions. If this argument is not included, transition sites will be identified from VCF alleles

> contaminate
    -vcf                [required] path to the vcf to simulate data in
    -out                outputfile (defaults to deaminate.bed)
    -targets            a comma separated list of targets sample names, or path to a json file 
    -ancestral          flag that indicates that contaminated sites will be converted to heterozygous
    -mh                 flag that indicates that contaminated sites will be contributed from a given set of modern human individuals
    -modern             comma separated list of individuals to contaminate with, or path to a json file
    -length             length of contaminating modern human fragments. Default = 1

#### downsample
-**num** number of snps to downsample to. Default = 30,000

#### missing
-**rate** rate of missingness to simulate. Default = 0.1

#### dpFilter 
-**mean** mean depth to simulate. Default = 5

-**variance** variance of depth to simulate. Default = 2

-**missing** flag that to convert genotypes at sites with 0 reads to missing (./.)

-**annotate** flag that indiciates to only annotate with depth (do not add missing genotypes, do not change genotypes to simulate homozygous bias)

*** Currently, only one mode can be run at a time (adding multiple flags will run but will overwrite each file with each newly created file)
```

## Examples:
vcf=original_filtered_21.vcf

Example adding 1% modern human contamination in blocks of 500 bp to populations Vindija and Denisova from populations AFR and mh_contam:

python src/main.py contaminate -mh -vcf data/archaic_admix_MHtarget/original/full/vcf/original_filtered_21.vcf -out ./test/mhcontam_21.vcf -rate 0.01 -length 500 -target Vindija,Denisova -modern AFR,mh_contam

Example adding deamination to all individuals:

python src/main.py deaminate -vcf $vcf -out ./test/deaminated_21.vcf -r 0.5

Example making all populations pseudohaploid:

python src/main.py pseudohaploid -vcf $vcf -out ./test/pseudohaploid_21.vcf 

Example making only populations 0 and 10 pseudohaploid:

python src/main.py pseudohaploid -vcf $vcf -out ./test/pseudohaploid_pop0pop10_21.vcf -target pop_0,pop_10

## Simulation details
# pseudohaploid:
At every position, an allele will be randomly selected from each target individual, and the genotype will become homozygous for that allele. Homozygous positions will be unaffected, but heterozygous positions will be converted to homozygous reference or homozygous alternative with an even probability. If the input is phased VCF, the output pseudohaploid VCF will still be phased. 

Example:

# deaminate:
We induce genotype errors at transition sites, representative of errors likely to be seen from deamination, by converting homozygous reference calls to heterozygous calls at the specified rate (0.05 by default). By default, transition sites are determined from the VCF alleles as C/T, T/C, A/G, G/A sites. However, if the "-proportion" argument is specified, transition sites will be determined as that proprotion of all sites. Multiallelic positions are skipped in this step and removed from the output file. If the input genotypes are phased, the output genotypes will still be phased, and any new alternative alleles will be randomly assigned to either chromosome.  

# contaminate
At every position in all specified individuals, at a specified rate contamination may be added. When contamination is added:
1. a modern human individual is randomly selected
2. the genotype of the contaminatED individual is swapped for the genotype of the contaminatING individual
3. The genotypes are similarly swapped for the next 'length' basepairs (ie: if length = 1000, any SNPs in the next 1000 basepairs will receive the genotype of the contaminating individual). This is tracked separately for each contaminatED individual, so all contaminating "chunks" are independent
4. After this contaminating "chunk" the process repeats, and at the same rate again at the next position, that individual may be contaminated

# contaminate
At every position in all specified individuals, at a specified rate contamination may be added. When contamination is added:
1. a modern human individual is randomly selected
2. the genotype of the contaminatED individual is swapped for the genotype of the contaminatING individual
3. The genotypes are similarly swapped for the next 'length' basepairs (ie: if length = 1000, any SNPs in the next 1000 basepairs will receive the genotype of the contaminating individual). This is tracked separately for each contaminatED individual, so all contaminating "chunks" are independent
4. After this contaminating "chunk" the process repeats, and at the same rate again at the next position, that individual may be contaminated

> modern human contamination
At every position in all specified individuals, at a specified rate contamination may be added. When contamination is added:
1. a modern human individual is randomly selected
2. the genotype of the contaminatED individual is swapped for the genotype of the contaminatING individual
3. The genotypes are similarly swapped for the next 'length' basepairs (ie: if length = 1000, any SNPs in the next 1000 basepairs will receive the genotype of the contaminating individual). This is tracked separately for each contaminatED individual, so all contaminating "chunks" are independent
4. After this contaminating "chunk" the process repeats, and at the same rate again at the next position, that individual may be contaminated
```