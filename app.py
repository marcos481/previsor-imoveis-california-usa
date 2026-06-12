import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURAÇÃO VISUAL DA PÁGINA
st.set_page_config(page_title="Previsor Imobiliário Brasil Pro", page_icon="🏠", layout="wide")

# 2. BANCO DE DADOS NACIONAL DE PREÇOS E COORDENADAS
tabela_m2_nacional = {
    "AC": {"capital": 5100, "interior": 3400, "lat": -9.9749, "lon": -67.8076, "nome": "Acre"},
    "AL": {"capital": 6500, "interior": 3800, "lat": -9.6659, "lon": -35.7350, "nome": "Alagoas"},
    "AM": {"capital": 6900, "interior": 3900, "lat": -3.1189, "lon": -60.0217, "nome": "Amazonas"},
    "AP": {"capital": 4800, "interior": 3200, "lat": 0.0349, "lon": -51.0694, "nome": "Amapá"},
    "BA": {"capital": 6200, "interior": 3600, "lat": -12.9711, "lon": -38.5108, "nome": "Bahia"},
    "CE": {"capital": 5900, "interior": 3500, "lat": -3.7166, "lon": -38.5423, "nome": "Ceará"},
    "DF": {"capital": 8900, "interior": 5200, "lat": -15.7938, "lon": -47.8827, "nome": "Distrito Federal"},
    "ES": {"capital": 7400, "interior": 4500, "lat": -20.3197, "lon": -40.3378, "nome": "Espírito Santo"},
    "GO": {"capital": 6500, "interior": 3800, "lat": -16.6869, "lon": -49.2648, "nome": "Goiás"},
    "MA": {"capital": 5300, "interior": 3300, "lat": -2.5387, "lon": -44.2825, "nome": "Maranhão"},
    "MG": {"capital": 7900, "interior": 4200, "lat": -19.9173, "lon": -43.9345, "nome": "Minas Gerais"},
    "MS": {"capital": 5800, "interior": 3600, "lat": -20.4486, "lon": -54.6295, "nome": "Mato Grosso do Sul"},
    "MT": {"capital": 6200, "interior": 3900, "lat": -15.6010, "lon": -56.0974, "nome": "Mato Grosso"},
    "PA": {"capital": 5400, "interior": 3200, "lat": -1.4554, "lon": -48.5024, "nome": "Pará"},
    "PB": {"capital": 5700, "interior": 3400, "lat": -7.1150, "lon": -34.8631, "nome": "Paraíba"},
    "PE": {"capital": 7400, "interior": 3900, "lat": -8.0522, "lon": -34.9286, "nome": "Pernambuco"},
    "PI": {"capital": 5100, "interior": 3300, "lat": -5.0919, "lon": -42.8034, "nome": "Piauí"},
    "PR": {"capital": 7800, "interior": 4500, "lat": -25.4290, "lon": -49.2671, "nome": "Paraná"},
    "RJ": {"capital": 10100, "interior": 4800, "lat": -22.9068, "lon": -43.1729, "nome": "Rio de Janeiro"},
    "RN": {"capital": 5800, "interior": 3500, "lat": -5.7950, "lon": -35.2094, "nome": "Rio Grande do Norte"},
    "RO": {"capital": 5200, "interior": 3400, "lat": -8.7619, "lon": -63.9039, "nome": "Rondônia"},
    "RR": {"capital": 4700, "interior": 3100, "lat": 2.8198, "lon": -60.6715, "nome": "Roraima"},
    "RS": {"capital": 6800, "interior": 4100, "lat": -30.0346, "lon": -51.2177, "nome": "Rio Grande do Sul"},
    "SC": {"capital": 11000, "interior": 6500, "lat": -27.5954, "lon": -48.5480, "nome": "Santa Catarina"},
    "SE": {"capital": 5500, "interior": 3400, "lat": -10.9111, "lon": -37.0717, "nome": "Sergipe"},
    "SP": {"capital": 10200, "interior": 5400, "guaruja": 6900, "cubatao": 4300, "santos": 8200, "lat": -23.5505, "lon": -46.6333, "nome": "São Paulo"},
    "TO": {"capital": 5300, "interior": 3400, "lat": -10.1844, "lon": -48.3336, "nome": "Tocantins"},
    "PADRAO": {"capital": 5500, "interior": 3500, "lat": -15.7938, "lon": -47.8827, "nome": "Brasil"}
}

# 3. SISTEMA DE LOGIN INTEGRADO DIRETAMENTE NA BARRA LATERAL
st.sidebar.title("🔐 Área Restrita")

if "logado" not in st.session_state:
    st.session_state.logado = False

# Inputs permanentes na barra lateral para evitar quebras de ciclo
usuario = st.sidebar.text_input("Usuário", value="")
senha = st.sidebar.text_input("Senha", type="password", value="")

if st.sidebar.button("Entrar / Validar"):
    if usuario == "admin" and senha == "corretor123":
        st.session_state.logado = True
    else:
        st.sidebar.error("❌ Usuário ou Senha incorretos.")

# Botão de Logout rápido
if st.sidebar.button("🚪 Sair do Sistema"):
    st.session_state.logado = False
    st.rerun()

# 4. EXECUÇÃO DO CONTEÚDO PRINCIPAL APÓS LOGIN
if not st.session_state.logado:
    st.title("🏠 Sistema Inteligente de Avaliação Imobiliária Nacional")
    st.warning("🔒 Por favor, digite o usuário e senha corretos na barra lateral esquerda e clique em 'Entrar / Validar' para desbloquear o sistema.")
