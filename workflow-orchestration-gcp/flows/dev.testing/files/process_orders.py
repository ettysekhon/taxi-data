import pandas as pd

def process_orders():
    print("Running from GitHub-synced code via TenantSync!")
    
    data = {
        'order_id': [1, 2, 3],
        'customer': ['Alice', 'Bob', 'Charlie'],
        'amount': [150.00, 200.50, 99.99]
    }
    df = pd.DataFrame(data)
    
    df.to_csv('orders_output.csv', index=False)
    
    total = df['amount'].sum()
    print(f"✓ Total orders: ${total:,.2f}")
    return total

if __name__ == "__main__":
    process_orders()