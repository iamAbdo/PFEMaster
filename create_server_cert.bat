@echo off
echo Creating Server Certificate signed by ENAGEO CA...

REM Check if CA exists
if not exist "CA\certs\ca.cert.pem" (
    echo Error: CA certificate not found. Please run create_ca.bat first.
    pause
    exit /b 1
)

if not exist "CA\private\ca.key.pem" (
    echo Error: CA private key not found. Please run create_ca.bat first.
    pause
    exit /b 1
)

REM Check if index.txt exists and is properly formatted
if not exist "CA\index.txt" (
    echo Error: CA index.txt file not found. Please run create_ca.bat first.
    pause
    exit /b 1
)

REM Check if index.txt is empty (should be for a new CA)
for %%A in (CA\index.txt) do set size=%%~zA
if not "%size%"=="0" (
    echo Warning: CA index.txt file is not empty.
    echo This might cause issues with certificate signing.
    echo You can run fix_ca_index.bat to fix this.
    echo.
    set /p continue="Do you want to continue anyway? (y/N): "
    if /i not "%continue%"=="y" (
        echo Certificate creation cancelled.
        pause
        exit /b 1
    )
)

REM Create server certificate request configuration
echo [ req ] > server_req.cnf
echo default_bits = 2048 >> server_req.cnf
echo distinguished_name = req_distinguished_name >> server_req.cnf
echo req_extensions = v3_req >> server_req.cnf
echo prompt = no >> server_req.cnf
echo. >> server_req.cnf
echo [ req_distinguished_name ] >> server_req.cnf
echo C = DZ >> server_req.cnf
echo ST = Wilaya de Ouargla >> server_req.cnf
echo L = Hassi-Messaoud >> server_req.cnf
echo O = Entreprise Nationale de Geologie >> server_req.cnf
echo OU = IT Department >> server_req.cnf
echo CN = backend.enageo.com >> server_req.cnf
echo emailAddress = admin@enageo.dz >> server_req.cnf
echo. >> server_req.cnf
echo [ v3_req ] >> server_req.cnf
echo basicConstraints = CA:FALSE >> server_req.cnf
echo keyUsage = nonRepudiation, digitalSignature, keyEncipherment >> server_req.cnf
echo subjectAltName = @alt_names >> server_req.cnf
echo. >> server_req.cnf
echo [ alt_names ] >> server_req.cnf
echo DNS.1 = localhost >> server_req.cnf
echo DNS.2 = backend.enageo.com >> server_req.cnf
echo DNS.3 = 127.0.0.1 >> server_req.cnf
echo IP.1 = 127.0.0.1 >> server_req.cnf

REM Create server extensions configuration
echo [ v3_server ] > server_ext.cnf
echo basicConstraints = CA:FALSE >> server_ext.cnf
echo keyUsage = digitalSignature, keyEncipherment >> server_ext.cnf
echo extendedKeyUsage = serverAuth, clientAuth >> server_ext.cnf
echo subjectAltName = @alt_names >> server_ext.cnf
echo. >> server_ext.cnf
echo [ alt_names ] >> server_ext.cnf
echo DNS.1 = localhost >> server_ext.cnf
echo DNS.2 = backend.enageo.com >> server_ext.cnf
echo DNS.3 = 127.0.0.1 >> server_ext.cnf
echo IP.1 = 127.0.0.1 >> server_ext.cnf

REM Generate server private key
echo Generating server private key...
openssl genrsa -out backend\certs\server.key.pem 2048

REM Generate server certificate signing request
echo Generating server certificate signing request...
openssl req -new -key backend\certs\server.key.pem -out backend\certs\server.csr -config server_req.cnf

REM Sign server certificate with CA
echo Signing server certificate with CA...
openssl ca -config CA\openssl.cnf -batch -in backend\certs\server.csr -out backend\certs\server.cert.pem -extensions v3_server -extfile server_ext.cnf -passin pass:password

REM Clean up temporary files
del server_req.cnf
del server_ext.cnf
del backend\certs\server.csr

echo.
echo Server certificate created successfully!
echo Server private key: backend\certs\server.key.pem
echo Server certificate: backend\certs\server.cert.pem
echo.
echo The server certificate is now signed by the ENAGEO CA.
echo You can now start the backend server with proper SSL certificates.
pause 