import molsql
import MolDisplay
import json
import sys
import io
import sqlite3
import urllib
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

public_files = ['/index.html', '/style.css', '/script.js']

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in public_files:
            self.send_response(200)

            content_type = 'text/html'
            if self.path.endswith('.css'):
                content_type = 'text/css'
            elif self.path.endswith('.js'):
                content_type = 'text/javascript'

            self.send_header('Content-type', content_type)

            fp = open( self.path[1:] ) 
            page = fp.read()
            fp.close()

            self.send_header('Content-length', len(page))
            self.end_headers()
            self.wfile.write(bytes(page, 'utf-8'))

        elif self.path == '/removeElement':
            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Elements')
            elements = cursor.fetchall()
            cursor.close()
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(elements), 'utf-8'))

        elif self.path == '/displayMolecule':
            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM MOLECULES')
            molecules = cursor.fetchall()
            cursor.close()
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(molecules), 'utf-8'))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes('404: Not Found', 'utf-8'))

    def do_POST(self):
        if self.path == '/sdf':
            content_length = int(self.headers.get('Content-Length'))
            data = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(data.decode( 'utf-8' ))

            molecule_name = str(postvars[' name'][1])
            molecule_name = molecule_name.split('\n')
            molecule_name = str(molecule_name[2])
            molecule_name = molecule_name.rstrip('\r')
            

            file = io.StringIO(data.decode())
            for i in range (4):
                file.readline()

            mol = molsql.Database(False)
            mol.add_molecule(molecule_name, file)

            message = 'SDF file uploaded.'
            response = {'status': 'success', 'message': message}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/addElement':
            content_length = int(self.headers.get('Content-Length'))
            data = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(data.decode( 'utf-8' ))
            
            element_number = postvars['element_number'][0]
            element_code = postvars['element_code'][0]
            element_name = postvars['element_name'][0]
            color1 = postvars['color1'][0]
            color2 = postvars['color2'][0]
            color3 = postvars['color3'][0]
            radius = postvars['radius'][0]

            mol = molsql.Database(False)
            mol['Elements'] = (element_number, element_code, element_name, color1, color2, color3, radius)

            response = {'status': 'success', 'message': 'Element Added.'}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/deleteElement':
            content_length = int(self.headers.get('Content-Length'))
            data = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(data.decode( 'utf-8' ))

            element_code = postvars['element_code'][0]
            
            conn = sqlite3.connect('molecules.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Elements WHERE ELEMENT_CODE = ?", (element_code,))
            conn.commit()
            cursor.close()
            conn.close()

            response = {'status': 'success'}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/svg':
            content_length = int(self.headers.get('Content-Length'))
            data = self.rfile.read(content_length)
            postvars = urllib.parse.parse_qs(data.decode( 'utf-8' ))

            molecule_name = postvars['molecule_name'][0]
            db = molsql.Database(False)
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()
            mol = db.load_mol(molecule_name)
            mol.sort()
            svgData = mol.svg() 
            
            self.send_response(200)
            self.send_header('Content-type', 'image/svg+xml')
            self.end_headers()
            self.wfile.write(svgData.encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes('404: Not Found', 'utf-8'))

httpd = HTTPServer(('localhost', int(sys.argv[1])), handler)
httpd.serve_forever()