// API Configuration
const API_BASE_URL = 'http://localhost:5000/api'; // Update with your Bridge Server URL

// Initialize on page load
// Navbar scroll effect
function initializeNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeNavbarScroll();
    initializeHeroSlideshow();
    initializeGallery();
    initializeBookingForm();
    initializeModal();
    initializeMarketplace();
    initializeReviews();
});

// Navigation
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-menu a[href^="#"]');
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');

    // Close mobile menu function
    function closeMobileMenu() {
        if (navMenu) {
            navMenu.classList.remove('active');
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const navHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetSection.offsetTop - navHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
            
            // Close mobile menu if open
            closeMobileMenu();
        });
    });

    // Mobile menu toggle
    if (mobileToggle && navMenu) {
        function toggleMobileMenu() {
            navMenu.classList.toggle('active');
            
            // Animate hamburger icon
            const spans = mobileToggle.querySelectorAll('span');
            if (navMenu.classList.contains('active')) {
                spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                spans[1].style.opacity = '0';
                spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
                // Prevent body scroll when menu is open
                document.body.style.overflow = 'hidden';
            } else {
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
                document.body.style.overflow = '';
            }
        }

        mobileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleMobileMenu();
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navMenu.contains(e.target) && !mobileToggle.contains(e.target) && navMenu.classList.contains('active')) {
                closeMobileMenu();
                const spans = mobileToggle.querySelectorAll('span');
                spans[0].style.transform = 'none';
                spans[1].style.opacity = '1';
                spans[2].style.transform = 'none';
                document.body.style.overflow = '';
            }
        });

        // Close menu on window resize if it becomes desktop size
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (window.innerWidth > 768) {
                    closeMobileMenu();
                    const spans = mobileToggle.querySelectorAll('span');
                    spans[0].style.transform = 'none';
                    spans[1].style.opacity = '1';
                    spans[2].style.transform = 'none';
                    document.body.style.overflow = '';
                }
            }, 250);
        });
    }

    // Smooth scroll for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const navHeight = document.querySelector('.navbar').offsetHeight;
                    const targetPosition = target.offsetTop - navHeight;
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
}

// Hero Slideshow
function initializeHeroSlideshow() {
    const slides = document.querySelectorAll('.slide');
    let currentSlide = 0;

    if (slides.length === 0) return;

    function showNextSlide() {
        slides[currentSlide].classList.remove('active');
        currentSlide = (currentSlide + 1) % slides.length;
        slides[currentSlide].classList.add('active');
    }

    // Change slide every 5 seconds
    if (slides.length > 1) {
        setInterval(showNextSlide, 5000);
    }
}

