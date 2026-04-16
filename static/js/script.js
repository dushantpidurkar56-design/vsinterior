document.addEventListener('DOMContentLoaded', () => {

    /* =========================================
       2. NAVBAR GLASS EFFECT ON SCROLL
    ========================================= */
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 60) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    /* =========================================
       3. HAMBURGER MOBILE MENU
    ========================================= */
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const mobileNav = document.getElementById('mobileNav');

    if (hamburgerBtn && mobileNav) {
        hamburgerBtn.addEventListener('click', () => {
            hamburgerBtn.classList.toggle('open');
            mobileNav.classList.toggle('open');
            document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
        });
        mobileNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                hamburgerBtn.classList.remove('open');
                mobileNav.classList.remove('open');
                document.body.style.overflow = '';
            });
        });
    }

    /* =========================================
       4. SMOOTH SCROLLING
    ========================================= */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const offsetTop = targetElement.getBoundingClientRect().top + window.scrollY - 80;
                window.scrollTo({ top: offsetTop, behavior: 'smooth' });
            }
        });
    });

    /* =========================================
       5. HERO SLIDER WITH KEN BURNS EFFECT
    ========================================= */
    const slides = document.querySelectorAll('.slide');
    const nextBtn = document.querySelector('.slide-btn.next');
    const prevBtn = document.querySelector('.slide-btn.prev');
    let currentSlide = 0;
    let slideInterval;

    const showSlide = (index) => {
        slides.forEach((s, i) => {
            s.classList.remove('active', 'prev-slide');
            s.querySelector('.slide-content')?.classList.remove('animate-in');
        });
        slides[index].classList.add('active');
        // Re-trigger text animation
        setTimeout(() => {
            slides[index].querySelector('.slide-content')?.classList.add('animate-in');
        }, 100);
    };

    const nextSlide = () => {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    };
    const prevSlide = () => {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(currentSlide);
    };

    if (slides.length > 0) {
        // Trigger initial text animation
        setTimeout(() => {
            slides[0].querySelector('.slide-content')?.classList.add('animate-in');
        }, 300);

        nextBtn.addEventListener('click', () => { nextSlide(); resetInterval(); });
        prevBtn.addEventListener('click', () => { prevSlide(); resetInterval(); });

        const startInterval = () => { slideInterval = setInterval(nextSlide, 6000); };
        const resetInterval = () => { clearInterval(slideInterval); startInterval(); };
        startInterval();
    }

    /* =========================================
       6. SCROLL REVEAL — INTERSECTION OBSERVER
    ========================================= */
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

    // Add reveal class to elements and observe them
    const revealSelectors = [
        '.section-header',
        '.founder-card',
        '.about-text',
        '.expertise-list',
        '.featured-title',
        '.contact-wrapper > *',
        '.footer-col',
        '.featured-section',
    ];

    revealSelectors.forEach(sel => {
        document.querySelectorAll(sel).forEach((el, i) => {
            el.classList.add('reveal-on-scroll');
            el.style.transitionDelay = `${i * 0.1}s`;
            revealObserver.observe(el);
        });
    });

    /* =========================================
       7. PROJECT CARDS — STAGGERED FADE IN
    ========================================= */
    const projectCards = document.querySelectorAll('.filter-item');
    const filterBtns = document.querySelectorAll('.filter-btn');

    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('card-revealed');
                }, entry.target.dataset.delay || 0);
                cardObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08 });

    projectCards.forEach((card, index) => {
        card.classList.add('card-hidden');
        card.dataset.delay = index * 120;
        cardObserver.observe(card);
    });

    /* =========================================
       8. PROJECT FILTERING
    ========================================= */
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const filterValue = btn.getAttribute('data-filter');
            projectCards.forEach(card => {
                if (filterValue === 'all' || card.classList.contains(filterValue)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    /* =========================================
       9. SECTION HEADING ANIMATED DIVIDER
    ========================================= */
    const dividerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('divider-animated');
                dividerObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.divider').forEach(d => dividerObserver.observe(d));

    /* =========================================
       10. MARQUEE PAUSE ON HOVER
    ========================================= */
    const marquee = document.querySelector('.marquee');
    if (marquee) {
        marquee.addEventListener('mouseenter', () => marquee.style.animationPlayState = 'paused');
        marquee.addEventListener('mouseleave', () => marquee.style.animationPlayState = 'running');
    }

    /* =========================================
       11. CINEMATIC INTRO SEQUENCE
    ========================================= */
    const introScreen = document.getElementById('intro-screen');
    const introLogo = document.getElementById('intro-logo');

    if (introScreen && introLogo) {
        // Pause body animations and scrolling
        document.body.classList.add('intro-active');
        window.scrollTo(0, 0);

        // 1. Fade in the center logo
        setTimeout(() => {
            introLogo.style.opacity = '1';
            introLogo.style.transform = 'scale(1)';
        }, 100);

        // 2. Wait 1.4s, then fade out the logo and the background
        setTimeout(() => {
            // Fade out Logo and scale it up slightly for a nice exit effect
            introLogo.style.opacity = '0';
            introLogo.style.transform = 'scale(1.05)';
            
            // Animate Screen fading to transparent
            introScreen.style.opacity = '0';
            introScreen.style.pointerEvents = 'none'; // so user can click underneath immediately

            // 3. Clean up and trigger main page load animations
            setTimeout(() => {
                introScreen.style.display = 'none';
                document.body.classList.remove('intro-active');
                
                // Re-trigger the background page load animation if desired
                document.body.style.animation = 'none';
                void document.body.offsetWidth; // trigger reflow
                document.body.style.animation = 'pageFadeIn 0.6s ease forwards';
                
            }, 1200); // Wait for the transition to finish (matches CSS 1.2s transition)

        }, 1500); // Show center logo for 1.5 seconds
    }
});
