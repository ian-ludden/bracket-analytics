__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

import numpy as np
import sys; sys.path.append("..")

from samplingUtils import addNoiseToCdf
from triplets.Constant import UNPOOLED, POOLED, regions, DEFAULT_FORMAT, DEFAULT_ADD_NOISE
from triplets.priors.PriorDistributions import read_data
from time import time

triplets = [
    np.array([0, 1, 8]),
    np.array([2, 3, 9]),
    np.array([4, 5, 10]),
    np.array([6, 7, 11]),
    np.array([12, 13, 14])
]

cdf_cache = {}


def build_cdf(data, bits, idx, add_noise=False):
    if idx not in cdf_cache:
        group = data[bits].groupby(bits.tolist()).size().reset_index(name='count')

        def agg(row):
            row['count'] = group.iloc[0:row.name + 1]['count'].sum()
            return row
        group = group.apply(agg, axis=1)
        group['count'] = group['count'] / (1. * group['count'].values[-1])
        cdf_cache[idx] = group.values.astype(float)
    if not add_noise:
        return cdf_cache[idx]
    return addNoiseToCdf(cdf_cache[idx])


def generate(data, unpooled, pool_type, model):
    regions_a = regions if pool_type == UNPOOLED else [0, 0, 0, 0]
    add_noise = model.get('addNoise', DEFAULT_ADD_NOISE)

    vector = -np.ones(63, dtype=int)
    for region_id, region in enumerate(regions_a):
        for idx, triplet in enumerate(triplets):
            bits = triplet + region * 15
            cdf = build_cdf(data, bits, idx + region * 5, add_noise=add_noise)
            rn = np.random.rand()
            row = np.nonzero(cdf[:, 3] - rn > 0)[0][0]
            values = cdf[row][:3]
            vector[triplet + region_id * 15] = values

    triplet = np.array([60, 61, 62])
    cdf = build_cdf(unpooled, triplet, 21, add_noise=add_noise)
    rn = np.random.rand()
    row = np.nonzero(cdf[:,3] - rn > 0)[0][0]
    values = cdf[row][:3]
    for i, bit_id in enumerate(triplet):
        vector[bit_id] = values[i]

    return vector


unpooled, pooled = None, None
data = None
last_state = (None, None, None) # fmt, year, is_pooled


def generateSingleBracket(max_year, is_pooled=False, model=None):
    global unpooled
    global pooled
    global data
    global last_state
    fmt = model.get('format', DEFAULT_FORMAT)

    pool_type = POOLED if is_pooled else UNPOOLED
    new_state = (fmt, max_year, is_pooled)
    if data is None or new_state != last_state:
        cdf_cache.clear()
        unpooled, pooled = read_data(fmt, max_year)
        if is_pooled:
            data = pooled
        else:
            data = unpooled
        last_state = new_state

    return generate(data, unpooled, pool_type, model).tolist()
