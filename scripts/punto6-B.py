import pandas as pd
import numpy as np
from linearmodels import PanelOLS
from scipy.stats import iqr
import os

def q25(x):
    return x.quantile(0.25)
# End def

def q75(x):
    return x.quantile(0.75)
# End def


# ------------------------------------------------------- #
# Preparar los datos de tax revenue
# 

# Importar datos de tax rev
revenue = pd.read_parquet(f'data/oecd_tax_rev_stats.pqt')

#
cou_list = []

for cou in revenue['COU'].unique():
    for i in range(1989, 2023):
        cou_list.append((str(cou), i))
# End for

#
df = (pd
    .DataFrame(cou_list, columns=['COU', 'Year'])
    .convert_dtypes())

# Quedarse con los datos de Property Tax
condition   = (revenue['TAX'] == '4000')
# Quedarse con los datos de immovable tax
condition  |= (revenue['TAX'] =='4100')
# Quedarse con los datos de Total tax revenue
condition  |= (revenue['TAX'] == 'TOTALTAX')
# Quedarse con los datos del sector publico total
condition  &= (revenue['GOV'] == 'NES')
# Quedarse con los datos valuados en dolares
condition  &= (revenue['VAR'] == 'TAXUSD')

# Ejecutar el filtro
revenue = revenue[condition]

# Reshape de los datos
revenue = pd.pivot(
    revenue, 
    index = ['COU', 'Country', 'Year'],
    columns = 'Tax revenue',
    values = 'Value').reset_index()


# Variables de tax revenue
cols = [
    '4000 Taxes on property', 
    '4100 Recurrent taxes on immovable property'
]
# Modificar las vbles como % de total tax rev
for col in cols:
    revenue[col] = revenue[col] / revenue['Total tax revenue']
# End for


# Eliminar la variable de Total tax rev
revenue = revenue.drop(columns='Total tax revenue')

#
revenue.sort_values(['COU', 'Year'], inplace=True)


# Crear pct_change
for col in cols:
    revenue = revenue.rename(columns={col: col.split(' ')[0]})
# End for

#
revenue.COU = revenue.COU.astype(str)
revenue.Year = revenue.Year.astype(int)

df = pd.merge(df, revenue, how = 'left', on=['COU', 'Year'])


# ------------------------------------------------------- #
# Preparar los datos de inflacion

#
deflactor = pd.read_csv(
    'data/WB - GDPdef.csv',
    skiprows=3)

#
deflactor = deflactor.rename(columns={
    'Country Code': 'COU',
    'Country Name': 'Country'
    })

#
deflactor = pd.melt(
    deflactor,
    id_vars= ['COU', 'Country'],
    value_vars= [str(x) for x in range(1989,2022)],
    var_name= 'Year',
    value_name= 'deflactor')

#
deflactor.COU = deflactor.COU.astype(str)
deflactor.Year = deflactor.Year.astype(int)


df = pd.merge(
    df, 
    deflactor[['COU', 'Year', 'deflactor']], 
    how='left', on=['COU', 'Year'])


# ------------------------------------------------------- #
# Armar las bases para correr las regresiones

for col in ['4000', '4100', 'deflactor']:
    df[f'{col}_pctchg'] = df[col].pct_change(fill_method=None)
# End for

#
df['const'] = 1


# ------------------------------------------------------- #
# Regresiones

resultado = {}

# df_aux =df_aux[np.isfinite(df_aux['4000_pctchg'])]
# Subset ligero:
for col in ['4000', '4100', '4000_pctchg', '4100_pctchg']:
    
    #
    df_aux = df.copy()
    df_aux[col] = df_aux[col].replace(np.inf, np.NaN)
    df_aux = df_aux.dropna(subset=[col, 'deflactor_pctchg'])

    #
    condition = (
        ~df_aux.COU.isin(
            df_aux[df_aux[col] == 0 ]['COU'].unique()
        )
    )

    #
    df_aux = df_aux[condition]

    asd = df_aux.groupby('COU')['deflactor_pctchg'].agg([iqr, q25, q75])
    
    #
    asd = asd[asd['iqr'] >= .001]
    #
    asd.loc[:, 'lbound'] = asd['q25'] - 1.5*asd['iqr']
    asd.loc[:, 'ubound'] = asd['q75'] + 1.5*asd['iqr']

    df_aux = pd.merge(
        df_aux, 
        asd[['lbound', 'ubound']], 'left', 'COU')

    #
    df_aux = df_aux[(
        (df_aux['deflactor_pctchg'] < df_aux['ubound'])
        &
        (df_aux['deflactor_pctchg'] > df_aux['lbound'])
        )]

    df_aux.to_excel(f'{col}-gdpdef.xlsx')

    #
    df_aux = df_aux.set_index(['COU', 'Year'], drop=True)

    #
    modelo = PanelOLS(
        df_aux[col],
        df_aux[['const', 'deflactor_pctchg']],
        entity_effects=True,
        time_effects=True)

    #
    resultado[f'{col}_A'] = modelo.fit()


    #  
    pais_lista = ['COD' ,'TUR' ,'GHA' ,'MWI' ,'NGA' ,'CRI' ,'EGY' ,'MDG' ,'PAK' ,'KEN' ,'JAM' ,'URY' ,'MNG' ,'SLE' ,'BWA' ,'HND' ,'KAZ' ,'SLB' ,'RWA' ,'SWZ' ,'PRY' ,'LAO' ,'BRA' ,'KGZ' ,'BTN' ,'IDN' ,'GTM' ,'COL' ,'BGD' ,'LSO', 'NIC', 'BGR', 'DOM', 'ZAF', 'UGA', 'GEO', 'HUN', 'PNG', 'NAM', 'TTO', 'MEX']

    #
    condition = (
        df_aux.index.get_level_values('COU').isin(pais_lista)
    )

    #
    df_aux = df_aux[condition]

    #
    modelo = PanelOLS(
        df_aux[col],
        df_aux[['const', 'deflactor_pctchg']],
        entity_effects=True,
        time_effects=True)

    resultado[f'{col}_B'] = modelo.fit()
# End for



# ------------------------------------------------------- #
# Armar la tabla

#    
vbles = ['const', 'deflactor_pctchg']
table = pd.DataFrame([], index=['const', 'deflactor_pctchg', 'n'])

for key in resultado:
    
    #
    pvalues = list(resultado[key].pvalues)
    # 
    params = list(resultado[key].params)

    #
    for i in [0, 1]:
        val = np.round(params[i],5)
        if(pvalues[i] > .10):
            table.loc[vbles[i], key] = f'{val}'
        elif((pvalues[i] <= .1) & (pvalues[i] > .05)):
            table.loc[vbles[i], key] = f'{val} *'
        elif((pvalues[i] <= .05) & (pvalues[i] > .01)):
            table.loc[vbles[i], key] = f'{val} **'
        else:
            table.loc[vbles[i], key] = f'{val} ***'
        # End if
    # End for

    table.loc['n', key] = resultado[key].nobs
# End for

table.to_excel('table6.xlsx')