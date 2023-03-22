SELECT 'Togrute 1 - Tidspunkter og stasjoner på stopp' AS '';
SELECT tidspunkt, jernbanestasjon.navn AS stasjon, motHovedretning FROM togrute 
    INNER JOIN stopp USING(togruteId) 
    INNER JOIN stasjonPaaStrekning USING(sekvensnr, banestrekningId) 
    INNER JOIN jernbanestasjon USING(jernbanestasjonId)
    WHERE togruteId=1
    ORDER BY 
        CASE WHEN motHovedretning=0 THEN stopp.sekvensnr END ASC,
        CASE WHEN motHovedretning=1 THEN stopp.sekvensnr END DESC;

SELECT 'Togrute 2 - Tidspunkter og stasjoner på stopp' AS '';
SELECT tidspunkt, jernbanestasjon.navn AS stasjon, motHovedretning FROM togrute 
    INNER JOIN stopp USING(togruteId) 
    INNER JOIN stasjonPaaStrekning USING(sekvensnr, banestrekningId) 
    INNER JOIN jernbanestasjon USING(jernbanestasjonId)
    WHERE togruteId=2
    ORDER BY 
        CASE WHEN motHovedretning=0 THEN stopp.sekvensnr END ASC,
        CASE WHEN motHovedretning=1 THEN stopp.sekvensnr END DESC;

SELECT 'Togrute 3 - Tidspunkter og stasjoner på stopp' AS '';
SELECT tidspunkt, jernbanestasjon.navn AS stasjon, motHovedretning FROM togrute 
    INNER JOIN stopp USING(togruteId) 
    INNER JOIN stasjonPaaStrekning USING(sekvensnr, banestrekningId) 
    INNER JOIN jernbanestasjon USING(jernbanestasjonId)
    WHERE togruteId=3
    ORDER BY 
        CASE WHEN motHovedretning=0 THEN stopp.sekvensnr END ASC,
        CASE WHEN motHovedretning=1 THEN stopp.sekvensnr END DESC;

-- SELECT 'Togruter mellom to stopp' AS '';
-- SELECT togruteid, rutenavn, operatorId, banestrekningId, motHovedretning, tidspunkt AS klokkeslett, ukedagNr, ukeNr, aar FROM togrute 
-- INNER JOIN stopp AS startstopp USING (togruteId)
-- INNER JOIN stasjonPaaStrekning USING (banestrekningId, sekvensNr)
-- INNER JOIN jernbanestasjon USING (jernbanestasjonId)
-- INNER JOIN togruteforekomst USING (togruteId)
-- WHERE (
--     jernbanestasjonId = input_startstasjonId
--     AND togruteId IN (
--         SELECT sluttstopp.togruteId FROM togrute AS t2
--         INNER JOIN stopp AS sluttstopp USING (togruteId)
--         INNER JOIN stasjonPaaStrekning USING (banestrekningId, sekvensNr)
--         INNER JOIN jernbanestasjon USING (jernbanestasjonId)
--         WHERE jernbanestasjonId = input_sluttstasjonId
--         AND (
--             (motHovedretning = 0 AND startstopp.sekvensnr <= sluttstopp.sekvensnr) 
--             OR 
--             (motHovedretning = 1 AND startstopp.sekvensnr > sluttstopp.sekvensnr)
--             )
--     )
--     AND
--     aar = input_aar 
--     AND 
--     (
--         ukeNr = input_ukeNr AND (ukedagNr = input_ukedagNr OR ukedagNr = input_ukedagNr + 1)
--         OR
--         input_ukedagNr = 7 AND ukeNr = input_ukeNr + 1 AND ukedagNr = 1
--     )
--     OR
--     aar = input_aar + 1 AND ukeNr = 1 AND ukedagNr = 1
-- )
-- ORDER BY klokkeslett, ukedagNr, ukeNr, aar;


SELECT plassNr, vognId, sekvensNrStart, sekvensNrEnde FROM billett 
INNER JOIN kundeOrdre AS bestiltKundeOrdre USING(ordreNr) 
INNER JOIN kunde AS bestiltKunde USING(kundenummer) 
INNER JOIN togruteforekomst AS bestiltTogruteforekomst USING(forekomstId)
INNER JOIN togrute AS bestiltTogrute USING(togruteId)
INNER JOIN vogn AS bestiltVogn USING(vognId);

