(() => {
  const form = document.querySelector('.departure-card');
  const overlay = document.getElementById('route-transition');
  if (!form || !overlay) return;
  const submit = form.querySelector('.submit-route');
  let pending = false;
  let timer;

  // Submit fires only after the browser has validated the time fields.
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (pending) return;
    pending = true;
    submit.disabled = true;
    overlay.hidden = false;
    form.setAttribute('aria-busy', 'true');
    timer = window.setTimeout(() => {
      HTMLFormElement.prototype.submit.call(form);
    }, 1000);
  });

  // Restore the form when returning via the browser's back button.
  window.addEventListener('pageshow', () => {
    window.clearTimeout(timer);
    overlay.hidden = true;
    submit.disabled = false;
    form.removeAttribute('aria-busy');
    pending = false;
  });
})();
