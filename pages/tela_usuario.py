import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from streamlit_option_menu import option_menu

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Função para mostrar os dados do usuário
def mostrar_tela_usuario():
    st.title("👤 Tela do Usuário")
    
    # Verifica se o usuário está logado
    if st.session_state.user:
        user = st.session_state.user
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Nome:** {user['nome']}")
        st.write(f"**Data de Nascimento:** {user['nascimento']}")
    else:
        st.error("Você precisa estar logado para acessar esta página!")

# Função para fazer logout
def logout_usuario():
    supabase.auth.sign_out()

# Função para buscar dados do usuário
def obter_dados_usuario(email):
    try:
        user_data = supabase.table('users').select('email, nome, nascimento, senha, saldo').eq('email', email).execute()
        if user_data.data:
            return user_data.data[0]
        return None
    except Exception as e:
        return None

# Função para atualizar a senha do usuário
def atualizar_senha(email, nova_senha):
    try:
        response = supabase.table('users').update({'senha': nova_senha}).eq('email', email).execute()
        return response
    except Exception as e:
        return None

# Configurações iniciais do Streamlit
st.set_page_config(page_title="Sistema de Provas Inteligente", page_icon="🤖", layout="wide")

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

# Controle de sessão
if "page" not in st.session_state:
    st.session_state.page = "Início"

if "user" not in st.session_state:
    st.session_state.user = None

menu_opcoes = ["Início", "Meus Dados", "Provas", "Criar teste", "Resultados", "Logout"]
if st.session_state.page not in menu_opcoes:
    st.session_state.page = "Início"

# Sidebar - Menu
with st.sidebar:
    escolha = option_menu(
        menu_title="Menu Principal",  
        options=menu_opcoes,
        icons=["house", "person-plus", "play", "box-arrow-in-right", "activity", "box-arrow-left"],
        menu_icon="list",
        default_index=menu_opcoes.index(st.session_state.page),
        styles={
            "container": {
                "padding": "20px",
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

# Adiciona a navegação para "Criar teste"
if st.session_state.page == "Criar teste":
    st.session_state.page = "Criar teste"
    st.switch_page("pages/criar_perguntas.py")  # Redireciona para a página de criação de testes

# Exibir a página inicial
if escolha == "Início":
    st.title("🔐 Bem-vindo ao Sistema de Provas Inteligente!")
    if st.session_state.user:
        st.success(f"Bem-vindo(a) {st.session_state.user['nome']}!")
    else:
        st.info("Por favor, cadastre-se ou faça login.")

# Exibir a tela de dados do usuário
if st.session_state.page == "Meus Dados":
    if st.session_state.user:
        st.title("📋 Meus Dados")
        
        # Obter dados do usuário do banco
        usuario = obter_dados_usuario(st.session_state.user['email'])
        
        if usuario:
            # Exibição das informações do usuário
            st.subheader("Informações do Usuário")
            st.write(f"**Email:** {usuario['email']}")
            st.write(f"**Nome:** {usuario['nome']}")
            st.write(f"**Data de Nascimento:** {usuario['nascimento']}")
            st.write(f"**Saldo:** {usuario['saldo']}")
            
            # Formulário para alterar a senha
            with st.form(key="form_alterar_senha"):
                senha_atual = st.text_input("Senha Atual", type="password")
                nova_senha = st.text_input("Nova Senha", type="password")
                confirmacao_senha = st.text_input("Confirmar Nova Senha", type="password")
                
                if st.form_submit_button("Alterar Senha"):
                    if usuario['senha'] == senha_atual:
                        if nova_senha == confirmacao_senha:
                            # Atualizar senha no banco
                            response = atualizar_senha(usuario['email'], nova_senha)
                            if response:
                                st.success("Senha alterada com sucesso!")
                                logout_usuario()
                                st.session_state.page = "Início"
                                st.rerun()
                            else:
                                st.error("Erro ao alterar a senha.")
                        else:
                            st.error("As senhas novas não coincidem.")
                    else:
                        st.error("A senha atual está incorreta.")
        else:
            st.error("Erro ao carregar os dados do usuário.")
    else:
        st.error("Você precisa estar logado para acessar esta página.")

# Logout
elif escolha == "Logout":
    st.title("🚪 Logout")
    if st.session_state.user:
        logout_usuario()
        st.session_state.user = None
        st.session_state.page = "Início"
        st.success("Logout realizado com sucesso!")
        st.switch_page("app.py")
