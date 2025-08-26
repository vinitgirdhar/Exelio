// Apple-style interactions and gestures

// Initialize Apple-style interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAppleInteractions();
    initializeScrollEffects();
    initializeTouchGestures();
    initializeParallaxEffects();
});

function initializeAppleInteractions() {
    // Add smooth hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.transition = 'all 0.3s cubic-bezier(0.23, 1, 0.320, 1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
    });

    // Add magnetic effect to logo
    const logo = document.querySelector('.logo-icon');
    if (logo) {
        logo.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            this.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px) scale(1.05)`;
        });
        
        logo.addEventListener('mouseleave', function() {
            this.style.transform = 'translate(0, 0) scale(1)';
        });
    }
}

function createRippleEffect(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s cubic-bezier(0.23, 1, 0.320, 1);
        pointer-events: none;
        z-index: 1;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function initializeScrollEffects() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for scroll animations
    const animatedElements = document.querySelectorAll('.card, .hero-section, .feature-icon');
    animatedElements.forEach(el => observer.observe(el));
    
    // Parallax scrolling for hero section
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero-section');
        if (hero) {
            hero.style.transform = `translateY(${scrolled * 0.1}px)`;
        }
    });
}

function initializeTouchGestures() {
    // Add touch gestures for mobile devices
    let startY = 0;
    let startX = 0;
    
    document.addEventListener('touchstart', function(e) {
        startY = e.touches[0].clientY;
        startX = e.touches[0].clientX;
    }, { passive: true });
    
    document.addEventListener('touchmove', function(e) {
        const currentY = e.touches[0].clientY;
        const currentX = e.touches[0].clientX;
        const diffY = currentY - startY;
        const diffX = currentX - startX;
        
        // Add subtle transform during scroll
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            const factor = (index + 1) * 0.1;
            card.style.transform = `translateY(${diffY * factor * 0.1}px) rotateX(${diffY * factor * 0.05}deg)`;
        });
    }, { passive: true });
    
    document.addEventListener('touchend', function() {
        // Reset transforms
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.transform = '';
            card.style.transition = 'all 0.3s cubic-bezier(0.23, 1, 0.320, 1)';
        });
    }, { passive: true });
}

function initializeParallaxEffects() {
    // Create floating particles effect
    createFloatingParticles();
    
    // Add mouse parallax to navigation
    document.addEventListener('mousemove', function(e) {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            const x = (e.clientX / window.innerWidth) * 20 - 10;
            navbar.style.transform = `translateX(${x}px)`;
        }
    });
}

function createFloatingParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'floating-particles';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    `;
    
    // Create particles
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 4 + 1}px;
            height: ${Math.random() * 4 + 1}px;
            background: rgba(255, 255, 255, ${Math.random() * 0.3 + 0.1});
            border-radius: 50%;
            animation: float-particle ${Math.random() * 10 + 10}s infinite linear;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
        `;
        particleContainer.appendChild(particle);
    }
    
    document.body.appendChild(particleContainer);
}

// CSS animations for particles
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    @keyframes float-particle {
        0% {
            transform: translateY(0px) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }
    
    .animate-in {
        animation: slideUp 0.6s cubic-bezier(0.23, 1, 0.320, 1) forwards;
    }
    
    /* Apple-style cursor interactions */
    .btn, .card, .nav-link {
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.23, 1, 0.320, 1);
    }
    
    .btn:active {
        transform: scale(0.95);
    }
    
    .card:active {
        transform: scale(0.98);
    }
`;
document.head.appendChild(style);

// Add Apple-style preloader
function showAppleLoader() {
    const loader = document.createElement('div');
    loader.id = 'apple-loader';
    loader.innerHTML = `
        <div class="apple-loader-content">
            <div class="apple-logo-loader"></div>
            <div class="loading-text">Loading Exelio...</div>
        </div>
    `;
    loader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        opacity: 1;
        transition: opacity 0.5s ease;
    `;
    
    const loaderStyle = document.createElement('style');
    loaderStyle.textContent = `
        .apple-loader-content {
            text-align: center;
            color: white;
        }
        
        .apple-logo-loader {
            width: 60px;
            height: 60px;
            background: white;
            border-radius: 15px;
            margin: 0 auto 20px;
            animation: pulse 1.5s ease-in-out infinite;
            position: relative;
        }
        
        .apple-logo-loader::before {
            content: '📊';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
        }
        
        .loading-text {
            font-size: 18px;
            font-weight: 500;
            opacity: 0.8;
        }
    `;
    
    document.head.appendChild(loaderStyle);
    document.body.appendChild(loader);
    
    // Hide loader after page loads
    window.addEventListener('load', function() {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => {
                if (loader.parentNode) {
                    loader.parentNode.removeChild(loader);
                }
            }, 500);
        }, 1000);
    });
}

// Show loader immediately
if (document.readyState === 'loading') {
    showAppleLoader();
}