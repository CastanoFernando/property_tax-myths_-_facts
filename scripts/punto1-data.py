import pandas as pd


## ---------------------------------- #
## Datos de pob

#
pob = pd.read_csv('data/punto1/WB - POB.csv', skiprows=3)
#
pob = pob.rename(columns={'Country Code': 'COU'})

#
pob = pob.melt(
    id_vars= 'COU',
    value_vars= [str(x) for x in range(1990,2021)],
    var_name= 'Year',
    value_name= 'POB')
# End melt

#
pob.Year = pob.Year.astype(int)
pob.COU = pob.COU.astype(object)


# ----------------------------------- #
# Datos de gdp current USD

#
gdp = pd.read_csv('data/punto1/WB-GDP-CRNT-USD.csv', skiprows=3)
#
gdp = gdp.rename(columns={'Country Code': 'COU'})
gdp = gdp.melt(
    id_vars= 'COU',
    value_vars= [str(x) for x in range(1990,2021)],
    var_name= 'Year',
    value_name= 'GDP')

#
gdp.COU = gdp.COU.astype(str)
gdp.Year = gdp.Year.astype(int)

# ----------------------------------- #
# Datos de regiones

reg = pd.read_excel('data/punto1/CountryGroups.xlsx')


# ----------------------------------- #
# Datos de tax revenue

#
revenue = pd.read_parquet(f'data/oecd_tax_rev_stats.pqt')

# Quedarse con los datos de immovable tax
condition   = (revenue['TAX'] =='4100')
# Quedarse con los datos de vat
condition  |= (revenue['TAX'] =='5111')
# Quedarse con los datos de sales tax
condition  |= (revenue['TAX'] =='5112')
# Quedarse con los datos de indiv income tax
condition  |= (revenue['TAX'] =='1110')
# Quedarse con los datos de indiv income tax
condition  |= (revenue['TAX'] =='1210')
# Quedarse con los datos del sector publico total
condition  &= (revenue['GOV'] == 'NES')
# Quedarse con los datos valuados en dolares
condition  &= (~revenue['VAR'].isin(['TAXNAT', 'TAXUSD']))

#
revenue = revenue[condition]

#
xl = pd.ExcelWriter('data/punto1/Data-Ley-Wagner.xlsx')
#
for tax in revenue['TAX'].unique():
    
    #
    df_aux = revenue[revenue['TAX'] == tax]
    #
    df_aux = df_aux.pivot(
        index=['COU', 'TAX', 'Year'],
        columns='VAR',
        values='Value')
    # End pivot
    
    #
    df_aux = df_aux.reset_index()
    #
    df_aux = df_aux.merge(pob, how='left', on=['COU', 'Year'])
    #
    df_aux = df_aux.merge(gdp, how='left', on=['COU', 'Year'])
    #
    df_aux = df_aux.merge(reg, how='left', on='COU')
    #
    df_aux['GDPpc'] = df_aux['GDP'] / df_aux['POB']
    #
    df_aux.to_excel(xl, sheet_name=tax)
# End for
xl.close()