# Requisitos para Integração com a API do SEI

Este documento detalha todas as informações, permissões e endpoints necessários que devem ser solicitados à área de Tecnologia da Informação (TI) ou aos administradores do SEI para garantir o funcionamento do **Módulo de Monitoramento Automático SEI**.

---

## 1. Credenciais e Autenticação

Para que o aplicativo possa se conectar e puxar os dados do SEI em nome da sua unidade, a TI precisa fornecer as seguintes credenciais de acesso ao Web Service:

- **SiglaSistema**: O identificador do seu sistema cadastrado no SEI (ex: `SESEN_APP`).
- **IdentificacaoServico**: A chave de serviço vinculada à sigla acima.
- **IdUnidade (Opcional)**: O identificador numérico interno da sua unidade (ex: SESEN) dentro do banco de dados do SEI. Isso ajuda a filtrar andamentos específicos da unidade.

## 2. Infraestrutura e Conectividade

A infraestrutura de rede deve permitir a comunicação entre o servidor da sua aplicação e o Web Service do SEI.

- **URL do Web Service (WSDL)**: O endereço exato de produção (ou homologação para testes iniciais).
  - *Formato esperado:* `https://[ENDERECO_DO_SEI]/sei/controlador_ws.php?servico=sei&wsdl`
- **Liberação de Firewall**: A TI precisa garantir que o servidor onde a aplicação está hospedada (IP / Hostname: `tsevm203.tse.jus.br`) tenha permissão de saída para acessar a URL do WSDL do SEI.

---

## 3. Endpoints (Operações) Necessários

No cadastro do seu sistema dentro da área administrativa do SEI, a TI precisa liberar o acesso específico a duas operações do Web Service. Segue a justificativa técnica para cada uma:

### A. `consultarProcedimento`
- **Para que serve:** Permite obter os metadados (capa) do processo informando apenas o seu número.
- **Dados extraídos para o Dashboard:**
  - `Data de Autuação` (Data de recebimento original).
  - `Especificação` (Objeto central do processo).

### B. `listarAndamentos`
- **Para que serve:** Retorna todo o histórico de trâmite e movimentações do processo.
- **Dados extraídos para o Dashboard:**
  - `Descrição` do último andamento (usado para popular a coluna **"Situação"** e **"Tratativas"**).
  - `Data e Hora` da última movimentação (usado para calcular a coluna **"Dias Parado / Tempo de Tramitação"**).
  - `Unidade` onde o processo se encontra atualmente.

---

**Como utilizar as informações:**
Assim que a TI fornecer a **SiglaSistema**, a **IdentificacaoServico** e a **URL**, basta substituir as variáveis no arquivo `monitoramento_sei/sei_client.py` do código fonte. Após isso, a comunicação passará a funcionar em tempo real.
