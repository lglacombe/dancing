import tkinter as tk
from tkinter import font
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import serial
import json
import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from datetime import datetime
import threading
from queue import Queue
import whisper
import re
import google.generativeai as genai 
os.environ["PATH"] += os.pathsep + "C:\\Users\\aula2\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-7.1.1-full_build\\bin\\ffmpeg.exe"
auth_manager = SpotifyOAuth(
        client_id='c12b4448d82d468a9269611bfded3b91',
        client_secret='8dc438bb5a1d4da09046354443505b31',
        redirect_uri='http://127.0.0.1:8888/callback',
        scope='user-read-playback-state user-modify-playback-state',
        cache_path='.spotipy_cache',
        show_dialog=True)
token = auth_manager.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth_manager=auth_manager)

GEMINI_API_KEY = "AIzaSyDfMon89KuIcT4Eb-1QwXuD8_OomctKqdY"

print("\n[3] Enviando para Gemini...")

genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel('gemini-2.0-flash')
output_model ="""
[   {

     "start_time": "00:00",

     "end_time": "00:05",

    "actions": [   

   { "type": "gesture", "name": "hands_up" },

 { "type": "movement", "name": "move_right", "repeat": 2, "speed": "fast"}

   ]   },

 {   

"start_time": "00:05",  

 "end_time": "00:08",   

"actions": [   

  { "type": "movement", "name": "bounce", "speed": "slow" }   

]

  } ]"""


