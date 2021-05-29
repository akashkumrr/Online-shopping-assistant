import schedule
import time
from price_notifier import scan_prices_and_notify
from price_notifier import total_products_in_notification_list


# run_interval automatically acoomodates for the time consumed in running the function
# On average it takes 8 seconds to check a products price once.
# total_time_for_price_checking = total_products_in_notification_list()*10
# print(total_time_for_price_checking) 

#run_interval = 0.5 means script would run every half second
run_interval = 5

schedule.every(run_interval).seconds.do(scan_prices_and_notify,True)

while 1:
    schedule.run_pending()
    print("Waiting for next scheduled scanning of prices... ")
    time.sleep(0.5)
    # use time.sleep() to check for code at reasonable interval else it'll check for pending job every frame