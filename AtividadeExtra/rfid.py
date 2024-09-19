import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from time import sleep, time
import signal
import sys
import csv
from autorizacoes import Autorizacoes
from negacoes import Negacoes


GPIO.setmode(GPIO.BOARD)
LED_VERDE = 8
LED_VERMELHO = 10
BUZZER = 39
GPIO.setup(LED_VERDE, GPIO.OUT)
GPIO.setup(LED_VERMELHO, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)


leitor = SimpleMFRC522()


autorizados = Autorizacoes()
negados = Negacoes()
acessos_diarios = {}
entradas_e_saidas = {}
tentativas_negadas = {}
tentativas_invasao = 0


def acionar_buzzer(frequencia, duracao):
    pwm = GPIO.PWM(BUZZER, frequencia)
    pwm.start(50)
    sleep(duracao)
    pwm.stop()

def buzzer_sucesso():
    acionar_buzzer(1000, 0.2)  

def buzzer_erro():
    acionar_buzzer(500, 0.5)  

def buzzer_invasao():
    acionar_buzzer(300, 1)  


def salvar_relatorio():
    with open('relatorio_acessos.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Colaborador", "Tempo Total (horas)", "Tentativas de Acesso Negadas", "Tentativas de Invasão"])
        
        
        for tag, tempos in entradas_e_saidas.items():
            nome = autorizados.obter_nome(tag)
            tempo_total = sum([(saida - entrada) for entrada, saida in tempos if saida]) / 3600  # Em horas
            writer.writerow([nome, f"{tempo_total:.2f}", tentativas_negadas.get(nome, 0), tentativas_invasao])

        
        for tag, nome in negados._colaboradores_negados.items():
            writer.writerow([nome, "0.00", tentativas_negadas.get(nome, 0), tentativas_invasao])

        writer.writerow(["Tentativas de Invasão", "N/A", "N/A", tentativas_invasao])

def finalizar_programa(signal, frame):
    print("\nRelatório final:")
    for tag, tempos in entradas_e_saidas.items():
        nome = autorizados.obter_nome(tag)
        tempo_total = sum([saida - entrada for entrada, saida in tempos if saida is not None]) / 3600
        print(f"{nome} esteve na sala por {tempo_total:.2f} horas.")
    
    print(f"\nTotal de tentativas de invasão: {tentativas_invasao}")
    
    salvar_relatorio()
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, finalizar_programa)

try:
    while True:
        print("Aguardando leitura do cartão...")
        tag, _ = leitor.read()
        print(f"ID do cartão lido: {tag}")
        
        if autorizados.verifica_tag(tag):
            nome = autorizados.obter_nome(tag)

            if tag not in acessos_diarios:
                acessos_diarios[tag] = True
                entradas_e_saidas[tag] = entradas_e_saidas.get(tag, []) + [(time(), None)]
                print(f"Bem-vindo(a), {nome}!")
            else:
                if entradas_e_saidas[tag][-1][1] is None:
                    entradas_e_saidas[tag][-1] = (entradas_e_saidas[tag][-1][0], time())
                    print(f"Até logo, {nome}!")
                else:
                    entradas_e_saidas[tag].append((time(), None))
                    print(f"Bem-vindo(a) de volta, {nome}!")
            
            GPIO.output(LED_VERDE, GPIO.HIGH)
            buzzer_sucesso()
            sleep(5)
            GPIO.output(LED_VERDE, GPIO.LOW)

        elif negados.verifica_tag_negada(tag):
            nome = negados.obter_nome_negado(tag)
            print(f"Você não tem acesso a este projeto, {nome}.")
            tentativas_negadas[nome] = tentativas_negadas.get(nome, 0) + 1
            
            GPIO.output(LED_VERMELHO, GPIO.HIGH)
            buzzer_erro()
            sleep(5)
            GPIO.output(LED_VERMELHO, GPIO.LOW)
        
        else:
            print("Tentativa de invasão detectada!")
            tentativas_invasao += 1
            buzzer_invasao()
            for _ in range(10):
                GPIO.output(LED_VERMELHO, GPIO.HIGH)
                sleep(0.5)
                GPIO.output(LED_VERMELHO, GPIO.LOW)
                sleep(0.5)

finally:
    GPIO.cleanup()
