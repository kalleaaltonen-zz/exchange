from models import OrderBook, Order, Side
from random import randint, gauss
from time import time
from tqdm import tqdm


# For the stress test we just count the made trades
class DummySink:
    def __init__(self):
        self.count = 0

    def append(self, item):
        self.count += 1
        pass


s = DummySink()
ob = OrderBook(s)

def random_order(mean_price):
    side = Side(randint(0, 1))
    # we shift sell orders up 1% from mean and buy orders down, to give more realistic distribution
    mean_price *= 1.01 if Side.SELL else 0.99

    price = int(gauss(mean_price, mean_price * 0.1))
    quantity = randint(0, 1000)
    return Order('dummy', price, quantity, side)


N = 1000000
start = time()
for n in tqdm(range(N)):
    ob.add(random_order(1000))

took = time() - start
print(str(s.count) + " trades in " + str(took) + " seconds " + str(N / (took)) + " per second")
