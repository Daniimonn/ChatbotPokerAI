import streamlit as st
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from crewai import Agent, Task, Crew, LLM
from groq import Groq
import datetime
import os
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Función para guardar feedback en Google Sheets
def guardar_feedback_en_drive(feedback, comments):
    credentials_json = json.loads(st.secrets["GOOGLE_SHEETS_CREDENTIALS"])
    sheet_id = st.secrets["SHEET_ID"]

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
    client = gspread.authorize(creds)
    
    sheet = client.open_by_key(sheet_id).sheet1
    sheet.append_row([str(datetime.datetime.now()), feedback, comments])

st.set_page_config(page_title="PokerStarsAI", layout="centered")

# Botones para seleccionar agentes
if st.sidebar.button("💬 PokerStars AI"):
    st.session_state.agente_seleccionado = None
    st.session_state.first_interaction = True
    st.rerun()
st.write("")
st.sidebar.title("Agentes disponibles:")
if st.sidebar.button("🧠 Coach Poker"):
    st.session_state.agente_seleccionado = "Coach Poker"
    st.session_state.first_interaction = True
    st.rerun()
if st.sidebar.button("🃏 Evaluador Mano"):
    st.session_state.agente_seleccionado = "Evaluador Mano"
    st.session_state.first_interaction = True
    st.rerun()
if st.sidebar.button("🎲 Simulador Jugada"):
    st.session_state.agente_seleccionado = "Simulador Jugada"
    st.session_state.first_interaction = True
    st.rerun()
if st.sidebar.button("🛠 Soporte Técnico"):
    st.session_state.agente_seleccionado = "Soporte Técnico"
    st.session_state.first_interaction = True
    st.rerun()

# Selección de modelo y configuración
st.sidebar.markdown("---")
st.sidebar.title("Configuración del Modelo")
model_source = st.sidebar.radio(
    "Elige el modelo a usar:",
    ("Modelos en la Nube - Groq", "Modelo Local - llama3.2")
)
if model_source == "Modelos en la Nube - Groq":
    modelo_groq = st.sidebar.radio(
        "Selecciona el modelo Groq:",
        ("llama-3.3-70b-versatile", "gemma2-9b-it"),
        index=0
    )
    modelo_final = modelo_groq
else:
    modelo_final = "llama3.2"

# Instanciar el modelo
if model_source == "Modelo Local - llama3.2":
    from langchain_ollama import OllamaLLM
    llm = OllamaLLM(model=modelo_final, temperature=0.7, top_p=0.9, max_tokens=150)
else:
    llm = LLM(
        model=f"groq/{modelo_final}",
        temperature=0.5,
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY")
    )

# Crear agentes
coach_poker = Agent(
    role="Entrenador de Estrategia de Póker",
    goal="Ayudar al usuario a mejorar su juego ofreciendo consejos según la fase actual",
    backstory="""Eres un entrenador veterano especializado en mejorar estrategias de póker.
                Tu función es ayudar a los jugadores a tomar mejores decisiones estratégicas según la fase de la partida 
                (preflop, flop, turn, river). SOLO respondes preguntas relacionadas con estrategia de juego. 
                Si alguien te hace una pregunta fuera de ese tema (como reglas, soporte técnico, simulaciones o evaluación de manos), 
                responde de forma educada que no puedes ayudar con eso. Responde siempre en español y añade siempre al final que escribiendo 'Salir' se puede finalizar el chat.""",
    allow_delegation=False,
    llm=llm
)
evaluador_mano = Agent(
    role="Evaluador de manos",
    goal="Analizar la fuerza de una mano de póker en contexto",
    backstory="""Eres un experto en evaluar manos de póker y calcular probabilidades de ganar en tiempo real. 
                Tu función es analizar la fuerza de una mano según el contexto de la partida. SOLO debes responder a preguntas relacionadas con la evaluación de manos. 
                No debes responder preguntas sobre estrategia, simulaciones o soporte técnico. 
                Si te preguntan algo fuera de tu especialidad, responde educadamente que no puedes ayudar con eso. Responde siempre en español y añade siempre al final que escribiendo 'Salir' se puede finalizar el chat.""",
    allow_delegation=False,
    llm=llm
)
simulador_jugada = Agent(
    role="Simulador de decisiones",
    goal="Simular resultados de diferentes decisiones en una mano",
    backstory="""Eres un simulador especializado en analizar qué podría ocurrir si un jugador apuesta, iguala o se retira en una mano concreta. 
                Simulas diferentes escenarios posibles en base a la decisión del jugador. SOLO debes responder preguntas relacionadas con simulaciones de jugadas. 
                No debes dar consejos estratégicos ni evaluar la fuerza de manos. Si te preguntan algo fuera de tu función, responde amablemente que no puedes ayudar con eso. Responde siempre en español y añade siempre al final que escribiendo 'Salir' se puede finalizar el chat.""",
    allow_delegation=False,
    llm=llm
)
soporte_tecnico = Agent(
    role="Técnico de soporte",
    goal="Resolver problemas técnicos del usuario con la plataforma",
    backstory="""Eres un especialista en soporte técnico para plataformas de póker online.
                Tu función es resolver problemas técnicos como errores de conexión, cuentas, rendimiento de la app, etc. SOLO debes responder preguntas de soporte técnico.
                No estás autorizado a dar consejos de juego, evaluar manos o simular jugadas. Si alguien te pregunta sobre esos temas, responde educadamente que no es tu campo. Responde siempre en español y añade siempre al final que escribiendo 'Salir' se puede finalizar el chat.""",
    allow_delegation=False,
    llm=llm
)

