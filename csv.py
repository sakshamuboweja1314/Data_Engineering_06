# create_sales_csv.py
# This script creates a sample sales CSV file

import pandas as pd

# Sample sales data
data = {
    'sale_id': [1, 2, 3, 4, 5],
    'customer_id': [101, 102, 103, 104, 105],
    'product_id': [201, 202, 203, 204, 205],
    'store_id': [1, 2, 3, 4, 1],
    'quantity': [2, 1, None, 3, 2],   
    'price': [150.50, None, 200.00, 300.75, 100.25],  
    'timestamp': [
        '2025-09-15 10:30:00',
        '2025-09-15 11:00:00',
        '2025-09-15 12:15:00',
        '2025-09-15 13:45:00',
        '2025-09-15 14:20:00'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('sales.csv', index=False)
print("sales.csv created successfully!")
