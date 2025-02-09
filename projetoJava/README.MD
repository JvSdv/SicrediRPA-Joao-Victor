
# Projeto Java

## Configuração de ambiente java
Necessário o java instalado na máquina e o maven
```bash
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install maven
```

### Instalação de dependências
```bash
mvn clean install
```

### Gerar o .jar (compilado)
```bash
mvn clean package
```

- rodar o .jar
```bash
java -jar target/ClienteSocketIO-1.0-SNAPSHOT-jar-with-dependencies.jar
```