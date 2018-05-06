from enum import Enum
from time import time
from collections import deque
import json

class Side(Enum):
    SELL = 0
    BUY = 1

class Order:
    def __init__(self, owner, price, quantity, side):
        self.owner = owner
        self.price = price
        self.quantity = quantity
        self.filled = 0
        self.side = side
        self.created_at = time()  

    def __repr__(self):
        return "{} {} {}@{}".format(self.owner, self.side.name, self.quantity, self.price)

    def unfilled(self):
        return self.quantity - self.filled

class Trade:
    def __init__(self, seller, buyer, quantity, price):
        self.seller = seller
        self.buyer = buyer
        self.quantity = quantity
        self.price = price
        self.time = time()

    @staticmethod
    def validTrade(sell, buy):
        # sanity check
        if sell.side != Side.SELL or buy.side != Side.BUY:
            return False

        # Check the price range
        if sell.price > buy.price:
            return False

        return sell.unfilled() > 0 and buy.unfilled() > 0
    
    @staticmethod
    def create(newOrder, oldOrder):
        """
        creates a trade from two limit orders that can be partially filled. If the new order's
        price doesn't match the current bid/ask, we'll use the current bid/ask as the resulting price

        If this doesn't result in a valid trade None is returned. If a trade is created, the orders are 
        updated as (partially) filled 
        """
        price = oldOrder.price
        quantity = min(oldOrder.unfilled(), newOrder.unfilled())
        
        if Trade.validTrade(newOrder, oldOrder):
            newOrder.filled += quantity
            oldOrder.filled += quantity
            return Trade(newOrder.owner, oldOrder.owner, quantity, price)
        elif Trade.validTrade(oldOrder, newOrder):
            newOrder.filled += quantity
            oldOrder.filled += quantity
            return Trade(oldOrder.owner, newOrder.owner, quantity, price)
        
        return None


class OrderBucket:
    """ 
    OrderBucket is a group of orders with the same price in a linked list structure for quick inserts
    
    >>> ob = OrderBucket(Order('me', 100, 200, Side.BUY))
    >>> ob.add(Order('you', 100, 300, Side.BUY))
    BUY@100: me: 200, you: 300
    """
    def __init__(self, order):
        self.orders = deque([order]) # use a deque, because we are always removing at the start.
        self.price = order.price
        self.side = order.side
        self.next = None

    def add(self, order):
        self.orders.append(order)
        return self

    def head(self):
        return self.orders[0]

    def total(self):
        """
        The total size of this bucket
        """
        return sum(map(lambda x: x.quantity - x.filled, self.orders))


    def __repr__(self):
        return "{}@{}: {}".format(
            self.side.name, 
            self.price, 
            ", ".join(map(lambda x: "{}: {}".format(x.owner, x.quantity), self.orders)))


class OrderBook:
    def __init__(self, tradeSink=[]):
        self.sell = None
        self.buy = None
        self.tradeSink = tradeSink

    @staticmethod
    def fillBucket(order, bucket):
        trades = []
        while bucket:
            head = bucket.orders[0]
            trade = Trade.create(order, head)
            if not trade:
                break

            # if we filled that order we remove it
            if head.unfilled() == 0:
                bucket.orders.popleft()

            if not bucket.orders:
                bucket = bucket.next
            trades.append(trade)
        return trades

    def tryToFill(self, order):
        if order.side == Side.BUY:
            trades = OrderBook.fillBucket(order, self.sell)
            # remove the empty buckets
            while self.sell and not self.sell.orders:
                self.sell = self.sell.next 
        else:
            trades = OrderBook.fillBucket(order, self.buy)
            while self.buy and not self.buy.orders:
                self.buy = self.buy.next 
        
        return trades

    def ask(self):
        return self.sell and self.sell.orders[0].price

    def bid(self):
        return self.buy and self.buy.orders[0].price

    def add(self, order):

        trades = self.tryToFill(order)

        for trade in trades:
            self.tradeSink.append(trade)

        # if the order is immediately filled, we don't have to add it to the book
        if(order.unfilled() == 0):
            return trades

        # Find the right bucket or create
        if order.side == Side.SELL:
            current = self.sell
            compare = lambda x, y: x.price < y.price
        else:
            current = self.buy
            compare = lambda x, y: x.price > y.price

        prev = None
        while current and compare(current, order):
            prev = current
            current = current.next

        if current and current.price == order.price:
            current.add(order)
        else:
            # we create a new bucket as this price range doesn't exists
            bucket = OrderBucket(order)
            bucket.next = current
            current = bucket
            if prev: 
                prev.next = current
            elif order.side == Side.SELL:
                self.sell = current
            else:
                self.buy = current


        return trades

    def getData(self):
        """
        returns the orderbook in a JSON serializable form.
        """
        sells = []
        s = self.sell
        while s:
            sells.append({
                'price': s.price, 
                'total': s.total()
            })
            s = s.next

        buys = []
        b = self.buy
        while b:
            buys.append({
                'price': b.price, 
                'total': b.total()
            })
            b = b.next

        return {
            'bid': self.bid(),
            'ask': self.ask(),
            'sells': sells,
            'buys': buys
        }
