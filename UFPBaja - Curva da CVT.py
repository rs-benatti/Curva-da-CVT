import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt    
from scipy import signal
import re, os
import time as timea
import matplotlib.backends.backend_tkagg
import scipy.sparse.csgraph._validation
import scipy.spatial.ckdtree

def save():
    #try:
    flag = 0
    if tipo.get() == 'Pasta com .txt':
        pastatxt = arquivo.get()
        arquivostxt = []
        print(os.listdir(pastatxt))
        for ar in os.listdir(pastatxt):
            txtFile = ar.split('.')
            if txtFile[-1] == 'txt':
                print(txtFile[-1])
                arquivostxt.append(pastatxt + '\\' + ar)
    else:
        arquivostxt = [arquivo.get()] 
    #Abrir todos os arquivos de uma pasta
    #Dados na ordem: Tempo, RPM, Velocidade
    #Não deve ter texto no arquivo #Melhorar isso
    #Colocar opção de com ou sem passa baixa
    #Opção de redução por tempo, rpm por velocidade
    print(arquivostxt)
    for y in arquivostxt:
        buscaNum = re.compile(r'''
            (\d)+
        ''', re.VERBOSE)
        exampleData = []
        exampleFile = open(y, 'r')
        for linha in exampleFile.readlines():
            linha = linha.replace(linha[-1], '')
            exampleData.append(linha)
        exampleFile.close()
        #print(exampleData)
        colunaUm = []
        colunaDois = []
        colunaTres = []
        flag = 0
        flag1 = 0
        colunas = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        #Falta tirar as palavras
        def criaMatriz():
            #Adaptar o código p separar por espaço e duplo espaço
            #Tirar caracteres especiais
            try:
                temp = exampleData[0].split(' ')
                tentativa = temp.index('')
                errorFlag = 1
            except:
                errorFlag = 0
            if errorFlag == 0:
                l = exampleData[0].split(' ')
                for cool in range(0, len(l)):
                    colunaUm = []
                    flag = 0
                    mediacool = 0
                    totalcool = 0
                    for i in range(0, len(exampleData)):
                        l = exampleData[i].split(' ')
                        if buscaNum.search(l[cool]) != None:
                            l[cool] = buscaNum.search(l[cool]).group()    
                        else:
                            l[cool] = '0'
                        try:
                            colunaUm.append(float(l[cool]))
                        except:
                            errorFlag = 1
                            break
                    colunas[cool] = colunaUm
                return colunas #Matriz na forma [colunas][linhas]. última linha é len(exampleData) - 1
            if errorFlag == 1:
                l = exampleData[0].split('  ')
                col = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
                for cool in range(0, len(l)):
                    colunaUm = []
                    flag = 0
                    mediacool = 0
                    totalcool = 0
                    for i in range(0, len(exampleData)):
                        l = exampleData[i].split('  ')
                        if buscaNum.search(l[cool]) != None:
                            l[cool] = buscaNum.search(l[cool]).group()    
                        else:
                            l[cool] = '0'
                        colunaUm.append(float(l[cool]))
                    col[cool] = colunaUm
                return col
        colunas = criaMatriz()
        tempo = []
        columnTempo = colunaTempo.get() - 1
        columnRPM = colunaRPM.get() - 1
        columnVelocidade = colunaVelocidade.get() - 1
        try:
            per = 1000/(colunas[columnTempo].index(2) - colunas[columnTempo].index(1))
            print(per) 
        except:
            print("Possivelmente o tempo está em millisegundos")
            per = 0
        print(type(colunas[columnTempo][0]))
        T = int(colunas[columnTempo][len(exampleData) - 1]) - int(colunas[columnTempo][0])
        deltaTtotal = 0
        redCVT = []
        time = 0
        repet = False
        for r in range(0, len(exampleData)):
            if(colunas[columnTempo][r] > 1000):
                repet = True #O tempo está em millisegundos
            time = time + per
            tempo.append(time)
        #----------------PASSA BAIXA--------------------------#
        for i in range(1, len(exampleData)):
            deltaT = int(colunas[columnTempo][i]) - int(colunas[columnTempo][i - 1])
            deltaTtotal = deltaTtotal + deltaT
            deltaTmedio = deltaTtotal / i
        print(deltaTmedio)
        fs = 1000 / deltaTmedio
        if repet == False:
            #Melhorar isso
            fs = 1000 / per
        #fs = 2 * fs #Opç~çao de deixar o gráfcio mais claro
        print(fs)
        cutoff = float(lowpass.get())
        nyq = 0.5 * fs
        order = 2
        n = len(exampleData)
        w = cutoff / (fs / 2)
        b, a = signal.butter(2, w, output= 'ba')
        for i in range(1, len(exampleData)):
            motor = colunas[columnRPM][i]
            vel = colunas[columnVelocidade][i]
            if antideslizamento.get() == 1:
                if vel > 60 and i > 0: #Colocar isso como opcional (filtro para deslizamento)
                    vel = colunas[columnRPM][i - 1]
                    colunas[columnVelocidade][i] = colunas[columnVelocidade][i-1]
            try:
                #Checar se é 7.3 mesmo, ou 7.47
                x = motor/(vel * 9.09 * 7.47)
            except:
                x = 0
            redCVT.append(x)
        redCVT.append(redCVT[-1])
        output = signal.filtfilt(b, a, colunas[columnRPM])#botar redCVT
        output1 = signal.filtfilt(b, a, colunas[columnVelocidade])
        output2 = signal.filtfilt(b, a, redCVT)
        fig, ax = plt.subplots()
        print(graph.get())
        if (graph.get() == 'Velocidade x RPM'):
            plt.title("Velocidade x RPM")
            plt.xlabel("Velocidade (km/h)")
            plt.ylabel("RPM")
            if(ameniza.get() == 1):
                plt.plot(output1, output)
            else:
                plt.plot(colunas[columnVelocidade], output)
        if (graph.get() == 'Tempo x redução'):
            plt.xlabel("Tempo (ms)")
            plt.ylabel("Redução")
            plt.title("Tempo x redução")
            if repet == False:
                if (ameniza.get() == 1):
                    plt.plot(tempo, output2)
                else:
                    plt.plot(tempo, redCVT)  
            else:
                if (ameniza.get() == 1):
                    plt.plot(colunas[columnTempo], output2)
                else:
                    plt.plot(colunas[columnTempo], redCVT)
        imgNome=y.split('.')[0] + '_a'+ '.png'
        z = 'bcdefghijklmnopqrstuv'
        w = 0
        try:
            while imgNome.split('\\')[-1] in os.listdir(pastatxt):
                imgNome=y.split('.')[0] + '_' + z[w] + '.png'
                w+= 1
            print(imgNome)
            plt.grid()
            plt.savefig(imgNome)
        except:
            print("Failed to achieve a name")
    '''
    except Exception:
        flag = 1
        erro("Houve um problema", "red")
    '''
    if (flag == 0):
        erro("Imagens salvas", "green")
        timea.sleep(2)
        plt.close()

        
        #Adcionar mensagem de sucesso

