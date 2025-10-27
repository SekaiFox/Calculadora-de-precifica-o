import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from ttkthemes import ThemedTk
import csv
import io
from precificacao import compute_pricing, carregar_totais_custos, TAXAS_MARKETPLACES
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import os

class CalculadoraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Precificação")
        self.root.geometry("800x800")
        
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
        platform_cb.bind('<<ComboboxSelected>>', lambda e: self._on_platform_change())

        # Tipo de anúncio Mercado Livre (aparece apenas quando selecionado)
        ttk.Label(config_frame, text="Tipo anúncio ML:").grid(row=0, column=2, padx=5, pady=2)
        self.ml_listing_var = tk.StringVar(value='classico')
        self.ml_listing_cb = ttk.Combobox(config_frame, textvariable=self.ml_listing_var, values=['classico', 'premium'], state='disabled', width=10)
        self.ml_listing_cb.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Markup (%):").grid(row=1, column=0, padx=5, pady=2)
        self.markup_var = tk.StringVar(value='20.0')
        self.markup_entry = ttk.Entry(config_frame, textvariable=self.markup_var)
        self.markup_entry.grid(row=1, column=1, padx=5, pady=2)
        # Usar markup checkbox
        self.use_markup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text='Usar markup (%)', variable=self.use_markup_var, command=self._toggle_markup_mode).grid(row=1, column=2, padx=8)
        
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
        self.desired_profit_entry = ttk.Entry(product_frame, textvariable=self.desired_profit_var)
        self.desired_profit_entry.grid(row=4, column=1, padx=5, pady=2)

        # Faturamento mensal desejado (novo input)
        ttk.Label(product_frame, text="Faturamento mensal desejado (R$):").grid(row=5, column=0, padx=5, pady=2)
        self.faturamento_var = tk.StringVar(value='10000.00')
        self.faturamento_entry = ttk.Entry(product_frame, textvariable=self.faturamento_var)
        self.faturamento_entry.grid(row=5, column=1, padx=5, pady=2)
        
        # Mostrar fluxo por pedido (opção)
        self.show_fluxo_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(product_frame, text="Mostrar fluxo por pedido (Faturamento - Custos = Lucro líquido)", variable=self.show_fluxo_var).grid(row=5, column=0, columnspan=2, pady=(6,2), sticky="w")
        
        # Botão calcular
        ttk.Button(product_frame, text="Calcular", command=self.calculate).grid(row=6, column=0, columnspan=2, pady=10)
        
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
        # Botões de export (CSV / PDF)
        btn_frame = ttk.Frame(result_frame, style="TFrame")
        btn_frame.grid(row=1, column=0, pady=(8,0), sticky=(tk.W))
        ttk.Button(btn_frame, text="Exportar CSV", command=self.export_csv).grid(row=0, column=0, padx=(0,8))
        ttk.Button(btn_frame, text="Exportar PDF", command=self.export_pdf).grid(row=0, column=1)
        # Botão para alterar logo (requer senha)
        ttk.Button(btn_frame, text="Alterar logo (requer senha)", command=self.select_logo).grid(row=0, column=2, padx=(8,0))
        # Label do lucro real
        self.lucro_real_label = ttk.Label(result_frame, text="", style='Header.TLabel')
        self.lucro_real_label.grid(row=2, column=0, pady=(8,0), sticky=(tk.W))
        
        # Carregar custos
        self.load_costs()
        # Default protected logo path (user-provided)
        self.default_logo_path = r"G:\Meu Drive\The Fox Company\LOGO LINKEDIN.jpg"
        # By default reports will use the locked logo. An override is only allowed with the password.
        self.logo_override_path = None
        # set initial logo_path to default if it exists
        if os.path.exists(self.default_logo_path):
            self.logo_path = self.default_logo_path
        else:
            self.logo_path = None
        # aplicar estado inicial do modo markup
        try:
            self._toggle_markup_mode()
        except Exception:
            pass
        try:
            self._on_platform_change()
        except Exception:
            pass
        
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
                ml_listing=(self.ml_listing_var.get() if self.platform_var.get() == 'mercado_livre' else None),
                imposto=float(self.tax_var.get()),
                difal=0.0,  # Simplificado nesta versão
                faturamento_esperado=10000.0,  # Valor padrão
                custo_produto=float(self.product_cost_var.get()),
                custo_embalagem=float(self.packaging_cost_var.get()),
                custo_frete=float(self.shipping_cost_var.get()),
                adicional=float(self.additional_cost_var.get()),
                lucro_desejado=float(self.desired_profit_var.get()) if not self.use_markup_var.get() else 0.0,
                total_variavel=self.costs['total_variavel'],
                total_fixo=self.costs['total_fixo'],
                use_markup=self.use_markup_var.get(),
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
            
            # Mostrar fluxo por pedido (faturamento - custos = lucro líquido)
            if self.show_fluxo_var.get():
                faturamento = result.get('preco_venda', 0.0)
                custos_totais = result.get('custos_diretos_por_venda', 0.0) + result.get('taxas_totais_em_reais', 0.0)
                lucro_liquido = result.get('valor_lucro', 0.0)
                self.result_text.insert(tk.END, "\n--- Fluxo por pedido ---\n")
                self.result_text.insert(tk.END, f"Faturamento (preço de venda): R$ {faturamento:.2f}\n")
                self.result_text.insert(tk.END, f"Custos totais (diretos + taxas): R$ {custos_totais:.2f}\n")
                self.result_text.insert(tk.END, f"Lucro líquido: R$ {lucro_liquido:.2f}\n")
                self.result_text.insert(tk.END, f"Equação: R$ {faturamento:.2f} - R$ {custos_totais:.2f} = R$ {lucro_liquido:.2f}\n")

            # Mostrar quantas unidades precisam ser vendidas para atingir o faturamento mensal desejado
            try:
                faturamento_meta = float(self.faturamento_var.get() or 0.0)
                preco_unit = result.get('preco_venda', 0.0)
                unidades_necessarias = faturamento_meta / preco_unit if preco_unit > 0 else float('inf')
                self.result_text.insert(tk.END, f"\nPara atingir faturamento mensal de R$ {faturamento_meta:.2f}, é necessário vender aprox.: {unidades_necessarias:.1f} unidades\n")
            except Exception:
                pass

            # Atualizar label de lucro real (visível abaixo dos resultados)
            lucro_val = result.get('valor_lucro', 0.0)
            margem = result.get('margem_percentual', 0.0)
            texto = f"Lucro real por pedido: R$ {lucro_val:.2f} — Margem: {margem:.2f}%"
            self.lucro_real_label.config(text=texto)
            # cor baseada no sinal do lucro
            if lucro_val >= 0:
                self.lucro_real_label.config(foreground='#77DD77')
            else:
                self.lucro_real_label.config(foreground='#FF6961')

            if result.get('warning'):
                messagebox.showwarning("Atenção", result['warning'])

            # guardar último resultado para export
            self.last_result = result
                
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular: {str(e)}")

    def export_csv(self):
        """Exporta o último resultado para CSV via diálogo de salvamento."""
        if not hasattr(self, 'last_result') or not self.last_result:
            messagebox.showinfo("Exportar CSV", "Nenhum resultado para exportar. Execute um cálculo primeiro.")
            return
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], title='Salvar resumo como CSV')
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['campo', 'valor'])
                res = self.last_result
                writer.writerow(['preco_venda', f"{res.get('preco_venda', 0.0):.2f}"])
                writer.writerow(['valor_faturamento', f"{res.get('valor_faturamento', 0.0):.2f}"])
                writer.writerow(['valor_lucro', f"{res.get('valor_lucro', 0.0):.2f}"])
                writer.writerow(['margem_percentual', f"{res.get('margem_percentual', 0.0):.2f}"])
                writer.writerow([])
                writer.writerow(['detalhamento', 'valor'])
                for k, v in res.get('breakdown', {}).items():
                    writer.writerow([k, f"{v}"])
            messagebox.showinfo("Exportar CSV", f"Resumo salvo em: {path}")
            # Tenta abrir o arquivo salvo (Windows)
            try:
                if os.name == 'nt':
                    os.startfile(path)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Exportar CSV", f"Erro ao salvar CSV: {e}")

    def select_logo(self):
        """Permite ao usuário selecionar um arquivo de logo para usar nos relatórios."""
        # Require password to change the default logo
        try:
            pwd = simpledialog.askstring('Senha necessária', 'Insira a senha para alterar o logo:', show='*')
        except Exception:
            pwd = None
        DEFAULT_LOGO_PASSWORD = 'wasdeq123'
        if not pwd:
            return
        if pwd != DEFAULT_LOGO_PASSWORD:
            messagebox.showerror('Senha incorreta', 'Senha inválida. A alteração do logo foi cancelada.')
            return
        # password ok -> allow selecting override logo
        path = filedialog.askopenfilename(filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp;*.gif')], title='Selecionar logo')
        if not path:
            return
        self.logo_override_path = path
        messagebox.showinfo('Logo alterado', f'Logo alternativo selecionado: {path}')

    def export_pdf(self):
        """Exporta o último resultado para PDF via diálogo de salvamento (requer reportlab)."""
        if not hasattr(self, 'last_result') or not self.last_result:
            messagebox.showinfo("Exportar PDF", "Nenhum resultado para exportar. Execute um cálculo primeiro.")
            return
        path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF files', '*.pdf')], title='Salvar resumo como PDF')
        if not path:
            return
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except Exception:
            messagebox.showinfo("Exportar PDF", "Para exportar em PDF instale: pip install reportlab")
            return
        try:
            res = self.last_result
            # Determine logo: prefer password-protected override, then initial default, then ./logo.png
            logo_path = getattr(self, 'logo_override_path', None) or getattr(self, 'logo_path', None)
            if not logo_path:
                candidate = os.path.join(os.getcwd(), 'logo.png')
                if os.path.exists(candidate):
                    logo_path = candidate
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
                from reportlab.lib import colors
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            except Exception:
                messagebox.showinfo("Exportar PDF", "Para exportar em PDF instale: pip install reportlab")
                return

            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            # Improve base styles for readability
            styles.add(ParagraphStyle(name='ReportTitle', parent=styles['Title'], fontSize=20, leading=24, spaceAfter=12))
            styles.add(ParagraphStyle(name='ReportSub', parent=styles['Normal'], fontSize=12, leading=14, spaceAfter=8))
            styles.add(ParagraphStyle(name='Metric', parent=styles['Normal'], fontSize=14, leading=16, spaceAfter=6))

            story = []

            # Header with logo (if available) and title
            logo_width = 80
            title = Paragraph('<b>Resumo de Precificação</b>', styles['ReportTitle'])
            header_cells = []
            if logo_path and os.path.exists(logo_path):
                try:
                    # resize logo to fit header
                    img = Image.open(logo_path)
                    aspect = img.height / img.width
                    img_w = logo_width
                    img_h = int(img_w * aspect)
                    img_buf = io.BytesIO()
                    img.resize((img_w, img_h)).save(img_buf, format='PNG')
                    img_buf.seek(0)
                    from reportlab.platypus import Image as RLImage
                    rl_img = RLImage(img_buf, width=img_w, height=img_h)
                    header_cells = [[rl_img, title]]
                except Exception:
                    header_cells = [[Paragraph('', styles['Normal']), title]]
            else:
                header_cells = [[Paragraph('', styles['Normal']), title]]
            header_table = Table(header_cells, colWidths=[logo_width, 420])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 8))

            # Main highlighted metrics box
            preco = f"R$ {res.get('preco_venda', 0.0):.2f}"
            fatur = f"R$ {res.get('valor_faturamento', 0.0):.2f}"
            lucro = f"R$ {res.get('valor_lucro', 0.0):.2f}"
            margem = f"{res.get('margem_percentual', 0.0):.2f}%"
            metrics = [[Paragraph('<b>Preço sugerido</b>', styles['ReportSub']), Paragraph(preco, styles['Metric'])],
                       [Paragraph('<b>Faturamento</b>', styles['ReportSub']), Paragraph(fatur, styles['Metric'])],
                       [Paragraph('<b>Lucro líquido</b>', styles['ReportSub']), Paragraph(lucro, styles['Metric'])],
                       [Paragraph('<b>Margem</b>', styles['ReportSub']), Paragraph(margem, styles['Metric'])]]
            metrics_tbl = Table(metrics, colWidths=[260, 160])
            metrics_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(metrics_tbl)
            story.append(Spacer(1, 12))

            # Breakdown table with alternating row colors and right-aligned values
            bd = [['Quebra', 'Valor']]
            for k, v in res.get('breakdown', {}).items():
                bd.append([str(k), f"R$ {v}"])
            bd_tbl = Table(bd, colWidths=[300, 120])
            bd_style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d2d2d')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ])
            # zebra striping
            for i in range(1, len(bd)):
                if i % 2 == 1:
                    bd_style.add('BACKGROUND', (0,i), (-1,i), colors.whitesmoke)
            bd_tbl.setStyle(bd_style)
            story.append(bd_tbl)

            # Add matplotlib charts: composition and unidades necessárias
            try:
                # composition pie: custos vs lucro (per unit)
                custos = res.get('custos_diretos_por_venda', 0.0) + res.get('taxas_totais_em_reais', 0.0)
                lucro = res.get('valor_lucro', 0.0)
                labels = ['Custos', 'Lucro']
                vals = [max(custos, 0.0), max(lucro, 0.0)]
                fig1, ax1 = plt.subplots(figsize=(4, 3))
                ax1.pie(vals, labels=labels, autopct='%1.1f%%', colors=['#4c72b0', '#dd8452'])
                ax1.set_title('Composição por venda')
                buf1 = io.BytesIO()
                fig1.tight_layout()
                fig1.savefig(buf1, format='png', dpi=150)
                plt.close(fig1)
                buf1.seek(0)
                from reportlab.platypus import Image as RLImage
                story.append(RLImage(buf1, width=360, height=270))

                # unidades necessárias chart
                try:
                    faturamento_meta = float(self.faturamento_var.get() or 0.0)
                    preco_unit = res.get('preco_venda', 0.0)
                    unidades = faturamento_meta / preco_unit if preco_unit > 0 else 0
                    fig2, ax2 = plt.subplots(figsize=(6, 2.5))
                    ax2.bar(['Unidades necessárias'], [unidades], color='#2ca02c')
                    ax2.set_ylabel('Unidades')
                    ax2.set_title('Unidades aproximadas por mês para meta de faturamento')
                    for i, v in enumerate([unidades]):
                        ax2.text(i, v + max(v * 0.01, 1), f"{v:.1f}", ha='center')
                    buf2 = io.BytesIO()
                    fig2.tight_layout()
                    fig2.savefig(buf2, format='png', dpi=150)
                    plt.close(fig2)
                    buf2.seek(0)
                    story.append(Spacer(1, 12))
                    story.append(RLImage(buf2, width=400, height=140))
                except Exception:
                    pass
            except Exception:
                # if matplotlib missing or fails, continue without charts
                pass

            doc.build(story)
            buf.seek(0)
            with open(path, 'wb') as f:
                f.write(buf.read())
            messagebox.showinfo("Exportar PDF", f"Resumo PDF salvo em: {path}")
            # Tenta abrir o PDF salvo (Windows)
            try:
                if os.name == 'nt':
                    os.startfile(path)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Exportar PDF", f"Erro ao gerar PDF: {e}")

    def _toggle_markup_mode(self):
        """Habilita/desabilita campos conforme modo markup/lucro desejado."""
        use_markup = bool(self.use_markup_var.get())
        try:
            if use_markup:
                # habilita markup, desabilita lucro em R$
                self.markup_entry.config(state='normal')
                self.desired_profit_entry.config(state='disabled')
            else:
                self.markup_entry.config(state='disabled')
                self.desired_profit_entry.config(state='normal')
        except Exception:
            pass

    def _on_platform_change(self):
        """Ativa/Desativa opções específicas por plataforma (ex: ML listing type)."""
        try:
            if self.platform_var.get() == 'mercado_livre':
                # permitir seleção do tipo de anúncio
                self.ml_listing_cb.config(state='readonly')
            else:
                self.ml_listing_cb.config(state='disabled')
        except Exception:
            pass

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
    root.geometry("800x800")  # Tamanho inicial
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