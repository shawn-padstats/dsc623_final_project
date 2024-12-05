import sqlite3
import pandas as pd
import os

# Utility function to create a connection to the database
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, timeout=10)
        conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key support
        return conn
    except sqlite3.Error as e:
        print(e)
        return None

# Utility function to execute SQL queries
def execute_query(conn, query, params=()):
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True, None
    except sqlite3.Error as e:
        return False, str(e)

# Utility function to execute multiple SQL queries with parameterized data
def execute_many(conn, query, data):
    try:
        cursor = conn.cursor()
        cursor.executemany(query, data)
        conn.commit()
        return True, None
    except sqlite3.Error as e:
        return False, str(e)

# Utility function to fetch data and return a pandas DataFrame
def fetch_query(conn, query, params=()):
    df = pd.DataFrame()
    try:
        df = pd.read_sql_query(query, conn, params=params)
    except sqlite3.Error as e:
        print(f"Error fetching data: {e}")
    return df

# Utility function to print DataFrame nicely
def print_dataframe(title, df):
    print(f"\n--- {title} ---")
    if df.empty:
        print("No data found.")
    else:
        print(df.to_string(index=False))

# Function to drop existing tables
def drop_tables(conn):
    tables = ['Examination', 'Pet', 'Staff', 'Owner', 'Clinic']
    for table in tables:
        execute_query(conn, f"DROP TABLE IF EXISTS {table};")

# Function to create the database schema with constraints
def create_tables(conn):
    table_queries = {
        "Clinic": """
            CREATE TABLE IF NOT EXISTS Clinic (
                clinicNo TEXT PRIMARY KEY NOT NULL CHECK (clinicNo GLOB 'C[0-9][0-9][0-9][0-9][0-9][0-9]'),
                clinicName TEXT NOT NULL CHECK (clinicName NOT GLOB '*[0-9]*'),
                clinicAddress TEXT NOT NULL,
                clinicPhone TEXT NOT NULL UNIQUE CHECK (clinicPhone GLOB '[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
                CHECK (LENGTH(clinicPhone) = 12)
            );
        """,
        "Owner": """
            CREATE TABLE IF NOT EXISTS Owner (
                ownerNo TEXT PRIMARY KEY NOT NULL CHECK (ownerNo GLOB 'O[0-9][0-9][0-9][0-9][0-9][0-9]'),
                ownerName TEXT NOT NULL CHECK (ownerName NOT GLOB '*[0-9]*'),
                ownerAddress TEXT NOT NULL,
                ownerPhone TEXT NOT NULL UNIQUE CHECK (ownerPhone GLOB '[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
                CHECK (LENGTH(ownerPhone) = 12)
            );
        """,
        "Staff": """
            CREATE TABLE IF NOT EXISTS Staff (
                staffNo TEXT PRIMARY KEY NOT NULL CHECK (staffNo GLOB 'S[0-9][0-9][0-9][0-9][0-9][0-9]'),
                staffName TEXT NOT NULL CHECK (staffName NOT GLOB '*[0-9]*'),
                staffAddress TEXT NOT NULL,
                staffPhone TEXT NOT NULL UNIQUE CHECK (staffPhone GLOB '[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
                dateOfBirth TEXT CHECK (date(dateOfBirth) IS NOT NULL),
                position TEXT CHECK (position IN ('Veterinarian', 'Nurse', 'Technician', 'Receptionist')),
                salary REAL CHECK (salary > 0),
                clinicNo TEXT NOT NULL,
                FOREIGN KEY(clinicNo) REFERENCES Clinic(clinicNo)
            );
        """,
        "Pet": """
            CREATE TABLE IF NOT EXISTS Pet (
                petNo TEXT PRIMARY KEY NOT NULL CHECK (petNo GLOB 'P[0-9][0-9][0-9][0-9][0-9][0-9]'),
                petName TEXT NOT NULL CHECK (petName NOT GLOB '*[0-9]*'),
                petDateOfBirth TEXT NOT NULL CHECK (date(petDateOfBirth) IS NOT NULL),
                species TEXT NOT NULL CHECK(species IN ('Dog', 'Cat', 'Bird', 'Rabbit', 'Other')),
                breed TEXT,
                color TEXT,
                ownerNo TEXT NOT NULL,
                clinicNo TEXT NOT NULL,
                FOREIGN KEY(ownerNo) REFERENCES Owner(ownerNo),
                FOREIGN KEY(clinicNo) REFERENCES Clinic(clinicNo)
            );
        """,
        "Examination": """
            CREATE TABLE IF NOT EXISTS Examination (
                examNo TEXT PRIMARY KEY NOT NULL CHECK (examNo GLOB 'E[0-9][0-9][0-9][0-9][0-9][0-9]'),
                chiefComplaint TEXT NOT NULL CHECK (LENGTH(chiefComplaint) <= 500),
                description TEXT CHECK (LENGTH(description) <= 500),
                dateSeen TEXT NOT NULL CHECK (date(dateSeen) IS NOT NULL),
                actionsTaken TEXT,
                petNo TEXT NOT NULL,
                staffNo TEXT NOT NULL,
                FOREIGN KEY(petNo) REFERENCES Pet(petNo),
                FOREIGN KEY(staffNo) REFERENCES Staff(staffNo)
            );
        """
    }
    for table_name, query in table_queries.items():
        execute_query(conn, query)

