# Marketplace Template

A modern, full-featured e-commerce marketplace template built with Django and a React-ready front end. This template provides a scalable foundation for building online stores, multi-vendor marketplaces, and more.

## Latest Updates

- **Payment integration switched from Stripe to Paystack.**
- **Currency symbol updated from dollar ($) to naira (₦).**
- **Tax rate logic updated.**

## Features

- 🛒 Product catalog with images, categories, inventory, and price management
- 👥 User authentication and profile management (including Google login via Django Allauth)
- 🛍️ Shopping cart and order processing
- 💳 Paystack integration for payment handling (formerly Stripe)
- 📦 Order history and management for users
- 📃 Responsive UI with Tailwind CSS and Bootstrap components
- 🔐 Secure password validation and CSRF protection
- ⚙️ Modular structure for easy customization and extension

## Tech Stack

- **Backend:** Django (with Django Allauth for authentication, social login)
- **Frontend:** HTML, CSS (Tailwind, Bootstrap), JavaScript (React-ready)
- **Database:** MySQL (configurable via environment variables)
- **Payments:** Paystack
- **Authentication:** Django Allauth (email/password, Google)
- **Static/Media files:** Configured for easy development and deployment

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Diawhiz/marketplace_template.git
   cd marketplace_template
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file with:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=3306
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_SECRET=your_google_secret
   PAYSTACK_PUBLIC_KEY=your_paystack_public_key
   PAYSTACK_SECRET_KEY=your_paystack_secret_key
   # STRIPE keys are deprecated
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## Usage

- Access the home page for product browsing.
- Sign up or log in (Google login supported).
- Add products to your cart, then checkout using Paystack (₦).
- View and manage orders from your user profile.
- Admin panel available at `/admin` for managing products, users, and orders.

## Project Structure

```
marketplace_template/
├── accounts/          # User management & authentication
├── products/          # Product catalog & views
├── orders/            # Shopping cart & order handling
├── payments/          # Paystack integration
├── templates/         # HTML templates (Tailwind, Bootstrap)
├── static/            # Static files (CSS, JS, images)
├── manage.py
└── requirements.txt
```

## Contributing

1. Fork the repo
2. Create your branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to your branch (`git push origin feature/my-feature`)
5. Create a pull request

## License

This project is currently unlicensed. Please add a LICENSE file if you intend to open source or distribute it.

## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Paystack](https://paystack.com/)

---

Ready to build your marketplace? 🚀
