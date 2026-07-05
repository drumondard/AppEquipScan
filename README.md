# AppEquipScan
Projeto de identificação visual de ativos de rede utilizando IA e processamento de imagem.

O AppEquipScan é uma solução inteligente para inventário de ativos de rede. Ele utiliza visão computacional e Inteligência Artificial para identificar automaticamente equipamentos a partir de fotos, integrando os dados diretamente ao BigQuery para gestão de ativos em tempo real.

🚀 Funcionalidades
* Captura Visual: Upload de imagens de equipamentos de rede via interface web.  
* Identificação por IA: Processamento automático para extração de dados como Fabricante, Modelo, Função e Número de Série. 
* Interface de Edição: Permite ao usuário revisar e ajustar os dados identificados pela IA antes da confirmação final. 
* Persistência em Tempo Real: Integração com Google Cloud (GCS para armazenamento de fotos e BigQuery para banco de dados).  

🛠 Tecnologias 
* UtilizadasBackend: Python, FastAPI, Uvicorn. 
* IA & Processamento: Serviços customizados para extração de dados. 
* Google Cloud Platform: BigQuery (banco de dados), GCS (armazenamento de arquivos). 
* Frontend: HTML5, CSS3 (com identidade visual V.tal), JavaScript (Fetch API).
* Containerização: Docker e Docker Compose. 

🛠 Estrutura do Projeto
* app.py: Ponto de entrada da API FastAPI. 
* services/: Contém a lógica de negócios (IA, BigQuery e GCS). 
* templates/: Interface web (index.html). 
* static/: Recursos estáticos (logos e ícones). 

 🎨 Identidade Visual
 * O projeto segue estritamente as diretrizes da marca V.tal, utilizando: 
    * Paleta de Cores: Foco no Amarelo V.tal e Preto V.tal. 
    * Tipografia: Uso da fonte Inter para garantir legibilidade. 
Este projeto é destinado ao controle e inventário de rede.


📋 Como Rodar o Projeto
Pré-requisitos:
* Certifique-se de ter o Docker e o Docker Compose instalados.
* Configure suas credenciais do Google Cloud para acesso ao BigQuery e GCS.

Configuração:
* Preencha as variáveis de ambiente necessárias (como o projeto do GCP).
* Verifique se os arquivos de serviço (services/) estão corretamente organizados.