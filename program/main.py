import Train_Db as tdb
from messages import HELP, QUIT
from utils import *
import os
from sys import platform
import datetime
import pandas as pd
from tabulate import tabulate

isRunningOnMacos = platform.startswith("darwin")
if isRunningOnMacos:  # darwin = macos
    import readline

COMMANDS = ["hent_togruter_for_stasjon", "hent_ruter_mellom_stasjoner",
            "registrer_bruker", "finn_ledige_billetter", "kjop_billett",
            "hent_ordre", "finn_jernbanestasjon_for_togrute",
            "finn_banestrekninger", "finn_togruter_for_banestrekning", ]


def completer(text, state):
    options = [i for i in COMMANDS if i.startswith(text)]
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
    # Venter på en kommando fra input, kommando skal ikke være case sensitive
    command = input('$ ').lower()

    # Splitter opp kommandoen
    argument_list = command.split(" ")

    # Oppgave c), få ut alle togruter for en gitt jernbanestasjon på en gitt
    # ukedag
    # Tar inn en stasjon og en ukedag
    if argument_list[0] == "hent_togruter_for_stasjon":
        if len(argument_list) == 1:
            print("Dette er eksisterende jernbanestasjoner")
            db_manager.get_all_stops()
            stopp: int = int(input("Velg en jernbanestasjonId: "))
            ukedag: int = int(
                input("Hvilken ukedag? (1: mandag - 7: søndag): "))
            db_manager.get_train_routes(stopp, ukedag)

        elif len(argument_list) == 3:
            db_manager.get_train_routes(
                int(argument_list[1]),
                int(argument_list[2]))

        else:
            print(
                "Bruk: hent_togruter_for_stasjon jernbanestasjonId ukedagNr " +
                "(1: mandag - 7: søndag) \nEller: hent_togruter_for_stasjon")

    # Oppgave d), togruter mellom start-stasjon og slutt-stasjon
    # Returnere alle tider samme dag og neste dag
    elif argument_list[0] == "hent_ruter_mellom_stasjoner":

        if len(argument_list) == 1:
            print("Dette er eksisterende jernbanestasjoner")
            db_manager.get_all_stops()
            stopp_fra: int = int(
                input("Velg en jernbanestasjonId du vil reise fra: "))
            stopp_til: int = int(
                input("Velg en jernbanestasjonId du vil reise til: "))
            timestamp_string = input("Ønsket dato(yyyy-mm-dd): ")
            format_string = '%Y-%m-%d'
            dt_object = datetime.datetime.strptime(
                timestamp_string, format_string)

            db_manager.get_route_by_stations(
                stopp_fra, stopp_til, dt_object, True)

        elif len(argument_list) == 4:
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

        else:
            print(
                "Bruk: hent_ruter_mellom_stasjoner startstasjonid " +
                "sluttstasjonid yyyy-mm-dd")

    # Oppgave e) registrer bruker
    elif argument_list[0] == "registrer_bruker":
        if len(argument_list) < 5:
            print(
                "Bruk: registrer_bruker email phone_number etternavn" +
                " fornavn <optional x antall mellomnavn>\n" +
                "Eksempel: registrer_bruker ex@mail.com 40060200 nordmann " +
                "ola mellomnavn annetmellomnavn")
        else:
            first_name = ' '.join(argument_list[4:])
            db_manager.register_user(
                first_name,
                argument_list[3],
                argument_list[1],
                int(argument_list[2]),
            )

    # Oppgave g) finn ledige billetter og kjøp
    elif argument_list[0] == "finn_ledige_billetter":
        banestrekning_id: int
        train_route_id: int
        start_station_seq_nr: int
        end_station_seq_nr: int

        def proceed():
            if (len(argument_list) == 4 or len(argument_list) == 1):
                available_tickets = db_manager.find_tickets(
                    train_route_id,
                    start_station_seq_nr,
                    end_station_seq_nr
                )
                print(
                    tabulate(
                        pd.DataFrame(
                            available_tickets,
                            columns=["plassNr", "vognId", "dato",
                                    "vogntype", "togruteforekomstId"]),
                        headers='keys', tablefmt='psql', showindex=False))

            print("sekvensnr valgt start: {sekstart}\n".format(sekstart=start_station_seq_nr) +
                  "sekvensnr valgt ende: {sekende}".format(
                      sekende=end_station_seq_nr
                  ))


        if len(argument_list) == 1:
            # Vis baner
            print("\nDette er banestrekningene som eksisterer på jernbanenettet:")
            db_manager.get_banestrekninger()
            banestrekning_id = int(input("Skriv banestrekningId til " +
                                         "banestrekningen du vil reise på: "))

            # Vis togruter på bane
            print("\nDette er togrutene som eksisterer på valgt banestrekning:")
            db_manager.get_train_routes_on_banestrekning(banestrekning_id)
            train_route_id = int(input("Skriv togruteId til togruten du vil " +
                                       "reise på: "))

            # Vis togstopp på bane
            print("\nDette er stoppene som eksisterer på valgt togrute:")
            db_manager.get_sequence_n(train_route_id)
            start_station_seq_nr = int(input("Skriv sekvensNr til stasjonen " +
                                             "du vil reise fra: "))
            end_station_seq_nr = int(input("Skriv sekvensNr til stasjonen " +
                                           "du vil reise til: "))

            proceed()

        elif len(argument_list) == 4:
            train_route_id = argument_list[1]
            start_station_seq_nr = argument_list[2]
            end_station_seq_nr = argument_list[3]
            proceed()

        else:
            print(
                '''
                Bruk: finn_ledige_billetter togruteId startSekvensNr sluttSekvensNr
                Eller: finn_ledige_billetter
                '''
            )

    elif argument_list[0] == "kjop_billett":
        if (len(argument_list) != 7):
            print(
                "Bruk: kjop_billett vogn_id plass_nr sekvens_nr_start " +
                "sekvens_nr_ende kundenr togruteforekomst_id\n\n" +
                "Om du er usikker på hva disse feltene skal være, bruk:\n" +
                "finn_ledige_billetter"
            )
        else:
            db_manager.create_ticket(
                int(argument_list[1]),
                int(argument_list[2]),
                int(argument_list[3]),
                int(argument_list[4]),
                int(argument_list[5]),
                int(argument_list[6]))

    # Oppgave h) info om tidligere kjøp for fremtidige reiser
    elif argument_list[0] == "hent_ordre":
        if len(argument_list) == 2:
            db_manager.get_orders(argument_list[1])
        elif len(argument_list) == 1:
            print("Registrerte brukere:")
            db_manager.get_all_customers()
            kunde_nr: int = int(
                input("Kundenr du ønsker å hente ordre fra: "))
            db_manager.get_orders(kunde_nr)
        else:
            print("Bruk: hent_ordre kundenummer")

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

    # Finn jernbanestasjoner for gitt togrute
    elif argument_list[0] == "finn_jernbanestasjon_for_togrute":
        if len(argument_list) != 2:
            print("Bruk: finn_jernbanestasjon_for_togrute togrute_id")
        else:
            db_manager.get_sequence_n_station_id(int(argument_list[1]))

    # Finn banestrekninger
    elif argument_list[0] == "finn_banestrekninger":
        db_manager.get_banestrekninger()

    elif argument_list[0] == "finn_togruter_for_banestrekning":
        if len(argument_list) != 2:
            print("Bruk: finn_togruter_for_banestrekning banestrekning_id")
        else:
            db_manager.get_train_routes_on_banestrekning(int(argument_list[1]))

    # exit
    elif argument_list[0] in ["exit", "q", "quit", "slutt"]:
        print(QUIT)
        break

    elif argument_list[0] in ["help", "h", "", "hjelp"]:
        print(HELP)

    else:
        print("Kommando ikke gjenkjent. Skriv \"hjelp\" for hjelp.")


del db_manager
