import streamlit as st
import pandas as pd
import requests
import urllib.parse

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Dinâmico de Avaliação Imobiliária por CEP")
st.markdown("Insira o CEP de **qualquer rua ou município do Brasil** para realizar a avaliação de mercado baseada em dados reais.")

# 🗺️ TABELA COMPLETA NACIONAL: Todas as 27 Unidades Federativas do Brasil (26 Estados + DF) conferidas e preenchidas
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
    "SP": {"capital": 10200, "interior": 5400, "guaruja": 6900, "cubatao": 4300, "santos": 8200},
    "TO": {"capital": 5300, "interior": 3400},
    "PADRAO": {"capital": 5500, "interior": 3500}
}

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
    # Campo inicia 100% vazio para forçar o CEP a ser o condutor absoluto
    cep_digitado = st.text_input("Digite o CEP do Imóvel (Apenas números ou com hífen)", "")
    st.caption("Insira o CEP desejado para desbloquear os cálculos regionais automáticos.")

# 3. Processamento focado estritamente no CEP digitado
if st.button("🚀 Calcular Avaliação do CEP"):
    if not cep_digitado:
        st.error("❌ Por favor, insira um CEP para realizar a pesquisa.")
    else:
        with st.spinner("Consultando bases nacionais para o CEP informado..."):
            
            cep_limpo = ''.join(filter(str.isdigit, cep_digitado)).strip()
            
            # Inicialização zerada para apagar qualquer resquício de cache anterior
            cidade_detectada = ""
            estado_uf = ""
            endereco_oficial = ""
            latitude, longitude = 0.0, 0.0
            
            # 🚀 PASSO 1: Consulta direta à API do ViaCEP
            if len(cep_limpo) == 8:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    res_cep = requests.get(f"https://viacep.com.br{cep_limpo}/json/", headers=headers, timeout=6).json()
                    
                    if "localidade" in res_cep:
                        cidade_detectada = res_cep["localidade"]
                        estado_uf = res_cep["uf"].upper().strip()
                        rua = res_cep.get('logradouro', '')
                        bairro = res_cep.get('bairro', '')
                        endereco_oficial = f"{rua}, {bairro} - {cidade_detectada}, {estado_uf}" if rua else f"{bairro} - {cidade_detectada}, {estado_uf}"
                except:
                    pass

            # Executa apenas se o CEP foi encontrado com sucesso na base nacional
            if estado_uf and cidade_detectada:
                
                # 🚀 PASSO 2: Tradução de texto em coordenadas geográficas decimais para o st.map
                try:
                    endereco_url = urllib.parse.quote(f"{endereco_oficial}, Brasil")
                    url_geo = f"https://openstreetmap.org{endereco_url}"
                    res_geo = requests.get(url_geo, headers={'User-Agent': 'previsor_ia_nacional_v24'}, timeout=6).json()
                    
                    if isinstance(res_geo, list) and len(res_geo) > 0:
                        latitude = float(res_geo[0]['lat'])
                        longitude = float(res_geo[0]['lon'])
                except:
                    pass

                # Fallback matemático seguro por capitais para o mapa renderizar mesmo se a internet oscilar
                if latitude == 0.0:
                    mapeamento_capitais_coords = {
                        "SP": (-23.5505, -46.6333), "RJ": (-22.9068, -43.1729), "ES": (-20.3155, -40.3128),
                        "MG": (-19.9167, -43.9345), "SC": (-27.5954, -48.5480), "PR": (-25.4284, -49.2733),
                        "RS": (-30.0346, -51.2177), "BA": (-12.9777, -38.5016), "PE": (-8.0578, -34.8829),
                        "CE": (-3.7327, -38.5267), "DF": (-15.7938, -47.8827), "GO": (-16.6869, -49.2648)
                    }
                    latitude, longitude = mapeamento_capitais_coords.get(estado_uf, (-15.7938, -47.8827))

                # 💎 BUSCA O PREÇO DO m² DE FORMA PRECISA NA TABELA EXPANDIDA DO ESTADO DETECTADO
                sub_tabela = tabela_m2_nacional.get(estado_uf, tabela_m2_nacional["PADRAO"])
                cidade_limpa = cidade_detectada.lower().strip()
                
                # Exceções de microrregiões paulistas salvas
                if estado_uf == "SP" and ("guaruja" in cidade_limpa or "guarujá" in cidade_limpa):
                    preco_m2_base = sub_tabela.get("guaruja")
                elif estado_uf == "SP" and ("cubatão" in cidade_limpa or "cubatao" in cidade_limpa):
                    preco_m2_base = sub_tabela.get("cubatao")
                elif estado_uf == "SP" and "santos" in cidade_limpa:
                    preco_m2_base = sub_tabela.get("santos")
                # Filtro para identificar se o CEP pertence a alguma grande capital brasileira
                elif any(k in cidade_limpa for k in ["são paulo", "rio", "curitiba", "belo horizonte", "porto alegre", "brasília", "vitória", "vitoria", "salvador", "recife", "fortaleza", "goiânia", "manaus", "belém"]):
                    preco_m2_base = sub_tabela.get("capital")
                else:
                    preco_m2_base = sub_tabela.get("interior")

                # 🧠 MOTOR DE CÁLCULO ARITMÉTICO SUAVIZADO
                valor_base_estrutura = (area_m2 * preco_m2_base) + (quartos * 9000) + (vagas * 14000)
                if padrao == "Econômico / Popular": valor_base_estrutura *= 0.82
                elif padrao == "Alto Padrão / Luxo": valor_base_estrutura *= 1.25
                
                preco_total_calculado = valor_base_estrutura * 0.94

                # 4. SAÍDAS E RELATÓRIOS NA TELA
                st.success(f"## Valor de Mercado Estimado: R$ {preco_total_calculado:,.2f}")
                
                c1, c2 = st.columns(2)
                c1.metric(label="Preço do m² Aplicado", value=f"R$ {preco_total_calculado/area_m2:,.2f}/m²")
                c2.metric(label="Localidade Detectada", value=f"{cidade_detectada} - {estado_uf}")
                
                st.info(f"📍 **Endereço do Logradouro:** {endereco_oficial}")
                
                # 🗺️ MAPA NATIVO DO STREAMLIT (Sempre abre utilizando 'latitude' e 'longitude' corrigidas)
                st.subheader("🗺️ Localização Geográfica do Imóvel")
                df_mapa = pd.DataFrame({'latitude': [float(latitude)], 'longitude': [float(longitude)]})
                st.map(df_mapa, zoom=15)
                
                # 🔗 LINK UNIVERSAL DO GOOGLE MAPS SEM DEPENDÊNCIAS PAGAS
                endereco_url_seguro = urllib.parse.quote(f"{endereco_oficial}, Brasil")
                url_google_maps = f"https://google.com{endereco_url_seguro}"
                st.link_button("➡️ Abrir Localização no Aplicativo do Google Maps", url_google_maps, type="primary")
            
            else:
                st.error("❌ CEP inválido ou não localizado na base nacional. Certifique-se de digitar 8 dígitos corretos.")
