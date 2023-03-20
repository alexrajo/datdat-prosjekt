from sqlite3 import Cursor, Connection, connect
from datetime import datetime
import pandas as pd


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

    def find_tickets(self, train_route_id: int, start_station_id: int,
                     end_station_id: int):
        """Finds all available tickets between two stations.

        Parameters:
            train_route_id (int): number corresponding to id of train route 
            which tickets to return.
            start_station_id (int): number corresponding to id of start station.
            end_station_id (int): number corresponding to id of end station.

        Returns:
            A list of tuples containing <attributes>.

            list<(<attribute>: <type>,...)>.
        """
        return NotImplemented

    def get_orders(self, customer_n: int):
        """Gets future orders of a customer.

        Parameters:
            customer_n (int): customer number of customer which orders to 
            return.

        Returns:
            A list of tuples containing <attributes>.

            list<(<attribute>: <type>,...)>.
        """
        return NotImplemented

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
        print(pd.read_sql_query("""
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
        ), self.db_connection))

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
        print(pd.read_sql_query("""
            SELECT 
            togrute.togruteId,  
            rutenavn
            FROM togrute
            INNER JOIN ukedag USING (togruteId) 
            INNER JOIN stopp USING (togruteId)
            INNER JOIN stasjonPaaStrekning USING (banestrekningId, sekvensNr) 
            WHERE ukedag.ukedagNr = {ukedagNr} 
            AND jernbanestasjonId = {jernbanestasjonId};
        """.format(ukedagNr=weekday_n, jernbanestasjonId=station_id), self.db_connection))

    def register_user(
            self, first_name: str, surname: str, email: str, phone_number: str):
        """Registers customer to sqlite database.

        Parameters:
            first_name (str): first name of customer.
            surname (str): surname of customer.
            email (str): email of customer.
            phone_number (str): phone number of customer, 8 numeliterals, 
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
