SELECT "Togrute 1 - Tidspunkter og stasjoner på stopp" AS "";
SELECT tidspunkt, jernbanestasjon.navn AS stasjon, motHovedretning FROM togrute 
    INNER JOIN stopp USING(togruteId) 
    INNER JOIN stasjonPaaStrekning USING(sekvensnr, banestrekningId) 
    INNER JOIN jernbanestasjon USING(jernbanestasjonId)
    WHERE togruteId=1
    ORDER BY 
        CASE WHEN motHovedretning=0 THEN stopp.sekvensnr END ASC,
        CASE WHEN motHovedretning=1 THEN stopp.sekvensnr END DESC;

SELECT "Togrute 2 - Tidspunkter og stasjoner på stopp" AS "";
SELECT tidspunkt, jernbanestasjon.navn AS stasjon, motHovedretning FROM togrute 
    INNER JOIN stopp USING(togruteId) 
    INNER JOIN stasjonPaaStrekning USING(sekvensnr, banestrekningId) 
    INNER JOIN jernbanestasjon USING(jernbanestasjonId)
    WHERE togruteId=2
    ORDER BY 
        CASE WHEN motHovedretning=0 THEN stopp.sekvensnr END ASC,
        CASE WHEN motHovedretning=1 THEN stopp.sekvensnr END DESC;

SELECT "Togrute 3 - Tidspunkter og stasjoner på stopp" AS "";
SELECT tidspunkt, jernbanestasjon.navn AS stasjon, motHovedretning FROM togrute 
    INNER JOIN stopp USING(togruteId) 
    INNER JOIN stasjonPaaStrekning USING(sekvensnr, banestrekningId) 
    INNER JOIN jernbanestasjon USING(jernbanestasjonId)
    WHERE togruteId=3
    ORDER BY 
        CASE WHEN motHovedretning=0 THEN stopp.sekvensnr END ASC,
        CASE WHEN motHovedretning=1 THEN stopp.sekvensnr END DESC;

-- SELECT "Togruter mellom to stopp" AS "";
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
