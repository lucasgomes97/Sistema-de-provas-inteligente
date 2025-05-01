# Cabeçalho da página
import requests
from supabase.client import create_client, Client
import streamlit as st
import pandas as pd
import re
import os
import time
st.title("📋 Criar Novo Teste")

# Formulário para criar o teste
with st.form(key="form_criar_teste"):
    test_name = st.text_input("Nome do Teste")
    test_description = st.text_area("Descrição do Teste")
    estimated_time = st.number_input("Tempo Estimado (em minutos)", min_value=1, max_value=180, value=30)
    total_questions = st.number_input("Total de Perguntas", min_value=1, value=10)
    
    submit_button = st.form_submit_button(label="Criar Teste")

# Lógica para criação de teste
if submit_button:
    if test_name and test_description:
        st.success(f"Teste '{test_name}' criado com sucesso!")
        # Aqui você pode adicionar a lógica para salvar o teste no banco de dados ou realizar outras ações
    else:
        st.error("Por favor, preencha todos os campos.")

