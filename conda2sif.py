#!/usr/bin/env python

import argparse
from pathlib import Path

import jinja2
import yaml


def conda2def(conda_env_file: Path, output: Path, template_name: str = "conda2def.def"):
    with open(conda_env_file, "r") as f:
        conda_env = yaml.safe_load(f)
        env_name = conda_env["name"]

        with open(output, "w") as sif:
            template_loader = jinja2.FileSystemLoader(searchpath=Path(__file__).parent / "templates")
            template_env = jinja2.Environment(loader=template_loader)
            template = template_env.get_template(template_name)
            sif.write(template.render({"env": {"name": env_name, "filename": str(conda_env_file), "base_filename": str(conda_env_file.name)}}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert conda environment file to Singularity definition file")
    parser.add_argument("--env", help="Conda environment file (yaml)", type=Path, required=True)
    parser.add_argument("--output", help="Output Singularity definition file", type=Path, default="output.def")
    parser.add_argument("--template", help="Singularity definition template file", default="conda2def.def")

    args = parser.parse_args()
    conda2def(args.env, args.output, args.template)

    # subprocess.call(["singularity", "build", "--fakeroot", f"{args.output.stem}.sif", f"{args.output}"])

    # os.remove(args.output)
