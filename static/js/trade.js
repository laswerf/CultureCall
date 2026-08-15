document.addEventListener('DOMContentLoaded', function () {
    const search = document.getElementById('quote-input');
    const suggestionsBox = document.getElementById('suggestions-quote');

    if (!search || !suggestionsBox) {
        return;
    }

    // This JS was written by me with the help of AI

    search.addEventListener('input', function () {
        const query = this.value.trim();

        if (query.length < 1) {
            suggestionsBox.innerHTML = '';
            suggestionsBox.classList.add('suggestions-hidden');
            return;
        }

        fetch(`/autocomplete?q=${encodeURIComponent(query)}`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then((htmlFragment) => {
                suggestionsBox.innerHTML = htmlFragment;
                suggestionsBox.classList.remove('suggestions-hidden');
            })
            .catch((error) => {
                console.error('Fetch error', error);
                suggestionsBox.innerHTML = '';
                suggestionsBox.classList.add('suggestions-hidden');
            });
    });

    document.addEventListener('click', function (event) {
        if (!search.contains(event.target) && !suggestionsBox.contains(event.target)) {
            suggestionsBox.innerHTML = '';
            suggestionsBox.classList.add('suggestions-hidden');
        }
    });
});

function selectItem(value) {
    const searchInput = document.getElementById('quote-input');
    const suggestionsBox = document.getElementById('suggestions-quote');

    if (!searchInput || !suggestionsBox) {
        return;
    }

    searchInput.value = value;
    suggestionsBox.innerHTML = '';
    suggestionsBox.classList.add('suggestions-hidden');
}