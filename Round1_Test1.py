from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from collections import deque
import numpy as np

raw_list = deque([], maxlen=50)
moving_average_list = deque([], maxlen=50)
last_buy = 0

pl = 2_000_000

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        print(pl)
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
                # print('Raw List:', raw_list)

                global moving_average_list
                moving_average_list.append(np.average(raw_list))
                # print('Moving Average List: ', moving_average_list)

                price_grad = np.gradient(moving_average_list)
                price_sign = np.sign(price_grad)

                if len(price_sign) <= 20:
                    continue


                # NOTE IMPROVE SPEED
                if moving_average_list[-1] - moving_average_list[0] < 0:
                    acceptable_price = moving_average_list[-1]

                    # # If statement checks if there are any SELL orders in the PEARLS market
                    # if len(order_depth.sell_orders) > 0:

                    #     # Sort all the available sell orders by their price,
                    #     # and select only the sell order with the lowest price
                    #     best_ask = min(order_depth.sell_orders.keys())
                    #     best_ask_volume = order_depth.sell_orders[best_ask]

                    #     # Check if the lowest ask (sell order) is lower than the above defined fair value
                    #     if best_ask < acceptable_price:

                    #         # In case the lowest ask is lower than our fair value,
                    #         # This presents an opportunity for us to buy cheaply
                    #         # The code below therefore sends a BUY order at the price level of the ask,
                    #         # with the same quantity
                    #         # We expect this order to trade with the sell order
                    #         print('ok',best_ask_volume)
                    #         print('huh', (20 - state.position.get('BANANAS', 0), -best_ask_volume))
                    #         buy_amount = min(20 - state.position.get('BANANAS', 0), -best_ask_volume)

                            
                    #         print("BUY", str(buy_amount) + "x", best_ask)
                    #         print(state.position)
                    #         orders.append(Order(product, best_ask, buy_amount))
                            
                    #         global last_buy
                    #         last_buy = best_ask

                    # TODO BANANA LIMIT IS HARD CODED
                    if order := self.buy(state, product, acceptable_price, 20):
                        orders.append(order)

                elif moving_average_list[-1] - moving_average_list[0] > 0:

                    acceptable_price = moving_average_list[-1]

                    # if len(order_depth.buy_orders) != 0:
                    #     best_bid = max(order_depth.buy_orders.keys())
                    #     best_bid_volume = order_depth.buy_orders[best_bid]
                    #     if best_bid > acceptable_price:
                    #         print("SELL", str(best_bid_volume) + "x", best_bid)
                    #         print(state.position)
                    #         orders.append(Order(product, best_bid, -best_bid_volume))

                    if order := self.sell(state, product, acceptable_price, 20):
                        orders.append(order)

                # if state.position.get('BANANAS', 0) :
                #     acceptable_price = last_buy

                #     if len(order_depth.buy_orders) != 0:
                #         best_bid = max(order_depth.buy_orders.keys())
                #         best_bid_volume = order_depth.buy_orders[best_bid]
                #         if best_bid > acceptable_price:
                #             print("SELL", str(best_bid_volume) + "x", best_bid)
                #             print(state.position)
                #             orders.append(Order(product, best_bid, -best_bid_volume))

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
    
    # def trade_pearl(self, state: TradingState) -> Order:
    #     """
    #     This method is used to trade PEARLS
    #     """

    #     buy_price = 9996
    #     sell_price = 10004


    def buy(self, state: TradingState, product: str, acceptable_price: float, limit: int) -> Order:

        order_depth: OrderDepth = state.order_depths[product]
        if len(order_depth.sell_orders) > 0:

            # Sort all the available sell orders by their price,
            # and select only the sell order with the lowest price
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_volume = order_depth.sell_orders[best_ask]

            # Check if the lowest ask (sell order) is lower than the above defined fair value
            if best_ask <= acceptable_price:

                # In case the lowest ask is lower than our fair value,
                # This presents an opportunity for us to buy cheaply
                # The code below therefore sends a BUY order at the price level of the ask,
                # with the same quantity
                # We expect this order to trade with the sell order
                buy_amount = min(limit - state.position.get(product, 0), -best_ask_volume)

                
                print("BUY", str(buy_amount) + "x", best_ask)
                print(state.position)

                global pl
                pl -= buy_amount * best_ask
                return Order(product, best_ask, buy_amount)
        
        return None
    
    def sell(self, state: TradingState, product: str, acceptable_price: float, limit: int) -> Order:

        order_depth: OrderDepth = state.order_depths[product]

        if len(order_depth.buy_orders) != 0:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_volume = order_depth.buy_orders[best_bid]
            if best_bid >= acceptable_price:
                print('sell volume', best_bid_volume)
                sell_amount = min(limit + state.position.get(product, 0), best_bid_volume)
                print("SELL", str(-sell_amount) + "x", best_bid)
                print(state.position)

                global pl
                pl += sell_amount * best_bid
                return Order(product, best_bid, -sell_amount)
            
        return None