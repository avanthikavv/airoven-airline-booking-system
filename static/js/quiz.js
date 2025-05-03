document.addEventListener('DOMContentLoaded', function() {
  // Quiz functionality
  const quizForm = document.getElementById('quizForm');
  
  if (quizForm) {
    const radioInputs = quizForm.querySelectorAll('input[type="radio"]');
    const submitButton = quizForm.querySelector('button[type="submit"]');
    const questionElements = quizForm.querySelectorAll('.quiz-question');
    
    // Track user's choices
    let userAnswers = {
      'question_1': '',
      'question_2': '',
      'question_3': '',
      'question_4': '',
      'question_5': ''
    };
    
    // Check if all questions are answered
    function checkAllAnswered() {
      let allAnswered = true;
      for (const key in userAnswers) {
        if (userAnswers[key] === '') {
          allAnswered = false;
          break;
        }
      }
      
      // We're now using the form's submit button directly, which is always enabled
      return allAnswered;
    }
    
    // Add event listeners to radio inputs
    radioInputs.forEach(input => {
      input.addEventListener('change', function() {
        const questionName = this.name;
        const answer = this.value;
        
        userAnswers[questionName] = answer;
        
        // Mark question as answered visually
        const questionElement = this.closest('.quiz-question');
        if (questionElement) {
          questionElement.classList.add('answered');
        }
        
        checkAllAnswered();
      });
    });
    
    // Animation for quiz questions
    questionElements.forEach((question, index) => {
      setTimeout(() => {
        question.classList.add('quiz-question-visible');
      }, 300 * index);
    });
    
    // Submit handler
    quizForm.addEventListener('submit', function(e) {
      if (!checkAllAnswered()) {
        e.preventDefault();
        alert('Please answer all questions before submitting.');
      }
    });
    
    // Initialize
    checkAllAnswered();
  }
  
  // Quiz timer (optional)
  const timerElement = document.getElementById('quizTimer');
  if (timerElement) {
    let timeLeft = 300; // 5 minutes
    
    const timer = setInterval(function() {
      const minutes = Math.floor(timeLeft / 60);
      const seconds = timeLeft % 60;
      
      timerElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
      
      if (timeLeft <= 0) {
        clearInterval(timer);
        document.getElementById('quizForm').submit();
      }
      
      timeLeft--;
    }, 1000);
  }
  
  // Quiz option hover effect
  const quizOptions = document.querySelectorAll('.quiz-options label');
  
  if (quizOptions) {
    quizOptions.forEach(option => {
      option.addEventListener('mouseenter', function() {
        if (!this.classList.contains('selected')) {
          this.style.transform = 'translateX(10px)';
        }
      });
      
      option.addEventListener('mouseleave', function() {
        if (!this.classList.contains('selected')) {
          this.style.transform = 'translateX(0)';
        }
      });
      
      option.addEventListener('click', function() {
        // Remove selected class from all options in this group
        const groupOptions = this.closest('.quiz-options').querySelectorAll('label');
        groupOptions.forEach(opt => opt.classList.remove('selected'));
        
        // Add selected class to this option
        this.classList.add('selected');
      });
    });
  }
});
