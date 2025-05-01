import requests
from supabase import create_client, Client
import streamlit as st
import pandas as pd
import re
import os
import time
# Exibindo os testes realizados pelo candidato (simulação de dados)
st.subheader("Seus Testes Realizados")

# Aqui você pode substituir os dados simulados pela consulta ao banco de dados que retorna os testes do candidato
# Simulando dados dos testes realizados (substitua com dados reais da consulta ao banco de dados)
test_data = {
    "Nome do Teste": [""],
    "Data de Criação": [""],
    "Nota": [""]
}

# Criando um DataFrame
df_tests = pd.DataFrame(test_data)

# Exibindo a tabela de testes realizados
st.dataframe(df_tests)