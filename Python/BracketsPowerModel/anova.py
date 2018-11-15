__author__ = "Nestor Bermudez"
__license__ = "MIT"
__version__ = "1.0.0"
__email__ = "nab6@illinois.edu"
__status__ = "Development"


import numpy as np
from scipy.stats import f_oneway, kruskal


root = '/Users/nbermudezs/Library/Mobile Documents/com~apple~Numbers/Documents/bt-fixed'
file_1 = 'preparedForMCB-Nov15-{}-bt_baseline.csv'
file_2 = 'preparedForMCB-Nov15-{}-power.csv'


def get_data(file):
    with open(file) as f:
        year_data = []
        for line in f:
            if line.replace(',', '').strip() == '':
                yield np.array(year_data)[:, [0, 2, 4, 6, 8]].astype(float)
                year_data = []
            elif 'Tournament' in line or 'Batch' in line:
                continue
            else:
                values = line.replace('\n', '').split(',')[1:]
                year_data.append(values)


def model_anova(bt_i, power_i):
    cols = bt_i.shape[1]
    return [f_oneway(bt_i[:, j], power_i[:, j])[1].round(3) for j in range(cols)]


if __name__ == '__main__':
    import sys
    metric = sys.argv[1] if len(sys.argv) > 1 else 'score'
    start = 2013
    bt = get_data('{}/{}'.format(root, file_1.format(metric)))
    power = get_data('{}/{}'.format(root, file_2.format(metric)))

    print('ANOVA over {} metric'.format(metric))

    p_values = np.array([model_anova(bt_i, power_i) for bt_i, power_i in zip(bt, power)])
    reject_h_0 = p_values < 0.05
    print('p-values')
    print(p_values)
    print('-' * 80)
    print('Rejections')
    print(reject_h_0)
    print('-' * 80)
    print('=' * 80)