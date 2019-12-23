import numpy as np
from functools import reduce
import dict as dic

# ===========================================
# Funções para adequação do output do forms
# ===========================================


def preco_ajustado(preco, lista_gr, item='cerveja', decimal=2):
    """ Esta função faz o ajuste dos preços das cervejas premium, trucando o resultado (default: 2 casas) """
    if item == 'cerveja':
        gramatura_cesta = 0.35
    else:
        gramatura_cesta = 0.2

    try:
        gramatura_media = reduce(lambda x, y: x + y, lista_gr) / len(lista_gr)
        preco = gramatura_cesta * preco / gramatura_media
        m = 10 ** decimal
        preco = int(preco * m) / m
    except:
        preco = np.nan

    return preco


def input_cerveja(df_forms, df):
    """ Esta função faz o input dos dados de cervejas, já tratados, na base de dados auxiliar"""

    for i in range(0, len(df_forms)):
        lista_gr = [df_forms['Cerveja Premium (GRAMATURA) - Preço 1'].loc[i],
                    df_forms['Cerveja Premium (GRAMATURA) - Preço 2'].loc[i],
                    df_forms['Cerveja Premium (GRAMATURA) - Preço 3'].loc[i]]

        lista_preco = [df_forms['Cerveja Premium (1 garrafa) - Preço 1'].loc[i],
                       df_forms['Cerveja Premium (1 garrafa) - Preço 2'].loc[i],
                       df_forms['Cerveja Premium (1 garrafa) - Preço 3'].loc[i]]

        cerveja_ajustada = [preco_ajustado(preco, lista_gr, 'cerveja', 3) for preco in lista_preco]

        for j in range(1, 4):
            dic.dict_cerveja[f'Cerveja Premium (1 garrafa) - Preço {j}']['preco'] = cerveja_ajustada[j-1]

            for key in dic.dict_cerveja.keys():
                if key == f'Cerveja Premium (1 garrafa) - Preço {j}':
                    df = df.append({
                        f'preco_{j}': dic.dict_cerveja[key]['preco'],
                        'data': df_forms['Data'].loc[i],
                        'id_mercado': dic.dict_mercado[f'{df_forms["Mercado"].loc[i]}']['id'],
                        'regiao': dic.dict_mercado[f'{df_forms["Mercado"].loc[i]}']['regiao'],
                        'descricao': dic.dict_cerveja[key]['descricao'],
                        'peso': 0.35,
                        'peso_obs': 0.35
                                    }, ignore_index=True)

    return df


def input_restante(df_forms, df):
    """ Esta função faz o input dos outros dados, que nao são cerveja mas também tem gramatura diferenciada,
    já tratados, na base de dados auxiliar """

    for i in range(0, len(df_forms)):
        lista_gr = [df_forms['Biscoito Salgado (GRAMATURA) - Preço 1'].loc[i],
                    df_forms['Biscoito Salgado (GRAMATURA) - Preço 2'].loc[i],
                    df_forms['Biscoito Salgado (GRAMATURA) - Preço 3'].loc[i],
                    df_forms['Biscoito Recheado (GRAMATURA) - Preço 1'].loc[i],
                    df_forms['Biscoito Recheado (GRAMATURA) - Preço 2'].loc[i],
                    df_forms['Biscoito Recheado (GRAMATURA) - Preço 3'].loc[i],
                    df_forms['Cereal Matinal (GRAMATURA) - Preço 1'].loc[i],
                    df_forms['Cereal Matinal (GRAMATURA) - Preço 2'].loc[i],
                    df_forms['Cereal Matinal (GRAMATURA) - Preço 3'].loc[i]]

        lista_preco = [df_forms['Biscoito Salgado - Preço 1'].loc[i],
                       df_forms['Biscoito Salgado - Preço 2'].loc[i],
                       df_forms['Biscoito Salgado - Preço 3'].loc[i],
                       df_forms['Biscoito Recheado (1 pacote) - Preço 1'].loc[i],
                       df_forms['Biscoito Recheado (1 pacote) - Preço 2'].loc[i],
                       df_forms['Biscoito Recheado (1 pacote) - Preço 3'].loc[i],
                       df_forms['Cereal Matinal (1 caixa) - Preço 1'].loc[i],
                       df_forms['Cereal Matinal (1 caixa) - Preço 2'].loc[i],
                       df_forms['Cereal Matinal (1 caixa) - Preço 3'].loc[i]]

        ajuste = [preco_ajustado(preco, lista_gr, 'outros', 3) for preco in lista_preco]

        count = 0
        for key in dic.dict_restante.keys():
            dic.dict_restante[key]['preco_ajustado'] = ajuste[count]

            for j in range(1, 4):
                if dic.dict_restante[key]['preco'] == f'preco_{j}':
                    df = df.append({
                        f'preco_{j}': dic.dict_restante[key]['preco_ajustado'],
                        'data': df_forms['Data'].loc[i],
                        'id_mercado': dic.dict_mercado[f'{df_forms["Mercado"].loc[i]}']['id'],
                        'regiao': dic.dict_mercado[f'{df_forms["Mercado"].loc[i]}']['regiao'],
                        'descricao': dic.dict_restante[key]['descricao'],
                        'peso': 0.2,
                        'peso_obs': 0.2
                        }, ignore_index=True)
            count += 1

    return df


