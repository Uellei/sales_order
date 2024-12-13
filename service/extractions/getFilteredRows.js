function getFilteredRows() {
    const table = document.querySelector('#salesOrderDataTable');
    const elements = Array.from(table.querySelectorAll('tbody tr')).filter(el => {
        return Array.from(el.querySelectorAll('td:nth-child(5)')).find(td => 
            td.textContent.trim() === "Confirmed" || td.textContent.trim() === "Delivery Outstanding"
        );
    });

    return elements.map(tr => {
        const firstTd = tr.querySelector('td');
        const SoOrder = tr.querySelector('td:nth-child(2)').textContent.trim();
        let index;
        let nestedTds = [];

        if (firstTd && firstTd.querySelector('i.fa-square-plus')) {
            const parentChildren = Array.from(firstTd.parentNode.parentNode.children);
            index = parentChildren.indexOf(tr) + 1;
            firstTd.click();
        }

        let nextTr = tr.nextElementSibling;
        while (nextTr && nextTr.nodeType !== 1) {
            nextTr = nextTr.nextSibling;
        }

        if (nextTr) {
            nestedTds = Array.from(nextTr.querySelectorAll('tbody > tr > td:nth-child(2)')).map(td => td.textContent.trim());
        }

        if (firstTd && firstTd.querySelector('i.fa-square-minus')) {
            firstTd.click();
        }

        return { index: index, elements: nestedTds, SoOrder: SoOrder };
    });
}