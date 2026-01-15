// API Configuration
const API_BASE_URL = 'http://localhost:5000/api'; // Update with your Bridge Server URL

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeHeroSlideshow();
    initializeGallery();
    initializeBookingForm();
    initializeModal();
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

    // List of image files (you can expand this list)
    const imageFiles = [
        'content_visit_cropped-Sundowner-9.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Elephants-at-waterhole.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Manyatta-Dancing-7c.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Pool-Jan-2016-8.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Main-House-Night-9.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Bush-Breakfast-Brooke-and-Kirstin-7b.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Camera-Kenya-2-336.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Manyatta-Hunting-8.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Beading-3.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Camera-Kenya-2-516.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Manyatta-Donkey-8.jpg',
        'content_visit_2016_04_04_staying-at-il-ngwesi_Beef-and-Wine-10.jpg',
        'content_visit_Il-Ngwesi-Elephant.jpg',
        'content_visit_Mukogodo-Escarpment.jpg',
        'content_visit_Dancing-at-the-Manyatta.jpg',
        'content_visit_Manyatta-Dancing-7b.jpg',
        'content_visit_Pool-Air-9.jpg',
        'content_visit_Il-Ngwesi-Board-Directors-.jpg'
    ];

    // Filter to get only full-size images (not thumbnails)
    const fullSizeImages = imageFiles.filter(img => 
        !img.includes('-300x') && 
        !img.includes('-768x') && 
        !img.includes('-1024x') &&
        !img.includes('-200x') &&
        !img.includes('-682x') &&
        !img.includes('-683x') &&
        !img.includes('-512x') &&
        !img.includes('-1152x') &&
        !img.includes('-1153x')
    );

    fullSizeImages.forEach(imageFile => {
        const galleryItem = document.createElement('div');
        galleryItem.className = 'gallery-item';
        
        const img = document.createElement('img');
        img.src = `images/${imageFile}`;
        img.alt = imageFile.replace(/\.jpg$/, '').replace(/-/g, ' ');
        img.loading = 'lazy';
        
        galleryItem.appendChild(img);
        galleryGrid.appendChild(galleryItem);
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

