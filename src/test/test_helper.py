def extract_number_from_kpi(data_file, kpi):
    # Open file in read only mode
    # f = open(data_file, 'r')
    lines = get_list_line_from_kpi(data_file, kpi)

def extract_value_from_line(line):
    return float(line.split()[-1])

# return list of line acording to kpi
def get_list_line_from_kpi(data_file, kpi):
    res = []
    with open(data_file, 'r') as f:
        for line in f:
            if kpi in line:
                res.append(line)
    return res

def get_list_line_from_kpi_with_ident(data_file, kpi, ident):
    res = []
    with open(data_file, 'r') as f:
        for line in f:
            if kpi in line and ident in line:
                res.append(line)
    return res