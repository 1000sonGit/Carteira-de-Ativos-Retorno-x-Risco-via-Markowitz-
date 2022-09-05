import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QToolTip, QProgressBar, \
    QGroupBox, QGridLayout, QRadioButton, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLCDNumber, \
    QLineEdit, QFormLayout, QCheckBox, QAbstractItemView, QTableView, QAbstractButton, QTableWidget,\
    QTableWidgetItem, QLabel, QFileDialog, QMessageBox, QSizePolicy
from PyQt5 import QtCore
from PyQt5.QtGui import QDoubleValidator, QIcon
from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, QUrl, QStringListModel
import csv
import os.path
import pandas as pd
import threading
import requests

import Data_v10
import Algoritmo_threading
import QtRangeSlider
from time import sleep, perf_counter
import shelve

import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime
#from qrangeslider import qrangeslider
import qrangeslider_float
#from rangeSlider import *
import rangeSlider

class InitWindow(QWidget):

    def __init__(self, parent=None):
        super(InitWindow, self).__init__(parent)
        '''
        self.title = 'MONETA FII'

        #Geometria da tela
        self.top = 100
        self.left = 300
        self.width = 800
        self.height = 600

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # self.show()
        #sleep(2)
        '''
class Janela(QWidget, threading.Thread): #QMainWindow,
    emitSinal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(Janela, self).__init__(parent)

        threading.Thread.__init__(self)

        self.title = 'MONETA FII'

        #Valores Padrão
        self.An = 15
        self.capMax = 0.0
        self.pvpmin = 0.0
        self.pvpmax = 0.0
        self.liquidez = 0
        self.path_old = ''
        self.path_now = ''
        self.listDescarta = ['']
        self.listFixa = ['']

        self.grid = QGridLayout()
        #Tempo estimado do investimento
        self.grid.addWidget(self.primeiroGrid(), 0, 0)
        #Intervalo de tempo coletado
        self.grid.addWidget(self.segundoGrid(), 0, 1)
        #Número de papéis
        self.grid.addWidget(self.terceiroGrid(), 1, 0)
        #Volume diário
        self.grid.addWidget(self.quartoGrid(state=0), 3, 0)
        #Capital investido
        self.grid.addWidget(self.quintoGrid(), 1, 1)
        # P/VP preço da cota pelo valor patrimonial
        self.grid.addWidget(self.sextoGrid(state=0), 3, 1)
        #Botão de Simular investimento
        self.grid.addWidget(self.setimoGrid(), 5, 0, 1, 0)
        #Checkbox para Interferência Administrativa
        self.grid.addWidget(self.oitavoGrid(), 2, 0, 1, 0)
        #Tabela dos papéis disponíveis
        self.grid.addWidget(self.nonoGrid(state=0), 4, 0)
        # Botão para carregar os dados
        self.grid.addWidget(self.decimoGrid(), 4, 1)

        self.setLayout(self.grid)

        #self.InitWindow()
    '''
    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #self.show()
        sleep(2)
        self.close()
    '''
    # CHECANDO CONEXÃO COM INTERNET
    def internet_on(self):
        url = 'http://www.google.com/'
        timeout = 5
        try:
            _ = requests.get(url, timeout=timeout)
            return True
        except requests.ConnectionError:
            print("İnternet desconectada")
            return False

    # INSERINDO OS ELEMENTOS

    def primeiroGrid(self):

        # Tempo estimado de investimento
        titulo = QGroupBox('Tempo estimado do investimento')

        self.radio_kind1 = QRadioButton("1 dia(day-trade)")
        self.radio_kind1.toggled.connect(lambda: self.btnstateKind(self.radio_kind1))
        self.radio_kind2 = QRadioButton("1 semana")
        self.radio_kind2.toggled.connect(lambda: self.btnstateKind(self.radio_kind2))
        self.radio_kind3 = QRadioButton("1 mês")
        self.radio_kind3.toggled.connect(lambda: self.btnstateKind(self.radio_kind3))

        self.radio_kind3.setChecked(True)

        vbox = QVBoxLayout()
        # addWidget: adiciona os widget
        vbox.addWidget(self.radio_kind1)
        vbox.addWidget(self.radio_kind2)
        vbox.addWidget(self.radio_kind3)
        # Stretch é o espaço entre os itens
        vbox.addStretch(1)
        titulo.setLayout(vbox)

        return titulo

    def btnstateKind(self, a):

        if a.text() == '1 dia(day-trade)':
            if a.isChecked() == True:
                self.kind = 'diário'
                #print('diário')

        if a.text() == '1 semana':
            if a.isChecked() == True:
                self.kind = 'semanal'
                #print('mensal')

        if a.text() == '1 mês':
            if a.isChecked() == True:
                self.kind = 'mensal'
                #print('mensal')

        db = shelve.open('dados.db')
        db['tipo'] = self.kind
        db.close()

    def segundoGrid(self):
        #INTERVALO DE TEMPO DO BANCO DE DADOS
        titulo_2 = QGroupBox('Intervalo de tempo coletado')

        self.radio_time1 = QRadioButton("3 meses")
        self.radio_time1.toggled.connect(lambda:self.btnstateTime(self.radio_time1))
        self.radio_time2 = QRadioButton("6 meses")
        self.radio_time2.toggled.connect(lambda:self.btnstateTime(self.radio_time2))
        self.radio_time3 = QRadioButton("12 meses")
        self.radio_time3.toggled.connect(lambda:self.btnstateTime(self.radio_time3))

        self.radio_time2.setChecked(True)

        vbox_2 = QHBoxLayout()
        # addWidget: adiciona os widget
        vbox_2.addWidget(self.radio_time1)
        vbox_2.addWidget(self.radio_time2)
        vbox_2.addWidget(self.radio_time3)
        # Stretch é o espaço entre os itens
        vbox_2.addStretch(1)
        titulo_2.setLayout(vbox_2)

        return titulo_2

    def btnstateTime(self, b):

        if b.text() == '3 meses':
            if b.isChecked() == True:
                self.meses = 3
                #print('3 meses')
        if b.text() == '6 meses':
            if b.isChecked() == True:
                self.meses = 6
                #print('6 meses')
        if b.text() == '12 meses':
            if b.isChecked() == True:
                self.meses = 12
                #print('12 meses')
        db = shelve.open('dados.db')
        db['meses'] = self.meses
        db.close()

    def terceiroGrid(self):
        #NÚMERO DE PAPÉIS
        # Declarando objeto da classe QGroupBox
        titulo_3 = QGroupBox('Número de papéis')

        #Declarando objeto da classe QLCDNumber
        self.lcd = QLCDNumber(self)
        self.lcd.display(15)
        db = shelve.open('dados.db')
        db['An'] = self.An
        db.close()
        #self.lcd.setSizeIncrement(200, 200)

        #Declarando objeto da classe QSlider
        self.regua = QSlider(self)
        #Configurando intervalos
        self.regua.setMinimum(3)
        self.regua.setMaximum(30)
        self.regua.setValue(15)
        self.regua.setTickPosition(QSlider.TicksBelow)
        self.regua.setTickInterval(1)
        self.regua.setOrientation(QtCore.Qt.Horizontal)

        #Declarando objeto da classe QVBoxLayout
        vbox_3 = QVBoxLayout()
        vbox_3.addWidget(self.lcd)
        vbox_3.addWidget(self.regua)
        titulo_3.setLayout(vbox_3)
        self.regua.valueChanged.connect(self.lcd.display)
        #Obtendo os valores da regua referente ao número de papéis
        self.regua.valueChanged[int].connect(self.changeValue)

        return titulo_3

    def changeValue(self, value):
        self.An = value
        db = shelve.open('dados.db')
        db['An'] = self.An
        db.close()

    def quartoGrid(self, state):

        # Para apagar configuração anterior
        try:
            self.titulo_4.setParent(None)
        except:
            pass

        #VOLUME DIÁRIO
        self.titulo_4 = QGroupBox('Volume diário')
        #Tornar a opção inacessível
        if state > 0:
            self.titulo_4.setEnabled(True)
            #Valor inicial da variável
            self.liquidez = 2000
            db = shelve.open('dados.db')
            db['liquidez'] = self.liquidez
            db.close()
            # Para apagar configuração anterior
            try:
                self.lcd2.setParent(None)
                self.regua2.setParent(None)
            except:
                pass
        else:
            self.titulo_4.setEnabled(False)
            # Valor inicial da variável
            self.liquidez = 0
            # Para apagar configuração anterior
            try:
                self.lcd2.setParent(None)
                self.regua2.setParent(None)
            except:
                pass

        # Declarando objeto da classe QLCDNumber
        self.lcd2 = QLCDNumber(self)
        self.lcd2.display(2000)

        self.regua2 = QSlider(QtCore.Qt.Horizontal)
        # addWidget: adiciona os widget
        self.regua2.setMinimum(0)
        self.regua2.setMaximum(6000)
        self.regua2.setValue(2000)
        self.regua2.setTickPosition(QSlider.TicksBelow)
        self.regua2.setTickInterval(1000)
        self.regua2.setSingleStep(1000)
        self.regua2.setOrientation(QtCore.Qt.Horizontal)

        vbox_4 = QVBoxLayout()
        vbox_4.addWidget(self.lcd2)
        vbox_4.addWidget(self.regua2)
        self.titulo_4.setLayout(vbox_4)
        self.regua2.valueChanged.connect(self.lcd2.display)
        self.regua2.valueChanged.connect(self.changeValue2)

        return self.titulo_4

    def changeValue2(self, value):
        self.liquidez = value
        #print(self.liquidez)
        db = shelve.open('dados.db')
        db['liquidez'] = self.liquidez
        db.close()

    def quintoGrid(self):
        #CAPITAL INVESTIDO:
        titulo_5 = QGroupBox('Capital Investido')

        #CAMPO DE INSERÇÃO DO CAPITAL
        self.capital = QLineEdit(self)
        #Alinhando o texto na caixa
        self.capital.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.capital.setValidator(QDoubleValidator(0.99, 99.99, 2))
        #Colocando texto de exemplo
        self.capital.setPlaceholderText('Ex: R$ 12435,89')
        #TEXTO DE OBSERVAÇÃO
        self.texto = QLabel('OBS: Deixar este campo em branco '
                            'permite o software calcular'
                            '\n uma carteira de investimento sem limitar um '
                            'valor para o capital investido.')

        vbox_5 = QFormLayout()
        vbox_5.addWidget(self.capital)
        vbox_5.addWidget(self.texto)
        titulo_5.setLayout(vbox_5)
        #Obtendo o valor do capital digitado|inserido
        self.capital.textChanged.connect(self.onChanged)
        # Armazenando o valor do Capital investido
        db = shelve.open('dados.db')
        db['capital'] = self.capMax
        db.close()

        return titulo_5

    def onChanged(self, text):
        self.capMax = text
        db = shelve.open('dados.db')
        db['capital'] = self.capMax
        db.close()

    #@property
    def sextoGrid(self, state):

        # Para apagar configuração anterior
        try:
            self.titulo_6.setParent(None)
        except:
            pass

        #P/VP preço da cota pelo valor patrimonial
        self.titulo_6 = QGroupBox('Preço da cota pelo valor patrimonial (P/VP)')
        # Tornar a opção inacessível
        if state > 0:
            #Habilita ou Desabilita o QGroupBox
            self.titulo_6.setEnabled(True)
            self.pvpmin = 0.9
            self.pvpmax = 1.2
            db = shelve.open('dados.db')
            db['pvp'] = [self.pvpmin, self.pvpmax]
            db.close()
            # Para apagar configuração anterior
            try:
                #Deixa o widget desabilitado
                self.slider.setParent(None)
            except:
                pass
        else:
            self.titulo_6.setEnabled(False)
            self.pvpmin = 0
            self.pvpmax = 0
            db = shelve.open('dados.db')
            db['pvp'] = [self.pvpmin, self.pvpmax]
            db.close()
            # Para apagar configuração anterior
            try:
                self.slider.setParent(None)
            except:
                pass
        '''
        slider = qrangeslider_float.QRangeSlider()
        slider.setWindowTitle('Preço da cota pelo valor patrimonial (P/VP)')
        slider.show()
        slider.setRange(0.9, 1.2)
        slider.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        slider.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')
        #self.min = slider._setStart(0.9)
        #self.max = slider._setEnd(1.2)
        #self.range = slider._handleMoveSplitter()
        print(self.min)
        #print(self.range)
        '''

        hslider = QtRangeSlider.QHRangeSlider(slider_range=[0.0, 2.0, 0.1], values=[0.9, 1.2])
        hslider.setEmitWhileMoving(True)
        #hslider.show()

        self.dhslider = QtRangeSlider.QHSpinBoxRangeSlider(slider_range=[0.0, 2.0, 0.1], values=[0.9, 1.2])
        self.dhslider.setEmitWhileMoving(True)
        #dhslider.show()

        vbox_6 = QVBoxLayout()
        vbox_6.addWidget(hslider)
        vbox_6.addWidget(self.dhslider)
        self.titulo_6.setLayout(vbox_6)
        #Obtendo os valores inseridos
        self.dhslider.rangeChanged.connect(self.getPvp)

        return self.titulo_6

    def getPvp(self):

        self.pvpmin = self.dhslider.getValues()[0]
        self.pvpmax = self.dhslider.getValues()[1]
        #print(self.pvpmin, self.pvpmax)
        #print(self.dhslider.getValues())
        db = shelve.open('dados.db')
        db['pvp'] = [self.pvpmin, self.pvpmax]
        db.close()

    def setimoGrid(self):
        #BOTÃO DE SIMULAR INVESTIMENTO
        titulo_7 = QGroupBox()

        self.button = QPushButton('Simular', self)
        self.button.setStyleSheet('QPushButton {font: bold}')

        #Demonstrar mensagem ao deixar o indicador parado no botão
        self.button.setToolTip('CLICK PARA INICIAR A SIMULAÇÃO DA CARTEIRA DE INVESTIMENTO')

        #Definindo o tamanho do botão
        self.button.move(200, 200)

        # Ação para o botão
        self.button.clicked.connect(self.action)

        vbox_7 = QVBoxLayout()
        vbox_7.addWidget(self.button)
        titulo_7.setLayout(vbox_7)

        return titulo_7

    def action(self):
        x = 0
        #Checando conexão com Internet
        if self.internet_on() == True:
            pass
        else:
            QMessageBox.information(self, 'Conexão', 'Sem conexão de Internet!', QMessageBox.Ok)
            x = 1
            pass

        #Verificando dados incompletos

        if self.text_box.text() != '' and self.text_box1.text() != '':
            pass
        else:
            QMessageBox.information(self, 'Dados incompletos', 'Preencha os campos de selecionar dados!', QMessageBox.Ok)
            x = 1
            pass

        if x == 0:
            # Iniciando as Variáveis
            arq = shelve.open('dados.db')
            meses = arq['meses']
            tipo = arq['tipo']
            listDescarta = arq['listDescarta']
            #listFixa = arq['listFixa']
            path_old = arq['FileOld']
            path_now = arq['FileNew']
            arq.close()
            i = 0
            # Coletando dados para comparar a lista de descartados
            if os.path.exists('/Users/milso/OneDrive/Cursos Python/MONETA/moneta_FII/ListaFundos.db.bak'):
                arq_fundos = shelve.open('ListaFundos.db')
                fundos = arq_fundos['list_fundos']
                arq_fundos.close()
            else:
                fundos = ['']
            # OBTENDO A DATA DE MODIFICAÇÃO DO ARQUIVO
            if os.path.exists(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados/Dados_Papeis_{meses}_meses_{tipo}.csv'):
                dadosHoje = datetime.fromtimestamp(os.path.getmtime(f'/Users/milso/OneDrive/Cursos Python/MONETA/Dados/Dados_Papeis_{meses}_meses_{tipo}.csv'))

                # CONDICIONAL PARA NÃO TER QUE CARREGAR E TRATAR OS DADOS DESNECESSARIAMENTE
                resultado = ['1' if fundo in listDescarta else '0' for fundo in fundos]
                if datetime.today().day == dadosHoje.day and '1' not in resultado:
                    i = 1
                else:
                    i = 0
            if i == 0:
                stdoutmutex = threading.Lock()
                threads = []
                short = 9
                long = 18
                self.datas = Data_v10.WebScraping(meses, tipo,  short, long,listDescarta, path_old, path_now, stdoutmutex)
                self.datas.time()
                self.datas.listaFundos()
                threadRun = threading.Thread(target=self.datas.dadosCotacoes())  # , args=(capMax,))
                threadRun.daemon = True
                threadRun.start()
                threads.append(threadRun)
                for thread in threads:
                    thread.join()
                self.datas.dadosSelect()
            # Fechando Aplicativo

            # Emitindo sinal para chamada de outra tela
            self.emitSinal.emit(1)
            duracao = round((perf_counter()), 0)
            horas = int(duracao // 3600)
            minutos = int(round((duracao / 3600 - duracao // 3600) * 60, 0))
            segundos = int(round((duracao % 60), 0))
            print(f'Tempo de execução:{horas}:{minutos}:{segundos}')


        else: pass

    def oitavoGrid(self):
        # Checkbox para interferência administrativa
        titulo_8 = QGroupBox('Interferência Administrativa')

        check = QCheckBox("Ativar")
        check.setToolTip('Obs: Permite interferir em parâmetros fundamentalistas')

        check.setChecked(False)

        #Texto explicativo
        #texto_expli = QLabel('Obs: Permite interferir em parâmetros fundamentalistas')
        #texto_expli.setAlignment(QtCore.Qt.AlignLeft)

        vbox_8 = QHBoxLayout()
        # addWidget: adiciona os widget
        vbox_8.addWidget(check)
        #vbox_8.addWidget(texto_expli)
        # Conexão com a visibilidade dos métodos
        check.stateChanged.connect(self.changeState)
        #check.stateChanged.connect(self.sextoGrid)
        titulo_8.setLayout(vbox_8)

        return titulo_8

    def changeState(self, state):
        # Apagando o conteúdo do Grids que serão ativados|desativados
        try:
            self.grid.itemAt(10).widget().setParent(None)
        except:
            pass
        # Reinserindo Volume diário
        self.grid.addWidget(self.quartoGrid(state), 3, 0)
        # P/VP preço da cota pelo valor patrimonial
        self.grid.addWidget(self.sextoGrid(state), 3, 1)
        # Tabela dos papéis disponíveis
        self.grid.addWidget(self.nonoGrid(state), 4, 0)


    def nonoGrid(self, state):
        #Tabela com os papéis disponíveis
        x = 0
        # Checando conexão com Internet
        #if self.internet_on() == True:
        #    pass
        #else:
        #    QMessageBox.information(self, 'Conexão', 'Sem conexão de Internet!', QMessageBox.Ok)
        #    x = 1
        #    pass
        if x == 0:
            #Invocando as opções do usuário (tempo de investimento e intervalo coletado)

            #Importando módulo Data_Threading para obter os dados atualizados

            stdoutmutex = threading.Lock()
            #self.listDescarta = ['']
            # CONDICIONAL PARA CHECAR SE O ARQUIVO JÁ EXISTE, PARA EVITAR O USO DE INTERNET NA COLETA DA LISTA DE FUNDOS (ATUALIZANDO MENSALMENTE)
            fundos_time = datetime.fromtimestamp(os.path.getmtime('/Users/milso/OneDrive/Cursos Python/MONETA/moneta_FII/ListaFundos.db.bak'))
            if os.path.exists('/Users/milso/OneDrive/Cursos Python/MONETA/moneta_FII/ListaFundos.db.bak') and fundos_time.month == datetime.today().month:
                arq = shelve.open('ListaFundos.db')
                lista = arq['list_fundos']
                arq.close()
            else:
                short = 9
                long = 18
                obj = Data_v10.WebScraping(self.meses, self.kind,  short, long, self.listDescarta, self.path_old, self.path_now, stdoutmutex)
                lista = obj.listaFundos()

            # Para apagar configuração anterior
            try:
                self.titulo_9.setParent(None)
            except:
                pass

            self.titulo_9 = QGroupBox('Tabela dos papéis disponíveis')

            # Tornar a opção inacessível
            if state > 0:
                # Habilita ou Desabilita o QGroupBox
                self.titulo_9.setEnabled(True)
                # Para apagar configuração anterior
                try:
                    # Deixa o widget desabilitado
                    self.QTableWidget.setParent(None)
                except:
                    pass
            else:
                self.titulo_9.setEnabled(False)
                # Para apagar configuração anterior
                try:
                    self.QTableWidget.setParent(None)
                except:
                    pass

            #Criando a tabela
            rows = len(lista)
            #print(lista)
            columns = 3
            self.table = QTableWidget(rows, columns)
            #PREENCHENDO A TABELA
            #Mudando o cabeçalho da tabela
            self.table.setHorizontalHeaderLabels(['Papéis', 'Fixar', 'Descartar'])
            for column in range(columns):
                for c, i in enumerate(lista):
                    if column == 0:
                        item = QTableWidgetItem(i)
                    else:
                        item = QTableWidgetItem()
                        #item.setTextAlignment(QtCore.Qt.AlignHCenter)
                        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        item.setCheckState(QtCore.Qt.Unchecked)
                    self.table.setItem(c, column, item)
            self.table.itemClicked.connect(self.handleItemClicked)
            layout = QVBoxLayout(self)
            layout.addWidget(self.table)
            self.titulo_9.setLayout(layout)
            #Guarda os papéis a serem fixados ou descartados

            return self.titulo_9

        else:
            self.close()
            #Fechando Aplicativo
            QApplication.quit()


    def handleItemClicked(self, item):

        #Condicionais para checkbox acionado
        if self.table.item(item.row(), 1).checkState() == QtCore.Qt.Checked and self.table.item(item.row(), 2).checkState() == QtCore.Qt.Unchecked:
            #Retirando a seleção do checkbox vizinho
            if item.column() == 1:
                self.table.item(item.row(), 2).setCheckState(QtCore.Qt.Unchecked)
                try:
                    celula = self.table.item(item.row(), 0)
                    self.listDescarta.remove(celula.text())
                except ValueError:
                    pass

            if item.column() == 2:
                self.table.item(item.row(), 1).setCheckState(QtCore.Qt.Unchecked)
                try:
                    celula = self.table.item(item.row(), 0)
                    self.listFixa.remove(celula.text())
                except ValueError:
                    pass

            #print('"%s" Checked' % item.text())
            #Pegando o item selecionado
            celula = self.table.item(item.row(), 0) #(row,column)
            self.listFixa.append(celula.text())
            #print(item.row())
            #print(self.listFixa)

        #Condicional para remover item da listFixa
        elif self.table.item(item.row(), 1).checkState() == QtCore.Qt.Unchecked and self.table.item(item.row(), 2).checkState() == QtCore.Qt.Unchecked:
            if item.column() == 1:
                self.table.item(item.row(), 2).setCheckState(QtCore.Qt.Unchecked)
                try:
                    celula = self.table.item(item.row(), 0)  # (row,column)
                    self.listFixa.remove(celula.text())
                    #print(self.listFixa)
                except ValueError:
                    pass
            if item.column() == 2:
                self.table.item(item.row(), 1).setCheckState(QtCore.Qt.Unchecked)
                try:
                    celula = self.table.item(item.row(), 0)  # (row,column)
                    self.listDescarta.remove(celula.text())
                    #print(self.listDescarta)
                except ValueError:
                    pass

        # Condicional para remover item da listFixa
        elif self.table.item(item.row(), 1).checkState() == QtCore.Qt.Checked and self.table.item(item.row(), 2).checkState() == QtCore.Qt.Checked:
            if item.column() == 1:
                self.table.item(item.row(), 2).setCheckState(QtCore.Qt.Unchecked)
                try:
                    celula = self.table.item(item.row(), 0)  # (row,column)
                    self.listDescarta.remove(celula.text())
                    #print(self.listDescarta)
                except ValueError:
                    pass
                celula = self.table.item(item.row(), 0)
                self.listFixa.append(celula.text())
            if item.column() == 2:
                self.table.item(item.row(), 1).setCheckState(QtCore.Qt.Unchecked)
                try:
                    celula = self.table.item(item.row(), 0)  # (row,column)
                    self.listFixa.remove(celula.text())
                    #print(self.listFixa)
                except ValueError:
                    pass
                celula = self.table.item(item.row(), 0)
                self.listDescarta.append(celula.text())

        else:#if self.table.item(item.row(), 2).checkState() == QtCore.Qt.Checked:
            # Retirando a seleção do checkbox vizinho

            if item.column() == 1:
                self.table.item(item.row(), 2).setCheckState(QtCore.Qt.Unchecked)
                try:
                    celula = self.table.item(item.row(), 0)
                    self.listDescarta.remove(celula.text())
                except ValueError:
                    pass

            if item.column() == 2:
                self.table.item(item.row(), 1).setCheckState(QtCore.Qt.Unchecked)
                try:
                    celula = self.table.item(item.row(), 0)
                    self.listFixa.remove(celula.text())
                except ValueError:
                    pass
            #print('"%s" Clicked' % item.text())
            # Pegando o item selecionado
            celula = self.table.item(item.row(), 0)  # (row,column)

            self.listDescarta.append(celula.text())
            #print(item.row())
            #print(self.listDescarta)
        db = shelve.open('dados.db')
        db['listDescarta'] = self.listDescarta
        db['listFixa'] = self.listFixa
        db.close()

    def decimoGrid(self):
        #BOTÕES PARA CARREGAR OS DADOS
        titulo_10 = QGroupBox('Carregar dados')

        texto = QLabel('Selecionar dados do Ano passado')

        self.text_box = QLineEdit(self)
        self.text_box.setReadOnly(True)
        self.text_box.setPlaceholderText('Caminho do arquivo')
        self.text_box.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # BOTÃO DE PARA CARREGAR DADOS DO ANO PASSADO
        buttonOld = QPushButton()
        buttonOld.setStyleSheet('QPushButton {font: bold}')
        buttonOld.setIcon(QIcon('pasta.png'))

        # Demonstrar mensagem ao deixar o indicador parado no botão
        buttonOld.setToolTip('CLICK PARA SELECIONAR O ARQUIVO DE DADOS DO ANO PASSADO')

        # Definindo o tamanho do botão
        buttonOld.move(10, 10)
        #Ação para o botão
        buttonOld.clicked.connect(self.getFile_old)

        # BOTÃO DE PARA CARREGAR DADOS DO ANO ATUAL
        texto1 = QLabel('Selecionar dados do Ano atual')
        #button1 = QPushButton('Selecionar dados do Ano atual', self)
        self.text_box1 = QLineEdit(self)
        self.text_box1.setReadOnly(True)
        self.text_box1.setPlaceholderText('Caminho do arquivo')
        self.text_box1.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        buttonNew = QPushButton()
        buttonNew.setStyleSheet('QPushButton {font: bold}')
        buttonNew.setIcon(QIcon('pasta.png'))

        # Demonstrar mensagem ao deixar o indicador parado no botão
        buttonNew.setToolTip('CLICK PARA SELECIONAR O ARQUIVO DE DADOS DO ANO ATUAL')

        # Definindo o tamanho do botão
        buttonNew.move(10, 10)
        # Ação para o botão
        buttonNew.clicked.connect(self.getFile_now)
        #button1.clicked.connect(self.text_box1.setText)

        # BOTÃO DE PARA CARREGAR DADOS SALVOS
        texto2 = QLabel('Selecionar dados de investimentos anteriores(obs: se tiver)')
        # button1 = QPushButton('Selecionar dados do Ano atual', self)
        self.text_box2 = QLineEdit(self)
        self.text_box2.setReadOnly(True)
        self.text_box2.setPlaceholderText('Caminho do arquivo')
        self.text_box2.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        buttonSalvo = QPushButton()
        buttonSalvo.setStyleSheet('QPushButton {font: bold}')
        buttonSalvo.setIcon(QIcon('pasta.png'))

        # Demonstrar mensagem ao deixar o indicador parado no botão
        buttonSalvo.setToolTip('CLICK PARA SELECIONAR O ARQUIVO DE DADOS DO INVESTIMENTO ANTERIOR')

        # Definindo o tamanho do botão
        buttonSalvo.move(10, 10)
        # Ação para o botão
        buttonSalvo.clicked.connect(self.getFile_salvo)

        vbox_10 = QVBoxLayout()
        vbox_10.addWidget(texto)
        vbox_10.addWidget(self.text_box)
        vbox_10.addWidget(buttonOld)

        vbox_10.addWidget(texto1)
        vbox_10.addWidget(self.text_box1)
        vbox_10.addWidget(buttonNew)

        vbox_10.addWidget(texto2)
        vbox_10.addWidget(self.text_box2)
        vbox_10.addWidget(buttonSalvo)

        titulo_10.setLayout(vbox_10)

        return titulo_10

    def getFile_old(self):
        file_old = QFileDialog.getOpenFileName(self, 'Selecionar arquivo de texto', 'c://', 'Arquivos de texto (*.txt)')
        # Obtendo o caminho do arquivo
        #print(file_old[0].replace('C:', ''))
        self.path_old = file_old[0].replace('C:', '')
        #print(self.path_old)

        # Inserindo o Caminho no text box
        self.text_box.setText(file_old[0])

        # Obtendo somente o nome do arquivo
        url = QUrl.fromLocalFile(file_old[0])
        #print(url.fileName())

        db = shelve.open('dados.db')
        db['FileOld'] = self.path_old
        db.close()

    def getFile_now(self):
        file_now = QFileDialog.getOpenFileName(self, 'Selecionar arquivo de texto', 'c://',
                                                'Arquivos de texto (*.txt)')
        # Obtendo o caminho do arquivo
        #print(file_now[0].replace('C:', ''))
        self.path_now = file_now[0].replace('C:', '')

        # Inserindo o Caminho no text box
        self.text_box1.setText(file_now[0])
        # Obtendo somente o nome do arquivo
        url = QUrl.fromLocalFile(file_now[0])
        # print(url.fileName())
        db = shelve.open('dados.db')
        db['FileNew'] = self.path_now
        db.close()

    def getFile_salvo(self):
        file_salvo = QFileDialog.getOpenFileName(self, 'Selecionar arquivo de texto', 'c://',
                                                'Arquivos de csv (*.csv)')
        # Obtendo o caminho do arquivo
        #print(file_now[0].replace('C:', ''))
        self.path_salvo = file_salvo[0].replace('C:', '')

        # Inserindo o Caminho no text box
        self.text_box2.setText(file_salvo[0])
        # Obtendo somente o nome do arquivo
        url = QUrl.fromLocalFile(file_salvo[0])
        # print(url.fileName())
        db = shelve.open('dados.db')
        db['FileSalvo'] = self.path_salvo
        db.close()

class Processo(threading.Thread):
    #emitFinish = pyqtSignal(int)

    def __init__(self, parent=None):
        super(Processo, self).__init__(parent)
        threading.Thread.__init__(self)

        #Importando os dados salvos em Shelve
        arq = shelve.open('dados.db')
        self.meses = arq['meses']
        self.tipo = arq['tipo']
        self.listFixa = arq['listFixa']
        self.path_salvo = arq['FileSalvo']
        self.pvpmin = arq['pvp'][0]
        self.pvpmax = arq['pvp'][1]
        self.liquidez = arq['liquidez']
        self.papeis = arq['An']
        self.capMax = arq['capital']
        arq.close()
        self.iter = 1000000
        #print(listFixa, pvpmin, pvpmax, capMax)
        arq.close()
        self.initCalc()

    def initCalc(self):
        threads = []
        stdoutmutex = threading.Lock()
        #Importando Algoritmo_threading
        bob = Algoritmo_threading.Calculo(self.papeis, self.meses, self.tipo, self.iter, stdoutmutex, self.capMax, self.pvpmin, self.pvpmax, self.liquidez, self.listFixa, self.path_salvo)
        bob.selectAtivos()
        #bob.start()
        threadSolve = threading.Thread(target=bob.solve())
        threadSolve.daemon = True
        threadSolve.start()
        threads.append(threadSolve)
        #threads.append(bob)
        for thread in threads:
            thread.join()

        # Implementando threading para o PO
        threadPO = threading.Thread(target=bob.quantAtivos())  # , args=(capMax,))
        threadPO.daemon = True
        threadPO.start()
        threads.clear()
        threads.append(threadPO)
        for thread in threads:
            thread.join()
        # PARA VERIFICAR A ACERTIVIDADE
        # bob.ganhoReal()
        #self.bob.comparaInvest()
        # Obtendo o tempo de execução:
        duracao = round((perf_counter()), 0)
        horas = int(duracao // 3600)
        minutos = int(round((duracao / 3600 - duracao // 3600) * 60, 0))
        segundos = int(round((duracao % 60), 0))
        print(f'Tempo de execução:{horas}:{minutos}:{segundos}')
        #self.objResult = PlotCanvas()
        #self.objResult.__init__(self,  width=5, height=4, dpi=100)
        #self.emitFinish.emit(2)

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class PizzaWidget(MplCanvas):

    def compute_initial_figure(self):

        arq = shelve.open('dados.db')
        meses = arq['meses']
        tipo = arq['tipo']
        papeis = arq['An']
        capMax = arq['capital']
        arq.close()

        db_shelve = shelve.open('Invest.db')
        columns_name = db_shelve['columns_name']
        best_name = db_shelve['nomes']
        linha = db_shelve['linha']
        db_shelve.close()

        # Composição da carteira Pizza
        #titulo_1P = QGroupBox()

        #vbox_1P = QHBoxLayout()
        # Inserindo o gráfico
        #pizza_canvas = FigureCanvas(Figure(figsize=(30, 30)))
        if capMax == 0:
            file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{meses}_meses_{tipo}_{papeis}papeis.csv'
            df = pd.read_csv(file_name, engine='python')
            df.columns = columns_name
            df = df.sort_values(['Maximum'], ascending=False)
            # Gráfico de pizza das porcentagens
            labels = best_name
            porcent = []
            for i in range(papeis):
                porcent.append(df.iloc[0, i] * 100)
            sizes = porcent
            # explode = (0, 0, 0.1)
            #self.fig1, self.ax1 = plt.subplots()#plt.subplots()
            self.axes.pie(sizes, autopct='%1.1f%%', shadow=False, textprops=dict(color='w'),
                    startangle=90)  # , labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            self.axes.legend(labels, title='Papéis', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            self.axes.set_title('Composição da Carteira')
            # ax1.axis('equal')
            #self.draw()

        else:
            file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{meses}_meses_{tipo}_{papeis}papeis.csv'
            df = pd.read_csv(file_name, engine='python')
            df.columns = columns_name
            df = df.sort_values(['Maximum'], ascending=False)

            # Gráfico de pizza das porcentagens
            labels = best_name
            porcent = []
            for i in range(papeis):
                porcent.append(df.iloc[linha, i] * 100)
            sizes = porcent
            # explode = (0, 0, 0.1)
            #self.fig1, self.ax1 = plt.subplots()
            # ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            # ax1.axis('equal')
            self.axes.pie(sizes, autopct='%1.1f%%', shadow=False, textprops=dict(color='w'), startangle=90)
            self.axes.legend(labels, title='Papéis', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
            self.axes.set_title('Composição da Carteira')

        #vbox_1P.addWidget(self.draw())
        #titulo_1P.setLayout(vbox_1P)

        #return titulo_1P

class DispersaoWidget(MplCanvas):

    def compute_initial_figure(self):

        arq = shelve.open('dados.db')
        meses = arq['meses']
        tipo = arq['tipo']
        papeis = arq['An']
        capMax = arq['capital']
        arq.close()

        db_shelve = shelve.open('Invest.db')
        columns_name = db_shelve['columns_name']
        db_shelve.close()

        # Composição da carteira
        #titulo_2P = QGroupBox()

        #vbox_2P = QVBoxLayout()
        # Inserindo Gráfico
        #dispersao_canvas = FigureCanvas(Figure(figsize=(30, 30)))
        if capMax == 0:
            file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{meses}_meses_{tipo}_{papeis}papeis.csv'
            df = pd.read_csv(file_name, engine='python')
            df.columns = columns_name
            df = df.sort_values(['Maximum'], ascending=False)
            # df.plot('Risco', 'Retorno') #(x,y)
            # plt.plot(df['Risco'], df['Retorno'], 'ro')

            # Gráfico de dispersão de Markovit
            #self.fig, self.ax = plt.subplots()
            self.axes.scatter(df['Risco'], df['Retorno'], alpha=0.5, c=df['Risco'])
            # plt.legend()
            self.axes.set_title('Gráfico do retorno ótimo de Markowitz')
            self.axes.set_xlabel('Risco')
            self.axes.set_ylabel('Retorno')

        else:
            file_name = f'/Users/milso/OneDrive/Cursos Python/MONETA/Resultados/Dados_Resultados_{meses}_meses_{tipo}_{papeis}papeis.csv'
            df = pd.read_csv(file_name, engine='python')
            df.columns = columns_name
            df = df.sort_values(['Maximum'], ascending=False)
            # df.plot('Risco', 'Retorno') #(x,y)
            # plt.plot(df['Risco'], df['Retorno'], 'ro')

            # Gráfico de dispersão de Markovit
            #self.fig, self.ax = plt.subplots()
            self.axes.scatter(df['Risco'], df['Retorno'], alpha=0.5, c=df['Risco'])
            # plt.legend()
            self.axes.title('Gráfico do retorno ótimo de Markowitz')
            self.axes.xlabel('Risco')
            self.axes.ylabel('Retorno')

class Janela3(QWidget):

    def __init__(self, parent=None):
        super(Janela3, self).__init__(parent)

        self.title = 'MONETA FII: Resultado'

        self.gridP = QGridLayout()
        # Gráficos de pizza e dispersão
        self.gridP.addWidget(self.firstDraw(), 0, 0)
        self.gridP.addWidget(self.secundeDraw(), 0, 1)

        self.setLayout(self.gridP)

    def firstDraw(self):

        # Composição da carteira Pizza
        titulo_1P = QGroupBox('Composição da carteira')

        self.main_widget = QWidget(self)
        vbox_1P = QVBoxLayout()
        # Inserindo o gráfico
        pizza = PizzaWidget(self.main_widget, width=10, height=8, dpi=100)
        #dispersao = DispersaoWidget()
        #self.main_widget = QWidget(self)
        #vbox_1P.addWidget(pizza)#.pizza(self.main_widget))
        vbox_1P.addWidget(pizza)
        #vbox_1P.addWidget(figuras.dispersao(self.main_widget))

        titulo_1P.setLayout(vbox_1P)

        return titulo_1P

    def secundeDraw(self):

        # Gráfico de dispersão
        titulo_2P = QGroupBox('Gráfico de Dispersão')

        self.main_widget = QWidget(self)
        vbox_2P = QVBoxLayout()
        # Inserindo o gráfico
        dispersao = DispersaoWidget(self.main_widget, width=10, height=8, dpi=100)
        #self.main_widget = QWidget(self)
        vbox_2P.addWidget(dispersao)
        #vbox_1P.addWidget(figuras.dispersao(self.main_widget))

        titulo_2P.setLayout(vbox_2P)

        return titulo_2P


class ProgressBar(threading.Thread):

    def rodando(self):
        x = 0
        # Checando conexão com Internet
        if self.internet_on() == True:
            pass
        else:
            QMessageBox.information(self, 'Conexão', 'Sem conexão de Internet!', QMessageBox.Ok)
            x = 1
            pass

        # Verificando dados incompletos

        if self.text_box.text() != '' and self.text_box1.text() != '':
            pass
        else:
            QMessageBox.information(self, 'Dados incompletos', 'Preencha os campos de selecionar dados!',
                                    QMessageBox.Ok)
            x = 1
            pass

        if x == 0:
            # Iniciando as Variáveis
            arq = shelve.open('dados.db')
            meses = arq['meses']
            tipo = arq['tipo']
            listDescarta = arq['listDescarta']
            # listFixa = arq['listFixa']
            path_old = arq['FileOld']
            path_now = arq['FileNew']
            arq.close()
            stdoutmutex = threading.Lock()
            threads = []
            self.datas = Data_v10.WebScraping(meses, tipo, listDescarta, path_old, path_now, stdoutmutex)
            self.datas.time()
            self.datas.listaFundos()
            threadRun = threading.Thread(target=self.datas.dadosCotacoes())  # , args=(capMax,))
            threadRun.daemon = True
            threadRun.start()
            threads.append(threadRun)
            for thread in threads:
                thread.join()
            self.datas.dadosSelect()
            duracao = round((perf_counter()), 0)
            horas = int(duracao // 3600)
            minutos = int(round((duracao / 3600 - duracao // 3600) * 60, 0))
            segundos = int(round((duracao % 60), 0))
            print(f'Tempo de execução:{horas}:{minutos}:{segundos}')
        else: pass

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.title = 'MONETA FII'

        # Geometria da tela
        self.top = 50
        self.left = 300
        self.width = 800
        self.height = 650
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.startInit()

    def startInit(self):
        self.objInit = InitWindow()
        self.setWindowTitle(self.title)
        self.setCentralWidget(self.objInit)
        self.show()
        sleep(1)
        self.startJanela()
        #self.startProcess()

    def startJanela(self):
        self.objJanela = Janela()
        self.setWindowTitle(self.title)
        self.setCentralWidget(self.objJanela)
        self.objJanela.emitSinal.connect(self.startCalc)
        #self.objJanela.button.clicked.connect(self.hide)
        #self.objJanela.show()
        self.show()

    def startCalc(self):
        self.objProcess = Processo()
        #self.objProcess.emitFinish.connect(self.desenhar)
        self.desenhar()

    def desenhar(self):
        self.objJanela3 = Janela3()
        #self.setGeometry(0, 0, 1200, 800)
        self.setWindowTitle(self.title)
        self.setCentralWidget(self.objJanela3)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #obj = Janela()
    obj = MainWindow()
    #obj.show()

    sys.exit(app.exec_())