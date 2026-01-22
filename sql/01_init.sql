-- mettre ici le code sql puis faire tourner le server docker avec "docker-compose up -d", si t'as un problemme dit le moi

-- 01_init.sql
CREATE DATABASE IF NOT EXISTS MSPR1B1 CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE g4;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
