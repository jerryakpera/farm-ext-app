(function () {
  console.log('SOLID');
  const form = document.querySelector('form[data-wards-url]');

  if (!form) return;

  const lgaSelect = form.querySelector('[id$="-farm_lga"]');
  const wardSelect = form.querySelector('[id$="-farm_ward"]');
  const wardWrapper = document.getElementById('ward-field-wrapper');

  if (!lgaSelect || !wardSelect || !wardWrapper) return;

  const wardsUrlTpl = form.dataset.wardsUrl;

  async function loadWards(lgaId, selectedWardId = null) {
    wardSelect.innerHTML = '';
    wardWrapper.classList.add('hidden');

    if (!lgaId) return;

    try {
      const url = wardsUrlTpl.replace('__LGA_ID__', lgaId);
      const response = await fetch(url);

      if (!response.ok) return;

      const data = await response.json();

      if (!data.wards.length) return;

      wardSelect.appendChild(new Option('— Select ward —', ''));

      data.wards.forEach((ward) => {
        const option = new Option(ward.name, ward.id);
        if (String(ward.id) === String(selectedWardId)) {
          option.selected = true;
        }
        wardSelect.appendChild(option);
      });

      wardWrapper.classList.remove('hidden');
    } catch (err) {
      console.error('Failed to load wards:', err);
    }
  }

  lgaSelect.addEventListener('change', () => {
    console.log('LGA changed, loading wards...');
    loadWards(lgaSelect.value);
  });

  const initialLga = lgaSelect.value;
  const initialWard = wardSelect.dataset.selected ?? null;

  if (initialLga) {
    loadWards(initialLga, initialWard);
  }
})();
