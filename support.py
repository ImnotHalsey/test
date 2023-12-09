import re, pdfplumber,os 
import random
import string
import pandas as pd


def files_processor(downloaded_file, option, code=None):
    # Specify the directory for PDF files
    pdf_directory = os.path.join(os.path.expanduser("~"), "Documents", "bot", "test", "pdf")
    os.makedirs(pdf_directory, exist_ok=True)

    # Generate a unique name for the PDF file
    pdf_filename = f'{BankStatementProcessor.generate_random_name()}_file.pdf'
    pdf_path = os.path.join(pdf_directory, pdf_filename)

    try:
        with open(pdf_path, 'wb') as f:
            f.write(downloaded_file)
    except Exception as e:
        print(f"Error writing to file: {e}")
        
    if option == "IDFC":  # IDFC
        dfs = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table is not None:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    dfs.append(df)
                else:
                    print("An Error Occured")


        data = pd.concat(dfs)
        data.drop(['Value Date', 'Cheque\nNo', 'A2A', 'Account to Account'], axis=1,inplace=True)
        data['Debit'] = data['Debit'].str.replace(',', '')
        data['Credit'] = data['Credit'].str.replace(',', '')
        data['Balance'] = data['Balance'].str.replace(',', '')
        for column in ['Debit', 'Credit', 'Balance']:
            data[column] = pd.to_numeric(data[column],errors='coerce').fillna(0)
        data['UTR'] = [BankStatementProcessor.extract_data_from_text(value) for value in data['Particulars']]
        total_summary = {
            'Total Credit': data['Credit'].sum(),
            'Total Debit': data['Debit'].sum(),
            'Total Transactions': len(data[data['UTR'].str.len() > 4]),
            "total credit Transactions": (data['Credit'] > 0).sum(),
            "total debit Transactions": (data['Debit'] > 0).sum()}
        return data,total_summary,option
    
    elif option == "Bank Of Baroda":  # Bank of Baroda 
        dfs = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for pages in table:
                        dfs.append(pages)

        dfs = dfs[2:]
        columns = ["DATE", "UTR", "Debit", "Credit", "Balance"]
        df = pd.DataFrame(columns=columns)
        for entry in dfs:
            new_data = BankStatementProcessor.maker(entry)
            new_df = pd.DataFrame([new_data])
            df = pd.concat([df, new_df], ignore_index=True) 
        total_summary = {
            'Total Credit': df['Credit'].sum(),
            'Total Debit': df['Debit'].sum(),
            'Total Transactions': len(df),
            "total credit Transactions": (df['Credit'] > 0).sum(),
            "total debit Transactions": (df['Debit'] > 0).sum()}
        return df,total_summary,option

    elif option  == "ICICI Bank":  # ICICI Bank
        dfs = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                for i in table:
                    dfs.append(i)

        df = pd.DataFrame(dfs[1:], columns=dfs[0])
        df = df.rename(columns={'Sr No':'Serial_Number','Transactio\nn Date': 'Transaction Date','Cheque\nNumber': 'UTR','Transactio\nn Remarks': 'Transaction Remarks','Debit\nAmount':'Debit','Credit\nAmount':'Credit','Balance(IN\nR)':'Balance'})
        cols_to_replace = ['Balance', 'Transaction Date']
        df[cols_to_replace] = df[cols_to_replace].replace({r'\n3': '', r'\n': ''}, regex=True)
        cols = ['Credit', 'Debit']
        df[cols] = df[cols].replace('NA', 0)
        df = df.drop(columns=['Value Date'])
        for column in ['Debit','Credit', 'Balance']:
            df[column] = pd.to_numeric(df[column],errors='coerce').fillna(0)
        total_summary = {
            'Total Credit': df['Credit'].sum(),
            'Total Debit': df['Debit'].sum(),
            'Total Transactions': len(df),
            "total credit Transactions": (df['Credit'] > 0).sum(),
            "total debit Transactions": (df['Debit'] > 0).sum()}
        return df,total_summary,option

    elif option  =="State Bank of India":  # State Bank of India
        dfs = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table is not None and len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    dfs.append(df)

        data = pd.concat(dfs)
        cols = ["Date", "UTR", "Credit", "Debit", "Balance"]
        s_data = pd.DataFrame(columns=cols)
        s_data['Date'] = data['Txn\nDate'].replace('\n', '') if 'Txn\nDate' in data else data['Txn Date']
        s_data['UTR'] = data['Description']
        s_data['Credit'] = data['Credit'].str.replace(',', '').replace('', '0').astype(float)
        debit_values = data['Debit'].str.replace(',', '').str.replace('\n', '').str.strip().replace('', '0')
        s_data['Debit'] = debit_values.astype(float)
        s_data['Balance'] = data['Balance'].str.replace(',', '').replace('', '0').astype(float)
        total_summary = {
            'Total Credit': s_data['Credit'].sum(),
            'Total Debit': s_data['Debit'].sum(),
            'Total Transactions': len(s_data),
            'total credit Transactions': (s_data['Credit'] > 0).sum(),
            'total debit Transactions': (s_data['Debit'] > 0).sum()}
        return s_data,total_summary,option

    elif option == "Union Bank": # Union Bank
        tables = []
        cols = ['Date', 'Transaction_ID', 'Remarks', 'Amount(Rs.)', 'Balance']
        with pdfplumber.open(pdf_path, password=code) as pdf:
            for page in pdf.pages:
                table = page.extract_tables()
                tables.extend(table)
        data_rows = []
        data_row = []
        for i in tables[0][5:-2]:
            data_rows.append(i[2:-1])
        cleaned_list = [[item for item in sublist if item is not None] for sublist in data_rows]
        cleaned_list = [row for row in cleaned_list if row[0] and row[1] and row[0].strip() != "" and row[1].strip() != ""]
        for table in tables[1:]:
            if table[0] == [None, 'Date', 'Transaction Id', 'Remarks', 'Amount(Rs.)', None]:
                for row in table[1:]:
                    cleaned_list.append(row[1:])

        final = pd.DataFrame(data=cleaned_list[:-1], columns=['Date', 'UTR','Remarks','Debit/Credit','Balance'])
        final['Balance'] = final['Balance'].str.replace(r'\([^)]*\)', '', regex=True)
        final['Debit/Credit'] = final['Debit/Credit'].str.replace(r'\([^)]*\)', '', regex=True)
        final = final.drop(columns=['Remarks'])
        total_summary = {'Total Transactions': len(final)}
        return final,total_summary,option

    elif option == "CSB": # CSB
        tables = []
        with pdfplumber.open(pdf_path, password=code) as pdf:
            tables = [page.extract_tables() for page in pdf.pages]

        cols = tables[0][0][0]
        x_values = [row for row in tables[0][0][2:]]
        z_values = [z for table in tables[1:] for row in table for z in row]
        df = pd.DataFrame(x_values + z_values, columns=cols)
        df.drop(columns=['Cheque No', 'Value Date'], inplace=True)
        c_cols = ['Withdrawal', 'Deposit', 'Balance']

        for i in c_cols:
            df[i] = df[i].str.replace(',', '')
            df[i] = pd.to_numeric(df[i], errors='coerce')
            
        total_summary = {'Total Credit': df['Deposit'].sum(), 'Total Debit': df['Withdrawal'].sum(), 'Total Transactions': len(df), 'total credit Transactions': (df['Deposit'] > 0).sum(), 'total debit Transactions': (df['Withdrawal'] > 0).sum()}

        return df,total_summary,option  
    else:
        print("Option out of availability")

