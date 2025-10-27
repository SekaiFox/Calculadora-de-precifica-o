import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from precificacao import compute_pricing, carregar_totais_custos, TAXAS_MARKETPLACES

class CalculadoraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Precificação")
        self.root.geometry("1200x800")
        
        # Configurar tema escuro
        self.root.configure(bg='#1e1e1e')
        style = ttk.Style(self.root)
        style.theme_use('equilux')  # Tema escuro moderno
        
        # Configurar estilos personalizados
        style.configure("Title.TLabel", 
                       font=("Segoe UI", 24, "bold"),
                       foreground='#ffffff',
                       background='#1e1e1e')
        
        style.configure("Header.TLabel", 
                       font=("Segoe UI", 14, "bold"),
                       foreground='#ffffff',
                       background='#1e1e1e')
        
        style.configure("TLabel",
                       font=("Segoe UI", 10),
                       foreground='#ffffff',
                       background='#1e1e1e')
        
        style.configure("TEntry",
                       fieldbackground='#2d2d2d',
                       foreground='#ffffff',
                       insertcolor='#ffffff')
        
        style.configure("TButton",
                       font=("Segoe UI", 10),
                       background='#0078d4',
                       foreground='#ffffff')
        
        style.map("TButton",
                 background=[('active', '#1e88e5')],
                 foreground=[('active', '#ffffff')])
                 
        style.configure("TFrame",
                       background='#1e1e1e')
                       
        style.configure("TLabelframe",
                       background='#1e1e1e',
                       foreground='#ffffff')
                       
        style.configure("TLabelframe.Label",
                       font=("Segoe UI", 11, "bold"),
                       foreground='#ffffff',
                       background='#1e1e1e')
        
        # Frame principal com gradiente
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.configure(style="TFrame")
        
        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        
        # Título com ícone
        title_frame = ttk.Frame(main_frame, style="TFrame")
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        title = ttk.Label(title_frame, text="🧮 Calculadora de Precificação", style="Title.TLabel")
        title.pack(pady=(10, 20))
        
        # Container para os frames principais
        content_frame = ttk.Frame(main_frame, style="TFrame")
        content_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Frames com bordas arredondadas e espaçamento
        config_frame = ttk.LabelFrame(content_frame, text="⚙️ Configurações", padding="15")
        config_frame.grid(row=0, column=0, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        product_frame = ttk.LabelFrame(content_frame, text="📦 Dados do Produto", padding="15")
        product_frame.grid(row=1, column=0, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        middle_frame = ttk.Frame(content_frame, style="TFrame")
        middle_frame.grid(row=0, column=1, rowspan=2, padx=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        middle_frame.grid_rowconfigure(1, weight=1)
        
        costs_frame = ttk.LabelFrame(middle_frame, text="💰 Custos Operacionais", padding="15")
        costs_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        result_frame = ttk.LabelFrame(middle_frame, text="📊 Resultados", padding="15")
        result_frame.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurações
        ttk.Label(config_frame, text="Plataforma:").grid(row=0, column=0, padx=5, pady=2)
        self.platform_var = tk.StringVar(value='shopee')
        platform_cb = ttk.Combobox(config_frame, textvariable=self.platform_var, values=list(TAXAS_MARKETPLACES.keys()))
        platform_cb.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Markup (%):").grid(row=1, column=0, padx=5, pady=2)
        self.markup_var = tk.StringVar(value='20.0')
        ttk.Entry(config_frame, textvariable=self.markup_var).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Imposto (0.10 = 10%):").grid(row=2, column=0, padx=5, pady=2)
        self.tax_var = tk.StringVar(value='0.10')
        ttk.Entry(config_frame, textvariable=self.tax_var).grid(row=2, column=1, padx=5, pady=2)
        
        # Dados do produto
        ttk.Label(product_frame, text="Custo do produto (R$):").grid(row=0, column=0, padx=5, pady=2)
        self.product_cost_var = tk.StringVar(value='0.00')
        ttk.Entry(product_frame, textvariable=self.product_cost_var).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(product_frame, text="Custo embalagem (R$):").grid(row=1, column=0, padx=5, pady=2)
        self.packaging_cost_var = tk.StringVar(value='0.00')
        ttk.Entry(product_frame, textvariable=self.packaging_cost_var).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(product_frame, text="Custo frete (R$):").grid(row=2, column=0, padx=5, pady=2)
        self.shipping_cost_var = tk.StringVar(value='0.00')
        ttk.Entry(product_frame, textvariable=self.shipping_cost_var).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(product_frame, text="Adicional (R$):").grid(row=3, column=0, padx=5, pady=2)
        self.additional_cost_var = tk.StringVar(value='0.00')
        ttk.Entry(product_frame, textvariable=self.additional_cost_var).grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(product_frame, text="Lucro desejado (R$):").grid(row=4, column=0, padx=5, pady=2)
        self.desired_profit_var = tk.StringVar(value='0.00')
        ttk.Entry(product_frame, textvariable=self.desired_profit_var).grid(row=4, column=1, padx=5, pady=2)
        
        # Botão calcular
        ttk.Button(product_frame, text="Calcular", command=self.calculate).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Área de resultados com estilo moderno
        self.result_text = tk.Text(result_frame, 
                                 width=50, 
                                 height=20, 
                                 font=("Consolas", 10),
                                 bg='#2d2d2d',
                                 fg='#ffffff',
                                 insertbackground='#ffffff',
                                 selectbackground='#0078d4',
                                 selectforeground='#ffffff',
                                 relief='flat',
                                 padx=10,
                                 pady=10)
        self.result_text.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Carregar custos
        self.load_costs()
        
    def load_costs(self):
        """Carrega custos dos arquivos JSON."""
        self.costs = carregar_totais_custos()
        total_costs = self.costs['total_variavel'] + self.costs['total_fixo']
        ttk.Label(self.root, text=f"Total custos: R$ {total_costs:.2f}").grid(row=3, column=0, columnspan=3, pady=5)
    
    def calculate(self):
        """Executa o cálculo de preço e mostra resultados."""
        try:
            result = compute_pricing(
                markup_produto=float(self.markup_var.get()),
                plataforma=self.platform_var.get(),
                imposto=float(self.tax_var.get()),
                difal=0.0,  # Simplificado nesta versão
                faturamento_esperado=10000.0,  # Valor padrão
                custo_produto=float(self.product_cost_var.get()),
                custo_embalagem=float(self.packaging_cost_var.get()),
                custo_frete=float(self.shipping_cost_var.get()),
                adicional=float(self.additional_cost_var.get()),
                lucro_desejado=float(self.desired_profit_var.get()),
                total_variavel=self.costs['total_variavel'],
                total_fixo=self.costs['total_fixo'],
            )
            
            # Formata e mostra resultados
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "=== RESULTADO ===\n\n")
            self.result_text.insert(tk.END, f"Preço sugerido: R$ {result['preco_venda']:.2f}\n")
            self.result_text.insert(tk.END, f"Valor faturamento: R$ {result['valor_faturamento']:.2f}\n")
            self.result_text.insert(tk.END, f"Valor lucro: R$ {result['valor_lucro']:.2f}\n")
            self.result_text.insert(tk.END, f"Margem: {result['margem_percentual']:.2f}%\n\n")
            
            self.result_text.insert(tk.END, "=== DETALHAMENTO ===\n\n")
            for k, v in result['breakdown'].items():
                self.result_text.insert(tk.END, f"{k}: R$ {v:.2f}\n")
            
            if result.get('warning'):
                messagebox.showwarning("Atenção", result['warning'])
                
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular: {str(e)}")

def main():
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="equilux")
    except ImportError:
        root = tk.Tk()
        print("Aviso: ttkthemes não encontrado, usando tema padrão")
    
    # Configurar DPI awareness para melhor renderização em telas de alta resolução
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = CalculadoraApp(root)
    
    # Configurar tamanho inicial e posição
    root.geometry("1200x800")  # Tamanho inicial
    root.minsize(1000, 600)     # Tamanho mínimo
    
    # Centralizar na tela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 1200) // 2
    y = (screen_height - 800) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()