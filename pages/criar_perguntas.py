import requests
from supabase.client import create_client, Client
import streamlit as st
import re
import os
import time

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
# Criando o cliente do Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Definindo a função de tradução antes de usá-la
def translate_text(text, target_language):
    try:
        system_prompt = f"Traduza o seguinte texto para {target_language}:"
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.error(f"Erro na tradução via OpenAI: {e}")
        return text

def verificar_login():
    if "user" not in st.session_state:
        st.error("Você precisa estar logado para criar questões.")
        return False
    return True

if not verificar_login():
    st.stop()  # Impede que o resto da página seja carregado se não estiver logado

def gerar_nome_tabela(email):
    return email.split('@')[0].replace('.', '_')

def generate_questions(prompt: str):
    user = st.session_state.get("user")
    if user is None:
        st.error("Você precisa estar logado para criar questões.")
        return

    email_usuario = user["email"]

    data = {
    "model": "gpt-4",
    "messages": [
        {
            "role": "system",
            "content": (
                "Você é um gerador de questões de múltipla escolha com alternativas de A a D explicação da resposta e o porque das outras serem erradas. "
                "Cada questão deve conter apenas uma alternativa correta, mas todas devem ser plausíveis, "
                "incluindo erros conceituais comuns ou armadilhas frequentes. Use o mesmo tom e estrutura de linguagem em todas as alternativas "
                "para evitar pistas.Seja Criativo e crie cada questão a ponto que cada uma seja única."
            )
        },
        {"role": "user", "content": prompt}
    ],
    "temperature": 1,
    "max_tokens": 800,
}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)

    if response.status_code == 200:
        generated_questions = response.json().get('choices', [])
    else:
        st.error("Erro ao chamar a API da OpenAI.")
        return

    questions = []
    for choice in generated_questions:
        message = choice.get("message", {})
        text = message.get("content", "").strip()

        if text:
            # Separar explicação
            explanation_start = text.find("Explicação:")
            if explanation_start != -1:
                explanation = text[explanation_start + len("Explicação:"):].strip()
                text = text[:explanation_start].strip()
            else:
                explanation = "Não foi possível encontrar a explicação."

            # Capturar a resposta correta de forma flexível
            correct_answer_match = re.search(r'(?:Alternativa|Resposta) correta:\s*([ABCD])\)', text, re.IGNORECASE)
            correct_answer = correct_answer_match.group(1) if correct_answer_match else None

            # Separar pergunta e alternativas
            question_match = re.search(r'^(.*?)\n([A-D]\).*)$', text, re.DOTALL)
            if question_match:
                question_text = question_match.group(1).strip()
                options_text = question_match.group(2).strip()
            else:
                question_text = text.strip()
                options_text = ""

            questions.append({
                "text": question_text,
                "options_text": options_text,
                "correct_answer": correct_answer,
                "explanation": explanation
            })
        else:
            print("Texto vazio retornado pela IA, Gere novamente.")
        return questions


def add_question_to_database(materia, nivel, questions, resposta_correta, explicacao, idioma):
    email_usuario = st.session_state.get("user")["email"]
    nome_tabela = gerar_nome_tabela(email_usuario)
    supabase.rpc('check_or_create_user_table', { "email": email_usuario }).execute()

    # Se questions for string, transforma em lista
    if isinstance(questions, str):
        questions = [questions]

    data = {
        "materia": materia,
        "nivel": nivel,
        "questoes": questions,
        "resposta_correta": resposta_correta,
        "explicacao": explicacao,
        "idioma": idioma,
    }

    response = supabase.table(nome_tabela).insert(data).execute()
    print("Resposta do Supabase:", response)


# Configurações do Streamlit e fundo personalizado
st.set_page_config(page_title="Criar Teste", page_icon="📋", layout="wide")

