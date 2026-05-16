// Simple client-side validation
document.addEventListener("DOMContentLoaded", function() {
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function(e) {
            const inputs = form.querySelectorAll("input[required]");
            let valid = true;
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    alert("Please fill out all required fields.");
                    valid = false;
                }
            });
            if (!valid) e.preventDefault();
        });
    });
});
