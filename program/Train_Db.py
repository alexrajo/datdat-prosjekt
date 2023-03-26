from sqlite3 import Cursor, Connection, connect
from datetime import datetime, timedelta
import pandas as pd
from tabulate import tabulate
import math


class Train_Db_Manager:
    """Class with methods for managing the train database.

    Constructor parameters:
        db_location (str): path to database file.
    """
    db_connection: Connection
    db_cursor: Cursor

    def __init__(self, db_location: str):
        self.db_connection = connect(db_location)
        self.db_cursor = self.db_connection.cursor()
        self.execute("PRAGMA foreign_keys = ON;")

    def __del__(self):
        self.db_connection.close()

    def execute(self, command: str):
        """Executes sql.

        Parameters:
            command (str): sql command.

        Returns:
            Cursor: resulting cursor from sql command.
        """
        return self.db_cursor.execute(command)

    def find_tickets(self, train_route_id: int, start_station_seq_nr: int,
                     end_station_seq_nr: int):
        """Finds all available tickets between two stations with given sequence numbers.

        Parameters:
            train_route_id (int): number corresponding to id of train route 
            which tickets to return.
            start_station_id (int): number corresponding to id of start station.
            end_station_id (int): number corresponding to id of end station.

        Returns:
            A list of tuples containing <attributes>.

            list<(<attribute>: <type>,...)>.
        """

        self.execute("DROP VIEW IF EXISTS vognmodell_plasser;")
        self.execute("""
            CREATE TEMP VIEW vognmodell_plasser
            AS
            SELECT 
                vognModellId, 
                COALESCE(sittevognModell.seterPerRad, 0) * COALESCE(sittevognModell.stolrader, 0) + COALESCE(sovevognModell.kupeer, 0)*2 AS plasser
            FROM vognModell
            LEFT OUTER JOIN sittevognModell USING (vognModellId)
            LEFT OUTER JOIN sovevognModell USING (vognModellId);
        """)

        relevantCartModelIds = self.execute("""
            SELECT DISTINCT vognModellId FROM togrute
            INNER JOIN vogn USING(togruteId)
            WHERE togruteId = {input_togruteId};
        """.format(input_togruteId=train_route_id)).fetchall()

        available_tickets = []

        for row in relevantCartModelIds:
            cart_model_id = row[0]

            self.execute("DROP VIEW IF EXISTS vogn_plasser;")
            self.execute("""
                CREATE TEMP VIEW vogn_plasser
                AS 
                WITH plasser AS (
                        SELECT 1 AS plassNr
                        UNION ALL
                        SELECT (plassNr + 1)
                        FROM plasser CROSS JOIN vognmodell_plasser
                        WHERE plassNr < vognmodell_plasser.plasser
                        AND vognmodell_plasser.vognModellId = {vognModellId}
                    ) SELECT * FROM plasser;
            """.format(vognModellId=cart_model_id))

            # Find all available tickets with the corresponding vognModellId
            avtickets = self.execute('''
            SELECT DISTINCT 
                vogn_plasser.plassNr, 
                vognId,
                togruteforekomstMulig.forekomstId AS togruteforekomstId,
                COALESCE(date(strftime('%Y-%m-%d', aar || '-01-01', '+' || (ukedagNr+(ukeNr-1)*7+startstopp.dagOffset) || ' day')), 'N/A') AS avgangsdato,
                vognModell.modellnavn AS vogntype
            FROM togruteforekomst AS togruteforekomstMulig
            INNER JOIN togrute USING(togruteId)
            INNER JOIN vogn USING(togruteId)
            INNER JOIN stopp AS startstopp USING(togruteId)
            INNER JOIN stopp AS endestopp USING(togruteId)
            INNER JOIN vognModell USING(vognModellId)
            CROSS JOIN vogn_plasser
            WHERE (
                (motHovedretning = 0 AND startstopp.sekvensNr < endestopp.sekvensNr
                OR
                motHovedretning = 1 AND startstopp.sekvensNr > endestopp.sekvensNr)
                AND togruteId = {input_togruteId}
                AND vogn.vognModellId = {input_vognModellId}
                AND startstopp.sekvensNr = {input_sekvensNrStart}
                AND endestopp.sekvensNr = {input_sekvensNrEnde}
            )
            AND COALESCE(date(strftime('%Y-%m-%d', aar || '-01-01', '+' || (ukedagNr+(ukeNr-1)*7+endestopp.dagOffset) || ' day')), date('now')) >= date('now')
            AND NOT EXISTS (
                SELECT * FROM billett
                INNER JOIN kundeOrdre AS bestiltKundeOrdre USING(ordreNr)
                INNER JOIN vogn AS bestiltVogn USING(vognId)
                WHERE togruteforekomstMulig.forekomstId = 
                    bestiltKundeOrdre.forekomstId
                AND billett.vognId = vogn.vognId
                AND (
                    (
                        bestiltVogn.vognModellId IN 
                        (SELECT vognModellId FROM sovevognModell) AND 
                        (
                            floor((vogn_plasser.plassNr+1)/2) = 
                            floor((billett.plassNr+1)/2)
                        )
                    )
                    OR
                    (
                        bestiltVogn.vognModellId IN 
                        (SELECT vognModellId FROM sittevognModell) AND 
                        (
                            billett.plassNr = vogn_plasser.plassNr
                            AND
                            (startstopp.sekvensNr < billett.sekvensNrEnde AND
                            billett.sekvensNrStart < endestopp.sekvensNr)
                        )
                    )
                )
            )
            '''.format(
                input_vognModellId=cart_model_id,
                input_togruteId=train_route_id,
                input_sekvensNrStart=start_station_seq_nr,
                input_sekvensNrEnde=end_station_seq_nr
            )
            ).fetchall()
            available_tickets.extend(avtickets)

        pd.set_option("display.max_rows", None)
        return available_tickets

    def get_orders(self, customer_n: int):
        """Gets future orders of a customer.

        Parameters:
            customer_n (int): customer number of customer which orders to 
            return.

        Returns:
            A list of tuples containing <attributes>.

            list<(<attribute>: <type>,...)>.
        """

        current_year, current_week, current_weekday = datetime.today().isocalendar()

        sql = """
        SELECT 
            ordreNr AS 'OrdreNr', 
            kjopstidspunkt AS 'Kjøpstidpunkt', 
            tf.aar AS 'År', 
            tf.ukeNr as Uke,
            tf.ukedagNr AS Ukedag,
            kundeOrdre.kundenummer
        FROM kundeOrdre 
        INNER JOIN togruteforekomst AS tf USING (forekomstId) 
        WHERE kundenummer = {input_kundenummer}
        AND (
            aar > {current_aar}
            OR (
            aar = {current_aar} AND ukeNr > {current_ukeNr}
            ) OR (
            aar = {current_aar} AND ukeNr = {current_ukeNr} AND ukedagNr >= {current_ukedagNr}
            )
        );
        """.format(
            input_kundenummer=customer_n,
            current_aar=current_year,
            current_ukeNr=current_week,
            current_ukedagNr=current_weekday
        )

        print(tabulate(pd.read_sql_query(sql, self.db_connection),
              headers='keys', tablefmt='psql', showindex=False))

    def get_tickets_from_order(self, order_nr: int):
        self.execute("""
            SELECT
                billettNr AS BillettNr,
                aar,
                ukeNr,
                ukedagNr,
                rutenavn AS Rutenavn,
                vogn.vognNr AS VognNr,
                plassNr AS PlassNr,
                avgangsstopp.tidspunkt AS 'Avgang (kl.)',
                avgang_jbs.navn AS 'Fra stasjon',
                ankomststopp.tidspunkt AS 'Kommer fram (kl.)',
                ankomst_jbs.navn AS 'Til stasjon'
            FROM billett
            INNER JOIN kundeOrdre USING (ordreNr)
            INNER JOIN togruteforekomst USING (forekomstId)
            INNER JOIN togrute USING (togruteId)
            INNER JOIN stopp AS avgangsstopp ON avgangsstopp.sekvensnr = billett.sekvensNrStart AND avgangsstopp.togruteId = togrute.togruteId
            INNER JOIN stopp AS ankomststopp ON ankomststopp.sekvensnr = billett.sekvensNrEnde AND ankomststopp.togruteId = togrute.togruteId
            INNER JOIN banestrekning USING (banestrekningId)
            INNER JOIN stasjonPaaStrekning AS sps_av ON sps_av.sekvensnr = avgangsstopp.sekvensnr
            INNER JOIN stasjonPaaStrekning AS sps_an ON sps_an.sekvensnr = ankomststopp.sekvensnr
            INNER JOIN jernbanestasjon AS avgang_jbs ON avgang_jbs.jernbanestasjonId = sps_av.jernbanestasjonId
            INNER JOIN jernbanestasjon AS ankomst_jbs ON ankomst_jbs.jernbanestasjonId = sps_an.jernbanestasjonId
            INNER JOIN vogn USING (vognId)
            WHERE ordreNr = {input_ordreNr};
        """.format(input_ordreNr=order_nr))

        return self.db_cursor.fetchall()

    def get_route_by_stations(
        self, start_station_id: int, end_station_id: int,
            datetimeInput: datetime, arrives: bool):
        """Prints all train routes that arrives at given end station before a 
        specified datetime or leaves at a given start station before a specified 
        datetime.

        Parameters:
            start_station_id (int): number corresponding to id of start station.
            end_station_id (int): number corresponding to id of end station.
            datetime (datetime): date and time user searches for.
            arrives (bool): true for "arrives at given end station before a 
            specified datetime" false for "leaves at a given start station 
            before a specified datetime".

        Returns:
            void

        """
        year = datetimeInput.year # extract the year from the datetime object
        # create datetime objects for the first day of the year, the first day of the year after, and the last day of the year
        last_day_of_last_year = datetime(year-1, 12, 31)
        first_day_of_year = datetime(year, 1, 1)
        first_day_of_next_year = datetime(year+1, 1, 1)
        last_day_of_year = datetime(year, 12, 31)

        # get the weekday number for each date object
        weekday_of_last_day_of_last_year = last_day_of_last_year.weekday() + 1
        weekday_of_first_day_of_year = first_day_of_year.weekday() + 1
        weekday_of_first_day_of_next_year = first_day_of_next_year.weekday() + 1
        weekday_of_last_day_of_year = last_day_of_year.weekday() + 1

        print(tabulate(pd.read_sql_query("""
        SELECT DISTINCT
        togruteid, 
        rutenavn,  
        banestrekningId, 
        tidspunkt AS avgang
        FROM togrute 
        INNER JOIN stopp AS startstopp USING (togruteId, banestrekningId)
        INNER JOIN stasjonPaaStrekning USING (banestrekningId, sekvensNr)
        INNER JOIN jernbanestasjon USING (jernbanestasjonId)
        INNER JOIN togruteforekomst USING (togruteId)
        WHERE (
            jernbanestasjonId = {input_startstasjonId}
            AND 
            togruteId IN (
                SELECT sluttstopp.togruteId FROM togrute AS t2
                INNER JOIN stopp AS sluttstopp USING (togruteId)
                INNER JOIN stasjonPaaStrekning 
                USING (banestrekningId, sekvensNr)
                INNER JOIN jernbanestasjon USING (jernbanestasjonId)
                WHERE jernbanestasjonId = {input_sluttstasjonId}
                AND (
                    (motHovedretning = 0 
                    AND startstopp.sekvensnr <= sluttstopp.sekvensnr) 
                    OR 
                    (motHovedretning = 1 
                    AND startstopp.sekvensnr > sluttstopp.sekvensnr)
                    )
            )
            AND (
                aar = {input_aar}
                AND (
                    ukeNr = {input_ukeNr} AND (
                        ukedagNr + startstopp.dagOffset = {input_ukedagNr}
                        OR
                        ukedagNr + startstopp.dagOffset = {input_ukedagNr} + 1
                    )
                ) 
                OR
                (ukeNr = {input_ukeNr} - 1 AND (ukedagNr-1 + startstopp.dagOffset) % 7 + 1 = {input_ukedagNr})
                OR (
                    {input_ukedagNr} = 7 
                    AND 
                    ukeNr = {input_ukeNr} + 1 
                    AND 
                    (ukedagNr-1 + startstopp.dagOffset) % 7 + 1 = 1
                )
            )
            OR (
            aar = {input_aar} - 1
            AND
                (
                ukeNr = 52
                AND
                ukedagNr + startstopp.dagOffset > {weekday_of_last_day_of_last_year}
                AND
                {input_ukeNr} = 1
                AND 
                {input_ukedagNr} = {weekday_of_first_day_of_year}
                )
            )
            OR (
            aar = {input_aar} + 1
            AND
                (
                ukeNr = 1
                AND
                ukedagNr + startstopp.dagOffset = {weekday_of_first_day_of_next_year}
                AND
                {input_ukeNr} = 52
                AND 
                {input_ukedagNr} = {weekday_of_last_day_of_year}
                )
            )
        )
        ORDER BY avgang, ukedagNr, ukeNr, aar, avgang;
        """.format(
            input_startstasjonId=start_station_id,
            input_sluttstasjonId=end_station_id,
            input_aar=datetimeInput.isocalendar()[0],
            input_ukeNr=datetimeInput.isocalendar()[1],
            input_ukedagNr=datetimeInput.isocalendar()[2],
            weekday_of_last_day_of_last_year = weekday_of_last_day_of_last_year,
            weekday_of_first_day_of_year = weekday_of_first_day_of_year,
            weekday_of_first_day_of_next_year = weekday_of_first_day_of_next_year,
            weekday_of_last_day_of_year = weekday_of_last_day_of_year
        ), self.db_connection), headers='keys', tablefmt='psql', showindex=False))

    def get_train_routes(self, station_id: int, weekday_n: int):
        """Prints all train routes that goes through a given station on a given 
        weekday.

        Parameters:
            station_id (int): number corresponding to id of station.
            weekday_n (int): number corresponding to weekday, 1-7 monday-sunday.

        Returns:
            A list of tuples containing all attributes in a 'togrute'-entity:

            list<(togruteId: int, 
            operatorId: int, 
            banestrekningId: int, 
            motHovedretning: boolean, 
            rutenavn: string
            )>.
        """
        print(tabulate(pd.read_sql_query("""
            SELECT 
            togrute.togruteId,  
            rutenavn
            FROM togrute
            INNER JOIN ukedag USING (togruteId) 
            INNER JOIN stopp USING (togruteId)
            INNER JOIN stasjonPaaStrekning USING (banestrekningId, sekvensNr) 
            WHERE ukedag.ukedagNr = (({ukedagNr}-1) + stopp.dagOffset) % 7 + 1
            AND jernbanestasjonId = {jernbanestasjonId};
        """.format(ukedagNr=weekday_n, jernbanestasjonId=station_id),
            self.db_connection), headers='keys', tablefmt='psql', showindex=False))

    def register_user(
            self, first_name: str, surname: str, email: str, phone_number: int):
        """Registers customer to sqlite database.

        Parameters:
            first_name (str): first name of customer.
            surname (str): surname of customer.
            email (str): email of customer.
            phone_number (int): phone number of customer, 8 numbers, 
            no country code.

        Returns:
            int: generated customer number for customer.
        """

        # return NotImplemented

        res = self.execute("""
        INSERT INTO kunde(fornavn, etternavn, email, mobilnummer)
        VALUES ('{first_name}','{surname}','{email}',{phone_number});
        """.format(
            first_name=first_name,
            surname=surname,
            email=email,
            phone_number=phone_number
        ))
        self.db_connection.commit()
        return res.lastrowid

    def create_tickets(
            self,
            cartsPlacementsAndSequences,
            customer_n: int, train_route_instance_id: int):
        """Creates a ticket for customer with customer_id, 
        and creates an order on it at the same time.

        Parameters:
            cartsPlacementsAndSequences: List of:
                cart_id (int): id of cart customer buys ticket for.
                placement_n (int): number corresponding to seat number or bed number
                in the cart.
                sequence_n_start (int): sequence number of train stop the trip 
                starts on.
                sequence_n_end (int): sequence number of train stop the trip 
                stops on.
            customer_n (int): number corresponding to customer number of buyer.
            train_route_instance_id (int): number corresponding to id of train 
            route instance.

        Returns:
            boolean: True if ticked was craeted.
        """
        id = 0
        placements = []
        for cartPlacementSeq in cartsPlacementsAndSequences:
            newPlacement = cartPlacementSeq.copy()
            newPlacement.append(id)
            placements.append(newPlacement)
            id += 1
        for cartPlacementSeq1 in placements:
            for cartPlacementSeq2 in placements:
                if cartPlacementSeq1[-1] == cartPlacementSeq2[-1]:
                    continue
                # ticket 1
                cart_id = int(cartPlacementSeq1[0])
                placement_n = int(cartPlacementSeq1[1])
                sequence_n_start = int(cartPlacementSeq1[2])
                sequence_n_end = int(cartPlacementSeq1[3])
                # ticket 2
                cart_id2 = int(cartPlacementSeq2[0])
                placement_n2 = int(cartPlacementSeq2[1])
                sequence_n_start2 = int(cartPlacementSeq2[2])
                sequence_n_end2 = int(cartPlacementSeq2[3])
                # do they overlap in sequece numbers?
                hasOverlap = ((sequence_n_start < sequence_n_end2)
                              and (sequence_n_end > sequence_n_start2))
                if (cart_id == cart_id2 and placement_n == placement_n2 and hasOverlap):
                    return print(
                        "Ugyldig bestilling! Noen av billettene overlapper hverandre")

        for cartPlacementSeq in cartsPlacementsAndSequences:
            cart_id = int(cartPlacementSeq[0])
            placement_n = int(cartPlacementSeq[1])
            sequence_n_start = int(cartPlacementSeq[2])
            sequence_n_end = int(cartPlacementSeq[3])
            self.execute(
                """
                    SELECT togruteId
                    FROM togruteforekomst WHERE forekomstId = {train_route_instance_id}
                    
                """.format(train_route_instance_id=train_route_instance_id))
            found_togrute_row = self.db_cursor.fetchone()
            if found_togrute_row is None:
                return print("En av billettene finnes ikke for denne turen")
            found_togruteId = found_togrute_row[0]
            listOfTickets = self.find_tickets(
                found_togruteId, sequence_n_start, sequence_n_end)
            foundTicket = False
            for ticket in listOfTickets:
                harPlass = ticket[0] == placement_n
                harVogn = ticket[1] == cart_id
                harForekomst = ticket[2] == train_route_instance_id
                if harPlass and harVogn and harForekomst:
                    foundTicket = True
                    break
            if not foundTicket:
                return print(
                    "En av billettene du vil kjøpe er ikke ledig / finnes ikke")
            self.execute(
                """
                    SELECT tidspunkt, togruteforekomst.ukedagNr, ukeNr, aar, dagOffset FROM togruteforekomst 
                    INNER JOIN ukedag USING (togruteId) 
                    INNER JOIN stopp USING (togruteId)
                    WHERE (
                    forekomstId = {train_route_instance_id} 
                    AND 
                    sekvensnr = {sequence_n_start} 
                    )
                """.format(
                    train_route_instance_id=train_route_instance_id, sequence_n_start=sequence_n_start))
            row = self.db_cursor.fetchone()
            year = row[3]
            week_number = row[2]
            day_number = str(int(row[1]))
            dayOffset = row[4]
            time_object = datetime.strptime(str(row[0]), '%H:%M:%S').time()
            date_object = datetime.strptime(
                f"{year}-{week_number}-{day_number}", "%Y-%W-%u").date()
            combined_object = datetime.combine(date_object, time_object)
            current_time = datetime.now()
            if (current_time > combined_object + timedelta(days=dayOffset)):
                return print("The train has already passed the start-station")
            self.execute(
                """
                    SELECT * FROM togruteforekomst INNER JOIN togrute USING (togruteId) WHERE forekomstId =
                    {train_route_instance_id} AND motHovedretning = 1
                """.format(
                    train_route_instance_id=train_route_instance_id))
            isAgainstMainDirection = self.db_cursor.fetchone()
            if ((isAgainstMainDirection and sequence_n_start > sequence_n_end) or (not isAgainstMainDirection and sequence_n_start < sequence_n_end)):
                continue
            else:
                return print(
                    "You cannot book order a ticket that goes against the direction of the train!")
        # Ordre
        res_order = self.execute(
            """
            INSERT INTO kundeOrdre(kjopstidspunkt,kundenummer,forekomstId)
            VALUES (DateTime('now'),{customer_n},{train_route_instance_id})
            """.format(customer_n=customer_n,
                       train_route_instance_id=train_route_instance_id))
        # Billett
        listOfRecords = []
        for cartPlacementSeq in cartsPlacementsAndSequences:
            cart_id = cartPlacementSeq[0]
            placement_n = cartPlacementSeq[1]
            sequence_n_start = cartPlacementSeq[2]
            sequence_n_end = cartPlacementSeq[3]
            listOfRecords.append(
                (res_order.lastrowid, found_togruteId, cart_id, placement_n,
                 sequence_n_start, sequence_n_end))
        self.db_cursor.executemany(
            """
            INSERT INTO billett(
                ordreNr,
                togruteId, 
                vognId, 
                plassNr, 
                sekvensNrStart, 
                sekvensNrEnde
            )
            VALUES (?,?,?,?,?,?)
            """, listOfRecords)
        self.db_connection.commit()
        return print("\n\nSuksess! Vi ønsker deg/dere en god tur!\n\n")
        

    def create_cart_model(self, modelname, isSittingCart, seatRows, seatsPerRow,
                          compartments):
        """Creates a new cart model

        Parameters:
            modelname (str): the name of the new cart model to be made
            isSittingCart (boolean): is the cart a sitting cart?
            seatRows (int): the number of rows in the cart if it is a sitting cart
            seatsPerRow (int): the number of seats per row if it is a sitting cart
            compartments (int): the number of compartments with beds if it is a sleeping cart

        Returns:
            (int): generated id for vognModell and corresponding sittevognModell or sovevognModell.
        """

        self.execute("""
            INSERT INTO vognmodell (modellNavn) VALUES ('{modellNavn}');
        """.format(modellNavn=modelname))
        cart_model_id = self.db_cursor.lastrowid
        if isSittingCart:
            self.execute("""
                INSERT INTO sittevognModell VALUES ({vognModellId}, {stolrader}, {seterPerRad});
            """.format(vognModellId=cart_model_id, stolrader=seatRows, seterPerRad=seatsPerRow))
        else:
            self.execute("""
                INSERT INTO sovevognModell VALUES ({vognModellId}, {kupeer});
            """.format(vognModellId=cart_model_id, kupeer=compartments))

        self.db_connection.commit()
        return cart_model_id

    def get_sequence_n(self, togrute_id: int):
        sql_sentence = '''
        SELECT 
        jernbanestasjon.navn AS stasjonsnavn,
        stopp.sekvensnr AS sekvensnr
        FROM togrute 
        INNER JOIN stopp USING(togruteId,banestrekningId) 
        INNER JOIN stasjonPaaStrekning USING(banestrekningId,sekvensnr) 
        INNER JOIN jernbanestasjon USING (jernbanestasjonId) 
        WHERE togruteId = {togrute_id_input}
        ORDER BY 
            CASE WHEN motHovedretning=0 THEN stopp.sekvensnr END ASC,
            CASE WHEN motHovedretning=1 THEN stopp.sekvensnr END DESC;
        '''.format(togrute_id_input=togrute_id)

        print(
            tabulate(
                pd.read_sql_query(sql_sentence, self.db_connection),
                headers='keys', tablefmt='psql', showindex=False))

    def get_banestrekninger(self):
        sql_sentence = '''SELECT navn, banestrekningId FROM banestrekning;'''
        print(
            tabulate(
                pd.read_sql_query(sql_sentence, self.db_connection),
                headers='keys', tablefmt='psql', showindex=False))

    def get_train_routes_on_banestrekning(self, banestrekning_id: int):
        sql_sentence = '''SELECT rutenavn, togruteId FROM togrute
        WHERE (banestrekningId = {banestrekning_id_input});
        '''.format(banestrekning_id_input=banestrekning_id)
        print(
            tabulate(
                pd.read_sql_query(sql_sentence, self.db_connection),
                headers='keys', tablefmt='psql', showindex=False))

    def get_all_stops(self):
        sql_sentence = "SELECT navn, jernbanestasjonId FROM jernbanestasjon;"
        print(
            tabulate(
                pd.read_sql_query(sql_sentence, self.db_connection),
                headers='keys', tablefmt='psql', showindex=False))

    def get_all_customers(self):
        sql_sentence = "SELECT * FROM kunde;"
        print(
            tabulate(
                pd.read_sql_query(sql_sentence, self.db_connection),
                headers='keys', tablefmt='psql', showindex=False))
