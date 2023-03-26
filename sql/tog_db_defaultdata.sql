PRAGMA foreign_keys = ON;

-- Insert data into database --
INSERT INTO jernbanestasjon (navn, moh) VALUES ('Trondheim', 5.1);
INSERT INTO jernbanestasjon (navn, moh) VALUES ('Steinkjer', 3.6);
INSERT INTO jernbanestasjon (navn, moh) VALUES ('Mosjøen', 6.8);
INSERT INTO jernbanestasjon (navn, moh) VALUES ('Mo i rana', 3.5);
INSERT INTO jernbanestasjon (navn, moh) VALUES ('Fauske', 34);
INSERT INTO jernbanestasjon (navn, moh) VALUES ('Bodø', 4.1);

INSERT INTO delstrekning VALUES (1, 2, 120, true);
INSERT INTO delstrekning VALUES (2, 3, 280, false);
INSERT INTO delstrekning VALUES (3, 4, 90, false);
INSERT INTO delstrekning VALUES (4, 5, 170, false);
INSERT INTO delstrekning VALUES (5, 6, 60, false);

INSERT INTO banestrekning (navn, brukerDiesel) VALUES ('Nordlandsbanen', true);

INSERT INTO stasjonPaaStrekning VALUES (1, 1, 1);
INSERT INTO stasjonPaaStrekning VALUES (1, 2, 2);
INSERT INTO stasjonPaaStrekning VALUES (1, 3, 3);
INSERT INTO stasjonPaaStrekning VALUES (1, 4, 4);
INSERT INTO stasjonPaaStrekning VALUES (1, 5, 5);
INSERT INTO stasjonPaaStrekning VALUES (1, 6, 6);

INSERT INTO operator (navn) VALUES ('SJ');

INSERT INTO togrute (operatorId, banestrekningId, rutenavn) VALUES (1, 1, 'Dagtog fra Trondheim til Bodø');
INSERT INTO togrute (operatorId, banestrekningId, rutenavn) VALUES (1, 1, 'Nattog fra Trondheim til Bodø');
INSERT INTO togrute (operatorId, banestrekningId, rutenavn, motHovedretning) VALUES (1, 1, 'Morgentog fra Mo i Rana til Trondheim', 1);

-- Togrute 1
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (1, 1, 1, '07:49:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (1, 2, 1, '09:51:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (1, 3, 1, '13:20:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (1, 4, 1, '14:31:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (1, 5, 1, '16:49:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (1, 6, 1, '17:34:00');

-- Togrute 2
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (2, 1, 1, '23:05:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt, dagOffset) VALUES (2, 2, 1, '00:57:00', 1);
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt, dagOffset) VALUES (2, 3, 1, '04:41:00', 1);
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt, dagOffset) VALUES (2, 4, 1, '05:55:00', 1);
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt, dagOffset) VALUES (2, 5, 1, '08:19:00', 1);
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt, dagOffset) VALUES (2, 6, 1, '09:05:00', 1);

-- Togrute 3
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (3, 4, 1, '08:11:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (3, 3, 1, '09:14:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (3, 2, 1, '12:31:00');
INSERT INTO stopp (togruteId, sekvensnr, banestrekningId, tidspunkt) VALUES (3, 1, 1, '14:13:00');

-- Vognmodeller
INSERT INTO vognModell (modellNavn) VALUES ('SJ-sittevogn-1');
INSERT INTO sittevognModell (vognModellId, stolrader, seterPerRad) VALUES (1, 3, 4);

INSERT INTO vognModell (modellNavn) VALUES ('SJ-sovevogn-1');
INSERT INTO sovevognModell (vognModellId, kupeer) VALUES (2, 4);

-- Vogner
    --dagtog
INSERT INTO vogn (vognModellId, operatorId, togruteId, vognnr) VALUES (1, 1, 1, 1);
INSERT INTO vogn (vognModellId, operatorId, togruteId, vognnr) VALUES (1, 1, 1, 2);
    --nattog
INSERT INTO vogn (vognModellId, operatorId, togruteId, vognnr) VALUES (1, 1, 2, 1);
INSERT INTO vogn (vognModellId, operatorId, togruteId, vognnr) VALUES (2, 1, 2, 2);
    --morgentog
INSERT INTO vogn (vognModellId, operatorId, togruteId, vognnr) VALUES (1, 1, 3, 1);

-- Ruteforekomster
-- For togrute 1
INSERT INTO ukedag VALUES (1, 1);
INSERT INTO ukedag VALUES (1, 2);
INSERT INTO ukedag VALUES (1, 3);
INSERT INTO ukedag VALUES (1, 4);
INSERT INTO ukedag VALUES (1, 5);

-- For togrute 2
INSERT INTO ukedag VALUES (2, 1);
INSERT INTO ukedag VALUES (2, 2);
INSERT INTO ukedag VALUES (2, 3);
INSERT INTO ukedag VALUES (2, 4);
INSERT INTO ukedag VALUES (2, 5);
INSERT INTO ukedag VALUES (2, 6);
INSERT INTO ukedag VALUES (2, 7);

-- For togrute 3
INSERT INTO ukedag VALUES (3, 1);
INSERT INTO ukedag VALUES (3, 2);
INSERT INTO ukedag VALUES (3, 3);
INSERT INTO ukedag VALUES (3, 4);
INSERT INTO ukedag VALUES (3, 5);


-- Forekomster (1. dag i uke 14 2023 = 3. april 2023)
-- Togrute 1
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (1, 1, 14, 2023);
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (1, 2, 14, 2023);

-- Togrute 2 (har litt ekstra forekomster, for moro skyld / testing)
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (2, 1, 14, 2023);
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (2, 2, 14, 2023);
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (2, 7, 14, 2023);
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (2, 1, 15, 2023);

INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (2, 1, 12, 2023);
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (2, 7, 12, 2023);
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (2, 6, 12, 2023);
-- Togrute 3
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (3, 1, 14, 2023);
INSERT INTO togruteforekomst (togruteId, ukedagNr, ukeNr, aar) VALUES (3, 2, 14, 2023);

-- Ny kunde
INSERT INTO kunde (fornavn, etternavn, email, mobilnummer) VALUES ('Johan', 'Golden', 'johang@example.com', 98765432);

-- Ny kundeordre for togrute 1
INSERT INTO kundeOrdre (kundenummer, forekomstId) VALUES (1, 2);
INSERT INTO billett (ordreNr, togruteId, vognId, plassNr, sekvensNrStart, sekvensNrEnde) VALUES (1, 
    (SELECT togruteId FROM kundeOrdre INNER JOIN togruteforekomst USING (forekomstId) WHERE ordreNr=1)
, 1, 3, 2, 4);

INSERT INTO kundeOrdre (kundenummer, forekomstId) VALUES (1, 7);
INSERT INTO billett (ordreNr, togruteId, vognId, plassNr, sekvensNrStart, sekvensNrEnde) VALUES (2, 
    (SELECT togruteId FROM kundeOrdre INNER JOIN togruteforekomst USING (forekomstId) WHERE ordreNr=2)
, 1, 5, 1, 5);
