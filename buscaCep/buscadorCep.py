import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import json
import os
import requests

valorPadx = 5
valorPady = 5

fonte = ['Calibri', 16]

largura = 20

ARQUIVO_JSON = 'bucadorcep.json' 

def limpar_tabela():
    for item in tabela.get_children():
        tabela.delete(item)

def preencher_campos(event):
    item_selecionado = tabela.selection()[0]
    valores = tabela.item(item_selecionado, 'values')
    print(f"Rua selecionada: {valores[0]}")

def validar_cep(cep):
    cep_limpo = ''.join(filter(str.isdigit, cep))
    return cep_limpo if len(cep_limpo) == 8 else None

def pesquisarcep():
    cep = entryCep.get().strip()
    if not cep:
        messagebox.showerror("Erro", "Por favor, insira um CEP válido.")
        return

    cep_valid = validar_cep(cep)
    if not cep_valid:
        messagebox.showerror("Erro", "CEP inválido! Digite um CEP com 8 dígitos.")
        return

    try:
        url = f"https://viacep.com.br/ws/{cep_valid}/json/"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            dados = response.json()

            if 'erro' in dados:
                messagebox.showerror("Erro", "CEP não encontrado!")
                return

            limpar_tabela()
            tabela.insert('', 'end', values=(
                dados.get('cep', ''),
                dados.get('logradouro', ''),
                dados.get('bairro', ''),
                dados.get('localidade', ''),
                dados.get('uf', '')
            ))

            dados_salvos = {
                'cep': cep_valid,
                'logradouro': dados.get('logradouro', ''),
                'bairro': dados.get('bairro', ''),
                'localidade': dados.get('localidade', ''),
                'uf': dados.get('uf', '')
            }
            salvarpesquisas(dados_salvos)
            messagebox.showinfo("Sucesso", "CEP encontrado com sucesso!")
        else:
            messagebox.showerror("Erro", "Erro ao buscar CEP.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")

def salvarpesquisas(dados):
    try:
        if os.path.exists(ARQUIVO_JSON):
            with open(ARQUIVO_JSON, 'r', encoding='utf-8') as arquivo:
                historico = json.load(arquivo)
        else:
            historico = []

        historico.append(dados)

        with open(ARQUIVO_JSON, 'w', encoding='utf-8') as arquivo:
            json.dump(historico, arquivo, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar a pesquisa: {str(e)}")

def atualizar_tabela():
    try:
        if os.path.exists(ARQUIVO_JSON):
            with open(ARQUIVO_JSON, 'r', encoding='utf-8') as arquivo:
                historico = json.load(arquivo)

            limpar_tabela()

            for dados in historico:
                tabela.insert('', 'end', values=(
                    dados.get('cep', ''),
                    dados.get('logradouro', ''),
                    dados.get('bairro', ''),
                    dados.get('localidade', ''),
                    dados.get('uf', '')
                ))

            messagebox.showinfo("Atualizado", "Tabela atualizada com o histórico.")
        else:
            messagebox.showinfo("Info", "Arquivo de histórico não encontrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar tabela: {str(e)}")

def deletar():
    cep_para_deletar = entryCep.get().strip()
    cep_valid = validar_cep(cep_para_deletar)

    if not cep_valid:
        messagebox.showerror("Erro", "Digite um CEP válido para deletar.")
        return

    if not os.path.exists(ARQUIVO_JSON):
        messagebox.showinfo("Aviso", "Nenhum histórico encontrado para deletar.")
        return

    try:
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as arquivo:
            historico = json.load(arquivo)

        novo_historico = [item for item in historico if item.get('cep') != cep_valid]

        if len(novo_historico) == len(historico):
            messagebox.showinfo("Aviso", f"O CEP {cep_valid} não foi encontrado no histórico.")
        else:
            with open(ARQUIVO_JSON, 'w', encoding='utf-8') as arquivo:
                json.dump(novo_historico, arquivo, ensure_ascii=False, indent=4)
            messagebox.showinfo("Sucesso", f"O CEP {cep_valid} foi removido.")
            atualizar_tabela()
            entryCep.delete(0, ctk.END)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao deletar o CEP: {str(e)}")

def carregarhistorico():
    atualizar_tabela()

def limpar_campos():
    entryCep.delete(0, ctk.END)
    limpar_tabela()

def preencher_campos(event):
    item_selecionado = tabela.focus()
    valores = tabela.item(item_selecionado, 'values')
    if valores:
        entryCep.delete(0, ctk.END)
        entryCep.insert(0, valores[0]) 
        
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

buscacep = ctk.CTk()
buscacep.title("Consulta de CEP")
buscacep.geometry("800x600")

fonte = ("Arial", 12)

janela = ctk.CTkFrame(buscacep)
janela.pack(padx=10, pady=10)

labelCep = ctk.CTkLabel(janela, text='Digite o CEP que deseja encontrar', font=fonte)
labelCep.grid(row=0, column=0, padx=valorPadx, pady=valorPady)

entryCep = ctk.CTkEntry(janela, font=fonte, width=250)
entryCep.grid(row=1, column=0, padx=valorPadx, pady=valorPady)

ButtonPesquisar = ctk.CTkButton(janela, text='Pesquisar', command=pesquisarcep)
ButtonPesquisar.grid(row=2, column=0, padx=valorPadx, pady=valorPady)

ButtonHistorico = ctk.CTkButton(janela, text='Carregar Histórico', command=carregarhistorico)
ButtonHistorico.grid(row=3, column=0, padx=valorPadx, pady=valorPady)

ButtonLimpar = ctk.CTkButton(janela, text='Limpar', command=deletar)
ButtonLimpar.grid(row=4, column=0, padx=valorPadx, pady=valorPady)

frame_tabela = ctk.CTkFrame(buscacep)
frame_tabela.pack(padx=10, pady=10, fill='both')

tabela = ttk.Treeview(frame_tabela, columns=('Cep','Rua', 'Bairro', 'Cidade', 'Estado'), show='headings')

tabela.heading('Cep', text='Cep')
tabela.heading('Rua', text='Rua')
tabela.heading('Bairro', text='Bairro')
tabela.heading('Cidade', text='Cidade')
tabela.heading('Estado', text='Estado')

tabela.column('Cep', width=150)
tabela.column('Rua', width=150)
tabela.column('Bairro', width=150)
tabela.column('Cidade', width=150)
tabela.column('Estado', width=100)

scrollbar = ttk.Scrollbar(frame_tabela, orient='vertical', command=tabela.yview)
tabela.configure(yscroll=scrollbar.set)
scrollbar.pack(side='right', fill='y')
tabela.pack(fill='both', expand=True)
tabela.bind('<ButtonRelease-1>', preencher_campos)

buscacep.mainloop()
