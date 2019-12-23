import pandas as pd
from funcoes import adequa_forms, item_inflation, basket_inflation

# ===========================================
# Atualização da Base de Dados
# ===========================================

xlsx_forms = input('Qual o nome (sem extensão) da base de resposta do forms? Precisa estar em xlsx. R: ')

# Carregando Dados de Questionario Forms
forms = pd.read_excel(f'{xlsx_forms}.xlsx')
forms['Data'] = forms['Data'].apply(lambda dt: dt.replace(day=1))

forms_adeq = adequa_forms(forms, pd.DataFrame())

base_alimento = pd.read_excel('base_alimento.xlsx')

base_atualizada = base_alimento.append(forms_adeq, sort=True).reset_index()
base_atualizada.drop('index', axis=1, inplace=True)

# ===========================================
# Calculo Inflação e Atualização
# ===========================================

if __name__ == '__main__':
    # Resultados Item
    inflacao_item = item_inflation(base_atualizada)
    inflacao_item = inflacao_item.melt(id_vars=['data']).round(decimals=3)

    inflacao_item.to_csv('inflacao_item.csv', encoding='utf-16', sep=';', index=False, header=True, decimal=',')
    print('\nArquivo inflacao_item.csv atualizado')

    # Resultados Cestas
    inflacao_cesta = basket_inflation(base_atualizada)

    inflacao_cesta.to_csv('inflacao_cesta.csv', encoding='utf-16', sep=';', index=False, header=True, decimal=',')
    print("Arquivo inflacao_cesta.csv atualizado")
