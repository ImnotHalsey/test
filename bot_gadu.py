import os,gc,telebot
from telebot import types
from support import files_processor, excel_processor, BankStatementProcessor
import pandas as pd
from io import BytesIO


class PDFProcessor:
    def __init__(self):
        self.bot = telebot.TeleBot("6293447468:AAHlxvdm0kQKR4aU2VFWENTB_4x4fDd4mjY")
        @self.bot.message_handler(commands=['start'])
        def start(message):
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.add(types.KeyboardButton("IDFC"), types.KeyboardButton("Union Bank"),types.KeyboardButton("Bank Of Baroda"),types.KeyboardButton("State Bank of India"), types.KeyboardButton("ICICI Bank"),types.KeyboardButton("SIB"), types.KeyboardButton("HDFC"),types.KeyboardButton("CSB"),types.KeyboardButton("TEXT"),types.KeyboardButton("Get total by Text"))
            user_input = self.bot.reply_to(message," chào bạn\n choose an option:",reply_markup=markup)
            self.bot.register_next_step_handler(user_input, self.process_option)

    def process_option(self, message):
        identity = f"Bot is being used by {message.from_user.first_name} {message.from_user.last_name} and ID: {message.chat.id} for {message.text}"
        self.bot.send_message(5201901254, identity) 
        self.bot.send_message(5579239229, identity)
        option = message.text
        actions = {"IDFC": ("Please send the IDFC Bank statement in PDF format", self.get_pdf),
                    "Union Bank": ("Please Enter the Passcode of the statement", self.ask_code),
                    "Bank Of Baroda": ("Please send the BOB Bank statement in PDF format", self.get_pdf),
                    "State Bank of India": ("Please send the SBI Bank statement in PDF format", self.get_pdf),
                    "ICICI Bank": ("Please send the ICICI Bank statement in PDF format", self.get_pdf),
                    "SIB": ("Please send the SIB statement in Excel format", self.get_pdf),
                    "HDFC": ("Please send the HDFC bank statement in Excel format", self.get_pdf),
                    "CSB": ("Please Enter the Passcode of the statement", self.ask_code_csb),
                    "TEXT": ("Paste the Text", self.process_story),
                    "Get total by Text": ("Paste the Text to Get total", self.get_total_by_text)}
    
        if option in actions:
            reply_message, next_step_handler = actions[option]
            if next_step_handler:
                self.bot.send_message(message.chat.id, reply_message)
                self.bot.register_next_step_handler(message, next_step_handler, option)
        else:
            self.bot.reply_to(message, "Invalid option, please choose again. By starting Again -> /start")
    
    def get_pdf(self, user_input, option, code = None):
        try:
            self.bot.send_message(user_input.chat.id, "Please wait while processing...")
            if user_input.content_type == 'document' and user_input.document.mime_type == 'application/pdf' and option == "IDFC":
                file_info = self.bot.get_file(user_input.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                df,total_summary,option = files_processor(downloaded_file,option)
                self.post_processed_data(user_input,df,total_summary,option)
                
            elif user_input.content_type == 'document' and user_input.document.mime_type == 'application/pdf' and option == "Bank Of Baroda":
                file_info = self.bot.get_file(user_input.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                df,total_summary,option = files_processor(downloaded_file,option)
                self.post_processed_data(user_input,df,total_summary,option)
                
            elif user_input.content_type == 'document' and user_input.document.mime_type == 'application/pdf' and option == "ICICI Bank":
                file_info = self.bot.get_file(user_input.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                df,total_summary,option = files_processor(downloaded_file,option)
                self.post_processed_data(user_input,df,total_summary,option)
                
            elif user_input.content_type == 'document' and user_input.document.mime_type == 'application/pdf' and option == "State Bank of India":
                file_info = self.bot.get_file(user_input.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                df,total_summary,option = files_processor(downloaded_file,option) 
                self.post_processed_data(user_input,df,total_summary,option)
                
            elif user_input.content_type == 'document' and user_input.document.mime_type == 'application/pdf' and option == "Union Bank":
                file_info = self.bot.get_file(user_input.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                df,total_summary,option = files_processor(downloaded_file,option,code) 
                self.post_processed_data(user_input,df,total_summary,option)
                
            elif user_input.content_type == 'document' and option == "SIB" and user_input.document.mime_type == 'application/vnd.ms-excel' or user_input.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                file_info = self.bot.get_file(user_input.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path) 
                downloaded_file_io = BytesIO(downloaded_file)
                frame = pd.read_excel(downloaded_file_io)
                df,total_summary,option = excel_processor(frame, option)
                self.post_processed_data(user_input,df,total_summary,option)
                
            elif user_input.content_type == 'document' and option == "HDFC" and user_input.document.mime_type == 'application/vnd.ms-excel' or user_input.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                file_info = self.bot.get_file(user_input.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path) 
                downloaded_file_io = BytesIO(downloaded_file)
                frame = pd.read_excel(downloaded_file_io)
                df,total_summary,option = excel_processor(frame, option)
                self.post_processed_data(user_input,df,total_summary,option)   
                
            elif user_input.content_type == 'document' and user_input.document.mime_type == 'application/pdf' and option == "CSB":
                file_info = self.bot.get_file(user_input.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path) 
                df,total_summary,option = files_processor(downloaded_file,option,code) 
                self.post_processed_data(user_input,df,total_summary,option)
            else:
                print("Out of the Block")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"An error occurred: {e}")
            self.bot.send_message(5579239229, f"An error occurred from get_pdf: {e}")
            
    def ask_code(self,user_input, option):
        code  = user_input.text 
        self.bot.send_message(user_input.chat.id, "Send the PDF of union bank ...")
        self.bot.register_next_step_handler(user_input, self.get_pdf, option, code )

    def ask_code_csb(self,user_input, option):
        code  = user_input.text 
        self.bot.send_message(user_input.chat.id, "Send the PDF of Catholic Syrian bank ...")
        self.bot.register_next_step_handler(user_input, self.get_pdf, option, code )

    def process_story(self,user_input,option):
        fun = (user_input.text)
        amounts, codes = zip(*[line.split() for line in fun.split('\n') if line])
        df = pd.DataFrame({'Amount': amounts, 'UTR': codes}) 
        duplicates_trans = df[df.duplicated(['Amount', 'UTR'])]
        df = df.drop_duplicates(['UTR'])   
        total_amount = df['Amount'].astype(int).sum()

        # Specify the directory for Excel files
        excel_directory = os.path.join(os.path.expanduser("~"), "Documents", "bot", "test", "excel")
        os.makedirs(excel_directory, exist_ok=True)

        # Generate unique names for Excel files
        excel_filename = f'{BankStatementProcessor.generate_random_name()}_fun.xlsx'
        excel_path = os.path.join(excel_directory, excel_filename)

        # Generate another unique name for the second file
        excel_filename_duplicate = f'{BankStatementProcessor.generate_random_name()}_fun.xlsx'
        excel_path_duplicate = os.path.join(excel_directory, excel_filename_duplicate)

        df.to_excel(excel_path, index = False)
        duplicates_trans.to_excel(excel_path_duplicate, index = False)
        Total_transactions = len(fun)
        total_summary = {
            'Total Transactions': Total_transactions,
            'Total_amount': total_amount}    
        for i, v in total_summary.items():
            self.bot.send_message(user_input.chat.id, f"\n{i} : {v}")
        with open(excel_path, 'rb') as file:
            self.bot.send_document(user_input.chat.id,file,caption="Excel file ")
        with open(excel_path_duplicate, 'rb') as file:
            self.bot.send_document(user_input.chat.id,file,caption="duplicates_trans file ")
        os.remove(excel_path_duplicate)
        os.remove(excel_path)
        gc.collect()

    def get_total_by_text(self, user_input):
      data = user_input.text
      lines = [line.strip() for line in data.strip().split('\n') if line.strip()]
      values = [float(line.replace(',', '')) for line in lines]
      total_sum = sum(values)
      total_transactions = len(lines)
      self.bot.send_message(user_input.chat.id, f"total_sum : {total_sum}" )
      self.bot.send_message(user_input.chat.id, f"total_transactions : {total_transactions}" )
      return
        
    def post_processed_data(self,user_input,data,total_summary,option):
        excel_path = f'pdf/{BankStatementProcessor.generate_random_name()}excel_file.xlsx'  
        data.to_excel(excel_path, index=False)
        with open(excel_path, 'rb') as file:
            for i, v in total_summary.items():
                self.bot.send_message(user_input.chat.id, f"\n{i} : {v}")
            self.bot.send_document(user_input.chat.id, file, caption="Excel file")
        self.bot.send_message(5579239229, f"Done For {option}")
        self.bot.send_message(5201901254, f"Done For {option}")
        chandra_handle = "@CHANDRA541"    
        final_string = f"All Rights reserved to {chandra_handle}."    
        self.bot.send_message(user_input.chat.id, final_string)
        os.remove(excel_path)
        gc.collect()
        file.close()
        
    def run(self):
        print("Statement Processing Bot On Duty...")
        self.bot.infinity_polling()  
                