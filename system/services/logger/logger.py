import datetime
import traceback


class Logger:
    def err_logg(self, path, status, err):
        tb = traceback.extract_tb(err.__traceback__)
        error_path = ''
        for i in range(len(tb)):
            filename, line, func, text = tb[i]
            error_path += f'{filename} ({line} line); code: {text} -> '

        with open(f'./logs/strategy/{path}.txt', 'a',
                  encoding="utf-8") as file:
            file.write(f'{datetime.datetime.now()} [{status}]: Exception text: {err}; error path: {error_path[:-5]} \n')
            file.close()

    def logger(self, path, status, text):
        with open(f'./logs/strategy/{path}.txt', 'a', encoding="utf-8") as file:
            file.write(f'{datetime.datetime.now()} [{status.upper()}]: {text}\n')
            file.close()
