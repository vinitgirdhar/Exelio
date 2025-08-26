// iOS-style interactions and gestures

// Initialize iOS-style interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeIOSInteractions();
    initializeScrollEffects();
    initializeTouchGestures();
    initializeIOSNavigationEffects();
    initializeSwipeGestures();
    initializePullToRefresh();
    createIOSLoadingStates();
});

// Initialize iOS-style navigation effects
function initializeIOSNavigationEffects() {
    const navbar = document.querySelector('.navbar');
    let scrolled = false;
    
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 10 && !scrolled) {
            navbar.classList.add('scrolled');
            scrolled = true;
        } else if (currentScrollY <= 10 && scrolled) {
            navbar.classList.remove('scrolled');
            scrolled = false;
        }
    });
    
    // iOS-style navbar collapse animation
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            setTimeout(() => {
                if (navbarCollapse.classList.contains('show')) {
                    navbarCollapse.style.animation = 'slideInFromTop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                }
            }, 10);
        });
    }
}

function initializeIOSInteractions() {
    // iOS-style card interactions
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        // Mouse interactions
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.02)';
            this.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
        
        // Touch interactions for mobile
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        card.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
            this.style.transition = 'transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        });
    });

    // iOS-style button interactions
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        button.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
            this.style.transition = 'transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        });
        
        button.addEventListener('click', function(e) {
            createIOSRippleEffect(e, this);
        });
    });

    // iOS-style logo magnetic effect
    const logo = document.querySelector('.logo-icon');
    if (logo) {
        logo.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            this.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px) scale(1.1) rotate(${x * 0.1}deg)`;
            this.style.transition = 'transform 0.1s ease';
        });
        
        logo.addEventListener('mouseleave', function() {
            this.style.transform = 'translate(0, 0) scale(1) rotate(0deg)';
            this.style.transition = 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        });
    }
    
    // iOS-style form focus effects
    const formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 0 0 4px rgba(0, 122, 255, 0.1), 0 8px 20px rgba(0, 0, 0, 0.1)';
        });
        
        control.addEventListener('blur', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
}

function createIOSRippleEffect(event, element) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * 1.5;
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%);
        border-radius: 50%;
        transform: scale(0);
        animation: iosRipple 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        pointer-events: none;
        z-index: 10;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.remove();
        }
    }, 800);
}

// iOS-style swipe gestures
function initializeSwipeGestures() {
    let startX, startY, distX, distY;
    let startTime;
    
    document.addEventListener('touchstart', function(e) {
        const touch = e.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
        startTime = Date.now();
    }, { passive: true });
    
    document.addEventListener('touchend', function(e) {
        if (!startX || !startY) return;
        
        const touch = e.changedTouches[0];
        distX = touch.clientX - startX;
        distY = touch.clientY - startY;
        const elapsedTime = Date.now() - startTime;
        
        // Detect swipe gestures
        if (Math.abs(distX) > Math.abs(distY) && Math.abs(distX) > 50 && elapsedTime < 300) {
            if (distX > 0) {
                // Swipe right
                handleSwipeRight();
            } else {
                // Swipe left
                handleSwipeLeft();
            }
        }
        
        startX = null;
        startY = null;
    }, { passive: true });
}

function handleSwipeRight() {
    // Navigate back or show navigation
    console.log('Swipe right detected');
}

function handleSwipeLeft() {
    // Navigate forward or hide navigation
    console.log('Swipe left detected');
}

// iOS-style pull to refresh
function initializePullToRefresh() {
    let startY, pullDistance = 0;
    let isPulling = false;
    
    const pullIndicator = document.createElement('div');
    pullIndicator.className = 'pull-to-refresh-indicator';
    pullIndicator.innerHTML = `
        <div class="pull-refresh-spinner"></div>
        <div class="pull-refresh-text">Pull to refresh</div>
    `;
    document.body.insertBefore(pullIndicator, document.body.firstChild);
    
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
            isPulling = true;
        }
    }, { passive: true });
    
    document.addEventListener('touchmove', function(e) {
        if (!isPulling || window.scrollY > 0) return;
        
        const currentY = e.touches[0].clientY;
        pullDistance = Math.max(0, currentY - startY);
        
        if (pullDistance > 10) {
            e.preventDefault();
            const progress = Math.min(pullDistance / 100, 1);
            
            pullIndicator.style.transform = `translateY(${pullDistance - 60}px)`;
            pullIndicator.style.opacity = progress;
            
            if (pullDistance > 80) {
                pullIndicator.classList.add('ready-to-refresh');
                pullIndicator.querySelector('.pull-refresh-text').textContent = 'Release to refresh';
            } else {
                pullIndicator.classList.remove('ready-to-refresh');
                pullIndicator.querySelector('.pull-refresh-text').textContent = 'Pull to refresh';
            }
        }
    }, { passive: false });
    
    document.addEventListener('touchend', function() {
        if (!isPulling) return;
        
        if (pullDistance > 80) {
            // Trigger refresh
            pullIndicator.classList.add('refreshing');
            pullIndicator.querySelector('.pull-refresh-text').textContent = 'Refreshing...';
            
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
        
        pullIndicator.style.transform = 'translateY(-60px)';
        pullIndicator.style.opacity = '0';
        pullIndicator.classList.remove('ready-to-refresh');
        
        isPulling = false;
        pullDistance = 0;
    });
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

// CSS animations for iOS interactions
const iosStyle = document.createElement('style');
iosStyle.textContent = `
    @keyframes iosRipple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    @keyframes iosFloatParticle {
        0% {
            transform: translateY(0px) rotate(0deg);
            opacity: 0.4;
        }
        50% {
            opacity: 0.8;
        }
        100% {
            transform: translateY(-120vh) rotate(360deg);
            opacity: 0;
        }
    }
    
    @keyframes slideInFromTop {
        0% {
            transform: translateY(-20px);
            opacity: 0;
        }
        100% {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .animate-in {
        animation: slideUp 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    
    /* iOS-style cursor interactions */
    .btn, .card, .nav-link {
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .btn:active {
        transform: scale(0.95);
    }
    
    .card:active {
        transform: scale(0.98);
    }
    
    /* iOS-style table hover effects */
    .table tbody tr {
        transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .table tbody tr:hover {
        background: rgba(0, 122, 255, 0.08) !important;
        transform: translateX(4px);
    }
`;
document.head.appendChild(iosStyle);

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