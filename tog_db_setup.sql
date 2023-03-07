CREATE TABLE kunde (
    kundenummer INTEGER PRIMARY KEY,
    navn TEXT NOT NULL,
    email TEXT NOT NULL,
    mobilnummer INTEGER NOT NULL
);

CREATE TABLE kundeOrdre (
    ordreNr INTEGER PRIMARY KEY,
    kjopstidspunkt DATETIME NOT NULL,
    kundenummer INTEGER,

    FOREIGN KEY (kundenummer) REFERENCES kunde(kundenummer)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE billett (
    billettNr INTEGER,
    togruteId INTEGER,
    ordreNr INTEGER,
    vognId INTEGER NOT NULL,
    plassNr INTEGER NOT NULL,
    banestrekningId INTEGER NOT NULL,
    sekvensNrStart INTEGER NOT NULL,
    sekvensNrEnde INTEGER NOT NULL,
    togruteForekomstUkeDagNr INTEGER NOT NULL,
    dato DATE NOT NULL,

    PRIMARY KEY(billettNr, togruteId, ordreNr),

    FOREIGN KEY (togruteId) REFERENCES togrute(togruteId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (ordreNr) REFERENCES kundeOrdre(ordreNr)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (vognId) REFERENCES togrute(togruteId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
        
    FOREIGN KEY (banestrekningId) REFERENCES banestrekning(banestrekningId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (sekvensNrStart) REFERENCES stasjonPaaStrekning(sekvensNr)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (sekvensNrEnde) REFERENCES stasjonPaaStrekning(sekvensNr)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
        
    FOREIGN KEY (togruteForekomstUkeDagNr) REFERENCES togRuteForekomst(ukeDagNr)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE togRuteForekomst (
    togruteId INTEGER,
    ukedagNr INTEGER,

    PRIMARY KEY (togruteId, ukedagNr),

    FOREIGN KEY (togruteId) REFERENCES togrute(togruteId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE togrute (
    togruteId INTEGER PRIMARY KEY AUTOINCREMENT,
    operatorId INTEGER NOT NULL,
    banestrekningId INTEGER NOT NULL,
    rutenavn TEXT,
    
    FOREIGN KEY (operatorId) REFERENCES operator(operatorId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    
    FOREIGN KEY (banestrekningId) REFERENCES banestrekning(banestrekningId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE operator (
    operatorId INTEGER PRIMARY KEY AUTOINCREMENT,
    navn VARCHAR NOT NULL
);

CREATE TABLE banestrekning (
    banestrekningId INTEGER PRIMARY KEY AUTOINCREMENT,
    navn VARCHAR NOT NULL,
    brukerDiesel BOOLEAN NOT NULL
);


CREATE TABLE stasjonPaaStrekning (
    banestrekningId INTEGER,
    sekvensId INTEGER,
    jernbanestasjonId INTEGER NOT NULL,
    
    PRIMARY KEY (banestrekningId, sekvensId),
    
    FOREIGN KEY (banestrekningId) REFERENCES banestrekning(banestrekningId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
        
    FOREIGN KEY (jernbanestasjonId) REFERENCES jernbanestasjon(jernbanestasjonId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE jernbanestasjon (
    jernbanestasjonId INTEGER PRIMARY KEY AUTOINCREMENT,
    navn TEXT NOT NULL,
    moh DOUBLE NOT NULL
);

CREATE TABLE delstrekning (
    jernbanestasjonIdFra INTEGER,
    jernbanestasjonIdTil INTEGER,
    lengde INTEGER NOT NULL,
    dobbeltspor BOOLEAN NOT NULL,

    PRIMARY KEY (jernbanestasjonIdFra, jernbanestasjonIdTil),

    FOREIGN KEY (jernbanestasjonIdFra) REFERENCES jernbanestasjon(jernbanestasjonId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (jernbanestasjonIdTil) REFERENCES jernbanestasjon(jernbanestasjonId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE vognModell (
    vognModellId INTEGER PRIMARY KEY AUTOINCREMENT,
    modellNavn TEXT NOT NULL,
    operatorId INTEGER NOT NULL,
    erSittevogn BOOLEAN NOT NULL,
    stolrader INTEGER,
    seterPerRad INTEGER,
    kupeer INTEGER,
    
    FOREIGN KEY (operatorId) REFERENCES operator(operatorId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE vogn (
    vognId INTEGER PRIMARY KEY AUTOINCREMENT,
    vognModellId INTEGER NOT NULL,

    FOREIGN KEY (vognModellId) REFERENCES vognModell(vognModellId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE vognOppsett (
    vognOppsettId INTEGER PRIMARY KEY AUTOINCREMENT,
    togruteId INTEGER NOT NULL,
    
    FOREIGN KEY (togruteId) REFERENCES togrute(togruteId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE vognOppsettVogn (
    togruteId INTEGER,
    vognOppsettId INTEGER,
    vognId INTEGER,
    vognNr INTEGER NOT NULL,

    PRIMARY KEY (togruteId, vognOppsettId, vognId),
    UNIQUE (togruteId, vognOppsettId, vognId, vognNr),

    FOREIGN KEY (togruteId) REFERENCES togrute(togruteId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (vognOppsettId) REFERENCES vognOppsett(vognOppsettId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (vognId) REFERENCES vogn(vognId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE stopperPaa (
    togruteId INTEGER,
    sekvensNr INTEGER,
    tidspunkt TIME,

    PRIMARY KEY (togruteId, sekvensNr),

    FOREIGN KEY (togruteId) REFERENCES togrute(togruteId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (sekvensNr) REFERENCES stasjonPaaStrekning(sekvensNr)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- Insert data into database --
INSERT INTO jernbanestasjon (navn, moh) VALUES ("Trondheim", 5.1);
INSERT INTO jernbanestasjon (navn, moh) VALUES ("Steinkjer", 3.6);
INSERT INTO jernbanestasjon (navn, moh) VALUES ("Mosjøen", 6.8);
INSERT INTO jernbanestasjon (navn, moh) VALUES ("Mo i rana", 3.5);
INSERT INTO jernbanestasjon (navn, moh) VALUES ("Fauske", 34);
INSERT INTO jernbanestasjon (navn, moh) VALUES ("Bodø", 4.1);

INSERT INTO delstrekning VALUES (1, 2, 120, true);
INSERT INTO delstrekning VALUES (2, 3, 280, false);
INSERT INTO delstrekning VALUES (3, 4, 90, false);
INSERT INTO delstrekning VALUES (4, 5, 170, false);
INSERT INTO delstrekning VALUES (5, 6, 60, false);

INSERT INTO banestrekning (navn, brukerDiesel) VALUES ("Nordlandsbanen", true);

INSERT INTO stasjonPaaStrekning VALUES (1, 1, 1);
INSERT INTO stasjonPaaStrekning VALUES (1, 2, 2);
INSERT INTO stasjonPaaStrekning VALUES (1, 3, 3);
INSERT INTO stasjonPaaStrekning VALUES (1, 4, 4);
INSERT INTO stasjonPaaStrekning VALUES (1, 5, 5);
INSERT INTO stasjonPaaStrekning VALUES (1, 6, 6);

INSERT INTO operator (navn) VALUES ("SJ");

INSERT INTO togrute (operatorId, banestrekningId, rutenavn) VALUES (1, 1, "Dagtog fra Trondheim til Bodø");
INSERT INTO togrute (operatorId, banestrekningId, rutenavn) VALUES (1, 1, "Nattog fra Trondheim til Bodø");
INSERT INTO togrute (operatorId, banestrekningId, rutenavn) VALUES (1, 1, "Morgentog fra Mo i Rana til Trondheim");

-- Togrute 1
INSERT INTO stopperPaa VALUES (1, 1, "07:49:00");
INSERT INTO stopperPaa VALUES (1, 2, "09:51:00");
INSERT INTO stopperPaa VALUES (1, 3, "13:20:00");
INSERT INTO stopperPaa VALUES (1, 4, "14:31:00");
INSERT INTO stopperPaa VALUES (1, 5, "16:49:00");
INSERT INTO stopperPaa VALUES (1, 6, "17:34:00");

-- Togrute 2
INSERT INTO stopperPaa VALUES (2, 1, "23:05:00");
INSERT INTO stopperPaa VALUES (2, 2, "00:57:00");
INSERT INTO stopperPaa VALUES (2, 3, "04:41:00");
INSERT INTO stopperPaa VALUES (2, 4, "05:55:00");
INSERT INTO stopperPaa VALUES (2, 5, "08:19:00");
INSERT INTO stopperPaa VALUES (2, 6, "09:05:00");

-- Togrute 3
INSERT INTO stopperPaa VALUES (3, 4, "08:11:00");
INSERT INTO stopperPaa VALUES (3, 3, "09:14:00");
INSERT INTO stopperPaa VALUES (3, 2, "12:31:00");
INSERT INTO stopperPaa VALUES (3, 1, "14:13:00");

-- Vognmodeller
INSERT INTO vognModell (modellNavn, operatorId, erSittevogn, stolrader, seterPerRad, kupeer) VALUES ("SJ-sittevogn-1", 1, true, 3, 4, NULL);
INSERT INTO vognModell (modellNavn, operatorId, erSittevogn, stolrader, seterPerRad, kupeer) VALUES ("SJ-sovevogn-1", 1, false, NULL, NULL, 4);

-- Vogner
INSERT INTO vogn (vognModellId) VALUES (1);
INSERT INTO vogn (vognModellId) VALUES (1);
INSERT INTO vogn (vognModellId) VALUES (1);
INSERT INTO vogn (vognModellId) VALUES (2);
INSERT INTO vogn (vognModellId) VALUES (1);

-- Vognoppsett
INSERT INTO vognOppsett (togruteId) VALUES (1); -- Dagtog Trondheim til Bodø
INSERT INTO vognOppsettVogn VALUES (1, 1, 1, 1);
INSERT INTO vognOppsettVogn VALUES (1, 1, 2, 2);

INSERT INTO vognOppsett (togruteId) VALUES (2); -- Nattog Trondheim til Bodø
INSERT INTO vognOppsettVogn VALUES (2, 2, 3, 1);
INSERT INTO vognOppsettVogn VALUES (2, 2, 4, 2);

INSERT INTO vognOppsett (togruteId) VALUES (3); -- Morgentog Mo i Rana til Trondheim
INSERT INTO vognOppsettVogn VALUES (3, 3, 5, 1);

-- Ruteforekomster
-- For togrute 1
INSERT INTO togRuteForekomst VALUES (1, 1);
INSERT INTO togRuteForekomst VALUES (1, 2);
INSERT INTO togRuteForekomst VALUES (1, 3);
INSERT INTO togRuteForekomst VALUES (1, 4);
INSERT INTO togRuteForekomst VALUES (1, 5);

-- For togrute 2
INSERT INTO togRuteForekomst VALUES (2, 1);
INSERT INTO togRuteForekomst VALUES (2, 2);
INSERT INTO togRuteForekomst VALUES (2, 3);
INSERT INTO togRuteForekomst VALUES (2, 4);
INSERT INTO togRuteForekomst VALUES (2, 5);
INSERT INTO togRuteForekomst VALUES (2, 6);
INSERT INTO togRuteForekomst VALUES (2, 7);

-- For togrute 3
INSERT INTO togRuteForekomst VALUES (3, 1);
INSERT INTO togRuteForekomst VALUES (3, 2);
INSERT INTO togRuteForekomst VALUES (3, 3);
INSERT INTO togRuteForekomst VALUES (3, 4);
INSERT INTO togRuteForekomst VALUES (3, 5);