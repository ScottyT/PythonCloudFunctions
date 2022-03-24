import xlsxwriter
import os
from datetime import date, datetime
from google.cloud import storage

def search(list, search_term):
    for i in range(len(list)):
        if list[i] == search_term:
            return True
    return False

def create_excel(timesheet_data):
    file_name = timesheet_data["filename"]
    jobdate_arr = timesheet_data["dateArr"]
    tech_sheets = timesheet_data["techByDate"]
    env = os.environ.get("PYTHON_ENV")
    cell_names = ['C1', 'D1', 'E1', 'F1']
    eval_names = ["Travel In","Team Arrival","Time In","Time Out"]
    location = os.path.join(os.path.expanduser('~'), 'Timesheets')
    isExist = os.path.exists(os.path.join(os.path.expanduser('~'), 'Timesheets'))
    if not isExist:
        os.makedirs(location)
    outWorkbook = xlsxwriter.Workbook(os.path.join(location, file_name))
    row = 1
    bold = outWorkbook.add_format({'bold': True})
    time_format = outWorkbook.add_format({'num_format': 'hh:mm AM/PM'})
    duration_format = outWorkbook.add_format({'num_format': 'hh:mm:ss'})
    date_format = outWorkbook.add_format({'num_format': 'mm/dd/yyyy'})
    sheet_names = []

    for date_index in jobdate_arr:
        sheet_names.append("{}".format(date_index))
    for name in sheet_names:
        outSheet = outWorkbook.add_worksheet("{}".format(name))
        getSheet = outWorkbook.get_worksheet_by_name("{}".format(outSheet.get_name()))
        if search(sheet_names, getSheet.get_name()):
            getSheet.write("A1", "Name", bold)
            getSheet.write("B1", "Date", bold)
            getSheet.write("G1", "Travel Time", bold)
            getSheet.write("H1", "Project Hours", bold)
            getSheet.write("I1", "Total Time", bold)
            day_reports = tech_sheets[getSheet.get_name()]
            for rep in day_reports:
                emp_dict = dict(rep['teamMember'])
                eval_list = list(rep['evaluationLogs'])

                filtered_evals = list(filter(lambda c: c['label'] != 'Total Time', eval_list))
                
                eval_dict = {
                    "Travel In": datetime.strptime(filtered_evals[0]['value'], '%m-%d-%Y %H:%M:%S'),
                    "Team Arrival": datetime.strptime(filtered_evals[1]['value'], '%m-%d-%Y %H:%M:%S'),
                    "Time In": datetime.strptime(filtered_evals[1]['value'], '%m-%d-%Y %H:%M:%S'),
                    "Time Out": datetime.strptime(filtered_evals[2]['value'], '%m-%d-%Y %H:%M:%S')
                }
                getSheet.write(row, 0, emp_dict['name'])
                getSheet.set_column_pixels(0, 0, 120)
                date_time = datetime.strptime(rep['date'], '%m-%d-%Y')
                getSheet.write_datetime(row, 1, date_time, date_format)
                getSheet.set_column_pixels('B:I', 80)

                for index, item in enumerate(eval_names):
                    getSheet.write(cell_names[index], item, bold)

                for key, eval_log in eval_dict.items():
                    index = list(eval_dict).index(key)
                    getSheet.write_datetime(row, index + 2, eval_log, time_format)

                getSheet.write_formula(row, 6, '=TEXT(D%d-C%d, "hh:mm:ss")' % (row + 1, row + 1))
                getSheet.write_formula(row, 7, '=TEXT(F%d-E%d, "hh:mm:ss")' % (row + 1, row + 1))
                getSheet.write_formula(row, 8, '=SUM(H%d+G%d)' % (row + 1, row + 1), duration_format)
                if len(day_reports) > 1:
                    row += 1
    outWorkbook.close()
    return os.path.join(location, file_name)

def list_items(storage_client: storage.Client, storage_bucket, prefix, delimiter):
    iterator = storage_client.list_blobs(storage_bucket, prefix=prefix, delimiter=delimiter)

    my_dict = dict({
        'folders': list(dict([('name', x[:-1]), ('path', x)]) for x in iterator._get_next_page_response()['prefixes']) if delimiter else [], 
        'images': list(dict([('name', y.name), ('imageUrl', "https://firebasestorage.googleapis.com/v0/b/" + storage_bucket + "/o/")]) for y in iterator)
    })

    return my_dict

def list_prefixes(bucket, self, prefix=None):
    iterator = self.list_blobs(delimiter='/', prefix=prefix)
    list(iterator)  # Necessary to populate iterator.prefixes
    for p in iterator.prefixes:
        print(p)
        yield p