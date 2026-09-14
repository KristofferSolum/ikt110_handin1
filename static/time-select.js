const selects = document.querySelectorAll('[data-select]');

function closeAll(except) {
  selects.forEach((select) => {
    if (select !== except) {
      select.classList.remove('open');
      select.querySelector('.select-trigger').setAttribute('aria-expanded', 'false');
    }
  });
}

selects.forEach((select) => {
  const trigger = select.querySelector('.select-trigger');
  const input = select.querySelector('input');
  const options = select.querySelectorAll('[role="option"]');

  function syncSelection() {
    const value = input.value.padStart(2, '0');
    options.forEach((option) => {
      option.setAttribute('aria-selected', String(input.value !== '' && option.dataset.value === value));
    });
  }

  input.addEventListener('focus', () => {
    closeAll();
    input.select();
  });
  input.addEventListener('input', syncSelection);
  input.addEventListener('blur', () => {
    if (input.validity.valid) input.value = input.value.padStart(2, '0');
    syncSelection();
  });

  trigger.addEventListener('click', () => {
    const willOpen = !select.classList.contains('open');
    closeAll(select);
    select.classList.toggle('open', willOpen);
    trigger.setAttribute('aria-expanded', String(willOpen));
    if (willOpen) {
      const menu = select.querySelector('.select-menu');
      const selected = select.querySelector('[aria-selected="true"]');
      menu.scrollTop = selected ? selected.offsetTop - menu.clientHeight / 2 + selected.offsetHeight / 2 : 0;
    }
  });

  options.forEach((option) => option.addEventListener('click', () => {
    input.value = option.dataset.value;
    options.forEach((item) => item.setAttribute('aria-selected', String(item === option)));
    select.classList.remove('open');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.focus();
  }));
});

document.addEventListener('click', (event) => {
  if (!event.target.closest('[data-select]')) closeAll();
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeAll();
});