class ArduinoCommunication:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.response_queue = Queue()
        self.running = False
        self.thread = None
        
    def start(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  
            self.running = True
            self.thread = threading.Thread(target=self._read_from_arduino)
            self.thread.daemon = True
            self.thread.start()
            print("Comunicação com Arduino iniciada")
            return True
        except Exception as e:
            print(f"Erro ao conectar ao Arduino: {e}")
            return False
    
    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        print("Comunicação com Arduino encerrada")
    
    def _read_from_arduino(self):
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    if line:
                        self.response_queue.put(line)
                        print(f"ARDUINO: {line}")
            except Exception as e:
                print(f"Erro na leitura do Arduino: {e}")
                time.sleep(1)
    
    def send_command(self, actions):
        if actions == 'parado':
            self.serial_conn.write(('parado' + '\n').encode('utf-8'))
            return True
        try:
            formatted = self._format_command(actions)
            if not formatted:
                return False
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.write((formatted + '\n').encode('utf-8'))
                return True
            return False
        except Exception as e:
            print(f"Erro ao enviar comando: {e}")
            return False
    
    def _format_command(self, actions):
        try:
            movimento = ""
            quantidade = "1"
            velocidade = "medium"
            gesto = "disco"
            quantidade_gesto = "1"
            
            # Processa movimento
            movs = [a for a in actions if a['type'] == 'movement']
            if movs:
                mov = movs[0]
                movimento = mov['name']
                quantidade = str(mov.get('repeat', 0) + 1)
                velocidade = mov.get('speed', 'medium')
            
            # Processa gesto
            gests = [a for a in actions if a['type'] == 'gesture']
            if gests:
                gest = gests[0]
                gesto = gest['name']
                quantidade_gesto = str(gest.get('repeat', 0) + 1)
            print(f"{gesto}")
        
            return f"{gesto}" #"f"{movimento},{quantidade},{velocidade},{gesto}"
            
        except Exception as e:
            print(f"Erro ao formatar comando: {e}")
            return None
    
    def get_response(self):
        if not self.response_queue.empty():
            return self.response_queue.get()
        return None

class GravadorAudio:
    def __init__(self):  
        self.gravar = False
        self.frames = []
        self.sample_rate = 44100
        self.filename = ""
    
    def iniciar_gravacao(self, musica_nova):
        """Inicia a gravação usando o nome da música da variável musica_nova"""
        if self.gravar:
            print("Já está gravando!")
            return
        
        # Remove caracteres inválidos para nome de arquivo
        nome_arquivo = f"{musica_nova.replace('/', '-').replace(':', '')}.mp3"
        self.filename = nome_arquivo
        
        self.frames = []
        self.gravar = True
        print(f"Gravando: {musica_nova}...")
        
        try:
            self.stream = sd.InputStream(
                device = 7,  # 5 Ou 7 testar com print(sd.query_devices())
                samplerate=self.sample_rate,
                channels=2,
                callback=self.callback_gravacao,
                dtype='float32'
            )
            self.stream.start()
            print("Stream iniciado com sucesso!")
        except Exception as e:
            self.gravar = False
            print(f"Falha ao iniciar stream: {e}")
        
    
    def callback_gravacao(self, indata, frames, time, status):
        if self.gravar:
            self.frames.append(indata.copy())
              
    def parar_gravacao(self):
        if not self.gravar:
            print("Nenhuma gravação ativa!")
            return
        
        self.gravar = False
        self.stream.stop()
        self.stream.close()
        
        audio_gravado = np.concatenate(self.frames, axis=0)
        
        # Salva como MP3 (requer libav ou ffmpeg instalado)
        sf.write(self.filename, audio_gravado, self.sample_rate, format='mp3')
        print(f"Áudio salvo como: {self.filename}")
        
        return self.filename


# Variáveis globais
tocando = False
ja = True
musica_atual = ""
atual_sec = 0
total_sec = 0
musica_nova = None
IA = ""
gravador = GravadorAudio()
para_ms = False
para_mf = False

arduino = ArduinoCommunication('COM22', 9600)
arduino.start()
def extrair_json(texto):
    # Expressão regular para capturar o conteúdo entre ```json e ```
    match = re.search(r'```json\s*(.*?)\s*```', texto, re.DOTALL)
    if match:
        json_str = match.group(1).strip()  # Remove espaços extras
        try:
            dados = json.loads(json_str)
            return dados
        except json.JSONDecodeError as e:
            print("Erro ao decodificar o JSON:", e)
            print("Conteúdo problemático:", json_str)
    else:
        print("JSON não encontrado no texto.")
    return None

def play_pause():
    global tocando
    tocando = not tocando
    if tocando:
        play_pause_btn.config(text="⏸")
        try:
            sp.start_playback()
        except:
            print("Erro spotify1")
        #print("Comando PLAY enviado")
    else:
        play_pause_btn.config(text="▶")
        try:
            sp.pause_playback()
        except:
            print("Erro spotify2")
        #print("Comando PAUSE enviado")
def pausa_slider(event):
    sp.pause_playback()

def atualiza_tempo(atual_sec, total_sec):
    atual_min, atual_sec = divmod(atual_sec, 60)
    total_min, total_sec = divmod(total_sec, 60)
    
    tempo = f"{atual_min:02d}:{atual_sec:02d} / {total_min:02d}:{total_sec:02d}"
    campo_tempo.config(text=tempo)

def musica(event):
    global musica_nova, musica_atual
    nome = escolhe_musica.get().strip()
    if nome:
        try:
            resultado = sp.search(q=nome, type='track', limit=1)
            tracks = resultado.get('tracks', {}).get('items', [])
            if tracks:
                uri = tracks[0]['uri']
                sp.start_playback(uris=[uri])
                musica_nova = tracks[0]['name']
                escolhe_musica.delete(0, tk.END)
            else:
                print("Música não encontrada")
        except Exception as e:
            print("Erro ao buscar/tocar spotify:", e)
        musica_nova = nome
        escolhe_musica.delete(0,tk.END)

def atualizar_tempo(valor):
    valor = int(valor)
    pos_mili = total_sec*1000
    pos_nova = int(pos_mili*(valor/100))
    
    sp.seek_track(pos_nova)
    
def tempo_seg(t):
    m, s = map(int, t.split(':'))
    return m * 60 + s

def format_timestamp(segundos):
    minutos = int(segundos // 60)
    segundos_restantes = segundos % 60
    return f"{minutos:02}:{segundos_restantes:06.3f}"

def atualizar_interface():
    global atual_sec, total_sec, musica_atual, musica_nova, tocando , IA , ja,para_ms,para_mf
    
    
    playback = sp.current_playback()
    if playback and playback['is_playing']:
        tocando = True
        play_pause_btn.config(text="⏸")
        atual_sec = playback['progress_ms'] // 1000
        total_sec = playback['item']['duration_ms'] // 1000
        slider_tempo.set(int((atual_sec/total_sec)*100))
        if playback['item']['name'] != musica_atual:
            musica_atual = playback['item']['name']
            nome_musica.config(text=musica_atual)
    else:
        tocando = False
        play_pause_btn.config(text="▶")
    
        
    atualiza_tempo(atual_sec, total_sec)
    if tocando and atual_sec >= total_sec-1 and gravador.gravar:
        gravador.parar_gravacao()
        CAMINHO_ARQUIVO = musica_atual +".mp3"
        try:
            sp.pause_playback()
        except:
            print("Erro spotify2")
        print("[1] Carregando modelo Whisper...")
        model = whisper.load_model("medium")  # você pode usar "small" ou "medium" se quiser mais precisão

        print(f"[2] Transcrevendo áudio {CAMINHO_ARQUIVO} com timestamps...")
        resultado = model.transcribe(CAMINHO_ARQUIVO)

        musica = ""
        for segmento in resultado["segments"]:
            inicio = segmento["start"]
            fim = segmento["end"]
            texto = segmento["text"]

            musica += f"[{inicio:.2f}s - {fim:.2f}s] {texto}\n"
        print("Transcrição completa!")
        
        print(musica)
        
        print("Enviando transcrição para o Gemini...")
        genai.configure(api_key=GEMINI_API_KEY)

        modelo_gemini = genai.GenerativeModel("models/gemini-2.0-flash")
        prompt = f"""Prompt Title:
Generate Expressive Choreography for a Humanoid Robot Based on Timed Song Lyrics

Prompt:

You are choreographing a performance for a humanoid robot based on a song's lyrics and timestamps. The robot has articulated shoulders and arms and is capable of coordinated full-body movements across a horizontal scale ranging from 0 to 100, with its current position at {{current_position}}.

Robot Capabilities
1. Horizontal Body Movement (each moves the robot 10 units):
move_left: Moves the robot 10 units to the left.

move_right: Moves the robot 10 units to the right.

These commands can be:

Repeated to achieve larger displacements (e.g., two move_left = 20 units).

Combined with arm gestures in the same timestamp window.

bounce: A predefined rhythmic sequence: left → right → left → right.

2. Pre-Programmed Arm Gestures:

euphoric

neutral

happy

sad

loving

These gestures can be used alone or combined with horizontal movements in a single interval and can be Assigned a speed modifier: slow, neutral (default), or fast..

Your Objective
Given a list of lyrics with timestamps, assign meaningful and expressive robot commands that match the rhythm, mood, and energy of each lyrical segment. Ensure the choreography:

Enhances the performance visually and emotionally.

Reflects sentiment changes in the lyrics.

Uses smooth and logical transitions.

Respects the robot’s movement capabilities and boundaries (0–100 range).
IMPORTANT INSTRUCTIONS:
1. Timestamps will be received in format [seconds.miliseconds]
2. You will always output MM:SS format for timestamps [Minutes:Seconds].
3. Only output the JSON array, without any additional text or explanations
4. There need to always be an gesture in every timestamp
5. Follow exactly this example format:


Output Format
Produce an array of commands in this structured format:
{output_model}


Letra:
{musica}
""" 

        resposta = modelo_gemini.generate_content(prompt)
        print(resposta)
        

        print("\n[4] Resposta do Gemini:\n")
        try:
            # Extrai o JSON da resposta usando expressão regular
            json_extraido = extrair_json(resposta.text)

# Exibindo resultado (ou use json_extraido diretamente em seu código)
            if json_extraido:
                print(json.dumps(json_extraido,indent=2))
            
            with open(f'{musica_atual}.json', 'w') as f:
                json.dump(json_extraido, f, indent=4)
            ja = True
        except (AttributeError, json.JSONDecodeError) as e:
            print(f"Erro ao processar resposta do Gemini: {e}")
            # Fallback: grava a resposta completa se não conseguir extrair JSON
            with open(f'{musica_atual}.json', 'w') as f:
                json.dump(resposta.text, f, indent=4)
            ja = True

    if musica_nova is not None:
        try:       
            resultado = sp.search(q=musica_nova, type='track', limit=1)
            if resultado['tracks']['items']:
                uri = resultado['tracks']['items'][0]['uri']
                sp.start_playback(uris=[uri])
                musica_atual = resultado['tracks']['items'][0]['name']
                nome_musica.config(text=musica_atual)
                print(f"Tocando agora: {musica_atual}")
                
            if not os.path.exists(musica_atual + ".json"):
                gravador.iniciar_gravacao(musica_atual)
                print("Começa gravar")
            
        except:
            print("Erro spotify4")
        musica_nova = None
    if os.path.exists(musica_atual + ".json") and ja:
        with open(f'{musica_atual}.json', 'r') as f:
            IA = json.load(f)
        print("entrei load")
        for bloco in IA:
            bloco['start_seconds'] = tempo_seg(bloco['start_time'])
            bloco['end_seconds'] = tempo_seg(bloco['end_time'])
            bloco['executado'] = False
        ja = False
            
    if tocando and not gravador.gravar:
        if not para_ms:
            arduino.send_command('parado')
            para_ms = True
        for bloco in IA:
            if not bloco['executado'] and bloco['start_seconds'] <= atual_sec < bloco['end_seconds']:
                arduino.send_command(bloco['actions'])
                print(bloco['actions'])
                bloco['executado'] = True
            if bloco['end_seconds'] == atual_sec:
                bloco['executado'] = False
        if not para_mf:
            arduino.send_command('parado')
            para_mf = True
    if atual_sec >= total_sec -1:
        para_ms = False
        para_mf = False
    root.after(1000, atualizar_interface)


# Configuração da janela
root = tk.Tk()
root.title("Player de Música")
root.geometry("400x300")

frame = tk.Frame(root)
frame.pack(pady=(20, 5))

fonte = font.Font(family="Arial", size=12)

entrada = tk.Label(frame, text="Digite o nome da música:", font=fonte, cursor = "cross")
entrada.grid(column= 0, row =0)

escolhe_musica = tk.Entry(frame, font=fonte, width=30, cursor = "cross")
escolhe_musica.grid(column = 0, row =1)

btn_escolhe = tk.Button(frame,text= "OK",font=font.Font(size=10),width=3,height=1,bg="green")
btn_escolhe.bind("<Button-1>",musica)
btn_escolhe.grid(column = 1, row =1)

nome_musica = tk.Label(root, text="Nenhuma música selecionada", font=font.Font(family="Arial", size=12, weight="bold"), fg="green", cursor = "pirate")
nome_musica.pack(pady=10)

campo_tempo = tk.Label(root, text="00:00 / 00:00", font=fonte, cursor = "star")
campo_tempo.pack(pady=(10,0))

slider_tempo = tk.Scale(root, from_=0, to=100, orient="horizontal")
slider_tempo.bind("<ButtonRelease-1>", lambda event: atualizar_tempo(slider_tempo.get()))
#slider_tempo.bind("<ButtonPress-1>",pausa_slider)
slider_tempo.pack(pady=(0,0),fill="x")

play_pause_btn = tk.Button(root, text="▶", command=play_pause,font=font.Font(size=20), width=3, height=1,bg="lightblue")
play_pause_btn.pack(pady=(30, 0))

# Inicia o loop de atualização
atualizar_interface()

root.mainloop()

arduino.stop()