agentes = {
    "Coach Poker": coach_poker,
    "Evaluador Mano": evaluador_mano,
    "Simulador Jugada": simulador_jugada,
    "Soporte Técnico": soporte_tecnico
}

chatbot_system_message = SystemMessage(
    content="Eres un asistente experto en reglas del póker. Responde de forma clara, profesional y concisa solo a preguntas que tengan que ver con las reglas y a palabras técnicas. Añade siempre al final que escribiendo 'Salir' se puede finalizar el chat."
)

# Variables de estado
if "messages" not in st.session_state:
    st.session_state.messages = [chatbot_system_message]
if "message_agents" not in st.session_state:
    st.session_state.message_agents = ["Asistente PokerStars"]
if "feedback_pending" not in st.session_state:
    st.session_state.feedback_pending = False
if "chat_finished" not in st.session_state:
    st.session_state.chat_finished = False
if "agente_seleccionado" not in st.session_state:
    st.session_state.agente_seleccionado = None
if "first_interaction" not in st.session_state:
    st.session_state.first_interaction = False
if "ultimo_agente" not in st.session_state:
    st.session_state.ultimo_agente = None

st.markdown("<h1 style='text-align: center;'>👋 Hola, soy PokerStars AI</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>¿En qué puedo ayudarte hoy?</h5>", unsafe_allow_html=True)

# Mostrar historial de mensajes
for i, message in enumerate(st.session_state.messages):
    if i == 0:
        continue
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        nombre = "Tú" if isinstance(message, HumanMessage) else st.session_state.message_agents[i]
        st.markdown(f"**{nombre}**")
        st.markdown(message.content)

# Entrada del usuario
if not st.session_state.chat_finished:
    prompt = st.chat_input("Escribe tu mensaje...")
    if prompt:
        st.session_state.first_interaction = True
        if prompt.strip().lower() == "salir":
            st.session_state.feedback_pending = True
        else:
            st.session_state.messages.append(HumanMessage(content=prompt))
            st.session_state.message_agents.append(None)

            with st.spinner("Pensando..."):
                if st.session_state.agente_seleccionado:
                    task = Task(
                        description=prompt,
                        expected_output="Respuesta clara y útil para el usuario.",
                        agent=agentes[st.session_state.agente_seleccionado]
                    )
                    crew = Crew(
                        agents=[agentes[st.session_state.agente_seleccionado]],
                        tasks=[task],
                        verbose=False
                    )
                    result = crew.kickoff()
                    response_text = result.output if hasattr(result, "output") else str(result)
                    agente_nombre = st.session_state.agente_seleccionado
                else:
                    def groq_invoke(messages):
                        chat_history = [{"role": "system", "content": messages[0].content}] + [
                            {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
                            for m in messages[1:]
                        ]
                        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                        response = client.chat.completions.create(
                            model=modelo_final,
                            messages=chat_history
                        )
                        return response.choices[0].message.content

                    response_text = groq_invoke(st.session_state.messages)
                    agente_nombre = "Asistente PokerStars"

            st.session_state.messages.append(AIMessage(content=response_text))
            st.session_state.message_agents.append(agente_nombre)
            st.rerun()

# Feedback
if st.session_state.feedback_pending:
    st.subheader("📝 Valoración del Servicio")
    feedback = st.slider("¿Qué tan satisfecho estás con nuestro chatbot?", 1, 5, 3)
    comments = st.text_area("¿Tienes alguna sugerencia?")
    if st.button("Enviar valoración"):
        guardar_feedback_en_drive(feedback, comments)
        st.success("¡Gracias por tu valoración!")
        st.session_state.feedback_pending = False
        st.session_state.chat_finished = True
        st.rerun()
    elif st.button("Cerrar sin enviar"):
        st.success("Valoración cerrada.")
        st.session_state.feedback_pending = False
        st.session_state.chat_finished = True
        st.rerun()

if st.session_state.chat_finished:
    st.warning("El chat ha finalizado. Gracias por utilizar nuestro servicio.")
