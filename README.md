# singbuilder

This python script allows a user to convert a single conda environment definition file (typically in YAML format), into a singularity image file where all the components of your conda environment will be installed.

The resulting image will always activate said environment, whether on `run`, `exec`, or `shell`.

## Usage

### General usage

```
usage: singbuilder.py [-h] [--output OUTPUT_DIR] [--template TEMPLATE_NAME] [--def-only] [--name NAME] {conda2sif,pip2sif} ...

Convert conda environment file to Singularity image file

positional arguments:
  {conda2sif,pip2sif}   Sub-command to run
    conda2sif           Convert conda environment file to Singularity image
    pip2sif             Convert pip requirements file to Singularity image

options:
  -h, --help            show this help message and exit
  --output OUTPUT_DIR, -o OUTPUT_DIR
                        Output folder, with definitions and images subfolders. Definition file will be written to definitions/<name>.def Image file will be written to images/<name>.sif
  --template TEMPLATE_NAME, -t TEMPLATE_NAME
                        Singularity definition template file (relative to the templates folder in this app's install directory)
  --def-only            Only generate def file, do not run singularity build
  --name NAME, -n NAME  Name of the Singularity image file (without extension). If not specified, the name will be derived from the conda environment file or pip requirements file name.
```

### Quick start

```bash
./singbuilder.py conda2sif --env env.yaml
```

This will create a singularity image file named with the env name found in `env.yaml` (the default).

The `.def` file will be saved in the output directory, as `definitions/{name}/{name}.def`
If `--def-only` is not specified, this will create `images/{name}.sif`
