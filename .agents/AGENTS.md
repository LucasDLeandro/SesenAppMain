- Sempre atualize o arquivo requirements.txt ao instalar novas dependências ou modificar módulos.

- Sempre salve as alterações no git após a execução de tarefas (ex: git add . && git commit -m "Auto commit by Agent"), para não perder histórico de modificações.

- Antes de executar qualquer mudança que não seja solicitada por causa de erros, faça o commit dos arquivos para o git. Salve os arquivos para que se a mudança quebrar o código, seja possível retornar.

- Sempre aja como um engenheiro de software sênior e se preocupe se as novas atualizações não podem quebrar outras partes do código, então sempre verifique se existem integrações com o que você pretende modificar.

- Sempre que você criar um formulário, nas ações de POST mesmo se for sucesso ou falha, deve lançar um SweetAlert pertinente com o que ocorreu, substituindo o uso de `alert()` padrão.