def excel_processor(df,option):
    if option == "SIB":
        df = df[:-1].copy()
        df['UTR'] = df['Particulars'].apply(BankStatementProcessor.extract_info)
        columns_to_clean = ['Withdrawals', 'Deposits', 'Balance Amount']
        for column in columns_to_clean:
            df[column] = df[column].replace(',', '', regex=True).astype(float)
        df.drop(columns=['Unnamed: 4', 'Unnamed: 7', 'Value Date', 'Cheque Number', 'Particulars'], inplace=True)
        df.loc[:, ['Withdrawals', 'Deposits', 'Balance Amount']] = df[['Withdrawals', 'Deposits', 'Balance Amount']].apply(pd.to_numeric, errors='coerce')
        df.loc[:, :] = df.fillna(0)
        total_summary = {
            'Total Credit': df['Deposits'].sum(),
            'Total Debit': df['Withdrawals'].sum(),
            'Total Transactions': len(df),
            'total credit Transactions': (df['Deposits'] > 0).sum(),
            'total debit Transactions': (df['Withdrawals'] > 0).sum()}
        return df,total_summary,option

    elif option == "HDFC":
        matter = BankStatementProcessor.hdfc_processor(df)
        matter = matter.drop(columns=['Narration', 'Value Dt'], errors='ignore')
        matter.fillna(0, inplace=True)  
        listt = ['Withdrawal Amt.','Deposit Amt.']
        for i in listt:
            matter[i] = pd.to_numeric(matter[i], errors='coerce')
        total_summary = {
            'Total Credit': matter['Deposit Amt.'].sum(),
            'Total Debit': matter['Withdrawal Amt.'].sum(),
            'Total Transactions': len(matter),
            'total credit Transactions': (matter['Deposit Amt.'] > 0).sum(),
            'total debit Transactions': (matter['Withdrawal Amt.'] > 0).sum()}
        return matter,total_summary,option


