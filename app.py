import streamlit as st
import pandas as pd
import requests
import urllib.parse

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil Pro", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Profissional de Avaliação Imobiliária (Google Maps API)")
st.markdown("Estime o valor de mercado real cruzando dados físicos com a infraestrutura oficial do Google em todo o território nacional.")

# 🗺️ TABELA COMPLETA NACIONAL: Cobertura de todas as 27 Unidades Federativas do Brasil
# Valores de m² calibrados de acordo com os índices médios de mercado regionais
tabela_m2_nacional = {
    "AC": {"capital": 5100, "interior": 3400},
    "AL": {"capital": 6500, "interior": 3800},
    "AM": {"capital": 6900, "interior": 3900},
    "AP": {"capital": 4800, "interior": 3200},
    "BA": {"capital": 6200, "interior": 3600},
    "CE": {"capital": 5900, "interior": 3500},
    "DF": {"capital": 8900, "interior": 5200}, # Brasília e Regiões Administrativas
    "ES": {"capital": 7400, "interior": 4500},
    "GO": {"capital": 6500, "interior": 3800},
    "MA": {"capital": 5300, "interior": 3300},
    "MG": {"capital": 7900, "interior": 4200},
    "MS": {"capital": 5800, "interior": 3600},
    "MT": {"capital": 6200, "interior": 3900},
    "PA": {"capital": 5400, "interior": 3200},
    "PB": {"capital": 5700, "interior": 3400},
    "PE": {"capital": 7400, "interior": 3900},
    "PI": {"capital": 5100, "interior": 3300},
    "PR": {"capital": 7800, "interior": 4500},
    "RJ": {"capital": 10100, "interior": 4800},
    "RN": {"capital": 5800, "interior": 3500},
    "RO": {"capital": 5200, "interior": 3400},
    "RR": {"capital": 4700, "interior": 3100},
    "RS": {"capital": 6800, "interior": 4100},
    "SC": {"capital": 11000, "interior": 6500},
    "SE": {"capital": 5500, "interior": 3400},
    "SP": {"capital": 10200, "interior": 5400, "guaruja": 5400, "cubatao": 3600}, # Microrregiões paulistas salvas
    "TO": {"capital": 5300, "interior": 3400},
    "PADRAO": {"capital": 5500, "interior": 3500}
}

# Painel Lateral para inserir a Chave do Google
st.sidebar.header("🔑 Configuração de Produção")
google_api_key = st.sidebar.text_input(
    "Insira sua API Key do Google Maps", 
    type="password",
    help="Cole aqui a sua chave gerada no Google Cloud Console para ativar o mapa dinâmico por rua."
)

if not google_api_key:
    st.sidebar.warning("⚠️ Modo de Contingência Ativo: Insira a chave do Google para liberar o mapa oficial por lote.")

# Interface de entrada em colunas
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📐 Características do Imóvel")
    area_m2 = st.slider("Área Privativa (m²)", 30, 400, 70)
    quartos = st.slider("Quantidade de Quartos", 1, 5, 2)
    vagas = st.slider("Vagas de Garagem", 0, 4, 1)
    padrao = st.selectbox("Padrão de Acabamento", ["Econômico / Popular", "Médio / Padrão", "Alto Padrão / Luxo"])

with col_dir:
    st.subheader("📍 Localização por Google Maps")
    endereco_digitado = st.text_input("Digite o CEP ou Endereço com Número", "Avenida Santa Adelaide, 234, Guarujá - SP")

