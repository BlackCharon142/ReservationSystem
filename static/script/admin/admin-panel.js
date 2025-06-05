document.addEventListener("DOMContentLoaded", () => {
  const searchQuery = new URLSearchParams(window.location.search).get("q");

  if (searchQuery && searchQuery.trim() !== "") {
    const toggle = document.getElementById("search-accordion-toggle");
    if (toggle) {
      toggleAccordion(toggle, true); // 👈 force open
    }
  }
});

function toggleAccordion(element, forceState = null) {
    const content = element.nextElementSibling;

    if (forceState !== null) {
        // Force opening or closing based on forceState
        content.style.maxHeight = forceState ? content.scrollHeight + "px" : null;
    } else {
        // Toggle behavior
        if (content.style.maxHeight) {
            content.style.maxHeight = null;
        } else {
            // Set max-height to allow for animation
            content.style.maxHeight = content.scrollHeight + "px";
        }
    }
}
