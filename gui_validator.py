import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import yaml
from jsonschema import validate, ValidationError

# --- ESPECIFICAÇÃO BÁSICA DO SCHEMA ---
# (O SCHEMA deve ser expandido para uma validação mais completa!)
AUTOSINSTALL_SCHEMA = {
    "type": "object",
    "properties": {
        "autoinstall": {
            "type": "object",
            "properties": {
                "version": {"type": "integer", "enum": [1]},
                "identity": {"type": "object"},
                "storage": {"type": "object"},
            },
            "required": ["version", "identity", "storage"],
            "additionalProperties": True
        }
    },
    "required": ["autoinstall"],
    "additionalProperties": False
}

class AutoinstallValidatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Validador/Corretor Autoinstall Subiquity")

        # Configuração do Container Principal
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)

        # 1. Botões de Ação
        frame_botoes = tk.Frame(master)
        frame_botoes.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        tk.Button(frame_botoes, text="Abrir Arquivo YAML", command=self.abrir_arquivo).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="Salvar Corrigido", command=self.salvar_arquivo).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="VALIDAR e Corrigir", command=self.validar_e_corrigir, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=5)

        # 2. Área de Texto para Edição/Visualização do YAML
        self.yaml_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=30, font=("Courier", 10))
        self.yaml_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.yaml_text.insert(tk.END, "# Cole ou abra seu YAML de Autoinstall aqui...\nautoinstall:\n  version: 1\n  identity:\n    hostname: server01\n    username: ubuntu\n  storage:\n    layout: automatic")

    def abrir_arquivo(self):
        """Abre um arquivo YAML e carrega o conteúdo para a área de texto."""
        caminho_arquivo = filedialog.askopenfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("YAML files", "*.yml"), ("All files", "*.*")]
        )
        if caminho_arquivo:
            try:
                with open(caminho_arquivo, 'r') as f:
                    self.yaml_text.delete(1.0, tk.END)
                    self.yaml_text.insert(tk.END, f.read())
                messagebox.showinfo("Sucesso", f"Arquivo {os.path.basename(caminho_arquivo)} carregado.")
            except Exception as e:
                messagebox.showerror("Erro de Leitura", f"Não foi possível ler o arquivo:\n{e}")

    def salvar_arquivo(self):
        """Salva o conteúdo atual da área de texto em um novo arquivo."""
        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("YAML files", "*.yml")]
        )
        if caminho_arquivo:
            try:
                conteudo = self.yaml_text.get(1.0, tk.END)
                with open(caminho_arquivo, 'w') as f:
                    f.write(conteudo)
                messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{os.path.basename(caminho_arquivo)}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")

    def validar_e_corrigir(self):
        """Função principal para validação e correção do conteúdo."""
        conteudo_original = self.yaml_text.get(1.0, tk.END).strip()
        
        # --- LÓGICA DE CORREÇÃO E VALIDAÇÃO ---
        conteudo_corrigido = conteudo_original

        # 1. Correção do Cabeçalho
        if not conteudo_corrigido.startswith("#cloud-config"):
            conteudo_corrigido = "#cloud-config\n" + conteudo_corrigido
            self.yaml_text.delete(1.0, tk.END)
            self.yaml_text.insert(tk.END, conteudo_corrigido)
            messagebox.showinfo("Correção Aplicada", "Cabeçalho '#cloud-config' adicionado.")

        try:
            # 2. Carregamento e Verificação de Sintaxe YAML
            dados = yaml.safe_load(conteudo_corrigido)
            
            if not isinstance(dados, dict):
                messagebox.showerror("Erro de Sintaxe YAML", "O arquivo não é um objeto YAML válido (dicionário).")
                return

            # 3. Normalização e Correção da Versão
            if 'autoinstall' in dados and 'version' not in dados['autoinstall']:
                 dados['autoinstall']['version'] = 1
                 # Atualizar a área de texto com a correção de versão
                 self.yaml_text.delete(1.0, tk.END)
                 self.yaml_text.insert(tk.END, "#cloud-config\n" + yaml.dump(dados, sort_keys=False))
                 messagebox.showinfo("Correção Aplicada", "Chave 'version: 1' em 'autoinstall' foi adicionada.")
                 # Recarregar o conteúdo para a validação final
                 dados = yaml.safe_load(self.yaml_text.get(1.0, tk.END).strip())

            # 4. Validação Estrutural (Schema)
            validate(instance=dados, schema=AUTOSINSTALL_SCHEMA)
            
            messagebox.showinfo("SUCESSO", "O arquivo YAML está estruturalmente **VÁLIDO** para o Autoinstall!")

        except yaml.YAMLError as e:
            messagebox.showerror("Erro de Sintaxe YAML", f"Falha ao analisar YAML. Verifique a INDENTAÇÃO e SINTAXE:\n{e}")
        except ValidationError as e:
            messagebox.showerror("Erro de Validação", f"A estrutura YAML é inválida! Erro:\n{e.message}\nChave: {list(e.path)}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro desconhecido:\n{e}")

# --- Execução da Aplicação ---
if __name__ == "__main__":
    import os
    # Cria a janela principal do Tkinter
    root = tk.Tk()
    # Instancia a aplicação
    app = AutoinstallValidatorApp(root)
    # Inicia o loop da interface
    root.mainloop()