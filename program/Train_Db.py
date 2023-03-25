from sqlite3 import Cursor, Connection, connect
from datetime import datetime
import pandas as pd
from tabulate import tabulate


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
                COALESCE(date(strftime('%Y-%m-%d', aar || '-01-01', '+' || (ukedagNr+(ukeNr-1)*7) || ' day')), 'N/A') AS dato,
                vognModell.modellnavn AS vogntype,
                togruteforekomstMulig.forekomstId AS togruteforekomstId
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
            AND COALESCE(date(strftime('%Y-%m-%d', aar || '-01-01', '+' || (ukedagNr+(ukeNr-1)*7) || ' day')), date('now')) >= date('now')
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
            );'''.format(
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

        print(tabulate(pd.read_sql_query("""
        SELECT 
            ordreNr AS 'OrdreNr', 
            kjopstidspunkt AS 'Kjøpstidpunkt', 
            tf.aar AS 'År', 
            tf.ukeNr as Uke,
            tf.ukedagNr AS Ukedag
        FROM kundeOrdre 
        INNER JOIN togruteforekomst AS tf USING (forekomstId) 
        WHERE kundenummer = {input_kundenummer}
        AND 
            aar > {current_aar}
            OR (
            aar = {current_aar} AND ukeNr > {current_ukeNr}
            ) OR (
            aar = {current_aar} AND ukeNr = {current_ukeNr} AND ukedagNr > {current_ukedagNr}
            );
        """.format(
            input_kundenummer=customer_n,
            current_aar=current_year,
            current_ukeNr=current_week,
            current_ukedagNr=current_weekday
        ), self.db_connection), headers='keys', tablefmt='psql', showindex=False))

    def get_route_by_stations(
        self, start_station_id: int, end_station_id: int,
            datetime: datetime, arrives: bool):
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
        print(tabulate(pd.read_sql_query("""
        SELECT DISTINCT
        togruteid, 
        rutenavn,  
        banestrekningId, 
        tidspunkt AS avgang
        FROM togrute 
        INNER JOIN stopp AS startstopp USING (togruteId)
        INNER JOIN stasjonPaaStrekning USING (banestrekningId, sekvensNr)
        INNER JOIN jernbanestasjon USING (jernbanestasjonId)
        INNER JOIN togruteforekomst USING (togruteId)
        WHERE (
            jernbanestasjonId = {input_startstasjonId}
            AND togruteId IN (
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
            AND
            aar = {input_aar} 
            AND 
            (
                ukeNr = {input_ukeNr} AND (ukedagNr = {input_ukedagNr} 
                OR ukedagNr = {input_ukedagNr} + 1)
                OR {input_ukedagNr} = 7 
                AND ukeNr = {input_ukeNr} + 1 AND ukedagNr = 1
            )
            OR
            aar = {input_aar} + 1 AND ukeNr = 1 AND ukedagNr = 1
        )
        ORDER BY avgang, ukedagNr, ukeNr, aar, avgang;
        """.format(
            input_startstasjonId=start_station_id,
            input_sluttstasjonId=end_station_id,
            input_aar=datetime.isocalendar()[0],
            input_ukeNr=datetime.isocalendar()[1],
            input_ukedagNr=datetime.isocalendar()[2]
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
            WHERE ukedag.ukedagNr = {ukedagNr} 
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

    def create_ticket(
            self, cart_id: int, placement_n: int, sequence_n_start: int,
            sequence_n_end: int, customer_n: int, train_route_instance_id: int):
        """Creates a ticket for customer with customer_id, 
        and creates an order on it at the same time.

        Parameters:
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
            (int, int): generated id for (ticket, order).
        """
        self.execute(
            """
                SELECT tidspunkt, togruteforekomst.ukedagNr, ukeNr, aar FROM togruteforekomst 
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
        day_number = str(int(row[1])-1)
        time_object = datetime.strptime(str(row[0]), '%H:%M:%S').time()
        date_object = datetime.strptime(
            f"{year}-{week_number}-{day_number}", "%Y-%W-%w").date()
        combined_object = datetime.combine(date_object, time_object)
        print(combined_object)
        current_time = datetime.now()
        if (current_time > combined_object):
            return print("The train has already passed the start-station")
        self.execute(
            """
                SELECT * FROM togruteforekomst INNER JOIN togrute USING (togruteId) WHERE forekomstId =
                {train_route_instance_id} AND motHovedretning = 1
            """.format(
                train_route_instance_id=train_route_instance_id))
        isAgainstMainDirection = self.db_cursor.fetchone()
        if ((isAgainstMainDirection and sequence_n_start > sequence_n_end) or (not isAgainstMainDirection and sequence_n_start < sequence_n_end)):
            # Ordre
            res_order = self.execute(
                """
                INSERT INTO kundeOrdre(kjopstidspunkt,kundenummer,forekomstId)
                VALUES (DateTime('now'),{customer_n},{train_route_instance_id})
                """.format(customer_n=customer_n,
                           train_route_instance_id=train_route_instance_id))
            self.db_connection.commit()
            # Billett
            res_ticket = self.execute(
                """
                INSERT INTO billett(
                    ordreNr, 
                    vognId, 
                    plassNr, 
                    sekvensNrStart, 
                    sekvensNrEnde
                )
                VALUES (
                    {order_n}, 
                    {cart_id}, 
                    {placement_n}, 
                    {sequence_n_start}, 
                    {sequence_n_end}
                )
                """.format(
                    order_n=res_order.lastrowid,
                    cart_id=cart_id,
                    placement_n=placement_n,
                    sequence_n_start=sequence_n_start,
                    sequence_n_end=sequence_n_end
                ))
            self.db_connection.commit()
            return (res_ticket.lastrowid, res_order.lastrowid)
        else:
            return print(
                "You cannot book order a ticket that goes against the direction of the train!")

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
        sekvensNr
        FROM togrute 
        INNER JOIN banestrekning USING(banestrekningId)
        INNER JOIN stasjonPaaStrekning USING(banestrekningId)
        INNER JOIN jernbanestasjon USING(jernbanestasjonId)
        WHERE (togrute.togruteId = {togrute_id_input});
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
