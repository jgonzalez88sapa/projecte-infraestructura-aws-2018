### Guia d’instal·lació dels diferents programes i llibreries per fer funcionar els scripts.

Abans de res necessitarem tenir un compte d’AWS i els credencials per accedir-hi. Això ho podem trobar al nostre compte > My Security Credentials > Access keys.  

## Windows


Descarrega i instal·la Python 2.7 d’aquest [enllaç](https://www.python.org/downloads/).  
Durant la instal·lació assegurat d’afegir python.exe al Path.  
![instal·la python on windows](https://raw.githubusercontent.com/jgonzalez88sapa/projecte-infraestructura-aws-2018/master/img/w1.png)

Polsa la tecla Windows+R, escriu cmd i polsa Intro. Assegurat de tenir pip a la ultima versió amb aquesta comanda:  
> python -m pip install --upgrade pip  
  
Instal·la AWSCLI, l’administrador d’AWS per comandes, amb la següent comanda:  
> pip install awscli  

Ara escriu la comanda següent:  
> aws configure  

I introdueix el teu AWS Access Key ID, AWS Secret Access Key i el nom de la regió (eu-west-1).  
Això crea una carpeta anomenada .aws amb els fitxers config i credentials que inclouen la configuració introduïda amb l’anterior comanda.  

Per últim tenim que instal·lar la llibreria Boto 3 amb la següent comanda:  
> pip install boto3  

Ja tenim tot lo necessari per a que funcionin els scripts.  


## Linux (Ubuntu)  
Obrim un terminal i ens assegurem de tenir els repositoris actualitzats:   
> supo apt-get update  

I de tenir la versió 2.7 de Python:  
> python -V  

En cas contrari executem la següent comanda:  
> sudo apt install python2.7 python-pip  

Ens asegurem de tenir pip actualitzat a la última versió amb aquesta comanda:  
> sudo python -m pip install --upgrade pip  

Instal·la AWSCLI, l’administrador d’AWS per comandes, amb la següent comanda:  
> sudo pip install awscli  

Ara escriu la comanda següent:  
> aws configure  

I introdueix el teu AWS Access Key ID, AWS Secret Access Key i el nom de la regió (eu-west-1).  
Això crea una carpeta anomenada .aws amb els fitxers config i credentials que inclouen la configuració introduïda amb l’anterior comanda.  

Per últim tenim que instal·lar la llibreria Boto 3 amb la següent comanda:  
> pip install boto3  

Ja tenim tot lo necessari per a que funcionin els scripts.  
  
### Com connectar-se a una instancia EC2 a la que tenim accés per SSH.

## Windows

Primer de tot tenim que tenir el fitxer PEM. Descarreguem el programa Putty i PuttyGen d’aquest enllaç.

Obrim PuttyGen i carreguem el fitxer PEM a Load:  
![PuttyGen1](https://raw.githubusercontent.com/jgonzalez88sapa/projecte-infraestructura-aws-2018/master/img/1.png)

Un cop carregat, li donem al boto Save private key:  
![PuttyGen2](https://raw.githubusercontent.com/jgonzalez88sapa/projecte-infraestructura-aws-2018/master/img/2.png)

Això ens genera un fitxer PPK que tenim que guardar.  
Ara obrim Putty i introduïm la direcció IP o DNS de la instancia a la que ens volem connectar per SSH:  
![Putty1](https://raw.githubusercontent.com/jgonzalez88sapa/projecte-infraestructura-aws-2018/master/img/3.png) 

I anem a Connection > SSH > Auth i introduïm la ruta del fitxer PPK que em generat anteriorment i ja ens hi podem connectar.
![Putty2](https://raw.githubusercontent.com/jgonzalez88sapa/projecte-infraestructura-aws-2018/master/img/4.png)  

## Linux

Obra un terminal i localitza a on esta el fitxer PEM i ves a la seva carpeta.

Canvia els permisos amb aquesta comanda:

> sudo chmod 400 file.pem

Ara ja pots connectar-te per SSH a la instancia amb el nom d’usuari (que depèn de la AMI de la instancia) i la seva adreça IP o DNS:

> sudo ssh -i file.pem ubuntu@41.258.69.14
