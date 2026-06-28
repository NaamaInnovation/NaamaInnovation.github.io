const lightbox = document.querySelector("[data-lightbox]");
const lightboxImage = document.querySelector("[data-lightbox-image]");
const closeButton = document.querySelector("[data-lightbox-close]");
const galleryImages = document.querySelectorAll(".gallery-grid img");

function openLightbox(image) {
  lightboxImage.src = image.src;
  lightboxImage.alt = image.alt;
  lightbox.hidden = false;
  document.body.classList.add("lightbox-open");
  closeButton.focus();
}

function closeLightbox() {
  lightbox.hidden = true;
  lightboxImage.src = "";
  lightboxImage.alt = "";
  document.body.classList.remove("lightbox-open");
}

galleryImages.forEach((image) => {
  image.tabIndex = 0;
  image.addEventListener("click", () => openLightbox(image));
  image.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openLightbox(image);
    }
  });
});

closeButton.addEventListener("click", closeLightbox);
lightbox.addEventListener("click", (event) => {
  if (event.target === lightbox) {
    closeLightbox();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !lightbox.hidden) {
    closeLightbox();
  }
});
