# 🏠 Apartment Reservation Manager

A Flask web application for managing apartment reservations from Airbnb and Booking.com platforms.

## Features

- ✅ Add, edit, and delete reservations
- 📅 Track check-in and check-out dates
- 👥 Record number of adults and children
- 📝 Store special requests and notes (check-in times, etc.)
- 🏷️ Distinguish between Airbnb and Booking.com reservations
- 📊 Dashboard view with statistics
- 🗓️ Timeline calendar view
- 🔒 **Read-only mode for cleaning crew** (view only, no editing)

## Setup Instructions for GitHub Codespaces

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Application**
   - The app will run on `http://0.0.0.0:5000`
   - In Codespaces, you'll see a notification to open the port in your browser
   - Click "Open in Browser" when prompted

## Usage

### Dashboard
- View all reservations in a table format
- See total reservations and upcoming bookings
- Quick access to edit or delete reservations

### Add Reservation
1. Click "+ Add Reservation" in the navigation
2. Fill in the form:
   - Guest name (required)
   - Platform: Airbnb or Booking.com (required)
   - Check-in and check-out dates (required)
   - Number of adults (required, minimum 1)
   - Number of children (optional)
   - Special requests (optional)
   - Notes for check-in time, parking, etc. (optional)
3. Click "Add Reservation"

### Calendar View
- Timeline view of all reservations
- Shows duration of stays
- Color-coded by platform
- Displays all guest details and notes

### Edit/Delete Reservations
- Click "Edit" button to modify reservation details
- Click "Delete" button to remove a reservation (with confirmation)

### 🔒 Read-Only Mode (For Cleaning Crew)

The app includes a special read-only mode for your cleaning crew to view reservations without the ability to modify them.

**How to use:**
1. Click "🔒 Cleaning Crew Access" in the navigation
2. Enter the password (default: `cleaning123`)
3. View all reservations, dates, and notes
4. Cannot add, edit, or delete reservations
5. Click "Exit" to return to normal mode

**Changing the password:**
- Edit line 11 in `app.py`: `READONLY_PASSWORD = 'your-new-password'`
- Or set environment variable: `export READONLY_PASSWORD=your-password`

**Share with cleaning crew:**
- Give them the app URL and the read-only password
- They'll see all reservation details including check-in times and special requests
- Perfect for scheduling cleaning between guests

## Database

The application uses SQLite database (`reservations.db`) which will be automatically created on first run. The database stores:
- Guest information
- Booking platform
- Dates
- Number of guests
- Special requests and notes

## File Structure

```
apartment-reservation-manager/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── reservations.db       # SQLite database (created on first run)
├── TUTORIAL.md           # Step-by-step building guide
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Dashboard
│   ├── add_reservation.html
│   ├── edit_reservation.html
│   ├── calendar.html     # Timeline view
│   └── readonly_login.html  # Cleaning crew login
└── static/
    └── css/
        └── style.css     # Styling
```

## Tips

- Always verify dates before adding reservations
- Use the notes field for important information like check-in times
- The platform badges help quickly identify the booking source
- Check-out date must be after check-in date
- Share read-only access with cleaning crew for scheduling

## Customization

You can customize:
- The secret key in `app.py` (line 8)
- Read-only password in `app.py` (line 11) or via environment variable
- Colors and styling in `static/css/style.css`
- Add more fields to the Reservation model if needed

## Learning Resources

New to Flask? Check out `TUTORIAL.md` for a complete step-by-step guide on how this app was built from scratch!

Enjoy managing your apartment reservations! 🎉
