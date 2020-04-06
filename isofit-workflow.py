#!/usr/bin/env python3

import json
import isofit
import os
import copy

def mkdir_f(*argv):
    path = os.path.join(*argv)
    if not os.path.exists(path):
        os.mkdir(path)

# Read config file
with open("config.json") as f:
    config = json.load(f)

# Check config file
assert ('outdir' in config), "Missing `outdir` in config"
outdir = config["outdir"]
mkdir_f(outdir)

# Read Isofit template file
with open("template.json") as f:
    template = json.load(f)

# Write configs

mkdir_f(outdir, "configs")
# for az in config["az"]:
az = config["az"][0]
zen = config["zen"][0]
#     for zen in config["zen"]:

# Create look-up tables for atmospheric RTM
# TODO: No loop here?
lut_config = copy.deepcopy(template)
lut_config["output"]["simulated_measurement_file"] = output

# Forward atmospheric model
# surface reflectance -> TOA radiance

# Inverse atmospheric model
# TOA radiance -> surface reflectance
