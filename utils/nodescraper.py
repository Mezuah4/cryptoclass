from IPython.display import clear_output
from bitcoinrpc.authproxy import AuthServiceProxy
import random


class AddressSampler:

    def __init__(self, r_user, r_pass, heights):
        self._heights = heights     # Dataframe (Start Height, Month, Year)
        self._user = r_user         # RPC Username
        self._pass = r_pass         # RPC Password
        self._address_list = []     # Output

    def _rand_address(self, st, en, r):

        out = None
        while out is None:

            try:
                # Select Random Block
                block = random.randint(st, en - 1)

                # Get BlockHash
                block_hash = r.getblockhash(block)

                # Get TX List
                tx_list = r.getblock(block_hash)['tx']

                # Choose Random Transaction
                tx_i = random.randint(0, len(tx_list) - 1)
                tx = r.getrawtransaction(tx_list[tx_i], True)

                # Count Inputs/Outputs
                len_i, len_o = len(tx['vin']), len(tx['vout'])

                # Select Inputs or Outputs
                coin = random.randint(0, 1)

                # Select Random Input/Output Address
                if coin == 0:
                    out = tx['vout'][random.randint(0, len_o - 1)]['scriptPubKey']['address']
                else:
                    inp = tx['vin'][random.randint(0, len_i - 1)]
                    prev_tx = inp['txid']
                    prev_vout = inp['vout']
                    prev_tx = r.getrawtransaction(prev_tx, True)
                    out = prev_tx['vout'][prev_vout]['scriptPubKey']['address']

                # Skip if Duplicate
                if out in [x["Address"] for x in self._address_list]:
                    out = None

            except KeyError:
                continue

        return out

    def get_list(self):
        return self._address_list

    def sample_month(self, n, month, year, as_sub=False):

        # Establish RPC Connection
        rpc = AuthServiceProxy(f"http://{self._user}:{self._pass}@127.0.0.1:8332")

        # Get Block Height Range
        start_index = self._heights.loc[(self._heights['Month'] == month) & (self._heights['Year'] == year)].index
        end_index = start_index + 1
        start = list(self._heights['Height'][start_index])[0]
        end = list(self._heights['Height'][end_index])[0]

        # Make N Samples
        for i in range(n):
            res = self._rand_address(start, end, rpc)
            self._address_list.append({"Address": res, "Month": month, "Year": year})

            # Update Terminal
            if not as_sub:
                clear_output(wait=True)
                print(f'Sampling Addresses For {month}/{year}.')
                print("Sampled: ", i)
                print("Remaining: ", (n - i))

        # Return List of Records
        if not as_sub:
            return self._address_list

    def sample_year(self, n, y):

        for i in range(n):
            mo = random.randint(1, 12)
            _ = self.sample_month(1, mo, y, as_sub=True)[0]

            # Update Terminal
            clear_output(wait=True)
            print(f'Sampling Addresses For {y}.')
            print("Sampled: ", i + 1)
            print("Remaining: ", (n - i - 1))

        return self._address_list
