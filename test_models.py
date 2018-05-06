from models import Side, Order, Trade, OrderBook

# Helpers to create Orders:
def createBuy(owner='me', price=100, quantity=100):
    return Order(owner, price, quantity, Side.BUY)

def createSell(owner='me', price=100, quantity=100):
    return Order(owner, price, quantity, Side.SELL)

class TestTrade:
    def test_invalid_trade(self):
        buy = createBuy()

        # Orders shouldn't should only fill to opposing side
        assert not Trade.create(buy, buy)

        # Order shouldn't match if the prices don't intersect
        assert not Trade.create(buy, createSell(price=101))

    def test_completely_filled(self):
        # Same size orders should fill each other completely
        buy = createBuy()
        sell = createSell()
        trade = Trade.create(buy, sell)
        assert trade
        assert trade.quantity == sell.quantity
        assert buy.unfilled() == 0
        assert sell.unfilled() == 0
    
    def test_partially_filled(self):
        # Same size orders should fill each other completely
        buy = createBuy(quantity=200)
        sell = createSell()
        trade = Trade.create(buy, sell)
        assert trade
        assert trade.quantity == sell.quantity
        assert buy.unfilled() == 100
        assert sell.unfilled() == 0

        sell = createSell(quantity=300)
        trade = Trade.create(buy, sell)
        assert trade
        assert trade.quantity == 100
        assert buy.unfilled() == 0
        assert sell.unfilled() == 200
        
class TestOrderBook:
    def test_add(self):
        ob = OrderBook()
        ob.add(createBuy('you', 100, 10))
        ob.add(createSell('me', 110, 10))
        assert ob.bid() == 100
        assert ob.ask() == 110
        # The best buy and sell offer should always be at the top
        ob.add(createBuy('you', 104, 20))
        ob.add(createSell('you', 106, 20))
        assert ob.bid() == 104
        assert ob.ask() == 106
        
    def test_fill_immediately(self):
        ob = OrderBook()
        ob.add(createBuy('you', 100, 10))
        ob.add(createSell('me', 100, 20))
        assert not ob.bid()
        assert ob.ask() == 100
