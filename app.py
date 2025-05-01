import streamlit as st
import datetime
from datetime import date, datetime
from supabase import create_client, Client
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv

# Configurações iniciais
st.set_page_config(page_title="Sistema de Provas Inteligente", page_icon="🤖", layout="wide")

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Usando a classe 'date' para chamar 'today()'
hoje = date.today()

# Função para cadastro de usuário
def cadastrar_usuario(email, senha, nome, nascimento):
    try:
        # Verificar se o usuário já existe
        existing_user = supabase.table('users').select('email').eq('email', email).execute()
        if existing_user.data:
            return {"error": "❌ Email já cadastrado. Faça login ou use outro email."}

        # Cadastrar no sistema de autenticação do Supabase
        response = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {
                "should_send_email": False
            }
        })

        if response.user is None:
            return {"error": "Erro ao cadastrar usuário na autenticação."}

        # Converter nascimento se for string
        if isinstance(nascimento, str):
            nascimento = datetime.strptime(nascimento, '%d/%m/%Y').date()

        nascimento_formatado = nascimento.strftime('%Y-%m-%d')

        # Dados para inserir no banco
        data = {
            "email": email,
            "nome": nome,
            "nascimento": nascimento_formatado,
            "senha": senha,
            "saldo": 100  # Saldo inicial
        }

        # Inserir no banco
        insert_response = supabase.table('users').insert(data).execute()

        if insert_response.data:
            return {"success": "Usuário cadastrado com sucesso! Vá para aba de Login"}
        else:
            return {"error": "Erro ao inserir usuário no banco de dados."}

    except Exception as e:
        return {"error": str(e)}

# Função para verificar ou criar tabela do usuário
def verificar_ou_criar_tabela_usuario(email):
    try:
        response = supabase.rpc('check_or_create_user_table', {'email': email}).execute()
        if response.data is not None:
            return {"success": "Login realizado com sucesso! Tabela do usuário criada ou já existe."}
        else:
            return {"error": "Erro ao criar ou verificar a tabela do usuário."}
    except Exception as e:
        return {"error": f"Erro ao verificar ou criar a tabela: {str(e)}"}

# Função para login
def login_usuario(email, senha):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha
        })
        
        if response.user is None:
            return {"error": "Credenciais inválidas"}

        user_data = supabase.table('users').select('nome, nascimento, email').eq('email', email).execute()

        if user_data and user_data.data:
            return {"success": "Login realizado com sucesso!", "user_data": user_data.data[0]}
        else:
            return {"error": "Usuário não encontrado no banco de dados."}
        
    
    except Exception as e:
        return {"error": str(e)}

# Background personalizado
background_image_html = """
<style>
.stApp {
  background-image: url('https://raw.githubusercontent.com/lucasgomes97/Sistema-de-provas-inteligente/main/ChatGPT%20Image%2026%20de%20abr.%20de%202025%2C%2014_39_03%20(2).png');
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
        background: rgba(255, 255, 255, 0.8);
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        z-index: 1;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Controle de sessão
if "page" not in st.session_state:
    st.session_state.page = "Início"

if "user" not in st.session_state:
    st.session_state.user = None

menu_opcoes = ["Início", "Cadastrar", "Login"]

if st.session_state.page not in menu_opcoes:
    st.session_state.page = "Início"

# Sidebar - Menu
with st.sidebar:
    escolha = option_menu(
        menu_title="Menu Principal",  
        options=menu_opcoes,
        icons=["house", "person-plus", "box-arrow-in-right"],
        menu_icon="list",
        default_index=menu_opcoes.index(st.session_state.page),
        styles={
            "container": {
                "padding": "10px",
                "background-color": "#262730",
                "border-radius": "12px",
            },
            "icon": {"color": "#ffffff", "font-size": "24px"},
            "nav-link": {
                "font-size": "20px",
                "color": "#ffffff",
                "padding": "12px",
                "border-radius": "10px",
                "background-color": "#4CAF50",
            },
            "nav-link-selected": {
                "background-color": "#45a049",
                "color": "white",
            }
        }
    )
    st.session_state.page = escolha

# Conteúdo principal
if escolha == "Início":
    st.title("🔐 Bem-vindo ao Sistema de Provas Inteligente!")
    if st.session_state.user:
        st.success(f"Bem-vindo(a) {st.session_state.user['nome']}!")
    else:
        st.info("Por favor, cadastre-se ou faça login.")

elif escolha == "Cadastrar":
    st.title("📝 Cadastro de Usuário")
    with st.container():
        nome = st.text_input("Nome completo")
        nascimento = st.date_input(
            "Data de nascimento",
            min_value=date(1900, 1, 1),
            max_value=hoje,
            format="DD/MM/YYYY"
        )
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Cadastrar"):
            nascimento_str = nascimento.strftime("%d/%m/%Y")
            if nome and email and senha:
                resultado = cadastrar_usuario(email, senha, nome, nascimento_str)
                if "error" in resultado:
                    st.error(resultado['error'])
                else:
                    st.success(resultado['success'])
            else:
                st.warning("Preencha todos os campos!")


if escolha == "Login":
    st.title("🔑 Login")
    with st.container():
        email = st.text_input("Email", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_password")
        
        if st.button("Entrar"):
            if email and senha:
                resultado = login_usuario(email, senha)
                
                if "error" in resultado:
                    st.error(resultado['error'])
                else:
                    # Armazenando os dados do usuário no session_state
                    st.session_state.user = resultado["user_data"]

                    # Verificando ou criando a tabela do usuário
                    resultado_tabela = verificar_ou_criar_tabela_usuario(email)
                    if "error" in resultado_tabela:
                        st.error(resultado_tabela['error'])
                    else:
                        st.success(resultado_tabela['success'])

                    # Definindo a página para o redirecionamento
                    st.session_state.page = "Tela do Usuário"

                    # Redirecionando para a tela do usuário
                    st.switch_page("pages/tela_usuario.py")

                    # Reinicia a execução da página para carregar os novos dados
                    st.rerun()
            else:
                st.warning("Preencha todos os campos!")

if st.session_state.page == "Tela do Usuário":
    from pages.tela_usuario import mostrar_tela_usuario
    mostrar_tela_usuario()
    if st.session_state.user:
        st.title(f"👤 Bem-vindo, {st.session_state.user['nome']}")
        st.write(f"**Email:** {st.session_state.user['email']}")
        st.write(f"**Data de Nascimento:** {st.session_state.user['nascimento']}")
    else:
        st.error("Você precisa estar logado para acessar esta página!")
