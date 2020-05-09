import argparse

from pack import doPack
from extract import doExtract

parser = argparse.ArgumentParser()
subParsers = parser.add_subparsers(title="subcommands")

parserPack = subParsers.add_parser(
    "pack", 
    help = "compress and pack data into a .p8 cart", 
    description = "Reads assets from a text file, compresses them, and writes them to the cart data of the target .p8 cart, along with the code required to unpack those assets."
    )

parserPack.add_argument("--no-hilbert", action = "store_true", help = "disable rectangle subdivision and Hilbert mapping")
parserPack.add_argument("--no-rle", action = "store_true", help = "disable RLE compression")
parserPack.add_argument("--no-huffman", action = "store_true", help = "disable Huffman coding")
parserPack.add_argument("--spare-music", action = "store_true", help = "do not write into the music and sfx areas")
parserPack.add_argument("--gfx-only", action = "store_true", help = "do not write anywhere but the gfx area")
parserPack.add_argument("--progressbar", action = "store_true", help = "add a progress bar to the loader (21 tokens)")
parserPack.add_argument("input", help = "the text file to read assets from")
parserPack.add_argument("output", help = "the .p8 cart to write the data to")
parserPack.set_defaults(func = doPack)

parserExtract = subParsers.add_parser(
    "extract", 
    help = "extract data from a .p8 cart", 
    description = "Reads data from a .p8 cart and outputs it into a text file that can be read by the packer. Choose the cart data area to extract, \"soundtrack\" if you wish to combine the music and sfx areas into one asset, \"all\" if you wish to dump all cart data into one big asset, or \"bitmap\" if you wish to extract an image from the sprite sheet. Background color (black by default) will be cropped out and the width will be padded to an even amount of pixels."
    )
    
parserExtract.add_argument("source", choices = ["bitmap", "soundtrack", "all", "gfx", "gff", "map", "sfx", "music"], help = "the cart data area to extract")
parserExtract.add_argument("input", help = "the .p8 file to extract from")
parserExtract.add_argument("output", help = "the text file to output to")
parserExtract.add_argument("assetname", help = "a name for the asset")
parserExtract.add_argument("--bgcolor", help = "define background color for bitmap, default is 0", default = "0")
parserExtract.set_defaults(func = doExtract)

args = parser.parse_args()

if hasattr(args, 'func'):
    args.func(args)
else:
    parser.print_help()