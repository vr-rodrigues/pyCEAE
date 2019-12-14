import pandas as pd
import os

os.chdir('dados/combustivel')
arquivos = os.listdir()


df_consolidada = pd.DataFrame()

for arquivo in arquivos:
    df = pd.read_csv(arquivo, sep=',')
    df_consolidada = df_consolidada.append(df, sort=True)
    print(arquivo)

df_consolidada.to_csv('base_combustivel.csv', encoding='utf-16', sep=';', index=False)