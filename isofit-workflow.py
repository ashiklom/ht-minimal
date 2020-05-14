#!/usr/bin/env python3

import json
import os
import copy

def mkdir_f(*argv):
    path = os.path.abspath(os.path.join(*argv))
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def save_json(obj, json_path):
    """Save dict() to JSON text file."""
    try:
        with open(json_path, 'w') as fh:
            fh.write(json.dumps(obj, indent=4, sort_keys=True))
    except OSError as e:
        raise

# Read config file
with open("config.json") as f:
    config = json.load(f)

# Set environment variables if present
if "env" in config:
    for key, value in config["env"].items():
        os.environ[key] = value

# Check config file
assert ('outdir' in config), "Missing `outdir` in config"
outdir = mkdir_f(config["outdir"])

# Read Isofit template file
with open("template.json") as f:
    template = json.load(f)

# Get file extension of input reflectance
# If it's text, spit out text.
# Otherwise, assume binary (ENVI shapefile)
infile = template["forward_model"]["surface"]["reflectance_file"]
is_txt = infile.endswith("\\.txt")
if is_txt:
    ext = ".txt"
else:
    ext = ""

# Forward atmospheric model
# surface reflectance -> TOA radiance
final_script_file = os.path.join(outdir, "run_all.sh")
final_script = open(final_script_file, "w")
final_script.write("#!/usr/bin/env bash\n")
for date in config["dates"]:
    for time in config["times"]:
        assert (len(time) == 4), "Invalid time format. Must be HHMM."
        for atm in config["atmospheres"]:
            for vzen in config["vzen"]:

                # function of date, time, atm, vzen

                year, month, day = date.split("-")
                hour = time[0:2]
                minute = time[2:4]

                casedir = mkdir_f(outdir, "atm_{}__{}__{}__vzen_{:.2f}".format(atm, date, time, vzen))

                lrt_template = open(template["forward_model"]["radiative_transfer"]["radiative_transfer_engines"]["vswir"]["template_file"], "r").read()
                lrt_configuration = lrt_template.format(atmosphere = atm, year = year, month = month, day = day,
                                                        hour = hour, minute = minute)
                lut_path = mkdir_f(casedir, "lut")
                lrt_outfile = os.path.join(lut_path, "lrt_template.inp")
                with open(lrt_outfile, "w") as f:
                    f.write(lrt_configuration)

                forward_config = copy.deepcopy(template)
                lrt_config = forward_config["forward_model"]["radiative_transfer"]["radiative_transfer_engines"]["vswir"]
                lrt_config["lut_path"] = lut_path
                lrt_config["template_file"] = lrt_outfile

                # Fix a few other important absolute paths
                lrt_config["wavelength_file"] = os.path.abspath(lrt_config["wavelength_file"])
                forward_config["forward_model"]["instrument"]["wavelength_file"] = os.path.abspath(forward_config["forward_model"]["instrument"]["wavelength_file"])
                forward_config["forward_model"]["surface"]["reflectance_file"] = os.path.abspath(forward_config["forward_model"]["surface"]["reflectance_file"])

                case_outdir = mkdir_f(casedir, "output")
                simulated_radfile = os.path.join(case_outdir, "simulated_toa_radiance" + ext)
                forward_config["output"] = {"simulated_measurement_file": simulated_radfile}
                forward_config["inversion"]["simulation_mode"] = True
                forward_file = os.path.join(casedir, "forward.json")
                save_json(forward_config, forward_file)

                # Inverse atmospheric model
                # TOA radiance -> surface reflectance
                inverse_config = copy.deepcopy(template)
                inverse_config["input"] = {"measured_radiance_file": simulated_radfile}
                inverse_config["output"] = {
                    "estimated_reflectance_file": os.path.join(case_outdir, "estimated_reflectance" + ext),
                    "estimated_state_file": os.path.join(case_outdir, "estimated_state" + ext)
                }
                inverse_config["forward_model"] = forward_config["forward_model"]
                inverse_file = os.path.join(casedir, "inverse.json")
                save_json(inverse_config, inverse_file)

                # Write script for running case
                scriptfile = os.path.abspath(os.path.join(casedir, "run.sh"))
                with open(scriptfile, "w") as f:
                    f.write("#!/usr/bin/env bash\n")
                    f.write("set -e\n")
                    f.write("echo 'Starting forward mode'\n")
                    f.write("isofit --level DEBUG {}\n".format(forward_file))
                    f.write("echo 'Done!'\n")
                    f.write("echo 'Starting inverse mode'\n")
                    f.write("isofit --level DEBUG {}\n".format(inverse_file))
                    f.write("echo 'Done!'")

                final_script.write("bash {} &> {}/log \n".format(scriptfile, casedir))