SELECT DISTINCT vognId, startstopp.sekvensNr, endestopp.sekvensNr
FROM togruteforekomst
INNER JOIN togrute USING(togruteId)
INNER JOIN vogn USING (togruteId)
INNER JOIN stopp AS startstopp USING (togruteId)
INNER JOIN stopp AS endestopp USING (togruteId)
WHERE (startstopp.sekvensNr < endestopp.sekvensNr);
-- TODO: retning

CREATE TEMP VIEW vognmodell_plasser
AS
SELECT 
    vognModellId, 
    COALESCE(sittevognModell.seterPerRad, 0) * COALESCE(sittevognModell.stolrader, 0) + COALESCE(sovevognModell.kupeer, 0)*2 AS plasser
FROM vognModell
LEFT OUTER JOIN sittevognModell USING (vognModellId)
LEFT OUTER JOIN sovevognModell USING (vognModellId);

-- Hvilke vognModellIder har vi for togruta?
SELECT DISTINCT vognModellId FROM togrute
INNER JOIN vogn USING(togruteId)
WHERE togruteId = 1;

CREATE TEMP VIEW vogn_plasser
AS 
WITH plasser AS (
        SELECT 1 AS plassNr
        UNION ALL
        SELECT (plassNr + 1)
        FROM plasser CROSS JOIN vognmodell_plasser
        WHERE plassNr < vognmodell_plasser.plasser
        AND vognmodell_plasser.vognModellId = 1
    ) SELECT * FROM plasser;

SELECT DISTINCT 
    vogn_plasser.plassNr, 
    vognId, 
    startstopp.sekvensNr AS startNr, 
    endestopp.sekvensNr AS endeNr,
    aar,
    ukeNr,
    ukedagNr,
    motHovedretning
FROM togruteforekomst AS togruteforekomstMulig
INNER JOIN togrute USING(togruteId)
INNER JOIN vogn USING(togruteId)
INNER JOIN stopp AS startstopp USING(togruteId)
INNER JOIN stopp AS endestopp USING(togruteId)
CROSS JOIN vogn_plasser
WHERE (
    (motHovedretning = 0 AND startstopp.sekvensNr < endestopp.sekvensNr
    OR
    motHovedretning = 1 AND startstopp.sekvensNr > endestopp.sekvensNr)
    AND togruteId = 1
    AND vogn.vognModellId = 1
    AND startstopp.sekvensNr = 1
    AND endestopp.sekvensNr = 6
)
AND NOT EXISTS (
    SELECT * FROM billett 
    INNER JOIN kundeOrdre AS bestiltKundeOrdre USING(ordreNr) 
    INNER JOIN togruteforekomst AS bestiltTogruteforekomst USING(forekomstId)
    INNER JOIN togrute AS bestiltTogrute USING(togruteId)
    INNER JOIN vogn AS bestiltVogn USING(vognId)
    WHERE (startstopp.sekvensNr < billett.sekvensNrEnde AND
    billett.sekvensNrStart < endestopp.sekvensNr)
    AND bestiltTogruteforekomst.forekomstId = togruteforekomstMulig.forekomstId
    AND billett.plassNr = vogn_plasser.plassNr
    AND vogn.vognId = bestiltVogn.vognId
);

-- DONE


-- AND EXISTS (
--     SELECT plassNr, vognId, sekvensNrStart, sekvensNrEnde, forekomstId FROM billett 
--     INNER JOIN kundeOrdre AS bestiltKundeOrdre USING(ordreNr) 
--     INNER JOIN togruteforekomst AS bestiltTogruteforekomst USING(forekomstId)
--     INNER JOIN togrute AS bestiltTogrute USING(togruteId)
--     INNER JOIN vogn AS bestiltVogn USING(vognId)
--     WHERE ( (startstopp.sekvensNr < billett.sekvensNrEnde AND
--     billett.sekvensNrStart < endestopp.sekvensNr)
--     AND togruteforekomst.forekomstId = bestiltTogruteforekomst.forekomstId
--     AND billett.plassNr = vogn_plasser.plassNr
--     AND vogn.vognId = bestiltVogn.vognId
--     )
-- );


