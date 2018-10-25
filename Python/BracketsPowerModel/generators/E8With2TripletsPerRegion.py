__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

import numpy as np
import random
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

p_star = np.array([
    1.0,
    0.4231184017779921,
    0.7522862656332272,
    0.9491817654669973,
    0.721206790987267,
    1.0,
    0.7345229047483148,
    1.0
])

cdf_cache = {}


def build_cdf(data, bits, idx, add_noise=False, model=dict()):
    if idx not in cdf_cache:
        if bits.size == 1 and bits[0] < 60 and bits[0] % 15 < 8 and model.get('overrideR1Probs', False):
            cdf_cache[idx] = np.array([[0, 1 - p_star[bits[0] % 15]], [1, 1.0]])
        else:
            group = data[bits].groupby(bits.tolist()).size().reset_index(name='count')

            def agg(row):
                row['count'] = group.iloc[0:row.name + 1]['count'].sum()
                return row
            group = group.apply(agg, axis=1)
            try:
                group['count'] = group['count'] / (1. * group['count'].values[-1])
            except IndexError:
                import pdb; pdb.set_trace()
            cdf_cache[idx] = group.values.astype(float)
    # import pdb; pdb.set_trace()
    if not add_noise:
        return cdf_cache[idx]
    return addNoiseToCdf(cdf_cache[idx])


def getTriplet(s1, s2, s1Wins, s2Wins, matchPosition, roundNum):
    triplet = [0, 0, 0]
    if s1Wins:
        triplet[0] = 1
    if s2Wins:
        triplet[1] = 1


def generate(data, unpooled, pool_type, e8Seeds, model):
    fmt = model.get('format', DEFAULT_FORMAT)
    override_f4 = model.get('overrideF4', False)
    regions_a = regions if pool_type == UNPOOLED else [0, 0, 0, 0]
    add_noise = model.get('addNoise', DEFAULT_ADD_NOISE)

    vector = -np.ones(63, dtype=int)

    # fill in all bits fixed by f4Seeds
    offsets = [None, 0, 8, 12, 14]
    dummy = -1
    for region in range(4):
        regionOffset = region * 15
        seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
        for roundNum in range(1, 5):
            roundOffset = offsets[roundNum]
            numGames = int(len(seeds) / 2)
            newSeeds = []
            for gameNum in range(numGames):
                s1 = seeds[2 * gameNum]
                s2 = seeds[2 * gameNum + 1]
                matchPosition = regionOffset + roundOffset + gameNum

                if vector[matchPosition] != -1:
                    continue

                # Force any fixed F4 seeds to make it through
                s1Wins = ((roundNum < 4) and ((s1 == e8Seeds[2*region]) or (s1 == e8Seeds[2*region + 1])))
                s2Wins = ((roundNum < 4) and ((s2 == e8Seeds[2*region]) or (s2 == e8Seeds[2*region + 1])))

                if s1Wins:
                    vector[matchPosition] = 1 if fmt == 'TTT' else (1 if s1 < s2 else 0)
                    newSeeds.append(s1)
                elif s2Wins:
                    vector[matchPosition] = 0 if fmt == 'TTT' else (1 if s2 < s1 else 0)
                    newSeeds.append(s2)
                else:
                    newSeeds.append(dummy)
                    dummy -= 1
            seeds = newSeeds

    for region_idx, region in enumerate(regions_a):
        for idx, bit_group in enumerate(bit_groups):
            bits = bit_group + region * 15
            vector_bits = bit_group + region_idx * 15

            if np.all(vector[vector_bits] == -1):
                bits = bit_group + region * 15
                cdf = build_cdf(data, bits, idx + region * len(bit_groups), add_noise=add_noise, model=model)
                rn = np.random.rand()
                row = np.nonzero(cdf[:, len(bits)] - rn > 0)[0][0]
                values = cdf[row][:len(bits)]
                vector[bit_group + region_idx * 15] = values
            else:
                if vector_bits.size == 1:
                    continue
                key = hash(tuple(bits.tolist() + vector[vector_bits].tolist()))
                tmp_data = data
                others, vector_others = [], []
                for bit, vector_bit in zip(bits, vector_bits):
                    if vector[vector_bit] != -1:
                        if key not in cdf_cache:
                            tmp_data = tmp_data[tmp_data[bit] == vector[vector_bit]]
                    else:
                        others.append(bit)
                        vector_others.append(vector_bit)
                if tmp_data.size == 0:
                    tmp_data = data

                cdf = build_cdf(tmp_data, np.array(others), key, add_noise=add_noise, model=model)
                rn = np.random.rand()
                row = np.nonzero(cdf[:, -1] - rn > 0)[0][0]
                values = cdf[row][:-1]
                vector[vector_others] = values

    # import pdb; pdb.set_trace()
    f4Seeds = [-1, -1, -1, -1]
    if override_f4:
        triplet = np.array([60, 61, 62])
        cdf = build_cdf(unpooled, triplet, 'f4_triplet', add_noise=add_noise)
        rn = np.random.rand()
        row = np.nonzero(cdf[:, 3] - rn > 0)[0][0]
        values = cdf[row][:3]
        for i, bit_id in enumerate(triplet):
            vector[bit_id] = values[i]
    else:
        for region in range(4):
            regionOffset = region * 15
            seeds = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
            for roundNum in range(1, 5):
                roundOffset = offsets[roundNum]
                numGames = int(len(seeds) / 2)
                newSeeds = []
                for gameNum in range(numGames):
                    s1 = seeds[2 * gameNum]
                    s2 = seeds[2 * gameNum + 1]
                    matchPosition = regionOffset + roundOffset + gameNum
                    bit = vector[matchPosition]
                    if fmt == 'TTT':
                        if bit == 1:
                            newSeeds.append(s1)
                        else:
                            newSeeds.append(s2)
                    elif fmt == 'FFF':
                        if bit == 1:
                            newSeeds.append(min(s1, s2))
                        else:
                            newSeeds.append(max(s1, s2))
                seeds = newSeeds
            f4Seeds[region] = seeds[0]
    # assert np.count_nonzero(vector == -1) == 0
    return vector, f4Seeds


unpooled, pooled = None, None
data = None
last_state = (None, None, None) # fmt, year, is_pooled


def generateSingleBracket(max_year, e8Seeds, is_pooled=False, model=None):
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
            data = pooled.astype(int)
        else:
            data = unpooled.astype(int)
        last_state = new_state

    bracket, f4Seeds = generate(data, unpooled, pool_type, e8Seeds, model)
    return bracket.tolist(), f4Seeds
