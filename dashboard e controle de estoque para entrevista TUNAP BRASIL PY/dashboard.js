// Configuração inicial
const config = {
  responsive: true,
  displayModeBar: false
};

// Dados simulados para demonstração
const dadosSimulados = {
  vendas: [
    { mes: 'Jan', valor: 150000 },
    { mes: 'Fev', valor: 180000 },
    { mes: 'Mar', valor: 220000 },
    { mes: 'Abr', valor: 190000 },
    { mes: 'Mai', valor: 250000 },
    { mes: 'Jun', valor: 280000 },
    { mes: 'Jul', valor: 310000 },
    { mes: 'Ago', valor: 290000 },
    { mes: 'Set', valor: 320000 },
    { mes: 'Out', valor: 350000 },
    { mes: 'Nov', valor: 380000 },
    { mes: 'Dez', valor: 420000 }
  ],
  produtos: [
    { nome: 'Limpa Bicos Injeção', vendas: 1200 },
    { nome: 'Óleo Motor Sintético 5W30', vendas: 950 },
    { nome: 'Aditivo Radiador Concentrado', vendas: 800 },
    { nome: 'Limpa TBI Profissional', vendas: 750 },
    { nome: 'Descarbonizante Motor', vendas: 600 },
    { nome: 'Limpa Ar Condicionado', vendas: 580 },
    { nome: 'Pasta Multiuso', vendas: 520 },
    { nome: 'Fluido de Freio DOT4', vendas: 490 }
  ]
};

// Dados simulados para demonstração de níveis de estoque
const dadosEstoqueInicial = {
  produtos: [
    { codigo: 'LIM4521', nome: 'Limpa Bicos Injeção Pro', quantidade_atual: 245, estoque_minimo: 50 },
    { codigo: 'OLE3892', nome: 'Óleo Motor Sintético 5W30', quantidade_atual: 178, estoque_minimo: 100 },
    { codigo: 'ADT7823', nome: 'Aditivo Radiador Concentrado', quantidade_atual: 42, estoque_minimo: 60 },
    { codigo: 'LIM9234', nome: 'Limpa TBI Profissional', quantidade_atual: 156, estoque_minimo: 40 },
    { codigo: 'DES5612', nome: 'Descarbonizante Motor', quantidade_atual: 89, estoque_minimo: 45 },
    { codigo: 'LAC4389', nome: 'Limpa Ar Condicionado', quantidade_atual: 234, estoque_minimo: 70 },
    { codigo: 'PAS7812', nome: 'Pasta Multiuso', quantidade_atual: 67, estoque_minimo: 30 },
    { codigo: 'FLU2345', nome: 'Fluido de Freio DOT4', quantidade_atual: 112, estoque_minimo: 50 }
  ]
};

// Funções de renderização dos gráficos
function renderizarVendasTotais() {
  const trace = {
    x: dadosSimulados.vendas.map(d => d.mes),
    y: dadosSimulados.vendas.map(d => d.valor),
    type: 'bar',
    marker: {
      color: '#0066cc'
    }
  };

  const layout = {
    margin: { t: 20, r: 20, l: 40, b: 40 },
    yaxis: {
      title: 'Valor (R$)',
      tickformat: ',.0f'
    }
  };

  Plotly.newPlot('vendasTotais', [trace], layout, config);
}

function renderizarProdutosMaisVendidos() {
  const trace = {
    x: dadosSimulados.produtos.map(p => p.vendas),
    y: dadosSimulados.produtos.map(p => p.nome),
    type: 'bar',
    orientation: 'h',
    marker: {
      color: '#004d99'
    }
  };

  const layout = {
    margin: { t: 20, r: 20, l: 120, b: 40 },
    xaxis: {
      title: 'Quantidade Vendida'
    }
  };

  Plotly.newPlot('produtosMaisVendidos', [trace], layout, config);
}

function renderizarMapaCalor() {
  const regioes = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];
  const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
  
  const data = {
    z: Array(5).fill().map(() => Array(6).fill().map(() => Math.random() * 100000)),
    x: meses,
    y: regioes,
    type: 'heatmap',
    colorscale: 'Blues'
  };

  const layout = {
    margin: { t: 20, r: 20, l: 100, b: 40 }
  };

  Plotly.newPlot('mapaCalor', [data], layout, config);
}

