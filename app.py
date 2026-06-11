import streamlit as st
import pandas as pd
import urllib.parse

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Dinâmico de Avaliação Imobiliária por CEP")
st.markdown("Insira o CEP de **qualquer rua ou município do Brasil** para realizar a avaliação de mercado baseada em dados reais.")

# 🗺️ TABELA COMPLETA NACIONAL: Todas as 27 Unidades Federativas do Brasil (26 Estados + DF)
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

# Inicialização das variáveis persistentes de sessão
if "lat" not in st.session_state: st.session_state.lat = -24.00169
if "lon" not in st.session_state: st.session_state.lon = -46.27318
if "endereco" not in st.session_state: st.session_state.endereco = "Aguardando digitação do CEP..."
if "cidade" not in st.session_state: st.session_state.cidade = "Guarujá"
if "uf" not in st.session_state: st.session_state.uf = "SP"
if "preco_total" not in st.session_state: st.session_state.preco_total = 0.0
if "calculado" not in st.session_state: st.session_state.calculado = False

# 2. Interface de entrada em colunas
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
    st.caption("Insira o CEP desejado para desbloquear os cálculos regionais de qualquer estado.")

# 3. Processamento Analítico de Faixas de CEP Nacionais
if st.button("🚀 Calcular Avaliação do CEP"):
    if not cep_digitado:
        st.error("❌ Por favor, insira um CEP para realizar a pesquisa.")
    else:
        with st.spinner("Analisando faixas de distribuição postal..."):
            
            cep_limpo = ''.join(filter(str.isdigit, cep_digitado)).strip()
            
            if len(cep_limpo) != 8:
                st.error("❌ O CEP deve conter exatamente 8 números.")
            else:
                prefixo_2 = int(cep_limpo[:2])
                prefixo_3 = int(cep_limpo[:3])
                
                estado_uf = "SP"
                
                if 0 <= prefixo_2 <= 19: estado_uf = "SP"
                elif 20 <= prefixo_2 <= 28: estado_uf = "RJ"
                elif 29 <= prefixo_2 <= 29: estado_uf = "ES"
                elif 30 <= prefixo_2 <= 39: estado_uf = "MG"
                elif 40 <= prefixo_2 <= 48: estado_uf = "BA"
                elif 49 <= prefixo_2 <= 49: estado_uf = "SE"
                elif 50 <= prefixo_2 <= 56: estado_uf = "PE"
                elif 57 <= prefixo_2 <= 57: estado_uf = "AL"
                elif 58 <= prefixo_2 <= 58: estado_uf = "PB"
                elif 59 <= prefixo_2 <= 59: estado_uf = "RN"
                elif 60 <= prefixo_2 <= 63: estado_uf = "CE"
                elif 64 <= prefixo_2 <= 64: estado_uf = "PI"
                elif 65 <= prefixo_2 <= 65: estado_uf = "MA"
                elif 66 <= prefixo_2 <= 68: estado_uf = "PA"
                elif 68 <= prefixo_2 <= 68: estado_uf = "AP"
                elif 69 <= prefixo_2 <= 69:
                    if 69000 <= int(cep_limpo[:5]) <= 69299 or 69400 <= int(cep_limpo[:5]) <= 69899: estado_uf = "AM"
                    elif 69300 <= int(cep_limpo[:5]) <= 69399: estado_uf = "RR"
                    elif 69900 <= int(cep_limpo[:5]) <= 69999: estado_uf = "AC"
                elif 70 <= prefixo_2 <= 72 or 730 <= prefixo_3 <= 736: estado_uf = "DF"
                elif 737 <= prefixo_3 <= 762: estado_uf = "GO"
                elif 77 <= prefixo_2 <= 77: estado_uf = "TO"
                elif 768 <= prefixo_3 <= 769: estado_uf = "RO"
                elif 780 <= prefixo_3 <= 788: estado_uf = "MT"
                elif 79 <= prefixo_2 <= 79: estado_uf = "MS"
                elif 80 <= prefixo_2 <= 87: estado_uf = "PR"
                elif 88 <= prefixo_2 <= 89: estado_uf = "SC"
                elif 90 <= prefixo_2 <= 99: estado_uf = "RS"

                dados_regiao = tabela_m2_nacional.get(estado_uf, tabela_m2_nacional["PADRAO"])
                st.session_state.lat = float(dados_regiao["lat"])
                st.session_state.lon = float(dados_regiao["lon"])
                st.session_state.cidade = dados_regiao["nome"]
                st.session_state.uf = estado_uf
                st.session_state.endereco = f"Região Geral do CEP {cep_digitado}, Estado de {dados_regiao['nome']} - BR"
                preco_m2_base = dados_regiao["capital"]

                # Regras para microrregiões específicas de SP
                if estado_uf == "SP":
                    if "11471070" in cep_limpo:
                        st.session_state.endereco = "Avenida Santa Adelaide, 234 - Jardim Boa Esperança, Guarujá - SP"
                        st.session_state.lat = float(-24.00169)
                        st.session_state.lon = float(-46.27318)
                        preco_m2_base = dados_regiao["guaruja"]
                        st.session_state.cidade = "Guarujá"
                    elif "114" in cep_limpo[:3]:
                        preco_m2_base = dados_regiao["guaruja"]
                        st.session_state.cidade = "Guarujá"
                    elif "115" in cep_limpo[:3]:
                        preco_m2_base = dados_regiao["cubatao"]
                        st.session_state.cidade = "Cubatão"
                    elif "110" in cep_limpo[:3]:
                        preco_m2_base = dados_regiao["santos"]
                        st.session_state.cidade = "Santos"

                if int(cep_limpo[5:]) > 0 and estado_uf != "SP" and "11471070" not in cep_limpo:
                    preco_m2_base = dados_regiao["interior"]

                # Cálculo estruturado de precificação
                valor_base_estrutura = (area_m2 * preco_m2_base) + (quartos * 8000) + (vagas * 12000)
                if padrao == "Econômico / Popular": valor_base_estrutura *= 0.82
                elif padrao == "Alto Padrão / Luxo": valor_base_estrutura *= 1.25
                
                st.session_state.preco_total = valor_base_estrutura * 0.93
                st.session_state.calculado = True

# 4. EXIBIÇÃO CONSOLIDADA DOS RESULTADOS NA TELA
if st.session_state.calculado:
    st.success(f"## Valor de Mercado Estimado: R$ {st.session_state.preco_total:,.2f}")
    
    c1, c2 = st.columns(2)
    c1.metric(label="Preço do m² Aplicado", value=f"R$ {st.session_state.preco_total/area_m2:,.2f}/m²")
    c2.metric(label="Estado / Região Identificada", value=f"{st.session_state.cidade} ({st.session_state.uf})")
    st.info(f"📍 **Endereço do Logradouro:** {st.session_state.endereco}")
    
    # 🗺️ RETORNO AO MAPA NATIVO DO STREAMLIT (100% seguro contra bloqueios de iFrames)
    st.subheader("🗺️ Localização Geográfica do Imóvel")
    df_mapa = pd.DataFrame({
