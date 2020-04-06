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
