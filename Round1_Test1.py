from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from collections import deque
import numpy as np

raw_list = deque([], maxlen=50)
moving_average_list = deque([], maxlen=50)


class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                ##############
                global raw_list
                raw_list.append(min(order_depth.sell_orders.keys()))
                print('Raw List:', raw_list)

                global moving_average_list
                moving_average_list.append(np.average(raw_list))
                print('Moving Average List: ', moving_average_list)

                price_grad = np.gradient(moving_average_list)
                price_sign = np.sign(price_grad)

                if len(price_sign) <= 20:
                    continue


                # NOTE IMPROVE SPEED
                last_sign, cur_sign = price_sign[-20], price_sign[-1]
                if moving_average_list[-1] - moving_average_list[0] < 0:
                    print("Sell", state.timestamp, order_depth.buy_orders)
                    if len(order_depth.buy_orders) != 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = order_depth.buy_orders[best_bid]

                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                elif moving_average_list[-1] - moving_average_list[0] > 0:
                    print("Buy", state.timestamp, order_depth.sell_orders)
                    if len(order_depth.sell_orders) > 0:
                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = order_depth.sell_orders[best_ask]

                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))


                '''
                Next steps:
                Calculate average
                Maintain deque for smoothed values
                Write a function for momentum trading
                '''


                # Add all the above orders to the result dict
                result[product] = orders

            # Return the dict of orders
            # These possibly contain buy or sell orders for PEARLS
            # Depending on the logic above
        return result