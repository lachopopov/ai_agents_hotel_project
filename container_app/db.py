def init_db(conn):
    # Create the rooms table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            room_number INTEGER PRIMARY KEY,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            max_capacity INTEGER NOT NULL,
            amenities TEXT
        )
    ''')

    # Create the reservations table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            room_number INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            FOREIGN KEY (room_number) REFERENCES rooms(room_number)
        )
    ''')

    # Example data for rooms
    rooms_data = [
        (101, 'Single', 100, 1, 'TV, Wi-Fi'),
        (102, 'Double', 150, 2, 'TV, Wi-Fi, Balcony'),
        (103, 'Suite', 250, 3, 'TV, Wi-Fi, Balcony, Jacuzzi'),
        (104, 'Deluxe', 200, 2, 'TV, Wi-Fi, Mini-bar'),
        (105, 'Family Suite', 300, 4,
        'TV, Wi-Fi, Balcony, Kitchenette'),
        (106, 'Executive Suite', 350, 2,
        'TV, Wi-Fi, Balcony, Jacuzzi, City View'),
        (107, 'Double', 150, 2, 'TV, Wi-Fi'),
        (108, 'Deluxe', 200, 2, 'TV, Wi-Fi, Balcony, Fireplace')
    ]

    # Insert the data
    conn.executemany('INSERT OR IGNORE INTO rooms VALUES (?, ?, ?, ?, ?)',
                    rooms_data)

    reservations_data = [
        ('Alice Smith', 102, '2025-03-15', '2025-03-18'),
        ('Bob Johnson', 105, '2025-04-22', '2025-04-25'),
        ('Charlie Brown', 106, '2025-06-10', '2025-06-12')
    ]

    # Insert the data
    conn.executemany('''INSERT INTO reservations (guest_name, room_number,
                    start_date, end_date) VALUES (?, ?, ?, ?)''',
                    reservations_data)

    conn.commit()