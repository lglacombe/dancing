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


Interação com a IA

"""
Primeiramente estabelecesse uma comunicação com a API do Spotify utilizando da biblioteca do spotipy e da interface com o usuário para controlar qual música será tocada,
e seus instantes de reprodução, após isso temos 2 cenários possíveis, 
músicas já gravadas e músicas não gravadas, se a música já não tiver sido gravada será feita a gravação da música através de stereo mix e salva-la como mp3
para, através do uso da local whisper transcrevenmos a musica, obtendo também o timestamp de cada frase, assim que a trasncrição é completa enviamos um Prompt contendo um json como OUTPUT model,
e a letra da musica trascrita da musica, a seguir o promt:
output_model =

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

  } ]

F-string prompt = Prompt Title:
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
hands_in_heart

hands_in_head

hands_up

left_hand_up

left_hand_down

left_hand_front_to_left

right_hand_up

right_hand_down

right_hand_front_to_right

These gestures can be used alone or combined with horizontal movements in a single interval and can be Assigned a speed modifier: slow, neutral (default), or fast..

Your Objective
Given a list of lyrics with timestamps, assign meaningful and expressive robot commands that match the rhythm, mood, and energy of each lyrical segment. Ensure the choreography:

Enhances the performance visually and emotionally.

Reflects sentiment changes in the lyrics.

Uses smooth and logical transitions.

Respects the robot’s movement capabilities and boundaries (0–100 range).
IMPORTANT INSTRUCTIONS:
1. Always use MM:SS format for timestamps (e.g. 00:00, 01:30)
2. Only output the JSON array, without any additional text or explanations
3. Follow exactly this example format:

Letra:
\n{musica}

Output Format
Produce an array of commands in this structured format:
\n{output_model}
""" 
Esse prompt é então enviado para o gemini que retorna o json estruturado e pronto para servir de estrutura de dados de envio para o arduino. 
após o Json concluído caímos no outro caso onde agora temos uma música gravada sendo reproduzida, ao iniciar a reprodução de uma música com Json de mesmo nome, 
será comparado os tempos dos movimentos no Json com o tempo atual da música, ao entrar dentro do intervalo será enviado um comando para o Arduino através de uma tread em separado
para não travar a interface com o usuário. 
Esse envio será formatado para enviar somente o gesto a ser reproduzido naquele instante. {Arduino}
