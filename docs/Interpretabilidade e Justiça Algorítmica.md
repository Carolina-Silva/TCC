# Texto — Seção: Interpretabilidade e Justiça Algorítmica

> **Instruções de uso:** Copie cada bloco de texto para o Word na posição indicada. Os marcadores `[Figura N]` devem ser substituídos pela numeração real das figuras no seu documento. As figuras correspondentes estão salvas em `reports/figures/`.

---

## 4.X Interpretabilidade e Justiça Algorítmica

### Importância Global das Features (SHAP Summary)

Para além das métricas preditivas, a interpretabilidade do modelo XGBoost foi investigada por meio dos valores SHAP (*SHapley Additive exPlanations*), que decompõem a contribuição de cada variável para a predição individual de risco de óbito. A [Figura N] apresenta o *summary plot* de beeswarm para uma amostra de 2.000 registros do conjunto de teste, evidenciando tanto a magnitude quanto a direção do efeito de cada preditor.

A variável `idade` destacou-se como o fator de maior importância global, com valores SHAP que alcançam amplitude superior a 1,0 na escala de log-odds: pacientes mais idosos (valores da feature em vermelho) apresentam consistentemente SHAP positivos — indicando elevação do risco de óbito —, enquanto pacientes mais jovens concentram SHAP negativos, exercendo efeito protetor. Esse padrão é coerente com a fisiopatologia do IAM e com a literatura epidemiológica que aponta a idade como principal fator de risco para mortalidade intra-hospitalar por síndrome coronariana aguda.

O `procedimento_realizado_cod` posicionou-se como segundo preditor em importância, com SHAP predominantemente negativos associados a valores altos da feature — sugerindo que determinados procedimentos de maior complexidade/intervenção (como cateterismo e angioplastia, códigos de maior valor numérico) estão associados à redução do risco de óbito, possivelmente por representarem acesso efetivo a tratamento intervencionista. O `tipo_gestor`, em terceiro lugar, apresentou SHAP fortemente negativos para valores altos: estabelecimentos de gestão privada/federal (códigos mais elevados) associam-se a menor risco de óbito, refletindo diferenças estruturais e de capacidade instalada entre os tipos de gestão do SUS. O `tipo_diag_sec_2_cod`, relativo ao diagnóstico secundário codificado, apresentou SHAP positivos para valores elevados, indicando que comorbidades específicas elevam o risco de desfecho fatal.

Entre as variáveis de infraestrutura hospitalar, `qtd_leitos_cirurgicos` apareceu na 11ª posição do ranking de importância global, com SHAP predominantemente negativos para valores altos — ou seja, hospitais com maior número de leitos cirúrgicos associam-se a menor probabilidade de óbito —, confirmando a hipótese central deste estudo de que a estrutura do estabelecimento exerce influência independente sobre o desfecho, além das características clínicas do paciente.

`[Figura N. Valores SHAP por variável para o modelo XGBoost (amostra n=2.000 do conjunto de teste). O eixo horizontal representa o impacto no output do modelo (log-odds de óbito); cada ponto corresponde a um paciente. A cor indica o valor da feature (vermelho = alto, azul = baixo). Fonte: Resultados originais da pesquisa.]`

---

### Ranking de Importância Absoluta (SHAP Bar Plot)

A [Figura N+1] confirma a hierarquia de importância por meio da importância SHAP média absoluta — métrica que captura a magnitude do efeito independentemente de sua direção. `Idade` (média |SHAP| ≈ 0,43) e `procedimento_realizado_cod` (≈ 0,35) concentram, de forma conjunta, a maior parcela da capacidade preditiva do modelo. As variáveis `tipo_gestor` (≈ 0,24) e `tipo_diag_sec_2_cod` (≈ 0,18) completam o quarteto dominante. A partir da quinta posição, as contribuições individuais decrescem de forma acentuada, com `tipo_diag_sec_1_Preexistente`, `carater_internacao_Urgência` e os demais preditores apresentando importância média inferior a 0,10 — indicando que o poder preditivo do modelo está relativamente concentrado em um subconjunto de quatro variáveis principais.

`[Figura N+1. Importância SHAP média absoluta das 15 principais variáveis do modelo XGBoost. Fonte: Resultados originais da pesquisa.]`

---

### Análise de Equidade por Sexo

