#!/usr/bin/env python

import argparse
import os
import subprocess
from pathlib import Path

import jinja2
import yaml


def conda2def(conda_env_file: Path, output: Path, template_name: str = "conda2def.def"):
    with open(conda_env_file, "r") as f:
        conda_env = yaml.safe_load(f)
        env_name = conda_env["name"]

        with open(output.with_suffix(".def"), "w") as def_file:
            template_loader = jinja2.FileSystemLoader(
                searchpath=Path(__file__).parent / "templates"
            )
            template_env = jinja2.Environment(loader=template_loader)
            try:
                template = template_env.get_template(template_name)
            except jinja2.exceptions.TemplateNotFound:
                print(
                    f"Error: Template {template_name} not found in templates directory! Remember it has to be relative to {Path(__file__).parent / 'templates'}."
                )
                print("Available templates are:")
                for template in template_loader.list_templates():
                    print(template)
                exit(1)
            def_file.write(
                template.render(
                    {
                        "env": {
                            "name": env_name,
                            "filename": str(conda_env_file),
                            "base_filename": str(conda_env_file.name),
                        }
                    }
                )
            )

    return 0


def def2sif(output_file_name: Path):
    if output_file_name.exists():
        confirmation = input(f"Remove existing image at {output_file_name}? (yes/No)")
        if confirmation.lower()[0] != "y":
            print("Exiting without creating the image.")
            exit(0)
        else:
            os.remove(output_file_name)

    command = [
        "singularity",
        "build",
        "--fakeroot",
        str(output_file_name),
        str(output_file_name.with_suffix(".def")),
    ]

    print("Running command: ", " ".join(command))

    success = subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert conda environment file to Singularity image file"
    )
    parser.add_argument(
        "--env", "-e", help="Conda environment file (yaml)", type=Path, required=True
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output Singularity image file (either relative or absolute)",
        type=Path,
        default="output.sif",
    )
    parser.add_argument(
        "--template",
        help="Singularity definition template file (relative to the templates folder in this app's install directory)",
        default="conda2def.def",
    )
    parser.add_argument(
        "--keep-def",
        "-k",
        help="Keep the generated Singularity definition file",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--singularity-images",
        help="Path to folder containing your images",
        default=f"{os.environ['HOME']}/singularity_images",
        type=Path,
    )

    args = parser.parse_args()

    output_file_name: Path = args.output
    output_dir: Path = args.singularity_images

    if not output_dir.is_dir():
        print(
            "Warning: No directory specified for Singularity images. Using the current directory instead."
        )
        print(
            "If you'd like to specify a directory, use the --singularity-images option."
        )
        output_dir = Path.cwd()

    if not output_file_name.is_absolute():
        if not output_dir.exists():
            print(
                "Error: Cannot find the specified directory for Singularity images. Please create it first."
            )
            exit(1)
        if not output_dir.is_dir():
            print(
                "Warning: The specified path for Singularity images is not a directory. Using the current directory instead."
            )
            output_dir = Path.cwd()

        output_file_name = output_dir / output_file_name

    def_success = conda2def(args.env, output_file_name, args.template)

    if def_success == 0:
        print(
            f"Singularity definition file created at {output_file_name.with_suffix('.def')}"
        )
    else:
        print("Error creating Singularity definition file. Exiting.")
        exit(1)

    sif_success = def2sif(output_file_name)

    if sif_success == 0:
        print(f"Singularity image file created at {output_file_name}")

        if not args.keep_def:
            os.remove(output_file_name.with_suffix(".def"))
    else:
        print(
            f"Error creating Singularity image file. Image definition file is kept at {output_file_name.with_suffix('.def')}"
        )
