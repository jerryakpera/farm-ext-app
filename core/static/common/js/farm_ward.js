const wardsUrlTpl = form.dataset.wardsUrl; // "/api/common/lgas/__LGA_ID__/wards/"
const lgaSelect = document.getElementById('id_farm_lga');
const wardSelect = document.getElementById('id_farm_ward');
const wardWrapper = document.getElementById('ward-field-wrapper');

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
  loadWards(lgaSelect.value);
});

// On edit: LGA and ward are already set — restore the full ward list
// and re-select the saved ward.
const initialLga = lgaSelect.value;
const initialWard = wardSelect.dataset.selected ?? null;

if (initialLga) {
  loadWards(initialLga, initialWard);
}
