QUIT = "Avslutter TogDB CLI..."
HELP = {
    "main": """
TogDB CLI Hjelp
#################

BRUK -h ETTER EN KOMMANDO FOR Å FÅ SPESIFIKK BRUK AV KOMMANDO

slutt,
exit,
q,
quit - avslutter TogDB CLI

help,
h,
,
hjelp - viser hjelp

hent_togruter_for_stasjon - skriver alle togruter som går gjennom en 
stasjon på en gitt ukedag. 

hent_ruter_mellom_stasjoner - skriver alle togruter som går mellom
to stasjoner

registrer_bruker - registrerer en ny bruker

finn_ledige_billetter - finner alle potensielle ledige billetter mellom 
to stasjoner på en spesifikk togrute

kjop_billett - kjøper en billett

hent_ordre - henter ordrer i fremtiden for en bruker.

ny_vognmodell - lag ny vognmodell

finn_banestrekninger - finner alle banestrekninger på jernbanenettverket

finn_togruter_for_banestrekning - finner alle togruter for en gitt banestrekning

finn_jernbanestasjon_for_togrute - finner alle jernbanestasjoner for en gitt 
togrute
""",


    "hent_togruter_for_stasjon":
    "Bruk: hent_togruter_for_stasjon " +
    "jernbanestasjonId ukedagNr " +
    "(1: mandag - 7: søndag) \nEller: hent_togruter_for_stasjon",


    "finn_ledige_billetter":
    '''Bruk: finn_ledige_billetter togruteId startSekvensNr sluttSekvensNr
    Eller: finn_ledige_billetter''',


    "hent_ruter_mellom_stasjoner":
    "Bruk: hent_ruter_mellom_stasjoner startstasjonid " +
    "sluttstasjonid yyyy-mm-dd",


    "registrer_bruker":
    "Bruk: registrer_bruker email phone_number etternavn" +
    " fornavn <optional x antall mellomnavn>\n" +
    "Eksempel: registrer_bruker ex@mail.com 40060200 nordmann " +
    "ola mellomnavn annetmellomnavn",


    "kjop_billett":
    "Bruk: kjop_billett vogn_id plass_nr sekvens_nr_start " +
    "sekvens_nr_ende kundenr togruteforekomst_id\n\n" +
    "Om du er usikker på hva disse feltene skal være, bruk:\n" +
    "finn_ledige_billetter",


    "ny_vognmodell":
    "Bruk: ny_vognmodell modellnavn",


    "finn_jernbanestasjon_for_togrute":
    "Bruk: finn_jernbanestasjon_for_togrute togrute_id",

    "finn_togruter_for_banestrekning":
    "Bruk: finn_togruter_for_banestrekning banestrekning_id",

}

READY = "TogDB CLI er klar for bruk. Skriv 'hjelp' / 'h' for mer informasjon."
