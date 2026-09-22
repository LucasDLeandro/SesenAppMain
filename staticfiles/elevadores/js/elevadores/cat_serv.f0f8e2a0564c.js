function adicionarItem() {

    const lista = document.getElementById('serviceList');
    const totalForms = document.getElementById('id_servicos-TOTAL_FORMS');
    const emptyForm = document.getElementById('item-formset-vazio');
    //emptyForm.children[2].style.display = "none"
    const cloneForm = emptyForm.cloneNode(true);

    const inputs = cloneForm.querySelectorAll("input, textarea");
    const labels = cloneForm.querySelectorAll("label");

    labels.forEach((label) => {
        const forAtributo = label.getAttribute('for');
        let novoFor = forAtributo.replace(/__prefix__/g, totalForms.value);
        label.setAttribute('for', novoFor);
    });

    inputs.forEach((input) => {
        const nomeAtual = input.name;
        const idAtual = input.id;

        let novoNome = nomeAtual.replace(/__prefix__/g, totalForms.value);
        let novoId = idAtual.replace(/__prefix__/g, totalForms.value);
        
        input.name = novoNome;
        input.id = novoId;
        input.value = "";
        
    });

    cloneForm.removeAttribute('id');
    cloneForm.removeAttribute('style');
    lista.appendChild(cloneForm);
    totalForms.value = parseInt(totalForms.value) + 1;
    
}

function removerItem(btn) {
    // PEGA A LISTA
    const lista = document.getElementById('serviceList');

    //PEGA O VALOR DO TOTALFORMS
    const totalForms = document.getElementById('id_servicos-TOTAL_FORMS');
    let total = totalForms.value;
    
    // AGE NO CONTAINER PAI DO BOTAO
    const container = btn.closest('.item-formset');
    const deleteCheckbox = container.querySelector('input[name$="-DELETE"]');
    if (deleteCheckbox) {
        deleteCheckbox.checked = true;
        container.style.display = "none";
        
    } else {
        container.remove()
        
    }

    // SELECIONA OS ITENS RESTANTES E SUBSTITUI OS INDICES

    const itensRestantes = document.querySelectorAll('#serviceList .item-formset:not(#item-formset-vazio)')
    itensRestantes.forEach((li, index) => {
        const labels = li.querySelectorAll("label")
        const inputs = li.querySelectorAll("input, textarea")
    
        labels.forEach(label => {
            const forAtributo = label.getAttribute('for');
            let novoFor = forAtributo.replace(/\d+/g, index);
            console.log(novoFor);
            label.setAttribute('for', novoFor);
        })
        
        inputs.forEach(input => {
            input.name = input.name.replace(/\d+/g, index)
            input.id = input.id.replace(/\d+/g, index)
            })
    })
    console.log(`Qnt itens depois: ${itensRestantes.length}`)
    totalForms.value = itensRestantes.length
}
