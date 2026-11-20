"""Validate, preview, or install the bundled v2 desktop pet."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
from tempfile import TemporaryDirectory

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "pet.json"
CELL_WIDTH, CELL_HEIGHT = 192, 208
COLS = 8
ROW_SPECS = (
    ("idle", 6, (1680, 660, 660, 840, 840, 1920)),
    ("running-right", 8, (120,) * 7 + (220,)),
    ("running-left", 8, (120,) * 7 + (220,)),
    ("waving", 4, (140,) * 3 + (280,)),
    ("hover", 5, (140,) * 4 + (280,)),
    ("failed", 8, (140,) * 7 + (240,)),
    ("waiting", 6, (150,) * 5 + (260,)),
    ("running", 6, (120,) * 5 + (220,)),
    ("review", 6, (150,) * 5 + (280,)),
    ("look-a", 8, (120,) * 8),
    ("look-b", 8, (120,) * 8),
)


def cell(atlas, row, column):
    x = column * CELL_WIDTH
    y = row * CELL_HEIGHT
    return atlas.crop((x, y, x + CELL_WIDTH, y + CELL_HEIGHT))


def load_pet():
    with MANIFEST.open(encoding="utf-8") as source:
        config = json.load(source)
    pet_id = config.get("id")
    if not isinstance(pet_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", pet_id):
        raise ValueError("pet.json needs a lowercase ASCII ID with only letters, digits and hyphens.")
    if not isinstance(config.get("displayName"), str) or not config["displayName"].strip():
        raise ValueError("pet.json needs a display name.")
    if config.get("spriteVersionNumber") != 2:
        raise ValueError("This package uses the v2 sprite format.")

    filename = config.get("spritesheetPath")
    if not isinstance(filename, str) or Path(filename).name != filename:
        raise ValueError("spritesheetPath must name a file next to pet.json.")
    spritesheet = ROOT / filename
    if spritesheet.stat().st_size > 20 * 1024 * 1024:
        raise ValueError("The sprite sheet is over 20 MiB.")
    with Image.open(spritesheet) as image:
        if image.format != "PNG" or image.is_animated:
            raise ValueError("The sprite sheet must be a static transparent PNG.")
        if image.size != (COLS * CELL_WIDTH, len(ROW_SPECS) * CELL_HEIGHT):
            raise ValueError("Expected a 1536 x 2288 sprite sheet.")
        atlas = image.convert("RGBA")

    for row, (name, count, _) in enumerate(ROW_SPECS):
        for column in range(COLS):
            alpha = cell(atlas, row, column).getchannel("A")
            low, high = alpha.getextrema()
            if column < count and (low != 0 or high == 0):
                raise ValueError(f"{name}, column {column + 1}: expected artwork on transparency.")
            if column >= count and high != 0:
                raise ValueError(f"{name}, column {column + 1}: unused cell must be transparent.")

    return config, spritesheet, atlas


def render_previews(atlas, output_dir):
    def render_frame(source):
        background = Image.new("RGBA", source.size, "#f5f6fa")
        background.alpha_composite(source)
        return background.convert("RGB")

    def save(name, poses, durations):
        frames = [render_frame(pose) for pose in poses]
        frames[0].save(
            output_dir / f"{name}.gif", save_all=True, append_images=frames[1:],
            duration=list(durations), loop=0
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    directions = []
    for row, (name, count, durations) in enumerate(ROW_SPECS):
        poses = [cell(atlas, row, column) for column in range(count)]
        if name.startswith("look-"):
            directions.extend(poses)
        else:
            save(name, poses, durations)
    save("look-around", directions, (120,) * len(directions))


def install(config, spritesheet, codex_home):
    pets = codex_home / "pets"
    destination = pets / config["id"]
    sources = (MANIFEST, spritesheet)
    if destination.exists():
        matches = all(
            (destination / source.name).is_file()
            and (destination / source.name).read_bytes() == source.read_bytes()
            for source in sources
        )
        if matches:
            return destination
        raise FileExistsError(f"Another local pet already uses {destination}.")

    pets.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=pets, prefix=".install-") as staging:
        package = Path(staging) / config["id"]
        package.mkdir()
        for source in sources:
            shutil.copyfile(source, package / source.name)
        package.rename(destination)
    return destination


def main():
    codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Check the manifest, v2 grid and transparency.")
    preview = commands.add_parser("preview", help="Render the nine motions and the gaze loop as GIFs.")
    preview.add_argument("--output", type=Path, default=ROOT / "preview-output")
    local_install = commands.add_parser("install", help="Copy the pet to a local Codex installation.")
    local_install.add_argument("--codex-home", type=Path, default=codex_home)
    args = parser.parse_args()
    try:
        config, spritesheet, atlas = load_pet()
        if args.command == "preview":
            render_previews(atlas, args.output)
            print(f"Previews written to {args.output.resolve()}")
        elif args.command == "install":
            destination = install(config, spritesheet, args.codex_home.expanduser())
            print(f"Pet installed at {destination.resolve()}")
        else:
            print("Validated v2 sprite sheet: 73 frames, 15 transparent cells.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
