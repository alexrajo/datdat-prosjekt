import Train_Db as tdb
from utils import *
import os
from sys import platform
import datetime

isRunningOnMacos = platform.startswith("darwin")
if isRunningOnMacos: # darwin = macos
    import readline

COMMANDS = ["hent_togruter_for_stasjon","hent_ruter_mellom_stasjoner", "registrer_bruker", "finn_ledige_billetter", "kjop_billett","hent_ordre"]

def completer(text, state):
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None


dir_path = os.path.dirname(os.path.realpath(__file__))
db_manager = tdb.Train_Db_Manager(dir_path + "/../data/tog.db")


print("TogDB CLI er klar for bruk. Skriv 'hjelp' / 'h' for mer informasjon.")
while True:
    if isRunningOnMacos:
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer)
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
        if len(argument_list) != 5:
            print(
                "Bruk: registrer_bruker fornavn etternavn email phone_number")
        else:
            db_manager.register_user(
                argument_list[1],
                argument_list[2],
                argument_list[3],
                argument_list[4],
            )

    # Oppgave g) finn ledige billetter og kjøp
    elif argument_list[0] == "finn_ledige_billetter":
        db_manager.find_tickets()

    elif argument_list[0] == "kjop_billett":
        db_manager.create_ticket()

    # Oppgave h) info om tidligere kjøp for fremtidige reiser
    elif argument_list[0] == "hent_ordre":
        if len(argument_list) != 2:
            print(
                "Bruk: hent_ordre kundenummer")
        else:
            db_manager.get_orders(
                argument_list[1],
            )

    # lage ny vognmodell
    elif argument_list[0] == "ny_vognmodell":
        if len(argument_list) != 2:
            print(
                "Bruk: ny_vognmodell modellnavn")
        else:
            isSittingCart = input("Sittevogn? y/n: ").lower() == "y"
        
            if isSittingCart:
                sittingCartArgs = input("stolrader seterPerRad: ").split(" ")
                compartments = None
            else:
                compartments = input("kupeer: ")
                sittingCartArgs = [None, None]

            cart_model_id = db_manager.create_cart_model(
                argument_list[1], 
                isSittingCart, 
                sittingCartArgs[0], 
                sittingCartArgs[1], 
                compartments
            )

            print("ID til ny VognModell: ", cart_model_id)

    # exit
    elif argument_list[0] in ["exit", "q", "quit", "slutt"]:
        print("Avslutter TogDB CLI...")
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

ny_vognmodell - lag ny vognmodell
""")

    else:
        print("Kommando ikke gjenkjent.")


del db_manager
