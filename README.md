# Quickstart

Prerequisites:

- A compiled version of LibRadTran. Make sure to compile it in a _separate_ conda environment (or in your native OS environment); it will not compile if `python` is pointing to `python3` instead of `python2`, as is the case with this conda environment. Note that LibRadTran does not have to be installed on the `PATH` -- just compiled; e.g. I configured it with (from inside the LibRadtran directory) `./configure --prefix=$PWD` and just `make` (not `make install`).
- The latest version of Isofit, patched with @ashiklom's [fixes for LibRadTran](https://github.com/ashiklom/isofit/tree/libradtran-fixes). The recommendation is to install this _inside_ your hypertrace-specific conda environment.

Template files:

- `template.json` -- The Isofit template configuration. Specific sections of this will be overwritten by the `isofit-workflow.py` script, but in general, this should be a complete Isofit JSON configuration file. See `isofit/test/data/config_forward.json` and `isofit/test/data/config_inversion.json` from the Isofit repository for some examples.
- `data/lrt_template.inp` -- A complete LibRadTran template file. Similar to `template.json`, this will be only slightly modified by the Python script (only the string formatting templates `{aerosol_visibility}` and `{h2o_mm}`), so it should be otherwise self-sufficient. In particular, you may need to modify the `source solar` path -- the default is relative to the `$LIBRADTRAN_DIR/test` directory, but an absolute path may be safer.

Configuration file (`config.json`): A JSON file with the following fields:

- `atmospheres` -- List of LibRadTran atmospheres over which to iterate
- `dates` -- List of dates over which to iterate (e.g. `["2017-06-01", "2017-08-01"]`)
- `times` -- List of times over which to iterate, as strings with format `"HHMM"` (e.g. `["0900", "1700"]`)
- `vzen` -- List of view (instrument) zenith angles, in degrees, to iterate over (numeric) (e.g. `[0, 30]`)
- `outdir` -- The output directory, as a string
- `reflectance_file` -- The true input reflectance file
- `env` (optional) -- A named list of environment variables to pass to Isofit. The most important one is probably `LIBRADTRAN_DIR`, which points to the directory where your `libradtran` installation is located.

Executing a workflow involves two steps:

- Run `python isofit-workflow.py` to generate the Isofit configuration files
- Run `bash <outdir>/run_all.sh` script to actually execute the workflow. Note that this uses native bash background process syntax (`&`) to run workflows in parallel over as many cores as are available.

# Hypertrace workflow

## Forward model

Go from surface reflectance to top-of-atmosphere radiance.
A complete example is in `forward.json`.
Needs the following components:

- `output`
  - `simulated_measurement_file` -- Path to target output file. All parent directories must exist -- they will not be created automatically.
- `forward_model`
    - `instrument`
        - `integrations` -- Number of integrations (default = 1) ???
        - `wavelength_file` -- Instrument wavelength file. Plain-text file with two columns, separated by spaces: wavelength (μm or nm) and FWHM
        - `SNR`, `parametric_noise_file`, `pushbroom_noise_file`, `NEDT_noise_file` -- Instrument noise characteristics. Either a single SNR value or a path to the file with corresponding coefficients.
    - `surface`
        - `reflectance_file` -- Path to a file containing measured surface reflectance, which will be converted to TOA radiance
    - `radiative_transfer`
        - `libradtran_vswir` (if using Libradtran)
            - `wavelength_file` -- Wavelengths to simulate (??)
            - `libradtran_directory` -- Path to libradtran source code
            - `libradtran_template_file` -- Path to libradtran template file
            - `lut_path` -- Target directory for RTM look-up tables (LUTs) (dir must already exist)
            - `lut_names` -- Character array of names of variables in look-up tables. Typically `["H2OSTR", "AOT550"]`
            - `statevector_names` -- The corresponding names of variables in the statevector. For LibRadtran, should be the same as `lut_names`
- `inversion`:
    - `simulation_mode`: Whether or not to do forward simulation. Here, this should be `true`
    - `windows`: Inversion wavelength windows. List of length-2 lists. Usually `[[400, 1300], [1450, 1780], [1950, 2450]]`.
