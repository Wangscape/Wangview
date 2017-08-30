
# coding: utf-8
# Use this notebook to run Wangview while developing with IPython.
# 
# The `autoreload` extension will allow you to test changes to the code without restarting the kernel.
get_ipython().magic('load_ext autoreload')

get_ipython().magic('autoreload 2')

from Wangview.Display import Display

w = Display('../Wangscape/doc/examples/example3/output')
w.run()