# 3. Processamento com o Motor do Google Maps
if st.button("🚀 Calcular Avaliação Profissional"):
    
    # Valores de contingência padrão (Caso esteja sem chave)
    cidade_detectada = "Guarujá"
    estado_uf = "SP"
    endereco_oficial = "Avenida Santa Adelaide, 234 - Jardim Boa Esperança, Guarujá - SP"
    latitude, longitude = -24.00169, -46.27318
    
    # Se o usuário digitou Cubatão, ajusta a contingência básica
    if "cubatao" in endereco_digitado.lower() or "cubatão" in endereco_digitado.lower():
        cidade_detectada = "Cubatão"
        endereco_oficial = "Região de Cubatão, SP"
        latitude, longitude = -23.8920, -46.4250

    # 🌐 SE A CHAVE EXISTIR: O Google assume o controle absoluto da localização e descobre a UF real
    if google_api_key:
        with st.spinner("Consultando servidores do Google Geocoding..."):
            try:
                endereco_encoded = urllib.parse.quote(f"{endereco_digitado}, Brasil")
                url_google = f"https://googleapis.com{endereco_encoded}&key={google_api_key}"
                response = requests.get(url_google, timeout=8).json()
                
                if response['status'] == 'OK':
                    resultado = response['results']
                    latitude = float(resultado['geometry']['location']['lat'])
                    longitude = float(resultado['geometry']['location']['lng'])
                    endereco_oficial = resultado['formatted_address']
                    
                    # Varre os componentes do Google para achar Cidade e Estado corretos
                    for comp in resultado['address_components']:
                        if "administrative_area_level_2" in comp['types']:
                            cidade_detectada = comp['long_name']
                        if "administrative_area_level_1" in comp['types']:
                            estado_uf = comp['short_name'].upper().strip()
                else:
                    st.error(f"Erro na API do Google: {response['status']}. Verifique as permissões da sua chave.")
            except:
                st.error("Falha de comunicação com o servidor do Google Maps.")

    # 💎 PREÇO DO M² PONDERADO REGIONAL DINÂMICO NACIONAL
    cidade_limpa = cidade_detectada.lower().strip()
    
    # Busca a sub-tabela do estado retornado pelo Google (Ex: "RJ", "MG", "SC")
    sub_tabela = tabela_m2_nacional.get(estado_uf, tabela_m2_nacional["PADRAO"])
    
    # Regras específicas para cidades paulistas salvas
    if estado_uf == "SP" and ("guaruja" in cidade_limpa or "guarujá" in cidade_limpa):
        preco_m2_base = sub_tabela.get("guaruja", 5400)
    elif estado_uf == "SP" and ("cubatão" in cidade_limpa or "cubatao" in cidade_limpa):
        preco_m2_base = sub_tabela.get("cubatao", 3600)
    # Lógica nacional geral: se o nome da cidade conter o termo da própria capital ou se for região metropolitana polo
    elif any(k in cidade_limpa for k in ["são paulo", "rio", "belo horizonte", "curitiba", "porto alegre", "brasília", "recife", "salvador", "fortaleza", "goiânia", "manaus"]):
        preco_m2_base = sub_tabela.get("capital")
    else:
        preco_m2_base = sub_tabela.get("interior")

    # Cálculo final de avaliação comercial estruturada
    valor_base_estrutura = (area_m2 * preco_m2_base) + (quartos * 8000) + (vagas * 12000)
    if padrao == "Econômico / Popular": valor_base_estrutura *= 0.82
    elif padrao == "Alto Padrão / Luxo": valor_base_estrutura *= 1.22
    preco_final = valor_base_estrutura * 0.93

    # 4. EXIBIÇÃO DOS RESULTADOS
    st.success(f"## Valor de Mercado Estimado: R$ {preco_final:,.2f}")
    
    c1, c2 = st.columns(2)
    c1.metric(label="Preço do m² Calculado", value=f"R$ {preco_final/area_m2:,.2f}/m²")
    c2.metric(label="Localidade Validada", value=f"{cidade_detectada} - {estado_uf}")
    st.info(f"📍 **Endereço Confirmado:** {endereco_oficial}")
    
    # 🗺️ VISUALIZADOR DE MAPA PROFISSIONAL COM SELEÇÃO INTELIGENTE
    st.subheader("🗺️ Localização Geográfica")
    if google_api_key:
        endereco_mapa_encoded = urllib.parse.quote(endereco_oficial)
        embed_url = f"https://google.com{google_api_key}&q={endereco_mapa_encoded}&zoom=16"
        st.components.v1.iframe(embed_url, width=1100, height=400, scrolling=False)
    else:
        df_contingencia = pd.DataFrame({'latitude': [latitude], 'longitude': [longitude]})
        st.map(df_contingencia, zoom=14)

    # 🔗 LINK DE DIRECIONAMENTO EXTERNO (Universal)
    url_final_google = f"https://google.com{latitude},{longitude}"
    st.link_button("➡️ Abrir Rota Direta no Aplicativo do Google Maps", url_google_maps_oficial if 'url_google_maps_oficial' in locals() else url_final_google, type="primary")
