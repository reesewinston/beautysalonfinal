# Beauty Salon Booking System

A full-stack database management application designed to help beauty salons manage appointments, stylists, services, scheduling conflicts, and customer reviews.

This project was created as a senior final project for Intro to Database Management Systems Design at Spelman College.

---

## Features

- Book appointments
- Select service categories and stylists
- Prevent double booking conflicts
- View appointments using phone number lookup
- Cancel appointments
- Reschedule appointments
- Leave verified reviews after completed appointments
- Relational database design with MySQL
- Tkinter graphical user interface

---

## Technologies Used

- Python
- MySQL
- SQL
- Tkinter
- mysql-connector-python
- MySQL Workbench
- VS Code

---

## Database Design

The system uses a relational database called:

```bash
beauty_booking_system
Main Tables
clients
stylists
services
stylist_services
appointments
reviews
Relationships
One client can have many appointments
One stylist can have many appointments
Many stylists can offer many services
Reviews are linked to completed appointments only
Project Structure
beautysalon/
│
├── app.py
├── gui.py
├── queries.py
├── connection.py
├── updatedbeautysalon.sql
├── fixedconnectionerror_code.sql
└── README.md
How to Run the Project
1. Clone Repository
git clone https://github.com/reesewinston/beautysalonfinal.git
2. Open Project Folder
cd beautysalonfinal
3. Install Required Library
pip3 install mysql-connector-python

or

python3 -m pip install mysql-connector-python
Database Setup

Before running the application:

Open MySQL Workbench
Run:
updatedbeautysalon.sql
fixedconnectionerror_code.sql

These files will:

Create the database
Create tables
Insert starter data
Configure database connection settings
Run the Application
python3 app.py
Key Functionality
Booking Validation

The system prevents scheduling conflicts by checking if a stylist already has an appointment at a selected date and time.

Appointment Management

Users can:

Search appointments by phone number
Cancel appointments
Reschedule appointments
Verified Reviews

Only completed appointments can leave reviews, helping maintain accurate customer feedback.

