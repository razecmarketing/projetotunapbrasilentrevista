import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS
import sqlite3
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from werkzeug.exceptions import BadRequest, NotFound
import traceback
import random
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter, landscape
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
import json

app = Flask(__name__)
CORS(app)

# Database configuration
def get_db_connection():
    conn = sqlite3.connect('tunap.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database tables
def init_db():
    conn = sqlite3.connect('tunap.db')
    conn.row_factory = sqlite3.Row
    
    # Create tables if they don't exist
    conn.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE,
            produto TEXT,
            categoria TEXT,
            regiao TEXT,
            quantidade INTEGER,
            valor REAL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nome TEXT,
            descricao TEXT,
            categoria TEXT,
            unidade_medida TEXT,
            estoque_minimo INTEGER,
            estoque_maximo INTEGER,
            quantidade_atual INTEGER,
            data_cadastro DATE,
            preco_unitario REAL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            tipo TEXT,
            quantidade INTEGER,
            data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            observacao TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Initialize sample data if tables are empty
    if not check_data_exists():
        init_sample_data()

def check_data_exists():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) as count FROM produtos').fetchone()['count']
    conn.close()
    return count > 0

# Add sample data initialization
def init_sample_data():
    conn = get_db_connection()
    
    # Categories and their typical characteristics
    categorias = {
        'limpeza': {
            'prefixos': ['LIM', 'CLN', 'DET'],
            'tipos': ['Limpa Bicos', 'Descarbonizante', 'Limpa TBI', 'Limpa Radiador', 'Limpa Motor',
                     'Desengraxante', 'Limpa Para-brisa', 'Limpa Estofado', 'Limpa Ar Condicionado'],
            'medidas': ['un', 'L', 'ml'],
            'preco_base': (50, 200)
        },
        'lubrificantes': {
            'prefixos': ['LUB', 'OLE', 'GRX'],
            'tipos': ['Óleo Motor', 'Óleo Câmbio', 'Óleo Hidráulico', 'Graxa', 'Lubrificante',
                     'Fluido de Freio', 'Óleo Diferencial', 'Óleo 2T', 'Óleo 4T'],
            'medidas': ['L', 'ml', 'kg'],
            'preco_base': (80, 400)
        },
        'aditivos': {
            'prefixos': ['ADT', 'ADV', 'BOO'],
            'tipos': ['Aditivo Motor', 'Aditivo Combustível', 'Aditivo Radiador', 'Aditivo Óleo',
                     'Aditivo Arrefecimento', 'Octanagem', 'Condicionador'],
            'medidas': ['ml', 'L', 'un'],
            'preco_base': (30, 150)
        },
        'ferramentas': {
            'prefixos': ['FER', 'TOL', 'EQP'],
            'tipos': ['Chave', 'Alicate', 'Scanner', 'Medidor', 'Teste', 'Kit Reparo',
                     'Equipamento Diagnóstico', 'Ferramenta Especial'],
            'medidas': ['un', 'kit', 'pç'],
            'preco_base': (100, 2000)
        },
        'quimicos': {
            'prefixos': ['QUI', 'CHM', 'SOL'],
            'tipos': ['Solvente', 'Removedor', 'Anticorrosivo', 'Selante', 'Vedante',
                     'Cola', 'Trava Química', 'Silicone'],
            'medidas': ['ml', 'L', 'g', 'kg'],
            'preco_base': (40, 180)
        }
    }

    # Specifications and their variations
    especificacoes = {
        'viscosidades': ['5W30', '5W40', '10W40', '15W40', '20W50'],
        'volumes': ['100ml', '250ml', '500ml', '1L', '5L', '20L'],
        'qualidades': ['Premium', 'Profissional', 'Standard', 'Ultra', 'Max'],
        'aplicacoes': ['Diesel', 'Gasolina', 'Flex', 'Universal', 'Sintético', 'Mineral']
    }

    # Generate 10,000 unique products
    produtos = []
    codigos_usados = set()
    
    for i in range(10000):
        # Select random category and its properties
        categoria = random.choice(list(categorias.keys()))
        cat_props = categorias[categoria]
        
        # Generate unique product code
        while True:
            prefixo = random.choice(cat_props['prefixos'])
            numero = str(random.randint(1000, 9999))
            codigo = f"{prefixo}{numero}"
            if codigo not in codigos_usados:
                codigos_usados.add(codigo)
                break
        
        # Generate product name and description
        tipo = random.choice(cat_props['tipos'])
        specs = []
        if categoria in ['lubrificantes', 'aditivos']:
            specs.append(random.choice(especificacoes['viscosidades']))
        specs.append(random.choice(especificacoes['volumes']))
        specs.append(random.choice(especificacoes['qualidades']))
        specs.append(random.choice(especificacoes['aplicacoes']))
        
        nome = f"{tipo} {' '.join(specs[:2])}"
        descricao = f"{tipo} {' '.join(specs)} para aplicação em veículos {specs[-1]}"
        
        # Generate stock levels
        preco_min, preco_max = cat_props['preco_base']
        estoque_max = random.randint(100, 1000)
        estoque_min = int(estoque_max * 0.2)
        quantidade_atual = random.randint(
            int(estoque_min * 0.5),
            int(estoque_max * 1.2)
        )
        
        # Add to products list
        produtos.append((
            codigo,
            nome,
            descricao,
            categoria,
            random.choice(cat_props['medidas']),
            estoque_min,
            estoque_max,
            quantidade_atual,
            datetime.now().date(),
            random.uniform(preco_min, preco_max)
        ))
    
    # Batch insert products
    try:
        conn.executemany('''
            INSERT INTO produtos (
                codigo, nome, descricao, categoria, 
                unidade_medida, estoque_minimo, estoque_maximo, 
                quantidade_atual, data_cadastro, preco_unitario
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', produtos)
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Error inserting products: {e}")
    
    # Generate realistic sales data with the new products
    regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
    
    # Generate sales for each product
    vendas = []
    for ano in [2022, 2023, 2024]:
        for mes in range(1, 13):
            # Seasonal factors
            seasonal_factor = 1.0
            if mes in [12, 1, 2]:  # Summer in Brazil
                seasonal_factor = 1.3
            elif mes in [6, 7, 8]:  # Winter
                seasonal_factor = 0.8
            
            # Generate multiple sales entries per month
            for _ in range(random.randint(500, 1000)):
                produto = random.choice(produtos)
                regiao = random.choice(regioes)
                
                # Regional factors
                regional_factor = {
                    'Sudeste': 1.4,
                    'Sul': 1.2,
                    'Nordeste': 1.0,
                    'Centro-Oeste': 0.9,
                    'Norte': 0.8
                }[regiao]
                
                data = datetime(ano, mes, random.randint(1, 28)).date()
                base_valor = random.uniform(
                    categorias[produto[3]]['preco_base'][0],
                    categorias[produto[3]]['preco_base'][1]
                )
                quantidade = int(random.uniform(1, 50) * seasonal_factor)
                valor = base_valor * quantidade * seasonal_factor * regional_factor
                
                vendas.append((
                    data,
                    produto[0],  # código do produto
                    produto[3],  # categoria
                    regiao,
                    quantidade,
                    valor
                ))
    
    # Batch insert sales
    try:
        conn.executemany('''
            INSERT INTO vendas (
                data, produto, categoria, regiao, 
                quantidade, valor
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', vendas)
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Error inserting sales: {e}")
    
    conn.close()

def getStockStatus(atual, minimo, maximo):
    if atual <= minimo:
        return 'BAIXO'
    elif atual >= maximo:
        return 'ALTO'
    return 'NORMAL'

# Rotas da API
@app.route('/api/vendas', methods=['GET'])
def get_vendas():
    try:
        periodo = request.args.get('periodo', 'all')
        regiao = request.args.get('regiao', 'all')
        categoria = request.args.get('categoria', 'all')
        
        conn = get_db_connection()
        query = 'SELECT * FROM vendas WHERE 1=1'
        
        if periodo != 'all':
            query += f" AND strftime('%Y', data) = '{periodo}'"
        if regiao != 'all':
            query += f" AND regiao = '{regiao}'"
        if categoria != 'all':
            query += f" AND categoria = '{categoria}'"
            
        vendas = conn.execute(query).fetchall()
        conn.close()
        
        return jsonify([dict(venda) for venda in vendas])
    
    except Exception as e:
        raise e

@app.route('/api/metricas', methods=['GET'])
def get_metricas():
    try:
        conn = get_db_connection()
        
        # Receita total
        receita_total = conn.execute('''
            SELECT SUM(valor) as total
            FROM vendas
        ''').fetchone()['total']
        
        # Crescimento YoY
        ano_atual = datetime.now().year
        vendas_atual = conn.execute(f'''
            SELECT SUM(valor) as total
            FROM vendas
            WHERE strftime('%Y', data) = '{ano_atual}'
        ''').fetchone()['total']
        
        vendas_anterior = conn.execute(f'''
            SELECT SUM(valor) as total
            FROM vendas
            WHERE strftime('%Y', data) = '{ano_atual - 1}'
        ''').fetchone()['total']
        
        crescimento = ((vendas_atual - vendas_anterior) / vendas_anterior) * 100 if vendas_anterior else 0
        
        # Ticket médio
        ticket_medio = conn.execute('''
            SELECT AVG(valor/quantidade) as media
            FROM vendas
        ''').fetchone()['media']
        
        conn.close()
        
        return jsonify({
            'receita_total': receita_total,
            'crescimento': crescimento,
            'ticket_medio': ticket_medio
        })
    
    except Exception as e:
        raise e

@app.route('/api/previsao', methods=['GET'])
def get_previsao():
    try:
        conn = get_db_connection()
        
        # Obter dados históricos
        dados = pd.read_sql_query('''
            SELECT data, SUM(valor) as valor
            FROM vendas
            GROUP BY data
            ORDER BY data
        ''', conn)
        
        conn.close()
        
        # Preparar dados para previsão
        dados['data'] = pd.to_datetime(dados['data'])
        X = (dados['data'] - dados['data'].min()).dt.days.values.reshape(-1, 1)
        y = dados['valor'].values
        
        # Treinar modelo
        model = LinearRegression()
        model.fit(X, y)
        
        # Fazer previsão para próximos 30 dias
        ultimo_dia = dados['data'].max()
        dias_previsao = pd.date_range(start=ultimo_dia + timedelta(days=1), periods=30)
        X_prev = (dias_previsao - dados['data'].min()).days.values.reshape(-1, 1)
        
        previsoes = model.predict(X_prev)
        
        return jsonify({
            'datas': dias_previsao.strftime('%Y-%m-%d').tolist(),
            'previsoes': previsoes.tolist()
        })
    
    except Exception as e:
        raise e

@app.route('/api/exportar', methods=['GET'])
def exportar_relatorio():
    try:
        periodo = request.args.get('periodo', 'all')
        regiao = request.args.get('regiao', 'all')
        categoria = request.args.get('categoria', 'all')
        
        conn = get_db_connection()
        query = 'SELECT * FROM vendas WHERE 1=1'
        
        if periodo != 'all':
            query += f" AND strftime('%Y', data) = '{periodo}'"
        if regiao != 'all':
            query += f" AND regiao = '{regiao}'"
        if categoria != 'all':
            query += f" AND categoria = '{categoria}'"
            
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Vendas')
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='relatorio_vendas.xlsx'
        )
    
    except Exception as e:
        print(f"Error exporting report: {str(e)}")
        return jsonify({'error': 'Erro ao gerar relatório'}), 500

# New inventory routes
@app.route('/api/produtos', methods=['GET', 'POST'])
def produtos():
    try:
        conn = get_db_connection()
        
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                raise BadRequest('Dados JSON inválidos')
            
            required_fields = ['codigo', 'nome', 'categoria', 'unidade_medida',
                             'estoque_minimo', 'estoque_maximo', 'quantidade_inicial', 'preco_unitario']
            
            for field in required_fields:
                if field not in data:
                    raise BadRequest(f'Campo obrigatório ausente: {field}')
            
            try:
                conn.execute('''
                    INSERT INTO produtos (codigo, nome, descricao, categoria, 
                                        unidade_medida, estoque_minimo, estoque_maximo, 
                                        quantidade_atual, data_cadastro, preco_unitario)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['codigo'], data['nome'], data.get('descricao', ''),
                    data['categoria'], data['unidade_medida'],
                    int(data['estoque_minimo']), int(data['estoque_maximo']),
                    int(data['quantidade_inicial']), datetime.now().date(),
                    float(data['preco_unitario'])
                ))
                conn.commit()
                return jsonify({'message': 'Produto cadastrado com sucesso'})
            except sqlite3.IntegrityError:
                raise BadRequest('Código de produto já existe')
        
        produtos = conn.execute('SELECT * FROM produtos').fetchall()
        return jsonify([dict(produto) for produto in produtos])
    
    except Exception as e:
        raise e
    finally:
        conn.close()

@app.route('/api/movimentacao', methods=['POST'])
def registrar_movimentacao():
    try:
        conn = get_db_connection()
        data = request.get_json()
        
        if not data:
            raise BadRequest('Dados JSON inválidos')
        
        required_fields = ['produto_id', 'tipo', 'quantidade']
        
        for field in required_fields:
            if field not in data:
                raise BadRequest(f'Campo obrigatório ausente: {field}')
        
        # Verificar estoque atual
        produto = conn.execute('SELECT quantidade_atual FROM produtos WHERE id = ?',
                             (data['produto_id'],)).fetchone()
        
        if not produto:
            raise NotFound('Produto não encontrado')
        
        nova_quantidade = produto['quantidade_atual']
        if data['tipo'] == 'entrada':
            nova_quantidade += data['quantidade']
        else:
            nova_quantidade -= data['quantidade']
            if nova_quantidade < 0:
                raise BadRequest('Estoque insuficiente')
        
        # Registrar movimentação
        conn.execute('''
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, 
                                     data_movimentacao, observacao)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['produto_id'], data['tipo'], data['quantidade'],
            datetime.now().date(), data.get('observacao', '')
        ))
        
        # Atualizar estoque
        conn.execute('''
            UPDATE produtos 
            SET quantidade_atual = ?
            WHERE id = ?
        ''', (nova_quantidade, data['produto_id']))
        
        conn.commit()
        return jsonify({'message': 'Movimentação registrada com sucesso'})
    
    except Exception as e:
        raise e
    finally:
        conn.close()

