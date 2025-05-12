#!/usr/bin/env python

import argparse
import os
import subprocess
from pathlib import Path

import jinja2
import yaml


def pip2def(reqs: list[str], output: Path, template_name: str = None):

    template_name = template_name or "pip2def.def"

    with open(output, "w") as def_file:
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
            for tpl in template_loader.list_templates():
                print(tpl)
            exit(1)

        def_file.write(template.render({"reqs": reqs}))

    return 0


def conda2def(conda_env_file: Path, output: Path, template_name: str = None):

    import shutil

    template_name = template_name or "conda2def.def"

    shutil.copyfile(conda_env_file, output.parent / conda_env_file.name)

    with open(conda_env_file, "r") as f:
        conda_env = yaml.safe_load(f)
        env_name = conda_env["name"]

        with open(output, "w") as def_file:
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
                for template_name in template_loader.list_templates():
                    print(template_name)
                exit(1)
            def_file.write(
                template.render(
                    {
                        "env": {
                            "env_name": env_name,
                            "filename": str(conda_env_file.name),
                        }
                    }
                )
            )

    return 0


def def2sif(input_file: Path, output_file: Path):
    if output_file.exists():
        confirmation = input(f"Remove existing image at {output_file}? (yes/No)")
        if confirmation.lower()[0] != "y":
            print("Exiting without creating the image.")
            exit(0)
        else:
            os.remove(output_file)

    pwd_before = os.getcwd()

    # cd to input def file's directory. Definition files refer to files relative to their parent directory
    os.chdir(input_file.parent)

    command = [
        "singularity",
        "build",
        "--fakeroot",
        str(output_file),
        str(input_file),
    ]

    print("Running command: ", " ".join(command))

    success = subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # After the command is run, we don't want confusing bugs for the rest of the program (even though I know this is the last function run for now)
    os.chdir(pwd_before)

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Convert conda environment file to Singularity image file"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Sub-command to run"
    )

    # Subparser for conda2sif
    conda_parser = subparsers.add_parser(
        "conda2sif", help="Convert conda environment file to Singularity image"
    )
    conda_parser.add_argument(
        "--env",
        "-e",
        help="Conda environment file (yaml)",
        type=Path,
        required=True,
        dest="conda_env_file",
    )
    conda_parser.set_defaults(func=conda2def)

    # Subparser for pip2sif
    pip_parser = subparsers.add_parser(
        "pip2sif", help="Convert pip requirements file to Singularity image"
    )
    pip_parser.add_argument(
        "--reqs", "-r", help="Pip requirements file (txt)", type=Path, required=True
    )
    pip_parser.set_defaults(func=pip2def)

    # Common arguments for both subparsers
    parser.add_argument(
        "--output",
        "-o",
        help="Output folder, with definitions and images subfolders. Definition file will be written to definitions/<name>.def\nImage file will be written to images/<name>.sif",
        type=Path,
        default="~/Bioinfo/singularities",
        dest="output_dir",
    )
    parser.add_argument(
        "--template",
        "-t",
        help="Singularity definition template file (relative to the templates folder in this app's install directory)",
        dest="template_name",
        default=None,
    )
    parser.add_argument(
        "--def-only",
        help="Only generate def file, do not run singularity build",
        action="store_true",
    )
    parser.add_argument(
        "--name",
        "-n",
        help="Name of the Singularity image file (without extension). If not specified, the name will be derived from the conda environment file or pip requirements file name.",
        type=str,
        default=None,
    )

    args = vars(parser.parse_args())

    def_generator = args.pop("func")
    command = args.pop("command")
    name = args.pop("name")
    output_dir: Path = args.pop("output_dir")
    def_only: bool = args.pop("def_only")

    if not output_dir.is_dir():
        print(
            "Warning: No directory specified for Singularity images. Using the current directory instead."
        )
        print(
            "If you'd like to specify a directory, use the --singularity-images option."
        )
        output_dir = Path.cwd()

    if name is None:
        if command == "conda2sif":
            import yaml

            with open(args["env"], "r") as f:
                conda_env = yaml.safe_load(f)
                name: str = conda_env["name"]
        elif command == "pip2sif":
            name: str = args["reqs"].stem

    (output_dir / "definitions" / name).mkdir(parents=True, exist_ok=True)
    (output_dir / "images").mkdir(parents=True, exist_ok=True)

    def_file_path = output_dir / "definitions" / name / f"{name}.def"

    def_success = def_generator(**args, output=def_file_path)

    if def_success == 0:
        print(f"Singularity definition file created at {def_file_path}")
    else:
        print("Error creating Singularity definition file. Exiting.")
        exit(1)

    if not def_only:

        sif_file_path = output_dir / "images" / f"{name}.sif"

        sif_success = def2sif(def_file_path, sif_file_path)

        if sif_success == 0:
            print(f"Singularity image file created at {sif_file_path}")

        return sif_success


if __name__ == "__main__":
    exit(main())
