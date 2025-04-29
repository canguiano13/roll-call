
// Set form field for date to one week from today
const dateInput = document.getElementById('event-date');
const today = new Date();
const nextWeek = new Date(today);
nextWeek.setDate(today.getDate() + 7);

const year = nextWeek.getFullYear();
const month = String(nextWeek.getMonth() + 1).padStart(2, '0');
const day = String(nextWeek.getDate()).padStart(2, '0');

dateInput.value = `${year}-${month}-${day}`;

// autofill form field for date to 6pm
const timeInput = document.getElementById('event-time');
timeInput.value = "18:00";
