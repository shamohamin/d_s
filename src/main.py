from database.query_executer import Database as DB
from utils.worker import Worker

if __name__ == '__main__':
    db = DB()
    Worker(db=db, base_url="https://rahavard365.com/stock").run_program()
    # db.execute(file="create_table.sql")
    # db.execute(query="SELECT * from stocks")
    # re = RequestHandler(db, "https://rahavard365.com/stock")
    # params = {
    #     'last_trade': 'any'
    # }
    # print(params['last_trade'])
    # re.make_request(params)
    # re.execute(params)
    # with ThreadPoolExecutor(max_workers=6) as executor:
        # for index in range(4);


            
    
