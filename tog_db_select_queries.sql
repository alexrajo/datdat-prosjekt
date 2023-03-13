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