document.addEventListener('DOMContentLoaded', function() {
  // Initialize Bootstrap tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Initialize Bootstrap popovers
  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
  
  // Show/hide password toggle
  const togglePassword = document.querySelector('#togglePassword');
  const password = document.querySelector('#password');
  
  if (togglePassword && password) {
    togglePassword.addEventListener('click', function() {
      const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
      password.setAttribute('type', type);
      
      // Toggle icon
      this.querySelector('i').classList.toggle('fa-eye');
      this.querySelector('i').classList.toggle('fa-eye-slash');
    });
  }
  
  // Flight search form origin/destination swap
  const swapBtn = document.querySelector('#swapLocations');
  const originInput = document.querySelector('#origin');
  const destinationInput = document.querySelector('#destination');
  
  if (swapBtn && originInput && destinationInput) {
    swapBtn.addEventListener('click', function(e) {
      e.preventDefault();
      const temp = originInput.value;
      originInput.value = destinationInput.value;
      destinationInput.value = temp;
    });
  }
  
  // Dynamic flight status color
  const statusElements = document.querySelectorAll('.flight-status');
  if (statusElements) {
    statusElements.forEach(function(element) {
      const status = element.textContent.trim();
      if (status === 'On Time') {
        element.classList.add('status-badge', 'status-on-time');
      } else if (status === 'Delayed') {
        element.classList.add('status-badge', 'status-delayed');
      } else if (status === 'Advance') {
        element.classList.add('status-badge', 'status-advance');
      }
    });
  }
  
  // Animate wallet balance
  const walletAmount = document.querySelector('.wallet-balance .amount');
  if (walletAmount) {
    const amount = parseFloat(walletAmount.getAttribute('data-amount'));
    const currency = walletAmount.getAttribute('data-currency');
    
    // Animate from 0 to the actual amount
    const duration = 1000; // 1 second animation
    const frameDuration = 1000 / 60; // 60fps
    const totalFrames = Math.round(duration / frameDuration);
    const easeOutQuad = t => t * (2 - t);
    
    let frame = 0;
    const countTo = amount;
    const counter = setInterval(() => {
      frame++;
      const progress = easeOutQuad(frame / totalFrames);
      const currentCount = Math.round(countTo * progress * 100) / 100;
      
      if (currency === '₹') {
        walletAmount.textContent = `${currency}${currentCount.toLocaleString()}`;
      } else {
        walletAmount.textContent = `${currentCount.toLocaleString()} ${currency}`;
      }
      
      if (frame === totalFrames) {
        clearInterval(counter);
      }
    }, frameDuration);
  }
  
  // Flight search results filter
  const filterBtn = document.querySelector('#filterToggle');
  const filterContainer = document.querySelector('#filterContainer');
  
  if (filterBtn && filterContainer) {
    filterBtn.addEventListener('click', function() {
      filterContainer.classList.toggle('d-none');
      
      const icon = this.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-filter');
        icon.classList.toggle('fa-times');
      }
    });
  }
  
  // Handle booking confirmation modal
  const bookingForms = document.querySelectorAll('.booking-form');
  
  if (bookingForms) {
    bookingForms.forEach(form => {
      form.addEventListener('submit', function(e) {
        const travelClass = form.querySelector('#travel_class').value;
        const passengerName = form.querySelector('#passenger_name').value;
        
        if (!travelClass || !passengerName) {
          return; // Let form validation handle this
        }
        
        // If all info is valid, show confirmation modal
        const confirmModal = new bootstrap.Modal(document.getElementById('confirmBookingModal'));
        
        // Update modal with booking details
        document.getElementById('modal-passenger-name').textContent = passengerName;
        document.getElementById('modal-travel-class').textContent = travelClass.charAt(0).toUpperCase() + travelClass.slice(1);
        
        // Only prevent default if we want to show modal
        // e.preventDefault();
        // confirmModal.show();
      });
    });
  }
  
  // Flight details "Read More" functionality
  const readMoreBtns = document.querySelectorAll('.read-more-btn');
  
  if (readMoreBtns) {
    readMoreBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        const target = document.getElementById(this.getAttribute('data-target'));
        if (target) {
          target.classList.toggle('d-none');
          this.textContent = target.classList.contains('d-none') ? 'Read More' : 'Read Less';
        }
      });
    });
  }
  
  // Handle back to top button
  const backToTopBtn = document.getElementById('backToTop');
  
  if (backToTopBtn) {
    window.addEventListener('scroll', function() {
      if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
        backToTopBtn.style.display = 'block';
      } else {
        backToTopBtn.style.display = 'none';
      }
    });
    
    backToTopBtn.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
});

// Format dates for better display
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });
}

function formatTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Calculate flight duration
function getFlightDuration(departure, arrival) {
  const departureTime = new Date(departure);
  const arrivalTime = new Date(arrival);
  const durationMs = arrivalTime - departureTime;
  
  const hours = Math.floor(durationMs / (1000 * 60 * 60));
  const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
  
  return `${hours}h ${minutes}m`;
}

// Format price
function formatPrice(price, currency = '₹') {
  return `${currency}${parseFloat(price).toLocaleString('en-IN')}`;
}
