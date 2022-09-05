from pulp import *
import csv
import os.path
from functools import reduce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from matplotlib import style
from time import process_time, perf_counter
from math import ceil
import threading
import random
import shelve


class Calculo(threading.Thread):

    def __init__(self, An, meses, kind, iter, mutex, capMax, pvpmin, pvpmax, liquidez,  preco_suporte, fixos, salvo):
        self.An = An
        self.meses = meses
        self.kind = kind
        self.iter = iter
        self.mutex = mutex
        self.capMax = capMax
        self.pvpmin = pvpmin
        self.pvpmax = pvpmax
        self.liquidez = liquidez
        self.preco_suporte = preco_suporte
        self.fixos = fixos
        self.path_salvo = salvo
        threading.Thread.__init__(self)

    def geraAi(self, numbers):
        #fonte: https://stackoverflow.com/questions/18659858/generating-a-list-of-random-numbers-summing-to-1
        self.b = np.random.dirichlet(np.ones(numbers), size=1)
        #print(self.b, self.b.sum())
        return self.b

    def selectAtivos(self):

        # Acessando o arquivo csv
        file_name = os.path.join(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados/Dados_Papeis_{self.meses}_meses_{self.kind}.csv')

        # Criando o DataFrame
        df = pd.read_csv(file_name, engine='python', sep=',')
        #print(df)

        # Invertendo as linhas e colunas [Função transpose (transposta)]
        df_transpose = df.T
        print('-'*20, 'DataFrame dos dados Transposto', '-'*20)
        print(df_transpose)
        self.num_column = 0
        # Filtrando os dados pelo valor de p/vp, liquidez diária e médias móveis
        # Obs: Ao efetuar o filtro ocorre a modificação dos índices, por isso da erro ao fazer filtragens em sequência.
        if self.pvpmin != 0 and self.pvpmax != 0 and self.liquidez >= 0:
            df_filtered = df[(df_transpose.iloc[6, 0:] <= self.pvpmax) & (df_transpose.iloc[6, 0:] >= self.pvpmin) &
                             (df_transpose.iloc[4, 0:] >= self.liquidez) & (df_transpose.iloc[5, 0:] >= 0) &
                             (df_transpose.iloc[8, 0:] > 0) & (df_transpose.iloc[9, 0:] > 0) & (df_transpose.iloc[8, 0:] >= df_transpose.iloc[8, 0:]) &
                             (df_transpose.iloc[3, 0:] <= df_transpose.iloc[7, 0:] * self.preco_suporte)] # Compara a último preço com o preço médio
            df_filtered_transpose = df_filtered.T
            self.num_column = df_filtered_transpose.shape[1]
        #print(df_filtered_transpose)
        elif self.liquidez >= 0:
            df_filtered = df[(df_transpose.iloc[4, 0:] >= self.liquidez) & (df_transpose.iloc[5, 0:] >= 0) &
                             (df_transpose.iloc[8, 0:] > 0) & (df_transpose.iloc[9, 0:] > 0) &
                             (df_transpose.iloc[8, 0:] >= df_transpose.iloc[9, 0:]) &
                             (df_transpose.iloc[3, 0:] <= df_transpose.iloc[7, 0:] * self.preco_suporte)]  # Compara a último preço com o preço médio
            df_filtered_transpose = df_filtered.T
            self.num_column = df_filtered_transpose.shape[1]
        # Filtrando somente pelas médias móveis e média simples
        else:
            df_filtered = df[(df_transpose.iloc[8, 0:] > 0) & (df_transpose.iloc[9, 0:] > 0) &
                             (df_transpose.iloc[8, 0:] >= df_transpose.iloc[9, 0:]) & (df_transpose.iloc[3, 0:] <= df_transpose.iloc[7, 0:] * self.preco_suporte)]
            df_filtered_transpose = df_filtered.T
            self.num_column = df_filtered_transpose.shape[1]
        # Imprime as médias, ordenando de forma decrescente.
        # OBS: a função média desconsidera automaticamente dados nulos

        # Fazendo a média por coluna e ordenando de forma decrescente
        ordenado = df_filtered_transpose.iloc[10:, 0:].mean().sort_values(ascending=False)

        #ordenado = df_transpose.iloc[6:, 0:].mean().sort_values(ascending=False)
        #print(ordenado)
        # Selecionando as An, melhores médias e pegando os índices das colunas (porque é df transposta)
        if self.num_column >= self.An:
            self.best_mean = np.array(ordenado[0:self.An])
            self.best_mean_index = list(ordenado[0:self.An].index)
        else:
            self.best_mean = np.array(ordenado[0:self.num_column])
            self.best_mean_index = list(ordenado[0:self.num_column].index)
        self.best_name = []
        self.best_tipoDoPapel = []
        self.dividendo = []
        self.cota = []
        self.liquidez = []
        self.pvp = []
        if self.num_column >= self.An:
            for i in range(self.An):
                self.best_name.append(df_transpose.iloc[0, self.best_mean_index[i]])
                self.best_tipoDoPapel.append(df_transpose.iloc[1, self.best_mean_index[i]])
                self.dividendo.append(df_transpose.iloc[2, self.best_mean_index[i]])
                self.cota.append(df_transpose.iloc[3, self.best_mean_index[i]])
                self.liquidez.append(df_transpose.iloc[4, self.best_mean_index[i]])
                self.pvp.append(df_transpose.iloc[5, self.best_mean_index[i]])
                #try:
                    #self.dividendo.append(df_transpose.iloc[2, self.best_mean_index[i]]/df_transpose.iloc[3, self.best_mean_index[i]])
                #except ZeroDivisionError:
                    #self.dividendo.append(0)
        else:
            for i in range(self.num_column):
                self.best_name.append(df_transpose.iloc[0, self.best_mean_index[i]])
                self.best_tipoDoPapel.append(df_transpose.iloc[1, self.best_mean_index[i]])
                self.dividendo.append(df_transpose.iloc[2, self.best_mean_index[i]])
                self.cota.append(df_transpose.iloc[3, self.best_mean_index[i]])
                self.liquidez.append(df_transpose.iloc[4, self.best_mean_index[i]])
                self.pvp.append(df_transpose.iloc[5, self.best_mean_index[i]])
        print('-'*20, 'Lista dos melhores papéis', '-'*20)
        print(self.best_name)
        print(self.best_tipoDoPapel)
        print(self.dividendo)
        #print(self.cota)
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
            lista_best.append(df_transpose.iloc[10:, i])
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
        file_name = os.path.join(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados_Papeis_{self.meses}_meses_{self.kind}.csv')

        # Criando o DataFrame
        df = pd.read_csv(file_name, engine='python', sep=',')

        #Adicionando título as colunas
        #df.columns = list(range(0, len(df.columns)))
        #print('-'*20, 'DataFrame dos dados', '-'*20)
        #print(df)

        # Invertendo as linhas e colunas [Função transpose (transposta)]
        df_transpose = df.T
        #print('-'*20, 'DataFrame dos dados Transposto', '-'*20)
        #print(df_transpose)

        # Imprime as médias, ordenando de forma decrescente.
        # OBS: a função média desconsidera automaticamente dados nulos


        # Filtrando os dados pelo valor de liquidez e p/vp
        # df_transpose = (df_transpose.iloc[4, 0:] <= 1.1) & (df_transpose.iloc[4, 0:] >= 0.9)
        df_filtered = df[(df_transpose.iloc[4, 0:] >= 2000) & (df_transpose.iloc[5, 0:] <= 1.1) & (df_transpose.iloc[5, 0:] >= 0.9)]
        df_filtered_transpose = df_filtered.T
        # print(df_filtered_transpose)
        # Imprime as médias, ordenando de forma decrescente.
        # OBS: a função média desconsidera automaticamente dados nulos

        # Fazendo a média por coluna e ordenando de forma decrescente
        # 7 porque estamos utilizando n dias/meses de histórico para prever 1 dia/mês
        ordenado = df_filtered_transpose.iloc[7:, 0:].mean().sort_values(ascending=False)
        #ordenado = df_transpose.iloc[35:, 0:].mean().sort_values(ascending=False)
        print(ordenado.head())
        # Selecionando as An, melhores médias e pegando os índices das colunas (porque é df transposta)
        self.best_mean = np.array(ordenado[0:self.An])
        self.best_mean_index = list(ordenado[0:self.An].index)
        self.best_name = []
        self.best_tipoDoPapel = []
        self.dividendo = []
        self.cota = []
        self.liquidez = []
        self.pvp = []
        for i in range(self.An):
            self.best_name.append(df_transpose.iloc[0, self.best_mean_index[i]])
            self.best_tipoDoPapel.append(df_transpose.iloc[1, self.best_mean_index[i]])
            self.dividendo.append(df_transpose.iloc[2, self.best_mean_index[i]])
            self.cota.append(df_transpose.iloc[3, self.best_mean_index[i]])
            self.liquidez.append(df_transpose.iloc[4, self.best_mean_index[i]])
            self.pvp.append(df_transpose.iloc[5, self.best_mean_index[i]])
        print('-'*20, 'Lista dos melhores papéis', '-'*20)
        print(self.best_name)
        print(self.best_tipoDoPapel)
        print(self.dividendo)
        print(self.cota)
        # Inserindo os dados dos melhores papéis em uma lista
        lista_best = []
        self.lista_best_10 = []
        for i in self.best_mean_index:
            lista_best.append(df_transpose.iloc[7:, i])
            self.lista_best_10.append(df_transpose.iloc[6, i])
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


    def solve(self): #Antigo run

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
        if os.path.exists(f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv'):
            os.remove(f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv')
        with open(f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv', 'w', newline='') as dados:
            writer = csv.writer(dados)

            # Criando lista para renomear as colunas
            self.columns_name = []
            c = 0
            if self.num_column >= self.An:
                for i in range(0, (self.An // 10) + 1):
                    for v in range(0, 10):
                        if i == 0 and v == 0:
                            c += 1
                            pass
                        else:
                            self.columns_name.append(f'A{i}{v}')
                            c += 1
                            if c == self.An + 1: break
            else:
                for i in range(0, (self.num_column // 10) + 1):
                    for v in range(0, 10):
                        if i == 0 and v == 0:
                            c += 1
                            pass
                        else:
                            self.columns_name.append(f'A{i}{v}')
                            c += 1
                            if c == self.num_column + 1: break
            self.columns_name.append('Retorno')
            self.columns_name.append('Risco')
            self.columns_name.append('Maximum')
            writer.writerow(self.columns_name)

            unilist = []
            for i in range(0, self.iter):
                with self.mutex:
                    # Chama o gerador de Ai
                    if self.num_column >= self.An:
                        Ain = self.geraAi(self.An)
                    else:
                        Ain = self.geraAi(self.num_column)
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
                    maximum = 1/risco#retorno/risco
                    #print('-' * 20, 'Maximum retorno', '-' * 20)
                    #print(maximum)
                    if self.num_column >= self.An:
                        for i in range(self.An):
                            unilist.append(Ain[0, i])
                        unilist.append(retorno[0, 0])
                        unilist.append(risco[0, 0])
                        unilist.append(maximum[0, 0])
                        #print(unilist)
                        writer.writerow(unilist)
                        unilist.clear()
                    else:
                        for i in range(self.num_column):
                            unilist.append(Ain[0, i])
                        unilist.append(retorno[0, 0])
                        unilist.append(risco[0, 0])
                        unilist.append(maximum[0, 0])
                        #print(unilist)
                        writer.writerow(unilist)
                        unilist.clear()
        file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv'
        df = pd.read_csv(file_name, engine='python')

        #df.columns = ['A1', 'A2', 'A3', 'Retorno', 'Risco', 'Maximum']
        #df.columns = self.columns_name
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
        file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv'
        df = pd.read_csv(file_name, engine='python')
        #df.columns = self.columns_name
        df = df.sort_values(['Maximum'], ascending=False)
        #investido = 10000

        total = 0.0
        parce = 1.0

        # Efetuando o cálculo de juros compostos sobre o capital investido
        for p in self.investimento_min:
            for i in self.lista_best_10:
                if parce == 1:
                    parce = p * (1 + (i/100))
                else:
                    parce *= (1 + (i / 100))
            total += parce
            parce = 1
        print(f'Ganho total real R${total:.2f}')
        retorno = (total - self.total_invest) / (self.total_invest)
        print(f'Retorno real {retorno*100:.2f}%')
        #print(df.iloc[self.linha, self.An])
        if capMax != 0:
            desvio = np.array([retorno*100, df.iloc[self.linha, self.An]])
        else:
            desvio = np.array([retorno * 100, df.iloc[0, self.An]])
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
        file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv'
        df = pd.read_csv(file_name, engine='python')
        #df.columns = self.columns_name
        df = df.sort_values(['Maximum'], ascending=False)

        if self.capMax == 0:

            with self.mutex:
                # Cria o problema
                prob = LpProblem('Investimento Mínimo', LpMinimize)

                # Cria as variáveis
                '''
                x1 = LpVariable('a1', 0)
                x2 = LpVariable('a2', 0)
                x3 = LpVariable('a3', 0)
                '''
                # Dando nome às variáveis
                if self.num_column >= self.An:
                    name_var = [LpVariable(n, 0) for n in self.columns_name[:self.An]]
                else:
                    name_var = [LpVariable(n, 0) for n in self.columns_name[:self.num_column]]
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
                if self.num_column >= self.An:
                    for i in range(0, self.An):
                        prob += name_var[i]*self.cota[i] >= df.iloc[0, i], f'Quantidade {i}'
                else:
                    for i in range(0, self.num_column):
                        prob += name_var[i]*self.cota[i] >= df.iloc[0, i], f'Quantidade {i}'

                # Escreve o modelo no arquivo
                prob.writeLP('Minimize_Invest.lp')

                # Resolve o problema
                prob.solve()

                # imprime o status da resolução
                #print(f'Status: {LpStatus[prob.status]}')

                # Soluções ótimas das variáveis (quantidades)
                list_var = []
                for variable in prob.variables():
                    #print(f'{variable.name} = {variable.varValue}')
                    list_var.append(variable.varValue)

                # Objetivo otimizado
                #print(f'A quantidade de cota de cada ativo é:{prob.objective}')
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
                self.valores = [round(x*coeficiente) for x in list_var]
                print(self.best_name)
                # Valor de cada papel
                print(self.cota)
                # Valor gasto em cada cota/papel
                self.investimento_min = [self.cota[i]*v for i, v in enumerate(self.valores)]
                # Valor total a ser investido
                self.total_invest = reduce(lambda a, b: a+b, self.investimento_min)
                if self.num_column >= self.An:
                    print(f'Retorno:{df.iloc[0, self.An]:.2f}, Risco:{df.iloc[0, self.An + 1]:.2f}, Maximum:{df.iloc[0, self.An + 2]:.2f}')
                else:
                    print(f'Retorno:{df.iloc[0, self.num_column]:.2f}, Risco:{df.iloc[0, self.num_column + 1]:.2f}, Maximum:{df.iloc[0, self.num_column + 2]:.2f}')
                print(f'A quantidade de cota de cada ativo é:\n{self.valores}')
                print(self.investimento_min)
                print(f'R${self.total_invest:.2f}')
                # Valor total do dividendo
                vec_valor = np.array(self.valores)
                vec_dividendo = np.array(self.dividendo)
                self.total_dividendo = vec_valor.dot(vec_dividendo.T)
                print(f'A soma dos dividendos é: R${self.total_dividendo:.2f}')

                # SHELVE PARA GUARDAR OS DADOS
                db_shelve = shelve.open('Invest.db')
                db_shelve['nomes'] = self.best_name
                db_shelve['qnt_cotas'] = self.valores
                db_shelve['valorPapel'] = self.cota
                db_shelve['investimento_min'] = self.investimento_min
                db_shelve['totalInvest'] = self.total_invest
                db_shelve['somaDividendo'] = self.total_dividendo
                db_shelve['columns_name'] = self.columns_name
                db_shelve.close()
        else:
            # (self.linha): Conta a linha na qual encontraremos o valor satisfatório
            self.linha = 0

            while True:
                with self.mutex:
                    # Cria o problema
                    prob = LpProblem('Investimento Mínimo', LpMinimize)

                    # Cria as variáveis
                    '''
                    x1 = LpVariable('a1', 0)
                    x2 = LpVariable('a2', 0)
                    x3 = LpVariable('a3', 0)
                    '''
                    # Dando nome às variáveis
                    if self.num_column >= self.An:
                        name_var = [LpVariable(n, 0) for n in self.columns_name[:self.An]]
                    else:
                        name_var = [LpVariable(n, 0) for n in self.columns_name[:self.num_column]]
                    # Colocando as variáveis e os valores das cotas numa array
                    matriz_var = np.array(name_var)
                    matriz_cota = np.array(self.cota)

                    # Cria Função Objetivo
                    # prob += (x1 * self.cota[0]) + (x2 * self.cota[1]) + (x3 * self.cota[2]), 'Investimento'
                    prob += matriz_var.dot(matriz_cota.T)

                    # Restrições
                    if self.num_column >= self.An:
                        for i in range(0, self.An):
                            prob += name_var[i] * self.cota[i] >= df.iloc[self.linha, i]#, f'Quantidade {i+n}'
                    else:
                        for i in range(0, self.num_column):
                            prob += name_var[i] * self.cota[i] >= df.iloc[self.linha, i]  # , f'Quantidade {i+n}'

                    # Escreve o modelo no arquivo
                    prob.writeLP('Minimize_Invest.lp')

                    # Resolve o problema
                    prob.solve()

                    # imprime o status da resolução
                    #print(f'Status: {LpStatus[prob.status]}')

                    # Soluções ótimas das variáveis (quantidades)
                    list_var = []
                    for variable in prob.variables():
                        #print(f'{variable.name} = {variable.varValue}')
                        list_var.append(variable.varValue)

                    # Objetivo otimizado
                    #print(f'A quantidade de cota de cada ativo é:{prob.objective}')
                    # print(list_var)

                    # Determinando as quantidades de cada papel
                    array_var = np.array(list_var)
                    menor_var = array_var.min()
                    '''
                    Para descobrir a quantidade de cada ativo pega-se o menor valor das variáveis encontrado pela PO
                    e calcula-se qual número multiplicado por ele é igual a 1, para atribuir uma unidade ao ativo em
                    questão, em seguida multiplica-se esse coeficiente aos demais valores encontrando assim as quantidades
                    de cada ativo.
                    '''
                    coeficiente = 1 / menor_var
                    # Quantidade de cada cota/papel
                    self.valores = [round(x * coeficiente) for x in list_var]
                    # Valor de cada papel
                    #print(self.cota)
                    # Valor gasto em cada cota/papel
                    self.investimento_min = [self.cota[i] * v for i, v in enumerate(self.valores)]

                    # Valor total a ser investido
                    self.total_invest = reduce(lambda a, b: a + b, self.investimento_min)
                    #print(valores)
                    #print(investimento_min)
                    #print(f'R${total_invest:.2f}')

                    # CONDIÇÃO PARA SATISFAZER CAPITAL MÍNIMO INVESTIDO
                    if self.total_invest <= capMax:

                        # CONDIÇÃO PARA CAPITAL INICIAL ELEVADO
                        qtd = self.capMax // self.total_invest
                        if qtd > 1:
                            self.valores = [x * qtd for x in self.valores]
                            self.investimento_min = [self.cota[i] * v for i, v in enumerate(self.valores)]
                            # Novo valor total
                            self.total_invest = reduce(lambda a, b: a + b, self.investimento_min)
                        else:
                            pass

                        print(self.best_name)
                        # Valor de cada papel
                        print(self.cota)
                        #porcent = []
                        #for i in range(self.An):
                        #    porcent.append(df.iloc[self.linha, i] * 100)
                        #print(porcent)
                        if self.num_column >= self.An:
                            print(f'Retorno:{df.iloc[self.linha, self.An]:.2f}, Risco:{df.iloc[self.linha, self.An + 1]:.2f}, Maximum:{df.iloc[self.linha, self.An + 2]:.2f}')
                        else:
                            print(f'Retorno:{df.iloc[self.linha, self.num_column]:.2f}, Risco:{df.iloc[self.linha, self.num_column + 1]:.2f}, Maximum:{df.iloc[self.linha, self.num_column + 2]:.2f}')
                        print(f'A quantidade de papéis de cada ativo é:\n{self.valores}')
                        print(self.investimento_min)
                        print(f'R${self.total_invest:.2f}')
                        # Valor total do dividendo
                        vec_valor = np.array(self.valores)
                        vec_dividendo = np.array(self.dividendo)
                        self.total_dividendo = vec_valor.dot(vec_dividendo.T)
                        print(f'A soma dos dividendos é: R${self.total_dividendo:.2f}')

                        # SHELVE PARA GUARDAR OS DADOS
                        db_shelve = shelve.open('Invest.db')
                        db_shelve['nomes'] = self.best_name
                        db_shelve['qnt_cotas'] = self.valores
                        db_shelve['valorPapel'] = self.cota
                        db_shelve['investimento_min'] = self.investimento_min
                        db_shelve['totalInvest'] = self.total_invest
                        db_shelve['somaDividendo'] = self.total_dividendo
                        db_shelve['columns_name'] = self.columns_name
                        db_shelve['linha'] = self.linha
                        db_shelve.close()

                        break

                    else:
                        self.linha += 1
                        pass

    def saveInvest(self):

        hoje = date.today()

        # DECLARANDO LOCAL PARA SALVAR INVESTIMENTO
        if os.path.exists(f'/Users/milso/OneDrive/Cursos Python/MONETA/Investimentos/Investimento_{self.meses}_meses_{self.kind}_{self.An}papeis_{hoje}.csv'):
            os.remove(f'/Users/milso/OneDrive/Cursos Python/MONETA/Investimentos/Investimento_{self.meses}_meses_{self.kind}_{self.An}papeis_{hoje}.csv')
        with open(f'/Users/milso/OneDrive/Cursos Python/MONETA/Investimentos/Investimento_{self.meses}_meses_{self.kind}_{self.An}papeis_{hoje}.csv', 'w', newline='') as dados:
            writer = csv.writer(dados)

            lista = []
            lista.append(self.total_invest)
            if self.num_column >= self.An:
                colName = [x for x in range(self.An)]
            else:
                colName = [x for x in range(self.num_column)]
            if self.capMax == 0:
                writer.writerow(colName)
                writer.writerow(self.best_name) #Nome de cada papel
                writer.writerow(self.cota) #Valor de cada cota
                writer.writerow(self.valores) #Qnt de cotas de cada papel
                writer.writerow(self.investimento_min) #Qnt investida em cada papel
                #writer.writerow(lista) # Total investido
                #writer.writerow(df.iloc[0, 0:]) #Qnt investida antes do cálculo da PO
            else:
                writer.writerow(self.best_name)
                writer.writerow(self.cota)
                writer.writerow(self.valores)
                writer.writerow(self.investimento_min)
                #writer.writerow(lista)
                #writer.writerow(df.iloc[self.linha, 0:])

    def comparaInvest(self):

        #ABRINDO O ARQUIVO DO INVESTIMENTO EFETUADO
        #openFile = f'/Users/milso/OneDrive/Cursos Python/MONETA/Investimentos/Investimento_{self.meses}_meses_{self.kind}_{self.An}papeis_2019-06-17.csv'
        #openFile = f'/Users/milso/OneDrive/Cursos Python/MONETA/Investimentos/Investimento_6_meses_mensal_14papeis_2019-06-06.csv'
        openFile = self.path_salvo
        df_Open = pd.read_csv(openFile, sep=';', engine='python')
        #Transpondo a dataframe
        df_Open = df_Open.T
        print(df_Open)

        self.contem = []
        self.indice = []
        self.naoContem = []

        self.comprar = []
        self.vender = []
        self.vender_all = []
        self.manter = []

        #VERIFICANDO OS PAPÉIS COINCIDENTES

        # c é o índice da coluna dos dados salvos
        #for c, i in enumerate(df_Open.iloc[0, 0:]):
        # l é o índice da linha dos dados salvos
        for l, i in enumerate(df_Open.iloc[0, 0:]):
            if i in self.best_name:
                #Contem é o índice da coluna dos dados salvos(Carteira atual)
                self.contem.append(l)
                for v, b in enumerate(self.best_name):
                    if i == b:
                        #indice é o índice da coluna dos ativos da nova carteira
                        self.indice.append(v)
            else:
                self.naoContem.append(l)

        #SHELVE PARA ARMAZENAR OS DADOS
        db = shelve.open('ComparaInvest.db')
        # Calculando a quantidade a ser comprada e vendida
        for i in range(len(self.contem)):
            #Cálculo para saber a quantidade de cada papel temos atualmente
            #cotaAtual = round(df_Open.iloc[3, i]/self.cota[self.indice[i]]) #O valor investido em cada papel dividido pelo valor atual da cota
            cota_now = self.valores[self.indice[i]]
            cota_before = float(df_Open.iloc[1, self.contem[i]])
            valor = cota_now - cota_before
            #valor = df_Open.iloc[2, i] - self.valores[self.indice[i]]

            if valor >= 1:
                print(f'Comprar {valor} do papel {df_Open.iloc[0, self.contem[i]]} a R${self.cota[i]}')
                self.comprar.append([valor, df_Open.iloc[0, self.contem[i]], self.cota[i]])
            elif valor < 1 and valor != 0:
                print(f'Vender {-valor} do papel {df_Open.iloc[0, self.contem[i]]} a R${self.cota[i]}')
                self.vender.append([-valor, df_Open.iloc[0, self.contem[i]], self.cota[i]])
            else:
                print(f'Manter a quantidade atual do papel {df_Open.iloc[0, self.contem[i]]}')
                self.manter.append(df_Open.iloc[0, self.contem[i]])
        db['vender'] = self.vender
        db['manter'] = self.manter
        self.vender.clear()
        self.manter.clear()

        #PAPÉIS QUE NÃO CONTÉM NA NOVA CARTEIRA SERÃO VENDIDOS
        for i in self.naoContem:
            print(f'Vender o papel {df_Open.iloc[0, i]}')
            self.vender_all.append(df_Open.iloc[0, i])
        db['vender_all'] = self.vender_all

        #PAPÉIS QUE NÃO ESTAVAM NA CARTEIRA ANTIGA E SERÃO COMPRADOS
        conteudo = [l for l in (df_Open.iloc[0, 0:])]
        for c, i in enumerate(self.best_name):
            if i not in conteudo:
                print(f'Comprar {self.valores[c]} do papel {self.best_name[c]} a R${self.cota[c]}')
                self.comprar.append([self.valores[c], self.best_name[c], self.cota[c]])
        db['comprar'] = self.comprar
        db.close()

    def plot(self):
        if self.capMax == 0:
            file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv'
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
            if self.num_column >= self.An:
                for i in range(self.An):
                    porcent.append(df.iloc[0, i] * 100)
            else:
                for i in range(self.num_column):
                    porcent.append(df.iloc[0, i] * 100)
            sizes = porcent
            # explode = (0, 0, 0.1)
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, autopct='%1.1f%%', shadow=False, textprops=dict(color='w'),
                    startangle=90)  # , labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            ax1.legend(labels, title='Papéis', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            ax1.set_title('Composição da Carteira')
            # ax1.axis('equal')

            plt.show()

        else:
            file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv'
            df = pd.read_csv(file_name, engine='python')
            df.columns = self.columns_name
            df = df.sort_values(['Maximum'], ascending=False)
            # df.plot('Risco', 'Retorno') #(x,y)
            # plt.plot(df['Risco'], df['Retorno'], 'ro')

            # Gráfico de dispersão de Markovit
            plt.scatter(df['Risco'], df['Retorno'], alpha=0.5, c=df['Risco'])
            # plt.legend()
            plt.title('Gráfico do retorno ótimo de Markowitz')
            plt.xlabel('Risco')
            plt.ylabel('Retorno')

            # Gráfico de pizza das porcentagens

            # Recuperando a linha
            db = shelve.open('Invest.db')
            linha = db['linha']
            db.close()
            labels = self.best_name
            porcent = []
            if self.num_column >= self.An:
                for i in range(self.An):
                    porcent.append(df.iloc[linha, i] * 100)
            else:
                for i in range(self.num_column):
                    porcent.append(df.iloc[linha, i] * 100)
            sizes = porcent
            # explode = (0, 0, 0.1)
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, autopct='%1.1f%%', shadow=False, textprops=dict(color='w'),
                    startangle=90)  # , labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            ax1.legend(labels, title='Papéis', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            ax1.set_title('Composição da Carteira')
            # ax1.axis('equal')

            plt.show()

    def plotPizza(self):
        if self.capMax == 0:
            file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv'
            df = pd.read_csv(file_name, engine='python')
            df.columns = self.columns_name
            df = df.sort_values(['Maximum'], ascending=False)

            # Gráfico de pizza das porcentagens
            labels = self.best_name
            porcent = []
            for i in range(self.An):
                porcent.append(df.iloc[0, i] * 100)
            sizes = porcent
            # explode = (0, 0, 0.1)
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, autopct='%1.1f%%', shadow=False, textprops=dict(color='w'), startangle=90)#, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            ax1.legend(labels, title='Papéis', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            ax1.set_title('Composição da Carteira')
            #ax1.axis('equal')
            plt.show()

        else:
            file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{self.meses}_meses_{self.kind}_{self.An}papeis.csv'
            df = pd.read_csv(file_name, engine='python')
            df.columns = self.columns_name
            df = df.sort_values(['Maximum'], ascending=False)

            # Gráfico de pizza das porcentagens
            labels = self.best_name
            porcent = []
            for i in range(self.An):
                porcent.append(df.iloc[self.linha, i] * 100)
            sizes = porcent
            # explode = (0, 0, 0.1)
            fig1, ax1 = plt.subplots()
            #ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            #ax1.axis('equal')
            ax1.pie(sizes, autopct='%1.1f%%', shadow=False, textprops=dict(color='w'), startangle=90)
            ax1.legend(labels, title='Papéis', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            ax1.set_title('Composição da Carteira')

            plt.show()

'''
fonte: https://blog.rico.com.vc/fundos-imobiliarios
Comparativo de rentabilidade dos Fundos Imobiliários

Vamos utilizar dois exemplos de fundos.

O primeiro tem o valor da cota em R$ 120,00. Os aluguéis foram de R$ 1,20 por cota. 
Ao dividir, 1,20/ 120,  a sua rentabilidade foi de 1%.
'''

if __name__ == '__main__':
    stdoutmutex = threading.Lock()
    threads = []
    fixos = ['']
    papeis = 15
    #kind = 'mensal'
    #kind = 'diario'
    kind = 'semanal'
    meses = 6
    iter = 1000000
    capMax = float(5200)
    pvpmin = 0.0
    pvpmax = 0.0
    liquidez = 300000.0
    preco_suporte = 1.2
    path_salvo = f'/Users/milso/OneDrive/Investimento/Carteira atual/Exportar_custodia_2019-09-05.csv'
    bob = Calculo(papeis, meses, kind, iter, stdoutmutex, capMax, pvpmin, pvpmax, liquidez, preco_suporte, fixos, path_salvo)
    bob.selectAtivos()
    # Ativar quando quiser ver acertividade e comentar bob.selectAtivos
    #bob.selectAtivosAcertivo()
    #bob.solve()
    bob.start()
    threads.append(bob)
    for thread in threads:
        thread.join()

    # Implementando threading para o PO
    threadPO = threading.Thread(target=bob.quantAtivos())#, args=(capMax,))
    threadPO.daemon = True
    threadPO.start()
    threads.clear()
    threads.append(threadPO)
    for thread in threads:
        thread.join()
    # PARA VERIFICAR A ACERTIVIDADE
    #bob.ganhoReal()
    bob.comparaInvest()
    # Obtendo o tempo de execução:
    duracao = round((perf_counter()), 0)
    horas = int(duracao // 3600)
    minutos = int(round((duracao / 3600 - duracao // 3600) * 60, 0))
    segundos = int(round((duracao % 60), 0))
    print(f'Tempo de execução:{horas}:{minutos}:{segundos}')
    #bob.plotPizza()
    bob.plot()
    #ALTEREI O MAXIMUM RETIRANDO O RETORNO!!!!!!!!!!!
    resp_salve = input(str('Deseja salvar a simulação? S/N'))
    if resp_salve in 'Ss':
        bob.saveInvest()

    #print(f'Tempo de execução:{process_time()} segundos')