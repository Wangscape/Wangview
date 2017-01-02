# Wangview
Parse Wangscape's output and generate random map from the tilesets

## Usage

You can find all needed Python modules in the `requirements.txt` file.

To install them (in a [virtual enviroment](https://virtualenv.pypa.io/en/stable/)),
just execute (assumming you've installed `virtualenv` before):

```shell
$ virtualenv -p python3 venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

After installation, you can generate a random map from [Wangscape](https://github.com/Wangscape/Wangscape)'s output
by executing:

```shell
python Wangview.py <PATH_TO_OUTPUT_DIRECTORY>
```

#### Example
```shell
python Wangview.py ../Wangscape/build/bin/example3/output/
```