def erro(msgDeErro, color):
    msgLabel['foreground'] = color
    msgLabel['text'] = msgDeErro
    root.update()


def fechar():
    root.destroy()

def pre():
    #Abrir todos os arquivos de uma pasta
    #Dados na ordem: Tempo, RPM, Velocidade
    #Não deve ter texto no arquivo #Melhorar isso
    #Colocar opção de com ou sem passa baixa
    #Opção de redução por tempo, rpm por velocidade
    try:
        flag = 0
        if (tipo.get() == 'Pasta com .txt'):
            erro("A pré-visualização não pode ser\nfeita com pastas", "red")
            flag == 1
        buscaNum = re.compile(r'''
            (\d)+
        ''', re.VERBOSE)
        exampleData = []
        txt = arquivo.get()
        if flag == 0:
            try:
                exampleFile = open(txt, 'r')
            except:
                flag = 1
                erro("Houve um problema na\nabertura do arquivo.", "red")
        if flag == 0:
            for linha in exampleFile.readlines():
                linha = linha.replace(linha[-1], '')
                exampleData.append(linha)
            exampleFile.close()
            #print(exampleData)
            colunaUm = []
            colunaDois = []
            colunaTres = []
            flag = 0
            flag1 = 0
            colunas = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
            #Falta tirar as palavras
            def criaMatriz():
                #Adaptar o código p separar por espaço e duplo espaço
                #Tirar caracteres especiais
                try:
                    temp = exampleData[0].split(' ')
                    tentativa = temp.index('')
                    errorFlag = 1
                except:
                    errorFlag = 0
                if errorFlag == 0:
                    l = exampleData[0].split(' ')
                    for cool in range(0, len(l)):
                        colunaUm = []
                        flag = 0
                        mediacool = 0
                        totalcool = 0
                        for i in range(0, len(exampleData)):
                            l = exampleData[i].split(' ')
                            if buscaNum.search(l[cool]) != None:
                                l[cool] = buscaNum.search(l[cool]).group()    
                            else:
                                l[cool] = '0'
                            try:
                                colunaUm.append(float(l[cool]))
                            except:
                                errorFlag = 1
                                break
                        colunas[cool] = colunaUm
                    return colunas #Matriz na forma [colunas][linhas]. última linha é len(exampleData) - 1
                if errorFlag == 1:
                    l = exampleData[0].split('  ')
                    col = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
                    for cool in range(0, len(l)):
                        colunaUm = []
                        flag = 0
                        mediacool = 0
                        totalcool = 0
                        for i in range(0, len(exampleData)):
                            l = exampleData[i].split('  ')
                            if buscaNum.search(l[cool]) != None:
                                l[cool] = buscaNum.search(l[cool]).group()    
                            else:
                                l[cool] = '0'
                            colunaUm.append(float(l[cool]))
                        col[cool] = colunaUm
                    return col
            colunas = criaMatriz()
            tempo = []
            columnTempo = colunaTempo.get() - 1
            columnRPM = colunaRPM.get() - 1
            columnVelocidade = colunaVelocidade.get() - 1
            try:
                per = 1000/(colunas[columnTempo].index(2) - colunas[columnTempo].index(1))
                print(per) 
            except:
                print("Possivelmente o tempo está em millisegundos")
                per = 0
            print(type(colunas[columnTempo][0]))
            T = int(colunas[columnTempo][len(exampleData) - 1]) - int(colunas[columnTempo][0])
            deltaTtotal = 0
            redCVT = []
            time = 0
            repet = False
            for r in range(0, len(exampleData)):
                if(colunas[columnTempo][r] > 1000):
                    repet = True #O tempo está em millisegundos
                time = time + per
                tempo.append(time)
            #----------------PASSA BAIXA--------------------------#
            for i in range(1, len(exampleData)):
                deltaT = int(colunas[columnTempo][i]) - int(colunas[columnTempo][i - 1])
                deltaTtotal = deltaTtotal + deltaT
                deltaTmedio = deltaTtotal / i
            print(deltaTmedio)
            fs = 1000 / deltaTmedio
            if repet == False:
                #Melhorar isso
                fs = 1000 / per
            #fs = 2 * fs #Opç~çao de deixar o gráfcio mais claro
            print(fs)
            cutoff = float(lowpass.get())
            nyq = 0.5 * fs
            order = 2
            n = len(exampleData)
            w = cutoff / (fs / 2)
            b, a = signal.butter(2, w, output= 'ba')

            for i in range(1, len(exampleData)):
                motor = colunas[columnRPM][i]
                vel = colunas[columnVelocidade][i]
                if antideslizamento.get() == 1:
                    if vel > 60 and i > 0: #Colocar isso como opcional (filtro para deslizamento)
                        vel = colunas[columnRPM][i - 1]
                        colunas[columnVelocidade][i] = colunas[columnVelocidade][i-1]
                try:
                    #Checar se é 7.3 mesmo, ou 7.47
                    x = motor/(vel * 9.09 * 7.47)
                except:
                    x = 0
                redCVT.append(x)
            redCVT.append(redCVT[-1])
            output = signal.filtfilt(b, a, colunas[columnRPM])#botar redCVT
            output1 = signal.filtfilt(b, a, colunas[columnVelocidade])
            output2 = signal.filtfilt(b, a, redCVT)
            fig, ax = plt.subplots()
            print(graph.get())
            if (graph.get() == 'Velocidade x RPM'):
                plt.title("Velocidade x RPM")
                plt.xlabel("Velocidade (km/h)")
                plt.ylabel("RPM")
                if(ameniza.get() == 1):
                #plt.plot(tempo, output1)
                    plt.plot(output1, output)
                else:
                    plt.plot(colunas[columnVelocidade], output)
            if (graph.get() == 'Tempo x redução'):
                plt.title("Tempo x redução")
                plt.xlabel("Tempo (ms)")
                plt.ylabel("Redução")
                if repet == False:
                    if (ameniza.get() == 1):
                        plt.plot(tempo, output2)
                    else:
                        plt.plot(tempo, redCVT)
                else:
                    if (ameniza.get() == 1):
                        plt.plot(colunas[columnTempo], output2)
                    else:
                        plt.plot(colunas[columnTempo], redCVT)
            #plt.savefig('teste.png')
            plt.show()
    except:
        erro("Houve um erro", "red")

