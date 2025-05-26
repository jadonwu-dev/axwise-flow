// Animation for sections on scroll
document.addEventListener('DOMContentLoaded', () => {
  // Intersection Observer for fade-in animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      }
    });
  }, {
    threshold: 0.15,
    rootMargin: '0px 0px -100px 0px'
  });

  // Observe all sections
  document.querySelectorAll('.o-section').forEach((section) => {
    observer.observe(section);
  });

  // Animated counters for stats
  function animateCounter(el, to) {
    const start = 0;
    const duration = 1500;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);
      const value = Math.floor(progress * to);

      if (to.toString().includes('-')) {
        // Handle ranges like "65-80%"
        const range = to.split('-');
        const min = parseInt(range[0]);
        const max = parseInt(range[1].replace(/\D/g, ''));
        const rangeText = `${Math.floor(progress * min)}-${Math.floor(progress * max)}%`;
        el.textContent = rangeText;
      } else {
        // Handle regular numbers
        el.textContent = value + (to.toString().includes('$') ? '$' : '');
      }

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.textContent = to;
      }
    }

    requestAnimationFrame(update);
  }

  // Process all stats when they become visible
  const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const statEl = entry.target;
        const originalValue = statEl.getAttribute('data-value') || statEl.textContent;

        // Don't animate if already animated
        if (!statEl.classList.contains('animated')) {
          animateCounter(statEl, originalValue);
          statEl.classList.add('animated');
        }

        // Unobserve after animation
        statsObserver.unobserve(statEl);
      }
    });
  }, { threshold: 0.5 });

  // Prepare all stats for animation
  document.querySelectorAll('.c-vision__stat-value').forEach(stat => {
    // Store original text as data attribute
    const originalText = stat.textContent;
    stat.setAttribute('data-value', originalText);

    // Initial value
    if (!originalText.includes('-')) {
      stat.textContent = '0';
    } else {
      stat.textContent = '0-0%';
    }

    statsObserver.observe(stat);
  });

  // Data points staggered animation
  const dataPoints = document.querySelectorAll('.c-data-point--highlight');
  dataPoints.forEach((point, index) => {
    point.style.opacity = '0';
    point.style.transform = 'translateY(20px)';
    point.style.transition = 'opacity 0.4s ease, transform 0.4s ease';

    setTimeout(() => {
      point.style.opacity = '1';
      point.style.transform = 'translateY(0)';
    }, 100 + (index * 100));
  });

  // Add smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();

      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);

      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 50,
          behavior: 'smooth'
        });
      }
    });
  });
});
