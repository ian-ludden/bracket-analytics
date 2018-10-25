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


bit_groups = [
    np.array([8, 9, 12]),
    np.array([10, 11, 13]),
    np.array([0]),
    np.array([1]),
    np.array([2]),
    np.array([3]),
    np.array([4]),
    np.array([5]),
    np.array([6]),
    np.array([7]),
    np.array([14])
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
    vector = -np.ones(63, dtype=int)
    add_noise = model.get('addNoise', DEFAULT_ADD_NOISE)

    # fill up the 4 regions
    for region_idx, region in enumerate(regions_a):
        for idx, bit_group in enumerate(bit_groups):
            bits = bit_group + region * 15
            cdf = build_cdf(data, bits, idx + region * len(bit_groups), add_noise=add_noise)
            rn = np.random.rand()
            row = np.nonzero(cdf[:, len(bits)] - rn > 0)[0][0]
            values = cdf[row][:len(bits)]
            vector[bit_group + region_idx * 15] = values

    # fill up the last 2 rounds
    last_3 = np.array([60, 61, 62])[:, np.newaxis]
    for bit in last_3:
        cdf = build_cdf(unpooled, bit, len(bit_groups) * 4, add_noise=add_noise)
        rn = np.random.rand()
        row = np.nonzero(cdf[:,1] - rn > 0)[0][0]
        values = cdf[row][:1]
        for i, bit_id in enumerate(bit):
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
        unpooled, pooled = read_data(fmt, max_year)
        if is_pooled:
            pool_type = POOLED
            data = pooled
        else:
            pool_type = UNPOOLED
            data = unpooled
        last_state = new_state

    return generate(data, unpooled, pool_type, model).tolist()