#---------------------ROOT------------------------

root = tk.Tk() #Cria a janela principal
root.title("UFPBaja - Curva da CVT                                                                                                                                                 Rafael Benatti") #Define o título da janela
root.geometry("810x208") #Define o tamanho

#---------------------FRAME-----------------------

frame = ttk.Frame(root,  padding = "0") #Cria um frame, que permite que alguns comandos pra organizar as coisas (textos, imagens, botões) sejam usados
frame.pack(fill=tk.BOTH, expand=True) #pack é um método utilizado para que as coisas apareçam na janela principal, entretanto, a frame é invísvel
#De qualquer forma, é preciso usar o método pack para a frame, como foi utilizado acima

#--------------------ARQUIVO LABEL----------------

arquivoLabel = ttk.Label(frame, text = "Digite o endereço do arquivo que será utilizado: ")#Label é um bloco de texto. Aqui é utilizado para 
#solicitar que o usuário digite o endereço do arquivo que será utilizado para gerar o gráfico
formatoLabel = ttk.Label(frame, text = "Ex.: \"C:\\\\pasta1\\\\pasta2\\\\pasta3\\\\arquivo.txt\"") #Aqui um exemplo de como o usuário deverá escrever o diretório do arquivo
#São utilizadas 4 '\', mas só aparecem duas, já que a '\' é um caractere especial, dessa forma para que apareça uma contrabarra na
#janela principal é necessário escrever '\\'
arquivoLabel.grid(column = 0, row = 0, sticky = tk.W, pady = 5, padx = 10)#Aqui é utilizado o método grid para que os objetos criados apareçam na janela principal
#Assim como 'pack()', 'grid()' serve para fazer as coisas aparecerem, entretanto recebe alguns parâmetros a mais, permitindo uma organização mais precisa
formatoLabel.grid(column = 0, row = 1, sticky = tk.W, padx = 10)

