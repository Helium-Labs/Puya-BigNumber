import os
import subprocess


def process_algokit(dir_path: str, filename: str) -> None:
    """
    Process the algokit compilation and TypeScript file generation.

    Args:
    - dir_path: The directory path where the contract file is located.
    - filename: The name of the file (without the extension).
    """
    # Get the script directory (assuming the script is run from its location)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Full path to the contract file
    contract_path = os.path.join(dir_path, f"{filename}.py")

    # Output directory for the compiled files
    output_dir = os.path.join(script_dir, "build")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Run the algokit compile command
    compile_command = [
        "algokit",
        "compile",
        "py",
        contract_path,
        "-g",
        "2",
        "-O",
        "2",
        "--out-dir",
        output_dir,
    ]
    subprocess.run(compile_command, check=True)


def build(path: str, filename: str):
    process_algokit(path, filename)
