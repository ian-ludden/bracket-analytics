__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"

import numpy as np
import random
import sys; sys.path.append("..")

from samplingUtils import toDistribution, cdfToPdf, addNoiseToCdf
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
        try:
            group['count'] = group['count'] / (1. * group['count'].values[-1])
        except IndexError:
            import pdb; pdb.set_trace()
        cdf_cache[idx] = group.values.astype(float)
        # print('==== TRUE PDF ====')
        # print(cdfToPdf(cdf_cache[idx][:, -1]))
    if not add_noise:
        return cdf_cache[idx]

    return addNoiseToCdf(cdf_cache[idx])



def getP(s1, s2, matchPosition, roundNum):
    # import pdb; pdb.set_trace()
    return 0

def getTriplet(s1, s2, s1Wins, s2Wins, matchPosition, roundNum):
    triplet = [0, 0, 0]
    if s1Wins:
        triplet[0] = 1
    if s2Wins:
        triplet[1] = 1

def generate(data, unpooled, pool_type, f4Seeds, champRegion, ruRegion, model):
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
                s1Wins = s1 == f4Seeds[region]
                s2Wins = s2 == f4Seeds[region]

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

    for region_id, region in enumerate(regions_a):
        for idx, triplet in enumerate(triplets):
            bits = triplet + region * 15
            vector_bits = triplet + region_id * 15

            if np.all(vector[vector_bits] == -1):
                cdf = build_cdf(data, bits, idx + region * 5, add_noise=add_noise)

                # not fixed bits on the triplet
                rn = np.random.rand()
                row = np.nonzero(cdf[:, 3] - rn > 0)[0][0]
                values = cdf[row][:3]
                vector[vector_bits] = values
            else:
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
                if len(others) == 0:
                    # all bits are already filled (possible with Rev_4)
                    continue

                cdf = build_cdf(tmp_data, np.array(others), key, add_noise=add_noise)
                rn = np.random.rand()
                try:
                    row = np.nonzero(cdf[:, -1] - rn > 0)[0][0]
                except Exception as err:
                    import pdb; pdb.set_trace()
                values = cdf[row][:-1]
                vector[vector_others] = values
                # either use conditional p or independent

    if override_f4:
        triplet = np.array([60, 61, 62])
        cdf = build_cdf(unpooled, triplet, 21, add_noise=add_noise)
        rn = np.random.rand()
        row = np.nonzero(cdf[:, 3] - rn > 0)[0][0]
        values = cdf[row][:3]
        for i, bit_id in enumerate(triplet):
            vector[bit_id] = values[i]
    return vector


unpooled, pooled = None, None
data = None
last_state = (None, None, None) # fmt, year, is_pooled


def generateSingleBracket(max_year, f4Seeds, champRegion, ruRegion, is_pooled=False, model=None):
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

    return generate(data, unpooled, pool_type, f4Seeds, champRegion, ruRegion, model).tolist()


if __name__ == '__main__':
    unpooled, pooled = read_data('TTT', 2017)
    data = pooled

    ref_cdf = build_cdf(data, bits=np.array([8, 9, 12]), idx='dummy', add_noise=False)

    print('==== TRUE CDF ====')
    print(ref_cdf)
    cdfs = []
    for i in range(100000):
        cdf = build_cdf(data, bits=np.array([8, 9, 12]), idx='dummy', add_noise=True)
        cdf = cdf[:, -1]
        valid = np.all([(cdf[i] <= cdf[i+1]) for i in range(len(cdf) - 1)])
        if not valid:
            import pdb; pdb.set_trace()
            continue
        cdfs.append(cdf)
    print('==== AVG CDF ====')
    print(np.mean(cdfs, axis=0).round(6))
    print('==== AVG PDF FROM CDF ====')
    print(cdfToPdf(np.mean(cdfs, axis=0)))