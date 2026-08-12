# Bus reservation system

A desktop application for searching and booking bus connections, built in Python using `tkinter` and `sqlite3`.

## Features

- User login (Admin / User role distinction)
- Search connections by direction, departure time, and date
- Book a connection with a double-click in the search results
- Overview of your own reservations
- Display of the next 5 upcoming departures and arrivals
- Automatic cleanup of past connections and reservations from the database

## Requirements

- Python 3.11 or 3.12
- `Pillow` (PIL) for image handling

Install dependencies:

```bash
pip install Pillow
```

## Database setup

The database is created and populated automatically when `riesenie.py` is run (it imports and runs `plnenie.py`, which always wipes and refills the database with fresh data — routes, departures, arrivals, test users, and sample reservations).

Test accounts:

| Username | Password | Role |
|---|---|---|
| admin | admin | Admin |
| user | user | User |
| Adrian | Adrian | User |

## Running the app

```bash
python riesenie.py
```

## How to book a connection

1. In the "Search connections" form, fill in the direction, departure time (HH:MM), and optionally the date
2. Click "Search connections" — a window with the matching results will open
3. Double-click a connection in that window to book it

## Project structure

```
├── riesenie.py           # main application (UI + logic)
├── plnenie.py           # database creation and seeding with test data
├── databaza.db           # SQLite database
└── prihlasovanie.txt           # notes on test accounts
```

## Database schema

- **uzivatelia** (users) – id, meno (name), heslo (password hash), admin (0/1)
- **linky** (routes) – id, cislo_linky (route number), ciel (destination), nazov (name)
- **odchody** (departures) – id, id_linky, datum (date), cas (time), volne_miesta (seats available)
- **prichody** (arrivals) – id, id_linky, datum (date), cas (time), volne_miesta (seats available)
- **rezervacie** (reservations) – id, id_pouzivatel (user id), id_odchodu (departure id), cas_rezervacie (booking time)

## Author

Adrian Bartoš
