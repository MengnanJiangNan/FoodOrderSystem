---
title: Order System
emoji: 🍽️
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "latest"
app_file: app.py
pinned: false
---

# Food Order System

A web-based food ordering system built with Flask and Vue.js, designed for managing breakfast orders in a group setting.

## Features

- 🔐 Password-protected user access
- 👥 User management system
  - View existing users
  - Add new users dynamically
- 🍽️ Menu management
  - Display food items with images
  - Show prices and descriptions
- 🛒 Order management
  - Place new orders
  - Edit existing orders
  - View order history
- 💶 Price calculation
  - Real-time total calculation
  - Per-user order summary
- 🌐 Multi-language support
  - German interface

## Tech Stack

- Backend:
  - Python 3.9+
  - Flask
  - Pandas (for data management)
- Frontend:
  - Vue.js 3
  - Bootstrap 5
  - HTML5/CSS3
- Data Storage:
  - Excel files (food_orders.xlsx, menu_data.xlsx)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MengnanJiangNan/FoodOrderSystem.git
cd FoodOrderSystem
```

2. Create and activate a Python virtual environment:
```bash
# Using conda
conda create -n order-system python=3.9
conda activate order-system

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:7860
```

3. Enter the system password to access the user selection screen
   - Default password: `001`

4. Select an existing user or create a new one

5. Start placing your orders!

## Data Structure

The system uses two Excel files for data storage:

### food_orders.xlsx
- Sheet 'users': Stores user information
  - id: Unique user identifier
  - name: User name
- Sheet 'orders': Stores order information
  - user_id: Reference to user
  - food_id: Reference to menu item
  - quantity: Number of items ordered
  - price: Price per item
  - subtotal: Total price for this item

### menu_data.xlsx
- Stores menu items information
  - id: Unique item identifier
  - name: Item name
  - price: Item price
  - image: Path to item image
  - description: Item description

## Development

The project is actively maintained on both GitHub and Hugging Face:
- GitHub: https://github.com/MengnanJiangNan/FoodOrderSystem
- Hugging Face: https://huggingface.co/spaces/mengnanjiang/Order_System

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project was created as a practical solution for managing group breakfast orders. Special thanks to all contributors and users who have provided valuable feedback.