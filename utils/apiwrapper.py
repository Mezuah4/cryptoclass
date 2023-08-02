# Blockchain.com API Wrapper
# Andrei-Mihail Rotariu
# 51876039

# Core
from IPython.display import clear_output

# Data
import time
import numpy as np
import sqlite3

# API Interaction
import requests

# Exceptions
from json import JSONDecodeError


class APICaller:

    def __init__(self, delay, db_path):
        self._db_conn = sqlite3.connect(db_path)
        self._db_cur = self._db_conn.cursor()
        self._create_table()
        self._delay = delay

    def _create_table(self):
        try:
            self._db_cur.execute(
                "CREATE TABLE addr(Address, Total_Rec, Total_Sent, Balance, N_TX, N_Rec, N_Sent, Avg_Rec, Min_Rec, "
                "Max_Rec, Avg_Sent, Min_Sent, Max_Sent, Time_Between_FirstLast, Avg_Delta_Rec, "
                "Min_Delta_Rec, Max_Delta_Rec, Avg_Delta_Sent, Min_Delta_Sent, Max_Delta_Sent, "
                "Unique_Rec, Unique_Sent, Month)"
            )
            self._db_conn.commit()
        except sqlite3.OperationalError as e:
            print(e)

    @staticmethod
    def _get_amounts(addr, txs):

        rec = []
        sent = []
        for transaction in txs:
            for out in transaction['out']:
                if addr == out['addr']:
                    rec.append(out['value'])

            for inp in transaction['inputs']:
                if addr == inp['prev_out']['addr']:
                    sent.append(inp['prev_out']['value'])

        if len(rec) == 0:
            rec.append(0)

        if len(sent) == 0:
            sent.append(0)

        return rec, sent

    @staticmethod
    def _get_times(addr, txs):

        rec = []
        sent = []

        for transaction in txs:
            for out in transaction['out']:
                if addr == out['addr']:
                    rec.append(transaction['time'])

            for inp in transaction['inputs']:
                if addr == inp['prev_out']['addr']:
                    sent.append(transaction['time'])

        return sorted(rec), sorted(sent)

    @staticmethod
    def _get_time_feats(rec, sent):

        # Concat List
        times = sorted(rec + sent)

        # Time Range
        time_range = 0
        if len(times) != 0:
            time_range = max(times) - min(times)

        # Time Deltas
        rec_deltas = []
        if len(rec) > 2:
            rec_deltas = [(rec[i] - rec[i - 1]) for i in range(1, len(rec))]

        sent_deltas = []
        if len(sent) > 2:
            sent_deltas = [(sent[i] - sent[i - 1]) for i in range(1, len(sent))]

        # Delta Feats
        if len(rec_deltas) > 1:
            avg_rec_d, min_rec_d, max_rec_d = sum(rec_deltas) / len(rec_deltas), min(rec_deltas), max(rec_deltas)
        elif len(rec_deltas) == 1:
            avg_rec_d = min_rec_d = max_rec_d = rec_deltas[0]
        else:
            avg_rec_d = min_rec_d = max_rec_d = 0

        if len(sent_deltas) > 1:
            avg_sent_d, min_sent_d, max_sent_d = sum(sent_deltas) / len(sent_deltas), min(sent_deltas), max(sent_deltas)
        elif len(sent_deltas) == 1:
            avg_sent_d = min_sent_d = max_sent_d = sent_deltas[0]
        else:
            avg_sent_d = min_sent_d = max_sent_d = 0

        return time_range, avg_rec_d, min_rec_d, max_rec_d, avg_sent_d, min_sent_d, max_sent_d

    @staticmethod
    def _get_unique_counts(addr, txs):

        rec = []
        sent = []

        for transaction in txs:
            for inp in transaction['inputs']:
                if addr != inp['prev_out']['addr']:
                    rec.append(inp['prev_out']['addr'])

            for out in transaction['out']:
                if addr != out['addr']:
                    sent.append(out['addr'])

        # Return Only Unique
        return set(sorted(rec)), set(sorted(sent))

    @staticmethod
    def _request_address(addr):

        # Target URL
        url = "https://blockchain.info/rawaddr/"

        # Make Request
        resp = requests.get(url + addr)

        # Return Output
        return resp

    def _add_to_db(self, dat, m=None):

        # Extract Data From JSON
        rec_amounts, sent_amounts = self._get_amounts(dat['address'], dat['txs'])
        n_rec, n_sent = len(rec_amounts), len(sent_amounts)
        rec_times, sent_times = self._get_times(dat['address'], dat['txs'])
        time_dat = self._get_time_feats(rec_times, sent_times)
        unique_rec, unique_sent = self._get_unique_counts(dat['address'], dat['txs'])

        # Format Dataframe Input
        df_inp = {'Address': dat['address'], 'Total_Rec': dat['total_received'], 'Total_Sent': dat['total_sent'],
                  'Balance': dat['final_balance'], 'N_TX': dat['n_tx'], 'N_Rec': n_rec, 'N_Sent': n_sent,
                  'Avg_Rec': np.mean(rec_amounts), 'Min_Rec': min(rec_amounts), 'Max_Rec': max(rec_amounts),
                  'Avg_Sent': np.mean(sent_amounts), 'Min_Sent': min(sent_amounts), 'Max_Sent': max(sent_amounts),
                  'Time_Between_FirstLast': time_dat[0], 'Avg_Delta_Rec': time_dat[1], 'Min_Delta_Rec': time_dat[2],
                  'Max_Delta_Rec': time_dat[3], 'Avg_Delta_Sent': time_dat[4], 'Min_Delta_Sent': time_dat[5],
                  'Max_Delta_Sent': time_dat[6], 'Unique_Rec': len(unique_rec), 'Unique_Sent': len(unique_sent),
                  "Month": None}

        # Add Month if Provided
        if m is not None:
            df_inp['Month'] = m

        # Add to DB
        self._db_cur.execute(
            "INSERT INTO addr VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            list(df_inp.values()))

        self._db_conn.commit()

    def extract_info(self, addresses, months=None):
        """Extracts Blockchain.info Data for a list of Bitcoin Addresses.
        Loops through list of NordVPN SOCKS5 Proxy Servers for Each API Request.
        Returns Dataframe of Data."""

        # Loop Through Addresses
        for i in range(len(addresses)):

            # Make Request
            resp = self._request_address(addresses[i])

            # Update Terminal
            clear_output(wait=True)
            print("Current Address: ", i, " Status: ", resp.status_code)
            print("Addresses Remaining: ", len(addresses) - i)
            print("Percentage: ", round((i / len(addresses)) * 100, 2), "%")

            # Add Address Data to Dataframe
            if resp.status_code == 200:
                try:
                    data = resp.json()

                    if months is not None:
                        self._add_to_db(data, months[i])
                    else:
                        self._add_to_db(data)

                except (JSONDecodeError, KeyError):
                    pass

            time.sleep(self._delay)


class SuspChecker:

    def __init__(self):
        self._api_token = "kQUtq7V2Cce6Gi6SCGbPCHveLdMGwvZADPAwIxpe"

    def is_suspicious(self, address):
        # Format URL
        target_url = f"https://www.bitcoinabuse.com/api/reports/check?address={address}&api_token={self._api_token}"

        # Call Limit
        time.sleep(2)

        # Make Request
        res = requests.get(target_url)

        if res.status_code != 200:
            # Ignore Address if API Fails
            return True
        elif res.json()['count'] > 0:
            return True
        else:
            return False