else:
    st.title("🏠 Sistema Inteligente de Avaliação Imobiliária Nacional")
    st.success("Painel nacional desbloqueado com sucesso.")

    # Interface dividida em 2 colunas igualzinho ao código estável original
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("📐 Características do Imóvel")
        area_m2 = st.slider("Área Privativa (m²)", 30, 400, 70)
        quartos = st.slider("Quantidade de Quartos", 1, 5, 2)
        vagas = st.slider("Vagas de Garagem", 0, 4, 1)
        padrao = st.selectbox("Padrão de Acabamento", ["Econômico / Popular", "Médio / Padrão", "Alto Padrão / Luxo"])

    with col_dir:
        st.subheader("📍 Localização Obrigatória")
        cep_digitado = st.text_input("Digite o CEP do Imóvel (Apenas números ou com hífen)", "")
        st.caption("Exemplos: '11471-070' (Guarujá), '11520-000' (Cubatão), '76801-000' (Rondônia)")

    # Botão de cálculo tradicional
    if st.button("🚀 Calcular Avaliação do CEP"):
        if not cep_digitado:
            st.error("❌ Por favor, insira um CEP para realizar a pesquisa.")
        else:
            with st.spinner("Processando dados do CEP imobiliário..."):
                
                cep_limpo = ''.join(filter(str.isdigit, cep_digitado)).strip()
                
                if len(cep_limpo) != 8:
                    st.error("❌ O CEP deve conter exatamente 8 números.")
                else:
                    # Motor de busca por Strings robusto e idêntico ao que funcionava
                    if cep_limpo.startswith(("0", "1")): estado_uf = "SP"
                    elif cep_limpo.startswith(("20", "21", "22", "23", "24", "25", "26", "27", "28")): estado_uf = "RJ"
                    elif cep_limpo.startswith("29"): estado_uf = "ES"
                    elif cep_limpo.startswith("3"): estado_uf = "MG"
                    elif cep_limpo.startswith(("40", "41", "42", "43", "44", "45", "46", "47", "48")): estado_uf = "BA"
                    elif cep_limpo.startswith("49"): estado_uf = "SE"
                    elif cep_limpo.startswith(("50", "51", "52", "53", "54", "55", "56")): estado_uf = "PE"
                    elif cep_limpo.startswith("57"): estado_uf = "AL"
                    elif cep_limpo.startswith("58"): estado_uf = "PB"
                    elif cep_limpo.startswith("59"): estado_uf = "RN"
                    elif cep_limpo.startswith(("60", "61", "62", "63")): estado_uf = "CE"
                    elif cep_limpo.startswith("64"): estado_uf = "PI"
                    elif cep_limpo.startswith("65"): estado_uf = "MA"
                    elif cep_limpo.startswith(("66", "67")) or (cep_limpo.startswith("68") and not cep_limpo.startswith(("689", "699", "693"))): estado_uf = "PA"
                    elif cep_limpo.startswith("689"): estado_uf = "AP"
                    elif cep_limpo.startswith("699"): estado_uf = "AC"
                    elif cep_limpo.startswith("693"): estado_uf = "RR"
                    elif cep_limpo.startswith(("690", "691", "692", "694", "695", "696", "697", "698")): estado_uf = "AM"
                    elif cep_limpo.startswith(("70", "71", "72")) or (730 <= int(cep_limpo[:3]) <= 736): estado_uf = "DF"
                    elif (737 <= int(cep_limpo[:3]) <= 762): estado_uf = "GO"
                    elif cep_limpo.startswith("77"): estado_uf = "TO"
                    elif cep_limpo.startswith(("768", "769")): estado_uf = "RO"
                    elif (780 <= int(cep_limpo[:3]) <= 788): estado_uf = "MT"
                    elif cep_limpo.startswith("79"): estado_uf = "MS"
                    elif cep_limpo.startswith("8"): estado_uf = "PR"
                    elif cep_limpo.startswith(("88", "89")): estado_uf = "SC"
                    elif cep_limpo.startswith("9"): estado_uf = "RS"
                    else: estado_uf = "PADRAO"

                    dados_regiao = tabela_m2_nacional.get(estado_uf, tabela_m2_nacional["PADRAO"])
                    lat = float(dados_regiao["lat"])
                    lon = float(dados_regiao["lon"])
                    cidade_detectada = dados_regiao["nome"]
                    endereco_oficial = f"Região Geral do CEP {cep_digitado}, Estado de {dados_regiao['nome']} - BR"
                    preco_m2_base = dados_regiao["capital"]

                    if "11471070" in cep_limpo:
                        endereco_oficial = "Avenida Santa Adelaide, 234 - Jardim Boa Esperança, Guarujá - SP"
                        lat = float(-24.00169)
                        lon = float(-46.27318)
                        preco_m2_base = dados_regiao["guaruja"]
                        cidade_detectada = "Guarujá"
                    elif estado_uf == "SP" and "114" in cep_limpo[:3]:
                        preco_m2_base = dados_regiao["guaruja"]
                        cidade_detectada = "Guarujá"
                    elif estado_uf == "SP" and "115" in cep_limpo[:3]:
                        preco_m2_base = dados_regiao["cubatao"]
                        cidade_detectada = "Cubatão"
                    elif estado_uf == "SP" and "110" in cep_limpo[:3]:
                        preco_m2_base = dados_regiao["santos"]
                        cidade_detectada = "Santos"

                    if int(cep_limpo[5:]) > 0 and estado_uf != "SP" and "11471070" not in cep_limpo:
                        preco_m2_base = dados_regiao["interior"]

                    # Cálculo matemático imobiliário estável
                    valor_base_estrutura = (area_m2 * preco_m2_base) + (quartos * 8000) + (vagas * 12000)
                    if padrao == "Econômico / Popular": valor_base_estrutura *= 0.82
                    elif padrao == "Alto Padrão / Luxo": valor_base_estrutura *= 1.25
                    
                    preco_total = valor_base_estrutura * 0.93

