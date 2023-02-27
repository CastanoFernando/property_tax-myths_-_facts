import pandas as pd
import numpy as np
from linearmodels import PanelOLS
from linearmodels.panel.results import compare
import matplotlib.pyplot as plt


# ------------------------------------------------------- #
# Regresiones


#
results = {}

for tax in ['1110', '1210', '4100', '5111']:
    #
    df = pd.read_excel(
        'data/punto1/Data-Ley-Wagner.xlsx', 
        sheet_name = tax)
    #
    df = df[~df['COU'].isin(['LIE', 'LUX'])]
    df = df.set_index(['COU', 'Year'])
    #
    df['CONST'] = 1
    df['lnGDPpc'] = np.log(df['GDPpc'])
    df['lnTAXGDP'] = np.log(df['TAXGDP'])
    df['lnTAXPER'] = np.log(df['TAXPER'])
    df['TAXpc'] = df['TAXGDP'] * df['GDP'] / df['POB']
    df['lnTAXpc'] = np.log(df['TAXpc'])

    #
    results[tax] = {}
    
    #
    for q in ['TAXGDP', 'TAXPER', 'TAXpc']:

        #
        results[tax][q] = {}

        #
        for z in ['lin_lin', 'lin_log', 'log_log']:

            #
            results[tax][q][z] = {}

            if z == 'lin_lin':
                aux_df = df.dropna(subset=[f'{q}', 'GDPpc'])
                aux_df[f'{q}'] = aux_df[f'{q}'].replace([np.inf, -np.inf], np.nan)
                aux_df['GDPpc'] = aux_df['GDPpc'].replace([np.inf, -np.inf], np.nan)
                aux_df = aux_df.dropna(subset=[f'{q}', 'GDPpc'])
                
                y = aux_df[f'{q}']
                x = aux_df[['CONST', 'GDPpc']]

            elif z == 'lin_log':
                aux_df = df.dropna(subset=[f'{q}', 'lnGDPpc'])
                aux_df[f'{q}'] = aux_df[f'{q}'].replace([np.inf, -np.inf], np.nan)
                aux_df['lnGDPpc'] = aux_df['lnGDPpc'].replace([np.inf, -np.inf], np.nan)
                aux_df = aux_df.dropna(subset=[f'{q}', 'lnGDPpc'])
                
                y = aux_df[f'{q}']
                x = aux_df[['CONST', 'lnGDPpc']]
            
            else:
                aux_df = df.dropna(subset=[f'ln{q}', 'lnGDPpc'])
                aux_df[f'ln{q}'] = aux_df[f'ln{q}'].replace([np.inf, -np.inf], np.nan)
                aux_df['lnGDPpc'] = aux_df['lnGDPpc'].replace([np.inf, -np.inf], np.nan)
                aux_df = aux_df.dropna(subset=[f'ln{q}', 'lnGDPpc'])

                y = aux_df[f'ln{q}']
                x = aux_df[['CONST', 'lnGDPpc']]
            # End if
            
            
            #
            i = 1
            for bool_entity in [False, True]:
                for bool_time in [False, True]:
                    #
                    modelo = PanelOLS(
                        y, x,
                        entity_effects = bool_entity,
                        time_effects = bool_time)
                    # End PanelOLS

                    results[tax][q][z][f'{tax}_{q}_{i}'] = modelo.fit(cov_type='robust')
                    i +=1
                # End for
            # End for

            #
            with open(f'output/punto1/results_{tax}_{q}_{z}.txt', 'w') as f:
                f.write(
                    compare(results[tax][q][z],stars=True)
                    .summary.as_text())
            # End with
        # End for
    # End for
# End for

results['1110']['TAXGDP']['lin_lin']['1110_TAXGDP_1'].fitted_values
# ------------------ #
# Pooled data

for h in ['1110', '1210', '4100', '5111']:

    df = pd.read_excel(f'output/{h}.xlsx')

    aux_df = df
    
    #
    for k in range(0,3):
        if k == 0:
            tax = 'TAXGDP'
            x = 'GDPpc'
            z = 'linlin_P_fv'
        elif k == 1:
            tax = 'TAXGDP'
            x = 'lnGDPpc'
            z = 'linlog_P_fv'
        elif k == 2:
            tax = 'lnTAXGDP'
            x = 'lnGDPpc'
            z = 'loglog_P_fv'
        # End if

        fig, ax = plt.subplots()

        groups = aux_df.groupby('Region')

        for name, group in groups:
            #
            ax.plot(
                group[x], 
                group[tax], 
                marker='o', 
                linestyle='',
                label=f'{name}')
        # End for

        ax.plot(
            aux_df[x], 
            aux_df[z], 
            marker='',
            label='Fitted value')
        
        plt.legend()
        plt.suptitle(f'{h}')
        plt.xlabel(f'{x}')
        plt.ylabel(f'{tax}')
        plt.style.use('tableau-colorblind10')
        plt.savefig(f'{h}_{tax}_{x}.png')
    # End for
# End for
