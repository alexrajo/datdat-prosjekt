import Train_Db as tdb
from utils import *
import os
import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
db_manager = tdb.Train_Db_Manager(dir_path + "/../data/tog.db")


print("TogDB CLI er klar for bruk. Skriv 'hjelp' / 'h' for mer informasjon.")
while True:
    # Venter på en kommando fra input
    command = input('$ ')

    # Splitter opp kommandoen
    argument_list = command.split(" ")

    # Kommando skal ikke være case sensitive
    argument_list[0] = argument_list[0].lower()

    # Oppgave c), få ut alle togruter for en gitt jernbanestasjon på en gitt ukedag
    # Tar inn en stasjon og en ukedag
    if argument_list[0] == "hent_togruter_for_stasjon":
        if len(argument_list) != 3:
            print(
                "Bruk: hent_togruter_for_stasjon jernbanestasjonId ukedagNr (1: mandag - 7: søndag)")
        else:
            db_manager.get_train_routes(
                int(argument_list[1]),
                int(argument_list[2]))

    # Oppgave d), togruter mellom start-stasjon og slutt-stasjon
    # Returnere alle tider samme dag og neste dag
    elif argument_list[0] == "hent_ruter_mellom_stasjoner":
        if len(argument_list) != 4:
            print(
                "Bruk: hent_ruter_mellom_stasjoner startstasjonid sluttstasjonid yyyy-mm-dd")
        else:
            timestamp_string = argument_list[3]
            format_string = '%Y-%m-%d'
            dt_object = datetime.datetime.strptime(
                timestamp_string, format_string)

            db_manager.get_route_by_stations(
                int(argument_list[1]),
                int(argument_list[2]),
                dt_object,
                True
            )

    # Oppgave e) registrer bruker
    elif argument_list[0] == "registrer_bruker":
        db_manager.register_user()

    # Oppgave g) finn ledige billetter og kjøp
    elif argument_list[0] == "finn_ledige_billetter":
        db_manager.find_tickets()

    elif argument_list[0] == "kjop_billett":
        db_manager.create_ticket()

    # Oppgave h) info om tidligere kjøp for fremtidige reiser
    elif argument_list[0] == "hent_ordre":
        db_manager.get_orders()

    # exit
    elif argument_list[0] in ["exit", "q", "quit", "slutt"]:
        print("Exiting traindb cli.")
        break

    elif argument_list[0] in ["help", "h", "", "hjelp"]:
        print("""
TogDB CLI Hjelp
#################

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
""")

    else:
        print("Kommando ikke gjenkjent.")


del db_manager
