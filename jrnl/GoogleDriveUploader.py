from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import errors
from apiclient.http import MediaFileUpload


class Uploader(object):

    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/drive-python-quickstart.json
    SCOPES = 'https://www.googleapis.com/auth/drive'
    CLIENT_SECRET_FILE = 'cmd_secret.json'
    APPLICATION_NAME = 'jrnl uploader'

    def _get_credentials(self):

        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'drive-creds.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            # try:
            #
            # except ImportError:
            #     flags = None

            flags = tools.argparser.parse_args(args=[])
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:
                credentials = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def _insert_file(self, service, title,
                    description, parent_id, mime_type, filename):
        """
        Given previously constructed service, title of file to be stored,
        description of file, parent directory of the file,
        mimetype, and filename to be stored as.
        """
        media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
        body = {
         'title': title,
         'description': description,
         'mimeType': mime_type
        }
        # Set the parent folder.
        if parent_id:
            body['parents'] = [{'id': parent_id}]
        file = None # file object uploaded to GDrive
        try:
            all_files = service.files().list().execute()
            for file_obj in all_files['items']:
                if file_obj['title'] == title:
                    file = service.files().update(fileId=file_obj['id'],
                                       body=body, media_body=media_body).execute()
                break
            else:
                file = service.files().insert(body=body, media_body=media_body).execute()
            return file
        except errors.HttpError as error:
            print('An error occurred: ', error)
            return None

    def upload(self, journal_name, journal_filename):
        credentials = self._get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('drive', 'v2', http=http)

        self._insert_file(service, journal_name, 'jrnl upload and save', None, 'text/plain',
                         journal_filename)



