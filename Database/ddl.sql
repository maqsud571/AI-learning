-- =========================================
-- TABLE: cars
-- Ushbu jadval tizimdagi avtomobillar haqidagi ma'lumotlarni saqlaydi.
-- =========================================

CREATE TABLE cars (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    color VARCHAR(50),
    year INTEGER,
    quantity INTEGER
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100),
    genre VARCHAR(100),
    price FLOAT,
    quantity INTEGER
);

CREATE TABLE stationery (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100),
    price FLOAT,
    quantity INTEGER
);

CREATE TABLE construction (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    material VARCHAR(100),
    price FLOAT,
    quantity INTEGER
);