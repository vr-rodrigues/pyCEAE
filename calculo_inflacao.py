import pandas as pd
from dict_auxiliar import cesta_light, cesta_padrao, cesta_vegan, cesta_top

# Definição de Funções Auxiliares

def mean_price(df):
    '''
    Esta função faz a correção do preço relacionando o peso observado e o peso da cesta
    '''

    for i in range(1, 4):
        df[f'preco_{i}'] = ((df[f'preco_{i}'] * df['peso']) / df['peso_obs']).round(decimals=2)

    df['preco'] = df[['preco_1', 'preco_2', 'preco_3']].astype(float).mean(axis=1)
    df['preco'] = df['preco'].round(decimals=2)

    df = df.drop(columns=['preco_1', 'preco_2', 'preco_3', 'peso_obs', 'peso', 'id_mercado'])

    return df


def item_inflation(df):
    '''
    Esta função faz o calculo da inflação por item
    '''
    df = mean_price(df)

    df = df.drop(columns=['regiao'])
    df = df.groupby(by=['nome', 'data']).mean().round(decimals=4)
    df['preco_lag'] = df.groupby('nome')['preco'].shift(1)
    df['var_mensal'] = (df['preco']/df['preco_lag']).round(decimals=4)
    df = df.drop(columns=['preco', 'preco_lag'])
    df = df.unstack(level=0)

    df = df.fillna(1)
    df.columns = df.columns.get_level_values(1)
    df = df.rename_axis([None], axis=1).reset_index()

    return df


def basket_inflation(df):
    '''
    Esta função faz o calculo da inflação por cesta
    '''
    df = mean_price(df)
    df = df.drop(columns=['regiao'])
    df = df.groupby(by=['nome', 'data']).mean().round(decimals=4)
    df = df.unstack(level=0)
    df.columns = df.columns.get_level_values(1)
    df = df.rename_axis([None], axis=1).reset_index()
    df = df.interpolate()

    df['padrao'] = df[[c for c in df.columns if c in cesta_padrao]].sum(axis=1)
    df['light'] = df[[c for c in df.columns if c in cesta_light]].sum(axis=1)
    df['vegan'] = df[[c for c in df.columns if c in cesta_vegan]].sum(axis=1)
    df['top'] = df[[c for c in df.columns if c in cesta_top]].sum(axis=1)

    for cesta in ['padrao', 'light', 'vegan', 'top']:
        df[f'var_{cesta}'] = (((df[f'{cesta}'] / df[f'{cesta}'].shift(1)) - 1)*100).round(decimals=5)

    # df = df[['data', 'var_padrao', 'var_light', 'var_vegan', 'var_top']]
    return df


# Carregando Base de Dados
base = pd.read_excel('base_alimento.xlsx')

# Printando Resultados
print(basket_inflation(base).to_string())
