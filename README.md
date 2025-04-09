
# 🃏 PokerStarsAI 

Esta app está desarrollada con **Streamlit** y usa agentes inteligentes con `CrewAI`, integrando modelos Groq y feedback del usuario en tiempo real guardado en **Google Sheets**.

---

## 🚀 ¿Qué hace esta app?

- Te permite chatear con 4 agentes especializados en póker:
  - 🧠 **Coach Poker**: Te aconseja estrategias.
  - 🃏 **Evaluador Mano**: Evalúa la fuerza de tus cartas.
  - 🎲 **Simulador Jugada**: Simula qué pasaría si apuestas, igualas o te retiras.
  - 🛠 **Soporte Técnico**: Resuelve problemas técnicos de la plataforma.
- También puedes usar el **Asistente General** para dudas de reglas.
- Guarda el **feedback del usuario en una hoja de cálculo de Google Sheets.**

---

## 🧠 Tecnologías utilizadas

- `Streamlit` para la interfaz web
- `CrewAI` para la arquitectura de agentes
- `Groq` para ejecutar modelos LLM en la nube (como LLaMA 3 o Gemma)
- `gspread` + `oauth2client` para guardar feedback en Google Sheets
- `Langchain` como middleware para llamadas LLM

---

## 📬 Contacto

Desarrollado por Daniel Montalvo · Proyecto académico para la materia **Agentes Inteligentes**.
Este proyecto no está afiliado con PokerStars 