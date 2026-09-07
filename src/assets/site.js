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
