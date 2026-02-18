import pandas as pd

def process_sales_data():
    print("Running from GitHub-synced code!")
    
    data = {
        'product': ['Laptop', 'Mouse', 'Keyboard'],
        'quantity': [50, 200, 150],
        'price': [999.99, 29.99, 79.99]
    }
    df = pd.DataFrame(data)
    df['revenue'] = df['quantity'] * df['price']
    
    df.to_csv('sales_output.csv', index=False)
    
    total = df['revenue'].sum()
    print(f"✓ Total revenue: ${total:,.2f}")
    return total

if __name__ == "__main__":
    process_sales_data()