#-----------------ARQUIVO OU PASTA-----------------

tipo = tk.StringVar()
tipoMenu = ttk.OptionMenu(frame, tipo, "Arquivo .txt", "Arquivo .txt", "Pasta com .txt")
tipoMenu.grid(column = 0, row = 0, sticky = tk.W, padx = 700)

#---------------CAIXA DE TEXTO DO ARQUIVO----------

arquivo = tk.StringVar()
arquivoEntry = ttk.Entry(frame, width = 70, textvariable = arquivo)
arquivoEntry.grid(column = 0, row = 0, sticky = tk.W, pady = 5, padx = 270)

#--------------------CHECKBUTTON AMENIZAÇÃO--------------

ameniza = tk.IntVar()
amenizar = ttk.Checkbutton(frame, text = "Amenizar curva", variable = ameniza, onvalue = 1, offvalue = 0)
amenizar.grid(column = 0, row = 2, sticky = tk.W, padx = 10, pady = 10)

#-----------------FILTRO PASSA BAIXA--------------------

lowpass = tk.StringVar()
lowpassLabel = ttk.Label(frame, text = "Filtro passa baixa: ")
lowpassLabel.grid(column = 0, row = 3, sticky = tk.W, padx = 180)
lowpassOptioMenu = ttk.OptionMenu(frame, lowpass, '-1','Sem filtro', '1.0', '1.5', '2.0', '2.5', '3.0', '3.5', '4.0', '4.5', '5.0', '5.5', '6.0')
lowpass.set('1.5')
lowpassOptioMenu.grid(column = 0, row = 3, sticky = tk.W, padx = 290)

