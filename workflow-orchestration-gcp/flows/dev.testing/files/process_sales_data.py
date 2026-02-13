import pandas as pd

def process_sales_data():
    # Create sample sales data
    data = {
        'product': ['Widget', 'Gadget', 'Doohickey'],
        'quantity': [100, 150, 200],
        'price': [10.0, 20.0, 15.0]
    }
    df = pd.DataFrame(data)
    
    # Calculate revenue
    df['revenue'] = df['quantity'] * df['price']
    
    # Save results
    df.to_csv('sales_report.csv', index=False)
    
    # Return summary
    total_revenue = df['revenue'].sum()
    return f"Total revenue: ${total_revenue:,.2f}"

if __name__ == "__main__":
    result = process_sales_data()
    print(result)