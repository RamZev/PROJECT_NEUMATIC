SELECT codigo_postal, COUNT(*) AS repeticiones
FROM localidad
GROUP BY codigo_postal
HAVING COUNT(*) > 1;

SELECT id_provincia_id, nombre_localidad, codigo_postal 
FROM localidad
WHERE codigo_postal = "2354"
ORDER BY id_provincia_id;

SELECT 
    l.nombre_localidad,
    l.id_provincia_id AS id_provincia,
    p.nombre_provincia,
    COUNT(*) AS repeticiones
FROM 
    localidad l
JOIN 
    provincia p ON l.id_provincia_id = p.id_provincia
GROUP BY 
    l.nombre_localidad, l.id_provincia_id
HAVING 
    COUNT(*) > 1;