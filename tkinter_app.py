import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from precificacao import compute_pricing, carregar_totais_custos, TAXAS_MARKETPLACES

class CalculadoraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Precificação")
        self.root.geometry("1200x800")
        
        # Estilo
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title = ttk.Label(main_frame, text="Calculadora de Precificação", style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Frames
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="5")
        config_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        product_frame = ttk.LabelFrame(main_frame, text="Dados do Produto", padding="5")
        product_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        costs_frame = ttk.LabelFrame(main_frame, text="Custos Operacionais", padding="5")
        costs_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        result_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="5")
        result_frame.grid(row=1, column=2, rowspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
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
        
        # Área de resultados (Text widget com fonte monoespaçada para alinhamento)
        self.result_text = tk.Text(result_frame, width=50, height=20, font=("Courier", 10))
        self.result_text.grid(row=0, column=0, padx=5, pady=5)
        
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
    root = tk.Tk()
    app = CalculadoraApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()