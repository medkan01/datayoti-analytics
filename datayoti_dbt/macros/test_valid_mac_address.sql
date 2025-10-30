{% test valid_mac_address(model, column_name) %}

-- Test personnalisé pour valider le format d'une adresse MAC
-- Format attendu: XX:XX:XX:XX:XX:XX avec X = caractère hexadécimal (0-9, A-F, a-f)
-- 
-- Usage dans schema.yml:
--   tests:
--     - valid_mac_address
--
-- Ce test retourne les enregistrements qui NE RESPECTENT PAS le format attendu
-- Si aucun enregistrement n'est retourné, le test passe (toutes les MAC sont valides)

select {{ column_name }}
from {{ model }}
where {{ column_name }} is not null
  and (
    length({{ column_name }}) != 17
    or {{ column_name }} !~ '^[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}$'
  )

{% endtest %}