import pandas as pd
from datetime import datetime, timedelta
import os

# Create sample data for the last 7 days
base_date = datetime.now() - timedelta(days=7)

locations = {
    'jembatan_merah': {'cars': 350, 'motorbikes': 1000, 'buses': 20, 'trucks': 15},
    'jl_djuanda': {'cars': 280, 'motorbikes': 900, 'buses': 25, 'trucks': 12},
    'stasiun_bogor': {'cars': 250, 'motorbikes': 850, 'buses': 30, 'trucks': 10}
}

# Generate daily data for 7 days
for location, base_counts in locations.items():
    daily_data = []
    minute_data = []
    
    for day in range(7):
        current_date = base_date + timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Daily totals with some variation
        cars = base_counts['cars'] + (day * 10)
        motorbikes = base_counts['motorbikes'] + (day * 20)
        buses = base_counts['buses'] + (day * 1)
        trucks = base_counts['trucks'] + (day * 0)
        
        daily_data.append({
            'date': date_str,
            'cars': int(cars),
            'motorbikes': int(motorbikes),
            'buses': int(buses),
            'trucks': int(trucks),
            'total': int(cars + motorbikes + buses + trucks)
        })
        
        # Per-minute data (60 records per day for hourly)
        for hour in range(24):
            time_str = f"{hour:02d}:00"
            # Add variation based on hour (traffic patterns)
            hour_factor = 0.5 + (hour / 24)
            
            minute_data.append({
                'timestamp': f"{date_str} {time_str}",
                'cars': int(cars / 24 * hour_factor),
                'motorbikes': int(motorbikes / 24 * hour_factor),
                'buses': int(buses / 24 * hour_factor),
                'trucks': int(trucks / 24 * hour_factor),
                'avg_speed_kmh': 25 + (hour % 10)
            })
    
    # Save daily CSV
    daily_path = f'data/{location}/daily.csv'
    pd.DataFrame(daily_data).to_csv(daily_path, index=False)
    print(f"✅ Created {daily_path}")
    
    # Save minute CSV
    minute_path = f'data/{location}/per_minute.csv'
    pd.DataFrame(minute_data).to_csv(minute_path, index=False)
    print(f"✅ Created {minute_path}")

print("\n✅ All sample data created successfully!")
print("\nSample data includes:")
print("- 7 days of daily traffic data")
print("- 24 hourly records per day (per-minute.csv)")
print("- 3 locations: Jembatan Merah, JL Djuanda, Stasiun Bogor")
print("- Vehicle types: Cars, Motorbikes, Buses, Trucks")
