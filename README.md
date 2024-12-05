# Veterinary Clinic Database Management Script

# Introduction

This script is designed to manage a veterinary clinic's database using SQLite, implemented in Python. It creates the entire database schema with all necessary constraints, inserts initial data, and performs several transactions to manipulate and query the data. The script is standalone and can be run in any Python-compatible environment.

# Features

Database Schema Creation: Develops SQL code to create the entire database schema, reflecting all specified constraints.
Data Insertion: Inserts at least 5 tuples for each relation (Clinic, Owner, Staff, Pet, Examination).
Transactions and Queries: Performs 5 transactions corresponding to common operations in a veterinary clinic, using embedded SQL.
Constraint Enforcement: Implements and demonstrates various constraints, ensuring data integrity and robustness.

# Requirements

Python Version: Python 3.6 or higher.
Required Packages:
sqlite3: Standard Python library for SQLite databases (no installation required).
pandas: For data manipulation and displaying query results in a tabular format.
Install via pip if not already installed

# How to Run the Script
Ensure Required Packages are Installed:

Verify that you have Python 3.6 or higher installed.
Install pandas if it's not already installed:
pip install pandas

Save the script code into a file named vet_clinic.py (code provided in the Complete Script section below).

Run the Script:
Open a terminal or command prompt.
Navigate to the directory containing vet_clinic.py.
Execute the script using the command:
python vet_clinic.py

Observe the Output:

The script will print the results of each transaction to the console.
Any constraint violations will be reported with error messages.
# Script Overview
# 1. Database Schema Creation with Constraints
The script defines the entire database schema with all specified constraints using SQL code within the create_tables(conn) function.

# Tables and Constraints
Clinic:

Primary Key: clinicNo
Unique Constraint: clinicPhone
Not Null Constraints: clinicNo, clinicName, clinicAddress, clinicPhone
Check Constraints:
clinicNo format: Must start with 'C' followed by 6 digits.
clinicPhone format: Must be in 'XXX-XXX-XXXX' format.
clinicName: Cannot contain numeric characters.
Owner:

Primary Key: ownerNo
Unique Constraint: ownerPhone
Not Null Constraints: ownerNo, ownerName, ownerAddress, ownerPhone
Check Constraints:
ownerNo format: Must start with 'O' followed by 6 digits.
ownerPhone format: Must be in 'XXX-XXX-XXXX' format.
ownerName: Cannot contain numeric characters.
Staff:

Primary Key: staffNo
Unique Constraint: staffPhone
Not Null Constraints: staffNo, staffName, staffAddress, staffPhone, clinicNo
Foreign Key: clinicNo references Clinic(clinicNo)
Check Constraints:
staffNo format: Must start with 'S' followed by 6 digits.
staffPhone format: Must be in 'XXX-XXX-XXXX' format.
staffName: Cannot contain numeric characters.
dateOfBirth: Must be a valid date in 'YYYY-MM-DD' format.
position: Must be one of ('Veterinarian', 'Nurse', 'Technician', 'Receptionist').
salary: Must be greater than 0.
Pet:

Primary Key: petNo
Not Null Constraints: petNo, petName, petDateOfBirth, species, ownerNo, clinicNo
Foreign Keys:
ownerNo references Owner(ownerNo)
clinicNo references Clinic(clinicNo)
Check Constraints:
petNo format: Must start with 'P' followed by 6 digits.
petName: Cannot contain numeric characters.
petDateOfBirth: Must be a valid date in 'YYYY-MM-DD' format.
species: Must be one of ('Dog', 'Cat', 'Bird', 'Rabbit', 'Other').
Examination:

Primary Key: examNo
Not Null Constraints: examNo, chiefComplaint, dateSeen, petNo, staffNo
Foreign Keys:
petNo references Pet(petNo)
staffNo references Staff(staffNo)
Check Constraints:
examNo format: Must start with 'E' followed by 6 digits.
dateSeen: Must be a valid date in 'YYYY-MM-DD' format.
chiefComplaint: Maximum length of 500 characters.
description: Maximum length of 500 characters.
Constraint Handling
Constraints are enforced using SQL CHECK constraints, UNIQUE constraints, and foreign keys. The script uses SQLite's pattern matching capabilities with GLOB to enforce formats.

# Example of Constraints in Table Creation:

