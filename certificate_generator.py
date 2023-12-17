import os
import time
import pandas
from PIL import Image, ImageDraw, ImageFont
from emailer import Emailer
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from colorama import init, Fore, Style
from shutil import copyfile

init(autoreset=True)  # Initialize colorama for cross-platform colored text
# Set the Colour before drawing
TEXT_COLOUR = (0,0,255) 
# Configure the folders
OUTPUT_DIRECTORY = "Certificates"
TEMPLATE_DIRECTORY = "template"
# Font configuration
FONT = ImageFont.truetype(r"Fonts/PlaypenSans-Bold.ttf", size=56)
pdfmetrics.registerFont(TTFont("cer_font",r"Fonts/PlaypenSans-Bold.ttf"))

class GenerateByPdf():
    def __init__(self, account, password) -> None:
        self.mailer = Emailer(account, password)
        self.pdf_template_path = os.path.join(TEMPLATE_DIRECTORY, "sample.pdf")

        # Make output directory
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
        self._store_participants_data()

    def _store_participants_data(self) -> None:
        self.df = pandas.read_csv(r"names.csv")
        self.names = self.df['Name'].tolist()
        self.emails = self.df['Email'].tolist()
        self.success_indices = []

    def _draw_text_on_pdf(self, pdf_path, name):
       
        pass
    
    def _send_email(self) -> None:
        for index, (name, email) in enumerate(zip(self.names, self.emails)):
            # Make path and generate certificates
            out_path_certificate = os.path.join(OUTPUT_DIRECTORY, f"{name}.pdf")
            self._draw_text_on_pdf(out_path_certificate, name)

            # Sending the mail
            self.status = self.mailer.SendMail(email, name)
            if self.status == "sent":
                self.success_indices.append(index)

        self.df = self.df.drop(index=self.success_indices)
        self.df.to_csv(r"names.csv", index=False)
        print(f"{Style.BRIGHT}{Fore.GREEN}Script Running Completed.{Fore.RESET}{Style.RESET_ALL}", flush=True)
        self.success_indices = []


    def _retry_failed_operation(self) -> None :

        # Reconfigure the remaining list 
        self.df = pandas.read_csv(r"names.csv")
        self.names = self.df['Name'].tolist()
        self.emails = self.df['Email'].tolist()

        if len(self.names) == 0 or len(self.emails) == 0 :
            pass
        else :
            print(f"{Style.BRIGHT}{Fore.YELLOW}Retrying the failed connection...{Fore.RESET}{Style.RESET_ALL}")
            time.sleep(1)
            self._send_email() 

    def _check_remaining(self) -> None:
        if len(self.names) == 0 or len(self.emails) == 0 :
            print(f"{Style.BRIGHT}{Fore.GREEN}All the persons has been mailed, no need to run script again{Fore.RESET}{Style.RESET_ALL}")
        else :
            print(f'{Style.BRIGHT}{Fore.YELLOW}Some names are remaining in the list, you may run script again by running:{Fore.RESET}{Fore.BLUE} ./certimailer.sh {Fore.RESET}{Fore.YELLOW}to send mails to remaining persons. {Fore.RESET}{Style.RESET_ALL}')

    def _is_csv_updated(self) :
        if len(self.names) == 0 or len(self.emails) == 0 :
            print(f"{Style.BRIGHT}{Fore.YELLOW}Please update the 'names.csv'{Fore.RESET}{Style.RESET_ALL}")
            return "break"

class GenerateByImage() :

    def __init__(self, account, password) -> None:

        # Mailer Object
        self.mailer = Emailer(account, password)

        # Load the certificate templae
        self.certificate_img = Image.open(r"template/sample.png")

        # Create a drawing object to calculate the length text wll take
        self.drawer_img = ImageDraw.Draw(self.certificate_img)
        
        # Font configuration
        # self.font = ImageFont.truetype(r"Fonts/PlaypenSans-Bold.ttf", size=56)
        self.png_template_path = os.path.join(TEMPLATE_DIRECTORY, "sample.png")
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
        self._store_participants_data()

    def _store_participants_data(self) -> None : 
        self.df = pandas.read_csv(r"names.csv")
        self.names = self.df['Name'].tolist()
        self.emails = self.df['Email'].tolist()
        self.success_indices = []

    def _draw_on_img(self, name) -> None :
        # Output path
        self.out_path_certificate = os.path.join(OUTPUT_DIRECTORY, f"{name}.pdf")

        # Make a canvas
        self.drawer = canvas.Canvas(self.out_path_certificate, pagesize=(self.certificate_img.width, self.certificate_img.height))

        # Insert image
        self.drawer.drawImage(self.png_template_path,0,0, width=self.certificate_img.width, height=self.certificate_img.height)

        # Set the drawer object font and colour
        self.drawer.setFont("cer_font",56)
        self.drawer.setFillColor(TEXT_COLOUR)

        # Adjust Position (x,y)
        # Adjust Coordinates by https://www.image-map.net/
        # Y - coordinate keep the touching line - Use link above to get the coordinates
        self.text_width = self.drawer_img.textlength(name,font=FONT)
        self.name_position = ((self.certificate_img.width - self.text_width)/2, self.certificate_img.height - 805)

        # Draw the name: 
        self.drawer.drawString(self.name_position[0], self.name_position[1], name)
        # Save the pdf with text written  
        self.drawer.save()

    def _send_email(self) -> None :
        for index, (name,email) in enumerate(zip(self.names, self.emails)) :
            # Make certificate
            self._draw_on_img(name)

            # Sending the mail
            self.status = self.mailer.SendMail(email, name)
            if self.status == "sent" :
                self.success_indices.append(index)

        #  Update the original dataframe: 
        self.df = self.df.drop(index=self.success_indices)

        # Save the dataframe
        self.df.to_csv(r"names.csv", index=False)

        # Closing the template image
        self.certificate_img.close()
        print(f"{Style.BRIGHT}{Fore.GREEN}Script Running Completed.{Fore.RESET}{Style.RESET_ALL}", flush=True)
        self.success_indices = []

    def _retry_failed_operation(self) -> None :

        # Reconfigure the remaining list 
        self.df = pandas.read_csv(r"names.csv")
        self.names = self.df['Name'].tolist()
        self.emails = self.df['Email'].tolist()

        if len(self.names) == 0 or len(self.emails) == 0 :
            pass
        else :
            print(f"{Style.BRIGHT}{Fore.YELLOW}Retrying the failed connection...{Fore.RESET}{Style.RESET_ALL}")
            time.sleep(1)
            self._send_email() 

    def _check_remaining(self) -> None:
        if len(self.names) == 0 or len(self.emails) == 0 :
            print(f"{Style.BRIGHT}{Fore.GREEN}All the persons has been mailed, no need to run script again{Fore.RESET}{Style.RESET_ALL}")
        else :
            print(f'{Style.BRIGHT}{Fore.YELLOW}Some names are remaining in the list, you may run script again by running:{Fore.RESET}{Fore.BLUE} ./certimailer.sh {Fore.RESET}{Fore.YELLOW}to send mails to remaining persons. {Fore.RESET}{Style.RESET_ALL}')

    def _is_csv_updated(self) :
        if len(self.names) == 0 or len(self.emails) == 0 :
            print(f"{Style.BRIGHT}{Fore.YELLOW}Please update the 'names.csv'{Fore.RESET}{Style.RESET_ALL}")
            return "break"