-- SELECT DISTINCT 
-- plasser.plassNr, vognId, startstopp.sekvensNr as sekvensNrStart, 
-- endestopp.sekvensNr AS sekvensNrEnde
-- FROM togruteforekomst
-- INNER JOIN togrute USING(togruteId)
-- INNER JOIN vogn USING (togruteId)
-- INNER JOIN sittevognModell AS SVM USING (vognModellId)
-- INNER JOIN stopp AS startstopp USING (togruteId)
-- INNER JOIN stopp AS endestopp USING (togruteId)
-- CROSS JOIN ( SELECT * FROM (
--     WITH plasser AS (
--         SELECT 1 AS plassNr
--         UNION ALL
--         SELECT plassNr + 1
--         FROM plasser
--         WHERE plassNr < SVM.seterPerRad
--     ) SELECT * FROM plasser) AS plasser
-- ) AS plasser
-- WHERE (startstopp.sekvensNr < endestopp.sekvensNr
-- AND forekomstId = 1)
-- AND NOT EXISTS (
--     SELECT sekvensNrStart, sekvensNrEnde FROM billett 
--     INNER JOIN kundeOrdre AS bestiltKundeOrdre USING(ordreNr) 
--     INNER JOIN kunde AS bestiltKunde USING(kundenummer) 
--     INNER JOIN togruteforekomst AS bestiltTogruteforekomst USING(forekomstId)
--     INNER JOIN togrute AS bestiltTogrute USING(togruteId)
--     INNER JOIN vogn AS bestiltVogn USING(vognId)
--     WHERE ( (startstopp.sekvensNr < billett.sekvensNrEnde AND
--     billett.sekvensNrStart < endestopp.sekvensNr)
--     AND togruteforekomst.forekomstId = bestiltTogruteforekomst.forekomstId
--     AND billett.plassNr = plasser.plassNr
--     AND vogn.vognId = bestiltVogn.vognId
--     )
-- )
-- ;

-- WHERE ( startstopp.sekvensNr < billett.sekvensNrEnde AND
-- billett.sekvensNrStart < endestopp.sekvensNr
-- )

-- SELECT DISTINCT 
-- plasser.plassNr AS plassNr, vognId, startstopp.sekvensNr as sekvensNrStart, 
-- endestopp.sekvensNr AS sekvensNrEnde
-- FROM togruteforekomst
-- INNER JOIN togrute USING(togruteId)
-- INNER JOIN vogn USING (togruteId)
-- INNER JOIN stopp AS startstopp USING (togruteId)
-- INNER JOIN stopp AS endestopp USING (togruteId)
-- CROSS JOIN (SELECT 1 plassNr UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
-- UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 
-- UNION SELECT 10 UNION SELECT 11 UNION SELECT 12) plasser
-- WHERE (startstopp.sekvensNr < endestopp.sekvensNr
-- AND forekomstId = 1) AND NOT EXISTS (
--     SELECT *
--     FROM billett 
--     INNER JOIN kundeOrdre AS bestiltKundeOrdre USING(ordreNr) 
--     INNER JOIN kunde AS bestiltKunde USING(kundenummer) 
--     INNER JOIN togruteforekomst AS bestiltTogruteforekomst USING(forekomstId)
--     INNER JOIN togrute AS bestiltTogrute USING(togruteId)
--     INNER JOIN vogn AS bestiltVogn USING(vognId)
--     WHERE startstopp.sekvensNr < billett.sekvensNrEnde AND billett.sekvensNrStart < endestopp.sekvensNr
-- );

-- SELECT * FROM vognmodell_plasser;

-- DROP VIEW IF EXISTS vognmodell_plasser;

-- CREATE TEMP VIEW plasser AS 
--     SELECT 1 AS plassNr
--     UNION ALL
--     SELECT plassNr + 1
--     FROM plasser
--     WHERE plassNr < 12;

-- SELECT * FROM plasser;

-- DROP VIEW IF EXISTS plasser;