@app.route('/api/relatorio/estoque', methods=['GET'])
def relatorio_estoque():
    try:
        formato = request.args.get('formato', 'pdf')
        conn = get_db_connection()
        
        produtos = pd.read_sql_query('''
            SELECT p.*, 
                   (SELECT COUNT(*) FROM movimentacoes m WHERE m.produto_id = p.id) as total_movimentacoes
            FROM produtos p
        ''', conn)
        
        if formato == 'excel':
            output = io.BytesIO()
            produtos.to_excel(output, index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='relatorio_estoque.xlsx'
            )
        else:
            # Gerar PDF
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            y = 750
            
            p.drawString(50, y, "Relatório de Estoque - TUNAP Brasil")
            y -= 30
            
            for _, produto in produtos.iterrows():
                p.drawString(50, y, f"Código: {produto['codigo']}")
                p.drawString(200, y, f"Nome: {produto['nome']}")
                p.drawString(400, y, f"Qtd: {produto['quantidade_atual']}")
                y -= 20
            
            p.save()
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='relatorio_estoque.pdf'
            )
    
    except Exception as e:
        raise e
    finally:
        conn.close()

@app.route('/api/produtos/search', methods=['GET'])
def search_produtos():
    try:
        search = request.args.get('search', '').lower()
        categoria = request.args.get('categoria', '')
        status = request.args.get('status', '')
        
        conn = get_db_connection()
        query = '''
            SELECT p.*, 
                   (SELECT MAX(data_movimentacao) 
                    FROM movimentacoes m 
                    WHERE m.produto_id = p.id) as ultima_movimentacao
            FROM produtos p 
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += ''' AND (
                LOWER(p.codigo) LIKE ? OR 
                LOWER(p.nome) LIKE ? OR 
                LOWER(p.descricao) LIKE ?
            )'''
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
            
        if categoria:
            query += ' AND p.categoria = ?'
            params.append(categoria)
            
        produtos = [dict(p) for p in conn.execute(query, params).fetchall()]
        
        if status:
            produtos = [p for p in produtos if getStockStatus(
                p['quantidade_atual'], 
                p['estoque_minimo'], 
                p['estoque_maximo']
            ).lower() == status.lower()]
        
        return jsonify(produtos)
    
    except Exception as e:
        print(f"Error in search_produtos: {str(e)}")
        return jsonify({'error': 'Erro ao buscar produtos'}), 500
    finally:
        conn.close()

def generate_sample_data_for_year(year):
    produtos_base = [
        ('TUN001', 'Limpa Bicos Injeção', 'Limpador profissional', 'limpeza', 'un', 50, 200, random.randint(100, 300)),
        ('TUN002', 'Óleo Motor Sintético', 'Óleo 5W30', 'lubrificantes', 'L', 100, 500, random.randint(200, 600)),
        ('TUN003', 'Aditivo Radiador', 'Concentrado', 'aditivos', 'L', 80, 300, random.randint(150, 400)),
        # ... add more sample products ...
    ]
    
    data = []
    for produto in produtos_base:
        # Add seasonal variations
        for month in range(1, 13):
            seasonal_factor = 1.0
            if month in [12, 1, 2]:  # Summer
                seasonal_factor = 1.3
            elif month in [6, 7, 8]:  # Winter
                seasonal_factor = 0.8
                
            quantidade = int(produto[7] * seasonal_factor)
            row = list(produto[:-1])  # Exclude the last random quantity
            row.append(quantidade)
            row.append(f"{year}-{month:02d}-01")
            data.append(row)
    
    return data

@app.route('/api/export/report', methods=['GET'])
def export_report():
    try:
        formato = request.args.get('format', 'pdf')
        ano = request.args.get('year', '2023')
        
        if formato == 'excel':
            # Generate Excel report
            output = BytesIO()
            data = generate_sample_data_for_year(int(ano))
            df = pd.DataFrame(data, columns=[
                'Código', 'Nome', 'Descrição', 'Categoria', 'Unidade',
                'Estoque Min', 'Estoque Max', 'Quantidade', 'Data'
            ])
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Estoque', index=False)
                
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'relatorio_estoque_{ano}.xlsx'
            )
        else:
            # Generate PDF report
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(letter),
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Prepare data
            data = generate_sample_data_for_year(int(ano))
            df = pd.DataFrame(data, columns=[
                'Código', 'Nome', 'Descrição', 'Categoria', 'Unidade',
                'Estoque Min', 'Estoque Max', 'Quantidade', 'Data'
            ])

            # Create story elements
            elements = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )

            # Add title
            elements.append(Paragraph(f"Relatório de Estoque {ano}", title_style))
            elements.append(Spacer(1, 20))

            # Add summary statistics
            summary_data = [
                ['Total de Produtos:', len(df['Código'].unique())],
                ['Valor Total em Estoque:', f'R$ {(df["Quantidade"].sum() * 100).:,.2f}'],
                ['Média de Estoque:', f'{df["Quantidade"].mean():.0f} unidades']
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 20))

            # Generate and add graphs
            plt.figure(figsize=(10, 5))
            df.groupby('Categoria')['Quantidade'].sum().plot(kind='bar')
            plt.title('Quantidade por Categoria')
            img_stream = BytesIO()
            plt.savefig(img_stream, format='png')
            img_stream.seek(0)
            elements.append(Image(img_stream))
            elements.append(Spacer(1, 20))

            # Add main data table
            table_data = [df.columns.tolist()] + df.values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black)
            ]))
            elements.append(table)

            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'relatorio_estoque_{ano}.pdf'
            )

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return jsonify({'error': 'Erro ao gerar relatório'}), 500

def generate_comprehensive_financial_data(year):
    """Generate realistic financial data for the given year."""
    months = range(1, 13)
    data = []
    
    base_revenue = 1000000  # Base monthly revenue
    growth_rate = 1.15  # 15% annual growth
    
    # Product categories and their typical profit margins
    categories = {
        'limpeza': {'margin': 0.35, 'weight': 0.4},
        'lubrificantes': {'margin': 0.45, 'weight': 0.35},
        'aditivos': {'margin': 0.50, 'weight': 0.25}
    }
    
    for month in months:
        # Apply seasonal and yearly growth factors
        seasonal_factor = 1.0
        if month in [12, 1, 2]:  # Summer in Brazil
            seasonal_factor = 1.3
        elif month in [6, 7, 8]:  # Winter
            seasonal_factor = 0.8
        
        yearly_factor = growth_rate ** (int(year) - 2023)
        
        # Calculate monthly revenue with variations
        monthly_revenue = base_revenue * seasonal_factor * yearly_factor
        
        # Add random variation (+/- 10%)
        monthly_revenue *= random.uniform(0.9, 1.1)
        
        # Split revenue by categories
        category_data = []
        for cat, props in categories.items():
            cat_revenue = monthly_revenue * props['weight']
            cat_profit = cat_revenue * props['margin']
            category_data.append({
                'categoria': cat,
                'receita': cat_revenue,
                'lucro': cat_profit,
                'margem': props['margin']
            })
        
        data.append({
            'mes': f"{year}-{month:02d}",
            'receita_total': monthly_revenue,
            'categorias': category_data
        })
    
    return data

@app.route('/api/comprehensive-report', methods=['GET'])
def comprehensive_report():
    try:
        year = request.args.get('year', '2024')
        format = request.args.get('format', 'pdf')
        
        # Generate financial data
        financial_data = generate_comprehensive_financial_data(year)
        
        if format == 'pdf':
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(letter),
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )
            elements.append(Paragraph(f"Relatório Anual TUNAP Brasil {year}", title_style))
            elements.append(Spacer(1, 20))
            
            # Summary Statistics
            total_revenue = sum(month['receita_total'] for month in financial_data)
            total_profit = sum(
                sum(cat['lucro'] for cat in month['categorias'])
                for month in financial_data
            )
            
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20
            )
            
            elements.append(Paragraph(f"Receita Total: R$ {total_revenue:,.2f}", summary_style))
            elements.append(Paragraph(f"Lucro Total: R$ {total_profit:,.2f}", summary_style))
            elements.append(Paragraph(f"Margem Média: {(total_profit/total_revenue)*100:.1f}%", summary_style))
            elements.append(Spacer(1, 20))
            
            # Monthly Revenue Chart
            drawing = Drawing(400, 200)
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 125
            bc.width = 300
            bc.data = [[month['receita_total']/1000000 for month in financial_data]]
            bc.categoryAxis.categoryNames = [month['mes'] for month in financial_data]
            bc.valueAxis.valueMin = 0
            bc.valueAxis.valueMax = max(month['receita_total'] for month in financial_data)/1000000 * 1.1
            drawing.add(bc)
            elements.append(drawing)
            elements.append(Spacer(1, 20))
            
            # Category Performance Table
            cat_data = [['Categoria', 'Receita Total', 'Lucro Total', 'Margem Média']]
            for categoria in ['limpeza', 'lubrificantes', 'aditivos']:
                cat_revenue = sum(
                    sum(cat['receita'] for cat in month['categorias'] if cat['categoria'] == categoria)
                    for month in financial_data
                )
                cat_profit = sum(
                    sum(cat['lucro'] for cat in month['categorias'] if cat['categoria'] == categoria)
                    for month in financial_data
                )
                cat_data.append([
                    categoria.title(),
                    f"R$ {cat_revenue:,.2f}",
                    f"R$ {cat_profit:,.2f}",
                    f"{(cat_profit/cat_revenue)*100:.1f}%"
                ])
            
            t = Table(cat_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)

            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'relatorio_completo_tunap_{year}.pdf'
            )
            
        else:  # Excel format
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Monthly summary
                monthly_df = pd.DataFrame([{
                    'Mês': month['mes'],
                    'Receita Total': month['receita_total'],
                    'Lucro Total': sum(cat['lucro'] for cat in month['categorias'])
                } for month in financial_data])
                monthly_df.to_excel(writer, sheet_name='Resumo Mensal', index=False)
                
                # Category performance
                cat_data = []
                for month in financial_data:
                    for cat in month['categorias']:
                        cat_data.append({
                            'Mês': month['mes'],
                            'Categoria': cat['categoria'],
                            'Receita': cat['receita'],
                            'Lucro': cat['lucro'],
                            'Margem': cat['margem']
                        })
                cat_df = pd.DataFrame(cat_data)
                cat_df.to_excel(writer, sheet_name='Desempenho Categorias', index=False)
            
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'relatorio_completo_tunap_{year}.xlsx'
            )
            
    except Exception as e:
        print(f"Error generating comprehensive report: {str(e)}")
        return jsonify({'error': 'Erro ao gerar relatório'}), 500

@app.errorhandler(Exception)
def handle_error(error):
    print(traceback.format_exc())  # Log the full error
    
    if isinstance(error, BadRequest):
        return jsonify({'error': 'Dados inválidos'}), 400
    elif isinstance(error, NotFound):
        return jsonify({'error': 'Recurso não encontrado'}), 404
    
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)