# Numberplater 🦊

**Generate UK Custom Number Plates**

Numberplater is a Python script for generating valid UK number plates based on specified words.

## Usage

1. Ensure Python is installed.
2. Open a command-line interface.
3. Navigate to the project directory.
4. Run `numberplater.py` with your chosen word as an argument.

```console
$ python numberplater.py [number plate options] <word>
```

The script will generate possible UK number plates based on your input.

### Example
```console
$ python numberplater.py cheetah
['ch33tah', 'che374h', 'che378h']

$ python numberplater.py --current cheetah
['ch33tah']
```

### Options

You can specify different types of UK number plates using the following options:

- `-d/--dateless`: Generate a dateless number plate.
- `-n/--northern-irish`: Generate a Northern Irish number plate.
- `-s/--suffix`: Generate a suffix number plate.
- `-p/--prefix`: Generate a prefix number plate.
- `-c/--current`: Generate a current number plate.
- `-a/--all`: Check across all formats (default).

For additional information on UK number plate formats, you can refer to [Platemaster](https://www.platemaster.com/uk-number-plate-formats.htm), a helpful resource to understand the different formats and rules for UK number plates.