def adequa_forms(df_forms, df):
    """Esta função faz o match entre os dados do output do forms e a
    base utilizada pelo CEAE via dicionários auxiliares"""

    df = input_restante(df_forms, df)
    for i in range(0, len(df_forms)):
        for key in dic.dict_produto.keys():
            for j in range(1, 4):
                if dic.dict_produto[key]['preco'] == f'preco_{j}':
                    df = df.append({
                        f'preco_{j}': df_forms[f'{key}'].loc[i],
                        'data': df_forms['Data'].loc[i],
                        'id_mercado': dic.dict_mercado[f'{df_forms["Mercado"].loc[i]}']['id'],
                        'regiao': dic.dict_mercado[f'{df_forms["Mercado"].loc[i]}']['regiao'],
                        'descricao': dic.dict_produto[key]['descricao'],
                        'peso': dic.dict_produto[key]['peso'],
                        'peso_obs': dic.dict_produto[key]['peso_obs']
                    }, ignore_index=True)

    df = df.groupby(by=['id_mercado', 'regiao', 'descricao']).agg(
        {'preco_1': 'sum', 'preco_2': 'sum', 'preco_3': 'sum', 'data': 'max', 'peso': 'max', 'peso_obs': 'max'})

    df = df.replace(0, np.NaN).reset_index()
    return df


# ===========================================
# Funções para calculo da inflação
# ===========================================

def mean_price(df):
    """ Esta função faz a correção do preço relacionando o peso observado e o peso da cesta """

    for i in range(1, 4):
        df[f'preco_{i}'] = ((df[f'preco_{i}'] * df['peso']) / df['peso_obs'])

    df['preco'] = df[['preco_1', 'preco_2', 'preco_3']].astype(float).mean(axis=1)
    df = df.drop(columns=['preco_1', 'preco_2', 'preco_3', 'peso_obs', 'peso', 'id_mercado'])

    return df


def item_inflation(df):
    """ Esta função faz o calculo da inflação por item """
    df = mean_price(df)

    df = df.drop(columns=['regiao'])
    df = df.groupby(by=['descricao', 'data']).mean()
    df['preco_lag'] = df.groupby('descricao')['preco'].shift(1)
    df['var_mensal'] = (df['preco']/df['preco_lag']) - 1
    df.drop(columns=['preco', 'preco_lag'], inplace=True)
    df = df.unstack(level=0)

    df = df.interpolate()
    df.columns = df.columns.get_level_values(1)
    df = df.rename_axis([None], axis=1).reset_index()

    return df


def basket_inflation(df):
    """ Esta função faz o calculo da inflação por cesta """
    df = mean_price(df)
    df = df.drop(columns=['regiao'])
    df = df.groupby(by=['descricao', 'data']).mean()
    df = df.unstack(level=0)
    df.columns = df.columns.get_level_values(1)
    df = df.rename_axis([None], axis=1).reset_index()
    df = df.interpolate()

    df['ICEAE Padrão'] = df[[c for c in df.columns if c in dic.cesta_padrao]].sum(axis=1)
    df['ICEAE Light'] = df[[c for c in df.columns if c in dic.cesta_light]].sum(axis=1)
    df['ICEAE Vegetariano'] = df[[c for c in df.columns if c in dic.cesta_vegetariano]].sum(axis=1)
    df['ICEAE Top'] = df[[c for c in df.columns if c in dic.cesta_top]].sum(axis=1)

    for cesta in ['ICEAE Padrão', 'ICEAE Light', 'ICEAE Vegetariano', 'ICEAE Top']:
        df[f'{cesta}'] = (df[f'{cesta}'] / df[f'{cesta}'].shift(1))

    df = df[['data', 'ICEAE Padrão', 'ICEAE Light', 'ICEAE Vegetariano', 'ICEAE Top']]

    df = df.melt(id_vars=['data'])
    df['acumulado'] = df.groupby(by=['variable'], group_keys=False).rolling(12).apply(np.prod, raw=True)

    df['acumulado'] = df['acumulado'] - 1
    df['value'] = df['value'] - 1

    return df.round(decimals=5)
