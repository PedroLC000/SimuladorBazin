import warnings
import pandas as pd
import streamlit as st

class App():

    def __init__(self):
        self.pageConfig = st.set_page_config(page_title='Simulador Método Bazin', page_icon=None, layout="centered", initial_sidebar_state="collapsed", menu_items=None)
        self.pageConfig = st.title('Simulador Método Bazin', help = 'O Método de Décio Bazin é uma forma majoritariamente quantitativa e matemática para escolher ações. Assim, ela dá prioridade a múltiplos de investimento e dados na hora de fazer suas filtragens. Portanto, esse simulador tem a função de realizar um filtro naquelas empresas que atendem os requisitos desse método para encontrar as melhores opções de ativos disponíveis no mercado')
        self.filtroPerenidade = ['Utilidade Pública', 'Bens Industriais', 'Financeiro', 'Materiais Básicos', 'Consumo não Cíclico']
        self.colunasRetornoRent = ['1 Mês Atrás', '3 Mêses Atrás', 'Último 1 Ano', 'Último 2 Anos', 'Último 5 Anos', 'Últimos 10 Anos']
        self.colunasRetornoDG = ['DY', 'Liquidez Média Diaria', 'Dívida Líquida/Ebitda', 'Dívida Líquida/Patrimônio', 'Setor']
        self.colunasRetornoRentReal = ['rent_real_mes', 'rent_real_3_meses', 'rent_real_1_ano', 'rent_real_2_anos', 'rent_real_5_anos', 'rent_real_10_anos']

    def datasetRead(self):
        self.dataset = pd.read_csv("./data/companies_treated.csv", delimiter = ';').rename(columns={'empresa' : 'Empresa', 'cotacao' : 'Cotação', 'dividend yield' : 'DY', 'liquidez media diaria' : 'Liquidez Média Diaria', 'dívida líquida/ebitda' : 'Dívida Líquida/Ebitda', 'dívida líquida/patrimônio' : 'Dívida Líquida/Patrimônio', 'setor': 'Setor', 'rent_mes' : '1 Mês Atrás', 'rent_3_meses' : '3 Mêses Atrás', 'rent_1_ano' : 'Último 1 Ano', 'rent_2_anos' : 'Último 2 Anos', 'rent_5_anos' : 'Último 5 Anos', 'rent_10_anos' : 'Últimos 10 Anos'})
    
    def datasetView(self):
        with st.form(key='my_form'):
            self.dataset = self.dataset.set_index('Empresa')
            self.listSelect = self.dataset['codigo'].tolist()
            self.listSelect.insert(0, 'Todos os Ativos')
            self.listAtivos = st.multiselect('Selecione os ativos', self.listSelect, placeholder = 'Ex: TAEE4, BBAS3, SULA11', help = "A opção 'Todos os Ativos' tende a demorar devido a quantidade de ativos disponíveis, logo, escolha ativos de forma personalizada")
            if "Todos os Ativos" in self.listAtivos:
                self.listAtivos = self.dataset['codigo'].tolist()
            self.statusAtivos = st.form_submit_button('Confirmar')

        if self.statusAtivos:
            self.guias = st.tabs(self.listAtivos)
            self.ativosGuias = [self.dataset.loc[(self.dataset.codigo == x)] for x in self.listAtivos]
            for cont, guia in enumerate(self.guias):
                with guia:
                    st.subheader(self.listAtivos[cont])
                    st.write('''A Ambev S.A., é uma empresa brasileira voltada para a produção de bebidas.
                                Em 2004, ao anunciar sua união com a companhia belga Interbrew, se tornou uma subsidiária do grupo internacional Anheuser-Busch InBev. Negociada na bolsa com o código ABEV3. Sua função principal é a fabricação de bebidas como refrigerantes, cervejas e energéticos.
                                Existente em diferentes estados, a Ambev está incluída no maior grupo fabricante de cervejas do mundo. Criada em 1999, após a união entre as concorrentes Companhia Cervejaria Brahma e Companhia Antarctica Paulista.
                                Através da influência dos sócios fundadores do grupo, a Ambev adotou um modelo de gestão centrado no desempenho e no alcance das metas financeiras. Tendo como destaque também uma política de meritocracia e uma visão de longo prazo.  Com lucro líquido de 12.188,33 milhões em 2019.''')

                    self.filtroPerene(cont)
                    self.filtroBazin()

                    with st.expander(f'INDICADORES FUNDAMENTALISTAS PRINCIPAIS DA {self.listAtivos[cont]}'):
                        st.write('**Informações Gerais**') 
                        self.retornoDG = self.ativosGuias[cont].loc[:,self.colunasRetornoDG]
                        st.write(self.retornoDG)

                        st.write('**Rentabilidade x Rentabilidade Real**')
                        self.concatDF = pd.concat([self.ativosGuias[cont].loc[:,self.colunasRetornoRent], self.ativosGuias[cont].loc[:,self.colunasRetornoRentReal].rename(columns={'rent_real_mes' : '1 Mês Atrás', 'rent_real_3_meses' : '3 Mêses Atrás', 'rent_real_1_ano' : 'Último 1 Ano', 'rent_real_2_anos' : 'Último 2 Anos', 'rent_real_5_anos' : 'Último 5 Anos', 'rent_real_10_anos' : 'Últimos 10 Anos'})], axis=0)
                        self.resetIndexDF = self.concatDF.reset_index(drop=True).T
                        self.renameIndexDF = self.resetIndexDF.rename(columns={0 : "Rentabilidade", 1 : "Rentabilidade Real"})
                        st.line_chart(self.renameIndexDF)
                        
                        self.precoTeto = round(16.67*((self.retornoDG['DY']/100)*self.ativosGuias[cont]['Cotação']), 2)
                        if not self.statusFiltro:
                            st.write(f"**Recomendação de Compra** ❌")
                            st.write("A situação de compra é não recomendada devido ao ativo não atender os requisitos do método")
                        else:
                            if float(self.ativosGuias[cont]['Cotação']) <= self.precoTeto[0]:
                                st.write(f"**Recomendação de Compra** ✅")
                                st.write(f"De acordo com Bazin o preço máximo atual é de {self.precoTeto[0]} para {self.listAtivos[cont]}") 
                                st.write(f"Logo, a situação de compra é recomendada devido ao preço mais recente ser de {str(self.ativosGuias[cont]['Cotação'][0])} e por atender os requisitos do método") 
                            else:
                                st.write(f"**Recomendação de Compra** ❌")
                                st.write(f"De acordo com Bazin o preço máximo atual é de {self.precoTeto[0]} para {self.listAtivos[cont]}") 
                                st.write(f"Logo, o ativo está considerado caro devido o ser preço mais recente ser de {self.ativosGuias[cont]['Cotação'][0]}")

                    with st.expander('INFORMAÇÕES COMPLEMENTARES'):
                        st.write('''A empresa AMBEV, está listada na B3 com um valor de mercado de 207,79 Bilhões, tendo um patrimônio de 85,07 Bilhões.
                                    Com um total de 29.607 funcionários, a empresa está listada na Bolsa de Valores no setor de Consumo não Cíclico e no segmento Cervejas e Refrigerantes.
                                    Nos últimos 12 meses a empresa teve um faturamento de 82,71 Bilhões, que gerou um lucro no valor de 14,72 Bilhões.
                                    Quanto aos seus principais indicadores, a empresa possui um P/L de 14,55, um P/VP de 2,44 e nos últimos 12 meses o dividend yeld da AMBEV ficou em 5,78% .''')

    def filtroPerene(self, cont):
        if st.session_state['Perene'] == 'Sim':
            self.statusFiltro = float(self.ativosGuias[cont]['Liquidez Média Diaria']/100000) >= float(st.session_state['Liquidez']) and float(self.ativosGuias[cont]['DY']) >= float(st.session_state['Dividend Yield']) and float(self.ativosGuias[cont]['Dívida Líquida/Ebitda']) <= float(st.session_state['Dívida Líquida/EBITDA']) and float(self.ativosGuias[cont]['Dívida Líquida/Patrimônio']) <= float(st.session_state['Dívida Líquida/Patrimônio Líquido']) and str(self.ativosGuias[cont]['Setor'].iloc[0]) in self.filtroPerenidade
        else:
            self.statusFiltro = float(self.ativosGuias[cont]['Liquidez Média Diaria']/100000) >= float(st.session_state['Liquidez']) and float(self.ativosGuias[cont]['dividend yield']) >= float(st.session_state['Dividend Yield']) and float(self.ativosGuias[cont]['Dívida Líquida/Ebitda']) <= float(st.session_state['Dívida Líquida/EBITDA']) and float(self.ativosGuias[cont]['Dívida Líquida/Patrimônio']) <= float(st.session_state['Dívida Líquida/Patrimônio Líquido'])
    
    def filtroBazin(self):
        if self.statusFiltro:
            st.write('**Status:** Aprovada no método Décio Bazin ✅') 
        else:
            st.write('**Status:** Reprovada no método Décio Bazin ❌')

    def sideBar(self):
        st.sidebar.title('Pontos Fundamentais: ')
        st.session_state['Liquidez'] = st.sidebar.slider('Liquidez', 0, 100, 5, help='Indica a possibilidade de transformar um ativo financeiro em dinheiro no mesmo dia em que o investidor solicita o resgate. Recomendado acima de 5')
        st.session_state['Dividend Yield'] = st.sidebar.slider('Dividend Yield', 1, 100, 4, help="Indicador utilizado para relacionar os proventos pagos por uma empresa e o preço atual de suas ações. Recomendado acima de 6")
        st.session_state['Dívida Líquida/EBITDA'] = st.sidebar.slider('Dívida Líquida/EBITDA', 0, 100, 3, help='Indica quanto tempo seria necessário para pagar a dívida líquida da empresa considerada o EBITDA atual. Indica também o grau de envividamento da empresa. Recomendado abaixo de 3')
        st.session_state['Dívida Líquida/Patrimônio Líquido'] = st.sidebar.slider('Dívida Líquida/Patrimônio Líquido', 0, 100, 1, help='Indica quanto de dívida uma empresa está usasndo para financiar os seus ativos em relação ao patrimônio dos acionistas. Recomendado abaixo de 1')
        st.session_state['Perene'] = st.sidebar.radio('Setores Perenes:', ['Sim','Não'], help = 'Os setores perenes são aqueles que são considerados estáveis e duradouros ao longo do tempo, com uma demanda constante e uma tendência a sobreviver a flutuações econômicas')

    def initializeSession(self):
        if 'Liquidez' not in st.session_state: 
            st.session_state['Liquidez'] = 500000
        if 'Dividend Yield' not in st.session_state.keys(): 
            st.session_state.messages['Dividend Yield'] = 6
        if 'Dívida Líquida/EBITDA' not in st.session_state: 
            st.session_state['Dívida Líquida/EBITDA'] = 3
        if 'Dívida Líquida/Patrimônio Líquido' not in st.session_state: 
            st.session_state['Dívida Líquida/Patrimônio Líquido'] = 1
        if 'Perene' not in st.session_state: 
            st.session_state['Perene'] = 'Sim'

if __name__ == "__main__":

    warnings.simplefilter(action='ignore', category=FutureWarning)

    app = App()
    app.datasetRead()
    app.sideBar()
    app.initializeSession()
    app.datasetView()
    