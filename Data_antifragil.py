# -*- coding: utf-8 -*-
from B3_Reader import *
#from time import process_time, perf_counter

#lxml ← para parsear(fazer a análise sintática)
#  o html e extrair as informações desejadas;

import lxml.html as parser

#requests ← para realizar nossas requisições,
# pode ser substituída por qualquer pacote similar;

import requests
from time import process_time, perf_counter, struct_time, localtime
from time import time as tm
import csv
import pandas as pd
import pandas_market_calendars as mark
import os.path
from numpy import *
import sys
from datetime import date, time, datetime, timedelta
import monthdelta
import threading
import shelve
from tqdm import tqdm_gui
from tqdm import tqdm
from random import random, randint
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import (QApplication, QProgressBar, QWidget)
from scipy import interpolate

class WebScraping(threading.Thread):#threading.Thread, QThread):
    #valueChanged = pyqtSignal(int)

    def __init__(self, meses, kind, short, long, descartados, path_old, path_now, mutex):

        self.meses = meses
        self.kind = kind
        self.short = short
        self.long = long
        self.descartados = descartados
        self.path_old = path_old
        self.path_now = path_now
        self.mutex = mutex
        threading.Thread.__init__(self)
        #QThread.__init__(self)

    def time(self):

        # Obtendo o calendário da BM&F bovespa
        bmf = mark.get_calendar('BMF')

        # CONDIÇÃO PARA DIAS VÁLIDOS
        if date.today() in bmf.valid_days(date.today(), date.today()):
            # OBTENDO OS DADOS DO DIA ANTERIOR

            # Obtendo a data de hoje
            hoje = date.today()
            # VERIFICANDO O DIA DA SEMANA
            # Se for diferente de segunda-feira
            if localtime(tm()).tm_wday != 0:
                ontem = hoje - timedelta(1)
            # Se for segunda-feira o dia anterior será sexta-feira, por isso 3 dias antes
            else:
                ontem = hoje - timedelta(3)
            self.dia = ontem.day
            self.mes = hoje.month
            self.ano = hoje.year
            # print(hoje)

            # Subtraindo os meses para obter a data inicial
            data_i = ontem - monthdelta.monthdelta(self.meses) #MonthDelta(self.meses)
            self.dia_i = data_i.day
            self.mes_i = data_i.month
            self.ano_i = data_i.year
            # print(data_i)

            # Obtendo a lista dos dias válidos
            self.lista_dias = bmf.valid_days(data_i, ontem)
            self.dias = len(self.lista_dias)

        #PARA DIAS NÃO ÚTEIS, INCLUSIVE CONSIDERANDO FERIADOS
        else:
            hoje = date.today()
            data_i = hoje - monthdelta.monthdelta(self.meses)
            intervalo = bmf.valid_days(data_i, hoje)
            # Obtendo último dia válido
            ultima_data = intervalo[-1]

            self.dia = ultima_data.day
            self.mes = ultima_data.month
            self.ano = ultima_data.year
            # print(hoje)

            # Subtraindo os meses para obter a data inicial
            data_i = ultima_data - monthdelta.monthdelta(self.meses)
            self.dia_i = data_i.day
            self.mes_i = data_i.month
            self.ano_i = data_i.year
            # print(data_i)

            # Obtendo a lista dos dias válidos
            self.lista_dias = bmf.valid_days(data_i, ultima_data)
            self.dias = len(self.lista_dias)
            # print(len(self.dias))

    # OBTENDO AS LISTAS DE FUNDOS IMOBILIÁRIOS

    # Acessando o site/endereço
    def listaFundos(self):
        #start_url = 'https://www.infomoney.com.br/imoveis/fundos-imobiliarios/cotacoes' original
        start_url = 'https://www.fundsexplorer.com.br/funds'
        r = requests.get(start_url)
        html = parser.fromstring(r.text)

        # Selecionando os dados da tabela (fundos)

        fundos = html.xpath("//div[@class='tickerBox__title']/text()")
        #print(fundos)
        #print(len(fundos))
        # Configurando a lista de fundos
        n = 0
        self.list_fundos = []
        for fundo in fundos:
            if fundo[-1] == 'B':
                n = len(fundo)
                fundo = fundo[0:(n-1)]
                #self.list_fundos.append(fundo[1:])
                #Filtrando os fundos descartados
                if fundo not in self.descartados:
                    self.list_fundos.append(fundo)
                else: pass
            else:
                #self.list_fundos.append(fundo[1:])
                if fundo not in self.descartados:
                    self.list_fundos.append(fundo)
                else: pass
        if len(self.descartados) == 0:
            fundos_shelve = shelve.open('ListaFundos.db')
            fundos_shelve['list_fundos'] = self.list_fundos
            fundos_shelve.close()

        return (self.list_fundos)
        #print(self.list_fundos)

    def listaAcoes(self):
        self.listaAcao = []
        # Carregando banco de dados: parse_dataset pertence à biblioteca B3_Reader
        self.dadosAcao = parse_dataset(self.path_now)
        # CRIANDO AS DATAFRAME COM OS BANCOS DE DADOS
        df_acao = pd.DataFrame(translate_bdi(self.dadosAcao))
        # FILTRANDO OS DATAFRAMES
        #df_acao_filtro = df_acao[(df_acao.iloc[0:, 6] == 'ON') & (df_acao.iloc[0:, 4] == 'VISTA')]# & (df_acao.iloc[0:, 1] == '20190102')]
        #print(df_acao_filtro.iloc[0, 1:9])
        for x in df_acao.iloc[0:, 3].sort_values(ascending=True):
            if x not in self.listaAcao and x[4] == '3' and len(x) == 5:
                self.listaAcao.append(x)
            else: pass
        print(self.listaAcao)
        print(len(self.listaAcao))

    # Selecionando as cotações
    def run(self):#antigo dadosCotacoes

        self.dados_fundos= []

        # DIVIDINDO O BANCO DE DADOS POR PERÍODO DE TEMPO
        self.unilist = []
        self.list_csv = []
        self.cota = []
        self.variacao = []
        self.lastPrice = []
        #Carregando banco de dados: parse_dataset pertence à biblioteca B3_Reader
        self.banco18 = parse_dataset(self.path_old)  # Loads dataset into pandas dataframe
        self.banco19 = parse_dataset(self.path_now)  # Loads dataset into pandas dataframe
        # print(translate_bdi(x))  # Translates BDI Codes and returns pandas df mofied
        # print(market_type(x))  # Translates market_types Codes and returns pandas df mofied
        # print(price_mod(x))  # Returns price fields formated as currency
        # CRIANDO AS DATAFRAME COM OS BANCOS DE DADOS
        df_18 = pd.DataFrame(translate_bdi(self.banco18))
        df_19 = pd.DataFrame(translate_bdi(self.banco19))
        #print(type(df_19.iloc[0:, 3]))
        with tqdm(total=len(self.list_fundos)) as self.pbar:
            #for Count, fundo in enumerate(self.list_fundos):
            for fundo in self.list_fundos:
                #Count += 1
                passa = 0
                # FILTRANDO OS DATAFRAMES
                #Verificando se contém o fundo no banco de dados
                try:
                    data_filtro18 = df_18[df_18.iloc[0:, 3] == fundo]
                    data_filtro19 = df_19[df_19.iloc[0:, 3] == fundo]

                    if data_filtro18.iloc[1, 3] == '' or data_filtro19.iloc[1, 3] == '':
                        raise ValueError
                    else: pass

                except:
                    passa = 1
                    pass
                #with self.mutex:
                if passa != 1:
                    # Obtendo somente a última cotação(preço de fechamento do dia anterior)obs: a linha é (-1) porque o último dia está na última linha
                    self.cota.append(data_filtro19.iloc[-1, 13])

                    # Obtendo todas as variações do período
                    # Variações no ano atual
                    for i in range(1, len(data_filtro19.iloc[0:, 0])+1):
                        self.variacao.append(((data_filtro19.iloc[-i, 13]/data_filtro19.iloc[-i, 9])-1)*100)
                        if i <= self.long+1:
                            self.lastPrice.append(data_filtro19.iloc[-i, 13])

                        if len(self.variacao) == self.dias:
                            break
                    # Variações do ano passado (Para complementar, caso não atinja o número de dias)
                    if len(self.variacao) < self.dias:
                        for i in range(1, len(data_filtro18.iloc[0:, 0])+1):
                            self.variacao.append(((data_filtro18.iloc[-i, 13]/data_filtro18.iloc[-i, 9])-1)*100)

                            if len(self.variacao) == self.dias:
                                break
                    with self.mutex:
                        i = requests.get(f'https://www.fundsexplorer.com.br/funds/{fundo}')
                        html3 = parser.fromstring(i.text)
                        # Obtendo o tipo de fundo
                        try:
                            tfundo = html3.xpath(
                                "/html/body/div[2]/section[13]/div/div/div[6]/p[2]/b/text()")
                        except:
                            tfundo = "Indefinido"
                        # Obtendo o valor do aluguel pago por cota
                        # vfundo = html3.xpath("//div[@class='col-md-12 col-xs-12']//div[@class='carousel-cell'][3]/span[@class='indicator-value']/text()")
                        # Obtendo a liquidez diária
                        liqDay = html3.xpath("/html/body/div[2]/section[2]/div/div[1]/p[2]/b/text()")
                        # Obtendo P_VP
                        pvp = html3.xpath("/html/body/div[2]/section[2]/div/div[7]/p[2]/b/text()")
                        # Site para obter os dividendos
                        # w = requests.get(f'https://www.meusdividendos.com/fundo-imobiliario/{fundo.replace("11", "").strip().upper()}')
                        # html4 = parser.fromstring(w.text)
                        # Obtendo valor anual dos dividendos
                        # vdividendo = html4.xpath("//div[@style='text-align:center;']//span/text()")
                        vdividendo = html3.xpath("/html/body/div[2]/section[6]/div/div[3]/div[1]/p[2]/b/text()")
                        # print('-'*20, 'Dados dos dividendos', '-'*20)
                        # print(dividendo)
                        # Inserindo os dados nas demais linhas
                        # Resumindo tudo numa só lista
                        # print(len(self.variacao))

                        if len(self.variacao) == self.dias:
                            self.unilist.append(fundo)
                            # tipo do fundo
                            for j in tfundo:
                                self.unilist.append(j.replace('"', '').strip())
                            # Valor do dividendo Anual
                            try:
                                if len(vdividendo[0]) != '' or len(vdividendo[0]) != 'N/A':
                                    self.unilist.append(float(vdividendo[0].replace(',', '.')))
                                else:
                                    self.unilist.append(0.0)
                            except ValueError:
                                self.unilist.append(0.0)

                            # Inserindo o valor do Papel na unilist
                            self.unilist.append(self.cota[0])
                            self.cota.clear()

                            # Adicionando a liquidez diária
                            try:
                                if "K" in liqDay[0]:
                                    self.unilist.append(float(liqDay[0].replace(',', '.').replace('K', ''))*1000)
                                elif "M" in liqDay[0]:
                                    self.unilist.append(float(liqDay[0].replace(',', '.').replace('M', '')) * 1000000)
                                else:
                                    self.unilist.append(float(liqDay[0].replace(',', '.')))
                            except ValueError:
                                self.unilist.append(0)
                            # Adicionando o p/vp, importante para ver se vale a pena comprar o papel
                            try:
                                self.unilist.append(float(pvp[0].replace(',', '.')))
                            except ValueError:
                                self.unilist.append(0)

                            # INSERINDO O RISCO
                            # CONVERTENDO A VARIAÇÃO(f(x)) PARA ARRAY
                            varia = [float(x) for x in self.variacao]
                            var = array(varia)
                            # CALCULANDO A MÉDIA DA FUNÇÃO
                            media_func = var.mean()
                            # OBTENDO A MÉDIA DO INTERVALO
                            inter = [x for x in range(1, len(self.variacao)+1)]
                            media_inter = array(inter).mean()
                            # OBTENDO A FUNÇÃO DA MÉDIA
                            radFunc = interpolate.Rbf(inter, var, function='gaussian')
                            funcMean = radFunc(media_inter)
                            # Inserindo o "Risco"
                            self.unilist.append(funcMean/media_func)

                            # FAZENDO AS MÉDIAS MÓVEIS
                            array_short = array([float(y) for y in self.lastPrice[0:self.short]])
                            array_short_desloc = array([float(y) for y in self.lastPrice[1:self.short+1]])
                            array_long = array([float(z) for z in self.lastPrice[0:self.long]])
                            array_long_desloc = array([float(z) for z in self.lastPrice[1:self.long+1]])
                            #print(array_short.shape, array_long.shape, array_short_desloc.shape, array_long_desloc.shape)
                            # ARMAZENANDO AS MÉDIAS COM INDICAÇÃO DE ALTA(+) OU BAIXA(-)
                            if array_short.mean() < array_short_desloc.mean():
                                self.unilist.append(array_short.mean()*-1)
                            else:
                                self.unilist.append(array_short.mean())
                            if array_long.mean() < array_long_desloc.mean():
                                self.unilist.append(array_long.mean()*-1)
                            else:
                                self.unilist.append(array_long.mean())
                            self.lastPrice.clear()
                            # SE A ANÁLISE FOR DIÁRIA, COLETAR OS DADOS NORMALMENTE
                            if self.kind == 'diario':
                                for i in self.variacao:
                                    self.unilist.append(float(i))  # .replace(',', '.')))
                                self.variacao.clear()
                                self.list_csv.append(self.unilist[:])
                                self.unilist.clear()
                                self.pbar.update(1)
                                # self.valueChanged.emit(Count)
                            # SE A ANÁLISE FOR MENSAL, CALCULAR A VARIAÇÃO MENSAL DO FUNDO
                            else:
                                # DIVIDINDO OS DADOS EM MESES
                                lista_qnts = []
                                n, now = 0, 0
                                for c, m in enumerate(self.lista_dias.month):
                                    if c == 0:
                                        now = m
                                        n += 1
                                    else:
                                        if now == m and c != len(self.lista_dias) - 1:
                                            n += 1
                                        elif now != m and c != len(self.lista_dias) - 1:
                                            now = m
                                            lista_qnts.append(n)
                                            n = 1
                                        else:
                                            n += 1
                                            lista_qnts.append(n)
                                # Invertendo a lista, deixando a data recente no começo da lista
                                list_normal = lista_qnts[::-1]

                                # Algoritmo para somar as variações deixando-as mensais
                                i, soma, c = 0, 0, 1
                                for v in self.variacao:
                                    if c <= list_normal[i]:
                                        soma += float(v)  # .replace(',', '.'))
                                        c += 1
                                    else:
                                        self.unilist.append(soma)
                                        soma, c = 0, 2
                                        soma += float(v)  # .replace(',', '.'))
                                        i += 1
                                self.variacao.clear()
                                self.list_csv.append(self.unilist[:])
                                self.unilist.clear()
                                self.pbar.update(1)
                                # self.valueChanged.emit(Count)
                        else:
                            self.cota.clear()
                            self.variacao.clear()
                            self.pbar.update(1)
                            # self.valueChanged.emit(Count)
                            continue
                else:
                    self.pbar.update(1)
                    #self.valueChanged.emit(Count)
                    pass


        return self.list_csv

    def dadosSelect(self):

        # Verificando se o arquivo existe
        if os.path.exists(f'E:/OneDrive/Cursos Python/MONETA/Dados/Dados_AntiFragil_{self.meses}_meses.csv'):
            os.remove(f'E:/OneDrive/Cursos Python/MONETA/Dados/Dados_AntiFragil_{self.meses}_meses.csv')
        with open(f'E:/OneDrive/Cursos Python/MONETA/Dados/Dados_AntiFragil_{self.meses}_meses.csv', 'w', newline='') as dados:
            writer = csv.writer(dados)
            col_name = list(range(0, len(self.list_csv[0])))
            #print(col_name)
            writer.writerow(col_name)
            for d in self.list_csv:  # obj.dadosCotacoes():
                writer.writerow(d)
        # Lendo a tabela com PANDAS Dataframe
        # df = pd.read_table('/Users/milso/Desktop/MONETA/Dados_Papeis.csv', 'utf-8')
        #df = pd.read_csv(f'E:/OneDrive/Cursos Python/MONETA/Dados/Dados_AntiFragil_{self.meses}_meses.csv', engine='python')
        df = pd.read_csv(f'E:/OneDrive/Cursos Python/MONETA/Dados/Dados_AntiFragil_{self.meses}_meses.csv', encoding='ISO-8859-1')
        print(df)

