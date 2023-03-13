SELECT tidspunkt, jernbanestasjon.navn AS stasjon, motHovedretning FROM togrute 
    INNER JOIN stopperPaa USING(togruteId) 
    INNER JOIN stasjonPaaStrekning USING(sekvensnr, banestrekningId) 
    INNER JOIN jernbanestasjon USING(jernbanestasjonId)
    WHERE togruteId=3
    ORDER BY 
        CASE WHEN motHovedretning=0 THEN stopperPaa.sekvensnr END ASC,
        CASE WHEN motHovedretning=1 THEN stopperPaa.sekvensnr END DESC;