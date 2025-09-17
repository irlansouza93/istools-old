# Sistema de Internacionalização (i18n) - ISTools

## Arquivos de Tradução

### Estrutura dos Arquivos

- **istools_pt_BR.ts** - Arquivo fonte de tradução para português brasileiro
- **istools_en.ts** - Arquivo fonte de tradução para inglês
- **istools_pt_BR.qm** - Arquivo compilado de tradução para português brasileiro
- **istools_en.qm** - Arquivo compilado de tradução para inglês

### Formato dos Arquivos .qm

Os arquivos .qm foram criados em formato texto simplificado para compatibilidade:

```
# Compiled translation file for ISTools
# Language: pt_BR
# Generated from: istools_pt_BR.ts

[Context]
"source_string" = "translated_string"
```

### Strings Traduzidas

#### Menus e Ações Principais
- ISTools → ISTools
- Extend Lines → Estender Linhas
- Polygon Generator → Gerador de Polígonos
- Bounded Polygon Generator → Gerador de Polígonos Limitados
- Point on Surface Generator → Gerador de Pontos na Superfície

#### Mensagens de Erro
- Error → Erro
- No valid input layer selected or layer is empty → Nenhuma camada de entrada válida selecionada ou camada está vazia

#### Mensagens Informativas
- Click on the map to define the center. Right-click to cancel. → Clique no mapa para definir o centro. Clique com o botão direito para cancelar.

### Sistema de Carregamento

O plugin carrega automaticamente as traduções baseado na configuração de idioma do QGIS:

1. Detecta o idioma configurado no QGIS
2. Procura pelo arquivo .qm correspondente
3. Carrega as traduções se o arquivo existir
4. Usa strings em inglês como fallback

### Manutenção

Para adicionar novas traduções:

1. Adicione `self.tr("String")` no código Python
2. Atualize os arquivos .ts com as novas strings
3. Atualize os arquivos .qm com as traduções
4. Teste no QGIS

### Compilação Alternativa

O script `manual_compile.py` pode ser usado para gerar arquivos .qm básicos a partir dos arquivos .ts quando o Qt lrelease não estiver disponível.