CREATE TABLE IF NOT EXISTS Owner (
    ownerNo TEXT PRIMARY KEY NOT NULL CHECK (ownerNo GLOB 'O[0-9][0-9][0-9][0-9][0-9][0-9]'),
    ownerName TEXT NOT NULL CHECK (ownerName NOT GLOB '*[0-9]*'),
    ownerAddress TEXT NOT NULL,
    ownerPhone TEXT NOT NULL UNIQUE CHECK (ownerPhone GLOB '[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
    CHECK (LENGTH(ownerPhone) = 12)
);
# 2. Inserting Data into Each Relation
The script inserts at least 5 tuples into each table using predefined data within the main() function.

# Example of Data Insertion for the Clinic Table:

clinics = [
    ('C000001', 'Downtown Veterinary Clinic', '123 Main St, New York, NY 10001', '212-555-0101'),
    # ... other clinics
]
query_clinic = "INSERT INTO Clinic (clinicNo, clinicName, clinicAddress, clinicPhone) VALUES (?, ?, ?, ?);"
execute_many(conn, query_clinic, clinics)
# 3. Performing Transactions Using Embedded SQL
The script performs 5 transactions corresponding to common operations in a veterinary clinic.

# Transaction 1: Add a New Pet and Owner

Purpose: Register a new pet and its owner.

Process:
Check if the owner exists.
Insert the new owner if they do not exist.
Insert the new pet.
Handle constraint violations (e.g., invalid data).
Example Code:



# New owner data
new_owner = ('O000006', 'Karen Taylor', '606 Sixth St, Philadelphia, PA 19102', '215-555-1212')
# New pet data
new_pet = ('P000006', 'Bella', '2021-06-15', 'Dog', 'Poodle', 'White', 'O000006', 'C000001')

Insert owner and pet
# Transaction 2: Record an Examination for a Pet

Purpose: Record a new examination performed on a pet.

Process:
Insert a new examination record.
Handle constraint violations.
Example Code:



new_exam = ('E000006', 'Skin rash', 'Examined skin for dermatitis', '2023-06-10', 'Prescribed topical ointment', 'P000006', 'S000001')

Insert examination
# Transaction 3: Update a Staff Member's Assigned Clinic

Purpose: Update the clinic assignment for a staff member.

Process:
Update the clinicNo for the staff member.
Handle constraint violations (e.g., invalid clinicNo).
Example Code:



execute_query(conn, """
    UPDATE Staff
    SET clinicNo = ?
    WHERE staffNo = ?;
""", ('C000002', 'S000003'))

# Transaction 4: Retrieve All Pets Registered at a Specific Clinic

Purpose: Get a list of pets registered at a particular clinic.

Process:
Query the Pet table where clinicNo matches the specified clinic.
Example Code:



clinic_no = 'C000001'
query = """
    SELECT petNo, petName, petDateOfBirth, species, breed, color, ownerNo
    FROM Pet
    WHERE clinicNo = ?;
"""
df_pets = fetch_query(conn, query, (clinic_no,))

# Transaction 5: Generate a Report of Examinations Conducted by a Staff Member

Purpose: Generate a report of all examinations performed by a specific staff member.

Process:
Query the Examination table, joining with Pet to include pet details.
Example Code:



staff_no = 'S000001'
query = """
    SELECT e.examNo, e.chiefComplaint, e.description, e.dateSeen, e.actionsTaken,
           p.petName, p.species, p.breed, p.ownerNo
    FROM Examination e
    JOIN Pet p ON e.petNo = p.petNo
    WHERE e.staffNo = ?;
"""
df_exams = fetch_query(conn, query, (staff_no,))
# 4. Constraint Enforcement Demonstration
The script attempts to insert erroneous data that violates constraints to demonstrate constraint enforcement. It handles errors gracefully and outputs appropriate error messages.

Example of Handling Constraint Violations:



# Attempt to insert erroneous pet data
erroneous_pet = ('P000007', '123InvalidName', '2021-15-15', 'Dinosaur', 'T-Rex', 'Green', 'O000007', 'C000001')
success, error = execute_query(conn, """
    INSERT INTO Pet (petNo, petName, petDateOfBirth, species, breed, color, ownerNo, clinicNo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
""", erroneous_pet)
if success:
    print("Erroneous pet added successfully (This should not happen).")
else:
    print(f"Failed to add erroneous pet due to constraint violation: {error}")
# 5. References
SQLite3 Documentation: [sqlite3 — SQLite Database Module](https://docs.python.org/3/library/sqlite3.html)
Pandas Documentation: [Pandas Documentation](https://pandas.pydata.org/docs/)
