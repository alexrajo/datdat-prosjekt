PRAGMA foreign_keys = ON;

CREATE TABLE kunde (
    kundenummer INTEGER PRIMARY KEY AUTOINCREMENT,
    fornavn TEXT NOT NULL,
    etternavn TEXT NOT NULL,
    email TEXT NOT NULL,
    mobilnummer INTEGER NOT NULL
);

CREATE TABLE kundeOrdre (
    ordreNr INTEGER PRIMARY KEY AUTOINCREMENT,
    kjopstidspunkt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    kundenummer INTEGER NOT NULL,
    forekomstId INTEGER,

    FOREIGN KEY (kundenummer) REFERENCES kunde(kundenummer)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (forekomstId) REFERENCES togruteforekomst(forekomstId)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE billett (
    billettNr INTEGER PRIMARY KEY AUTOINCREMENT,
    ordreNr INTEGER NOT NULL,
    togruteId INTEGER NOT NULL,
    vognId INTEGER,
    plassNr INTEGER NOT NULL,
    sekvensNrStart INTEGER NOT NULL,
    sekvensNrEnde INTEGER NOT NULL,

    FOREIGN KEY (ordreNr) REFERENCES kundeOrdre(ordreNr)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (vognId) REFERENCES vogn(vognId)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    FOREIGN KEY (togruteId, sekvensNrStart) REFERENCES stopp(togruteId, sekvensNr)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    FOREIGN KEY (togruteId, sekvensNrEnde) REFERENCES stopp(togruteId, sekvensNr)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE togruteforekomst (
    forekomstId INTEGER PRIMARY KEY AUTOINCREMENT,
    togruteId INTEGER NOT NULL,
    ukedagNr INTEGER NOT NULL,
    ukeNr INTEGER NOT NULL,
    aar INTEGER NOT NULL,

    UNIQUE(togruteId, ukedagNr, ukeNr, aar),

    FOREIGN KEY (togruteId, ukedagNr) REFERENCES ukedag(togruteId, ukedagNr)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE ukedag (
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
    motHovedretning BOOLEAN DEFAULT 0 NOT NULL,
    rutenavn TEXT,
    
    FOREIGN KEY (operatorId) REFERENCES operator(operatorId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    
    FOREIGN KEY (banestrekningId) REFERENCES banestrekning(banestrekningId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE banestrekning (
    banestrekningId INTEGER PRIMARY KEY AUTOINCREMENT,
    navn TEXT NOT NULL,
    brukerDiesel BOOLEAN NOT NULL
);


CREATE TABLE stasjonPaaStrekning (
    banestrekningId INTEGER,
    sekvensnr INTEGER,
    jernbanestasjonId INTEGER NOT NULL,
    
    PRIMARY KEY (banestrekningId, sekvensnr),
    
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
    modellNavn TEXT NOT NULL
);

CREATE TABLE sittevognModell (
    vognModellId INTEGER PRIMARY KEY,
    stolrader INTEGER NOT NULL,
    seterPerRad INTEGER NOT NULL,

    FOREIGN KEY (vognModellId) REFERENCES vognModell(vognModellId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE sovevognModell (
    vognModellId INTEGER PRIMARY KEY,
    kupeer INTEGER NOT NULL,

    FOREIGN KEY (vognModellId) REFERENCES vognModell(vognModellId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE vogn (
    vognId INTEGER PRIMARY KEY AUTOINCREMENT,
    vognModellId INTEGER NOT NULL,
    operatorId INTEGER,
    togruteId INTEGER,
    vognnr INTEGER,

    UNIQUE (togruteId, vognnr), -- To vogner skal ikke kunne ha samme nummer i rekka av vogner

    FOREIGN KEY (vognModellId) REFERENCES vognModell(vognModellId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (operatorId) REFERENCES operator(operatorId)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    FOREIGN KEY (togruteId) REFERENCES togrute(togruteId)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE operator (
    operatorId INTEGER PRIMARY KEY AUTOINCREMENT,
    navn TEXT NOT NULL
);

CREATE TABLE stopp (
    togruteId INTEGER,
    sekvensnr INTEGER,
    banestrekningId INTEGER NOT NULL,
    tidspunkt TIME NOT NULL,
    dagOffset INTEGER DEFAULT 0 NOT NULL,

    PRIMARY KEY (togruteId, sekvensNr),

    FOREIGN KEY (togruteId) REFERENCES togrute(togruteId)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (sekvensnr, banestrekningId) REFERENCES stasjonPaaStrekning(sekvensnr, banestrekningId)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);
