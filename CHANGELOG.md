# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [1.0.0] - 2026-04-08

### Adicionado
- Sistema de gerenciamento de fretes (app `fretes`)
  - Cadastro e listagem de cargas
  - Formulário de carga (`carga_form`)
  - Comando de seed para dados de demonstração (`seed_demo`)
- Dashboard com visão geral do sistema (app `dashboard`)
  - Índice com serviços e estatísticas
- Módulo core com página inicial e autenticação (app `core`)
  - Tela de login
  - Página home
- Configuração do projeto Django 6.0.4
  - Settings centralizados em `config/`
  - Banco de dados SQLite
  - Arquivos estáticos e templates organizados
- Virtualenv local com dependências em `requirements.txt`