// Gallery
function initializeGallery() {
    const galleryGrid = document.getElementById('galleryGrid');
    if (!galleryGrid) return;

    // List of image files with titles
    const imageData = [
        { file: 'content_visit_cropped-Sundowner-9.jpg', title: 'Sundowner Experience' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Elephants-at-waterhole.jpg', title: 'Elephants at Waterhole' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Manyatta-Dancing-7c.jpg', title: 'Traditional Maasai Dancing' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Pool-Jan-2016-8.jpg', title: 'Infinity Pool' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Main-House-Night-9.jpg', title: 'Main House at Night' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Bush-Breakfast-Brooke-and-Kirstin-7b.jpg', title: 'Bush Breakfast' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Camera-Kenya-2-336.jpg', title: 'Wildlife Photography' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Manyatta-Hunting-8.jpg', title: 'Cultural Experience' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Beading-3.jpg', title: 'Beading Workshop' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Camera-Kenya-2-516.jpg', title: 'Conservancy Views' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Manyatta-Donkey-8.jpg', title: 'Community Life' },
        { file: 'content_visit_2016_04_04_staying-at-il-ngwesi_Beef-and-Wine-10.jpg', title: 'Dining Experience' },
        { file: 'content_visit_Il-Ngwesi-Elephant.jpg', title: 'Elephant Encounter' },
        { file: 'content_visit_Mukogodo-Escarpment.jpg', title: 'Mukogodo Escarpment' },
        { file: 'content_visit_Dancing-at-the-Manyatta.jpg', title: 'Manyatta Dancing' },
        { file: 'content_visit_Manyatta-Dancing-7b.jpg', title: 'Cultural Celebration' },
        { file: 'content_visit_Pool-Air-9.jpg', title: 'Pool & Views' },
        { file: 'content_visit_Il-Ngwesi-Board-Directors-.jpg', title: 'Community Leadership' }
    ];

    // Filter to get only full-size images (not thumbnails)
    const fullSizeImages = imageData.filter(item => 
        !item.file.includes('-300x') && 
        !item.file.includes('-768x') && 
        !item.file.includes('-1024x') &&
        !item.file.includes('-200x') &&
        !item.file.includes('-682x') &&
        !item.file.includes('-683x') &&
        !item.file.includes('-512x') &&
        !item.file.includes('-1152x') &&
        !item.file.includes('-1153x')
    );

    // Create lightbox
    const lightbox = document.createElement('div');
    lightbox.className = 'gallery-lightbox';
    lightbox.innerHTML = `
        <div class="gallery-lightbox-close">×</div>
        <div class="gallery-lightbox-nav gallery-lightbox-prev">‹</div>
        <div class="gallery-lightbox-nav gallery-lightbox-next">›</div>
        <div class="gallery-lightbox-content">
            <img src="" alt="">
            <div class="gallery-lightbox-info"></div>
        </div>
    `;
    document.body.appendChild(lightbox);

    let currentImageIndex = 0;
    const images = [];

    fullSizeImages.forEach((item, index) => {
        const galleryItem = document.createElement('div');
        galleryItem.className = 'gallery-item';
        galleryItem.dataset.index = index;
        
        const img = document.createElement('img');
        img.src = `images/${item.file}`;
        img.alt = item.title;
        img.loading = 'lazy';
        
        const title = document.createElement('div');
        title.className = 'gallery-item-title';
        title.textContent = item.title;
        
        galleryItem.appendChild(img);
        galleryItem.appendChild(title);
        galleryGrid.appendChild(galleryItem);
        
        images.push({
            src: `images/${item.file}`,
            title: item.title
        });

        // Add click handler
        galleryItem.addEventListener('click', function() {
            currentImageIndex = index;
            showLightbox();
        });
    });

    function showLightbox() {
        const lightboxImg = lightbox.querySelector('img');
        const lightboxInfo = lightbox.querySelector('.gallery-lightbox-info');
        
        lightboxImg.src = images[currentImageIndex].src;
        lightboxInfo.textContent = `${currentImageIndex + 1} / ${images.length} - ${images[currentImageIndex].title}`;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function hideLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    }

    function nextImage() {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        showLightbox();
    }

    function prevImage() {
        currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
        showLightbox();
    }

    // Lightbox event handlers
    lightbox.querySelector('.gallery-lightbox-close').addEventListener('click', function(e) {
        e.stopPropagation();
        hideLightbox();
    });

    lightbox.querySelector('.gallery-lightbox-next').addEventListener('click', function(e) {
        e.stopPropagation();
        nextImage();
    });

    lightbox.querySelector('.gallery-lightbox-prev').addEventListener('click', function(e) {
        e.stopPropagation();
        prevImage();
    });

    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            hideLightbox();
        }
    });

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (lightbox.classList.contains('active')) {
            if (e.key === 'Escape') {
                hideLightbox();
            } else if (e.key === 'ArrowRight') {
                nextImage();
            } else if (e.key === 'ArrowLeft') {
                prevImage();
            }
        }
    });
}

