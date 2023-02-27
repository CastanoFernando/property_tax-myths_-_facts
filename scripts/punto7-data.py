'''

'''

# ------------------------------------------------------- #
# Summary

'''

'''

# ------------------------------------------------------- #
# import utilities

import pandas as pd
import os
from unrar import rarfile

# ------------------------------------------------------- #
# proccess - Brasil

bra_rar = rarfile.RarFile(
    'data/punto7/BRASIL - 2010to2020 - L GOV - AIF.rar')



# ----------------------------------- #
# Cargar raw data en un dataframe

#
df = pd.DataFrame([])
#
for year in range(2013, 2021):
    
    #
    file_name = f'BRASIL - {year} - L GOV - AIF - FINBRA.csv'
    bra_rar.extract(file_name, 'data/punto7')
    
    #
    aux_df = pd.read_csv(
        f'data/punto7/{file_name}', 
        skiprows = 3,
        encoding = "latin",
        sep = ";")
    # End read csv

    #
    os.remove(f'data/punto7/{file_name}')


    #
    if year == 2013:
        condition  = (aux_df['Conta'].str.startswith('1.1.1.2.02'))
        condition |= (aux_df['Conta'].str.startswith('1.7.0.0.00'))
        condition |= (aux_df['Conta'].str.startswith('1.0.0.0.00'))
        condition &= (aux_df['Coluna'] == 'Receitas Realizadas') 

    elif (year >= 2014) & (year <= 2017):
        condition  = (aux_df['Conta'].str.startswith('1.1.1.2.02'))
        condition |= (aux_df['Conta'].str.startswith('1.7.0.0.00'))
        condition |= (aux_df['Conta'].str.startswith('1.0.0.0.00'))
        condition &= (aux_df['Coluna'] == 'Receitas Brutas Realizadas') 
    
    else:
        condition  = (aux_df['Conta'].str.contains('1.1.1.8.01.1.0'))
        condition |= (aux_df['Conta'].str.contains('1.7.0.0.00.0.0'))
        #condition |= (aux_df['Conta'].str.contains('1.7.1.0.00.0.0'))
        #condition |= (aux_df['Conta'].str.contains('1.7.2.0.00.0.0'))
        condition |= (aux_df['Conta'].str.contains('1.0.0.0.00.0.0'))
        condition &= (aux_df['Coluna'] == 'Receitas Brutas Realizadas') 
    # End if
    
    aux_df = aux_df[condition]


    #
    aux_df = pd.pivot(
        aux_df, 
        index = ['Instituição', 'UF', 'População'],
        columns = 'Conta',
        values = 'Valor')
    # End pivot
    aux_df = aux_df.reset_index()


    #
    aux_df.columns = [
        'MUNICIPIO', 
        'ESTADO', 
        'POB', 
        'ING_CTE', 
        'PROPTAX', 
        'TRF_CTE'
    ]

    #
    aux_df['YEAR'] = year

    # 
    df = pd.concat([df, aux_df])
    aux_df = None
# End for


# ----------------------------------- #
# Pulir un poco la base

# 
df = df.reset_index(drop=True)

#
df['ESTADO'] = df['ESTADO'].astype('category')
df['MUNICIPIO'] = df['MUNICIPIO'].astype('category')
df['POB'] = df['POB'].astype(int)

#
df = df.set_index(['MUNICIPIO', 'YEAR'])

#
for col in ['ING_CTE', 'PROPTAX', 'TRF_CTE']:

    df[col] = (
        df[col]
            .str.replace(',', '.')
            .astype(float))
    # End nested methods
# End for


# ----------------------------------- #
# Crear variables de interes

#
df['INGCTE_STRF'] = df['ING_CTE'] - df['TRF_CTE']

for col in ['ING_CTE', 'PROPTAX', 'TRF_CTE', 'INGCTE_STRF']:
    df[f'{col}pc'] = df[col] / df['POB']
# End for

df.to_parquet('data/punto7/bra_13_20.pqt')


# ------------------------------------------------------- #
# proccess - Uruguay

# ----------------------------------- #
# Cargar raw data de población

file = pd.ExcelFile('data/punto7/URUGUAY - 1996to2025 - R GOV - POB.xls')
sheets = file.sheet_names

pob = pd.DataFrame([])
drop_years = [2021, 2022, 2023, 2024, 2025]
drop_indexs = [0, 1, 2, 3]

for sheet in sheets:
    
    if sheet == 'Nota':
        continue
    else:
        pass
    # End if
    
    #
    aux_df = pd.read_excel(
        file, 
        sheet_name=sheet,
        skiprows=4)
    
    #
    aux_df = aux_df.drop(columns = drop_years, index = drop_indexs)
    #
    aux_df = aux_df.rename(columns={'Unnamed: 0': 'serie'})
    
    #
    condition = (aux_df['serie'] == 'Ambos sexos')
    #
    aux_df = aux_df[condition]

    #
    aux_df['serie'] = ['loc1', 'loc2', 'loc3']

    aux_df = pd.melt(
        aux_df,
        id_vars='serie',
        value_vars=[x for x in range(1996, 2021)],
        value_name='Value',
        var_name='Year'
    )

    aux_df = pd.pivot(
        aux_df,
        index='Year',
        columns='serie',
        values='Value'
    )

    aux_df['pob'] = aux_df['loc1'] + aux_df['loc2'] + aux_df['loc3']
    aux_df['dpto'] = sheet

    pob = pd.concat([pob, aux_df])
# End for