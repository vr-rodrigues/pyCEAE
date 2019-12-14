import pandas as pd
import os


os.chdir('dados/alimento')
arquivos = os.listdir(os.getcwd())


def get_keys(arq):
    garbage = ['Média', 'Cestas', 'Lista']
    keys = pd.read_excel(arq, sheet_name=None).keys()
    sheet_list = list(keys)
    for x in garbage:
        try:
            sheet_list.remove(x)
        except:
            pass
    return sheet_list


df_consolidada = pd.DataFrame()

for arquivo in arquivos:
    periodo = arquivo[0:5]
    for key in get_keys(arquivo):
        df = pd.read_excel(arquivo, sheet_name=key, skiprows=3)
        df['periodo'] = periodo
        df['id'] = key

        df_consolidada = df_consolidada.append(df, sort=True)
        print(f'{periodo} - {key}')

df_consolidada.to_csv('base_cestas.csv', encoding='utf-16', sep=';', index=False)