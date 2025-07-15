document.addEventListener("DOMContentLoaded", function() {
    const diaryInput = document.getElementById("diaryInput");
    const entryInput = document.getElementById("entryInput");
    const form = document.querySelector("form");

    form.addEventListener("submit", function(e) {
        // Before submitting, copy contenteditable div content to hidden input
        entryInput.value = diaryInput.innerText.trim();
    });
});
