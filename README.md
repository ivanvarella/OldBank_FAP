<div align="center" style="padding-top: 20px;">
  
# Projeto Django Old Bank

## Este projeto implementa uma aplicação web construída com Django simular o funcionamento simples de contas bancárias.

</div>


## Índice
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Como Executar o Projeto](#como-executar-o-projeto)
- [Observações](#observações)
- [Dependências](#dependências)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Telas de exemplo do projeto](#telas-de-exemplo-do-projeto)

## Funcionalidades

- **Cadastro e edição de usuários**
- **Gerenciamento de sessão dos usuários (autenticação Django)**
- **Sistema de autenticação de usuários**
- **Gerenciamento de permissões de acesso e modificações no sistema**
- **Criação de novas contas bancárias para os usuários**
- **Listagem, edição e encerramento de contas**
- **Registro das operações bancárias (Criação de contas, depósitos, saques, transferências (pendente), extratos, grafico de médias de saldos e movimentações, filtragem das operações por período e por tipo de operação)**


## Tecnologias Utilizadas

- ![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
- ![Django](https://img.shields.io/badge/Django-5.x-green.svg)
- ![MySQL](https://img.shields.io/badge/MySQL-Workbench-blue.svg)
- ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-blue.svg)
- ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow.svg)
- ![Git](https://img.shields.io/badge/Git-F05032.svg?logo=git&logoColor=white)
- ![GitHub](https://img.shields.io/badge/GitHub-181717.svg?logo=github&logoColor=white)
- ![Material UI](https://img.shields.io/badge/Material--UI-0081CB.svg?logo=material-ui&logoColor=white)

## Como Executar o Projeto

1. **Instale o MySQL**  
   Certifique-se de que o MySQL está instalado na sua máquina. Se ainda não tiver, instale-o seguindo as instruções para o seu sistema operacional.

2. **Crie um banco de dados MySQL**  
   Abra o MySQL Workbench e crie um novo banco de dados para o projeto:
   ```sql
   CREATE DATABASE old_bank_db;
   ```

3. **Clone o repositório**  
   HTTPS:
   ```bash
   git clone https://github.com/ivanvarella/OldBank_FAP.git
   ```
   OU

   SSH:
   ```bash
   git clone git@github.com:ivanvarella/OldBank_FAP.git
   ```

4. **Crie um ambiente virtual**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

5. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure o arquivo `settings.py`**  
   No arquivo `settings.py`, configure o banco de dados com as informações do MySQL criado anteriormente:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'old_bank_db',
           'USER': 'seu_usuario_mysql',
           'PASSWORD': 'sua_senha_mysql',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```

7. **Crie as tabelas do banco de dados**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

8. **Crie o superuser no Django**
   ```bash
   python manage.py createsuperuser
   ```
   No terminal, configure o superuser:
   ```bash
   Username (leave blank to use 'admin'): admin
   Email address: admin@example.com
   Password: ********
   Password (again): ********
   ```

9. **Inicie o servidor**
   ```bash
   python manage.py runserver
   ```

10. **Acesse a aplicação**  
    Abra o seu navegador e acesse: http://127.0.0.1:8000/usuarios/logar

## Observações

- Este projeto é um exemplo simples para fins de estudo.
- É importante implementar medidas de segurança adicionais para proteger os dados dos usuários em um ambiente real.
- Adapte o projeto de acordo com as suas necessidades e requisitos.

## Dependências

- `asgiref==3.8.1`: Framework ASGI para Django.
- `Django==5.1`: Framework Django para desenvolvimento web.
- `mysqlclient==2.2.4`: Conector do banco de dados MySQL.
- `sqlparse==0.5.1`: Ferramenta para formatação e análise de SQL.
- `typing_extensions==4.12.2`: Extensões para o módulo typing.

## Estrutura do Repositório
```plaintext
Proj_Mod.1_2/
├── 1 - Documentacao -> Documentação do projeto e arquivos informativos pertinentes
├── contas -> App de contas
├── core -> Arquivos de projeto e configuração do Django
├── moviemntacoes -> App de movimentacoes
├── templates/ -> Arquivos HTML, CSS, IMG, JS
├── usuarios/ -> App de usuários
├── venv -> Arquivos do gerenciador de ambiente (não disponível ao clonar, deve ser criado após clonar)
├── manage.py
├── README.md -> Este arquivo que você está lendo agora
└── requirements.txt -> Lista do módulos e bibliotecas de dependência do projeto
```

## Telas de exemplo do projeto
<table align="center">
  <tr>
    <td>
      <a href="1 - Documentacao/Telas_programa/login.jpg" target="_blank">
        <img src="1 - Documentacao/Telas_programa/login.jpg" alt="Imagem 1" width="200"/>
      </a>
    </td>
    <td>
      <a href="1 - Documentacao/Telas_programa/cadastro_usuario.jpg" target="_blank">
        <img src="1 - Documentacao/Telas_programa/cadastro_usuario.jpg" alt="Imagem 2" width="200"/>
      </a>
    </td>
  </tr>
  <tr>
    <td>
      <a href="1 - Documentacao/Telas_programa/edicao_usuario.jpg" target="_blank">
        <img src="1 - Documentacao/Telas_programa/edicao_usuario.jpg" alt="Imagem 3" width="200"/>
      </a>
    </td>
    <td>
      <a href="1 - Documentacao/Telas_programa/cadastro_conta.jpg" target="_blank">
        <img src="1 - Documentacao/Telas_programa/cadastro_conta.jpg" alt="Imagem 4" width="200"/>
      </a>
    </td>
  </tr>
  <tr>
    <td>
      <a href="1 - Documentacao/Telas_programa/edicao_conta.jpg" target="_blank">
        <img src="1 - Documentacao/Telas_programa/edicao_conta.jpg" alt="Imagem 3" width="200"/>
      </a>
    </td>
    <td>
      <a href="1 - Documentacao/Telas_programa/conta_cliente.jpg" target="_blank">
        <img src="1 - Documentacao/Telas_programa/conta_cliente.jpg" alt="Imagem 4" width="200"/>
      </a>
    </td>
  </tr>
  <tr>
    <td>
      <a href="1 - Documentacao/Telas_programa/conta_extrato.jpg" target="_blank">
        <img src="1 - Documentacao/Telas_programa/conta_extrato.jpg" alt="Imagem 3" width="200"/>
      </a>
    </td>
    <td>
      <a href="1 - Documentacao/Telas_programa/listar_contas.jpg" target="_blank">
        <img src="1 - Documentacao/Telas_programa/listar_contas.jpg" alt="Imagem 4" width="200"/>
      </a>
    </td>
  </tr>
</table>