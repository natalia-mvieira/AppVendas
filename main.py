from kivy.app import App
from kivy.lang import Builder #o Buider conecta o main.kv com o main.py
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
import os
from functools import partial
from myfirebase import MyFirebase
from bannervendedores import BannerVendedor
from datetime import date

#cada tela/página do app vai ter uma classe (criada antes do GUI)
#sempre que for criar uma página, fazer primeiro o arquivo .kv dela, depois uma classe específica e adicionar a tela no main.kv

GUI = Builder.load_file('main.kv')  #variável de interface gráfica
class MainApp(App): #é uma subclasse de App
    cliente = None
    produto = None
    unidade = None

    def build(self):
        self.firebase = MyFirebase() #criei uma instância da classe MyFirebase para que no MainApp eu tenha todos os comandos dessa classe
        return GUI

    def on_start(self):
        #carregar fotos de perfil
        arquivos = os.listdir("AplicativoVendas/icones/fotos_perfil") #caminho da pasta onde estão as fotos
        pagina_fotoperfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_fotoperfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source= f"AplicativoVendas/icones/fotos_perfil/{foto}",
                                 on_release= partial(self.mudar_foto_perfil, foto)) #o partial permite passar uma info para uma função que estou usando como parametro, no caso a "foto"
            lista_fotos.add_widget(imagem)

        #carregar fotos clientes
        arquivos = os.listdir("AplicativoVendas/icones/fotos_clientes")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"AplicativoVendas/icones/fotos_clientes/{foto_cliente}",
                                 on_release= partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace(".png", "").capitalize(),
                                on_release= partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        #carregar fotos produtos
        arquivos = os.listdir("AplicativoVendas/icones/fotos_produtos")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        for foto_produto in arquivos:
            imagem = ImageButton(source=f"AplicativoVendas/icones/fotos_produtos/{foto_produto}",
                                 on_release= partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace(".png", "").capitalize(),
                                on_release= partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        #carregar data
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        label_data = pagina_adicionarvendas.ids["label_data"]
        label_data.text = f'Data: {date.today().strftime("%d/%m/%Y")}'

        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):

        try: #tenta carregar as infos do usuário, se não conseguir ele abre normalmente o app no pagina padrão
            with open("refresh_token.txt", 'r') as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # pegar informações do usuário
            link = f"https://aplicativovendashash-b684d-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}" #o local_id foi criado no myfirebase.py
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()

            # preencher foto de perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar #vai servir na hora de adicionar vendedor
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f"AplicativoVendas/icones/fotos_perfil/{avatar}"

            #preencher total de vendas
            total_vendas = requisicao_dic['total_vendas']
            self.total_vendas = total_vendas
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'

            #preencher equipe
            self.equipe = requisicao_dic['equipe']

            #preencher id_vendedor (o ID único que mostra no app)
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids['ajustespage']
            pagina_ajustes.ids['id_vendedor'].text = f'Seu ID Único: {id_vendedor}'

            # preencher lista de vendas
            try:
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids['homepage']
                lista_vendas = pagina_homepage.ids['lista_vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda["cliente"], data=venda["data"], preco=venda["preco"],
                                         quantidade=venda["quantidade"], unidade=venda['unidade'],
                                         foto_cliente=venda["foto_cliente"], foto_produto=venda["foto_produto"],
                                         produto=venda["produto"])
                    lista_vendas.add_widget(banner)  # add_widget adiciona um item na lista_vendas

            except Exception as erro:
                print(erro)

            #preencher equipe vendedores
            equipe = requisicao_dic['equipe']
            lista_equipe = equipe.split(',')
            pagina_listavendedores = self.root.ids['listarvendedorespage']
            lista_vendedores = pagina_listavendedores.ids['lista_vendedores']

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)

            self.mudar_tela("homepage")

        except:
            pass

    def mudar_foto_perfil(self, foto, *args):
        link = f"https://aplicativovendashash-b684d-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"AplicativoVendas/icones/fotos_perfil/{foto}"

        info = f'{{"avatar": "{foto}"}}' #o dicionário info deve ser editado como texto para ser usado no data. usamos chaves duplas para o f não entender as chaves do dicionario como chaves de formatação. Dentro do dicionário devem ser usadas aspas duplas.
        requisicao = requests.patch(link, data=info ) #para o data o dicionário deve ser formatado na forma de texto

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids['screenmanager'] #self.root faz referencia ao main.kv, o .ids gera um dicionário com as ids das telas
        gerenciador_telas.current = id_tela #faço a minha tela atual ser a tela correspondente ao id_tela

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://aplicativovendashash-b684d-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'  # depois do ? vêm os parêmetros que eu quero. Se dentro do link tenho termos em "", o link deve estar entre ''.
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        pagina_adicionarvendedor = self.root.ids["adicionarvendedorpage"]
        mensagem_texto = pagina_adicionarvendedor.ids['mensagem_outro_vendedor']

        if requisicao_dic == {}:
            mensagem_texto.text = 'Usuário não encontrado'
        else:
            equipe = self.equipe.split(',')
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = "Vendedor já faz parte da equipe"
            else:
                self.equipe = self.equipe + f',{id_vendedor_adicionado}'
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://aplicativovendashash-b684d-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data=info)
                mensagem_texto.text = "Vendedor adicionado com sucesso"
                #adicionar um novo banner na lista de vendedores
                pagina_listavendedores = self.root.ids['listarvendedorespage']
                lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self, foto, *args):
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        self.cliente = foto.replace(".png", "")
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        for item in list(lista_clientes.children): #o.children pega todos os parametros que estão dentro da lista_clientes, no caso, ele vai pegar todos os itens que estão dentro do Grid_Layout de id lista_clientes
            item.color = (1,1,1,1)
            #pintar de azul o item que selecionamos
            #foto -> carrefour.png / Label -> Carrefour -> carrefour -> .png (para verificação)
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        self.produto = foto.replace(".png", "")
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        for item in list(lista_produtos.children): #o.children pega todos os parametros que estão dentro da lista_clientes, no caso, ele vai pegar todos os itens que estão dentro do Grid_Layout de id lista_clientes
            item.color = (1,1,1,1)
            #pintar de azul o item que selecionamos
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        self.unidade = id_label.replace("unidades_", "")
        pagina_adicionarvendas.ids["unidades_kg"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_litros"].color = (1, 1, 1, 1)
        # pintar de azul o item que selecionamos
        pagina_adicionarvendas.ids[id_label].color = (0, 207/255, 219/255, 1)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        pagina_adicionarvendas = self.root.ids['adicionarvendaspage']
        data = pagina_adicionarvendas.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_adicionarvendas.ids["label_preco"].text
        quantidade = pagina_adicionarvendas.ids["quantidade"].text

        if not cliente:
            pagina_adicionarvendas.ids['label_selecione_cliente'].color = (1, 0, 0, 1)
        if not produto:
            pagina_adicionarvendas.ids['label_selecione_produto'].color = (1, 0, 0, 1)
        if not unidade:
            pagina_adicionarvendas.ids['unidades_kg'].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids['unidades_unidades'].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids['unidades_litros'].color = (1, 0, 0, 1)
        if not preco:
            pagina_adicionarvendas.ids['label_preco'].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids['label_preco'].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_adicionarvendas.ids['quantidade_total'].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids['quantidade_total'].color = (1, 0, 0, 1)

        #dado que ele preencheu tudo
        if produto and cliente and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade) == float):
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"
            info = f'{{"cliente": "{cliente}","produto": "{produto}","foto_cliente": "{foto_cliente}", '\
                    f'"foto_produto": "{foto_produto}","data": "{data}","unidade": "{unidade}",' \
                    f'"preco": "{preco}", "quantidade": "{quantidade}"}}'
            requests.post(f"https://aplicativovendashash-b684d-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}", data=info)

            banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente,
                                 foto_produto=foto_produto, data=data,unidade=unidade, preco=preco,
                                 quantidade=quantidade)
            pagina_homepage = self.root.ids["homepage"]
            lista_vendas = pagina_homepage.ids["lista_vendas"]
            lista_vendas.add_widget(banner)

            requisisao = requests.get(f"https://aplicativovendashash-b684d-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}")
            total_vendas = float(requisisao.json())
            total_vendas += preco*quantidade
            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://aplicativovendashash-b684d-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}", data=info)
            homepage = self.root.ids["homepage"]
            homepage.ids["label_total_vendas"].text = f'[color=#000000]Total de Vendas: [/color] [b]R${total_vendas:,.2f}[/b]'
            self.mudar_tela("homepage")

        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
        pagina_todas_vendas = self.root.ids["todasvendaspage"]
        lista_vendas = pagina_todas_vendas.ids["lista_vendas"]

        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)
        # pegar informações da empresa
        link = f'https://aplicativovendashash-b684d-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        # preencher foto da empresa
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"AplicativoVendas/icones/fotos_perfil/hash.png"

        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try: #para não dar erro se o usuário não tiver vendas
                vendas = requisicao_dic[local_id_usuario]["vendas"]
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    total_vendas += float(venda["preco"])*float(venda["quantidade"])
                    banner = BannerVenda(cliente=venda["cliente"], data=venda["data"], preco=venda["preco"],
                                         quantidade=venda["quantidade"], unidade=venda['unidade'],
                                         foto_cliente=venda["foto_cliente"], foto_produto=venda["foto_produto"],
                                         produto=venda["produto"])
                    lista_vendas.add_widget(banner)
            except:
                pass

        # preencher total de vendas
        pagina_todas_vendas.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'

        self.mudar_tela("todasvendaspage")

    def sair_todas_vendas(self, id_tela):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"AplicativoVendas/icones/fotos_perfil/{self.avatar}"
        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):
        try:
            vendas = dic_info_vendedor["vendas"]
            pagina_vendasoutrovendedor = self.root.ids["vendasoutrovendedorpage"]
            lista_vendas = pagina_vendasoutrovendedor.ids["lista_vendas"]
            for item in list(lista_vendas.children):
                lista_vendas.remove_widget(item)

            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda["cliente"], data=venda["data"], preco=venda["preco"],
                                     quantidade=venda["quantidade"], unidade=venda['unidade'],
                                     foto_cliente=venda["foto_cliente"], foto_produto=venda["foto_produto"],
                                     produto=venda["produto"])
                lista_vendas.add_widget(banner)
        except:
            pass
        total_vendas = dic_info_vendedor["total_vendas"]
        pagina_vendasoutrovendedor.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'
        foto_perfil = self.root.ids["foto_perfil"]
        avatar = dic_info_vendedor["avatar"]
        foto_perfil.source = f"AplicativoVendas/icones/fotos_perfil/{avatar}"

        self.mudar_tela("vendasoutrovendedorpage")



MainApp().run()


