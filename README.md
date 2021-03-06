# Larkstongue v.0.0.1-alpha

Larkstongue is an asset packer for the [PICO-8](https://www.lexaloffle.com/pico-8.php) fantasy console, written in Python. It compresses your assets, writes them to cart data, and generates the Lua code for unpacking that data. To use it, install Python 3, copy the “larkstongue” directory to your PICO-8 cart directory or wherever you wish to run it from, and the “include” directory to your PICO-8 cart directory.

Larkstongue currently supports the following compression methods:

- Hilbert curve mapping (only used on bitmaps, doesn’t compress by itself but often improves RLE results, generally more effective on larger images)
- RLE (mostly effective on bitmaps but occasionally useful with other data)
- Huffman coding

Note that Larkstongue is provided as is, and is currently in ***early public alpha***. Remember to keep backups of any carts you use it on!

Larkstongue has two subcommands, “pack” and “extract”. Pack compresses your assets and writes them on a .p8 cart, while extract grabs raw data from a .p8 cart and saves it into a plaintext asset file.

## pack

```
usage: larkstongue pack [-h] [--no-hilbert] [--no-rle] [--no-huffman] [--spare-music] [--gfx-only] input output
```

“Output” is the .p8 cart you wish to write to. “Input” is a plaintext file of assets in the format generated by extract. Assets come in two formats - bitmap and generic. Each asset must have a unique name. The definition of a bitmap asset looks like this:

```
name=face
bitmap=77777777
bitmap=70000007
bitmap=70700707
bitmap=70000007
bitmap=70700707
bitmap=70777707
bitmap=70000007
bitmap=77777777
-
```

The width of a bitmap must be an even number. A hyphen is required after each asset. A generic asset may be any string of hexadecimal digits, and it looks like this:

```
name=object
data=7ef9843368ce7ef99bcc68ce7ef99bcc
-
```

The string may be any length, but it is strongly suggested to pad your data to an even amount of digits, as the Huffman encoder expects 8 bit values and will fail if it receives an odd amount of nibbles.

Larkstongue tests several different configurations of compression methods with each asset, then uses the best configuration to compress that asset. It then generates a loader (which will be called something like mycart_larkstongue.p8l) and adds includes for every decompressor used to your original cart. All of these require tokens, and their efficiency may vary based on your data, so if any one of them produces only marginal results, or you simply wish to save tokens, you may disable them with --no-hilbert, --no-rle or --no-huffman. Larkstongue will notify you if a method only results in a 2% improvement and suggest that you consider disabling it.

Unpacked assets are stored as tables of strings. If an asset is a bitmap image, each line will be a separate string in the table. To load them into RAM, you can use str_to_mem(), like this:

```
str_to_mem(0x3100, soundtrack)
```

where 0x3100 is the memory address to write to (in this case, the start of the music area) and soundtrack is the table containing your unpacked soundtrack. If there are several lines in the table, a stride of 64 bytes (ie. one scanline) will be used. Here are some useful memory addresses:

- 0x0 - the sprite sheet
- 0x3100 - the music area
- 0x4300 - 6912 bytes general use RAM (you may use this for any purpose you like, such as storing 128 * 108 pixels of graphics)
- 0x6000 - the screen

Each byte of sprite sheet or screen RAM stores two pixels, so if you wish to write at specific screen coordinates, add an offset of y * 64 + x / 2.

Larkstongue will then overwrite as many data areas as it needs to store the compressed data, starting with the sprite sheet. Any data left over will be written as a string in the Lua code (however, note that compressed strings in the Lua code may increase the compressed size of your cart drastically). If you want to protect certain areas from overwriting, you may use --spare-music to protect the music and sound effect areas, or --gfx-only to restrict Larkstongue to using the sprite sheet only.

If you wish, you may use --progressbar to display a progress bar during unpacking (this will take 21 tokens). Otherwise, a black screen will be displayed.

## extract

```
usage: larkstongue extract [-h] [--bgcolor BGCOLOR]
                           {bitmap,soundtrack,all,gfx,gff,map,sfx,music} input output assetname
```

“Input” is the .p8 cart you wish to extract data from, and “output” is a text file containing assets. If that file does not exist, Larkstongue will create it.

There are eight different source settings:

- bitmap: Extracts an image from the sprite sheet. Automatically crops out background color (0 by default, use --bgcolor to define another color). The width of the resulting image will be padded to an even amount of pixels.
- soundtrack: Extracts the music and sound effect data areas and combines them into one asset.
- gfx, gff, map, sfx or music: Extract the sprite sheet, sprite flag, map, sound effect, or music area, respectively.
- all: Dump everything into one enormous asset.

Assetname is a unique name you wish to give your asset. If an asset by that name already exists, Larkstongue will prompt you before overwriting it.