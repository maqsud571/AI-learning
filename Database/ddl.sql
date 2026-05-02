-- =========================================
-- DATABASE: Multi AI Market System
-- Description: Cars, Books, Stationery, Construction tables
-- Author: AI Project
-- =========================================



-- =========================================
-- TABLE: cars
-- Description: Avtomobillar haqidagi ma'lumotlar
-- =========================================
CREATE TABLE cars (
    id SERIAL PRIMARY KEY,          -- Unikal ID
    brand VARCHAR(100) NOT NULL,    -- Mashina brendi (Chevrolet, BMW)
    model VARCHAR(100) NOT NULL,    -- Model (Malibu, Mersedes)
    color VARCHAR(50),              -- Rangi
    year INTEGER,                   -- Ishlab chiqarilgan yil
    price FLOAT,                   -- Narxi
    quantity INTEGER               -- Ombordagi soni
);



-- =========================================
-- TABLE: books
-- Description: Kitoblar katalogi
-- =========================================
CREATE TABLE books (
    id SERIAL PRIMARY KEY,          -- Unikal ID
    title VARCHAR(255) NOT NULL,    -- Kitob nomi
    author VARCHAR(100),            -- Muallif
    genre VARCHAR(100),             -- Janr (fizika, roman, tarix)
    price FLOAT,                   -- Narxi
    quantity INTEGER               -- Soni
);



-- =========================================
-- TABLE: stationery
-- Description: Kanstovar mahsulotlari (ruchka, daftar)
-- =========================================
CREATE TABLE stationery (
    id SERIAL PRIMARY KEY,          -- Unikal ID
    name VARCHAR(255) NOT NULL,     -- Mahsulot nomi
    brand VARCHAR(100),             -- Brend
    price FLOAT,                   -- Narxi
    quantity INTEGER               -- Soni
);



-- =========================================
-- TABLE: construction
-- Description: Qurilish materiallari
-- =========================================
CREATE TABLE construction (
    id SERIAL PRIMARY KEY,          -- Unikal ID
    name VARCHAR(255) NOT NULL,     -- Material nomi (sement, g‘isht)
    material VARCHAR(100),          -- Material turi
    price FLOAT,                   -- Narxi
    quantity INTEGER               -- Soni
);