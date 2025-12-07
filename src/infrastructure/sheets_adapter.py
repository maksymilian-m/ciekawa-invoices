import json
import logging
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.ports.interfaces import SheetsProvider
from src.domain.entities import ProcessedInvoice
from src.config import settings

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsAdapter(SheetsProvider):
    def __init__(self, spreadsheet_id: str | None = None, credentials_path: str | None = None, token_path: str = "sheets_token.json"):
        self.spreadsheet_id = spreadsheet_id or settings.google_sheets_id
        self.credentials_path = credentials_path or settings.gmail_credentials_path # Reusing same credentials file
        self.token_path = token_path
        self.service = self._authenticate()
        logger.info("Initialized GoogleSheetsAdapter")

    def _authenticate(self):
        creds = None
        
        # 1. Try loading from Environment Variable (Cloud/Production)
        if settings.google_sheets_token_json:
            try:
                info = json.loads(settings.google_sheets_token_json)
                creds = Credentials.from_authorized_user_info(info, SCOPES)
                logger.info("Loaded Sheets credentials from environment variable.")
            except Exception as e:
                logger.error(f"Failed to load credentials from environment variable: {e}")

        # 2. Try loading from local file (Development)
        if not creds and os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # 3. Refresh or Login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # If we are using a file, update it
                    if os.path.exists(self.token_path):
                        with open(self.token_path, "w") as token:
                            token.write(creds.to_json())
                except Exception as e:
                    logger.warning(f"Failed to refresh token: {e}. Re-authenticating...")
                    creds = None
            
            # 4. Interactive Login (Local only)
            if not creds:
                if not self.credentials_path or not os.path.exists(self.credentials_path):
                    logger.warning("No credentials found. GoogleSheetsAdapter will not work.")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_path, "w") as token:
                    token.write(creds.to_json())
        
        return build("sheets", "v4", credentials=creds)

    def append_invoice(self, invoice: ProcessedInvoice):
        if not self.service:
            logger.warning("Sheets service not initialized. Skipping append.")
            return

        try:
            data = invoice.extracted_data
            
            field_map = {
                "Data wstawienia": lambda d: f"'{d.invoice_date.strftime('%d.%m.%Y')}",
                "PŁATNOŚĆ ZA": lambda d: d.category,
                "FIRMA / KONTRAHENT": lambda d: d.vendor_name,
                "NETTO": lambda d: f"{d.net_amount:.2f}".replace('.', ','),
                "KWOTA BRUTTO": lambda d: f"{d.gross_amount:.2f}".replace('.', ','),
                "KWOTA BRUTTO NA FAKTURZE": lambda d: f"{d.gross_amount:.2f}".replace('.', ','),
                "NR FV": lambda d: d.invoice_number,
                "TERMIN PŁATNOŚCI": lambda d: f"'{d.due_date.strftime('%d.%m.%Y')}"
            }

            row = []
            for column_header in settings.sheets_column_mapping:
                if column_header in field_map:
                    row.append(field_map[column_header](data))
                else:
                    row.append("")

            body = {'values': [row]}

            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=settings.sheets_name, 
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body
            ).execute()
            
            updates = result.get('updates', {})
            updated_range = updates.get('updatedRange', 'unknown')
            updated_cells = updates.get('updatedCells', 0)
            logger.info(f"Appended invoice {invoice.id} to Sheets. Range: {updated_range}, Cells: {updated_cells}")

            logger.info(f"Appended invoice {invoice.id} to Sheets. {result.get('updates').get('updatedCells')} cells updated.")

        except HttpError as error:
            logger.error(f"An error occurred appending to Sheets: {error}")
            raise
