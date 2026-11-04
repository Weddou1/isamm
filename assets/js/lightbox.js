/* Agrandit les photos des fiches club au clic (sans dépendance).
   Utilise <dialog> : Échap, focus et fond sont gérés par le navigateur. */
(function () {
  var shots = Array.prototype.slice.call(
    document.querySelectorAll(".shot[data-full]")
  );
  if (!shots.length || typeof HTMLDialogElement === "undefined") return;

  var dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.setAttribute("aria-label", "Photo agrandie");
  dlg.innerHTML =
    '<figure><img alt=""><figcaption></figcaption></figure>' +
    '<button type="button" class="lb-close" aria-label="Fermer">&times;</button>' +
    '<button type="button" class="lb-nav lb-prev" aria-label="Photo précédente">&#8249;</button>' +
    '<button type="button" class="lb-nav lb-next" aria-label="Photo suivante">&#8250;</button>';
  document.body.appendChild(dlg);

  var img = dlg.querySelector("img");
  var cap = dlg.querySelector("figcaption");
  var prev = dlg.querySelector(".lb-prev");
  var next = dlg.querySelector(".lb-next");
  var current = 0;
  var opener = null;

  function show(i) {
    current = (i + shots.length) % shots.length;
    var s = shots[current];
    img.src = s.getAttribute("data-full");
    img.alt = s.getAttribute("data-alt") || "";
    cap.textContent = img.alt + " (" + (current + 1) + "/" + shots.length + ")";
    var multi = shots.length > 1;
    prev.hidden = next.hidden = !multi;
  }

  function open(i) {
    opener = shots[i];
    show(i);
    dlg.showModal();
    document.documentElement.classList.add("lb-open");
  }

  shots.forEach(function (s, i) {
    s.addEventListener("click", function () { open(i); });
  });

  prev.addEventListener("click", function () { show(current - 1); });
  next.addEventListener("click", function () { show(current + 1); });
  dlg.querySelector(".lb-close").addEventListener("click", function () { dlg.close(); });

  /* clic sur le fond (hors image et boutons) = fermer */
  dlg.addEventListener("click", function (e) {
    if (e.target === dlg || e.target.tagName === "FIGURE") dlg.close();
  });

  dlg.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft") show(current - 1);
    else if (e.key === "ArrowRight") show(current + 1);
  });

  /* balayage horizontal sur mobile */
  var x0 = null;
  dlg.addEventListener("touchstart", function (e) {
    x0 = e.touches.length === 1 ? e.touches[0].clientX : null;
  }, { passive: true });
  dlg.addEventListener("touchend", function (e) {
    if (x0 === null || shots.length < 2) return;
    var dx = e.changedTouches[0].clientX - x0;
    x0 = null;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
  });

  dlg.addEventListener("close", function () {
    document.documentElement.classList.remove("lb-open");
    img.removeAttribute("src");
    if (opener) opener.focus();
  });
})();
