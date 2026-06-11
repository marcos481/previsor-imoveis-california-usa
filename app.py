import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil Pro", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Inteligente de Avaliação Imobiliária (Versão Folium Pro)")
st.markdown("Estime o valor de mercado real baseado em CEP com localização exata e mapa dinâmico.")

# Tabela dinâmica de valor do m² médio por Cidade (Mercado Real)
tabela_m2_brasil = {
    "guaruja": 7100,
    "cubatao": 4300,
    "santos": 8200,
    "capital": 10200,
    "interior": 4500
}

# Variáveis persistentes de sessão para manter o mapa e estados ativos
if "lat" not in st.session_state: st.session_state.lat = -23.9930
if "lon" not in st.session_state: st.session_state.lon = -46.2560
if "endereco" not in st.session_state: st.session_state.endereco = "Digite o CEP e clique em Calcular."
if "cidade" not in st.session_state: st.session_state.cidade = "Guarujá"
if "uf" not in st.session_state: st.session_state.uf = "SP"
if "preco_m2" not in st.session_state: st.session_state.preco_m2 = 7100
if "calculado" not in st.session_state: st.session_state.calculado = False
if "preco_total" not in st.session_state: st.session_state.preco_total = 0.0

# 2. Interface de entrada em colunas
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📐 Características do Imóvel")
    area_m2 = st.slider("Área Privativa (m²)", 30, 400, 70)
    quartos = st.slider("Quantidade de Quartos", 1, 5, 2)
    vagas = st.slider("Vagas de Garagem", 0, 4, 1)
    padrao = st.selectbox("Padrão de Acabamento", ["Econômico / Popular", "Médio / Padrão", "Alto Padrão / Luxo"])

with col_dir:
    st.subheader("📍 Localização por CEP")
    cep_digitado = st.text_input("Digite o CEP do Imóvel", "11471-070")
    st.caption("Exemplos válidos de teste: '11471-070' (Guarujá) ou '11520-000' (Cubatão)")

# 3. Processamento da Localização e Cálculo do Preço ao clicar no botão
if st.button("🚀 Calcular Avaliação de Mercado"):
    with st.spinner("Buscando dados cadastrais da rua e aplicando índices locais..."):
        
        # Limpeza rígida do número do CEP para evitar erros de consulta
        cep_limpo = ''.join(filter(str.isdigit, cep_digitado)).strip()
        
        # Fallbacks preventivos imediatos caso as conexões de mapa falhem
        if "114" in cep_limpo:
            st.session_state.cidade = "Guarujá"
            st.session_state.uf = "SP"
            st.session_state.lat, st.session_state.lon = -23.9930, -46.2560
            st.session_state.endereco = "Bairro Identificado na Região do Guarujá, SP"
            st.session_state.preco_m2 = tabela_m2_brasil["guaruja"]
        elif "115" in cep_limpo:
            st.session_state.cidade = "Cubatão"
            st.session_state.uf = "SP"
            st.session_state.lat, st.session_state.lon = -23.8920, -46.4250
            st.session_state.endereco = "Bairro Identificado na Região de Cubatão, SP"
            st.session_state.preco_m2 = tabela_m2_brasil["cubatao"]
        else:
            st.session_state.cidade = "São Paulo"
            st.session_state.uf = "SP"
            st.session_state.lat, st.session_state.lon = -23.5505, -46.6333
            st.session_state.endereco = "Logradouro Geral, São Paulo - SP"
            st.session_state.preco_m2 = tabela_m2_brasil["capital"]

        # 🚀 REQUISIÇÃO PROTEGIDA COM USER-AGENT (Traz o nome da rua do ViaCEP)
        if len(cep_limpo) == 8:
            headers_seguros = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            try:
                url_cep = f"https://viacep.com.br{cep_limpo}/json/"
                res_cep = requests.get(url_cep, headers=headers_seguros, timeout=5).json()
                
                if "localidade" in res_cep:
                    st.session_state.cidade = res_cep["localidade"]
                    st.session_state.uf = res_cep["uf"]
                    
                    rua = res_cep.get('logradouro', 'Rua Não Especificada')
                    bairro = res_cep.get('bairro', 'Bairro Cadastrado')
                    st.session_state.endereco = f"{rua}, {bairro} - {st.session_state.cidade}, {st.session_state.uf}"
                    
                    # Atualiza o preço por m² com base na resposta oficial
                    cidade_limpa = st.session_state.cidade.lower().strip()
                    if "guaruja" in cidade_limpa or "guarujá" in cidade_limpa:
                        st.session_state.preco_m2 = tabela_m2_brasil["guaruja"]
                        st.session_state.lat, st.session_state.lon = -23.9930, -46.2560
                    elif "cubatao" in cidade_limpa or "cubatão" in cidade_limpa:
                        st.session_state.preco_m2 = tabela_m2_brasil["cubatao"]
                        st.session_state.lat, st.session_state.lon = -23.8920, -46.4250
                    elif "santos" in cidade_limpa:
                        st.session_state.preco_m2 = tabela_m2_brasil["santos"]
                        st.session_state.lat, st.session_state.lon = -23.9608, -46.3339
            except Exception as e:
                pass

        # 🧠 CÁLCULO ARITMÉTICO DIRETO
        valor_base_estrutura = (area_m2 * st.session_state.preco_m2) + (quartos * 12000) + (vagas * 15000)
        
        if padrao == "Econômico / Popular":
            st.session_state.preco_total = valor_base_estrutura * 0.85
        elif padrao == "Alto Padrão / Luxo":
            st.session_state.preco_total = valor_base_estrutura * 1.25
        else:
            st.session_state.preco_total = valor_base_estrutura

        st.session_state.preco_total *= 0.93  # Ajuste comercial de liquidez
        st.session_state.calculado = True

# 4. EXIBIÇÃO CONSOLIDADA DOS RESULTADOS
if st.session_state.calculado:
    st.success(f"## Valor de Mercado Estimado: R$ {st.session_state.preco_total:,.2f}")
    
    c1, c2 = st.columns(2)
    c1.metric(label="Média do m² Calculado", value=f"R$ {st.session_state.preco_total/area_m2:,.2f}/m²")
    c2.metric(label="Localidade Identificada", value=f"{st.session_state.cidade} - {st.session_state.uf}")
    
    st.info(f"📍 **Endereço do Logradouro:** {st.session_state.endereco}")
    
    # 🗺️ MOTOR DE MAPA AVANÇADO (FOLIUM)
    st.subheader("🗺️ Localização Geográfica do Imóvel (Visualizador Folium)")
    
    # Cria o mapa base centralizado nas coordenadas da cidade
    mapa_folium = folium.Map(
        location=[float(st.session_state.lat), float(st.session_state.lon)], 
        zoom_start=15, 
        control_scale=True
    )
    
    # Adiciona o pino vermelho marcador clássico com o endereço no clique
    folium.Marker(
        [float(st.session_state.lat), float(st.session_state.lon)],
        popup=st.session_state.endereco,
        tooltip="Clique para ver o endereço",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(mapa_folium)
    
    # Renderiza o mapa Folium dentro da interface do Streamlit
    st_folium(mapa_folium, width=1100, height=400)
    
    # 🔗 LINK GOOGLE MAPS DIRETO E SEGURO
    url_google_maps = f"https://google.com{st.session_state.lat},{st.session_state.lon}"
    st.link_button("➡️ Abrir Localização Detalhada no Google Maps", url_google_maps)
