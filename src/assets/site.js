document.documentElement.classList.add("js");

const menu = document.querySelector("[data-mobile-menu]");
if (menu) {
  const links = menu.querySelectorAll("a");
  links.forEach((link) => {
    link.addEventListener("click", () => {
      if (menu.open) menu.open = false;
    });
  });
}

const year = document.querySelector("[data-year]");
if (year) year.textContent = String(new Date().getFullYear());


const notesFilterBar = document.querySelector("[data-notes-filters]");
if (notesFilterBar) {
  const buttons = Array.from(notesFilterBar.querySelectorAll("[data-filter]"));
  const rows = Array.from(document.querySelectorAll(".note-teaser"));

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const wanted = button.dataset.filter || "all";
      buttons.forEach((b) => b.classList.toggle("active", b === button));
      rows.forEach((row) => {
        if (wanted === "all") {
          row.hidden = false;
          return;
        }
        const meta = (row.querySelector(".note-teaser-meta")?.textContent || "").toLowerCase();
        row.hidden = !meta.includes(wanted.toLowerCase());
      });
    });
  });
}


// MeanwhX navigator: progressive enhancement only.
// Links and labels remain fully usable without JavaScript.
const navigator = document.querySelector("[data-navigator]");
if (navigator) {
  const points = Array.from(navigator.querySelectorAll("[data-nav-code]"));
  const codeOut = navigator.querySelector("[data-nav-readout-code]");
  const titleOut = navigator.querySelector("[data-nav-readout-title]");
  const copyOut = navigator.querySelector("[data-nav-readout-copy]");

  const defaultState = {
    code: "MEANWH[x]",
    title: "The open coordinate",
    copy: "Still unresolved. This is not currently considered an emergency."
  };

  const show = (point) => {
    const code = point.dataset.navCode || defaultState.code;
    const title = point.dataset.navTitle || defaultState.title;
    const copy = point.dataset.navCopy || defaultState.copy;

    navigator.dataset.active = code;
    points.forEach((p) => p.classList.toggle("is-active", p === point));
    if (codeOut) codeOut.textContent = code;
    if (titleOut) titleOut.textContent = title;
    if (copyOut) copyOut.textContent = copy;
  };

  const reset = () => {
    delete navigator.dataset.active;
    points.forEach((p) => p.classList.remove("is-active"));
    if (codeOut) codeOut.textContent = defaultState.code;
    if (titleOut) titleOut.textContent = defaultState.title;
    if (copyOut) copyOut.textContent = defaultState.copy;
  };

  points.forEach((point) => {
    point.addEventListener("mouseenter", () => show(point));
    point.addEventListener("focus", () => show(point));
    point.addEventListener("mouseleave", reset);
    point.addEventListener("blur", reset);
  });
}
