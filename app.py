import streamlit as st
import pandas as pd
import requests
import urllib.parse

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil Pro", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Inteligente de Avaliação Imobiliária Nacional")
st.markdown("Estime o valor de mercado real de imóveis em **qualquer rua ou CEP do Brasil** de forma 100% gratuita.")

# 🗺️ TABELA COMPLETA NACIONAL: Todas as 27 Unidades Federativas do Brasil (26 Estados + DF)
# Valores de m² base baseados nos indicadores econômicos do mercado real
tabela_m2_nacional = {
    "AC": {"capital": 5100, "interior": 3400},
    "AL": {"capital": 6500, "interior": 3800},
    "AM": {"capital": 6900, "interior": 3900},
    "AP": {"capital": 4800, "interior": 3200},
    "BA": {"capital": 6200, "interior": 3600},
    "CE": {"capital": 5900, "interior": 3500},
    "DF": {"capital": 8900, "interior": 5200},
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
    "SP": {"capital": 10200, "interior": 5400, "guaruja": 6900, "cubatao": 4300, "santos": 8200},
    "TO": {"capital": 5300, "interior": 3400},
    "PADRAO": {"capital": 5500, "interior": 3500}
}

# Inicialização das variáveis de controle na sessão do Streamlit
if "lat" not in st.session_state: st.session_state.lat = -23.9922
if "lon" not in st.session_state: st.session_state.lon = -46.2594
if "endereco" not in st.session_state: st.session_state.endereco = "Aguardando digitação do CEP..."
if "cidade" not in st.session_state: st.session_state.cidade = "Guarujá"
if "uf" not in st.session_state: st.session_state.uf = "SP"
if "preco_m2" not in st.session_state: st.session_state.preco_m2 = 6900
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
    st.caption("Digite qualquer CEP do Brasil. Ex: '11471-070' (Guarujá), '11520-000' (Cubatão), '01310-100' (São Paulo)")

# 3. Processamento Dinâmico por APIs Gratuitas de Alta Disponibilidade
if st.button("🚀 Calcular Avaliação de Mercado"):
    with st.spinner("Buscando endereço e calculando preço local de mercado..."):
        
        cep_limpo = ''.join(filter(str.isdigit, cep_digitado)).strip()
        
        # Valores de contingência padrão (Caso a rede caia)
        cidade_detectada = "Guarujá"
        estado_uf = "SP"
        endereco_oficial = f"Região do CEP {cep_digitado}, Brasil"
        
        # Passo 1: Busca o endereço textual completo diretamente na API oficial do ViaCEP
        if len(cep_limpo) == 8:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res_cep = requests.get(f"https://viacep.com.br{cep_limpo}/json/", headers=headers, timeout=5).json()
                if "localidade" in res_cep:
                    cidade_detectada = res_cep["localidade"]
                    estado_uf = res_cep["uf"].upper().strip()
                    rua = res_cep.get('logradouro', '')
                    bairro = res_cep.get('bairro', '')
                    endereco_oficial = f"{rua}, {bairro} - {cidade_detectada}, {estado_uf}"
            except:
                pass

        # Passo 2: Traduz o texto do endereço em Latitude/Longitude para o mapa usando Nominatim público
        try:
            endereco_url = urllib.parse.quote(f"{endereco_oficial}, Brasil")
            url_geo = f"https://openstreetmap.org{endereco_url}"
            res_geo = requests.get(url_geo, headers={'User-Agent': 'previsor_imoveis_v21'}, timeout=5).json()
            if isinstance(res_geo, list) and len(res_geo) > 0:
                st.session_state.lat = float(res_geo[0]['lat'])
                st.session_state.lon = float(res_geo[0]['lon'])
        except:
            # Caso as coordenadas de satélite falhem, mantém localizações macro padrões da Baixada
            if "114" in cep_limpo: st.session_state.lat, st.session_state.lon = -23.9930, -46.2560
            elif "115" in cep_limpo: st.session_state.lat, st.session_state.lon = -23.8920, -46.4250
            else: st.session_state.lat, st.session_state.lon = -23.5505, -46.6333

        # 💎 FILTRO DE PREÇO POR METRO QUADRADO DA SUBTABELA NACIONAL
        sub_tabela = tabela_m2_nacional.get(estado_uf, tabela_m2_nacional["PADRAO"])
        cidade_limpa = cidade_detectada.lower().strip()
        
        if estado_uf == "SP" and ("guaruja" in cidade_limpa or "guarujá" in cidade_limpa):
            preco_m2_base = sub_tabela.get("guaruja")
        elif estado_uf == "SP" and ("cubatão" in cidade_limpa or "cubatao" in cidade_limpa):
            preco_m2_base = sub_tabela.get("cubatao")
        elif estado_uf == "SP" and "santos" in cidade_limpa:
            preco_m2_base = sub_tabela.get("santos")
        elif any(k in cidade_limpa for k in ["são paulo", "rio", "curitiba", "belo horizonte", "porto alegre", "brasília", "recife", "salvador", "fortaleza"]):
            preco_m2_base = sub_tabela.get("capital")
        else:
            preco_m2_base = sub_tabela.get("interior")

        # Atualiza o estado da aplicação
        st.session_state.cidade = cidade_detectada
        st.session_state.uf = estado_uf
        st.session_state.endereco = endereco_oficial
        st.session_state.preco_m2 = preco_m2_base

        # 🧠 MOTOR DE CÁLCULO MATRICIAL DINÂMICO
        valor_base_estrutura = (area_m2 * st.session_state.preco_m2) + (quartos * 9000) + (vagas * 14000)
        if padrao == "Econômico / Popular": valor_base_estrutura *= 0.82
        elif padrao == "Alto Padrão / Luxo": valor_base_estrutura *= 1.25
        
        st.session_state.preco_total = valor_base_estrutura * 0.94
        st.session_state.calculado = True

# 4. EXIBIÇÃO CONSOLIDADA DOS RESULTADOS NA TELA
if st.session_state.calculado:
    st.success(f"## Valor de Mercado Estimado: R$ {st.session_state.preco_total:,.2f}")
    
    c1, c2 = st.columns(2)
    c1.metric(label="Preço do m² Aplicado nesta simulação", value=f"R$ {st.session_state.preco_total/area_m2:,.2f}/m²")
    c2.metric(label="Localidade Identificada", value=f"{st.session_state.cidade} - {st.session_state.uf}")
    
    st.info(f"📍 **Endereço do Logradouro:** {st.session_state.endereco}")
    
    # 🗺️ MAPA NATIVO DO STREAMLIT (Sempre abre se as colunas forem 'latitude' e 'longitude')
    st.subheader("🗺️ Localização Geográfica do Imóvel")
    df_mapa = pd.DataFrame({
        'latitude': [float(st.session_state.lat)],
        'longitude': [float(st.session_state.lon)]
    })
    st.map(df_mapa, zoom=15)
    
    # 🔗 LINK GOOGLE MAPS DIRETO E SEGURO
    endereco_url_seguro = urllib.parse.quote(f"{st.session_state.endereco}, Brasil")
    url_google_maps = f"https://google.com{endereco_url_seguro}"
    st.link_button("➡️ Abrir Localização no Aplicativo do Google Maps", url_google_maps, type="primary")
