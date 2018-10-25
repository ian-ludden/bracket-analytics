__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

import numpy as np

regions = [0, 1, 2, 3]

rounds = [
    np.arange(0, 8),
    np.arange(8, 12),
    np.arange(12, 14),
    np.arange(14, 15)
]

triplets = [
    np.array([0, 1, 8]),
    np.array([2, 3, 9]),
    np.array([4, 5, 10]),
    np.array([6, 7, 11]),
    np.array([12, 13, 14])
]

UNPOOLED = 0
POOLED = 1
NOISE_STD = 0.01
DEFAULT_FORMAT = 'TTT'
DEFAULT_ADD_NOISE = False

# using strings to match the reading type from pandas
years = ['2013', '2014', '2015', '2016', '2017', '2018']

formats = ['TTT', 'FFF', 'TTF', 'TFT', 'TFF', 'FTT', 'FTF', 'FFT']
