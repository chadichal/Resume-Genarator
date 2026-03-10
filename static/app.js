// Dynamic form handling for resume builder
document.addEventListener('DOMContentLoaded', function() {
  const resumeLevel = document.getElementById('resume_level');
  const yearsGroup = document.getElementById('years_experience_group');
  const templateSelect = document.getElementById('template_type');

  if (resumeLevel && yearsGroup && templateSelect) {
    function toggleYearsAndTemplates() {
      const isExperienced = resumeLevel.value === 'experienced';
      yearsGroup.style.display = isExperienced ? 'block' : 'none';

      // Filter templates based on level
      const options = templateSelect.querySelectorAll('option');
      options.forEach(opt => {
        if (opt.value.startsWith('fresher_') && !isExperienced) {
          opt.disabled = false;
        } else if (opt.value.startsWith('experienced_') && isExperienced) {
          opt.disabled = false;
        } else if (opt.value !== 'fresher_' && opt.value !== 'experienced_' && opt.parentElement.label !== 'Fresher templates' && opt.parentElement.label !== 'Experienced templates') {
          opt.disabled = !isExperienced && opt.value.startsWith('experienced_') || isExperienced && opt.value.startsWith('fresher_');
        }
      });
    }

    resumeLevel.addEventListener('change', toggleYearsAndTemplates);
    toggleYearsAndTemplates(); // Initial call
  }

  // Password confirmation for register
  const password = document.getElementById('password');
  const confirmPassword = document.getElementById('confirm_password');
  const registerForm = document.getElementById('registerForm');

  if (registerForm && password && confirmPassword) {
    registerForm.addEventListener('submit', function(e) {
      if (password.value !== confirmPassword.value) {
        e.preventDefault();
        alert('Passwords do not match!');
      }
    });
  }

  // OTP functions (simulate sending)
  window.sendEmailOTP = function() {
    const email = document.getElementById('email').value;
    if (!email) return alert('Enter email first');
    // Simulate OTP generation and print to console (in real app, send via email)
    const otp = Math.floor(100000 + Math.random() * 900000);
    sessionStorage.setItem('email_otp', otp);
    console.log(`Email OTP for ${email}: ${otp}`); // Replace with actual send
    alert('OTP sent to console for testing');
  };

  window.sendPhoneOTP = function() {
    const phone = document.getElementById('phone').value;
    if (!phone) return alert('Enter phone first');
    // Simulate OTP
    const otp = Math.floor(100000 + Math.random() * 900000);
    sessionStorage.setItem('phone_otp', otp);
    console.log(`Phone OTP for ${phone}: ${otp}`); // Replace with SMS API
    alert('OTP sent to console for testing');
  };
});