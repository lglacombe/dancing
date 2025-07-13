# 🤖 Robô Humanoide Coreógrafo com Inteligência Artificial

## 💡 Ideia do Projeto

Robô humanoide da cintura para cima (braços e cabeça), com deslocamento horizontal por meio de uma esteira. O robô é capaz de realizar coreografias sincronizadas com qualquer música selecionada, utilizando inteligência artificial para gerar os movimentos de forma autônoma e criativa.

## 🔩 Hardware Utilizado

- **9 Servo-motores** para controle individual de articulações (braços, cabeça, etc.), garantindo movimentos precisos.
- **Shield Servo de 16 canais**, permitindo que o Arduino controle múltiplos servos simultaneamente.
- **Motor DC** para locomoção por esteira.
- **Shield Motor**, responsável pelo controle do motor DC.

<img width="600" alt="hardware" src="https://github.com/user-attachments/assets/cc69fa6f-24c2-43e7-8202-1652f50d13de" />

## 🛠️ Estrutura e Montagem

Toda a estrutura física do robô foi:

- Modelada no **SolidWorks** 💻
- Exportada no formato **STL** e impressa em **PLA** 🖨️
- Montada com o uso de **parafusos** e **cola quente** para fixação dos servos

<img width="400" alt="estrutura" src="https://github.com/user-attachments/assets/6be24647-575c-4353-ad9b-f4171cf2be1f" />

<img width="687" height="512" alt="image" src="https://github.com/user-attachments/assets/01611b99-1f2d-42fa-bb38-82a829838a3b" />


## 🎮 Funcionamento do Código (servo_control.ino)

O código implementa um sistema de controle de movimentos para um robô humanoide com 9 servos, representando articulações como mãos, cotovelos, ombros e cabeça. Cada movimento é composto por uma sequência de poses, armazenadas em uma matriz de ângulos.

A lógica principal funciona da seguinte forma:

- O robô recebe comandos via **porta serial** (ex: `happy`, `sad`, `neutral`, etc.);
- A função `execute_move()` percorre a sequência de poses associada ao comando;
- Cada pose define os ângulos desejados para os 9 servos;
- O código realiza a interpolação entre a posição atual e a nova, movimentando os servos suavemente;
- Entre cada pose há uma pequena pausa, criando o efeito de animação contínua.

Além disso, o código conta com funções auxiliares:

- `reset_servos()`: Define os ângulos iniciais dos servos;
- `set_pose(pose[])`: Define uma pose-alvo para os servos;
- `set_angle(channel, angle)`: Converte o ângulo em pulso PWM e envia para o servo.

É possível adicionar novos movimentos criando um vetor de poses e preenchendo uma estrutura `Move` com o número de poses, velocidade e matriz de ângulos.

## ⚙️ Controle de Motor DC com a Biblioteca AFMotor

### 🔧 Funcionamento:

- O motor é inicializado com uma velocidade de **210** (valor entre 0 e 255).
- No `loop()`, ele gira:
  - **Para frente (FORWARD)** por 500 ms
  - **Para trás (BACKWARD)** por 700 ms
- O ciclo se repete indefinidamente, alternando a direção do motor.

### 📦 Requisitos:

- Shield motor baseado em **Adafruit Motor Shield v1**
- Biblioteca `AFMotor` instalada no Arduino IDE
- O motor deve estar conectado à saída **M3** do shield.


## 🎵 Integração com Spotify e Controle de Movimentos