// Booking Form
function initializeBookingForm() {
    const form = document.getElementById('bookingForm');
    const serviceCheckboxes = document.querySelectorAll('input[name="services"]');
    const numVisitorsInput = document.getElementById('numVisitors');

    // Calculate total when services or number of visitors change
    function calculateTotal() {
        let subtotal = 0;
        const numVisitors = parseInt(numVisitorsInput.value) || 0;

        serviceCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const price = parseFloat(checkbox.dataset.price);
                const serviceValue = checkbox.value;
                
                // Homestay is per night, others are per person
                if (serviceValue === 'homestay') {
                    subtotal += price; // Per night, not per person
                } else {
                    subtotal += price * numVisitors;
                }
            }
        });

        const serviceFee = subtotal * 0.05;
        const total = subtotal + serviceFee;

        document.getElementById('subtotal').textContent = `KES ${subtotal.toLocaleString()}`;
        document.getElementById('serviceFee').textContent = `KES ${serviceFee.toLocaleString()}`;
        document.getElementById('totalAmount').textContent = `KES ${total.toLocaleString()}`;
    }

    serviceCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', calculateTotal);
    });

    numVisitorsInput.addEventListener('input', calculateTotal);

    // Payment Method Selection
    const paymentMethods = document.querySelectorAll('input[name="paymentMethod"]');
    const mpesaInfo = document.getElementById('mpesaPaymentInfo');
    const cardForm = document.getElementById('cardPaymentForm');
    const paypalInfo = document.getElementById('paypalPaymentInfo');

    paymentMethods.forEach(method => {
        method.addEventListener('change', function() {
            // Hide all payment sections
            mpesaInfo.style.display = 'none';
            cardForm.style.display = 'none';
            paypalInfo.style.display = 'none';

            // Show selected payment method
            if (this.value === 'mpesa') {
                mpesaInfo.style.display = 'block';
            } else if (this.value === 'card') {
                cardForm.style.display = 'block';
            } else if (this.value === 'paypal') {
                paypalInfo.style.display = 'block';
            }
        });
    });

    // Card Number Formatting
    const cardNumberInput = document.getElementById('cardNumber');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            // Limit to 16 digits
            value = value.substring(0, 16);
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formattedValue;
        });

        // Prevent non-numeric input
        cardNumberInput.addEventListener('keypress', function(e) {
            if (!/[0-9\s]/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }

    // Card Expiry Formatting
    const cardExpiryInput = document.getElementById('cardExpiry');
    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            // Limit to 4 digits
            value = value.substring(0, 4);
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });

        // Validate month
        cardExpiryInput.addEventListener('blur', function(e) {
            const value = e.target.value;
            if (value.length >= 2) {
                const month = parseInt(value.substring(0, 2));
                if (month < 1 || month > 12) {
                    e.target.setCustomValidity('Please enter a valid month (01-12)');
                } else {
                    e.target.setCustomValidity('');
                }
            }
        });
    }

    // Card CVC - Numbers only
    const cardCVCInput = document.getElementById('cardCVC');
    if (cardCVCInput) {
        cardCVCInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
        });
    }

    // Set minimum date to today for arrival date
    const arrivalDateInput = document.getElementById('arrivalDate');
    if (arrivalDateInput) {
        const today = new Date().toISOString().split('T')[0];
        arrivalDateInput.setAttribute('min', today);
    }

    // Statistics Counter Animation
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, 16);
    }

    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                
                // Animate statistics if it's a stat card
                if (entry.target.classList.contains('stat-card')) {
                    const statNumber = entry.target.querySelector('.stat-number');
                    if (statNumber && !statNumber.classList.contains('animated')) {
                        const target = parseInt(statNumber.getAttribute('data-target'));
                        statNumber.classList.add('animated');
                        animateCounter(statNumber, target);
                    }
                }
            }
        });
    }, observerOptions);

    // Observe all sections and cards
    document.querySelectorAll('.section, .step-card, .service-card, .stat-card, .revenue-item').forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validate form
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        // Get selected payment method
        const selectedPaymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;

        // Validate card fields if card payment selected
        if (selectedPaymentMethod === 'card') {
            const cardNumber = document.getElementById('cardNumber').value.replace(/\s/g, '');
            const cardExpiry = document.getElementById('cardExpiry').value;
            const cardCVC = document.getElementById('cardCVC').value;
            const cardName = document.getElementById('cardName').value;

            if (!cardNumber || cardNumber.length < 13) {
                alert('Please enter a valid card number');
                return;
            }
            if (!cardExpiry || !/^\d{2}\/\d{2}$/.test(cardExpiry)) {
                alert('Please enter a valid expiry date (MM/YY)');
                return;
            }
            if (!cardCVC || cardCVC.length < 3) {
                alert('Please enter a valid CVC');
                return;
            }
            if (!cardName) {
                alert('Please enter cardholder name');
                return;
            }
        }

        // Get form data
        const formData = {
            touristName: document.getElementById('touristName').value,
            touristEmail: document.getElementById('touristEmail').value,
            touristPhone: document.getElementById('touristPhone').value,
            arrivalDate: document.getElementById('arrivalDate').value,
            numVisitors: parseInt(document.getElementById('numVisitors').value),
            services: Array.from(document.querySelectorAll('input[name="services"]:checked')).map(cb => cb.value),
            specialRequests: document.getElementById('specialRequests').value,
            totalAmount: parseFloat(document.getElementById('totalAmount').textContent.replace(/[KES\s,]/g, '')),
            paymentMethod: selectedPaymentMethod
        };

        // Add card details if card payment
        if (selectedPaymentMethod === 'card') {
            formData.cardNumber = document.getElementById('cardNumber').value.replace(/\s/g, '');
            formData.cardExpiry = document.getElementById('cardExpiry').value;
            formData.cardCVC = document.getElementById('cardCVC').value;
            formData.cardName = document.getElementById('cardName').value;
        }

        // Show loading state
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.classList.add('loading');
        submitButton.disabled = true;

        try {
            // Send booking to API
            const response = await fetch(`${API_BASE_URL}/booking`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                // Show success modal
                document.getElementById('bookingCode').textContent = result.booking_code;
                document.getElementById('bookingModal').style.display = 'block';
                
                // Reset form
                form.reset();
                calculateTotal();
            } else {
                throw new Error(result.error || 'Booking failed');
            }
        } catch (error) {
            console.error('Booking error:', error);
            alert('There was an error submitting your booking. Please try again or contact us directly.');
        } finally {
            submitButton.classList.remove('loading');
            submitButton.disabled = false;
        }
    });
}

