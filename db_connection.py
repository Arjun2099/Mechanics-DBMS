import psycopg2
from psycopg2 import sql

def get_db_connection():
    conn = psycopg2.connect(
        dbname="Mechanix",
        user="postgres",
        password="postgres",
        host="localhost"
    )
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # SQL to create tables (same as provided before)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Users (
        User_Id SERIAL PRIMARY KEY,
        User_Name VARCHAR(100),
        Password VARCHAR(255),
        Phone_No VARCHAR(20),
        Email VARCHAR(100),
        Address TEXT
    );

    CREATE TABLE IF NOT EXISTS Customer (
        User_Id INT PRIMARY KEY REFERENCES Users(User_Id),
        Total_Visits INT
    );

    CREATE TABLE IF NOT EXISTS Employee (
        User_Id INT PRIMARY KEY REFERENCES Users(User_Id),
        Salary NUMERIC(10, 2),
        Joining_Date DATE,
        Workshop_Id INT
    );

    CREATE TABLE IF NOT EXISTS Owner (
        User_Id INT PRIMARY KEY REFERENCES Users(User_Id),
        Total_Capita NUMERIC(15, 2)
    );

    CREATE TABLE IF NOT EXISTS Workshop (
        Workshop_Id SERIAL PRIMARY KEY,
        Workshop_Name VARCHAR(100)
    );

    CREATE TABLE IF NOT EXISTS Ownership (
        Ownership_Id SERIAL PRIMARY KEY,
        Workshop_Id INT REFERENCES Workshop(Workshop_Id),
        User_Id INT REFERENCES Users(User_Id)
    );

    CREATE TABLE IF NOT EXISTS Spare (
        Spare_Part_Id SERIAL PRIMARY KEY,
        Spare_Name VARCHAR(100),
        Workshop_Id INT REFERENCES Workshop(Workshop_Id),
        Spare_Part_No VARCHAR(50),
        Spare_Quantity_Available INT,
        Spare_Price NUMERIC(10, 2)
    );

    CREATE TABLE IF NOT EXISTS Vehicle (
        Vehicle_No VARCHAR(20) PRIMARY KEY,
        Vehicle_Type VARCHAR(50),
        Vehicle_Make VARCHAR(50),
        Vehicle_Model VARCHAR(50),
        Manufacture_Year INT,
        User_Id INT REFERENCES Users(User_Id)
    );

    CREATE TABLE IF NOT EXISTS Job (
        Job_Id SERIAL PRIMARY KEY,
        User_Id INT REFERENCES Users(User_Id),
        Workshop_Id INT REFERENCES Workshop(Workshop_Id),
        Job_Description TEXT,
        Vehicle_No VARCHAR(20) REFERENCES Vehicle(Vehicle_No),
        Dropoff_Date DATE,
        Completion_Date DATE
    );

    CREATE TABLE IF NOT EXISTS Utilized (
        Spare_Part_Id INT REFERENCES Spare(Spare_Part_Id),
        Job_Id INT REFERENCES Job(Job_Id),
        Spare_Quantity_Used INT,
        PRIMARY KEY (Spare_Part_Id, Job_Id)
    );

    CREATE TABLE IF NOT EXISTS Bill (
        Bill_Id SERIAL PRIMARY KEY,
        Job_Id INT REFERENCES Job(Job_Id),
        Date_of_issue DATE,
        Amount NUMERIC(10, 2)
    );
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
