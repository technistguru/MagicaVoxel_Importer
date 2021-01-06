# MagicaVoxel_Importer

Blender addon for importing [MagicaVoxel](https://ephtracy.github.io/) `VOX` files.

### Installation

[Blender documentation for installing addons.](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html#rd-party-add-ons)

Only [`MagicaVoxel_Importer.py`](MagicaVoxel_Importer.py) is needed. Go to `Edit > Preferences > Add-ons`, click on `Install`, and select `MagicaVoxel_Importer.py`.

### Usage

Go to `File > Import > MagicaVoxel (.vox)` and select the file you want to import.

### Import Options

- `Voxel Size`: The side length, in blender units, of each voxel.
- `Palette Import Method`: Specifies how palette will be imported.
    - `None`: Don't import palette.
    - `Separate Materials`: Create a material for each palette color.
    - `Vertex Colors`: Create one material and store color and material data in vertex colors.
    - `Textures`: Generates textures to store color and material data.
- `Gamma Correct Colors`: In order to make the Blender models look similar to how they look in MagicaVoxel, the colors have to be gamma corrected. Only applies if `Palette Import Method` is `Separate Materials`.
- `Gamma Correction Value`: The power that color values are raised to for gamma correction.
- `Override Existing Materials`: Specifies whether material properties should be overriden if materials have already been generated for this file before. Disable if you are reimporting a model whose materials you have modified in blender.