// Modal
function initializeModal() {
    const modal = document.getElementById('bookingModal');
    const closeBtn = document.querySelector('.modal-close');

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }

    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Utility function to generate booking code (fallback if API doesn't)
function generateBookingCode() {
    const date = new Date();
    const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '');
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `V${dateStr}-${random}`;
}

// Marketplace Tabs
function initializeMarketplace() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            const targetContent = document.getElementById(`${targetTab}-tab`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// Add to Cart / Book Experience
function addToCart(productType) {
    alert(`Added ${productType} to cart! (This is a demo - cart functionality will be implemented)`);
}

function bookExperience(experienceType) {
    // Scroll to booking form and pre-select the experience
    const bookingSection = document.getElementById('booking');
    if (bookingSection) {
        bookingSection.scrollIntoView({ behavior: 'smooth' });
    }
    alert(`Redirecting to booking for ${experienceType} experience!`);
}

// Reviews Form
function initializeReviews() {
    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                reviewerName: document.getElementById('reviewerName').value,
                rating: document.getElementById('reviewRating').value,
                reviewText: document.getElementById('reviewText').value
            };

            // In a real implementation, this would send to the backend
            console.log('Review submitted:', formData);
            alert('Thank you for your review! It will be published after moderation.');
            reviewForm.reset();
        });
    }
}

