'''

'''

# ------------------------------------------------------- #
# Summary

'''

'''

# ------------------------------------------------------- #
# import utilities


import os
import pandas as pd
import numpy as np
from linearmodels import PanelOLS
from linearmodels.panel.results import compare

# ------------------------------------------------------- #
# proccess

#
df = pd.read_parquet('data/punto7/bra_13_20.pqt')
#
df['CONST'] = 1
df['lnPROPTAXpc'] = np.log(df['PROPTAXpc'])
df['lnTRF_CTEpc'] = np.log(df['TRF_CTEpc'])
df['lnTRF_CTEpc'] = np.log(df['TRF_CTEpc'])
df['lnINGCTE_STRFpc'] = np.log(df['INGCTE_STRFpc'])

#
results = {}
results['lin_lin'] = {}
results['lin_log'] = {}
results['log_log'] = {}

#
for z in list(results.keys()):

    if z == 'lin_lin':
        print('check1')
        aux_df = df.dropna(subset=['PROPTAXpc', 'TRF_CTEpc'])
        y = aux_df['PROPTAXpc']
        x = aux_df[['CONST', 'TRF_CTEpc']]
    elif z == 'lin_log':
        print('check2')
        aux_df = df.dropna(subset=['PROPTAXpc', 'lnTRF_CTEpc'])
        y = aux_df['PROPTAXpc']
        x = aux_df[['CONST', 'lnTRF_CTEpc']]
    else:
        print('check3')
        aux_df = df.dropna(subset=['lnPROPTAXpc', 'lnTRF_CTEpc'])
        y = aux_df['lnPROPTAXpc']
        x = aux_df[['CONST', 'lnTRF_CTEpc']]
    # End def

    #
    for bool_entity in [False, True]:
        for bool_time in [False, True]:
            #
            modelo = PanelOLS(
                y, x,
                entity_effects = bool_entity,
                time_effects = bool_time)
            # End PanelOLS

            results[z][f'{bool_entity}_{bool_time}'] = modelo.fit(cov_type='robust')
        # End for
    # End for

    #
    with open(f'output/punto7/results_{z}.txt', 'w') as f:
        f.write(
            compare(results[z],stars=True)
            .summary.as_text())
    # End with

df = df.reset_index()
df = df.set_index(['ESTADO', 'YEAR'])

#
results = {}
results['lin_lin'] = {}
results['lin_log'] = {}
results['log_log'] = {}

#
for z in list(results.keys()):

    if z == 'lin_lin':
        print('check1')
        aux_df = df.dropna(subset=['PROPTAXpc', 'TRF_CTEpc'])
        y = aux_df['PROPTAXpc']
        x = aux_df[['CONST', 'TRF_CTEpc']]
    elif z == 'lin_log':
        print('check2')
        aux_df = df.dropna(subset=['PROPTAXpc', 'lnTRF_CTEpc'])
        y = aux_df['PROPTAXpc']
        x = aux_df[['CONST', 'lnTRF_CTEpc']]
    else:
        print('check3')
        aux_df = df.dropna(subset=['lnPROPTAXpc', 'lnTRF_CTEpc'])
        y = aux_df['lnPROPTAXpc']
        x = aux_df[['CONST', 'lnTRF_CTEpc']]
    # End def

    #
    for bool_entity in [False, True]:
        for bool_time in [False, True]:
            #
            modelo = PanelOLS(
                y, x,
                entity_effects = bool_entity,
                time_effects = bool_time)
            # End PanelOLS

            results[z][f'{bool_entity}_{bool_time}'] = modelo.fit(cov_type='kernel')
        # End for
    # End for

    #
    with open(f'output/punto7/results2_{z}.txt', 'w') as f:
        f.write(
            compare(results[z],stars=True)
            .summary.as_text())
    # End with