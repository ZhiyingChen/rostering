from data_structure import Env
from time import time

if __name__ == '__main__':

    st = time()

    env = Env()
    env.read_config()
    env.dig_info()
    env.get_car_schedule()
    env.output()

    print(time() - st)