if __name__ == '__main__':
    meses = 12
    #kind = 'diario'
    kind = 'semanal'
    short = 9
    long = 21
    stdoutmutex = threading.Lock()
    threads = []
    descartados = ['HFOF11', 'BBVJ11', 'MGFF11', 'LVBI11']
    path_old = 'E:\OneDrive\Investimento\COTAHIST\COTAHIST_A2022.TXT'
    path_now = 'E:\OneDrive\Investimento\COTAHIST\COTAHIST_A2023.TXT'
    obj = WebScraping(meses, kind, short, long, descartados, path_old, path_now, stdoutmutex)
    obj.time()
    #obj.listaAcoes()
    obj.listaFundos()
    #obj.dadosCotacoes()
    obj.start()
    threads.append(obj)
    for thread in threads:
        thread.join()
    obj.dadosSelect()
    # Obtendo o tempo de execução:
    #print(f'Tempo de execução:{process_time()} segundos')
    #print(f'Tempo de execução:{perf_counter()} segundos')
    duracao = round((perf_counter()), 0)
    horas = int(duracao//3600)
    minutos = int(round((duracao/3600 - duracao//3600)*60, 0))
    segundos = int(round((duracao%60), 0))
    print(f'Tempo de execução:{horas}:{minutos}:{segundos}')