#--------------------COLUNA DO TEMPO------------------

colunaTempo = tk.IntVar()
colunaTempoLabel = ttk.Label(frame, text = "Coluna do tempo: ")
colunaTempoLabel.grid(column = 0, row = 2, sticky = tk.W, padx = 150)
colunaTempoSelect = ttk.OptionMenu(frame, colunaTempo, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
colunaTempo.set(1)
colunaTempoSelect.grid(column = 0, row = 2, sticky = tk.W, padx = 250)

#---------------------COLUNA DO RPM----------------------

colunaRPM = tk.IntVar()
colunaRPMLabel = ttk.Label(frame, text = "Coluna do RPM: ")
colunaRPMLabel.grid(column = 0, row = 2, sticky = tk.W, padx = 300, pady = 5)
colunaRPMSelect = ttk.OptionMenu(frame, colunaRPM, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
colunaRPM.set(2)
colunaRPMSelect.grid(column = 0, row = 2, sticky = tk.W, padx = 390, pady = 5)

#-------------------COLUNA DA VELOCIDADE------------------

colunaVelocidade= tk.IntVar()
colunaVelocidadeLabel = ttk.Label(frame, text = "Coluna da velocidade: ")
colunaVelocidadeLabel.grid(column = 0, row = 3, sticky = tk.W, padx = 10)
colunaVelocidadeSelect = ttk.OptionMenu(frame, colunaVelocidade, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
colunaVelocidade.set(3)
colunaVelocidadeSelect.grid(column = 0, row = 3, sticky = tk.W, padx = 130)

#------------------------BOTÕES---------------------------

button1 = ttk.Button(frame, text="Enviar", command = save) #Cria um botão na frame definindo um texto e uma função que será chamada quando o botão for apertado
button1.grid(column = 0, row = 5, sticky = tk.W, padx = 715) #Permite que o botão apareça
button2 = ttk.Button(frame, text = "Cancelar", command = fechar)
button2.grid(column = 0, row = 5, sticky = tk.W, padx = 637)
button3 = ttk.Button(frame, text = "Pré-visualização", command = pre)
button3.grid(column = 0, row = 5, sticky = tk.W, padx = 250, pady = 10)#Adcionar um command

#------------------ESCOLHA DE GRÁFICOS-------------------

graph = tk.StringVar()
graphLabel = ttk.Label(frame, text = 'Tipo de gráfico: ')
graphEscolha = ttk.OptionMenu(frame, graph, 'Velocidade x RPM', 'Velocidade x RPM', 'Tempo x redução')
graphLabel.grid(column = 0, row = 4, sticky = tk.W, padx = 10, pady = 10)
graphEscolha.grid(column = 0, row = 4, sticky = tk.W,  padx = 100)

#----------------CHECKBUTTON ANTIDESLIZAMENTO-------------

antideslizamento = tk.IntVar(value = 1)
antideslizamentoButton = ttk.Checkbutton(frame, text = "Filto antideslizamento para a roda", variable = antideslizamento, onvalue = 1, offvalue = 0)
antideslizamentoButton.grid(column = 0, row = 4, sticky = tk.W, padx = 240)

#---------------------MENSAGEM DE ERRO--------------------

msgLabel = ttk.Label(frame, text = "", foreground = 'red')
msgLabel.grid(column = 0, row = 4, sticky = tk.W, padx = 600)

#------------------------MAINLOOP-------------------------

root.mainloop()