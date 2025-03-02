# Food Order System

## Environment Setup

### Prerequisites

- Anaconda or Miniconda installed
- Git installed

### Setup Steps

1. Clone the repository

```bash
git clone https://github.com/MengnanJiangNan/FoodOrderSystem.git
cd FoodOrderSystem
```

2. Create and activate conda environment

```bash
# Create Python 3.9 environment
conda create -n menu python=3.9 -y

# Activate environment
conda activate menu
```

3. Install dependencies

```bash
pip install -r requirement.txt
```

## Starting the Application

```bash
# Activate environment (if not already activated)
conda activate menu

# Start the application
flask run
# or
python app.py
```

The application will run at http://localhost:5000