def main():
    database = 'vet_clinic.db'

    # Remove existing database file to start fresh
    if os.path.exists(database):
        os.remove(database)

    conn = create_connection(database)

    if conn is not None:
        # Step a: Develop SQL code to create the entire database schema with constraints
        drop_tables(conn)  # Ensure tables are dropped before creating
        create_tables(conn)
        print("Database schema with constraints created successfully.")

        # Step b: Insert at least 5 tuples for each relation
        # Data for Clinic
        clinics = [
            ('C000001', 'Downtown Veterinary Clinic', '123 Main St, New York, NY 10001', '212-555-0101'),
            ('C000002', 'Uptown Animal Hospital', '456 Elm St, Los Angeles, CA 90001', '213-555-0202'),
            ('C000003', 'Eastside Pet Care', '789 Oak St, Chicago, IL 60601', '312-555-0303'),
            ('C000004', 'Westside Animal Clinic', '321 Pine St, Houston, TX 77001', '713-555-0404'),
            ('C000005', 'North End Vet', '654 Maple St, Phoenix, AZ 85001', '602-555-0505')
        ]
        query_clinic = "INSERT INTO Clinic (clinicNo, clinicName, clinicAddress, clinicPhone) VALUES (?, ?, ?, ?);"
        execute_many(conn, query_clinic, clinics)

        # Data for Owner
        owners = [
            ('O000001', 'John Doe', '100 First St, Boston, MA 02108', '617-555-0606'),
            ('O000002', 'Jane Smith', '200 Second St, Seattle, WA 98101', '206-555-0707'),
            ('O000003', 'Bob Johnson', '300 Third St, Miami, FL 33101', '305-555-0808'),
            ('O000004', 'Alice Williams', '400 Fourth St, Denver, CO 80201', '303-555-0909'),
            ('O000005', 'Mike Brown', '500 Fifth St, Atlanta, GA 30301', '404-555-1010')
        ]
        query_owner = "INSERT INTO Owner (ownerNo, ownerName, ownerAddress, ownerPhone) VALUES (?, ?, ?, ?);"
        execute_many(conn, query_owner, owners)

        # Data for Staff
        staff_members = [
            ('S000001', 'Dr. Emily Davis', '101 First St, New York, NY 10001', '212-555-1111', '1975-05-15', 'Veterinarian', 85000.0, 'C000001'),
            ('S000002', 'Dr. Daniel Lee', '202 Second St, Los Angeles, CA 90001', '213-555-2222', '1980-07-20', 'Veterinarian', 80000.0, 'C000002'),
            ('S000003', 'Laura Kim', '303 Third St, Chicago, IL 60601', '312-555-3333', '1985-09-25', 'Nurse', 50000.0, 'C000003'),
            ('S000004', 'Anna Brown', '404 Fourth St, Houston, TX 77001', '713-555-4444', '1990-11-30', 'Receptionist', 35000.0, 'C000004'),
            ('S000005', 'Mark Wilson', '505 Fifth St, Phoenix, AZ 85001', '602-555-5555', '1988-02-05', 'Technician', 45000.0, 'C000005')
        ]
        query_staff = """
            INSERT INTO Staff (staffNo, staffName, staffAddress, staffPhone, dateOfBirth, position, salary, clinicNo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        execute_many(conn, query_staff, staff_members)

        # Data for Pet
        pets = [
            ('P000001', 'Buddy', '2015-06-01', 'Dog', 'Golden Retriever', 'Golden', 'O000001', 'C000001'),
            ('P000002', 'Whiskers', '2017-08-15', 'Cat', 'Siamese', 'Cream', 'O000002', 'C000002'),
            ('P000003', 'Charlie', '2019-12-20', 'Rabbit', 'Dutch', 'Black and White', 'O000003', 'C000003'),
            ('P000004', 'Max', '2018-03-10', 'Dog', 'Labrador', 'Black', 'O000004', 'C000004'),
            ('P000005', 'Coco', '2020-05-05', 'Bird', 'Parakeet', 'Green', 'O000005', 'C000005')
        ]
        query_pet = """
            INSERT INTO Pet (petNo, petName, petDateOfBirth, species, breed, color, ownerNo, clinicNo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        execute_many(conn, query_pet, pets)

        # Data for Examination
        examinations = [
            ('E000001', 'Annual Checkup', 'Routine physical examination', '2023-01-15', 'Vaccinated, dewormed', 'P000001', 'S000001'),
            ('E000002', 'Coughing', 'Examined respiratory system', '2023-02-20', 'Prescribed antibiotics', 'P000002', 'S000002'),
            ('E000003', 'Limping', 'Examined left hind leg', '2023-03-25', 'Applied bandage', 'P000003', 'S000003'),
            ('E000004', 'Loss of appetite', 'Conducted blood tests', '2023-04-30', 'Recommended special diet', 'P000004', 'S000004'),
            ('E000005', 'Feather plucking', 'Behavioral assessment', '2023-05-05', 'Provided environmental enrichment suggestions', 'P000005', 'S000005')
        ]
        query_exam = """
            INSERT INTO Examination (examNo, chiefComplaint, description, dateSeen, actionsTaken, petNo, staffNo)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        execute_many(conn, query_exam, examinations)

        print("Inserted initial data into all tables.")

        # Step c: Develop the 5 SQL queries that correspond to 2c using embedded SQL.

        # Transaction 1: Add a new pet to the database
        print("\n--- Transaction 1: Add a New Pet ---")
        # New owner data
        new_owner = ('O000006', 'Karen Taylor', '606 Sixth St, Philadelphia, PA 19102', '215-555-1212')
        # New pet data
        new_pet = ('P000006', 'Bella', '2021-06-15', 'Dog', 'Poodle', 'White', 'O000006', 'C000001')

        # Check if owner exists
        owner_exists = fetch_query(conn, "SELECT * FROM Owner WHERE ownerNo = ?", (new_owner[0],))
        if owner_exists.empty:
            success, error = execute_query(conn, "INSERT INTO Owner (ownerNo, ownerName, ownerAddress, ownerPhone) VALUES (?, ?, ?, ?);", new_owner)
            if success:
                print("New owner added successfully.")
            else:
                print(f"Failed to add new owner: {error}")
        else:
            print("Owner already exists.")

        success, error = execute_query(conn, """
            INSERT INTO Pet (petNo, petName, petDateOfBirth, species, breed, color, ownerNo, clinicNo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, new_pet)
        if success:
            print("New pet added successfully.")
            # Print the new pet's details
            pet_df = fetch_query(conn, "SELECT * FROM Pet WHERE petNo = ?;", (new_pet[0],))
            print_dataframe("New Pet Details", pet_df)
        else:
            print(f"Failed to add new pet: {error}")

        # Attempt to insert erroneous data that violates constraints
        print("\n--- Attempting to Add Erroneous Pet Data (Should Fail) ---")
        erroneous_pet = ('P000007', '123InvalidName', '2021-15-15', 'Dinosaur', 'T-Rex', 'Green', 'O000007', 'C000001')
        success, error = execute_query(conn, """
            INSERT INTO Pet (petNo, petName, petDateOfBirth, species, breed, color, ownerNo, clinicNo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, erroneous_pet)
        if success:
            print("Erroneous pet added successfully (This should not happen).")
        else:
            print(f"Failed to add erroneous pet due to constraint violation: {error}")

        # Transaction 2: Record an examination for a pet
        print("\n--- Transaction 2: Record an Examination ---")
        new_exam = ('E000006', 'Skin rash', 'Examined skin for dermatitis', '2023-06-10', 'Prescribed topical ointment', 'P000006', 'S000001')

        success, error = execute_query(conn, """
            INSERT INTO Examination (examNo, chiefComplaint, description, dateSeen, actionsTaken, petNo, staffNo)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, new_exam)
        if success:
            print("New examination recorded successfully.")
            # Print the new examination details
            exam_df = fetch_query(conn, "SELECT * FROM Examination WHERE examNo = ?;", (new_exam[0],))
            print_dataframe("New Examination Details", exam_df)
        else:
            print(f"Failed to record new examination: {error}")

        # Attempt to insert erroneous examination data
        print("\n--- Attempting to Record Erroneous Examination Data (Should Fail) ---")
        erroneous_exam = ('E000007', 'Cough', 'Pet not feeling well and exhibits constant coughing.', '2023-13-40', 'No action', 'P000006', 'S000001')
        success, error = execute_query(conn, """
            INSERT INTO Examination (examNo, chiefComplaint, description, dateSeen, actionsTaken, petNo, staffNo)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, erroneous_exam)
        if success:
            print("Erroneous examination recorded successfully (This should not happen).")
        else:
            print(f"Failed to record erroneous examination due to constraint violation: {error}")

        # Transaction 3: Update a staff member's assigned clinic
        print("\n--- Transaction 3: Update Staff Clinic Assignment ---")
        success, error = execute_query(conn, """
            UPDATE Staff
            SET clinicNo = ?
            WHERE staffNo = ?;
        """, ('C000002', 'S000003'))
        if success:
            print("Staff member's clinic assignment updated.")
            # Print the updated staff member's details
            staff_df = fetch_query(conn, "SELECT * FROM Staff WHERE staffNo = ?;", ('S000003',))
            print_dataframe("Updated Staff Member Details", staff_df)
        else:
            print(f"Failed to update staff member's clinic assignment: {error}")

        # Attempt to update staff with invalid clinicNo
        print("\n--- Attempting to Update Staff with Invalid ClinicNo (Should Fail) ---")
        success, error = execute_query(conn, """
            UPDATE Staff
            SET clinicNo = ?
            WHERE staffNo = ?;
        """, ('InvalidClinicNo', 'S000003'))
        if success:
            print("Staff clinic assignment updated to invalid clinic (This should not happen).")
        else:
            print(f"Failed to update staff clinic assignment due to constraint violation: {error}")

        # Transaction 4: Retrieve all pets registered at a specific clinic
        print("\n--- Transaction 4: Retrieve Pets by Clinic ---")
        clinic_no = 'C000001'
        query = """
            SELECT petNo, petName, petDateOfBirth, species, breed, color, ownerNo
            FROM Pet
            WHERE clinicNo = ?;
        """
        df_pets = fetch_query(conn, query, (clinic_no,))
        print_dataframe(f"Pets registered at clinic {clinic_no}", df_pets)

        # Transaction 5: Generate a report of examinations conducted by a staff member
        print("\n--- Transaction 5: Generate Examination Report by Staff ---")
        staff_no = 'S000001'
        query = """
            SELECT e.examNo, e.chiefComplaint, e.description, e.dateSeen, e.actionsTaken,
                   p.petName, p.species, p.breed, p.ownerNo
            FROM Examination e
            JOIN Pet p ON e.petNo = p.petNo
            WHERE e.staffNo = ?;
        """
        df_exams = fetch_query(conn, query, (staff_no,))
        print_dataframe(f"Examinations conducted by staff member {staff_no}", df_exams)

        # Close the database connection
        conn.close()
    else:
        print("Error! Cannot create the database connection.")

if __name__ == "__main__":
    main()