class BankStatementProcessor:
    @staticmethod
    def generate_random_name():
        return ''.join(random.choices(string.ascii_lowercase, k=4))

    @staticmethod
    def maker(data):
        pattern1 = r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(\d[\d,]+\.\d{2})\s+([\d,]+\.\d{2})Cr'
        pattern2 = r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(\d+\.\d{2})\s+([\d,]+\.\d{2})Cr$'
        pattern3 = r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+([\d,]+\.\d{2})Cr\n([\d,]+\.\d{2})'
        entry_dicts = []  
        for entry in data:
            match1 = re.match(pattern1, entry)
            match2 = re.match(pattern2, entry)
            match3 = re.match(pattern3, entry)

            if match1:
                date = match1.group(1)
                narration = match1.group(2)
                withdrawal = '0'
                deposit = match1.group(3)
                balance = match1.group(4)
            elif match2:
                date = match2.group(1)
                narration = match2.group(2)
                withdrawal = match2.group(3)
                deposit = '0'
                balance = match2.group(4)
            elif match3:
                date = match3.group(1)
                narration = match3.group(2)
                balance = match3.group(3)
                deposit = '0'
                withdrawal = match3.group(4)
            else:
                print("No match found for:", entry)
                continue  

            entry_dict = {
                "DATE": date,
                "NARRATION": narration,
                "WITHDRAWAL": float(withdrawal.replace(',', '').replace("'", '')),
                "DEPOSIT": float(deposit.replace(',', '').replace("'", '')),
                "BALANCE": float(balance.replace(',', '').replace("'", ''))
            }

            entry_dicts.append(entry_dict)  # Append the entry dictionary to the list

        return entry_dicts

    @staticmethod
    def extract_data_from_text(text):
        if isinstance(text, str):
            keys = ['Category', 'Type', 'Number', 'Description']
            values = text.split('/')
            data = {key: value for key, value in zip(keys, values)}
            number = data.get('Number', '')
            return number
        else:
            return ''

    @staticmethod
    def extract_info(text):
        patterns = [re.compile(r'IMPS - imps p2a - (\d+)'), re.compile(r'/(\d+)/'), re.compile(r'(\d+)\/')]
        if isinstance(text, str):
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    return match.group(1)
        return None

    @staticmethod
    def hdfc_processor(df):
        new_column_names = ['Date', 'Narration', 'Chq./Ref.No.', 'Value Dt', 'Withdrawal Amt.', 'Deposit Amt.','Closing Balance']
        pattern = r"^\d{2}/\d{2}/\d{2}$"
        if len(new_column_names) == len(df.columns):
            df.columns = new_column_names
            start_point = None
            for index, row in df.iterrows():
                if row.tolist() == new_column_names:
                    start_point = index + 2
            end_index = None
            for index, row in df.iloc[start_point:].iterrows():
                if not re.match(pattern, str(row.iloc[0])):
                    end_index = index
                    break
            if start_point is not None and end_index is not None:
                data = df[start_point:end_index]
                return data
            else:
                print("Matching rows not found or pattern not matched.")
        else:
            print("Column name mismatch.")