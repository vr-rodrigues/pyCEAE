import pandas as pd
import numpy as np
from functools import reduce
from dict_auxiliar import dict_produto, dict_mercado, dict_nome, dict_cerveja

# Definição de Funções Auxiliares
def preco_ajustado(preco, lista_gr, decimal=2):
    '''Esta função faz o ajuste dos preços das cervejas premium, trucando o resultado (default: 2 casas)'''
    gramatura_cesta = 0.35
    gramatura_media = reduce(lambda x, y: x + y, lista_gr) / len(lista_gr)
    preco = gramatura_cesta * preco / gramatura_media
    m = 10 ** decimal
    preco = int(preco * m) / m
    return preco

def input_cerveja(df_forms, df_aux):
    '''Esta função faz o input dos dados de cervejas
    já tratados na base de dados auxiliar'''
    for i in range(0, len(df_forms)):
        lista_gr = [forms['Cerveja Premium (GRAMATURA) - Preço 1'].loc[i],
                    forms['Cerveja Premium (GRAMATURA) - Preço 2'].loc[i],
                    forms['Cerveja Premium (GRAMATURA) - Preço 3'].loc[i]]

        lista_preco = [forms['Cerveja Premium (1 garrafa) - Preço 1'].loc[i],
                       forms['Cerveja Premium (1 garrafa) - Preço 2'].loc[i],
                       forms['Cerveja Premium (1 garrafa) - Preço 3'].loc[i]]

        cerveja_ajustada = [preco_ajustado(preco, lista_gr) for preco in lista_preco]

        for j in range(1,4):
            dict_cerveja[f'Cerveja Premium (1 garrafa) - Preço {j}']['preco'] = cerveja_ajustada[j-1]

            for key in dict_cerveja.keys():
                if key == f'Cerveja Premium (1 garrafa) - Preço {j}':
                    df_aux = df_aux.append({
                        f'preco_{j}': dict_cerveja[key]['preco'],
                        'data': df_forms['Data da Coleta'].loc[i],
                        'id_mercado': dict_mercado[f'{df_forms["Estabelecimento"].loc[i]}']['id'],
                        'regiao': dict_mercado[f'{df_forms["Estabelecimento"].loc[i]}']['regiao'],
                        'descricao': dict_cerveja[key]['descricao'],
                        'peso': 0.35,
                        'peso_obs': 0.35
                }, ignore_index=True)

    return df_aux

def input_product(df_forms, df_cerveja):
    '''Esta função faz o match entre os dados do output do forms e a
    base utilizada pelo CEAE via dicionários auxiliares'''
    for i in range(0, len(df_forms)):
        for key in dict_produto.keys():
            for j in range(1,4):
                if dict_produto[key]['preco'] == f'preco_{j}':
                    df_cerveja = df_cerveja.append({
                        f'preco_{j}': df_forms[f'{key}'].loc[i],
                        'data': df_forms['Data da Coleta'].loc[i],
                        'id_mercado': dict_mercado[f'{df_forms["Estabelecimento"].loc[i]}']['id'],
                        'regiao': dict_mercado[f'{df_forms["Estabelecimento"].loc[i]}']['regiao'],
                        'descricao': dict_produto[key]['descricao'],
                        'peso': dict_produto[key]['peso'],
                        'peso_obs': dict_produto[key]['peso_obs']
                    }, ignore_index=True)


    df_cerveja = df_cerveja.groupby(by=['id_mercado', 'regiao', 'descricao']).agg({
        'preco_1':'sum', 'preco_2':'sum', 'preco_3':'sum', 'data':'max', 'peso':'max', 'peso_obs':'max'})

    df_cerveja = df_cerveja.replace(0, np.NaN)
    return df_cerveja

def input_data(df_forms, df_aux):
    '''Essa função faz os inputs na ordem correta'''
    df_cerv = input_cerveja(df_forms, df_aux)
    df_cesta = input_product(df_forms, df_cerv)
    return df_cesta


# Gerando base auxiliar
cols = ['id_mercado', 'regiao', 'descricao', 'data', 'peso', 'peso_obs', 'preco_1', 'preco_2', 'preco_3']
df_aux = pd.DataFrame(columns=cols)

# Carregando Dados de Questionario Forms
forms = pd.read_excel('forms_output.xlsx')

# Chamando Função para Inputar Dados do Forms na Base Auxiliar
base_ajustada = input_data(forms,df_aux)

# Print Resultado
print(base_ajustada.to_string())