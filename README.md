# Conda2SIF

This python script allows a user to convert a single conda environment definition file (typically in YAML format), into a singularity image file where all the components of your conda environment will be installed.

## Usage

### General usage

```
usage: conda2sif.py [-h] --env ENV [--output OUTPUT] [--template TEMPLATE] [--keep-def] [--singularity-images SINGULARITY_IMAGES]

Convert conda environment file to Singularity image file

options:
  -h, --help            show this help message and exit
  --env ENV, -e ENV     Conda environment file (yaml)
  --output OUTPUT, -o OUTPUT
                        Output Singularity image file (either relative or absolute)
  --template TEMPLATE   Singularity definition template file (relative to the templates folder in this app's install directory)
  --keep-def, -k        Keep the generated Singularity definition file
  --singularity-images SINGULARITY_IMAGES
                        Path to folder containing your images
```

### Quick start

```bash
./conda2sif.py --env /path/to/env.yaml
```

This will create a singularity image file named `output.sif` (by default).
The `.def` file will be removed by default (use `-k` to keep it).

If a folder named `singularity_images` exists in your home path, both `.def` and `.sif` files will be outputted to this folder.

Otherwise, `.sif` and `.def` files will be stored in the current working directory.