@echo off
echo Creating ENAGEO Certificate Authority...

REM Create CA directory structure
if not exist "CA" mkdir CA
if not exist "CA\private" mkdir CA\private
if not exist "CA\certs" mkdir CA\certs
if not exist "CA\newcerts" mkdir CA\newcerts
if not exist "CA\crl" mkdir CA\crl

REM Create index.txt and serial files (index.txt must be completely empty)
type nul > CA\index.txt
echo 1000 > CA\serial

REM Create CA configuration file
echo [ ca ] > CA\openssl.cnf
echo default_ca = CA_default >> CA\openssl.cnf
echo. >> CA\openssl.cnf
echo [ CA_default ] >> CA\openssl.cnf
echo dir = ./CA >> CA\openssl.cnf
echo certs = $dir/certs >> CA\openssl.cnf
echo crl_dir = $dir/crl >> CA\openssl.cnf
echo new_certs_dir = $dir/newcerts >> CA\openssl.cnf
echo database = $dir/index.txt >> CA\openssl.cnf
echo certificate = $dir/certs/ca.cert.pem >> CA\openssl.cnf
echo serial = $dir/serial >> CA\openssl.cnf
echo crl = $dir/crl/ca.crl >> CA\openssl.cnf
echo private_key = $dir/private/ca.key.pem >> CA\openssl.cnf
echo RANDFILE = $dir/private/.rand >> CA\openssl.cnf
echo. >> CA\openssl.cnf
echo name_opt = ca_default >> CA\openssl.cnf
echo cert_opt = ca_default >> CA\openssl.cnf
echo default_days = 3650 >> CA\openssl.cnf
echo default_crl_days = 30 >> CA\openssl.cnf
echo default_md = sha256 >> CA\openssl.cnf
echo preserve = no >> CA\openssl.cnf
echo policy = policy_strict >> CA\openssl.cnf
echo. >> CA\openssl.cnf
echo [ policy_strict ] >> CA\openssl.cnf
echo countryName = match >> CA\openssl.cnf
echo stateOrProvinceName = match >> CA\openssl.cnf
echo organizationName = match >> CA\openssl.cnf
echo organizationalUnitName = optional >> CA\openssl.cnf
echo commonName = supplied >> CA\openssl.cnf
echo emailAddress = optional >> CA\openssl.cnf
echo. >> CA\openssl.cnf
echo [ req ] >> CA\openssl.cnf
echo default_bits = 4096 >> CA\openssl.cnf
echo distinguished_name = req_distinguished_name >> CA\openssl.cnf
echo string_mask = utf8only >> CA\openssl.cnf
echo default_md = sha256 >> CA\openssl.cnf
echo x509_extensions = v3_ca >> CA\openssl.cnf
echo. >> CA\openssl.cnf
echo [ req_distinguished_name ] >> CA\openssl.cnf
echo countryName = Country Name (2 letter code) >> CA\openssl.cnf
echo countryName_default = DZ >> CA\openssl.cnf
echo stateOrProvinceName = State or Province Name >> CA\openssl.cnf
echo stateOrProvinceName_default = Wilaya de Ouargla >> CA\openssl.cnf
echo localityName = Locality Name >> CA\openssl.cnf
echo localityName_default = Hassi-Messaoud >> CA\openssl.cnf
echo organizationName = Organization Name >> CA\openssl.cnf
echo organizationName_default = Entreprise Nationale de Geologie >> CA\openssl.cnf
echo organizationalUnitName = Organizational Unit Name >> CA\openssl.cnf
echo organizationalUnitName_default = IT Department >> CA\openssl.cnf
echo commonName = Common Name >> CA\openssl.cnf
echo commonName_default = ENAGEO Root CA >> CA\openssl.cnf
echo emailAddress = Email Address >> CA\openssl.cnf
echo emailAddress_default = admin@enageo.dz >> CA\openssl.cnf
echo. >> CA\openssl.cnf
echo [ v3_ca ] >> CA\openssl.cnf
echo subjectKeyIdentifier = hash >> CA\openssl.cnf
echo authorityKeyIdentifier = keyid:always,issuer >> CA\openssl.cnf
echo basicConstraints = critical, CA:true >> CA\openssl.cnf
echo keyUsage = critical, digitalSignature, cRLSign, keyCertSign >> CA\openssl.cnf

REM Generate CA private key (encrypted with password)
echo Generating CA private key...
openssl genrsa -aes256 -out CA\private\ca.key.pem -passout pass:password 4096

REM Generate CA certificate
echo Generating CA certificate...
openssl req -config CA\openssl.cnf -key CA\private\ca.key.pem -new -x509 -days 3650 -sha256 -extensions v3_ca -out CA\certs\ca.cert.pem -passin pass:password -subj "/C=DZ/ST=Wilaya de Ouargla/L=Hassi-Messaoud/O=Entreprise Nationale de Geologie/OU=IT Department/CN=ENAGEO Root CA/emailAddress=admin@enageo.dz"

REM Copy CA certificate to backend certs directory
if not exist "backend\certs" mkdir backend\certs
copy CA\certs\ca.cert.pem backend\certs\

echo.
echo Certificate Authority created successfully!
echo CA private key: CA\private\ca.key.pem (encrypted with password: password)
echo CA certificate: CA\certs\ca.cert.pem
echo CA certificate copied to: backend\certs\ca.cert.pem
echo.
echo Next step: Run create_server_cert.bat to create server certificate
pause 