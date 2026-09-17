# Regras de Formatação — TCC USP/Esalq (Data Science & Analytics)
> Template: Implementação de Algoritmo(s) de Machine Learning

---

## 1. Tabelas

| Regra | Detalhe |
|-------|---------|
| **Título** | Posicionado **acima** da tabela. Formato: `Tabela N. Descrição` |
| **Fonte/Notas** | Logo **abaixo** da tabela. Se dados próprios: `Fonte: Resultados originais da pesquisa` |
| **Bordas** | Apenas horizontais: borda superior e inferior do cabeçalho + borda inferior da tabela. **Sem bordas verticais nem internas** |
| **Cores** | Sem cores de fundo. Sem negrito dentro das células |
| **Fonte** | Arial 11, espaçamento simples |

---

## 2. Figuras (Gráficos, Imagens, Mapas)

| Regra | Detalhe |
|-------|---------|
| **Legenda/Título** | Posicionado **abaixo** da figura. Formato: `Figura N. Descrição` |
| **Fonte** | Logo abaixo da legenda |
| **Linhas de grade** | ❌ Proibido |
| **Bordas externas** | ❌ Proibido |
| **Fundo** | Branco ou transparente. ❌ Sem preenchimento colorido |
| **Título dentro do gráfico** | ❌ Proibido (o título fica como legenda abaixo) |
| **Eixos** | Linha sólida preta, espessura **1,5 pt** (apenas inferior e esquerdo) |
| **Títulos de eixos** | Arial 11 ou menor, cor preta |

### Configuração matplotlib equivalente
```python
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 1.5,
    "axes.edgecolor": "black",
    "axes.grid": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})
# Sem ax.set_title() — o título vai como legenda abaixo da figura no Word
```

---

## 3. Códigos e Algoritmos

| Regra | Detalhe |
|-------|---------|
| **Onde inserir** | Seção "Implementação de Algoritmo(s) de Machine Learning" |
| **Formato** | Texto editável com comentários explicativos em cada etapa |
| **Fonte** | Arial 11, cor preta, fundo branco (sem monoespaçada, sem fundo colorido) |
| **Outputs visuais** | Inserir como **Figuras** em "Resultados e Discussão", seguindo as regras de figura |

---

## 4. Regra Geral

> ⚠️ **Todo elemento visual (tabela, figura ou código) deve ser citado no parágrafo imediatamente anterior à sua aparição no texto.**

---

## 5. Checklist rápido antes de inserir qualquer elemento

- [ ] O elemento tem número sequencial? (Tabela 1, Figura 1, etc.)
- [ ] O título/legenda está no lugar correto? (acima para tabelas, abaixo para figuras)
- [ ] A fonte está indicada logo abaixo?
- [ ] O elemento foi citado no parágrafo anterior?
- [ ] Para gráficos: sem grid, sem borda, sem título interno, eixos pretos 1,5 pt?
- [ ] Para tabelas: sem bordas verticais, sem cores de fundo?
