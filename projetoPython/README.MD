### Configuração de ambiente python

- Acesse o `diretório` do projeto e configure o ambiente virtual com os comandos abaixo:
```bash
  cd projetoPython
```

- Instalar, Criar, Ativar, Atualizar um ambiente virtual com os comandos:
```bash
  sudo apt install python3.10-venv
  python3 -m venv .venv
  . .venv/bin/activate ou source .venv/bin/activate
  python -m pip install --upgrade pip
```

- instalação de dependências
```bash
  pip install -r requirements.txt
```

- instalação das dependencias playright e dos web browsers do playRight
```bash
  playwright install-deps
  playwright install
```

### Execução do projeto
- Para executar o projeto, utilize o comando abaixo, etando na `pasta do projeto`:
```bash
  python main.py
```

### Extra: utilizar o freeze para gerar o requirements.txt
```bash
  pip freeze > requirements.txt.lock
```