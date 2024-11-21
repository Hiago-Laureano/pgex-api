# PGEX API

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

Este projeto é uma API RESTful contruída com **Python** e **Django Rest Framework** para pesquisas de clima organizacional e geração de relatórios.

## Como usar o projeto

Instale o Docker e o Python caso não possuir em sua maquina

obs.: Docker será usado para subir o servidor de banco de dados MySQL

### Clone o Repositório
```sh
git clone https://github.com/Hiago-Laureano/pgex-api.git
```

### Crie o arquivo .env com o comando abaixo

```sh
python generate_ENVFILE.py
```
Se o comando não funcionar e você estiver em um ambiente linux tente:
```sh
python3 generate_ENVFILE.py
```
Caso funcionar com python3, nos seguintes comandos que exister "python" cambie por "python3"


### No arquivo .env criado atualize os dados que achar necessário
```dosini
DATABASE_NAME <-- nome do banco de dados
DATABASE_ROOT_PASSWORD <-- senha do root
DATABASE_USER <-- nome do usuário
DATABASE_USER_PASSWORD <-- senha do usuário
DATABASE_HOST <-- endereço do banco de dados
DATABASE_PORT <-- porta do banco de dados
SECRET_KEY <-- secret key da aplicação
```

## Ambiente de Desenvolvimento

### Crie um ambiente virtual para instalar as dependências do python
```sh
python -m venv venv
```
### Acesse o ambiente virtual

Windows
```sh
. venv/Scripts/activate
```
Linux
```sh
. venv/bin/activate
```

### Instale as Dependências
```sh
pip install -r requirements-dev.txt
```

### Subir o serviço com o banco de dados
```sh
docker-compose up -d
```

### Criar as migrations
```sh
python manage.py makemigrations
```

### Migrar para o banco de dados as migrations
```sh
python manage.py migrate
```

### Criar um superusuário inicial
```sh
python manage.py createsuperuser
```

### Rodar o projeto
```sh
python manage.py runserver
```

### Acessar o projeto

[http://localhost:8000](http://localhost:8000)


## API Endpoints

### Autenticação
```
POST /api/auth/ - Obter token access JWT [permissão: qualquer um]

CAMPOS DE /api/auth/ = [
    email[texto] <-- apenas POST - obrigatório
    password[texto] <-- apenas POST - obrigatório
    access[token JWT] <-- retorno POST
    refresh[token JWT] <-- retorno POST
]

POST /api/auth/refresh/ - Obter token refresh JWT [permissão: qualquer um]

CAMPOS DE /api/auth/refresh/ = [
    refresh[token JWT] <-- apenas POST - obrigatório
    access[token JWT] <-- retorno POST
]
```

### Pesquisas

```
GET /api/v1/surveys/ - Obter uma lista de todas as pesquisas [permissão: apenas membros da equipe]

GET /api/v1/surveys/{id}/ - Obter uma pesquisa específica [permissão: se a pesquisa estiver ativa, qualquer um, se não, apenas membros da equipe]

DELETE /api/v1/surveys/{id}/ - Deletar uma pesquisa [permissão: apenas superusuários]

POST /api/v1/surveys/ - Criar uma pesquisa [permissão: apenas membros da equipe]

PUT /api/v1/surveys/{id}/ - Atualizar todos os dados de uma pesquisa [permissão: apenas membros da equipe]

PATCH /api/v1/surveys/{id}/ - Atualizar dados de uma pesquisa parcialmente [permissão: apenas membros da equipe]

CAMPOS DE /api/v1/surveys/ ou /api/v1/surveys/{id}/ = [
    id[inteiro] <-- apenas GET
    name[texto] <-- obrigatório
    questions[JSON com as perguntas, exemplo do formato: 
    {'Perguntas sobre saúde': [
        {'id': 1, 'question': 'Como está sua saúde mental?', 'is_descriptive': false}, {'id': 2, 'question': 'Como está sua saúde física?', 'is_descriptive': false}
    ],
    'perguntas sobre trabalho': [
        {'id': 3, 'question': 'Descreva como está seu trabalho', 'is_descriptive': true}]}
    ] <-- obrigatório
    n_questions[inteiro] <-- não obrigatório
    active[booleano] <-- não obrigatório
    active_until[data limite para participar] <-- não obrigatório
    created[data] <-- apenas GET
    updated[data] <-- apenas GET
]

POST /api/v1/surveys/{id}/respond/ - Responder uma pesquisa [permissão: qualquer um]

CAMPOS DE /api/v1/surveys/{id}/respond/ = [
    id[inteiro] <-- apenas GET
    survey[inteiro - id Pesquisa] <-- obrigatório
    responses[JSON com as respostas, exemplo do formato: 
    {
        '1': 5,
        '2': 4,
        '3': 'Meu trabalho está muito bom'

    } - as chaves do JSON são os ids das perguntas] <-- obrigatório
    created[data] <-- apenas GET
    updated[data] <-- apenas GET
]

GET /api/v1/surveys/{id}/confirmation/?cc={código} - Confirmar código de participação em uma pesquisa. Note que é necessário informar o parâmetro de URL "cc" com o código [permissão: apenas membros da equipe]

CAMPOS DE /api/v1/surveys/{id}/confirmation/ = [
    valid[booleano] <-- apenas GET
]

GET /api/v1/surveys/{id}/json/ - Obter um arquivo JSON com as perguntas de uma pesquisa [permissão: apenas membros da equipe]

CAMPOS DE /api/v1/surveys/{id}/json/ = [
    link[texto com o link do arquivo] <-- apenas GET
]

GET /api/v1/surveys/{id}/report/ - Obter um relatório em HTML de uma pesquisa [permissão: apenas membros da equipe]

CAMPOS DE /api/v1/surveys/{id}/report/ = [
    link[texto com o link do arquivo] <-- apenas GET
]
```