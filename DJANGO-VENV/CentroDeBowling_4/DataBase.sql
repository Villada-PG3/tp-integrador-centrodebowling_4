create database if not exists Centro_de_Bowling_grupo_4;

UPDATE main_cliente
SET is_staff = true, is_superuser = true
WHERE main_cliente.email = 'n.pagani16@gmail.com';
