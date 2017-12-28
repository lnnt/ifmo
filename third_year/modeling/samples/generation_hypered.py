import simpy
import random
import xlrd, xlwt
import xlsxwriter

class Generator:

    def __init__(self):
        pass

    def generate_statistics(self, quantity_of_columns, quantity_of_numbers, low_bound, high_bound, params, get_number):
        self.generate(quantity_of_numbers, params, get_number)
        numbers_per_column = int((high_bound - low_bound + 1)/quantity_of_columns)
        start_value = low_bound
        statistics = [[],[]]
        for i in range(1, quantity_of_columns):
            statistics[0].append([start_value, start_value + numbers_per_column - 1])
            statistics[1].append(0)
            start_value += numbers_per_column
        
        statistics[0].append([start_value, high_bound])
        statistics[1].append(0)

        for i in range(len(self.numbers)):
            for j in range(len(statistics[0])):
                if (self.numbers[i] >= statistics[0][j][0] and \
                   self.numbers[i] <= statistics[0][j][1]) or (self.numbers[i] >= statistics[0][j][0] and\
                   j == len(statistics[0]) - 1) or (self.numbers[i] <= statistics[0][j][1] and\
                   j == 0):
                    statistics[1][j] += 1

        return statistics

    def generate(self, quantity, params, get_number):
        env = simpy.Environment()
        env.process(self.write_random_numbers(env, params, get_number))
        env.run(until=quantity)
        return self.numbers

    def write_random_numbers(self, env, params, get_number):
        self.numbers = []
        while True:
            self.numbers.append(get_number(params))
            yield env.timeout(1)

def get_random_exp(params):
    lambd = params[0][0]
    order = params[0][1]
    offset = params[0][2]
    return random.expovariate(1/(lambd - offset)) + offset

def get_random_hxp(params):
    arr = []
    accumulator = 0
    arr.append(0)
    for i in range(len(params)):
        accumulator += params[i][2]
        arr.append(accumulator)

    vr = random.random()
    for i in range(1,len(arr)):
        if vr >= arr[i - 1] and vr < arr[i]:
            return random.expovariate(1/(params[i-1][0] - params[i-1][1])) + params[i-1][1]
    
    return random.expovariate(1/(params[len(params)-1][0] - params[len(params)-1][1])) + params[len(params)-1][1]
    

def get_random_reg(params):
    lambd = params[0][0]
    order = params[0][1]
    offset = params[0][2]
    return int(random.random()*(lambd - offset)*2) + offset

def get_random_erl(params):
    lambd = params[0][0]
    order = params[0][1]
    offset = params[0][2]
    value = 0
    for i in range(order):
        value += random.expovariate(order/(lambd - offset))
    return value + offset

def write_data(worksheet, init_column, statistics, chart, name):
    num_format = workbook.add_format({'bg_color' : '#FF323C', 'font_color' : 'white', 'border_color' : 'white'})
    
    worksheet.merge_range(0, init_column, 0, init_column+1, name)
    
    worksheet.write(1,init_column,"Interval")
    worksheet.write(1,init_column+1,"Quantity")
    
    for i in range(len(statistics[0])):
        worksheet.write(i+2,init_column,"%i - %i" % (statistics[0][i][0],statistics[0][i][1]))
        worksheet.write(i+2,init_column+1,statistics[1][i], num_format)

    chart.add_series({
        'values': [worksheet.name] + [2,init_column+1] + [len(statistics_reg[0])+1, init_column+1],
        'categories': [worksheet.name] + [2,init_column] + [len(statistics_reg[0])+1, init_column],
        'name': name,
    })

if __name__ == "__main__":
    quantity_of_columns = 20
    quantity_of_numbers = 20000
    low_bound = 0
    high_bound = 5000

    generator = Generator()
    statistics_reg = generator.generate_statistics(quantity_of_columns, quantity_of_numbers, low_bound, high_bound, [[1000, 0, 750]], \
                                                   lambda params: get_random_reg(params))
    statistics_exp = generator.generate_statistics(quantity_of_columns, quantity_of_numbers, low_bound, high_bound, [[1000, 0, 750]], \
                                                    lambda params: get_random_exp(params))
    statistics_erl = generator.generate_statistics(quantity_of_columns, quantity_of_numbers, low_bound, high_bound, [[1000, 4, 0]], \
                                                    lambda params: get_random_erl(params))
    statistics_hxp = generator.generate_statistics(quantity_of_columns, quantity_of_numbers, low_bound, high_bound, [[3000, 0, 0.2], [500, 0, 0.8]], \
                                                    lambda params: get_random_hxp(params))
    

    workbook = xlsxwriter.Workbook('new_test1.xlsx')
    chart = workbook.add_chart({'type': 'column'})
    chart.set_y_axis({'name': 'Quantity'})
    chart.set_x_axis({'name': 'Interval'})
    chart.set_title({'name': 'Random numbers'})
    
    worksheet = workbook.add_worksheet()

    write_data(worksheet, 0, statistics_reg, chart, "Regular")
    write_data(worksheet, 3, statistics_exp, chart, "Exponential")
    write_data(worksheet, 6, statistics_erl, chart, "Erlang's")
    write_data(worksheet, 9, statistics_hxp, chart, "Hyperexponential")

    chart.set_size({'width': 720, 'height': 480})
    
    worksheet.insert_chart('M1', chart)
    workbook.close()
    
