document.documentElement.classList.add("js");

const navToggle = document.querySelector("[data-nav-toggle]");
const navLinks = document.querySelector("#site-nav-links");

function setNavigationOpen(open) {
  if (!navToggle || !navLinks) return;
  navToggle.setAttribute("aria-expanded", String(open));
  navLinks.dataset.navOpen = String(open);
}

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    const open = navToggle.getAttribute("aria-expanded") !== "true";
    setNavigationOpen(open);
  });

  navLinks.addEventListener("click", (event) => {
    if (event.target.closest("a")) setNavigationOpen(false);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setNavigationOpen(false);
      navToggle.focus();
    }
  });
}

const citationButton = document.querySelector("[data-copy-citation]");
const citationCode = document.querySelector("#citation-code");
const citationStatus = document.querySelector("#citation-status");

function fallbackCopy(element) {
  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(element);
  selection.removeAllRanges();
  selection.addRange(range);
  const copied = document.execCommand("copy");
  selection.removeAllRanges();
  return copied;
}

async function copyCitation() {
  if (!citationCode || !citationStatus) return;

  const citation = citationCode.textContent.trim();

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(citation);
    } else if (!fallbackCopy(citationCode)) {
      throw new Error("Copy command was unavailable");
    }

    citationStatus.textContent = "BibTeX copied to clipboard.";
    citationButton.textContent = "Copied";
  } catch (error) {
    citationStatus.textContent = "Copy was unavailable. Select the BibTeX manually.";
    citationButton.textContent = "Select BibTeX";
  }
}

if (citationButton) {
  citationButton.addEventListener("click", copyCitation);
}
