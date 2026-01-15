// Shopping Cart System
class ShoppingCart {
    constructor() {
        this.items = this.loadCart();
        this.updateCartUI();
    }

    loadCart() {
        const cartData = localStorage.getItem('shoppingCart');
        return cartData ? JSON.parse(cartData) : [];
    }

    saveCart() {
        localStorage.setItem('shoppingCart', JSON.stringify(this.items));
        this.updateCartUI();
    }

    addItem(product) {
        const existingItem = this.items.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push({
                id: product.id,
                name: product.name,
                price: product.price,
                image: product.image,
                category: product.category,
                quantity: 1
            });
        }
        
        this.saveCart();
        this.showCartNotification(product);
        this.animateCartIcon();
        return this.items;
    }

    removeItem(productId) {
        this.items = this.items.filter(item => item.id !== productId);
        this.saveCart();
    }

    updateQuantity(productId, quantity) {
        const item = this.items.find(item => item.id === productId);
        if (item) {
            if (quantity <= 0) {
                this.removeItem(productId);
            } else {
                item.quantity = quantity;
                this.saveCart();
            }
        }
    }

    getTotal() {
        return this.items.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    getItemCount() {
        return this.items.reduce((count, item) => count + item.quantity, 0);
    }

    clearCart() {
        this.items = [];
        this.saveCart();
    }

    updateCartUI() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.updateCartUI());
            return;
        }

        // Update cart icon badge
        const cartBadge = document.getElementById('cartBadge');
        if (cartBadge) {
            const count = this.getItemCount();
            cartBadge.textContent = count;
            cartBadge.style.display = count > 0 ? 'flex' : 'none';
        }

        // Update cart sidebar if open
        if (document.getElementById('cartSidebar')) {
            this.renderCartSidebar();
        }

        // Update cart page if on cart page
        if (document.getElementById('cartItems')) {
            this.renderCartPage();
        }
    }

    showCartNotification(product) {
        // Remove any existing notifications
        const existingNotification = document.querySelector('.cart-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Create notification toast
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.innerHTML = `
            <div class="cart-notification-content">
                <div class="cart-notification-icon">✓</div>
                <div class="cart-notification-info">
                    <div class="cart-notification-title">Added to Cart!</div>
                    <div class="cart-notification-product">${product.name}</div>
                    <div class="cart-notification-price">KES ${product.price.toLocaleString()}</div>
                </div>
                <img src="${product.image}" alt="${product.name}" class="cart-notification-image" onerror="this.style.display='none';">
            </div>
            <div class="cart-notification-actions">
                <a href="cart.html" class="cart-notification-link">View Cart (${this.getItemCount()})</a>
            </div>
        `;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    animateCartIcon() {
        const cartBadge = document.getElementById('cartBadge');
        const cartLink = document.querySelector('.cart-icon-link');
        
        if (cartBadge) {
            cartBadge.classList.add('cart-badge-bounce');
            setTimeout(() => {
                cartBadge.classList.remove('cart-badge-bounce');
            }, 600);
        }

        if (cartLink) {
            cartLink.classList.add('cart-icon-pulse');
            setTimeout(() => {
                cartLink.classList.remove('cart-icon-pulse');
            }, 600);
        }
    }

    renderCartSidebar() {
        const cartItems = document.getElementById('cartItems');
        const cartTotal = document.getElementById('cartTotal');
        const cartEmpty = document.getElementById('cartEmpty');

        if (!cartItems) return;

        if (this.items.length === 0) {
            cartItems.innerHTML = '';
            if (cartEmpty) cartEmpty.style.display = 'block';
            if (cartTotal) cartTotal.style.display = 'none';
            return;
        }

        if (cartEmpty) cartEmpty.style.display = 'none';
        if (cartTotal) cartTotal.style.display = 'block';

        cartItems.innerHTML = this.items.map(item => `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}" class="cart-item-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 200 200%27%3E%3Crect fill=%27%23f3f4f6%27 width=%27200%27 height=%27200%27/%3E%3Ctext fill=%27%239ca3af%27 font-family=%27sans-serif%27 font-size=%2714%27 x=%2750%25%27 y=%2750%25%27 text-anchor=%27middle%27 dy=%27.3em%27%3ENo Image%3C/text%3E%3C/svg%3E'">
                <div class="cart-item-details">
                    <h4 class="cart-item-name">${item.name}</h4>
                    <div class="cart-item-price">KES ${item.price.toLocaleString()}</div>
                    <div class="cart-item-quantity">
                        <button class="qty-btn" onclick="cart.updateQuantity(${item.id}, ${item.quantity - 1})">−</button>
                        <span class="qty-value">${item.quantity}</span>
                        <button class="qty-btn" onclick="cart.updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                    </div>
                </div>
                <button class="cart-item-remove" onclick="cart.removeItem(${item.id})" title="Remove">×</button>
            </div>
        `).join('');

        if (cartTotal) {
            cartTotal.innerHTML = `
                <div class="cart-total-row">
                    <span>Subtotal:</span>
                    <span>KES ${this.getTotal().toLocaleString()}</span>
                </div>
                <div class="cart-total-row">
                    <span>Shipping:</span>
                    <span>KES ${this.getShippingCost().toLocaleString()}</span>
                </div>
                <div class="cart-total-row total">
                    <span>Total:</span>
                    <span>KES ${(this.getTotal() + this.getShippingCost()).toLocaleString()}</span>
                </div>
                <a href="checkout.html" class="btn btn-primary" style="width: 100%; margin-top: 1rem; text-align: center; display: block;">Proceed to Checkout</a>
            `;
        }
    }

    renderCartPage() {
        const cartItems = document.getElementById('cartItems');
        const cartSummary = document.getElementById('cartSummary');

        if (!cartItems) return;

        if (this.items.length === 0) {
            cartItems.innerHTML = `
                <div class="empty-cart">
                    <h2>Your cart is empty</h2>
                    <p>Add some products to get started!</p>
                    <a href="marketplace.html" class="btn btn-primary">Continue Shopping</a>
                </div>
            `;
            if (cartSummary) cartSummary.style.display = 'none';
            return;
        }

        if (cartSummary) cartSummary.style.display = 'block';

        cartItems.innerHTML = this.items.map(item => `
            <div class="cart-page-item">
                <div class="cart-page-item-image">
                    <img src="${item.image}" alt="${item.name}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 200 200%27%3E%3Crect fill=%27%23f3f4f6%27 width=%27200%27 height=%27200%27/%3E%3Ctext fill=%27%239ca3af%27 font-family=%27sans-serif%27 font-size=%2714%27 x=%2750%25%27 y=%2750%25%27 text-anchor=%27middle%27 dy=%27.3em%27%3ENo Image%3C/text%3E%3C/svg%3E'">
                </div>
                <div class="cart-page-item-info">
                    <h3 class="cart-page-item-name">${item.name}</h3>
                    <div class="cart-page-item-category">${item.category}</div>
                    <div class="cart-page-item-price">KES ${item.price.toLocaleString()}</div>
                </div>
                <div class="cart-page-item-quantity">
                    <button class="qty-btn" onclick="cart.updateQuantity(${item.id}, ${item.quantity - 1})">−</button>
                    <input type="number" value="${item.quantity}" min="1" onchange="cart.updateQuantity(${item.id}, parseInt(this.value))" class="qty-input">
                    <button class="qty-btn" onclick="cart.updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                </div>
                <div class="cart-page-item-subtotal">
                    <div class="subtotal-label">Subtotal</div>
                    <div class="subtotal-amount">KES ${(item.price * item.quantity).toLocaleString()}</div>
                </div>
                <button class="cart-page-item-remove" onclick="cart.removeItem(${item.id})" title="Remove item">Remove</button>
            </div>
        `).join('');

        if (cartSummary) {
            const subtotal = this.getTotal();
            const shipping = this.getShippingCost();
            const total = subtotal + shipping;

            cartSummary.innerHTML = `
                <div class="cart-summary-card">
                    <h3>Order Summary</h3>
                    <div class="summary-row">
                        <span>Subtotal (${this.getItemCount()} items):</span>
                        <span>KES ${subtotal.toLocaleString()}</span>
                    </div>
                    <div class="summary-row">
                        <span>Shipping:</span>
                        <span>KES ${shipping.toLocaleString()}</span>
                    </div>
                    <div class="summary-row total">
                        <span>Total:</span>
                        <span>KES ${total.toLocaleString()}</span>
                    </div>
                    <a href="checkout.html" class="btn btn-primary" style="width: 100%; margin-top: 1.5rem; text-align: center; display: block; padding: 1rem;">Proceed to Checkout</a>
                    <a href="marketplace.html" class="btn-link" style="display: block; text-align: center; margin-top: 1rem;">Continue Shopping</a>
                </div>
            `;
        }
    }

    getShippingCost() {
        // Shipping cost: KES 500 for orders under KES 10,000, free above
        const subtotal = this.getTotal();
        return subtotal >= 10000 ? 0 : 500;
    }
}

// Initialize cart - make sure it's globally available
let cart;
if (typeof window !== 'undefined') {
    cart = new ShoppingCart();
    // Make cart available globally
    window.cart = cart;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ShoppingCart;
}
