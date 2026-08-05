document.addEventListener('DOMContentLoaded', function () {
  const bookingForm = document.querySelector('#bookingForm');
  if (bookingForm) {
    bookingForm.addEventListener('submit', function (event) {
      const pickup = bookingForm.querySelector('input[name="pickup"]').value.trim();
      const dropoff = bookingForm.querySelector('input[name="dropoff"]').value.trim();
      if (!pickup || !dropoff) {
        event.preventDefault();
        alert('Please provide both pickup and dropoff locations.');
      }
    });
  }
});