O sistema utiliza a biblioteca [Spotipy](https://spotipy.readthedocs.io/) para se conectar à API do Spotify e controlar a reprodução de músicas. Após a autenticação, o usuário deve configurar uma **saída de áudio estéreo mix** compatível com o gravador do sistema (deve ser testado experimentalmente no computador em uso).

A partir disso, o processo segue dois cenários:

1. **Músicas não gravadas**:  
   - O sistema grava a música em reprodução via stereo mix;
   - O áudio é salvo como `.mp3` e processado por um modelo de transcrição (como **Whisper**);
   - É gerado um arquivo `.json` que associa trechos temporais da música a gestos específicos.

2. **Músicas já gravadas**:  
   - Ao tocar uma música com um `.json` correspondente, o sistema compara o tempo atual da música com os tempos definidos no arquivo;
   - Quando um gesto estiver dentro do intervalo correto, ele é enviado ao **Arduino** via uma thread separada, garantindo que a interface com o usuário permaneça responsiva;
   - O gesto é enviado em formato simples, apenas com a identificação do movimento a ser executado naquele instante.

Esse mecanismo permite que o robô execute coreografias sincronizadas com qualquer música reproduzida no Spotify.



## 🎭 Interação com a IA

Primeiramente, é estabelecida uma comunicação com a API do **Spotify** utilizando a biblioteca `spotipy` e uma interface com o usuário para selecionar qual música será tocada e controlar seus instantes de reprodução.

A partir disso, temos dois cenários possíveis:

1. 🎵 **Música já gravada**  
2. 📡 **Música não gravada**

---

### 📡 Caso 1: Música não gravada

Se a música ainda **não tiver sido processada anteriormente**, ocorre o seguinte fluxo:

- A música é gravada via **Stereo Mix** e salva como `.mp3`.
- Utiliza-se a **local Whisper** para transcrever a música.
- São obtidos os **timestamps** de cada trecho da letra.
- Após a transcrição, é enviado um **prompt** para a IA (Gemini), contendo:
  - Um modelo de **output JSON** com movimentos e gestos.
  - A letra transcrita da música.

#### 🧠 Prompt enviado:

```json
[
  {
    "start_time": "00:00",
    "end_time": "00:05",
    "actions": [
      { "type": "gesture", "name": "hands_up" },
      { "type": "movement", "name": "move_right", "repeat": 2, "speed": "fast" }
    ]
  },
  {
    "start_time": "00:05",
    "end_time": "00:08",
    "actions": [
      { "type": "movement", "name": "bounce", "speed": "slow" }
    ]
  }
]
```
#### 📝 Prompt em F-string:

```python
prompt = f'''
Prompt Title:
Generate Expressive Choreography for a Humanoid Robot Based on Timed Song Lyrics

Prompt:

You are choreographing a performance for a humanoid robot based on a song's lyrics and timestamps. The robot has articulated shoulders and arms and is capable of coordinated full-body movements across a horizontal scale ranging from 0 to 100, with its current position at {current_position}.

Robot Capabilities
1. Horizontal Body Movement (each moves the robot 10 units):
- move_left: Moves the robot 10 units to the left.
- move_right: Moves the robot 10 units to the right.
- bounce: A predefined rhythmic sequence: left → right → left → right.

These commands can be:
- Repeated to achieve larger displacements (e.g., two move_left = 20 units).
- Combined with arm gestures in the same timestamp window.

2. Pre-Programmed Movements:
- sad
- happy
- euphoric
- neutral
- loving

These gestures can be used alone or combined with horizontal movements, and can include speed modifiers: slow, neutral (default), or fast.

Your Objective:
Given a list of lyrics with timestamps, assign meaningful and expressive robot commands that match the rhythm, mood, and energy of each lyrical segment. Ensure the choreography:
- Enhances the performance visually and emotionally.
- Reflects sentiment changes in the lyrics.
- Uses smooth and logical transitions.
- Respects the robot’s movement capabilities and boundaries (0–100 range).

IMPORTANT INSTRUCTIONS:
1. Always use MM:SS format for timestamps (e.g. 00:00, 01:30)
2. Only output the JSON array, without any additional text or explanations
3. Follow exactly this example format:

Letra:
{letra_da_musica}

Output Format:
{output_model}
```
Esse prompt é enviado para o **Gemini**, que retorna um **JSON estruturado** contendo os movimentos do robô sincronizados com a música.

---

### 🎵 Caso 2: Música já gravada

Se a música **já foi processada anteriormente**, e há um arquivo JSON com os movimentos gerado previamente, então:

- Ao iniciar a reprodução da música:
  - O tempo atual da música é comparado com os intervalos do JSON.
  - Ao entrar em um intervalo programado, o comando correspondente é enviado ao Arduino.
  - Esse envio ocorre em uma thread separada, garantindo que a interface com o usuário não trave.

A mensagem enviada ao Arduino é formatada para conter apenas o gesto a ser executado naquele instante:

```text
➡️ Envio final ao Arduino: {Arduino}


## 🔋 Alimentação do Robô

Para que o robô execute os movimentos corretamente, é necessário fornecer alimentação de **5V** tanto para os **Arduinos (servos e esteira)** quanto para o **shield de servos**.

- A alimentação deve ser feita com atenção à polaridade (positivo no pino V+ e negativo no GND do shield).
- Para os arduinos, pode-se usar as portas USB de um computador, se for conveniente.

⚠️ **Atenção:** Verifique sempre a tensão e corrente da fonte antes de ligar, para evitar danos aos componentes.
