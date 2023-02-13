from driver import Driver

class UC:
    @staticmethod
    def input(msg:str=None, return_type=str):
        while True:
            try:
                return return_type(input(msg))
            except (TypeError, ValueError) as e:
                Driver.Logging.failed("The input must be convertable to type {}!".format(return_type.__name__))
                raise e
            except Exception as e:
                raise e