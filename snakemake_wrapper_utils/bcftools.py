import sys


def get_bcftools_opts(snakemake):
    """Obtain bcf_opts from output, params, and handle resource definitions in resources."""
    bcf_opts = ""
    extra = snakemake.params.get("extra", "")

    ###############
    ### Threads ###
    ###############
    if "--threads" in extra:
        sys.exit(
            "You have specified number of threads (`--threads`) in params.extra; please use only `threads`."
        )
    bcf_opts += (
        "" if snakemake.threads <= 1 else "--threads {}".format(snakemake.threads - 1)
    )

    #####################
    ### Output format ###
    #####################
    if "-O" in extra or "--output-type" in extra:
        sys.exit(
            "You have specified output format (`-O/--output-type`) in params.extra; this is automatically infered from output file extension."
        )

    # Output uncompressed BCF; ignored if output is VCF
    uncompressed_bcf = snakemake.params.get("uncompressed_bcf", False)

    output = snakemake.output[0]
    if output.endswith(".vcf"):
        out_format = "v"
    elif output.endswith(".vcf.gz"):
        out_format = "z"
    elif output.endswith(".bcf"):
        if uncompressed_bcf:
            out_format = "u"
        else:
            out_format = "b"
    else:
        raise ValueError("invalid output file extension ('.vcf', '.vcf.gz', '.bcf').")

    bcf_opts += f" --output-type {out_format}"

    ##############
    ### Memory ###
    ##############
    # Should resources.mem_mb be passed to bcftools (not all tools support this option)
    bcftools_use_mem = snakemake.params.get("bcftools_use_mem", False)

    if "-m" in extra or "--max-mem" in extra:
        sys.exit(
            "You have provided `-m/--max-mem` in params.extra; please only use resources.mem_mb and set params.bcftools_use_mem."
        )
    # Getting memory in megabytes, as advised in documentation.
    if "mem_mb" in snakemake.resources.keys() and bcftools_use_mem:
        bcf_opts += " --max-mem {}M".format(snakemake.resources["mem_mb"])
    # Getting memory in gigabytes, for user convenience. Please prefer the use
    # of mem_mb over mem_gb as advised in documentation.
    elif "mem_gb" in snakemake.resources.keys() and bcftools_use_mem:
        bcf_opts += " --max-mem {}G".format(snakemake.resources["mem_gb"])

    ################
    ### Temp dir ###
    ################
    if "-T" in extra or "--temp-dir" in extra:
        sys.exit(
            "You have provided `-T/--temp-dir` in params.extra; please provide a temp dir as output.bcftools_temp."
        )
    # Getting temp directory from output files list
    if "bcftools_temp" in snakemake.output.keys():
        bcf_opts += " --temp-dir {}".format(snakemake.output["bcftools_temp"])

    return bcf_opts
