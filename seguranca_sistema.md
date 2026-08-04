# Mapeamento de Segurança do Sistema (FAQ)

Este documento foi elaborado para fornecer respostas técnicas e precisas a qualquer questionamento sobre as medidas de segurança implementadas na aplicação (SesenApp). Ele cobre desde o nível de acesso até a proteção contra invasões.

---

## 1. Autenticação e Controle de Acesso

**Q: Como é garantido que apenas usuários autorizados acessem o sistema?**
**R:** O sistema utiliza o framework de autenticação nativo do Django (um dos mais robustos do mercado). O acesso às páginas requer autenticação por sessão, blindada contra interceptações se transmitida via HTTPS. Para as APIs (que alimentam partes reativas como DataTables e modais), o acesso também é restrito às sessões válidas. Somente usuários ativamente cadastrados na base de dados podem fazer login.

**Q: O sistema possui diferenciação de perfis (Autorização / RBAC)?**
**R:** Sim. Implementamos o Controle de Acesso Baseado em Regras (Role-Based Access Control - RBAC). O sistema diferencia perfis (Comum, Supervisor, Administrador) e Grupos (ex: grupo `Telefonia`). Funcionalidades críticas, como visualização de painéis administrativos, deleção de registros e edição de configurações só são renderizadas e aceitas pelo backend se o usuário tiver a permissão e o perfil adequado.

## 2. Proteção Contra Ataques Comuns na Web

**Q: O sistema é vulnerável a Injeção de SQL (SQL Injection)?**
**R:** Não. Todas as interações com o banco de dados são feitas exclusivamente através do ORM (Object-Relational Mapping) do Django. O ORM automaticamente escapa e parametriza as *queries* enviadas ao banco de dados, neutralizando qualquer tentativa de injeção maliciosa de SQL inserida em formulários ou URLs.

**Q: Como o sistema se protege contra o roubo de sessões (XSS - Cross-Site Scripting)?**
**R:** O motor de *templates* do Django aplica o "Escalonamento Automático" (Autoescaping) em todos os dados textuais exibidos no HTML. Isso significa que se um usuário mal intencionado inserir um script JavaScript `<script>alert('hack')</script>` em um campo, o sistema converterá as tags para entidades HTML `&lt;script&gt;`, tornando o código inofensivo no navegador.

**Q: O sistema está protegido contra solicitações forjadas de outros sites (CSRF)?**
**R:** Sim. A proteção contra CSRF (Cross-Site Request Forgery) está ativada de forma global (Middleware padrão do Django). Todo formulário ou requisição *POST/PUT/PATCH/DELETE* vinda do frontend (incluindo as chamadas AJAX/Fetch) exige um `CSRF Token` dinâmico único e validado no servidor. Requisições sem esse token são imediatamente rejeitadas (Erro 403).

## 3. Armazenamento e Integridade dos Dados

**Q: Como as senhas dos usuários são armazenadas no banco de dados? Se o banco vazar, as senhas estarão expostas?**
**R:** O sistema não armazena as senhas em texto puro. Ele utiliza o algoritmo **PBKDF2** combinado com um hash criptográfico **SHA-256** e um *salt* único para cada senha. Trata-se de um padrão da indústria e de uso militar, projetado especificamente para ser resistente a ataques de força bruta e tabelas arco-íris (rainbow tables). 

**Q: Os dados de sessões (cookies) podem ser alterados pelo lado do cliente?**
**R:** Não, o sistema armazena a sessão de forma segura usando um ID único assinado no cookie, cujo conteúdo real (os dados da sessão) fica armazenado dentro do servidor (no banco de dados). Qualquer adulteração do Session ID no navegador fará a sessão se tornar inválida.

## 4. Manipulação de Arquivos e Uploads

**Q: É possível que um usuário faça upload de um arquivo malicioso, como um vírus ou um script `.exe` / `.php` se passando por uma foto ou PDF?**
**R:** Os *inputs* do front-end estão blindados com a tag `accept="application/pdf"` ou formatos de imagem. No Backend, os arquivos são salvos na pasta `/media/` (separada dos arquivos estáticos vitais do servidor). É altamente recomendado que o servidor web (ex: Nginx/Apache) seja configurado no momento do deploy para desabilitar qualquer execução de código ou script de dentro da pasta de mídia, transformando-a numa pasta puramente "read-only" para visualização.

## 5. Resiliência de Aplicação e Logs

**Q: Se ocorrer um erro crítico interno, o usuário verá informações confidenciais do servidor na tela (Stack trace/Erros de código)?**
**R:** Em ambiente de produção (quando a variável `DEBUG = False` estiver configurada no `.env`), o Django bloqueia a exibição de qualquer detalhe interno de código na tela do usuário. Em vez disso, exibe páginas padronizadas de Erro 404 (Não encontrado) e 500 (Erro no Servidor). Os rastreios de código falho ficam visíveis apenas nos *Logs Internos* do servidor.

**Q: As integrações externas (WhatsApp, E-mail) podem "travar" o sistema se saírem do ar?**
**R:** Não. Como implementado recentemente, as requisições de comunicação operam utilizando `Threading` de forma assíncrona. Se o servidor do WhatsApp ou de E-mail ficar fora do ar, o fluxo de execução principal do sistema continua funcionando sem travar os processos críticos, limitando-se apenas a reportar as falhas nos logs locais.

## 6. Comunicação de Rede

**Q: A comunicação entre o computador do usuário e o servidor pode ser interceptada (Man-in-the-Middle)?**
**R:** Esta é uma responsabilidade da camada de infraestrutura. Em ambiente de produção, a aplicação DEVE rodar sob o protocolo **HTTPS (SSL/TLS)** (ex: certificado Let's Encrypt / Certificado da Intranet do Tribunal). Quando implementado sob HTTPS, todos os dados transferidos entre o navegador e o servidor — incluindo os Tokens CSRF, IDs de sessão, uploads de arquivos e senhas — são totalmente criptografados de ponta a ponta.

---

> IMPORTANTE: Toda a arquitetura foi desenhada priorizando as melhores práticas da OWASP (Open Worldwide Application Security Project) atendidas nativamente pelo *Django Framework*. É de vital importância não desabilitar o `CsrfViewMiddleware` e manter a configuração `DEBUG = False` ao implantar o sistema definitivamente em um servidor de produção.
