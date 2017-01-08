
# coding: utf-8

# Use this notebook to run Wangview while developing with IPython.
# 
# The `autoreload` extension will allow you to test changes to the code without restarting the kernel.

# In[ ]:

get_ipython().magic('load_ext autoreload')


# In[ ]:

get_ipython().magic('autoreload 2')


# In[ ]:

from Wangview.Display import Display


# In[ ]:

w = Display('../Wangscape/Wangscape/example3/output')
w.run()