function renderizarTendencias() {
  const trace = {
    x: dadosSimulados.vendas.map(d => d.mes),
    y: dadosSimulados.vendas.map(d => d.valor),
    type: 'scatter',
    mode: 'lines+markers',
    line: {
      color: '#0066cc'
    }
  };

  const layout = {
    margin: { t: 20, r: 20, l: 40, b: 40 },
    yaxis: {
      title: 'Valor (R$)',
      tickformat: ',.0f'
    }
  };

  Plotly.newPlot('tendencias', [trace], layout, config);
}

function atualizarMetricas() {
  const receitaTotal = dadosSimulados.vendas.reduce((acc, curr) => acc + curr.valor, 0);
  const crescimento = 15.7; // Valor simulado
  const ticketMedio = receitaTotal / (dadosSimulados.vendas.length * 100); // Valor simulado

  document.getElementById('receitaTotal').textContent = 
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
      .format(receitaTotal);
  
  document.getElementById('crescimento').textContent = 
    `${crescimento.toFixed(1)}%`;
  
  document.getElementById('ticketMedio').textContent = 
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
      .format(ticketMedio);
}

// Função para renderizar tabela de produtos com dados iniciais
function renderizarTabelaProdutosInicial() {
  const tabela = document.getElementById('tabelaProdutos');
  if (!tabela) return;

  tabela.innerHTML = dadosEstoqueInicial.produtos.map(p => `
    <tr class="${p.quantidade_atual <= p.estoque_minimo ? 'estoque-baixo' : ''}">
      <td>${p.codigo}</td>
      <td>${p.nome}</td>
      <td>${p.quantidade_atual}</td>
      <td>${p.estoque_minimo}</td>
      <td>
        <button class="btn-movimento btn-entrada" onclick="registrarMovimentacao('${p.codigo}', 'entrada')">+</button>
        <button class="btn-movimento btn-saida" onclick="registrarMovimentacao('${p.codigo}', 'saida')">-</button>
      </td>
    </tr>
  `).join('');
}

// Função para renderizar gráfico de estoque inicial
function renderizarGraficoEstoqueInicial() {
  const trace = {
    x: dadosEstoqueInicial.produtos.map(p => p.nome),
    y: dadosEstoqueInicial.produtos.map(p => p.quantidade_atual),
    type: 'bar',
    marker: {
      color: dadosEstoqueInicial.produtos.map(p => 
        p.quantidade_atual <= p.estoque_minimo ? '#ff4444' : '#0066cc'
      )
    }
  };

  const layout = {
    title: 'Níveis de Estoque',
    margin: { t: 30, r: 20, l: 40, b: 90 },
    xaxis: {
      tickangle: -45
    }
  };

  Plotly.newPlot('graficoEstoque', [trace], layout, config);
}

// Update form submission handler
function cadastrarProduto(event) {
  event.preventDefault();
  
  const formData = new FormData(event.target);
  const produto = {
    codigo: formData.get('codigo'),
    nome: formData.get('nome'),
    descricao: formData.get('descricao'),
    categoria: formData.get('categoria'),
    unidade_medida: formData.get('unidade_medida'),
    estoque_minimo: parseInt(formData.get('estoque_minimo')),
    estoque_maximo: parseInt(formData.get('estoque_maximo')),
    quantidade_inicial: parseInt(formData.get('quantidade_inicial'))
  };

  // Validate required fields
  const requiredFields = ['codigo', 'nome', 'categoria', 'unidade_medida', 
                         'estoque_minimo', 'estoque_maximo', 'quantidade_inicial'];
  
  for (const field of requiredFields) {
    if (!produto[field]) {
      alert(`Campo ${field} é obrigatório`);
      return;
    }
  }

  fetch('/api/produtos', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(produto)
  })
  .then(response => response.json())
  .then(result => {
    if (result.error) {
      throw new Error(result.error);
    }
    alert('Produto cadastrado com sucesso!');
    document.getElementById('formProduto').style.display = 'none';
    event.target.reset();
    renderizarTabelaProdutosInicial();
    renderizarGraficoEstoqueInicial();
  })
  .catch(error => {
    console.error('Error:', error);
    alert(error.message || 'Ocorreu um erro ao cadastrar o produto');
  });
}

