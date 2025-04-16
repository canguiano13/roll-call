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
  // Handle dynamic slide button
  let button = document.getElementById("slide-action-button");

  if (button) {
    switch (slideIndex) {
      case 1:
        button.textContent = "View Birthday Event";
        button.onclick = () => window.location.href = "/events/birthday";
        break;
      case 2:
        button.textContent = "Explore Christmas Fun";
        button.onclick = () => window.location.href = "/events/christmas";
        break;
      case 3:
        button.textContent = "Join Halloween Bash";
        button.onclick = () => window.location.href = "/events/halloween";
        break;
      case 4:
        button.textContent = "Celebrate St. Patrick's Day";
        button.onclick = () => window.location.href = "/events/stpatrick";
        break;
      default:
        button.textContent = "Explore Event";
        button.onclick = null;
    }
  }
