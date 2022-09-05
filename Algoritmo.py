from pulp import *
import csv
import os.path
from functools import reduce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
from time import process_time, perf_counter
from math import ceil


class Calculo():

    def __init__(self, An, meses):
        self.An = An
        self.meses = meses

    def geraAi(self):
        #fonte: https://stackoverflow.com/questions/18659858/generating-a-list-of-random-numbers-summing-to-1
        self.b = np.random.dirichlet(np.ones(self.An), size=1)
        #print(self.b, self.b.sum())
        return self.b

    def selectAtivos(self):

        # Acessando o arquivo csv
        file_name = os.path.join(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Papeis_{self.meses}_meses.csv')

        # Criando o DataFrame
        df = pd.read_csv(file_name, engine='python', sep=',')

        #Adicionando título as colunas
        df.columns = list(range(0, len(df.columns)))
        #print('-'*20, 'DataFrame dos dados', '-'*20)
        #print(df)

        # Invertendo as linhas e colunas [Função transpose (transposta)]
        df_transpose = df.T
        #print('-'*20, 'DataFrame dos dados Transposto', '-'*20)
        #print(df_transpose)

        # Imprime as médias, ordenando de forma decrescente.
        # OBS: a função média desconsidera automaticamente dados nulos

        # Fazendo a média por coluna e ordenando de forma decrescente
        ordenado = df_transpose.iloc[4:, 0:].mean().sort_values(ascending=False)
        #print(ordenado)
        # Selecionando as An, melhores médias e pegando os índices das colunas (porque é df transposta)
        self.best_mean = np.array(ordenado[0:self.An])
        self.best_mean_index = list(ordenado[0:self.An].index)
        self.best_name = []
        self.best_tipoDoPapel = []
        self.dividendo = []
        self.cota = []
        for i in range(self.An):
            self.best_name.append(df_transpose.iloc[0, self.best_mean_index[i]])
            self.best_tipoDoPapel.append(df_transpose.iloc[1, self.best_mean_index[i]])
            self.dividendo.append(df_transpose.iloc[2, self.best_mean_index[i]])
            self.cota.append(df_transpose.iloc[3, self.best_mean_index[i]])
            #try:
                #self.dividendo.append(df_transpose.iloc[2, self.best_mean_index[i]]/df_transpose.iloc[3, self.best_mean_index[i]])
            #except ZeroDivisionError:
                #self.dividendo.append(0)
        print('-'*20, 'Lista dos melhores papéis', '-'*20)
        print(self.best_name)
        print(self.best_tipoDoPapel)
        print(self.dividendo)
        # Inserindo os dados dos melhores papéis em uma lista
        lista_best = []
        #FAZER UM VERIFICAÇÃO DE DADOS NULOS E RETIRAR O QUE NÃO FOR NECESSÁRIO.
        '''
        # função para contar os dados não nulos df.count()
        max = min = 0
        for c, v in enumerate(self.best_mean_index):
            if c == 0:
                max = df_transpose.iloc[4:, v].count()
            else:
                if max < df_transpose.iloc[4:, v].count():
                    min = max
                    max = df_transpose.iloc[4:, v].count()
                elif max > df_transpose.iloc[4:, v].count():
                    min = df_transpose.iloc[4:, v].count()
                else:
                    max = df_transpose.iloc[4:, v].count()
        #print('-' * 20, 'Números de dados não nulos', '-' * 20)
        #print(max, min)
        '''
        for i in self.best_mean_index:
            lista_best.append(df_transpose.iloc[4:, i])
            #lista_best.append(df_transpose.iloc[4:, i])
        #print('-'*20, 'Lista dos melhores papéis', '-'*20)
        #print(lista_best)

        # Gerando uma matriz com os dados dos melhores papéis
        self.matriz_best = np.mat(lista_best).astype(float)
        #print('-'*20, 'Matriz dos melhores papéis', '-'*20)
        #print(self.matriz_best)
        #print(self.matriz_best.shape)
        #print('-'*20, 'Melhores médias', '-'*20)
        #print(self.matriz_best)
        #print(self.matriz_dividendo)
        return self.best_mean, self.best_mean_index

    def selectAtivosAcertivo(self):

        # Acessando o arquivo csv
        file_name = os.path.join(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Papeis_{self.meses}_meses.csv')

        # Criando o DataFrame
        df = pd.read_csv(file_name, engine='python', sep=',')

        #Adicionando título as colunas
        df.columns = list(range(0, len(df.columns)))
        #print('-'*20, 'DataFrame dos dados', '-'*20)
        #print(df)

        # Invertendo as linhas e colunas [Função transpose (transposta)]
        df_transpose = df.T
        #print('-'*20, 'DataFrame dos dados Transposto', '-'*20)
        #print(df_transpose)

        # Imprime as médias, ordenando de forma decrescente.
        # OBS: a função média desconsidera automaticamente dados nulos

        # Fazendo a média por coluna e ordenando de forma decrescente
        # 34 porque estamos utilizando 2 meses de histórico para prever 1 mês
        ordenado = df_transpose.iloc[34:, 0:].mean().sort_values(ascending=False)
        print(ordenado.head())
        # Selecionando as An, melhores médias e pegando os índices das colunas (porque é df transposta)
        self.best_mean = np.array(ordenado[0:self.An])
        self.best_mean_index = list(ordenado[0:self.An].index)
        self.best_name = []
        self.best_tipoDoPapel = []
        self.dividendo = []
        self.cota = []
        for i in range(self.An):
            self.best_name.append(df_transpose.iloc[0, self.best_mean_index[i]])
            self.best_tipoDoPapel.append(df_transpose.iloc[1, self.best_mean_index[i]])
            self.dividendo.append(df_transpose.iloc[2, self.best_mean_index[i]])
            self.cota.append(df_transpose.iloc[3, self.best_mean_index[i]])
        print('-'*20, 'Lista dos melhores papéis', '-'*20)
        print(self.best_name)
        print(self.best_tipoDoPapel)
        print(self.dividendo)
        print(self.cota)
        # Inserindo os dados dos melhores papéis em uma lista
        lista_best = []
        self.lista_best_10 = []
        for i in self.best_mean_index:
            lista_best.append(df_transpose.iloc[34:, i])
            self.lista_best_10.append(df_transpose.iloc[4:34, i])
            #lista_best.append(df_transpose.iloc[4:, i])
        #print('-'*20, 'Lista dos melhores papéis', '-'*20)
        #print(lista_best)
        #print(self.lista_best_10)

        # Gerando uma matriz com os dados dos melhores papéis
        self.matriz_best = np.mat(lista_best).astype(float)
        #print('-'*20, 'Matriz dos melhores papéis', '-'*20)
        #print(self.matriz_best)
        #print(self.matriz_best.shape)
        #print('-'*20, 'Melhores médias', '-'*20)
        #print('-' * 20, 'Matriz best', '-' * 20)
        #print(self.matriz_best)
        #print(self.matriz_dividendo)
        return self.best_mean, self.best_mean_index


    def solve(self, iter):

        # Gerando a Matriz de Covariância
        matrix_Cov = np.cov(self.matriz_best, ddof=0)
        #print('-'*20, 'Matriz da Covariância', '-'*20)
        #print(matrix_Cov)

        # EQUAÇÃO DO RETORNO
        # Transformando a lista das melhores médias em matriz
        matrix_best_mean = np.mat(self.best_mean).astype(float)
        # Transformando a lista de dividendos em matriz
        self.matriz_dividendo = np.mat(self.dividendo).astype(float)
        # Somando as matrizes best_mean e dividendos
        matriz = matrix_best_mean + self.matriz_dividendo
        #print('-' * 20, 'Matrizes que compõem o retorno', '-' * 20)
        #print(matrix_best_mean)
        #print(self.matriz_dividendo)
        #print(matriz)

        # Armazenando os resultados
        # Verificando se o arquivo existe
        if os.path.exists(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Resultados_{self.meses}_meses.csv'):
            os.remove(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Resultados_{self.meses}_meses.csv')
        with open(f'Dados_Resultados_{self.meses}_meses.csv', 'w', newline='') as dados:
            writer = csv.writer(dados)
            unilist = []
            for i in range(0, iter):
                # Chama o gerador de Ai
                Ain = self.geraAi()
                # Retorno multiplicando as matrizes de An(1x3) x média(3x1)
                #retorno = Ain.dot(matrix_best_mean.T)
                retorno = Ain.dot(matriz.T)
                #print('-' * 20, 'Retorno', '-' * 20)
                #print(retorno)

                # EQUAÇÃO DO RISCO
                risco = Ain.dot(matrix_Cov).dot(Ain.T)
                #print('-' * 20, 'Risco', '-' * 20)
                #print(risco)

                # EQUAÇÃO DE MAXIMIZAÇÃO
                #maximum = retorno + (1/risco)
                maximum = retorno/risco
                #print('-' * 20, 'Maximum retorno', '-' * 20)
                #print(maximum)

                for i in range(self.An):
                    unilist.append(Ain[0, i])
                unilist.append(retorno[0, 0])
                unilist.append(risco[0, 0])
                unilist.append(maximum[0, 0])
                #print(unilist)
                writer.writerow(unilist)
                unilist.clear()
        file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Resultados_{self.meses}_meses.csv'
        df = pd.read_csv(file_name, engine='python')

        # Criando lista para renomear as colunas
        self.columns_name = []
        for i in range(self.An):
            self.columns_name.append(f'A{i+1}')
        self.columns_name.append('Retorno')
        self.columns_name.append('Risco')
        self.columns_name.append('Maximum')
        #df.columns = ['A1', 'A2', 'A3', 'Retorno', 'Risco', 'Maximum']
        df.columns = self.columns_name
        print('-' * 20, 'Dataframe dos resultados', '-' * 20)
        print(df.head())
        # Ordenando os valores de maximum e pegando o melhor
        #ord_max = df.iloc[0:, 5].sort_values(ascending=False)
        ord_max = df.sort_values(['Maximum'], ascending=False)
        print('-' * 20, 'Dataframe dos resultados Ordenada', '-' * 20)
        print(ord_max.head())
        #best_max = ord_max.index[0]
        #print(best_max)

    def ganhoReal(self):

        # Obtendo os resultados dos papéis através do Dataframe
        file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Resultados_{self.meses}_meses.csv'
        df = pd.read_csv(file_name, engine='python')
        df.columns = self.columns_name
        df = df.sort_values(['Maximum'], ascending=False)
        investido = 10000
        partes = []
        total = 0.0
        parce = 1.0
        # Separando o capital investido em cada papel numa lista
        for i in range(0, self.An):
            partes.append(df.iloc[0, i]*investido)
        #print(partes)
        #matrix_partes = np.mat(partes).astype(float)
        #print(len(self.lista_best_10[0]))
        # Efetuando o cálculo de juros compostos sobre o capital investido
        for c, p in enumerate(partes):
            for i in self.lista_best_10[c][::-1]:
                if parce == 1:
                    parce = p * (1 + (i/100))
                else:
                    parce *= (1 + (i / 100))
            total += parce
            parce = 1
        print(f'R${total:.2f}')
        retorno = (total - investido) / (investido)
        print(f'{retorno*100:.2f}%')
        #print(df.iloc[0, self.An])
        desvio = np.array([retorno*100, df.iloc[0, self.An]])
        print('-' * 20, 'Desvio padrão dos retornos', '-' * 20)
        print(desvio.std())
        '''
        print(df.iloc[0, 0:])
        parce_redondo = []
        for i in self.cota:
            parce_redondo.append(int(round(i)))
        print(parce_redondo)
        print(np.lcm.reduce(parce_redondo))
        #print(np.gcd.reduce(parce_redondo))
        '''

    def quantAtivos(self):
        # Coletando os dados de Ai
        file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Resultados_{self.meses}_meses.csv'
        df = pd.read_csv(file_name, engine='python')
        df.columns = self.columns_name
        df = df.sort_values(['Maximum'], ascending=False)

        # Cria o problema
        prob = LpProblem('Investimento Mínimo', LpMinimize)

        # Cria as variáveis
        '''
        x1 = LpVariable('a1', 0)
        x2 = LpVariable('a2', 0)
        x3 = LpVariable('a3', 0)
        '''
        # Dando nome às variáveis
        name_Str = [f'a{i+1}' for i in range(0, self.An)]
        name_var = [LpVariable(name_Str[n], 0) for n in range(0, self.An)]
        # Colocando as variáveis e os valores das cotas numa array
        matriz_var = np.array(name_var)
        matriz_cota = np.array(self.cota)

        # Cria Função Objetivo
        # prob += (x1 * self.cota[0]) + (x2 * self.cota[1]) + (x3 * self.cota[2]), 'Investimento'
        prob += matriz_var.dot(matriz_cota.T)

        # Restrições
        '''
        prob += x1*self.cota[0] >= df.iloc[0, 0], 'Quantidade 1'
        prob += x2*self.cota[1] >= df.iloc[0, 1], 'Quantidade 2'
        prob += x3*self.cota[2] >= df.iloc[0, 2], 'Quantidade 3'
        '''
        for i in range(0, self.An):
            prob += name_var[i]*self.cota[0] >= df.iloc[0, i], f'Quantidade {i}'

        # Escreve o modelo no arquivo
        prob.writeLP('Minimize_Invest.lp')

        # Resolve o problema
        prob.solve()

        # imprime o status da resolução
        print(f'Status: {LpStatus[prob.status]}')

        # Soluções ótimas das variáveis (quantidades)
        list_var = []
        for variable in prob.variables():
            print(f'{variable.name} = {variable.varValue}')
            list_var.append(variable.varValue)

        # Objetivo otimizado
        print(f'A quantidade de cota de cada ativo é:{prob.objective}')
        #print(list_var)

        # Determinando as quantidades de cada papel
        array_var = np.array(list_var)
        menor_var = array_var.min()
        '''
        Para descobrir a quantidade de cada ativo pega-se o menor valor das variáveis encontrado pela PO
        e calcula-se qual número multiplicado por ele é igual a 1, para atribuir uma unidade ao ativo em
        questão, em seguida multiplica-se esse coeficiente aos demais valores encontrando assim as quantidades
        de cada ativo.
        '''
        coeficiente = 1/menor_var
        # Quantidade de cada cota/papel
        valores = [round(x*coeficiente) for x in list_var]
        # Valor de cada papel
        print(self.cota)
        # Valor gasto em cada cota/papel
        investimento_min = [self.cota[i]*v for i, v in enumerate(valores)]
        # Valor total a ser investido
        total_invest = reduce(lambda a, b: a+b, investimento_min)
        print(valores)
        print(investimento_min)
        print(f'R${total_invest:.2f}')

    def plot(self):
        file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Resultados_{self.meses}_meses.csv'
        df = pd.read_csv(file_name, engine='python')
        df.columns = self.columns_name
        df = df.sort_values(['Maximum'], ascending=False)
        #df.plot('Risco', 'Retorno') #(x,y)
        #plt.plot(df['Risco'], df['Retorno'], 'ro')

        # Gráfico de dispersão de Markovit
        plt.scatter(df['Risco'], df['Retorno'], alpha=0.5, c=df['Risco'])
        #plt.legend()
        plt.title('Gráfico do retorno ótimo de Markowitz')
        plt.xlabel('Risco')
        plt.ylabel('Retorno')

        # Gráfico de pizza das porcentagens
        labels = self.best_name
        porcent = []
        for i in range(self.An):
            porcent.append(df.iloc[0, i]*100)
        sizes = porcent
        #explode = (0, 0, 0.1)
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.axis('equal')
        plt.show()
        #melhor maximum 7.233474 1.46 de retorno e 3.49% de retorno real
        '''
        fonte: https://blog.rico.com.vc/fundos-imobiliarios
        Comparativo de rentabilidade dos Fundos Imobiliários

        Vamos utilizar dois exemplos de fundos.

        O primeiro tem o valor da cota em R$ 120,00. Os aluguéis foram de R$ 1,20 por cota. 
        Ao dividir, 1,20/ 120,  a sua rentabilidade foi de 1%.
        '''

if __name__ == '__main__':
    bob = Calculo(8, 12)
    #bob.geraAi()
    bob.selectAtivos()
    #bob.selectAtivosAcertivo()
    bob.solve(80000)
    #bob.ganhoReal()
    bob.quantAtivos()
    duracao = round((perf_counter()), 0)
    horas = int(duracao // 3600)
    minutos = int(round((duracao / 3600 - duracao // 3600) * 60, 0))
    segundos = int(round((duracao % 60), 0))
    print(f'Tempo de execução:{horas}:{minutos}:{segundos}')
    bob.plot()
    #print(f'Tempo de execução:{process_time()} segundos')