// Função para exportar relatório
function exportarRelatorio() {
  const formato = document.getElementById('formatoExport').value;
  const ano = document.getElementById('anoRelatorio').value || '2023';
  
  fetch(`/api/export/report?format=${formato}&year=${ano}`)
    .then(response => {
      if (!response.ok) throw new Error('Erro ao gerar relatório');
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `relatorio_estoque_${ano}.${formato}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Erro ao gerar relatório. Por favor, tente novamente.');
    });
}

// Update registrarMovimentacao function to work with the initial data
function registrarMovimentacao(codigo, tipo) {
  const quantidade = parseInt(prompt(`Quantidade para ${tipo}:`));
  if (!quantidade || isNaN(quantidade)) {
    alert('Por favor, insira uma quantidade válida.');
    return;
  }

  // Find the product in the initial data
  const produto = dadosEstoqueInicial.produtos.find(p => p.codigo === codigo);
  if (!produto) {
    alert('Produto não encontrado.');
    return;
  }

  // Update quantity
  if (tipo === 'entrada') {
    produto.quantidade_atual += quantidade;
  } else {
    if (produto.quantidade_atual - quantidade < 0) {
      alert('Estoque insuficiente para esta saída.');
      return;
    }
    produto.quantidade_atual -= quantidade;
  }

  // Re-render the table and graph
  renderizarTabelaProdutosInicial();
  renderizarGraficoEstoqueInicial();
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  renderizarVendasTotais();
  renderizarProdutosMaisVendidos();
  renderizarMapaCalor();
  renderizarTendencias();
  atualizarMetricas();

  renderizarTabelaProdutosInicial();
  renderizarGraficoEstoqueInicial();

  // Adicionar listeners para filtros
  const filtros = ['periodoFilter', 'regiaoFilter', 'categoriaFilter'];
  filtros.forEach(filtro => {
    document.getElementById(filtro).addEventListener('change', () => {
      // Aqui seria implementada a lógica de filtro real
      renderizarVendasTotais();
      renderizarProdutosMaisVendidos();
      renderizarMapaCalor();
      renderizarTendencias();
      atualizarMetricas();
    });
  });

  // Listener para botão de exportação
  document.getElementById('exportBtn').addEventListener('click', exportarRelatorio);

  // Adicionar listeners para novos botões
  document.getElementById('cadastrarProduto').addEventListener('click', () => {
    const formProduto = document.getElementById('formProduto');
    formProduto.style.display = formProduto.style.display === 'none' ? 'block' : 'none';
  });
  
  document.getElementById('exportarEstoque').addEventListener('click', () => {
    const formato = document.getElementById('formatoExport').value;
    window.location.href = `/api/relatorio/estoque?formato=${formato}`;
  });

  // Update form listener to use named form fields
  const formProduto = document.getElementById('formProduto');
  formProduto.innerHTML = `
    <form onsubmit="cadastrarProduto(event)">
      <input type="text" name="codigo" placeholder="Código" required>
      <input type="text" name="nome" placeholder="Nome" required>
      <input type="text" name="descricao" placeholder="Descrição">
      <select name="categoria" required>
        <option value="">Selecione a categoria</option>
        <option value="limpeza">Limpeza</option>
        <option value="lubrificantes">Lubrificantes</option>
        <option value="aditivos">Aditivos</option>
      </select>
      <input type="text" name="unidade_medida" placeholder="Unidade de Medida" required>
      <input type="number" name="estoque_minimo" placeholder="Estoque Mínimo" required>
      <input type="number" name="estoque_maximo" placeholder="Estoque Máximo" required>
      <input type="number" name="quantidade_inicial" placeholder="Quantidade Inicial" required>
      <button type="submit">Salvar</button>
    </form>
  `;

  document.getElementById('formProduto').addEventListener('submit', cadastrarProduto);
});

// Update the admin view functionality
function toggleAdminView() {
  const adminView = document.getElementById('adminView');
  adminView.style.display = adminView.style.display === 'none' ? 'block' : 'none';
  if (adminView.style.display === 'block') {
    loadAdminInventory();
  }
}

function loadAdminInventory() {
  fetch('/api/produtos')
    .then(response => {
      if (!response.ok) throw new Error('Network response was not ok');
      return response.json();
    })
    .then(produtos => {
      const adminList = document.getElementById('adminProductList');
      adminList.innerHTML = produtos.map(p => {
        const status = getStockStatus(p.quantidade_atual, p.estoque_minimo, p.estoque_maximo);
        return `
          <tr>
            <td>${p.codigo}</td>
            <td>${p.nome}</td>
            <td>${p.categoria}</td>
            <td>${p.quantidade_atual}</td>
            <td>${p.estoque_minimo}</td>
            <td>${p.estoque_maximo}</td>
            <td class="status-${status.toLowerCase()}">${status}</td>
            <td>${formatDate(p.data_cadastro)}</td>
          </tr>
        `;
      }).join('');
    })
    .catch(error => {
      console.error('Error loading inventory:', error);
      alert('Erro ao carregar o inventário. Por favor, tente novamente.');
    });
}

function getStockStatus(atual, minimo, maximo) {
  if (atual <= minimo) return 'BAIXO';
  if (atual >= maximo) return 'ALTO';
  return 'NORMAL';
}

function formatDate(date) {
  return new Date(date).toLocaleDateString('pt-BR');
}

function setupAdminFilters() {
  const searchInput = document.getElementById('searchProduct');
  const categoryFilter = document.getElementById('filterCategory');
  const stockFilter = document.getElementById('stockStatus');

  function filterProducts() {
    const params = new URLSearchParams();
    if (searchInput.value) params.append('search', searchInput.value);
    if (categoryFilter.value) params.append('categoria', categoryFilter.value);
    if (stockFilter.value) params.append('status', stockFilter.value);
    
    fetch(`/api/produtos/search?${params.toString()}`)
      .then(response => response.json())
      .then(produtos => {
        const adminList = document.getElementById('adminProductList');
        adminList.innerHTML = produtos.map(p => {
          const status = getStockStatus(p.quantidade_atual, p.estoque_minimo, p.estoque_maximo);
          return `
            <tr>
              <td>${p.codigo}</td>
              <td>${p.nome}</td>
              <td>${p.categoria}</td>
              <td>${p.quantidade_atual}</td>
              <td>${p.estoque_minimo}</td>
              <td>${p.estoque_maximo}</td>
              <td class="status-${status.toLowerCase()}">${status}</td>
              <td>${formatDate(p.data_cadastro)}</td>
            </tr>
          `;
        }).join('');
      })
      .catch(error => {
        console.error('Error filtering products:', error);
        alert('Erro ao filtrar produtos');
      });
  }

  searchInput.addEventListener('input', debounce(filterProducts, 300));
  categoryFilter.addEventListener('change', filterProducts);
  stockFilter.addEventListener('change', filterProducts);
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Update the event listeners
document.addEventListener('DOMContentLoaded', () => {
  // ... existing event listeners ...

  // Setup admin view functionality
  document.getElementById('toggleAdminView').addEventListener('click', toggleAdminView);
  setupAdminFilters();

  // Initial load of admin inventory if admin view is visible
  if (document.getElementById('adminView').style.display !== 'none') {
    loadAdminInventory();
  }
  
  // Add new function for comprehensive report generation
  function generateComprehensiveReport() {
    const ano = document.getElementById('anoRelatorio').value;
    const formato = document.getElementById('formatoExport').value;
    
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'loading-message';
    loadingMsg.textContent = 'Gerando relatório...';
    document.body.appendChild(loadingMsg);

    fetch(`/api/comprehensive-report?format=${formato}&year=${ano}`)
      .then(response => {
        if (!response.ok) throw new Error('Erro ao gerar relatório');
        return response.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio_completo_${ano}.${formato}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(loadingMsg);
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Erro ao gerar relatório. Por favor, tente novamente.');
        document.body.removeChild(loadingMsg);
      });
  }

  document.getElementById('generateComprehensiveReport').addEventListener('click', generateComprehensiveReport);
});