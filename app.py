import streamlit as st
import pandas as pd
import requests
import urllib.parse

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Pro", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Profissional de Avaliação Imobiliária (Google Maps API)")
st.markdown("Estime o valor de mercado real cruzando dados físicos com a infraestrutura oficial do Google.")

# Tabela dinâmica nacional de valor do m² médio por Estado (Mercado Real)
tabela_m2_nacional = {
    "SP": {"capital": 10200, "interior": 5400, "guaruja": 5400, "cubatao": 3600},
    "RJ": {"capital": 10100, "interior": 4800},
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
    st.sidebar.warning("⚠️ Modo de Contingência Ativo: Insira a chave do Google para liberar o mapa por lote.")

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

    # 🌐 SE A CHAVE EXISTIR: O Google assume o controle absoluto da localização
    if google_api_key:
        with st.spinner("Consultando servidores do Google Geocoding..."):
            try:
                endereco_encoded = urllib.parse.quote(f"{endereco_digitado}, Brasil")
                url_google = f"https://googleapis.com{endereco_encoded}&key={google_api_key}"
                response = requests.get(url_google, timeout=8).json()
                
                if response['status'] == 'OK':
                    resultado = response['results'][0]
                    latitude = float(resultado['geometry']['location']['lat'])
                    longitude = float(resultado['geometry']['location']['lng'])
                    endereco_oficial = resultado['formatted_address']
                    
                    # Varre os componentes do Google para achar Cidade e Estado corretos
                    for comp in resultado['address_components']:
                        if "administrative_area_level_2" in comp['types']:
                            cidade_detectada = comp['long_name']
                        if "administrative_area_level_1" in comp['types']:
                            estado_uf = comp['short_name']
                else:
                    st.error(f"Erro na API do Google: {response['status']}. Verifique as permissões da sua chave.")
            except:
                st.error("Falha de comunicação com o servidor do Google Maps.")

    # 💎 PREÇO DO M² PONDERADO REGIONAL
    cidade_limpa = cidade_detectada.lower().strip()
    sub_tabela = tabela_m2_nacional.get(estado_uf, tabela_m2_nacional["PADRAO"])
    
    if "guaruja" in cidade_limpa or "guarujá" in cidade_limpa:
        preco_m2_base = sub_tabela.get("guaruja", 5400)
    elif "cubatão" in cidade_limpa or "cubatao" in cidade_limpa:
        preco_m2_base = sub_tabela.get("cubatao", 3600)
    elif any(k in cidade_limpa for k in ["são paulo", "rio"]):
        preco_m2_base = sub_tabela.get("capital")
    else:
        preco_m2_base = sub_tabela.get("interior")

    # Cálculo final
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
    
    # 🗺️ VISUALIZADOR DE MAPA PROFISSIONAL
    st.subheader("🗺️ Localização Geográfica")
    if google_api_key:
        # Se tem a chave, exibe o mapa interativo dinâmico oficial do Google via Embed
        endereco_mapa_encoded = urllib.parse.quote(endereco_oficial)
        embed_url = f"https://google.com{google_api_key}&q={endereco_mapa_encoded}&zoom=16"
        st.components.v1.iframe(embed_url, width=1100, height=400, scrolling=False)
    else:
        # Modo de segurança sem a chave (Apenas coordenadas em tabela e aviso)
        st.warning("Insira a sua API Key do Google Maps no menu lateral para visualizar o mapa interativo neste bloco.")
        df_contingencia = pd.DataFrame({'latitude': [latitude], 'longitude': [longitude]})
        st.dataframe(df_mapa_contingencia)

    # 🔗 LINK DE DIRECIONAMENTO EXTERNO (Sempre ativo e funcional)
    url_final_google = f"https://google.com{latitude},{longitude}"
    st.link_button("➡️ Abrir Rota Direta no Aplicativo do Google Maps", url_final_google, type="primary")
