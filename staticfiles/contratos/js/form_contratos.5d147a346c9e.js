const ids = ['id_sei_dod', 'id_sei_etp', 'id_sei_tr', 'id_sei_edital', 'id_sei_fiscais'];

ids.forEach(el => {
    let element = document.getElementById(el);
    if (element) {
        IMask(
            element,
            {
                mask: 'SEI nº: 0000000',
                lazy: false
            }
        );
    }
});

let cnpjElement = document.getElementById('id_cnpj');
if (cnpjElement) {
    IMask(
        cnpjElement,
        {
            mask: '00.000.000/0000-00',
            lazy: false
        }
    );
}

let numContratoElement = document.getElementById('id_num_contrato');
if (numContratoElement) {
    IMask(
        numContratoElement,
        {
            mask: 'TSE nº 00/0000',
            lazy: false
        }
    );
}

let seiProcessoElement = document.getElementById('id_sei_processo');
if (seiProcessoElement) {
    IMask(
        seiProcessoElement,
        {
            mask: '0000.00.000000000-0',
            lazy: false
        }
    );
}
