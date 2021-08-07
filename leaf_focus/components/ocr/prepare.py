from pathlib import Path
from PIL import Image


class Prepare:
    def threshold(self, input_file: Path, output_file: Path, threshold: int) -> None:
        if not input_file:
            raise ValueError("Must supply input file.")
        if not output_file:
            raise ValueError("Must supply output file.")
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist '{input_file}'.")
        if output_file.exists():
            raise FileExistsError(f"Output file already exists '{input_file}'.")
        if threshold < 0 or threshold > 255:
            raise ValueError(f"Threshold must between 0 and 255, not {threshold}.")

        img = Image.open(input_file)

        def calc_threshold(value):
            return 255 if value > threshold else 0

        r = img.convert("L").point(calc_threshold, mode="1")
        r.save(output_file)