# Background personalizado 
background_image_html = """
<style>
.stApp {
  background-image: url('https://raw.githubusercontent.com/lucasgomes97/Sistema-de-provas-inteligente/main/ChatGPT%20Image%2026%20de%202025%2C%2014_39_03%20(2).png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}
</style>
"""
st.markdown(background_image_html, unsafe_allow_html=True)

# CSS adicional
custom_css = """
<style>
    .stApp {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    .stTitle, .stHeader {
        font-size: 36px;
        font-weight: bold;
        color: #FF6347;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 12px 24px;
        font-size: 18px;
        border-radius: 12px;
        transition: all 0.3s ease 0s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-3px);
    }
    .stTextInput input {
        font-size: 16px;
        padding: 12px;
        border-radius: 8px;
    }
    .stAlert {
        background-color: rgba(0, 0, 0, 0.8);
        padding: 5px;
        border-radius: 5px;
        color: white;
        font-size: 28px;
        font-weight: bold;
    }
    .stContainer {
        max-width: 800px;
        background: rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        padding: 30px;
        margin-top: 20px;
        z-index: 1;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
    }
    .stForm {
        margin-top: 20px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def get_option_text(options_text, letter):
    """
    Extrai o texto da alternativa com base na letra (A, B, C ou D)
    """
    pattern = rf"{letter}\)\s(.*?)(?=\n[A-D]\)|$)"
    match = re.search(pattern, options_text, re.DOTALL)
    return match.group(1).strip() if match else ""


def main():
    st.title("Criador de Questões")

    # Campo para digitar o prompt
    prompt = st.text_area("Digite o prompt para gerar a questão", 
                          placeholder="Ex: Gere uma questão sobre Geografia com alternativas de A a D e explicação da resposta.")
    
    # Idioma
    idioma = st.selectbox("Selecione o idioma da questão", ["Português", "Inglês", "Espanhol"])

    # Campo para digitar a matéria
    materia = st.text_input("Digite a matéria da questão", placeholder="Ex: Geografia")

    # Campo para digitar o nível
    nivel = st.selectbox("Selecione o nível da questão", ["Fácil", "Médio", "Difícil"])

    # Botão para gerar nova questão
    
    if st.button("Gerar Nova Questão"):
        if prompt and materia and nivel:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                status_area = st.empty()
                mensagens = [
                    "🧠 Gerando questão, aguarde...",       # Português
                    "🧠 Generating question, please wait...",     # Inglês
                    "🧠 Generando pregunta, por favor espere..."   # Espanhol
                ]

                # Mostra animação enquanto gera a questão
                for i in range(6):  # Tempo total ~6 segundos (2s por mensagem)
                    status_area.markdown(f"### {mensagens[i % len(mensagens)]}")
                    time.sleep(3)

                questions = generate_questions(prompt)  # Geração real
                status_area.empty()  # Remove mensagem após gerar

            if questions:
                for idx, q in enumerate(questions, start=1):
                    translated_question = translate_text(q['text'], idioma)
                    translated_options = translate_text(q['options_text'], idioma)
                    translated_explanation = translate_text(q['explanation'], idioma)

                    # Salvando no banco
                    add_question_to_database(
                        materia,
                        nivel,
                        translated_question + "\n" + translated_options,
                        q["correct_answer"],
                        translated_explanation,
                        idioma
                    )
                    st.success("Questões geradas e salvas com sucesso!")

                    # Exibir
                    st.markdown(f"""
                        ---
                        Idioma da Questão {idx} ({idioma})

            
                        {translated_question}

                        Alternativas: 
                        {translated_options.replace('A)', 'A)').replace('B)', '\n **B)**').replace('C)', '\n **C)**').replace('D)', '\n **D)**')}


                        Explicação: 
                        {translated_explanation}
                        """)

            else:
                st.error("Nenhuma questão foi gerada. Verifique seu prompt.")
        else:
            st.error("Por favor, preencha todos os campos para gerar a questão.")

st.page_link("pages/tela_usuario.py", label="🔙 Voltar")

main()
