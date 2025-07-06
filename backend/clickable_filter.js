elements => {
    return elements
        .filter(el => {
            const style = window.getComputedStyle(el);
            return (
                (el.tagName === 'A' && el.href) ||
                el.tagName === 'BUTTON' ||
                el.onclick ||
                el.getAttribute('role') === 'button' ||
                el.getAttribute('tabindex') !== null ||
                style.cursor === 'pointer'
            );
        })
        .map(el => {
            return {
                tag: el.tagName,
                text: el.innerText.trim(),
                id: el.id,
                class: el.className,
                href: el.href || null
            };
        });
}