# TUTORIAL DE IMPLANTAÇÃO E EXECUÇÃO DO SERVIDOR (DJANGO + WAITRESS + NGINX)

Este documento detalha o passo a passo para configurar e executar a aplicação em um ambiente de produção no Windows Server, além de explicar a lógica de armazenamento de mídias.

=============================================================================
1. PRÉ-REQUISITOS E INSTALAÇÃO
=============================================================================
Certifique-se de que o Python esteja instalado e adicionado ao PATH do Windows.
Recomenda-se o uso de um ambiente virtual (venv).

1. Abra o terminal (PowerShell ou CMD) na pasta raiz do projeto (c:\Lucas\SesenAppMain).
2. Ative seu ambiente virtual (se aplicável):
   .\venv\Scripts\activate
3. Instale todas as dependências atualizadas:
   pip install -r requirements.txt

*Nota: O pacote waitress foi adicionado ao requirements.txt para servir como o servidor WSGI de produção em ambiente Windows.*

=============================================================================
2. CONFIGURAÇÃO DO SERVIDOR WSGI (WAITRESS)
=============================================================================
Diferente do ambiente de desenvolvimento (manage.py runserver), em produção utilizamos o Waitress por sua estabilidade e performance no Windows.

Para iniciar a aplicação via Waitress:
1. No terminal, certifique-se de que está na pasta raiz do projeto.
2. Execute o comando:
   waitress-serve --listen=127.0.0.1:8000 sesen_app.wsgi:application

O Waitress passará a rodar a aplicação em background ou na janela do terminal na porta 8000.
Recomenda-se criar um Script .bat ou usar o Gerenciador de Tarefas do Windows / NSSM para rodar esse comando como serviço sempre que o servidor for reiniciado.

=============================================================================
3. CONFIGURAÇÃO DO NGINX (PROXY REVERSO E SERVIDOR DE MÍDIA)
=============================================================================
O Nginx será responsável por receber as requisições de rede (porta 80), servir os arquivos estáticos (CSS, JS) e de mídias nativamente, e repassar requisições dinâmicas para o Waitress na porta 8000.

1. Baixe o Nginx versão Windows e extraia em C:\nginx\ (ou pasta similar).
2. Abra o arquivo C:\nginx\conf\nginx.conf e modifique/substitua as configurações do bloco "server" principal pela seguinte configuração:

    server {
        listen       80;
        server_name  localhost; # Ou seu endereço de IP local (ex: 192.168.0.x)

        # 1. Requisições dinâmicas encaminhadas para o Waitress
        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # 2. Servir Arquivos Estáticos (Static)
        location /static/ {
            alias C:/Lucas/SesenAppMain/staticfiles/;
        }

        # 3. Servir Arquivos de Mídia (Media) - (Uploads dos Elevadores)
        location /media/ {
            alias C:/Lucas/SesenAppMain/media/;
            # Importante: para PDFs, Imagens, e vídeos, isso garante o funcionamento correto:
            add_header Access-Control-Allow-Origin *;
        }
    }

3. Antes de iniciar, garanta que os arquivos estáticos estão reunidos executando:
   python manage.py collectstatic
4. Para iniciar o Nginx, dê dois cliques no nginx.exe, ou via terminal execute `start nginx`.

=============================================================================
4. LÓGICA DE ARMAZENAMENTO DE MÍDIAS (UPLOADS)
=============================================================================
O sistema agora possui capacidade para anexar fotos, PDFs, arquivos Word e Excel aos registros do módulo Elevadores (Ordens de Serviço, MPM e Peças).

Como funciona no backend:
- Configurações (settings.py): Foram definidos os caminhos base: MEDIA_URL = '/media/' e MEDIA_ROOT = BASE_DIR / 'media'.
- Salvar Dinamicamente: Ao fazer o upload (Ex: no modal Editar Chamado), os arquivos passam pela função `dinamic_upload_path` localizada em sesen_app/utils.py.
- Organização em Pastas: Os arquivos não ficam bagunçados. Eles são guardados de maneira estruturada e autoexplicativa com a seguinte lógica de caminho:
  C:\Lucas\SesenAppMain\media\<nome_do_app>\<nome_do_modelo>\<ano>\<mes>\<uuid>_nome_original.extensão
  
  *Exemplo:* media/elevadores/elevorderreg/2026/07/72e61-a3f2..._imagem.png

Como visualizar:
- Ao listar itens nas tabelas, o frontend verifica se a URL da mídia foi retornada.
- Os modais de visualização exibirão um botão de download/acesso que puxará o arquivo diretamente de `http://localhost/media/...`. É por conta dessa requisição que o bloco Nginx configurado acima é crucial, pois o Django não servirá estes arquivos de forma nativa e performática em produção.

=============================================================================
5. VERIFICAÇÕES DE SAÚDE
=============================================================================
Caso os uploads não estejam carregando:
1. Verifique se o diretório `C:\Lucas\SesenAppMain\media` existe e possui permissão de leitura/gravação pelo Windows (o Waitress precisará de permissão para gravar na pasta).
2. Verifique se o Nginx está de fato rodando, acesse `http://localhost/media/...` para testar.
3. Se os formulários do sistema enviarem erro, garanta que seu ambiente virtual esteja rodando e atualizado com as migrations: `python manage.py migrate`.
