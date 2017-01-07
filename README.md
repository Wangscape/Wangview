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
## Contributing

The repository structure may change in the future, but for now the Python scripts and IPython notebooks should be kept in sync.
Pull requests should make synchronous changes to both scripts and notebooks.

If you prefer to work on notebooks, they can be converted to scripts using using [nbconvert](https://nbconvert.readthedocs.io).
This can be done automatically using save hooks ([1](http://jupyter-notebook.readthedocs.io/en/latest/extending/savehooks.html), [2](http://stackoverflow.com/questions/29329667/ipython-notebook-script-deprecated-how-to-replace-with-post-save-hook)), or (deprecated) running IPython/Jupyter with the `--script` flag.

If you prefer to work on the scripts, the edited scripts can be converted back to notebooks using a tool like [PY2NB](https://github.com/sklam/py2nb).
