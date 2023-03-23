from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from collections import deque
import numpy as np

raw_list_banana = deque([], maxlen=50)
moving_average_banana = deque([], maxlen=100)
last_buy_banana = 0

raw_list_pearls = deque([], maxlen=50)
moving_average_pearls = deque([], maxlen=100)
last_buy_pearls = 0

raw_list_coco = deque([], maxlen=50)
moving_average_coco = deque([], maxlen=100)
last_buy_coco = 0

raw_list_pina = deque([], maxlen=50)
moving_average_pina = deque([], maxlen=100)
last_buy_pina = 0

pl = 2_000_000

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        print(pl, state.position)
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                ##############
                global raw_list_banana
                raw_list_banana.append(min(order_depth.sell_orders.keys()))
                # print('Raw List:', raw_list)

                global moving_average_banana
                moving_average_banana.append(np.average(raw_list_banana))
                # print('Moving Average List: ', moving_average_list)

                short_trend = self.trend(np.array(moving_average_banana), 15)
                long_trend = self.trend(np.array(moving_average_banana), 100)

                # print(f'Long Trend: {long_trend}, Short Trend: {short_trend}')

                if long_trend == -1 and short_trend == 1:
                    acceptable_price = moving_average_banana[-1] + 3

                    # TODO BANANA LIMIT IS HARD CODED
                    if order := self.buy(state, product, acceptable_price, 20):
                        orders.append(order)

                elif long_trend == 1 and short_trend == -1:

                    acceptable_price = moving_average_banana[-1] - 3
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

                # Add all the above orders to the result dict
                result[product] = orders


            # NOTE: KUNJ CODE
            if product == "PEARLS":
                pearl_orders = self.trade_pearls(state)
                result[product] = pearl_orders

            # NOTE: ROB CODE
            # if product == "PEARLS":
            #     pearl_limit = 20
            #     our_buy_price = 9996
            #     our_sell_price = 10004

            #     if order := self.sell(state, product, our_sell_price, pearl_limit):
            #         orders.append(order)

            #     if order := self.buy(state, product, our_buy_price, pearl_limit):
            #         orders.append(order)

            #     result[product] = orders

        return result
    

    def trade_pearls(self, state: TradingState) -> Order:
        """
        This method is used to trade PEARLS
        """
        pearl_limit = 20
        our_buy_price = 9996
        our_sell_price = 10004

        order_depth: OrderDepth = state.order_depths["PEARLS"]

        # Initialize the list of Orders to be sent as an empty list
        orders: list[Order] = []
        
        #### BUYING #####
        # sell_prices will be something like [10004, 10005]
        sell_prices = order_depth.sell_orders.keys()

        # ordering would now make it [10004, 10005]
        ordered_sell_prices = sorted(sell_prices)
        
        for offer in ordered_sell_prices:
            if offer <= our_buy_price:
                # We want to buy it
                order = self.buy(state, "PEARLS", offer, pearl_limit)
                orders.append(order)
        
        #### SELLING #####
        buy_prices = order_depth.buy_orders.keys()
        ordered_buy_prices = sorted(buy_prices, reverse=True)

        for buy_price in ordered_buy_prices:
            if buy_price >= our_sell_price:
                # We want to sell
                order = self.sell(state, "PEARLS", buy_price, pearl_limit)
                orders.append(order)
        
        return orders


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
                sell_amount = min(limit + state.position.get(product, 0), best_bid_volume)
                print("SELL", str(-sell_amount) + "x", best_bid)
                print(state.position)

                global pl
                pl += sell_amount * best_bid
                return Order(product, best_bid, -sell_amount)
            
        return None
    
    def trend(self, ma: np.array, cut_off: int, up_lim=0, down_lim=0) -> int:
        '''
        This method is used to calculate the long trend using the last cut off moving average which is based on 50 raw values
        '''
        if len(ma) < cut_off:
            return 0
        
        if np.diff(ma[-cut_off:]).sum() > up_lim:
            return 1
        
        elif np.diff(ma[-cut_off:]).sum() < down_lim:
            return -1
        
        else:
            return 0


