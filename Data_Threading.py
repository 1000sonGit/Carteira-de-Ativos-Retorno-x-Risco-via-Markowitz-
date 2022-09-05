# Para dados em JavaScript
#from selenium import webdriver
#import os

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
import numpy as np
import sys
from datetime import date, time, datetime, timedelta
import monthdelta
import threading

class WebScraping(threading.Thread):

    def __init__(self, meses, kind, descartados,mutex):

        self.meses = meses
        self.kind = kind
        self.descartados = descartados
        self.mutex = mutex
        threading.Thread.__init__(self)

    def time(self):
        self.coef_time = 0
        # Tempo de funcionamento do B3
        ti = time(9, 45, 0)
        tf = time(17, 15, 0)
        agora = datetime.now().time()
        # Obtendo o calendário da BM&F bovespa
        bmf = mark.get_calendar('BMF')

        # CONDIÇÃO PARA DIAS VÁLIDOS
        if date.today() in bmf.valid_days(date.today(), date.today()):
            # OBTENDO OS DADOS DO DIA ANTERIOR
            if agora <= ti:
                # Obtendo a data de hoje
                hoje = date.today()
                # VERIFICANDO O DIA DA SEMANA
                # Se for diferente de segunda-feira
                if localtime(tm()).tm_wday != 0:
                    ontem = hoje - timedelta(1)
                # Se for segunda-feira o dia anterior será sexta-feira, por isso 3 dias antes
                else:
                    ontem = hoje - timedelta(3)
                #ontem = hoje.replace(day=)
                self.dia = ontem.day
                self.mes = hoje.month
                self.ano = hoje.year
                # print(hoje)

                # Subtraindo os meses para obter a data inicial
                data_i = ontem - monthdelta.MonthDelta(self.meses)
                self.dia_i = data_i.day
                self.mes_i = data_i.month
                self.ano_i = data_i.year
                # print(data_i)

                # Obtendo a lista dos dias válidos
                self.lista_dias = bmf.valid_days(data_i, ontem)
                self.dias = len(self.lista_dias)
                self.coef_time = 1
                # print(len(self.dias))

            # APÓS O HORÁRIO DE FECHAMENTO
            elif agora >= tf:
                # Obtendo a data de hoje
                hoje = date.today()
                self.dia = hoje.day
                self.mes = hoje.month
                self.ano = hoje.year
                # print(hoje)

                # Subtraindo os meses para obter a data inicial
                data_i = hoje - monthdelta.MonthDelta(self.meses)
                self.dia_i = data_i.day
                self.mes_i = data_i.month
                self.ano_i = data_i.year
                # print(data_i)

                # Obtendo a lista dos dias válidos
                self.lista_dias = bmf.valid_days(data_i, hoje)
                self.dias = len(self.lista_dias)
                # print(len(self.dias))
                self.coef_time = 2
            # Condição em que a o valor da cota está oscilando
            else:
                # Obtendo a data de hoje
                hoje = date.today()
                self.dia = hoje.day
                self.mes = hoje.month
                self.ano = hoje.year
                # print(hoje)

                # Subtraindo os meses para obter a data inicial
                data_i = hoje - monthdelta.MonthDelta(self.meses)
                self.dia_i = data_i.day
                self.mes_i = data_i.month
                self.ano_i = data_i.year
                # print(data_i)

                # Obtendo a lista dos dias válidos
                self.lista_dias = bmf.valid_days(data_i, hoje)
                #print(self.lista_dias)
                self.dias = len(self.lista_dias)
                # print(len(self.dias))
                self.coef_time = 2

        #PARA DIAS NÃO ÚTEIS, INCLUSIVE CONSIDERANDO FERIADOS
        else:
            hoje = date.today()
            data_i = hoje - monthdelta.MonthDelta(self.meses)
            intervalo = bmf.valid_days(data_i, hoje)
            # Obtendo último dia válido
            ultima_data = intervalo[-1]

            self.dia = ultima_data.day
            self.mes = ultima_data.month
            self.ano = ultima_data.year
            # print(hoje)

            # Subtraindo os meses para obter a data inicial
            data_i = ultima_data - monthdelta.MonthDelta(self.meses)
            self.dia_i = data_i.day
            self.mes_i = data_i.month
            self.ano_i = data_i.year
            # print(data_i)

            # Obtendo a lista dos dias válidos
            self.lista_dias = bmf.valid_days(data_i, ultima_data)
            self.dias = len(self.lista_dias)
            # print(len(self.dias))
            self.coef_time = 1

    # OBTENDO AS LISTAS DE FUNDOS IMOBILIÁRIOS

    # Acessando o site/endereço
    def listaFundos(self):
        #start_url = 'https://www.infomoney.com.br/imoveis/fundos-imobiliarios/cotacoes' original
        start_url = 'https://www.fundsexplorer.com.br/funds'
        r = requests.get(start_url)
        html = parser.fromstring(r.text)

        # Selecionando os dados da tabela (fundos)

        #fundos = html.xpath("//table[@class='table-general']//a/@href")
        fundos = html.xpath("//div[@id='fiis-list-container']//span[@class='symbol']/text()")
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

        return (self.list_fundos)
        #print(self.list_fundos)

    #def data_dias_uteis(data_inicial, dias):
    #    return cal.add_working_days(data_inicial, dias).strftime('%d/%m/%Y')

    # Selecionando as cotações
    def run(self): #antigo dadosCotacoes

        self.dados_fundos= []

        # DIVIDINDO O BANCO DE DADOS POR PERÍODO DE TEMPO
        self.unilist = []
        self.list_csv = []
        self.cotacoes = []
        self.variacao = []

        for fundo in self.list_fundos:
            with self.mutex:
                s = requests.get(f'http://cotacoes.economia.uol.com.br/acao/cotacoes-historicas.html?codigo={fundo}.SA&beginDay={self.dia_i}&beginMonth={self.mes_i}&beginYear={self.ano_i}&endDay={self.dia}&endMonth={self.mes}&endYear={self.ano}&size={self.dias}&page=1')
                html2 = parser.fromstring(s.text)
                # Verificando se há conteúdo no site
                self.cota = html2.xpath(f"//tbody//td[@class='ultima']/text()")
                if len(self.cota) != 0:
                    if self.coef_time == 1:
                        # Obtendo somente a última cotação
                        cotacoes_site = html2.xpath("//table[@class='tblCotacoes']/tbody/tr[1]/td[2]/text()")
                        self.cotacoes = cotacoes_site[:]
                        # Obtendo todas as variações do período
                        variacao_site = html2.xpath("//table[@class='tblCotacoes']//tbody//td[6]/text()")
                        self.variacao = variacao_site[:]

                    elif self.coef_time == 2:
                        # Obtendo a cota no campo específico do dia
                        #self.cota = html2.xpath("//tr[@class='alta']//td[@class='ultima']/text()")
                        # Obtendo o restante da cotação
                        #cotacao = html2.xpath("//table[@class='tblCotacoes']/tbody/tr[1]/td[2]/text()")
                        # unindo as cotações
                        #self.cotacoes.append(cota)
                        #self.cotacoes.append(cotacao)
                        # Obtendo a variação no campo específico do dia
                        vari = html2.xpath(f"//tbody//td[3]/text()")
                        # Obtendo o restante das variações
                        variacao_site = html2.xpath("//table[@class='tblCotacoes']//tbody//td[6]/text()")
                        self.variacao.append(vari[0])
                        for i in variacao_site:
                            self.variacao.append(i)

                    i = requests.get(f'https://www.fundsexplorer.com.br/funds/{fundo}')
                    html3 = parser.fromstring(i.text)
                    # Obtendo o tipo de fundo
                    tfundo = html3.xpath("//div[@class='col-md-6 col-xs-12'][2]/ul/li[4]/div[@class='text-wrapper']/span[@class='description']/text()")
                    # Obtendo o valor do aluguel pago por cota
                    #vfundo = html3.xpath("//div[@class='col-md-12 col-xs-12']//div[@class='carousel-cell'][3]/span[@class='indicator-value']/text()")
                    # Obtendo a liquidez diária
                    # Obtendo P_VP OBS: na posição [0] é a liquidez e na [6] o pvp
                    pvp = html3.xpath("//div[@class='col-md-12 col-xs-12']//span[@class='indicator-value']/text()")
                    # Site para obter os dividendos
                    #w = requests.get(f'https://www.meusdividendos.com/fundo-imobiliario/{fundo.replace("11", "").strip().upper()}')
                    #html4 = parser.fromstring(w.text)
                    # Obtendo valor anual dos dividendos
                    #vdividendo = html4.xpath("//div[@style='text-align:center;']//span/text()")
                    vdividendo = html3.xpath("//div[@class='col-md-12 col-xs-12']//span[@class='indicator-value']/text()")
                    #print('-'*20, 'Dados dos dividendos', '-'*20)
                    #print(dividendo)
                    # Inserindo os dados nas demais linhas
                    # Resumindo tudo numa só lista
                    #print(len(self.variacao))

                    if len(self.variacao) == self.dias:

                        self.unilist.append(fundo)
                        # tipo do fundo
                        for j in tfundo:
                            self.unilist.append(j.replace('"', '').strip())
                        # Valor do dividendo Anual
                        if len(vdividendo) >= 1:
                            self.unilist.append(float(vdividendo[2].replace(',', '.').replace('R$', '').replace('%', '').strip()))
                        else:
                            self.unilist.append(0.0)
                        # valor do aluguel pago por cota
                        '''
                        for v in vfundo:
                            try:
                                j = v.replace('R$', '').strip()
                                unilist.append(float(j.replace(',', '.')))
                            except ValueError:
                                unilist.append(0.0)
                        '''
                        '''
                        f = [v.replace(',', '.') for v in self.cotacoes]
                        #f = (list(map(lambda v: str(v.replace(',', '.')), self.cotacoes)))
                        n = [float(i.replace('.', '', 1)) if f.count('.') >= 2 else float(i) for i in f]
                        self.unilist.append(n[0])
                        '''
                        for v in self.cota:
                            f = v.replace(',', '.')
                            # Tem que remover o segundo ponto. Ex: 1.163.76 (não pode ser convertido para float)
                            if f.count('.') >= 2:
                                n = f.replace('.', '', 1)
                                self.unilist.append(float(n))
                            else:
                                self.unilist.append(float(v.replace(',', '.')))
                            self.cota.clear()

                        #v = [float(i.replace(',', '.')) for i in self.variacao]
                        #self.unilist.append(v[0:])
                        # Adicionando a liquidez diária
                        try:
                            self.unilist.append(float(pvp[0].replace('.', '')))
                        except:
                            self.unilist.append(float(pvp[0]))
                        # Adicionando o p/vp, importante para ver se vale a pena comprar o papel
                        self.unilist.append(float(pvp[6].replace(',', '.')))

                        # SE A ANÁLISE FOR DIÁRIA, COLETAR OS DADOS NORMALMENTE
                        if self.kind == 'diario':
                            for i in self.variacao:
                                self.unilist.append(float(i.replace(',', '.')))
                            self.variacao.clear()
                            self.list_csv.append(self.unilist[:])
                            self.unilist.clear()
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
                                    if now == m and c != len(self.lista_dias)-1:
                                        n += 1
                                    elif now != m and c != len(self.lista_dias)-1:
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
                                    soma += float(v.replace(',', '.'))
                                    c += 1
                                else:
                                    self.unilist.append(soma)
                                    soma, c = 0, 2
                                    soma += float(v.replace(',', '.'))
                                    i += 1
                            self.variacao.clear()
                            self.list_csv.append(self.unilist[:])
                            self.unilist.clear()

                    else:
                        self.cota.clear()
                        self.variacao.clear()
                        continue
                else:
                    self.cota.clear()
                    continue

        return self.list_csv

    def dadosSelect(self):

        # Verificando se o arquivo existe
        if os.path.exists(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados/Dados_Papeis_{self.meses}_meses_{self.kind}.csv'):
            os.remove(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados/Dados_Papeis_{self.meses}_meses_{self.kind}.csv')
        with open(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados/Dados_Papeis_{self.meses}_meses_{self.kind}.csv', 'w', newline='') as dados:
            writer = csv.writer(dados)
            col_name = list(range(0, len(self.list_csv[0])))
            writer.writerow(col_name)
            for d in self.list_csv:  # obj.dadosCotacoes():
                writer.writerow(d)
        # Lendo a tabela com PANDAS Dataframe
        # df = pd.read_table('/Users/milso/Desktop/MONETA/Dados_Papeis.csv', 'utf-8')
        df = pd.read_csv(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados/Dados_Papeis_{self.meses}_meses_{self.kind}.csv', engine='python')
        print(df)

if __name__ == '__main__':
    meses = 6
    #kind = 'diario'
    kind = 'mensal'
    stdoutmutex = threading.Lock()
    threads = []
    descartados = ['']
    obj = WebScraping(meses, kind, descartados, stdoutmutex)
    obj.time()
    obj.listaFundos()
    #obj.dadosCotacoes()
    obj.start()
    threads.append(obj)
    for thread in threads:
        thread.join()
    obj.dadosSelect()
    #print(f'Tempo de execução:{process_time()} segundos')
    #print(f'Tempo de execução:{perf_counter()} segundos')
    duracao = round((perf_counter()), 0)
    horas = int(duracao//3600)
    minutos = int(round((duracao/3600 - duracao//3600)*60, 0))
    segundos = int(round((duracao%60), 0))
    print(f'Tempo de execução:{horas}:{minutos}:{segundos}')

'''
# Para contar o tamanho dos dados e definir a quantidade pelo menor número de dados.
                        for c, i in enumerate(unilist):
                            if c == 0:
                                min = len(unilist)
                            else:
                                if min > len(unilist):
                                    min = len(unilist)
                        selecao.append(unilist[:])
                        unilist.clear()
                    else:
                        continue
                for l in selecao:
                    if len(l) == min:
                        csv_list.insert(0, l)
                    elif len(l) > min:
                        csv_list.append(l[0:min])
'''