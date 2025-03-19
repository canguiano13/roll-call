let slideIndex = 1;
showSlides(slideIndex); // Start the slideshow

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");

  if (n > slides.length) {
    slideIndex = 1; // Loop back to first slide
  }
  if (n < 1) {
    slideIndex = slides.length; // Loop to last slide
  }

  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none"; // Hide all slides
  }

  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }

  slides[slideIndex - 1].style.display = "block"; // Show the current slide
  dots[slideIndex - 1].className += " active";
}
