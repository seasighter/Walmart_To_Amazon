document.getElementById('inputType').addEventListener('change', function() {
    const urlInput = document.getElementById('urlInput');
    const fileInput = document.getElementById('fileInput');

    if (this.value === 'single') {
        urlInput.style.display = 'block';
        fileInput.style.display = 'none';
    } else {
        urlInput.style.display = 'none';
        fileInput.style.display = 'block';
    }
});

document.getElementById('scrapeForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    const response = await fetch('/process/', {
        method: 'POST',
        body: formData
    });

    const resultHTML = await response.text();
    document.getElementById('results').innerHTML = resultHTML;
});