A análise de equidade (*fairness*) por sexo examinou se o modelo atribui importâncias e efeitos distintos a pacientes masculinos e femininos, o que poderia indicar viés sistemático. As [Figuras N+2 e N+3] apresentam os *summary plots* SHAP para cada subgrupo (n=1.000 por amostragem).

Em ambos os grupos, as mesmas variáveis dominam o ranking: `idade`, `procedimento_realizado_cod` e `tipo_gestor` ocupam as três primeiras posições, com padrões de direção de efeito consistentes — idade avançada eleva o risco, procedimentos intervencionistas e gestão privada/federal reduzem o risco de óbito. Essa estabilidade na hierarquia de preditores sugere que o modelo não discrimina de forma estrutural entre os sexos na atribuição de risco.

Uma diferença sutil foi observada no comportamento de `carater_internacao_Urgência`: no subgrupo masculino, a feature apresenta dispersão de SHAP ligeiramente maior à esquerda (efeito protetor em internações programadas mais frequentes), enquanto no subgrupo feminino a variável `sexo_Masculino` aparece com SHAP próximos de zero — o que é esperado, dado que essas pacientes são codificadas como 0 nessa feature binária. Não foram identificados padrões que indiquem viés sistemático do modelo na atribuição de risco entre os dois grupos sexuais.

`[Figura N+2. Valores SHAP para pacientes masculinos (n=1.000). Fonte: Resultados originais da pesquisa.]`

`[Figura N+3. Valores SHAP para pacientes femininos (n=1.000). Fonte: Resultados originais da pesquisa.]`

---

### Análise de Equidade por Raça/Cor

A análise de equidade por raça/cor foi conduzida para os grupos com volume mínimo de 50 registros no conjunto de teste, abrangendo as categorias **Branca**, **Parda**, **Preta** e **Amarela**. As [Figuras N+4 a N+7] apresentam os perfis SHAP para cada grupo.

De forma geral, observa-se notável consistência na hierarquia de importância entre os quatro grupos raciais: `idade` mantém-se como preditor dominante em todos eles, seguida por `procedimento_realizado_cod` e `tipo_gestor`. Os padrões de direção de efeito são preservados: idades mais elevadas e comorbidades secundárias elevam o risco de óbito de forma uniforme entre os grupos; procedimentos intervencionistas e tipo de gestor exercem efeito protetor em todos os subgrupos analisados.

A principal divergência identificada refere-se ao grupo **Amarela**: a variável `qtd_leitos_cirurgicos` ascende ao 7º lugar no ranking desse grupo (ante a 11ª posição no modelo global), com SHAP negativos para valores altos, sugerindo que a disponibilidade de leitos cirúrgicos exerce efeito protetor proporcionalmente mais pronunciado nessa subpopulação. Esse resultado deve ser interpretado com cautela, dado o menor volume amostral do grupo Amarela em relação aos grupos Branca e Parda, o que pode amplificar a variabilidade dos SHAP individuais. Para os grupos **Preta** e **Parda**, os perfis são muito próximos ao do grupo **Branca**, não sendo identificadas divergências de ordem ou de sinal que sugiram tratamento diferenciado do modelo.

Em síntese, os resultados da análise de equidade indicam que o XGBoost opera de forma relativamente consistente entre os grupos de raça/cor incluídos na análise, sem evidência de viés sistemático na hierarquia de preditores. A ressalva metodológica central é que a análise SHAP-based aqui realizada avalia *paridade de importância das features* entre grupos — e não métricas formais de equidade de decisão (como equalidade de oportunidade ou *demographic parity*), que demandariam análise complementar com frameworks dedicados como `Fairlearn` ou `AI Fairness 360`.

`[Figura N+4. Valores SHAP — grupo Branca (n=1.000). Fonte: Resultados originais da pesquisa.]`

`[Figura N+5. Valores SHAP — grupo Parda (n=1.000). Fonte: Resultados originais da pesquisa.]`

`[Figura N+6. Valores SHAP — grupo Preta (n=1.000). Fonte: Resultados originais da pesquisa.]`

`[Figura N+7. Valores SHAP — grupo Amarela (n=1.000). Fonte: Resultados originais da pesquisa.]`

---

> **Nota sobre o grupo "Sem Informação":** O grupo com raça/cor não declarada também gerou figura (`shap_fairness_raca_sem_informação.jpg`). Recomenda-se **não incluí-lo** na seção de equidade, pois a ausência de declaração racial impede interpretação clínica ou sociológica significativa dos padrões SHAP. Pode ser mencionado em nota de rodapé como limitação dos dados.
